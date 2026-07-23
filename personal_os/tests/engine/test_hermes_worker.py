"""Task 2.6 — real Hermes worker adapter (unit-mocked + nightly integration).

The unit test mocks the subprocess and asserts the adapter (a) injects the
ABSOLUTE artifact path into the prompt (the file-tool cwd trap) and (b) verifies
the artifact at that path on return (never trusts stdout/exit-0). The real
detached-``hermes`` call is a ``@pytest.mark.integration`` test bound to the
shared ``assert_workresult_contract`` oracle — excluded from default dev runs,
run in the non-optional nightly lane (Panel P0-D2).
"""

from __future__ import annotations

import os
from unittest import mock

import pytest

from personal_os.engine.adapters.hermes_worker import HermesWorker
from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.ports.conformance import assert_workresult_contract
from personal_os.engine.ports.worker import WorkKind, WorkRequest


def _req(rd):
    return WorkRequest(
        kind=WorkKind.EXECUTE, run_id=rd.run_id, node_id="n1", attempt=1,
        objective="write the fix", contract={"target": "brokencli/cli.py"},
    )


def test_adapter_injects_absolute_path_and_verifies_at_handle(tmp_path):
    rd = new_run(str(tmp_path))
    captured = {}

    def fake_run(cmd, prompt, out_abs_path, timeout_s):
        # Record what the adapter passed, and SIMULATE the detached hermes
        # writing the artifact to the absolute path it was told.
        captured["prompt"] = prompt
        captured["out_abs_path"] = out_abs_path
        with open(out_abs_path, "w") as f:
            f.write('{"target": "brokencli/cli.py", "content": "x = 1\\n"}')
        return 0, "WORKER_DONE"

    w = HermesWorker(rd, _run_hermes=fake_run)
    result = w.execute(_req(rd))

    # (a) An ABSOLUTE path was injected into the prompt.
    assert os.path.isabs(captured["out_abs_path"])
    assert captured["out_abs_path"] in captured["prompt"]
    # (b) The result references a handle that resolves (verified at path).
    assert result.artifact_handles
    assert_workresult_contract(result, rd)


def test_adapter_fails_when_artifact_absent_despite_exit0(tmp_path):
    rd = new_run(str(tmp_path))

    def fake_run_no_write(cmd, prompt, out_abs_path, timeout_s):
        # The 13-second "WORKER_DONE" with NO file — exit 0 but nothing written.
        return 0, "WORKER_DONE"

    w = HermesWorker(rd, _run_hermes=fake_run_no_write)
    result = w.execute(_req(rd))
    # Verify-at-handle failed -> status reflects failure, no phantom artifact.
    assert result.status == "failed"
    assert result.failure is not None


@pytest.mark.integration
def test_real_hermes_worker_passes_shared_oracle(tmp_path):
    # Nightly, non-optional, fingerprint-gated. Excluded from default dev runs.
    rd = new_run(str(tmp_path))
    result = HermesWorker(rd).execute(_req(rd))
    assert_workresult_contract(result, rd)
