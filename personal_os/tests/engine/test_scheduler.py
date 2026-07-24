"""Task 3.2 — the scheduler loop: recursion + budgets + attempt ledger.

The deterministic loop that applies ``route`` to drive a goal to conclusion:
top REFINE -> [research ADMISSIBILITY child + execution HARD child] -> discharge
the execution child -> top ends AWAITING_ACCEPTANCE (never auto-DONE). Also
exercises the BLOCKED branch (a no-progress execution leaf) and the FAILED
branch (budget exhaustion).
"""

from __future__ import annotations

import pytest

from personal_os.engine.adapters.fake_worker import FakeRefiner, FakeWorker
from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
from personal_os.engine.contract.journal import EventType, Journal, replay
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.core.scheduler import Scheduler
from personal_os.engine.core.staging import stage
from personal_os.engine.validators.hard_cli import HardCliValidator
from personal_os.tests.engine.fixtures.broken_cli_fixture import fixture_root


def _top(**over):
    kw = dict(
        id="top", parent_id=None, objective="make brokencli reproducibly runnable",
        done_contract={}, admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=2, max_children=4, max_attempts=2),
        status=NodeStatus.PENDING, provenance={"depth": 0, "attempts": 0},
    )
    kw.update(over)
    return ProofObligationNode(**kw)


def _scheduler(rd):
    return Scheduler(
        run_dir=rd,
        journal=Journal(rd.events_path, run_id=rd.run_id),
        refiner=FakeRefiner(rd),
        worker=FakeWorker(rd),
        hard_validator=HardCliValidator(),
    )


