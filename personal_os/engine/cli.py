"""Task 4.3 — the engine CLI entrypoint.

``python -m personal_os.engine.cli run --goal-file GOAL.md --root DIR
[--worker fake|hermes] [--fixture DIR]``
  Creates a RunDir under ``DIR/runs/<run_id>/``, stages the target project,
  runs the scheduler, writes the journal + receipts + a deterministic
  ``report.md``, and prints the run_id, top status, and report path.

``python -m personal_os.engine.cli accept --root DIR --run-id RUN_ID``
  Rebuilds the run's projection and, if the top is AWAITING_ACCEPTANCE,
  transitions it to DONE via the single ``mark_done`` writer.

v0 defaults to the bundled broken-CLI fixture as the target project (via
``--fixture``); ``--worker fake`` uses the deterministic worker (no LLM),
``--worker hermes`` docks the real detached-hermes adapter.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from personal_os.engine.contract.enums import NodeStatus
from personal_os.engine.contract.journal import Journal, replay
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.enums import ValidationStrength
from personal_os.engine.contract.run_dir import RunDir, new_run
from personal_os.engine.core.acceptance import accept
from personal_os.engine.core.scheduler import Scheduler, _find_top
from personal_os.engine.core.staging import stage
from personal_os.engine.core.synthesize import synthesize
from personal_os.engine.validators.hard_cli import HardCliValidator


def _default_fixture() -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "tests", "engine", "fixtures", "brokencli",
    )


def _build_worker(kind: str, run_dir: RunDir):
    if kind == "hermes":
        from personal_os.engine.adapters.hermes_worker import HermesWorker
        return HermesWorker(run_dir)
    from personal_os.engine.adapters.fake_worker import FakeWorker
    return FakeWorker(run_dir)


def _build_refiner(kind: str, run_dir: RunDir):
    # v0: the refiner is the deterministic FakeRefiner for both worker kinds
    # (a real LLM refiner adapter is post-v0). The worker kind governs execution.
    from personal_os.engine.adapters.fake_worker import FakeRefiner
    return FakeRefiner(run_dir)


def _cmd_run(args) -> int:
    goal_text = "make brokencli reproducibly runnable"
    if args.goal_file and os.path.exists(args.goal_file):
        with open(args.goal_file) as f:
            goal_text = f.read().strip() or goal_text

    fixture = args.fixture or _default_fixture()
    run_dir = new_run(args.root)
    stage(fixture, run_dir)

    top = ProofObligationNode(
        id="top", parent_id=None, objective=goal_text, done_contract={},
        admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=2, max_children=4, max_attempts=2),
        status=NodeStatus.PENDING, provenance={"depth": 0, "attempts": 0},
    )

    scheduler = Scheduler(
        run_dir=run_dir,
        journal=Journal(run_dir.events_path, run_id=run_dir.run_id),
        refiner=_build_refiner(args.worker, run_dir),
        worker=_build_worker(args.worker, run_dir),
        hard_validator=HardCliValidator(),
    )
    outcome = scheduler.run(top)

    report = synthesize(run_dir, run_dir.events_path)
    report_path = os.path.join(run_dir.path, "report.md")
    with open(report_path, "w") as f:
        f.write(report)

    print(f"run_id: {run_dir.run_id}")
    print(f"top_status: {outcome.top_status.name}")
    print(f"report: {report_path}")
    return 0


def _cmd_accept(args) -> int:
    run_dir = RunDir(os.path.join(args.root, "runs", args.run_id), args.run_id)
    if not os.path.exists(run_dir.events_path):
        print(f"error: no run journal at {run_dir.events_path}", file=sys.stderr)
        return 2

    proj = replay(run_dir.events_path)
    top_id = _find_top(proj)
    if proj.node_status.get(top_id) is None:
        print(f"error: top node not found in run {args.run_id}", file=sys.stderr)
        return 2

    # F14: journal-authoritative acceptance — accept() re-reads the journal and
    # gates through the single mark_done writer; no stale in-memory status.
    try:
        new_status = accept(run_dir, top_id)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    print(f"top_status: {new_status.name}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="personal_os.engine.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run the engine on a goal")
    p_run.add_argument("--goal-file", required=True)
    p_run.add_argument("--root", required=True)
    p_run.add_argument("--worker", choices=["fake", "hermes"], default="fake")
    p_run.add_argument("--fixture", default=None,
                       help="target project tree (defaults to the bundled brokencli)")
    p_run.set_defaults(func=_cmd_run)

    p_acc = sub.add_parser("accept", help="accept an AWAITING_ACCEPTANCE run -> DONE")
    p_acc.add_argument("--root", required=True)
    p_acc.add_argument("--run-id", required=True)
    p_acc.set_defaults(func=_cmd_accept)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
