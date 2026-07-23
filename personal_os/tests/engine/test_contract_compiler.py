"""Task 2.1 / 2.1a — canonical contract compiler + fingerprint (SSOT).

``compile_leaf_contract(proposal)`` is the SINGLE author of the canonical
versioned execution-leaf contract: it normalizes a refiner proposal, raises on
missing OR extra fields (fail-closed), and stamps the schema version.
``fingerprint(contract)`` is a stable canonical hash (key-order independent).
``LEAF_CONTRACT_FIELDS`` is the one schema both the compiler and the HARD
validator derive from (Task 2.1a — no hand-mirrored second schema).
"""

from __future__ import annotations

import pytest

from personal_os.engine.contract import ENGINE_SCHEMA_VERSION
from personal_os.engine.core.contract_compiler import (
    LEAF_CONTRACT_FIELDS,
    compile_leaf_contract,
    fingerprint,
)


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


def test_valid_proposal_compiles():
    c = compile_leaf_contract(_proposal())
    assert c["schema_version"] == ENGINE_SCHEMA_VERSION
    assert c["target"] == "brokencli/cli.py"
    for f in LEAF_CONTRACT_FIELDS:
        assert f in c


def test_missing_field_rejected():
    p = _proposal()
    del p["run_cmd"]
    with pytest.raises(ValueError):
        compile_leaf_contract(p)


def test_extra_field_rejected():
    with pytest.raises(ValueError):
        compile_leaf_contract(_proposal(sneaky="x"))


def test_fingerprint_stable_across_key_order():
    a = compile_leaf_contract(_proposal())
    # Rebuild with reversed insertion order.
    b = {k: a[k] for k in reversed(list(a.keys()))}
    assert fingerprint(a) == fingerprint(b)


def test_fingerprint_changes_with_content():
    a = compile_leaf_contract(_proposal())
    b = compile_leaf_contract(_proposal(target="other/file.py"))
    assert fingerprint(a) != fingerprint(b)


def test_compile_is_idempotent():
    c1 = compile_leaf_contract(_proposal())
    # Recompiling a compiled contract (which has schema_version) still works
    # and yields the same fingerprint.
    c2 = compile_leaf_contract({k: c1[k] for k in c1 if k != "schema_version"})
    assert fingerprint(c1) == fingerprint(c2)
