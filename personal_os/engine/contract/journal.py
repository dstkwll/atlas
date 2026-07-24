"""Task 0.6 — append-only, crash-consistent per-run journal + projection.

**One journal file per run** (``runs/<run_id>/events.jsonl``); no cross-run
interleaving (Skeptic D7). The journal is authoritative TRUTH; node lifecycle
is a rebuildable projection reconciled on resume (invariant 7).

Write discipline: each event is a single serialized ``O_APPEND`` write of one
JSON line, followed by ``flush() + os.fsync()`` (invariant 8 durability).
Documented ordering rule for callers: **artifact bytes must be fsync'd BEFORE
a ``RECEIPT_WRITTEN`` event is appended** (invariant 8/E1) — this module gives
callers a durable append primitive; sequencing is enforced at the call site
(discharge core, Task 1.6).

Reader/replay (0.6b): tolerate a truncated final line (crash mid-write), dedup
by ``event_id`` (idempotent replay), and rebuild a ``LifecycleProjection``.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    NODE_CREATED = "NODE_CREATED"
    NODE_STATUS = "NODE_STATUS"
    CHILDREN_ADDED = "CHILDREN_ADDED"
    RECEIPT_WRITTEN = "RECEIPT_WRITTEN"
    ATTEMPT = "ATTEMPT"
    ESCALATED = "ESCALATED"
    RESIDUAL_ADDED = "RESIDUAL_ADDED"
    RUN_COMPLETED = "RUN_COMPLETED"


# Events that terminate a run for active_run_id purposes.
_TERMINAL_TYPES = {EventType.RUN_COMPLETED.value}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Journal:
    """Durable, serialized append-only writer for ONE run's event log."""

    def __init__(self, path: str, run_id: str) -> None:
        self.path = path
        self.run_id = run_id
        self._lock = threading.Lock()
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._parent = parent
        # F5: fsync the parent directory once so the journal file's directory
        # entry is itself durable (a durable file with a non-durable dir entry
        # can vanish on crash).
        self._fsync_parent_dir(parent)

    @staticmethod
    def _fsync_parent_dir(parent: str) -> None:
        if not parent:
            return
        try:
            dfd = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except OSError:
            # Some filesystems disallow directory fsync; best-effort.
            pass

    def append(
        self,
        event_type: EventType,
        node_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Append one durable event line; returns its ``event_id``.

        A single ``O_APPEND`` write of one JSON line + ``flush()`` +
        ``os.fsync()`` so a crash can only ever leave a torn *final* line,
        never a corrupted earlier one. The write LOOPS until every byte lands
        (``os.write`` may return a short count — F5) so a partial write can
        never convert into malformed interior data.
        """
        event_id = str(uuid.uuid4())
        event = {
            "event_id": event_id,
            "ts": _now_iso(),
            "run_id": self.run_id,
            "node_id": node_id,
            "type": EventType(event_type).value,
            "payload": payload or {},
        }
        data = (json.dumps(event, sort_keys=True) + "\n").encode("utf-8")
        with self._lock:
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            created = False
            try:
                fd = os.open(self.path, flags | os.O_EXCL, 0o644)
                created = True
            except FileExistsError:
                fd = os.open(self.path, flags, 0o644)
            try:
                view = memoryview(data)
                total = 0
                while total < len(data):
                    written = os.write(fd, view[total:])
                    if written <= 0:
                        raise OSError("journal write made no progress")
                    total += written
                os.fsync(fd)
            finally:
                os.close(fd)
            if created:
                self._fsync_parent_dir(self._parent)
        return event_id


@dataclass
class LifecycleProjection:
    """Rebuilt-from-journal view of node lifecycle (never inferred elsewhere)."""

    node_status: Dict[str, str] = field(default_factory=dict)
    active_run_id: Optional[str] = None
    event_count: int = 0
    receipts: Dict[str, list] = field(default_factory=dict)
    # F13: per-node ATTEMPT tally, so the attempt budget is enforceable from the
    # journal (the ledger is the journal, not mutable in-memory provenance).
    attempt_counts: Dict[str, int] = field(default_factory=dict)


def replay(path: str) -> LifecycleProjection:
    """Rebuild the projection from a run's journal.

    Tolerates a truncated final line, dedups by ``event_id`` (idempotent), and
    tracks ``active_run_id`` = the run whose start event has no terminal event.
    """
    proj = LifecycleProjection()
    seen: set = set()
    started_runs: list = []
    terminated_runs: set = set()

    if not os.path.exists(path):
        return proj

    # F4: read BINARY and split on newline. A crash can tear a multibyte UTF-8
    # sequence in the final line; decoding the whole file as text would raise
    # UnicodeDecodeError and bypass the JSON handler. Decode each COMPLETE line
    # individually; a torn/undecodable final fragment is ignored, not fatal.
    with open(path, "rb") as f:
        blob = f.read()

    raw_lines = blob.split(b"\n")
    for raw_bytes in raw_lines:
        if not raw_bytes.strip():
            continue
        try:
            raw = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            # Torn multibyte sequence (crash mid-write): ignore this fragment.
            continue
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            # A torn final line from a crash mid-write: ignore, not fatal.
            continue
        eid = ev.get("event_id")
        if not eid or eid in seen:
            continue
        seen.add(eid)
        proj.event_count += 1

        run_id = ev.get("run_id")
        etype = ev.get("type")
        node_id = ev.get("node_id")
        payload = ev.get("payload") or {}

        if run_id and run_id not in started_runs:
            started_runs.append(run_id)
        if etype in _TERMINAL_TYPES and run_id:
            terminated_runs.add(run_id)

        if etype in (EventType.NODE_CREATED.value, EventType.NODE_STATUS.value):
            status = payload.get("status")
            if node_id and status:
                proj.node_status[node_id] = status
        elif etype == EventType.RECEIPT_WRITTEN.value:
            if node_id:
                proj.receipts.setdefault(node_id, []).append(payload)
        elif etype == EventType.ATTEMPT.value:
            if node_id:
                proj.attempt_counts[node_id] = proj.attempt_counts.get(node_id, 0) + 1

    # active_run_id = last started run with no terminal event.
    for run_id in reversed(started_runs):
        if run_id not in terminated_runs:
            proj.active_run_id = run_id
            break

    return proj