def test_full_one_level_run_ends_awaiting_acceptance(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    sched = _scheduler(rd)
    outcome = sched.run(_top())

    # Top decomposed into a research (ADMISSIBILITY) + execution (HARD) child;
    # the execution child was HARD-discharged; top ends AWAITING_ACCEPTANCE.
    assert outcome.top_status is NodeStatus.AWAITING_ACCEPTANCE
    statuses = outcome.node_statuses
    exec_ids = [nid for nid in statuses if nid.endswith("-exec")]
    assert exec_ids and statuses[exec_ids[0]] is NodeStatus.HARD_DISCHARGED
    research_ids = [nid for nid in statuses if nid.endswith("-research")]
    assert research_ids and statuses[research_ids[0]] is NodeStatus.ADMISSIBILITY_PASSED


def test_top_never_auto_done(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    outcome = _scheduler(rd).run(_top())
    assert outcome.top_status is not NodeStatus.DONE


def test_no_progress_execution_leaf_reaches_blocked(tmp_path):
    from personal_os.engine.ports.worker import WorkResult
    import json

    class _BadWorker:
        def __init__(self, rd):
            self._rd = rd

        def execute(self, request):
            payload = {"target": "brokencli/cli.py", "content": "x='broken'\n"}
            h = self._rd.put_artifact(json.dumps(payload, sort_keys=True).encode())
            return WorkResult(status="ok", artifact_handles=[h],
                              evidence_proposals=[{"claim_id": "bad"}], usage={}, failure=None)

    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    sched = Scheduler(
        run_dir=rd, journal=Journal(rd.events_path, run_id=rd.run_id),
        refiner=FakeRefiner(rd), worker=_BadWorker(rd),
        hard_validator=HardCliValidator(),
    )
    outcome = sched.run(_top())
    exec_ids = [nid for nid in outcome.node_statuses if nid.endswith("-exec")]
    assert exec_ids and outcome.node_statuses[exec_ids[0]] is NodeStatus.BLOCKED


def test_budget_exhausted_branch_reaches_failed(tmp_path):
    # A top node that can only refine, with depth budget 0 -> the refiner's
    # children can't go deeper; an inadmissible refine leaves no exec child and
    # the top exhausts budget -> FAILED.
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    sched = Scheduler(
        run_dir=rd, journal=Journal(rd.events_path, run_id=rd.run_id),
        refiner=FakeRefiner(rd, make_inadmissible=True), worker=FakeWorker(rd),
        hard_validator=HardCliValidator(),
    )
    outcome = sched.run(_top(budget=Budget(max_depth=1, max_children=2, max_attempts=1)))
    assert outcome.top_status is NodeStatus.FAILED


def test_run_refuses_to_rerun_attempt_exhausted_node(tmp_path):
    # F13/sol-7: the attempt ledger is the JOURNAL. If a node already has
    # ATTEMPT events >= max_attempts in the journal, a fresh run() must NOT
    # start another attempt (the router sees the projected count, not a
    # zeroed in-memory provenance).
    from personal_os.engine.contract.journal import Journal, EventType
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    # Pre-seed the journal with an exhausted attempt ledger for the top.
    j = Journal(rd.events_path, run_id=rd.run_id)
    j.append(EventType.NODE_CREATED, node_id="top", payload={"status": "pending"})
    j.append(EventType.ATTEMPT, node_id="top", payload={"attempt": 1})
    top = _top(budget=Budget(max_depth=2, max_children=4, max_attempts=1))
    outcome = _scheduler(rd).run(top)
    # With attempts already at the cap, the run must FAIL (no-progress), not
    # refine/discharge a second time.
    assert outcome.top_status is NodeStatus.FAILED


def test_run_is_journaled(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _scheduler(rd).run(_top())
    proj = replay(rd.events_path)
    # Journal has the top and both children.
    assert "top" in proj.node_status
    assert any(k.endswith("-exec") for k in proj.node_status)


def test_execution_child_routed_not_role_dispatched(tmp_path, monkeypatch):
    # F10/sol-inv5: the execution child must reach discharge THROUGH route(),
    # not by the scheduler hardcoding the verb from child["role"]. If route()
    # says something other than DISCHARGE for that node, the scheduler must NOT
    # discharge it. We assert route() is consulted for the execution child.
    import personal_os.engine.core.scheduler as sched_mod

    routed_nodes = []
    real_route = sched_mod.route

    def spy_route(node, projection):
        routed_nodes.append(node.id)
        return real_route(node, projection)

    monkeypatch.setattr(sched_mod, "route", spy_route)
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _scheduler(rd).run(_top())
    # The execution child id must have been passed through route().
    assert any(nid.endswith("-exec") for nid in routed_nodes), routed_nodes


@pytest.mark.parametrize("status", [status for status in NodeStatus
                                     if status is not NodeStatus.PENDING])
def test_run_noops_without_journaling_for_non_schedulable_status(tmp_path, status):
    """Terminal and transitional nodes retain their authoritative status."""
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    outcome = _scheduler(rd).run(_top(status=status))

    assert outcome.top_status is status
    assert replay(rd.events_path).event_count == 0


def test_second_run_uses_terminal_journal_status_and_does_no_work(tmp_path):
    """A stale PENDING object cannot restart a journal-terminal node."""
    class _CountingPort:
        def __init__(self, delegate):
            self.delegate = delegate
            self.calls = 0

        def execute(self, request):
            self.calls += 1
            return self.delegate.execute(request)

    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    refiner = _CountingPort(FakeRefiner(rd))
    worker = _CountingPort(FakeWorker(rd))
    sched = Scheduler(
        run_dir=rd, journal=Journal(rd.events_path, run_id=rd.run_id),
        refiner=refiner, worker=worker, hard_validator=HardCliValidator(),
    )
    stale_top = _top()
    first = sched.run(stale_top)
    assert first.top_status is NodeStatus.AWAITING_ACCEPTANCE
    calls_before = (refiner.calls, worker.calls)
    events_before = replay(rd.events_path).event_count

    second = sched.run(stale_top)

    assert second.top_status is NodeStatus.AWAITING_ACCEPTANCE
    assert (refiner.calls, worker.calls) == calls_before
    assert replay(rd.events_path).event_count == events_before


def test_execution_child_attempt_cap_survives_restart(tmp_path):
    """A journal-exhausted execution child cannot discharge again."""
    class _CountingWorker:
        calls = 0

        def execute(self, request):
            self.calls += 1
            raise AssertionError("attempt-exhausted child reached worker")

    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    journal = Journal(rd.events_path, run_id=rd.run_id)
    journal.append(EventType.NODE_CREATED, node_id="top",
                   payload={"status": NodeStatus.PENDING.value})
    journal.append(EventType.ATTEMPT, node_id="top-exec", payload={"attempt": 1})
    worker = _CountingWorker()
    sched = Scheduler(
        run_dir=rd, journal=journal, refiner=FakeRefiner(rd), worker=worker,
        hard_validator=HardCliValidator(),
    )

    outcome = sched.run(_top())

    assert outcome.node_statuses["top-exec"] is NodeStatus.FAILED
    assert worker.calls == 0
    assert replay(rd.events_path).attempt_counts["top-exec"] == 1
