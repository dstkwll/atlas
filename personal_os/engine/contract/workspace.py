"""Task 0.7 — the code-enforced filesystem containment wall.

``Workspace`` is Core's guarantee that every path it touches stays inside the
run root. ``resolve(relpath)`` rejects absolute-path escape, ``..`` traversal,
and symlink escape by comparing the fully-resolved real path against the
resolved real root (invariant 12). Core never validates against a
worker-selected path — only against this staged, contained tree.

``id`` hashes the **canonicalized run-relative structure** (relative paths +
content hashes), not the absolute root, so ``workspace_id`` is deterministic
across machines and runs (invariant 11 — feeds byte-identical reports).

``fail_closed_if_synced(root)`` raises if the root resolves inside a known
cloud-synced location — the confidentiality wall is CODE, not mere no-sync
hygiene (locked decision).
"""

from __future__ import annotations

import hashlib
import json
import os
import stat

# Path fragments that indicate a cloud-synced location (case-insensitive).
_SYNCED_MARKERS = (
    "library/mobile documents",   # macOS iCloud Drive
    "/icloud",
    "/dropbox",
    "/onedrive",
    "/google drive",
    "/googledrive",
    "com~apple~clouddocs",
)


class Workspace:
    """A root-contained view of a run directory."""

    def __init__(self, root: str) -> None:
        self.root = os.path.realpath(root)
        os.makedirs(self.root, exist_ok=True)

    def resolve(self, relpath: str) -> str:
        """Resolve a run-relative path, raising on any escape.

        Rejects absolute inputs, ``..`` traversal, and symlink escape. Returns
        an absolute path guaranteed to live inside the root.
        """
        if os.path.isabs(relpath):
            raise ValueError(f"absolute path not allowed: {relpath!r}")
        if os.pardir in relpath.replace("\\", "/").split("/"):
            raise ValueError(f"parent traversal not allowed: {relpath!r}")

        candidate = os.path.join(self.root, relpath)
        # Resolve symlinks along the whole path (incl. leaf and any parent).
        real = os.path.realpath(candidate)
        root_prefix = self.root + os.sep
        if real != self.root and not real.startswith(root_prefix):
            raise ValueError(f"path escapes workspace root: {relpath!r}")
        # Return the canonicalized real path (symlinks collapsed) so what we
        # hand back is exactly what we validated (P3-1: no validate/return gap).
        return real

    @property
    def id(self) -> str:
        """Deterministic hash of the canonicalized run-relative structure.

        F3: lstat every entry and NEVER follow a symlink. A symlinked file is
        hashed by its link TEXT (marked as a symlink), not by opening it — so
        the id can never depend on content outside the containment wall, and an
        external mutation can't change the workspace id. Directory symlinks are
        also not traversed (``os.walk(followlinks=False)`` default) and are
        recorded as symlink entries. Any stat/read race fails closed to a
        stable sentinel rather than an attested outside-read.
        """
        h = hashlib.sha256()
        entries = []
        for dirpath, dirnames, filenames in os.walk(self.root, followlinks=False):
            dirnames.sort()
            # Record every directory entry. Symlinks carry their target text;
            # ordinary directories carry a typed empty payload so even an empty
            # directory changes the canonical workspace structure.
            for name in sorted(dirnames):
                abs_p = os.path.join(dirpath, name)
                rel = os.path.relpath(abs_p, self.root).replace(os.sep, "/")
                if os.path.islink(abs_p):
                    try:
                        target = os.readlink(abs_p)
                    except OSError:
                        target = ""
                    entries.append((rel, "symlink", target))
                else:
                    entries.append((rel, "dir", ""))
            for name in sorted(filenames):
                abs_p = os.path.join(dirpath, name)
                rel = os.path.relpath(abs_p, self.root).replace(os.sep, "/")
                try:
                    before = os.lstat(abs_p)
                except OSError:
                    entries.append((rel, "unreadable", ""))
                    continue

                # Never open a known FIFO/device: even a read-only open can
                # block or have side effects. Symlinks are deliberately passed
                # to O_NOFOLLOW so classification and access are enforced by
                # the kernel at the same pathname lookup.
                if not (stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode)):
                    entries.append((rel, "type", f"{stat.S_IFMT(before.st_mode):o}"))
                    continue

                fd = None
                try:
                    flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
                    fd = os.open(abs_p, flags)
                    opened = os.fstat(fd)
                    if not stat.S_ISREG(opened.st_mode):
                        entries.append((rel, "type", f"{stat.S_IFMT(opened.st_mode):o}"))
                        continue
                    digest = hashlib.sha256()
                    while True:
                        chunk = os.read(fd, 1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                    entries.append((rel, "file", digest.hexdigest()))
                except OSError:
                    # O_NOFOLLOW rejects a symlink atomically. Inspect only to
                    # choose a stable representation; never retry a path open.
                    try:
                        current = os.lstat(abs_p)
                        if stat.S_ISLNK(current.st_mode):
                            entries.append((rel, "symlink", os.readlink(abs_p)))
                        else:
                            entries.append(
                                (rel, "type", f"{stat.S_IFMT(current.st_mode):o}")
                            )
                    except OSError:
                        entries.append((rel, "unreadable", ""))
                finally:
                    if fd is not None:
                        os.close(fd)
        records = [
            json.dumps(entry, ensure_ascii=True, separators=(",", ":"), sort_keys=False)
            for entry in entries
        ]
        for record in sorted(records):
            h.update(record.encode("utf-8"))
            h.update(b"\n")
        return h.hexdigest()


def fail_closed_if_synced(root: str) -> None:
    """Raise if ``root`` resolves inside a known cloud-synced location."""
    real = os.path.realpath(root).lower()
    for marker in _SYNCED_MARKERS:
        if marker in real:
            raise ValueError(
                f"run root resolves inside a cloud-synced location ({marker!r}): {root!r}"
            )
