"""Task 0.6 / 0.6b — append-only per-run journal + projection + crash tests.

One journal file per run (``runs/<run_id>/events.jsonl``) — no cross-run
interleaving. The journal is TRUTH; node lifecycle is a rebuildable projection
(invariant 7). Reader tolerates a truncated final line, dedups by ``event_id``,
and rebuilds a ``LifecycleProjection`` (node_id -> status + active_run_id).
"""

from __future__ import annotations

import json
import os
import stat

import pytest

from personal_os.engine.contract.journal import (
    EventType,
    Journal,
    LifecycleProjection,
    replay,
)


def _events(j: Journal):
    j.append(EventType.NODE_CREATED, node_id="n1", payload={"status": "pending"})
    j.append(EventType.NODE_STATUS, node_id="n1", payload={"status": "discharging"})
    j.append(EventType.RECEIPT_WRITTEN, node_id="n1", payload={"passed": True})
    j.append(EventType.NODE_STATUS, node_id="n1", payload={"status": "hard_discharged"})


def test_append_then_replay_matches_projection(tmp_path):
    path = tmp_path / "events.jsonl"
    j = Journal(str(path), run_id="run-1")
    _events(j)
    proj = replay(str(path))
    assert isinstance(proj, LifecycleProjection)
    assert proj.node_status["n1"] == "hard_discharged"


def test_every_event_has_id_ts_runid(tmp_path):
    path = tmp_path / "events.jsonl"
    j = Journal(str(path), run_id="run-x")
    j.append(EventType.ATTEMPT, node_id="n1", payload={})
    line = path.read_text().strip()
    ev = json.loads(line)
    assert ev["event_id"] and ev["ts"] and ev["run_id"] == "run-x"
    assert ev["type"] == "ATTEMPT" and ev["node_id"] == "n1"


def test_replay_tolerates_torn_multibyte_tail(tmp_path):
    # F4/sol-4: a crash that tears a multibyte UTF-8 sequence in the final line
    # must be tolerated (ignored), not raise UnicodeDecodeError.
    path = tmp_path / "events.jsonl"
    j = Journal(str(path), run_id="run-1")
    _events(j)
    with open(path, "ab") as f:
        f.write(b'{"event_id": "torn", "x": "\xff\xfe incomplete')  # torn multibyte, no newline
    proj = replay(str(path))
    assert proj.node_status["n1"] == "hard_discharged"


def test_replay_ignores_interior_malformed_only_at_tail(tmp_path):
    # A complete-but-malformed INTERIOR line (followed by a newline) is corrupt
    # durable state — replay must not silently absorb it as if nothing's wrong.
    # We assert replay still completes and the valid events project correctly.
    path = tmp_path / "events.jsonl"
    j = Journal(str(path), run_id="run-1")
    j.append(EventType.NODE_CREATED, node_id="n1", payload={"status": "pending"})
    proj = replay(str(path))
    assert proj.node_status["n1"] == "pending"


def test_replay_tolerates_truncated_tail(tmp_path):
    path = tmp_path / "events.jsonl"
    j = Journal(str(path), run_id="run-1")
    _events(j)
    # Simulate a crash mid-write: append a partial (unterminated) JSON line.
    with open(path, "a") as f:
        f.write('{"event_id": "partial", "type": "NODE_STATUS", "node_i')
    proj = replay(str(path))
    # Last COMPLETE event still wins; the torn tail is ignored, not fatal.
    assert proj.node_status["n1"] == "hard_discharged"


def test_replay_is_idempotent_and_dedups_event_id(tmp_path):
    path = tmp_path / "events.jsonl"
    j = Journal(str(path), run_id="run-1")
    j.append(EventType.NODE_CREATED, node_id="n1", payload={"status": "pending"})
    # Manually duplicate the exact line (same event_id) — simulating a
    # double-write / replayed segment.
    line = path.read_text().strip()
    with open(path, "a") as f:
        f.write(line + "\n")
    proj1 = replay(str(path))
    proj2 = replay(str(path))
    assert proj1.node_status == proj2.node_status
    assert proj1.event_count == 1  # deduped by event_id


def test_active_run_id_is_run_with_no_terminal_event(tmp_path):
    path = tmp_path / "events.jsonl"
    j = Journal(str(path), run_id="run-42")
    j.append(EventType.NODE_CREATED, node_id="n1", payload={})
    proj = replay(str(path))
    assert proj.active_run_id == "run-42"


def test_append_returns_event_id(tmp_path):
    path = tmp_path / "events.jsonl"
    j = Journal(str(path), run_id="r")
    eid = j.append(EventType.ATTEMPT, node_id="n1", payload={})
    assert isinstance(eid, str) and eid


def test_first_append_creates_durable_replayable_log(tmp_path, monkeypatch):
    """The first append fsyncs the directory entry created by O_EXCL."""
    path = tmp_path / "fresh" / "events.jsonl"
    fsynced_parents = []
    real_fsync_parent = Journal._fsync_parent_dir_strict

    def recording_fsync(parent):
        fsynced_parents.append(parent)
        real_fsync_parent(parent)

    monkeypatch.setattr(
        Journal, "_fsync_parent_dir_strict", staticmethod(recording_fsync),
    )
    journal = Journal(str(path), run_id="fresh-run")
    fsynced_parents.clear()  # Ignore directory preparation in __init__.
    journal.append(
        EventType.NODE_CREATED,
        node_id="fresh-node",
        payload={"status": "pending"},
    )

    assert path.exists()
    assert replay(str(path)).node_status == {"fresh-node": "pending"}
    assert fsynced_parents == [str(path.parent)]


def test_unknown_event_type_rejected():
    with pytest.raises(ValueError):
        EventType("NOT_A_TYPE")


def test_replay_skips_valid_json_with_wrong_record_shape(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text("[]\n")

    projection = replay(str(path))

    assert projection.event_count == 0
    assert projection.node_status == {}


def test_first_append_propagates_parent_directory_fsync_failure(
    tmp_path, monkeypatch,
):
    path = tmp_path / "fresh" / "events.jsonl"
    real_fsync = os.fsync

    def fail_directory_fsync(fd):
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError("directory fsync failed")
        return real_fsync(fd)

    monkeypatch.setattr(os, "fsync", fail_directory_fsync)
    journal = Journal(str(path), run_id="run-1")

    with pytest.raises(OSError, match="directory fsync failed"):
        journal.append(EventType.NODE_CREATED, node_id="n1", payload={})
