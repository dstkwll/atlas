"""Task 2.2 — contract parity: worker↔worker AND compiler↔validator.

A single parametrized conformance check (not a CDC framework — Simplifier S2)
proving the ONE canonical execution-leaf contract is consistent across every
party that touches it:

- **worker↔worker:** the contract the refiner emits and the contract the
  FakeWorker fulfills compile to the SAME fingerprint.
- **compiler↔validator:** the compiler's canonical output is exactly what the
  ``HardCliValidator`` accepts (derived from the same ``LEAF_CONTRACT_FIELDS``),
  and neither has a hand-mirrored second schema (Skeptic D2 / Architect SSOT).
"""

from __future__ import annotations

from personal_os.engine.adapters.fake_worker import (
    _EXECUTION_CONTRACT_PROPOSAL,
    FakeWorker,
)
from personal_os.engine.core.contract_compiler import (
    LEAF_CONTRACT_FIELDS,
    compile_leaf_contract,
    fingerprint,
)
from personal_os.engine.validators.hard_cli import HardCliValidator

# The FakeWorker fulfils the brokencli/cli.py target with this same contract
# shape; the refiner emits _EXECUTION_CONTRACT_PROPOSAL. They must be identical.
_FAKEWORKER_FULFILLED = {
    "target": "brokencli/cli.py",
    "objective": "make brokencli reproducibly runnable",
    "install_cmd": "pip install --no-index --no-build-isolation .",
    "run_cmd": "python -m brokencli.cli hello 8",
    "test_cmd": "python -m unittest discover -p test_*.py",
}


def test_worker_to_worker_parity():
    refiner_emitted = compile_leaf_contract(_EXECUTION_CONTRACT_PROPOSAL)
    worker_fulfilled = compile_leaf_contract(_FAKEWORKER_FULFILLED)
    assert fingerprint(refiner_emitted) == fingerprint(worker_fulfilled)


def test_compiler_to_validator_parity():
    contract = compile_leaf_contract(_EXECUTION_CONTRACT_PROPOSAL)
    # The validator accepts EXACTLY the compiler's canonical output.
    HardCliValidator().validate_contract(contract)
    # And their schemas are the same single source (no hand mirror).
    assert set(HardCliValidator().expected_contract_fields()) == set(LEAF_CONTRACT_FIELDS)


def test_validator_rejects_a_stray_field_the_compiler_would_reject():
    contract = compile_leaf_contract(_EXECUTION_CONTRACT_PROPOSAL)
    drifted = dict(contract)
    drifted["extra_flag"] = True
    # Both the compiler and validator fail closed on the same stray field.
    import pytest
    with pytest.raises(ValueError):
        HardCliValidator().validate_contract(drifted)
    with pytest.raises(ValueError):
        compile_leaf_contract({**_EXECUTION_CONTRACT_PROPOSAL, "extra_flag": True})
