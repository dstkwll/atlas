"""Task 2.1a — the HARD validator derives its schema from the canonical SSOT.

``HardCliValidator.validate_contract(contract)`` checks a leaf contract against
``LEAF_CONTRACT_FIELDS`` (the single source) and fails closed on any unknown
field — the validator has NO independent hand-mirrored schema, so it can never
drift from the compiler (Panel P1-Arch-2).
"""

from __future__ import annotations

import pytest

from personal_os.engine.core.contract_compiler import compile_leaf_contract
from personal_os.engine.validators.hard_cli import HardCliValidator


def _proposal(**over):
    p = {
        "target": "brokencli/cli.py",
        "objective": "make brokencli reproducibly runnable",
        "install_cmd": "pip install --no-index --no-build-isolation .",
        "run_cmd": "python -m brokencli.cli hello 8",
        "test_cmd": "python -m unittest discover -p test_*.py",
    }
    p.update(over)
    return p


def test_validator_accepts_canonical_contract():
    c = compile_leaf_contract(_proposal())
    # Should not raise.
    HardCliValidator().validate_contract(c)


def test_validator_rejects_unknown_field():
    c = compile_leaf_contract(_proposal())
    c["stray"] = "x"
    with pytest.raises(ValueError):
        HardCliValidator().validate_contract(c)


def test_validator_rejects_missing_field():
    c = compile_leaf_contract(_proposal())
    del c["test_cmd"]
    with pytest.raises(ValueError):
        HardCliValidator().validate_contract(c)


def test_validator_schema_is_the_canonical_one():
    from personal_os.engine.core.contract_compiler import LEAF_CONTRACT_FIELDS

    # The validator's expected fields ARE the canonical set (no hand mirror).
    assert set(HardCliValidator().expected_contract_fields()) == set(LEAF_CONTRACT_FIELDS)
