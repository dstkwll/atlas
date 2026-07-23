"""Task 0.2 — enums: membership + FailureClass total worst->least order.

No SEMANTIC strength in v0 (Simplifier S3). Every NodeStatus is reached by a
Phase-3 task (prove-or-cut). FailureClass must expose a total, stable ordering
so deterministic failure selection (Task 2.4) is reproducible.
"""

from __future__ import annotations

import pytest

from personal_os.engine.contract.enums import (
    FailureClass,
    NodeStatus,
    RationaleCode,
    RouterAction,
    ValidationStrength,
)


def test_validation_strength_members():
    assert {s.name for s in ValidationStrength} == {"HARD", "ADMISSIBILITY"}
    # No SEMANTIC in v0.
    assert not hasattr(ValidationStrength, "SEMANTIC")


def test_node_status_members():
    assert {s.name for s in NodeStatus} == {
        "PENDING", "REFINING", "DISCHARGING", "ADMISSIBILITY_PASSED",
        "HARD_DISCHARGED", "ESCALATED", "AWAITING_ACCEPTANCE", "BLOCKED",
        "FAILED", "DONE",
    }


def test_router_action_members():
    assert {a.name for a in RouterAction} == {
        "DISCHARGE", "REFINE", "ESCALATE", "FAIL",
    }


def test_failure_class_members():
    assert {f.name for f in FailureClass} == {
        "CLEAN_INSTALL_BLOCKER", "DOCUMENTED_COMMAND_FAILURE",
        "TEST_FAILURE", "UNKNOWN",
    }


def test_rationale_code_members():
    assert {r.name for r in RationaleCode} == {
        "NO_VALIDATOR_YET", "HARD_VALIDATOR_AVAILABLE", "BUDGET_EXHAUSTED",
        "NO_REFINEMENT_PROGRESS", "NEEDS_HUMAN_INTERPRETATION",
        "RESUME_REVERIFY_FAILED",
    }


def test_failure_class_total_order_worst_to_least():
    # Worst first. CLEAN_INSTALL_BLOCKER outranks a documented command failure,
    # which outranks a plain test failure, which outranks UNKNOWN.
    ordered = FailureClass.worst_to_least()
    assert ordered == [
        FailureClass.CLEAN_INSTALL_BLOCKER,
        FailureClass.DOCUMENTED_COMMAND_FAILURE,
        FailureClass.TEST_FAILURE,
        FailureClass.UNKNOWN,
    ]


def test_failure_class_severity_is_total_and_stable():
    sev = {f: f.severity for f in FailureClass}
    # All distinct -> a total order (no ties).
    assert len(set(sev.values())) == len(FailureClass)
    # Worst has the smallest rank so plain sort() gives worst-first.
    assert sev[FailureClass.CLEAN_INSTALL_BLOCKER] < sev[FailureClass.UNKNOWN]
    # Stable: sorting the shuffled set by severity reproduces worst_to_least.
    shuffled = list(reversed(FailureClass.worst_to_least()))
    assert sorted(shuffled, key=lambda f: f.severity) == FailureClass.worst_to_least()


def test_enum_rejects_unknown_value():
    with pytest.raises(ValueError):
        ValidationStrength("nope")
    with pytest.raises(ValueError):
        NodeStatus("bogus")
