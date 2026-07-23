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
import os

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
        """Deterministic hash of the canonicalized run-relative structure."""
        h = hashlib.sha256()
        entries = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames.sort()
            for name in sorted(filenames):
                abs_p = os.path.join(dirpath, name)
                rel = os.path.relpath(abs_p, self.root).replace(os.sep, "/")
                try:
                    with open(abs_p, "rb") as f:
                        digest = hashlib.sha256(f.read()).hexdigest()
                except (OSError, IOError):
                    digest = ""
                entries.append(f"{rel}:{digest}")
        for e in sorted(entries):
            h.update(e.encode("utf-8"))
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
