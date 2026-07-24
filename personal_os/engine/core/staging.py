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
import stat
import uuid

from personal_os.engine.contract.run_dir import ArtifactHandle, RunDir
from personal_os.engine.contract.workspace import Workspace


def stage(source_tree: str, run_dir: RunDir) -> str:
    """Copy ``source_tree`` into ``run_dir/staging`` and return the staged root.

    The source is left untouched (isolation). If staging is already populated
    it is replaced wholesale (a run stages exactly once in normal flow). Source
    symlinks are copied without dereferencing and then rejected: v0 fixtures
    must contain only plain files and directories.
    """
    if stat.S_ISLNK(os.lstat(source_tree).st_mode):
        raise ValueError(f"source_tree must not be a symlink: {source_tree!r}")

    staged = run_dir.staging_dir
    if os.path.isdir(staged) and os.listdir(staged):
        shutil.rmtree(staged)
    # copytree needs the dest to not exist (py3.9 has no dirs_exist_ok default
    # we want to rely on); ensure a clean target.
    if os.path.isdir(staged):
        shutil.rmtree(staged)
    shutil.copytree(source_tree, staged, symlinks=True)
    for root, directories, files in os.walk(staged, followlinks=False):
        for name in directories + files:
            path = os.path.join(root, name)
            if stat.S_ISLNK(os.lstat(path).st_mode):
                raise ValueError(f"source fixture contains a symlink: {path!r}")
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
    ws.resolve(target)
    relative = os.path.normpath(target)
    if relative in ("", os.curdir):
        raise ValueError(f"patch target must name a file: {target!r}")
    components = relative.split(os.sep)
    leafname = components.pop()
    dest = os.path.join(run_dir.staging_dir, relative)

    if os.open not in os.supports_dir_fd or os.mkdir not in os.supports_dir_fd:
        raise RuntimeError("descriptor-relative path operations are unavailable")

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    root_fd = None
    parent_fd = None
    fd = None
    tmpname = None
    data = content.encode("utf-8")
    try:
        root_fd = os.open(run_dir.staging_dir, directory_flags)
        parent_fd = root_fd
        for component in components:
            try:
                child_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            except FileNotFoundError:
                try:
                    os.mkdir(component, dir_fd=parent_fd)
                except FileExistsError:
                    pass
                child_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            if parent_fd != root_fd:
                os.close(parent_fd)
            parent_fd = child_fd

        # Write a fresh inode and atomically install it. Opening the existing
        # leaf with O_TRUNC would mutate every hard link to that inode,
        # including links outside the containment wall.
        tmpname = f".patch-{uuid.uuid4().hex}"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        fd = os.open(tmpname, flags, 0o644, dir_fd=parent_fd)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError(f"patch target is not a regular file: {target!r}")
        view = memoryview(data)
        total = 0
        while total < len(data):
            written = os.write(fd, view[total:])
            if written <= 0:
                raise OSError("patch write made no progress")
            total += written
        os.fsync(fd)
        os.close(fd)
        fd = None

        try:
            existing = os.lstat(leafname, dir_fd=parent_fd)
        except FileNotFoundError:
            existing = None
        if existing is not None and stat.S_ISLNK(existing.st_mode):
            raise ValueError(f"patch target is a symlink: {target!r}")

        os.replace(
            tmpname,
            leafname,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
        )
        tmpname = None
        os.fsync(parent_fd)
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(
            f"refusing unsafe patch target component: {target!r} ({exc})"
        ) from exc
    finally:
        if fd is not None:
            os.close(fd)
        if tmpname is not None and parent_fd is not None:
            try:
                os.unlink(tmpname, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
        if parent_fd is not None and parent_fd != root_fd:
            os.close(parent_fd)
        if root_fd is not None:
            os.close(root_fd)
    return dest
