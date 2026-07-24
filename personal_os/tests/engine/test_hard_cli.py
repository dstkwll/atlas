"""Task 1.4 — HARD CLI validator: clean-env install + run + test, Core receipt.

Real (non-mocked) offline validation against a staged tree. Slower than the
contract tests (builds venvs) but it is the load-bearing HARD gate, so it must
exercise the true toolchain. Covers: unfixed staged tree -> passed False;
hand-fixed staged tree -> passed True with content-addressed artifacts whose
hashes match; a simulated timeout -> ran True / passed False (never a silent
None).
"""

from __future__ import annotations

import os

from personal_os.engine.contract.enums import ValidationStrength
from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.core.staging import stage
from personal_os.engine.validators.hard_cli import HardCliValidator
from personal_os.tests.engine.fixtures.broken_cli_fixture import fixture_root


def _fix_staged(staged):
    cli = os.path.join(staged, "brokencli", "cli.py")
    with open(cli) as f:
        content = f.read()
    content = content.replace(
        "from tinyfmt import leftpad  # noqa: F401  (BUG: wrong module path)",
        "from brokencli.vendor.tinyfmt import leftpad",
    )
    with open(cli, "w") as f:
        f.write(content)


def test_validator_identity():
    v = HardCliValidator()
    assert v.id == "hard_cli"
    assert v.version == "0.1.0"
    assert v.strength is ValidationStrength.HARD


def test_unfixed_fixture_fails(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    v = HardCliValidator()
    receipt = v.validate(rd, node=None, config={})
    assert receipt.ran is True
    assert receipt.passed is False
    assert receipt.strength is ValidationStrength.HARD
    # Core-minted identity present.
    assert receipt.validator_id == "hard_cli"
    assert receipt.workspace_id


def test_fixed_fixture_passes_with_matching_artifacts(tmp_path):
    rd = new_run(str(tmp_path))
    staged = stage(fixture_root(), rd)
    _fix_staged(staged)
    v = HardCliValidator()
    receipt = v.validate(rd, node=None, config={})
    assert receipt.ran is True
    assert receipt.passed is True
    # Artifacts were content-addressed and their hashes are recorded + resolve.
    assert receipt.artifact_hashes
    for handle_str, sha in receipt.artifact_hashes.items():
        assert handle_str.startswith("artifact:")
        # the recorded hash equals the handle's content-address id
        assert handle_str == f"artifact:{sha}"
        path = os.path.join(rd.artifacts_dir, sha)
        assert os.path.exists(path)
    assert 0 in receipt.exit_codes


def test_simulated_timeout_is_ran_true_passed_false(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    v = HardCliValidator()
    # A 0-second timeout forces every subprocess to time out.
    receipt = v.validate(rd, node=None, config={"timeout_s": 0})
    assert receipt.ran is True
    assert receipt.passed is False
    # Timeout is captured, not a silent None.
    assert receipt is not None


def test_validator_internal_error_fails_closed_to_receipt(tmp_path):
    # P2 hardening: a generic internal error (not just timeout/missing-exec)
    # must still mint a ran=True, passed=False receipt — never propagate a raw
    # exception (the docstring/plan promise "never a silent None").
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    v = HardCliValidator()

    # Force an internal failure deep in the run: monkeypatch put_artifact to
    # raise, simulating an OSError while capturing output.
    import personal_os.engine.validators.hard_cli as mod

    orig = mod.subprocess.run

    def boom(*a, **k):
        raise OSError("simulated internal failure")

    mod.subprocess.run = boom
    try:
        receipt = v.validate(rd, node=None, config={})
    finally:
        mod.subprocess.run = orig
    assert receipt is not None
    assert receipt.ran is True
    assert receipt.passed is False
    assert receipt.validator_id == "hard_cli"


def test_bad_timeout_config_fails_closed_not_raises(tmp_path):
    # F6/sol-5: a non-integer timeout_s (parsed BEFORE the old try block) must
    # still produce a ran=True, passed=False receipt, not propagate ValueError.
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    v = HardCliValidator()
    receipt = v.validate(rd, node=None, config={"timeout_s": "not-an-int"})
    assert receipt is not None
    assert receipt.ran is True
    assert receipt.passed is False
    assert receipt.validator_id == "hard_cli"
