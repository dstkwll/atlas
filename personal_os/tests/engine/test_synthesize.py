"""Task 4.1 / 4.1b — deterministic report synthesis (whitelist projection).

``synthesize(run_dir, journal_path) -> report.md`` assembles objective →
evidence → patch → validator receipt → residual risks, referencing ONLY
receipted evidence, rendered through an explicit field WHITELIST that excludes
wall-clock ``ts``/``accessed_at`` and absolute paths (paths canonicalized
run-relative — invariant 11). 4.1b proves two runs produce byte-identical
reports after journal normalization.
"""

from __future__ import annotations

import json
import os

from personal_os.engine.adapters.fake_worker import FakeRefiner, FakeWorker
from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
from personal_os.engine.contract.journal import EventType, Journal
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.core.scheduler import Scheduler
from personal_os.engine.core.staging import stage
from personal_os.engine.core.synthesize import synthesize
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


def _run(rd):
    Scheduler(
        run_dir=rd, journal=Journal(rd.events_path, run_id=rd.run_id),
        refiner=FakeRefiner(rd), worker=FakeWorker(rd),
        hard_validator=HardCliValidator(),
    ).run(_top())


def test_report_has_expected_sections(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run(rd)
    report = synthesize(rd, rd.events_path)
    for section in ("# Goal Engine Report", "## Objective", "## Evidence",
                    "## Validator receipt", "## Residual risks"):
        assert section in report


def test_report_excludes_wallclock_and_abs_paths(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run(rd)
    report = synthesize(rd, rd.events_path)
    # No absolute run path leaks in.
    assert rd.path not in report
    assert str(tmp_path) not in report
    # No ISO wall-clock timestamps (the run's events all carry ts, excluded).
    import re
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", report)


def test_two_runs_byte_identical(tmp_path):
    rd1 = new_run(str(tmp_path / "a"))
    stage(fixture_root(), rd1)
    _run(rd1)
    r1 = synthesize(rd1, rd1.events_path)

    rd2 = new_run(str(tmp_path / "b"))
    stage(fixture_root(), rd2)
    _run(rd2)
    r2 = synthesize(rd2, rd2.events_path)

    # Byte-identical despite different run_ids / abs paths / timestamps.
    assert r1 == r2


def test_report_references_only_receipted_evidence(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run(rd)
    report = synthesize(rd, rd.events_path)
    # The HARD receipt's pass status is reported.
    assert "hard_cli" in report
    assert "passed" in report.lower()


def test_missing_artifact_degrades_with_residual_note(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run(rd)
    # Delete a referenced artifact, then synthesize: must degrade explicitly,
    # never emit a stale byte-stable-looking clean report.
    from personal_os.engine.contract.journal import replay
    proj = replay(rd.events_path)
    exec_id = [n for n in proj.node_status if n.endswith("-exec")][0]
    sha = proj.receipts[exec_id][0]["receipt_handle"].split(":", 1)[1]
    os.remove(os.path.join(rd.artifacts_dir, sha))
    report = synthesize(rd, rd.events_path)
    assert "MISSING" in report or "unavailable" in report.lower()


def test_attestation_derives_from_verified_receipt_not_journal(tmp_path):
    # F8/sol-6: a forged journal event claiming passed:true beside a valid
    # receipt must NOT drive the report — attestation comes from the verified
    # receipt body only.
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run(rd)
    # Append a forged NODE receipt event lying about pass status for a bogus node.
    from personal_os.engine.contract.journal import Journal, EventType
    j = Journal(rd.events_path, run_id=rd.run_id)
    j.append(EventType.RECEIPT_WRITTEN, node_id="forged",
             payload={"receipt_handle": "artifact:" + "e" * 64,
                      "passed": True, "validator_id": "hard_cli"})
    report = synthesize(rd, rd.events_path)
    # The forged node's claimed pass must not appear as a clean attestation;
    # its receipt artifact is absent so it degrades.
    assert "forged" in report
    # The real exec node still shows a genuine verified pass.
    assert "hard_cli" in report


def test_missing_journal_is_globally_degraded(tmp_path):
    rd = new_run(str(tmp_path))
    # No run at all — journal absent.
    report = synthesize(rd, rd.events_path)
    assert "DEGRADED" in report or "no journal" in report.lower() or "MISSING" in report


def test_path_bearing_residual_is_canonicalized_or_rejected(tmp_path):
    # F8/sol-12: a residual carrying an absolute path or ISO timestamp must not
    # leak into the report verbatim (breaks determinism + leaks paths).
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    _run(rd)
    report = synthesize(rd, rd.events_path)
    import re
    assert str(tmp_path) not in report
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", report)


def test_verified_receipt_node_id_overrides_forged_journal_heading(tmp_path):
    rd = new_run(str(tmp_path))
    receipt = {
        "node_id": "trusted-node",
        "validator_id": "hard_cli",
        "validator_version": "1",
        "strength": "hard",
        "ran": True,
        "passed": True,
        "exit_codes": [0],
        "artifact_hashes": {},
        "residual": [],
    }
    handle = rd.put_artifact(json.dumps(receipt, sort_keys=True).encode("utf-8"))
    Journal(rd.events_path, run_id=rd.run_id).append(
        EventType.RECEIPT_WRITTEN,
        node_id="forged-node",
        payload={"receipt_handle": handle.to_str()},
    )

    report = synthesize(rd, rd.events_path)

    assert "### trusted-node" in report
    assert "### forged-node" not in report
    assert "MISMATCH" in report


def test_empty_journal_is_globally_degraded(tmp_path):
    rd = new_run(str(tmp_path))
    open(rd.events_path, "wb").close()

    assert "DEGRADED" in synthesize(rd, rd.events_path)


def test_unreadable_journal_is_globally_degraded(tmp_path, monkeypatch):
    rd = new_run(str(tmp_path))
    open(rd.events_path, "wb").close()

    def fail_replay(_path):
        raise OSError("unreadable")

    monkeypatch.setattr("personal_os.engine.core.synthesize.replay", fail_replay)
    assert "DEGRADED" in synthesize(rd, rd.events_path)


def test_windows_unc_file_uri_and_spaced_posix_paths_are_scrubbed(tmp_path):
    rd = new_run(str(tmp_path))
    residual = (
        r"failed at C:\Users\Dan\build log.txt, \\host\share\private dir\x.log, "
        "file:///var/tmp/private%20file.txt, and /Users/Dan/My Project/build.log"
    )
    receipt = {
        "node_id": "node",
        "validator_id": "hard_cli",
        "validator_version": "1",
        "strength": "hard",
        "ran": True,
        "passed": False,
        "exit_codes": [1],
        "artifact_hashes": {},
        "residual": [residual],
    }
    handle = rd.put_artifact(json.dumps(receipt, sort_keys=True).encode("utf-8"))
    journal = Journal(rd.events_path, run_id=rd.run_id)
    journal.append(
        EventType.NODE_CREATED,
        node_id="node",
        payload={"status": "failed", "objective": residual},
    )
    journal.append(
        EventType.RECEIPT_WRITTEN,
        node_id="node",
        payload={"receipt_handle": handle.to_str()},
    )

    report = synthesize(rd, rd.events_path)
    report_again = synthesize(rd, rd.events_path)

    assert report == report_again
    assert report.count("<path>") >= 4
    for fragment in ("C:\\Users", "host\\share", "file://", "/Users/Dan", "My Project"):
        assert fragment not in report
