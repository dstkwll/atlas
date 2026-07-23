"""Task 0.5 — Validator Protocol + Core-minted Receipt.

A ``Receipt`` records validator identity/version/config, workspace identity,
commands, exit codes, artifact hashes, evidence, residual, ts. It is
constructed ONLY by validator/Core code — never from worker output (invariant
1). ``can_discharge_hard`` is True iff ``strength == HARD and passed`` — an
ADMISSIBILITY receipt can never discharge a HARD obligation (invariant 3/5).
"""

from __future__ import annotations

import pytest

from personal_os.engine.contract.enums import ValidationStrength
from personal_os.engine.contract.receipt import Receipt, can_discharge_hard
from personal_os.engine.contract.validator import Validator


def _receipt(strength=ValidationStrength.HARD, passed=True, ran=True):
    return Receipt(
        node_id="n1",
        validator_id="hard_cli",
        validator_version="0.1.0",
        strength=strength,
        ran=ran,
        passed=passed,
        workspace_id="ws-abc",
        commands=["pip install .", "pytest"],
        exit_codes=[0, 0],
        artifact_hashes={"artifact:stdout": "deadbeef"},
        evidence=[],
        residual=[],
        ts="2026-07-23T00:00:00Z",
    )


def test_receipt_requires_validator_identity():
    r = _receipt()
    assert r.validator_id == "hard_cli"
    assert r.validator_version == "0.1.0"
    # These are non-optional constructor args (identity is mandatory).
    with pytest.raises(TypeError):
        Receipt(node_id="n1")  # type: ignore[call-arg]


def test_receipt_round_trip():
    r = _receipt()
    assert Receipt.from_dict(r.to_dict()).to_dict() == r.to_dict()


def test_can_discharge_hard_true_only_for_passed_hard():
    assert can_discharge_hard(_receipt(ValidationStrength.HARD, passed=True)) is True


def test_can_discharge_hard_false_for_failed_hard():
    assert can_discharge_hard(_receipt(ValidationStrength.HARD, passed=False)) is False


def test_admissibility_cannot_discharge_hard_even_when_passed():
    # The load-bearing invariant: a passed ADMISSIBILITY receipt still can't
    # discharge a HARD obligation.
    r = _receipt(ValidationStrength.ADMISSIBILITY, passed=True)
    assert can_discharge_hard(r) is False


def test_validator_protocol_shape():
    # A conforming validator has id/version/strength + validate(...).
    class _V:
        id = "x"
        version = "0.0.1"
        strength = ValidationStrength.HARD

        def validate(self, workspace, node, config):  # pragma: no cover - shape
            ...

    assert isinstance(_V(), Validator)
