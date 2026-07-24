"""Task 1.6 / 1.6b — discharge core (the Phase 1 end-to-end milestone).

``discharge(node, worker, validator, run_dir, journal)`` runs the full HARD
leaf: build a WorkRequest, ``worker.execute`` (conformance-checked), stage +
``apply_patch`` the proposal onto the STAGED tree, ``validator.validate``, then
— in the invariant-8 order — fsync the receipt artifact BEFORE appending the
``RECEIPT_WRITTEN`` journal event, and set status ``HARD_DISCHARGED`` iff
``can_discharge_hard(receipt)``. Never trusts stdout: it verifies the patched
artifact is actually present at its handle.

1.6b: a ``BadFakeWorker`` proposing a wrong/no patch must leave the node NOT
``HARD_DISCHARGED`` (the validator can reject, not just rubber-stamp).
"""

from __future__ import annotations

import json
import os

import pytest

from personal_os.engine.adapters.fake_worker import FakeWorker
from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
from personal_os.engine.contract.journal import EventType, Journal, replay
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.core.discharge import discharge
from personal_os.engine.core.staging import stage
from personal_os.engine.ports.worker import WorkResult
from personal_os.engine.validators.hard_cli import HardCliValidator
from personal_os.tests.engine.fixtures.broken_cli_fixture import fixture_root


def _node():
    return ProofObligationNode(
        id="leaf-1", parent_id="top", objective="make brokencli runnable",
        done_contract={"target": "brokencli/cli.py"}, admissible_evidence=[],
        validator_ref="hard_cli", validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=1, max_children=0, max_attempts=1),
        status=NodeStatus.PENDING, provenance={},
    )


class _BadFakeWorker:
    """Proposes a patch that does NOT fix the bug (still broken import)."""

    def __init__(self, run_dir):
        self._rd = run_dir

    def execute(self, request):
        payload = {"target": "brokencli/cli.py", "content": "x = 'still broken'\n"}
        h = self._rd.put_artifact(json.dumps(payload, sort_keys=True).encode())
        return WorkResult(status="ok", artifact_handles=[h],
                          evidence_proposals=[{"claim_id": "bad"}], usage={}, failure=None)


class _EmptyHandleWorker:
    """Returns an EXECUTE result with no proposed patch handle."""

    def execute(self, request):
        return WorkResult(status="ok", artifact_handles=[],
                          evidence_proposals=[], usage={}, failure=None)


def test_discharge_hard_leaf_end_to_end(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    journal = Journal(rd.events_path, run_id=rd.run_id)
    node = _node()

    result = discharge(node, FakeWorker(rd), HardCliValidator(), rd, journal)

    assert result.receipt.passed is True
    assert result.status is NodeStatus.HARD_DISCHARGED
    # Journal replay shows the receipt event.
    proj = replay(rd.events_path)
    assert "leaf-1" in proj.receipts
    assert proj.node_status["leaf-1"] == NodeStatus.HARD_DISCHARGED.value
    # Artifact verified at handle (not just stdout).
    assert result.patched_ok is True


def test_discharge_negative_bad_patch_not_hard_discharged(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    journal = Journal(rd.events_path, run_id=rd.run_id)
    node = _node()

    result = discharge(node, _BadFakeWorker(rd), HardCliValidator(), rd, journal)

    assert result.receipt.passed is False
    assert result.status is not NodeStatus.HARD_DISCHARGED
    proj = replay(rd.events_path)
    assert proj.node_status["leaf-1"] != NodeStatus.HARD_DISCHARGED.value


def test_discharge_writes_receipt_artifact_before_event(tmp_path):
    # Invariant 8: the receipt artifact must be durable before the journal
    # event referencing it. We assert the receipt artifact exists and the
    # RECEIPT_WRITTEN event carries its handle.
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    journal = Journal(rd.events_path, run_id=rd.run_id)
    result = discharge(_node(), FakeWorker(rd), HardCliValidator(), rd, journal)

    proj = replay(rd.events_path)
    payloads = proj.receipts["leaf-1"]
    assert payloads
    receipt_handle = payloads[0].get("receipt_handle")
    assert receipt_handle
    # The referenced artifact is present on disk (fsynced before the event).
    sha = receipt_handle.split(":", 1)[1]
    assert os.path.exists(os.path.join(rd.artifacts_dir, sha))


def test_failed_patch_landing_blocks_hard_discharge(tmp_path, monkeypatch):
    """A passing receipt cannot discharge a patch Core did not verify."""
    import importlib

    discharge_module = importlib.import_module("personal_os.engine.core.discharge")
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    journal = Journal(rd.events_path, run_id=rd.run_id)
    monkeypatch.setattr(discharge_module, "_verify_patch_landed",
                        lambda *args: False)

    result = discharge_module.discharge(
        _node(), FakeWorker(rd), HardCliValidator(), rd, journal,
    )

    assert result.receipt.passed is True
    assert result.patched_ok is False
    assert result.status is NodeStatus.BLOCKED
    assert replay(rd.events_path).node_status["leaf-1"] == NodeStatus.BLOCKED.value


def test_discharge_request_attempt_follows_journal_count(tmp_path):
    """Worker attempts are numbered from the durable journal ledger."""
    class _CapturingWorker:
        def __init__(self, delegate):
            self.delegate = delegate
            self.attempt = None

        def execute(self, request):
            self.attempt = request.attempt
            return self.delegate.execute(request)

    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    journal = Journal(rd.events_path, run_id=rd.run_id)
    journal.append(EventType.ATTEMPT, node_id="leaf-1", payload={"attempt": 1})
    worker = _CapturingWorker(FakeWorker(rd))

    discharge(_node(), worker, HardCliValidator(), rd, journal)

    assert worker.attempt == 2


def test_discharge_rejects_missing_patch_handle_before_indexing(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    journal = Journal(rd.events_path, run_id=rd.run_id)

    with pytest.raises(AssertionError):
        discharge(_node(), _EmptyHandleWorker(), HardCliValidator(), rd, journal)
