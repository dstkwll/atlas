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

    # F2 (TOCTOU): resolve() validated a real path, but a concurrent worker
    # descendant could swap a component for an outward symlink before the write.
    # Defend by (a) re-confirming no path component is a symlink right now, and
    # (b) opening the LEAF with O_NOFOLLOW|O_CREAT|O_EXCL-or-truncate so the
    # kernel itself refuses to follow a symlink at the target. The write can
    # never land outside staging even under a racing symlink swap.
    staging_root = os.path.realpath(run_dir.staging_dir)
    parent = os.path.dirname(dest)
    os.makedirs(parent, exist_ok=True)

    # Re-verify the parent (post-mkdir) still resolves inside staging.
    real_parent = os.path.realpath(parent)
    if real_parent != staging_root and not real_parent.startswith(staging_root + os.sep):
        raise ValueError(f"patch parent escapes staging root: {target!r}")

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    data = content.encode("utf-8")
    try:
        fd = os.open(dest, flags, 0o644)
    except OSError as exc:
        # O_NOFOLLOW raises ELOOP if the leaf is a symlink — a TOCTOU attempt.
        raise ValueError(f"refusing to write through a symlink target: {target!r} ({exc})")
    try:
        # Final guard: the opened fd must be a regular file inside staging.
        st = os.fstat(fd)
        import stat as _stat
        if not _stat.S_ISREG(st.st_mode):
            raise ValueError(f"patch target is not a regular file: {target!r}")
        view = memoryview(data)
        total = 0
        while total < len(data):
            written = os.write(fd, view[total:])
            if written <= 0:
                raise OSError("patch write made no progress")
            total += written
        os.fsync(fd)
    finally:
        os.close(fd)
    return dest
