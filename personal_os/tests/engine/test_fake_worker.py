"""Task 1.5 — FakeWorker: deterministic, no-LLM worker for the HARD leaf.

For an EXECUTE request, ``FakeWorker`` writes a KNOWN-good patch payload to the
request's ``output_handles[0]`` (resolved via the RunDir) and returns a
well-formed ``WorkResult`` — no receipt, no pass bit (invariant 1). The patch
is the one-line import fix that makes brokencli reproducibly runnable.
"""

from __future__ import annotations

import json
import os

from personal_os.engine.adapters.fake_worker import FakeWorker
from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.ports.worker import WorkKind, WorkRequest


def _request(rd):
    # Pre-mint an output handle by storing a placeholder; the worker overwrites
    # its content-addressed target via the RunDir put path in a real flow. Here
    # we pass an output "slot" the worker fills.
    return WorkRequest(
        kind=WorkKind.EXECUTE,
        run_id=rd.run_id,
        node_id="n1",
        attempt=1,
        objective="make brokencli reproducibly runnable",
        contract={"target": "brokencli/cli.py"},
        input_handles=[],
        output_handles=[],
        constraints={},
    )


def test_fake_worker_returns_wellformed_result(tmp_path):
    rd = new_run(str(tmp_path))
    w = FakeWorker(rd)
    result = w.execute(_request(rd))
    assert result.status == "ok"
    assert result.failure is None
    assert len(result.artifact_handles) == 1
    # No receipt / pass bit anywhere.
    d = result.to_dict()
    assert "receipt" not in d and "passed" not in d


def test_fake_worker_patch_is_the_known_good_fix(tmp_path):
    rd = new_run(str(tmp_path))
    w = FakeWorker(rd)
    result = w.execute(_request(rd))
    handle = result.artifact_handles[0]
    resolved = rd.resolve_handle(handle)
    with open(resolved) as f:
        payload = json.loads(f.read())
    assert payload["target"] == "brokencli/cli.py"
    assert "from brokencli.vendor.tinyfmt import leftpad" in payload["content"]
    # The broken import must be gone from the proposed content.
    assert "from tinyfmt import leftpad" not in payload["content"]


def test_fake_worker_is_deterministic(tmp_path):
    rd1 = new_run(str(tmp_path / "a"))
    rd2 = new_run(str(tmp_path / "b"))
    h1 = FakeWorker(rd1).execute(_request(rd1)).artifact_handles[0]
    h2 = FakeWorker(rd2).execute(_request(rd2)).artifact_handles[0]
    # Same patch bytes -> same content-address.
    assert h1.id == h2.id
