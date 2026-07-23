"""Task 0.8 — run-dir manager + ArtifactHandle (run isolation, invariant 10).

All mutable state is namespaced under ``runs/<run_id>/`` (staging, venv,
artifacts, events.jsonl). Artifacts are content-addressed
(``artifacts/<sha256>``) and immutable for the run's life. A run refuses to
adopt a non-empty run dir (invariant 10 / D6).

``ArtifactHandle`` is the OPAQUE token that crosses the ``WorkerPort``
(invariant 9): ``artifact:<sha256>``. It carries NO filesystem path; only a
``RunDir`` can resolve it, and only to an artifact that RunDir actually stores.
This is what keeps the port harness-neutral — an adapter (Hermes, future
Copilot) resolves the handle to its own substrate, Core never mints a path into
a port payload.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass

_HANDLE_PREFIX = "artifact:"
_SUBDIRS = ("staging", "venv", "artifacts")


@dataclass(frozen=True)
class ArtifactHandle:
    """Opaque, content-addressed reference that crosses the port."""

    id: str  # the sha256 hex of the artifact bytes

    def to_str(self) -> str:
        return f"{_HANDLE_PREFIX}{self.id}"

    @classmethod
    def from_str(cls, s: str) -> "ArtifactHandle":
        if not s.startswith(_HANDLE_PREFIX):
            raise ValueError(f"not an artifact handle: {s!r}")
        return cls(id=s[len(_HANDLE_PREFIX):])


class RunDir:
    """Isolated per-run directory; the only minter/resolver of ArtifactHandles."""

    def __init__(self, path: str, run_id: str) -> None:
        self.path = os.path.abspath(path)
        self.run_id = run_id

    @property
    def artifacts_dir(self) -> str:
        return os.path.join(self.path, "artifacts")

    @property
    def staging_dir(self) -> str:
        return os.path.join(self.path, "staging")

    @property
    def venv_dir(self) -> str:
        return os.path.join(self.path, "venv")

    @property
    def events_path(self) -> str:
        return os.path.join(self.path, "events.jsonl")

    @classmethod
    def adopt(cls, path: str, run_id: str, require_empty: bool = True) -> "RunDir":
        """Create/adopt a run dir, refusing a populated one when required."""
        rd = cls(path, run_id)
        if require_empty and os.path.isdir(rd.path):
            # Non-empty == ANY pre-existing content: a populated subdir OR a
            # stale top-level file (e.g. an events.jsonl from a prior aborted
            # run). Judging emptiness by subdirs alone would let a leftover
            # journal slip through and weaken invariant 10 (P2-1 hardening).
            for entry in os.listdir(rd.path):
                full = os.path.join(rd.path, entry)
                if os.path.isdir(full):
                    if os.listdir(full):
                        raise ValueError(
                            f"refusing to reuse non-empty run dir: {rd.path}"
                        )
                else:
                    raise ValueError(
                        f"refusing to reuse non-empty run dir: {rd.path}"
                    )
        for sub in _SUBDIRS:
            os.makedirs(os.path.join(rd.path, sub), exist_ok=True)
        return rd

    def put_artifact(self, data: bytes) -> ArtifactHandle:
        """Content-address ``data`` into ``artifacts/<sha256>`` (immutable)."""
        sha = hashlib.sha256(data).hexdigest()
        dest = os.path.join(self.artifacts_dir, sha)
        if not os.path.exists(dest):
            os.makedirs(self.artifacts_dir, exist_ok=True)
            tmp = dest + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, dest)
        return ArtifactHandle(id=sha)

    def resolve_handle(self, handle: ArtifactHandle) -> str:
        """Resolve a handle to an absolute path — only if THIS run stores it."""
        dest = os.path.join(self.artifacts_dir, handle.id)
        if not os.path.exists(dest):
            raise ValueError(
                f"handle {handle.to_str()!r} not present in run {self.run_id}"
            )
        return dest


def new_run(root: str) -> RunDir:
    """Mint a fresh, empty, isolated run dir under ``root/runs/<run_id>/``."""
    run_id = str(uuid.uuid4())
    path = os.path.join(os.path.abspath(root), "runs", run_id)
    return RunDir.adopt(path, run_id, require_empty=True)
