"""Task 1.1 — WorkerPort + WorkRequest/WorkResult (handles, not paths).

The port is harness-neutral (invariant 9): payloads carry opaque
``ArtifactHandle``s, never absolute paths. ``WorkResult`` carries NO receipt
and NO pass bit — a worker proposes artifacts + evidence; only Core mints
receipts (invariant 1).
"""

from __future__ import annotations

import pytest

from personal_os.engine.contract.run_dir import ArtifactHandle
from personal_os.engine.ports.worker import (
    WorkKind,
    WorkerPort,
    WorkRequest,
    WorkResult,
)


def _req():
    return WorkRequest(
        kind=WorkKind.EXECUTE,
        run_id="run-1",
        node_id="n1",
        attempt=1,
        objective="fix the CLI",
        contract={"kind": "cli_reproducible"},
        input_handles=[ArtifactHandle("aaa")],
        output_handles=[ArtifactHandle("bbb")],
        constraints={"deadline_s": 60, "no_external_actions": True},
    )


def test_workrequest_round_trip():
    r = _req()
    assert WorkRequest.from_dict(r.to_dict()).to_dict() == r.to_dict()


def test_workrequest_kind_is_harness_neutral_verb():
    assert {k.name for k in WorkKind} == {"REFINE", "EXECUTE", "SYNTHESIZE"}


def test_workresult_has_no_receipt_or_pass_bit():
    res = WorkResult(
        status="ok",
        artifact_handles=[ArtifactHandle("ccc")],
        evidence_proposals=[],
        usage={},
        failure=None,
    )
    d = res.to_dict()
    assert "receipt" not in d
    assert "passed" not in d
    assert "pass" not in d


def test_workresult_round_trip():
    res = WorkResult(
        status="ok",
        artifact_handles=[ArtifactHandle("ccc")],
        evidence_proposals=[{"claim_id": "c1"}],
        usage={"tokens": 10},
        failure=None,
    )
    assert WorkResult.from_dict(res.to_dict()).to_dict() == res.to_dict()


def test_request_carries_handles_not_abs_paths():
    r = _req()
    d = r.to_dict()
    for h in d["input_handles"] + d["output_handles"]:
        assert h.startswith("artifact:")
        assert not h.startswith("/")


def test_worker_port_is_protocol():
    class _W:
        def execute(self, request):  # pragma: no cover - shape
            ...

    assert isinstance(_W(), WorkerPort)
