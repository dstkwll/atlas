"""Task 0.6 / 0.6b — append-only per-run journal + projection + crash tests.

One journal file per run (``runs/<run_id>/events.jsonl``) — no cross-run
interleaving. The journal is TRUTH; node lifecycle is a rebuildable projection
(invariant 7). Reader tolerates a truncated final line, dedups by ``event_id``,
and rebuilds a ``LifecycleProjection`` (node_id -> status + active_run_id).
"""

from __future__ import annotations

import json

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


def test_unknown_event_type_rejected():
    with pytest.raises(ValueError):
        EventType("NOT_A_TYPE")
