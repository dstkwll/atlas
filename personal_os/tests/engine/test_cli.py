"""Task 4.3 — CLI entrypoint E2E (fake worker).

``python -m personal_os.engine.cli run --goal-file G --root DIR`` creates a
RunDir, runs the scheduler on the broken-CLI fixture, writes journal + receipts
+ report, and prints the report path + top status (AWAITING_ACCEPTANCE).
``--accept RUN_ID`` transitions AWAITING_ACCEPTANCE -> DONE.
"""

from __future__ import annotations

import json
import os

from personal_os.engine.cli import main
from personal_os.tests.engine.fixtures.broken_cli_fixture import fixture_root


def _goal_file(tmp_path):
    p = tmp_path / "goal.md"
    p.write_text("make brokencli reproducibly runnable\n")
    return str(p)


def test_cli_run_then_accept(tmp_path, capsys):
    root = str(tmp_path / "engine-root")
    goal = _goal_file(tmp_path)

    rc = main(["run", "--goal-file", goal, "--root", root,
               "--worker", "fake", "--fixture", fixture_root()])
    assert rc == 0
    out = capsys.readouterr().out
    assert "AWAITING_ACCEPTANCE" in out
    # Report path printed and exists.
    assert "report.md" in out
    # Extract run_id from output.
    run_id = None
    for line in out.splitlines():
        if line.startswith("run_id:"):
            run_id = line.split(":", 1)[1].strip()
    assert run_id
    report_path = os.path.join(root, "runs", run_id, "report.md")
    assert os.path.exists(report_path)

    # Accept the run -> DONE.
    rc2 = main(["accept", "--root", root, "--run-id", run_id])
    assert rc2 == 0
    out2 = capsys.readouterr().out
    assert "DONE" in out2


def test_cli_run_writes_journal_and_report(tmp_path, capsys):
    root = str(tmp_path / "r")
    goal = _goal_file(tmp_path)
    main(["run", "--goal-file", goal, "--root", root, "--worker", "fake",
          "--fixture", fixture_root()])
    out = capsys.readouterr().out
    run_id = [l.split(":", 1)[1].strip() for l in out.splitlines()
              if l.startswith("run_id:")][0]
    run_dir = os.path.join(root, "runs", run_id)
    assert os.path.exists(os.path.join(run_dir, "events.jsonl"))
    assert os.path.exists(os.path.join(run_dir, "report.md"))


def test_cli_accept_bad_state_fails(tmp_path, capsys):
    # Accepting a nonexistent/never-run run_id fails cleanly (nonzero rc).
    root = str(tmp_path / "r2")
    os.makedirs(root, exist_ok=True)
    rc = main(["accept", "--root", root, "--run-id", "does-not-exist"])
    assert rc != 0
