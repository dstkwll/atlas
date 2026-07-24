"""E2E crash runner — a REAL child process that blocks mid-discharge.

Run as ``python -m personal_os.tests.engine._e2e_crash_runner ROOT FIXTURE
READY_PATH BLOCK_PATH``. It builds the real Scheduler with the real
``HermesWorker`` adapter, but injects a ``_run_hermes`` that:

  1. writes the genuine correct brokencli patch to the adapter's absolute
     output path (so the adapter's verify-at-handle path runs for real), then
  2. touches ``READY_PATH`` (signalling the parent the worker is INSIDE
     ``discharge`` — the journal already carries ``DISCHARGING``), then
  3. blocks until ``BLOCK_PATH`` appears (which never happens: the parent
     ``kill -9``s this process instead).

The parent then resumes the run and asserts the interrupted node fails closed
to ``BLOCKED`` — a real OS crash mid-discharge, not a hand-forged journal.
"""

from __future__ import annotations

import os
import sys
import time


def _patch_content(fixture: str) -> str:
    src = os.path.join(fixture, "brokencli", "cli.py")
    with open(src) as f:
        content = f.read()
    return content.replace(
        "from tinyfmt import leftpad  # noqa: F401  (BUG: wrong module path)",
        "from brokencli.vendor.tinyfmt import leftpad",
    )


def main(argv):
    root, fixture, ready_path, block_path = argv

    from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
    from personal_os.engine.contract.journal import Journal
    from personal_os.engine.contract.node import Budget, ProofObligationNode
    from personal_os.engine.contract.run_dir import new_run
    from personal_os.engine.adapters.fake_worker import FakeRefiner
    from personal_os.engine.adapters.hermes_worker import HermesWorker
    from personal_os.engine.core.scheduler import Scheduler
    from personal_os.engine.core.staging import stage
    from personal_os.engine.validators.hard_cli import HardCliValidator

    run_dir = new_run(root)
    # Announce the run_id immediately (flushed) so the parent can find it even
    # if we are killed a moment later.
    sys.stdout.write(run_dir.run_id + "\n")
    sys.stdout.flush()

    stage(fixture, run_dir)

    def blocking_run(cmd, prompt, out_abs_path, timeout_s):
        # Write the REAL correct patch to the adapter's chosen absolute path.
        with open(out_abs_path, "w") as f:
            import json
            f.write(json.dumps(
                {"target": "brokencli/cli.py", "content": _patch_content(fixture)}))
        # Signal we are inside discharge (DISCHARGING already journaled), then
        # block forever — the parent SIGKILLs us here.
        with open(ready_path, "w") as f:
            f.write("ready")
        while not os.path.exists(block_path):
            time.sleep(0.05)
        return 0, "WORKER_DONE"

    top = ProofObligationNode(
        id="top", parent_id=None, objective="make brokencli reproducibly runnable",
        done_contract={}, admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=2, max_children=4, max_attempts=2),
        status=NodeStatus.PENDING, provenance={"depth": 0, "attempts": 0},
    )
    scheduler = Scheduler(
        run_dir=run_dir,
        journal=Journal(run_dir.events_path, run_id=run_dir.run_id),
        refiner=FakeRefiner(run_dir),
        worker=HermesWorker(run_dir, _run_hermes=blocking_run),
        hard_validator=HardCliValidator(),
    )
    scheduler.run(top)  # never returns cleanly: we are killed mid-discharge


if __name__ == "__main__":
    main(sys.argv[1:])
