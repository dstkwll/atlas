"""Task 4.2 — HITL acceptance: the SINGLE writer of DONE (Panel P1-C2).

``mark_done(node, projection)`` is the ONLY code in the engine that sets
``DONE``. It asserts the prior state is ``AWAITING_ACCEPTANCE`` and raises
otherwise — so DONE can never be reached from any other state, by any other
path. No SEMANTIC assessor in v0 (Simplifier S3).
"""

from __future__ import annotations

import pytest

from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.core.acceptance import mark_done


def _node(status):
    return ProofObligationNode(
        id="top", parent_id=None, objective="obj", done_contract={},
        admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=1, max_children=0, max_attempts=1),
        status=status, provenance={},
    )


def test_mark_done_from_awaiting_acceptance():
    n = _node(NodeStatus.AWAITING_ACCEPTANCE)
    done = mark_done(n)
    assert done.status is NodeStatus.DONE


def test_mark_done_from_any_other_state_raises():
    for bad in (NodeStatus.PENDING, NodeStatus.HARD_DISCHARGED,
                NodeStatus.BLOCKED, NodeStatus.FAILED, NodeStatus.DONE,
                NodeStatus.ADMISSIBILITY_PASSED, NodeStatus.ESCALATED):
        with pytest.raises(ValueError):
            mark_done(_node(bad))


def test_done_has_exactly_one_writer_in_the_codebase():
    # grep-guard (invariant 6): NodeStatus.DONE is only ASSIGNED to a node's
    # status in acceptance.py. Search the engine source for assignments.
    import os
    import re

    engine_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..", "engine",
    )
    engine_dir = os.path.normpath(engine_dir)
    writers = []
    for root, _dirs, files in os.walk(engine_dir):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            with open(path) as f:
                text = f.read()
            # Any construction of the DONE status that gets assigned/returned:
            # covers `status = NodeStatus.DONE`, `NodeStatus("done")`, and
            # `replace(..., status=NodeStatus.DONE)`. Semantic, not just one
            # pattern (P3 hardening).
            for m in re.finditer(r"status\s*=\s*NodeStatus\.DONE", text):
                writers.append(path)
            for m in re.finditer(r'NodeStatus\(\s*["\']done["\']\s*\)', text):
                writers.append(path)
    # The only real status setter is in acceptance.py.
    assert all("acceptance.py" in w for w in writers), writers


def test_accept_run_is_journal_authoritative(tmp_path):
    # F14/sol-3: accept() must re-read the journal itself, not trust a caller's
    # in-memory status. A real AWAITING_ACCEPTANCE top in the journal accepts.
    from personal_os.engine.contract.journal import Journal, EventType, replay
    from personal_os.engine.contract.run_dir import new_run
    from personal_os.engine.core.acceptance import accept

    rd = new_run(str(tmp_path))
    j = Journal(rd.events_path, run_id=rd.run_id)
    j.append(EventType.NODE_CREATED, node_id="top", payload={"status": "pending"})
    j.append(EventType.NODE_STATUS, node_id="top",
             payload={"status": NodeStatus.AWAITING_ACCEPTANCE.value})
    status = accept(rd, "top")
    assert status is NodeStatus.DONE
    # The DONE transition is journaled — a fresh replay sees DONE.
    assert replay(rd.events_path).node_status["top"] == NodeStatus.DONE.value


def test_accept_refuses_when_journal_says_blocked(tmp_path):
    # If resume journaled the top BLOCKED, accept() must refuse even if an
    # earlier AWAITING_ACCEPTANCE event exists (last-writer-wins from journal).
    from personal_os.engine.contract.journal import Journal, EventType
    from personal_os.engine.contract.run_dir import new_run
    from personal_os.engine.core.acceptance import accept

    rd = new_run(str(tmp_path))
    j = Journal(rd.events_path, run_id=rd.run_id)
    j.append(EventType.NODE_STATUS, node_id="top",
             payload={"status": NodeStatus.AWAITING_ACCEPTANCE.value})
    j.append(EventType.NODE_STATUS, node_id="top",
             payload={"status": NodeStatus.BLOCKED.value})
    with pytest.raises(ValueError):
        accept(rd, "top")
