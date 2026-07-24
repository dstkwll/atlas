"""Task 3.3 — crash-resume (bounded, verification-only).

On resume the scheduler rebuilds the ``LifecycleProjection`` from the journal,
then re-verifies the receipts on the resume frontier as VERIFICATION-ONLY:
re-hash the receipted artifacts cheaply; do not re-run the HARD validator unless
artifacts are missing/changed; never consume ``max_attempts``. A failed
re-verify marks the node ``BLOCKED`` with ``RESUME_REVERIFY_FAILED`` and never
re-enters ``DISCHARGING`` (invariant 8 / Skeptic D3).
"""

from __future__ import annotations

import json
import os

from personal_os.engine.adapters.fake_worker import FakeRefiner, FakeWorker
from personal_os.engine.contract.enums import NodeStatus
from personal_os.engine.contract.journal import Journal, replay
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.enums import ValidationStrength
from personal_os.engine.contract.run_dir import RunDir, new_run
from personal_os.engine.core.scheduler import Scheduler, resume
from personal_os.engine.core.staging import stage
from personal_os.engine.validators.hard_cli import HardCliValidator
from personal_os.tests.engine.fixtures.broken_cli_fixture import fixture_root


def _top():
    return ProofObligationNode(
        id="top", parent_id=None, objective="make brokencli reproducibly runnable",
        done_contract={}, admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=2, max_children=4, max_attempts=2),
        status=NodeStatus.PENDING, provenance={"depth": 0, "attempts": 0},
    )


def _run_once(rd):
    sched = Scheduler(
        run_dir=rd, journal=Journal(rd.events_path, run_id=rd.run_id),
        refiner=FakeRefiner(rd), worker=FakeWorker(rd),
        hard_validator=HardCliValidator(),
    )
    return sched.run(_top())


def test_resume_after_truncated_tail_completes(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run_once(rd)
    # Simulate a crash: append a torn final line to the journal.
    with open(rd.events_path, "a") as f:
        f.write('{"event_id": "torn", "type": "NODE_ST')
    # Resume rebuilds the projection; the torn line is ignored, no dup.
    outcome = resume(rd, HardCliValidator())
    assert outcome.top_status is NodeStatus.AWAITING_ACCEPTANCE


def test_resume_reverifies_and_holds_hard_discharged(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run_once(rd)
    outcome = resume(rd, HardCliValidator())
    exec_ids = [nid for nid in outcome.node_statuses if nid.endswith("-exec")]
    assert exec_ids
    # Re-verify passed (artifacts intact) -> stays HARD_DISCHARGED.
    assert outcome.node_statuses[exec_ids[0]] is NodeStatus.HARD_DISCHARGED


def test_resume_deleted_artifact_blocks_not_stale_done(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    outcome0 = _run_once(rd)
    exec_ids = [nid for nid in outcome0.node_statuses if nid.endswith("-exec")]
    exec_id = exec_ids[0]

    # Find the exec node's receipt artifact from the journal and DELETE it.
    proj = replay(rd.events_path)
    receipt_handle = proj.receipts[exec_id][0]["receipt_handle"]
    sha = receipt_handle.split(":", 1)[1]
    os.remove(os.path.join(rd.artifacts_dir, sha))

    # Resume must detect the missing receipt artifact and BLOCK, not report a
    # stale success.
    outcome = resume(rd, HardCliValidator())
    assert outcome.node_statuses[exec_id] is NodeStatus.BLOCKED
    # And the reason is recorded.
    proj2 = replay(rd.events_path)
    assert proj2.node_status[exec_id] == NodeStatus.BLOCKED.value


def test_resume_deleted_referenced_artifact_blocks(tmp_path):
    # P2-3: even if the receipt BLOB is intact, deleting an artifact the receipt
    # REFERENCES (a captured stdout/stderr/patch in receipt.artifact_hashes)
    # must trip re-verify -> BLOCKED (not a stale success).
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    outcome0 = _run_once(rd)
    exec_id = [n for n in outcome0.node_statuses if n.endswith("-exec")][0]

    proj = replay(rd.events_path)
    receipt_handle = proj.receipts[exec_id][0]["receipt_handle"]
    sha = receipt_handle.split(":", 1)[1]
    # Read the receipt JSON, pick a REFERENCED artifact hash, delete THAT (leave
    # the receipt blob itself intact).
    with open(os.path.join(rd.artifacts_dir, sha)) as f:
        receipt = json.load(f)
    referenced = list(receipt["artifact_hashes"].values())
    assert referenced
    victim = referenced[0]
    os.remove(os.path.join(rd.artifacts_dir, victim))

    outcome = resume(rd, HardCliValidator())
    assert outcome.node_statuses[exec_id] is NodeStatus.BLOCKED


def test_resume_does_not_consume_attempts(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run_once(rd)
    # Count ATTEMPT events before and after resume; resume must add none.
    def _attempts():
        with open(rd.events_path) as f:
            return sum(1 for line in f if line.strip() and
                       json.loads(line)["type"] == "ATTEMPT")
    before = _attempts()
    resume(rd, HardCliValidator())
    after = _attempts()
    assert after == before  # verification-only, no new attempts
