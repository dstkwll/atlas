"""Task 1.3 — staging + patch application (Core-owned, handle-based).

Core copies the source fixture into ``run_dir/staging`` (``stage``) so the
original tree is never mutated, then applies a worker's proposed patch to the
STAGED tree only (``apply_patch``). The patch crosses the port as an opaque
``ArtifactHandle``; Core resolves it and enforces the filesystem wall: the
patch's declared target is a run-relative path validated through the staging
``Workspace``, so ``..`` traversal / absolute / symlink escape is rejected
(invariant 12). A worker never hands Core a filesystem path — only a handle to
a patch payload whose *target* Core itself re-contains.

Patch payload schema (v0, deterministic + minimal): a JSON object
``{"target": "<run-relative path under staging>", "content": "<full new file
bytes as text>"}``. Whole-file replacement keeps the wall trivially auditable
(no fuzzy hunks that could smuggle a path); the refiner/worker proposes the new
content, Core decides where it may land.
"""

from __future__ import annotations

import json
import os
import shutil

from personal_os.engine.contract.run_dir import ArtifactHandle, RunDir
from personal_os.engine.contract.workspace import Workspace


def stage(source_tree: str, run_dir: RunDir) -> str:
    """Copy ``source_tree`` into ``run_dir/staging`` and return the staged root.

    The source is left untouched (isolation). If staging is already populated
    it is replaced wholesale (a run stages exactly once in normal flow).
    """
    staged = run_dir.staging_dir
    if os.path.isdir(staged) and os.listdir(staged):
        shutil.rmtree(staged)
    # copytree needs the dest to not exist (py3.9 has no dirs_exist_ok default
    # we want to rely on); ensure a clean target.
    if os.path.isdir(staged):
        shutil.rmtree(staged)
    shutil.copytree(source_tree, staged)
    return staged


def apply_patch(run_dir: RunDir, patch_handle: ArtifactHandle) -> str:
    """Apply a worker's proposed patch to the STAGED tree (wall-enforced).

    Resolves the opaque handle, parses the ``{target, content}`` payload, and
    writes ``content`` to ``staging/<target>`` — but only after the staging
    ``Workspace`` confirms the target stays inside the staging root. Returns the
    absolute path written. Raises ``ValueError`` on any containment violation.
    """
    resolved = run_dir.resolve_handle(patch_handle)
    with open(resolved, "rb") as f:
        payload = json.loads(f.read().decode("utf-8"))

    target = payload["target"]
    content = payload["content"]

    ws = Workspace(run_dir.staging_dir)
    # resolve() fails closed on absolute / .. / symlink escape (invariant 12).
    dest = ws.resolve(target)

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    return dest
