"""Task 0.3 — ProofObligationNode + Budget (3 dims).

The one recursive unit of work. Its absence of a ``kind``/``is_leaf`` field is
LOAD-BEARING (Architect one-primitive check): the router — and only the router
— maps ``validation_strength`` to a verb. Round-trips deterministically.
"""

from __future__ import annotations

import json

import pytest

from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
from personal_os.engine.contract.node import Budget, ProofObligationNode


def _node(**over):
    kw = dict(
        id="n1",
        parent_id=None,
        objective="make the CLI runnable",
        done_contract={"kind": "cli_reproducible"},
        admissible_evidence=["clean_run_log"],
        validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=3, max_children=5, max_attempts=2),
        status=NodeStatus.PENDING,
        provenance={"attempts": []},
    )
    kw.update(over)
    return ProofObligationNode(**kw)


def test_budget_has_three_dims_only():
    b = Budget(max_depth=3, max_children=5, max_attempts=2)
    assert b.max_depth == 3 and b.max_children == 5 and b.max_attempts == 2
    d = b.to_dict()
    assert set(d) == {"max_depth", "max_children", "max_attempts"}


def test_node_has_no_kind_or_is_leaf_field():
    n = _node()
    d = n.to_dict()
    assert "kind" not in d
    assert "is_leaf" not in d


def test_node_round_trip():
    n = _node()
    d = n.to_dict()
    n2 = ProofObligationNode.from_dict(d)
    assert n2.to_dict() == d
    assert n2.validation_strength is ValidationStrength.HARD
    assert n2.status is NodeStatus.PENDING
    assert n2.budget.max_attempts == 2


def test_node_serializes_with_deterministic_key_order():
    n = _node()
    s1 = json.dumps(n.to_dict(), sort_keys=True)
    s2 = json.dumps(ProofObligationNode.from_dict(n.to_dict()).to_dict(), sort_keys=True)
    assert s1 == s2


def test_node_rejects_unknown_strength():
    with pytest.raises(ValueError):
        ProofObligationNode.from_dict({**_node().to_dict(), "validation_strength": "bogus"})


def test_node_rejects_unknown_status():
    with pytest.raises(ValueError):
        ProofObligationNode.from_dict({**_node().to_dict(), "status": "bogus"})


def test_node_accepts_optional_validator_ref():
    n = _node(validator_ref="hard_cli")
    assert ProofObligationNode.from_dict(n.to_dict()).validator_ref == "hard_cli"
