"""E2E — the real HermesWorker adapter driven through the WHOLE pipeline.

The existing tests prove the pieces in isolation: ``test_hermes_worker`` mocks
the subprocess and checks the adapter's path-injection + verify-at-handle;
``test_resume`` drives the full scheduler but only with the ``FakeWorker``; the
nightly ``@integration`` test spawns real hermes but only asserts the shared
oracle on one ``execute()``. NONE drives the REAL ``HermesWorker`` adapter
through refine -> discharge -> synthesize -> accept, and none kills a REAL
process mid-discharge. This module closes both gaps.

The subprocess boundary (``_run_hermes``) is injected with a runner that writes
the genuine correct patch to the adapter's own absolute output path — so 100%
of the adapter's REAL code path runs (path allocation, absolute-path injection,
artifact-absent check, read-bytes, content-address, mint handle, cross the
port), deterministically and without an LLM. This is the fake->real seam
exercised end-to-end, not just at the oracle.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

import pytest

from personal_os.engine.adapters.fake_worker import FakeRefiner
from personal_os.engine.adapters.hermes_worker import HermesWorker
from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
from personal_os.engine.contract.journal import Journal, replay
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.run_dir import RunDir, new_run
from personal_os.engine.core.acceptance import accept
from personal_os.engine.core.scheduler import Scheduler, _find_top, resume
from personal_os.engine.core.staging import stage
from personal_os.engine.core.synthesize import synthesize
from personal_os.engine.validators.hard_cli import HardCliValidator
from personal_os.tests.engine.fixtures.broken_cli_fixture import fixture_root


_BAD_IMPORT = "from tinyfmt import leftpad  # noqa: F401  (BUG: wrong module path)"
_GOOD_IMPORT = "from brokencli.vendor.tinyfmt import leftpad"


def _real_patch(fixture: str) -> str:
    with open(os.path.join(fixture, "brokencli", "cli.py")) as f:
        return f.read().replace(_BAD_IMPORT, _GOOD_IMPORT)


def _top() -> ProofObligationNode:
    return ProofObligationNode(
        id="top", parent_id=None, objective="make brokencli reproducibly runnable",
        done_contract={}, admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=2, max_children=4, max_attempts=2),
        status=NodeStatus.PENDING, provenance={"depth": 0, "attempts": 0},
    )


def test_real_worker_adapter_full_pipeline_to_done(tmp_path):
    """Real HermesWorker -> refine -> discharge -> synthesize -> accept -> DONE."""
    fixture = fixture_root()
    rd = new_run(str(tmp_path))
    stage(fixture, rd)

    captured = {}

    def run_hermes(cmd, prompt, out_abs_path, timeout_s):
        # The adapter chose an absolute output path and injected it into the
        # prompt (its real cwd-trap fix). Prove it, then write the REAL patch
        # there so the adapter's verify-at-handle + content-address path runs.
        captured["out_abs_path"] = out_abs_path
        captured["prompt"] = prompt
        assert os.path.isabs(out_abs_path)
        assert out_abs_path in prompt
        with open(out_abs_path, "w") as f:
            f.write(json.dumps({"target": "brokencli/cli.py",
                                "content": _real_patch(fixture)}))
        return 0, "WORKER_DONE"

    scheduler = Scheduler(
        run_dir=rd,
        journal=Journal(rd.events_path, run_id=rd.run_id),
        refiner=FakeRefiner(rd),
        worker=HermesWorker(rd, _run_hermes=run_hermes),
        hard_validator=HardCliValidator(),
    )
    outcome = scheduler.run(_top())

    # The real adapter actually ran (its absolute path was injected + used).
    assert captured.get("out_abs_path")
    # The execution child HARD-discharged on a Core-minted receipt.
    exec_ids = [n for n in outcome.node_statuses if n.endswith("-exec")]
    assert exec_ids
    assert outcome.node_statuses[exec_ids[0]] is NodeStatus.HARD_DISCHARGED
    # The top ended AWAITING_ACCEPTANCE (never auto-DONE).
    assert outcome.top_status is NodeStatus.AWAITING_ACCEPTANCE

    # Synthesis renders a deterministic report from the real run.
    report = synthesize(rd, rd.events_path)
    assert "brokencli" in report or "AWAITING_ACCEPTANCE" in report.upper() \
        or exec_ids[0] in report

    # The single DONE writer accepts it, journal-authoritatively.
    top_id = _find_top(replay(rd.events_path))
    new_status = accept(rd, top_id)
    assert new_status is NodeStatus.DONE
    assert replay(rd.events_path).node_status[top_id] == NodeStatus.DONE.value


def test_real_process_killed_mid_discharge_resumes_blocked(tmp_path):
    """A REAL SIGKILL mid-discharge -> resume fails the node closed to BLOCKED.

    Unlike the hand-forged-journal crash tests, this spawns an actual child
    process that reaches DISCHARGING and blocks; the parent SIGKILLs it, then
    resumes the run from the on-disk journal alone.
    """
    fixture = fixture_root()
    root = str(tmp_path / "root")
    os.makedirs(root, exist_ok=True)
    ready = str(tmp_path / "ready")
    block = str(tmp_path / "unblock-never")

    env = dict(os.environ)
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    env["PYTHONPATH"] = repo_root + os.pathsep + env.get("PYTHONPATH", "")

    proc = subprocess.Popen(
        [sys.executable, "-m", "personal_os.tests.engine._e2e_crash_runner",
         root, fixture, ready, block],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
        cwd=repo_root,
    )
    run_id = proc.stdout.readline().strip()
    assert run_id, "crash runner did not announce a run_id"

    # Wait until the child is INSIDE discharge (DISCHARGING already journaled).
    deadline = time.time() + 30
    while not os.path.exists(ready):
        assert time.time() < deadline, "worker never reached discharge"
        assert proc.poll() is None, "crash runner exited before discharge"
        time.sleep(0.05)

    # Hard kill mid-discharge — the ungraceful crash we must survive.
    proc.send_signal(signal.SIGKILL)
    proc.wait(timeout=10)

    rd = RunDir(os.path.join(root, "runs", run_id), run_id)
    # Sanity: the journal captured DISCHARGING but no terminal receipt/status.
    proj = replay(rd.events_path)
    exec_ids = [n for n in proj.node_status if n.endswith("-exec")]
    assert exec_ids, "no execution node was journaled before the kill"
    exec_id = exec_ids[0]
    assert proj.node_status[exec_id] == NodeStatus.DISCHARGING.value

    # Resume from disk alone: the interrupted node fails closed to BLOCKED and
    # NEVER re-enters DISCHARGING or fabricates a stale success.
    outcome = resume(rd, HardCliValidator())
    assert outcome.node_statuses[exec_id] is NodeStatus.BLOCKED
    assert replay(rd.events_path).node_status[exec_id] == NodeStatus.BLOCKED.value
    assert outcome.top_status is not NodeStatus.DONE
