"""Task 3.1 / 3.1b — the router: sole author of strength→verb dispatch.

``route(node, projection) -> (RouterAction, RationaleCode)`` is the ONLY code
mapping a node's state to a verb. DISCHARGE if a HARD validator is available;
REFINE if not and budget/depth allow; ESCALATE if human interpretation needed /
no HARD oracle at an acceptance point; FAIL if budget exhausted or no progress.
3.1b: a node whose only children are ADMISSIBILITY_PASSED does not route to a
HARD discharge / DONE.
"""

from __future__ import annotations

from personal_os.engine.contract.enums import (
    NodeStatus,
    RationaleCode,
    RouterAction,
    ValidationStrength,
)
from personal_os.engine.contract.journal import LifecycleProjection
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.core.router import route


def _node(**over):
    kw = dict(
        id="n", parent_id=None, objective="obj", done_contract={},
        admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=3, max_children=4, max_attempts=2),
        status=NodeStatus.PENDING, provenance={"depth": 0, "attempts": 0},
    )
    kw.update(over)
    return ProofObligationNode(**kw)


def _proj():
    return LifecycleProjection()


def test_discharge_when_hard_validator_available():
    n = _node(validator_ref="hard_cli", validation_strength=ValidationStrength.HARD)
    action, code = route(n, _proj())
    assert action is RouterAction.DISCHARGE
    assert code is RationaleCode.HARD_VALIDATOR_AVAILABLE


def test_terminal_and_transitional_states_are_noop():
    # F13/sol-8: a HARD node in a terminal or transitional state must NOT be
    # routed back to DISCHARGE — only schedulable (PENDING) states discharge.
    for terminal in (NodeStatus.HARD_DISCHARGED, NodeStatus.BLOCKED,
                     NodeStatus.FAILED, NodeStatus.DONE, NodeStatus.DISCHARGING,
                     NodeStatus.ESCALATED, NodeStatus.REFINING):
        n = _node(validator_ref="hard_cli", status=terminal)
        action, _ = route(n, _proj())
        assert action is RouterAction.NOOP, f"{terminal} should be NOOP, got {action}"


def test_terminal_top_not_escalated_again():
    # A DONE/FAILED top must be NOOP, not ESCALATE-for-being-non-PENDING.
    for terminal in (NodeStatus.DONE, NodeStatus.FAILED):
        n = _node(parent_id=None, validator_ref=None, status=terminal)
        action, _ = route(n, _proj())
        assert action is RouterAction.NOOP, f"{terminal} top should be NOOP, got {action}"


def test_refine_when_no_validator_yet_and_budget_allows():
    n = _node(validator_ref=None, provenance={"depth": 0, "attempts": 0})
    action, code = route(n, _proj())
    assert action is RouterAction.REFINE
    assert code is RationaleCode.NO_VALIDATOR_YET


def test_fail_when_budget_exhausted_by_depth():
    n = _node(validator_ref=None,
              budget=Budget(max_depth=1, max_children=4, max_attempts=2),
              provenance={"depth": 1, "attempts": 0})
    action, code = route(n, _proj())
    assert action is RouterAction.FAIL
    assert code is RationaleCode.BUDGET_EXHAUSTED


def test_fail_when_attempts_exhausted():
    n = _node(validator_ref=None,
              budget=Budget(max_depth=3, max_children=4, max_attempts=2),
              provenance={"depth": 0, "attempts": 2})
    action, code = route(n, _proj())
    assert action is RouterAction.FAIL
    assert code is RationaleCode.NO_REFINEMENT_PROGRESS


def test_escalate_at_acceptance_point_without_hard_oracle():
    # A top node (no parent) that can't be discharged and whose objective needs
    # human interpretation escalates rather than looping.
    n = _node(parent_id=None, validator_ref=None,
              status=NodeStatus.AWAITING_ACCEPTANCE)
    action, code = route(n, _proj())
    assert action is RouterAction.ESCALATE
    assert code is RationaleCode.NEEDS_HUMAN_INTERPRETATION


def test_admissibility_passed_children_do_not_route_parent_to_discharge():
    # 3.1b / invariant 5: a parent whose children are only ADMISSIBILITY_PASSED
    # is NOT eligible for a HARD discharge — it must not route to DISCHARGE
    # merely because children passed.
    proj = LifecycleProjection()
    proj.node_status["c1"] = NodeStatus.ADMISSIBILITY_PASSED.value
    parent = _node(id="p", validator_ref=None, validation_strength=ValidationStrength.HARD)
    action, code = route(parent, proj)
    assert action is not RouterAction.DISCHARGE
