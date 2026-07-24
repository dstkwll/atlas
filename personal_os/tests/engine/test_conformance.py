"""Task 1.7 — shared WorkResult contract oracle.

``assert_workresult_contract(result, run_dir)`` is the ONE oracle both the
FakeWorker (now) and the real HermesWorker (Phase 2) must pass. It asserts a
``WorkResult`` is schema-valid: status in the allowed set, artifact handles
resolve inside the run, evidence_proposals well-formed, and — critically — NO
receipt / pass bit is present (invariant 1). A malformed result raises.
"""

from __future__ import annotations

import pytest

from personal_os.engine.adapters.fake_worker import FakeWorker
from personal_os.engine.contract.run_dir import ArtifactHandle, new_run
from personal_os.engine.ports.conformance import assert_workresult_contract
from personal_os.engine.ports.worker import WorkKind, WorkRequest, WorkResult


def _req(rd):
    return WorkRequest(
        kind=WorkKind.EXECUTE, run_id=rd.run_id, node_id="n1", attempt=1,
        objective="fix", contract={"target": "brokencli/cli.py"},
    )


def test_fake_worker_output_passes_oracle(tmp_path):
    rd = new_run(str(tmp_path))
    result = FakeWorker(rd).execute(_req(rd))
    # Should not raise.
    assert_workresult_contract(result, rd)


def test_unresolvable_handle_fails_oracle(tmp_path):
    rd = new_run(str(tmp_path))
    bad = WorkResult(status="ok", artifact_handles=[ArtifactHandle("f" * 64)],
                     evidence_proposals=[], usage={}, failure=None)
    with pytest.raises(AssertionError):
        assert_workresult_contract(bad, rd)


def test_bad_status_fails_oracle(tmp_path):
    rd = new_run(str(tmp_path))
    h = rd.put_artifact(b"x")
    bad = WorkResult(status="not-a-status", artifact_handles=[h],
                     evidence_proposals=[], usage={}, failure=None)
    with pytest.raises(AssertionError):
        assert_workresult_contract(bad, rd)


def test_malformed_evidence_proposal_fails_oracle(tmp_path):
    rd = new_run(str(tmp_path))
    h = rd.put_artifact(b"x")
    bad = WorkResult(status="ok", artifact_handles=[h],
                     evidence_proposals=[{"no_claim_id": True}], usage={}, failure=None)
    with pytest.raises(AssertionError):
        assert_workresult_contract(bad, rd)


def test_receipt_field_smuggled_in_fails_oracle(tmp_path):
    rd = new_run(str(tmp_path))
    h = rd.put_artifact(b"x")
    result = WorkResult(status="ok", artifact_handles=[h], evidence_proposals=[],
                        usage={}, failure=None)
    d = result.to_dict()
    d["receipt"] = {"passed": True}  # a worker trying to self-certify
    with pytest.raises(AssertionError):
        assert_workresult_contract(d, rd)


def test_nested_self_certification_outside_evidence_fails_oracle(tmp_path):
    """Forbidden keys are rejected anywhere in the normalized result."""
    rd = new_run(str(tmp_path))
    h = rd.put_artifact(b"x")
    bad = WorkResult(status="ok", artifact_handles=[h], evidence_proposals=[],
                     usage={"provider": {"passed": True}}, failure=None)

    with pytest.raises(AssertionError):
        assert_workresult_contract(bad, rd)


def test_normal_result_with_nested_non_certification_payload_passes(tmp_path):
    rd = new_run(str(tmp_path))
    h = rd.put_artifact(b"x")
    valid = WorkResult(
        status="ok", artifact_handles=[h],
        evidence_proposals=[{"claim_id": "observed", "details": {"count": 1}}],
        usage={"provider": {"tokens": 12}}, failure=None,
    )

    assert_workresult_contract(valid, rd)


def test_non_list_evidence_proposals_fails_with_assertion(tmp_path):
    rd = new_run(str(tmp_path))
    malformed = {
        "status": "ok",
        "artifact_handles": [],
        "evidence_proposals": None,
        "usage": {},
        "failure": None,
    }
    with pytest.raises(AssertionError):
        assert_workresult_contract(malformed, rd)


def test_execute_result_requires_at_least_one_patch_handle(tmp_path):
    rd = new_run(str(tmp_path))
    result = WorkResult(
        status="ok", artifact_handles=[], evidence_proposals=[],
        usage={}, failure=None,
    )
    with pytest.raises(AssertionError):
        assert_workresult_contract(result, rd, require_patch_handle=True)
