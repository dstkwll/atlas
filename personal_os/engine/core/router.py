"""Task 3.1 — the router: the SOLE author of strength→verb dispatch.

``route(node, projection)`` is the ONLY code in the engine that maps a node's
``validation_strength`` + budget + lifecycle to one of the four verbs. Neither
``refine`` nor ``discharge`` self-selects (Architect rec 3): they are invoked BY
the scheduler AFTER the router decides.

Decision order (deterministic):
1. **FAIL / BUDGET_EXHAUSTED** — depth cap already reached (can't refine deeper).
2. **FAIL / NO_REFINEMENT_PROGRESS** — attempts cap reached with no discharge.
3. **DISCHARGE / HARD_VALIDATOR_AVAILABLE** — a HARD validator_ref is present.
4. **ESCALATE / NEEDS_HUMAN_INTERPRETATION** — at an acceptance point (a top
   node with no HARD oracle) or explicitly awaiting acceptance.
5. **REFINE / NO_VALIDATOR_YET** — otherwise, decompose (budget/depth allow).

Invariant 5 (3.1b): children being ADMISSIBILITY_PASSED never makes a parent
route to DISCHARGE — discharge is gated purely on the node's own HARD
validator_ref, never on child status.
"""

from __future__ import annotations

from typing import Tuple

from personal_os.engine.contract.enums import (
    NodeStatus,
    RationaleCode,
    RouterAction,
    ValidationStrength,
)
from personal_os.engine.contract.journal import LifecycleProjection
from personal_os.engine.contract.node import ProofObligationNode


def route(
    node: ProofObligationNode,
    projection: LifecycleProjection,
) -> Tuple[RouterAction, RationaleCode]:
    """Map a node's state to exactly one (action, rationale). Pure function."""
    depth = int(node.provenance.get("depth", 0))
    attempts = int(node.provenance.get("attempts", 0))
    budget = node.budget

    # F13/sol-8: terminal + transitional states are NOT schedulable. A node that
    # already reached a terminal outcome (HARD_DISCHARGED, BLOCKED, FAILED,
    # DONE, ESCALATED) or is mid-transition (DISCHARGING, REFINING — owned by
    # the in-flight op or by resume's fail-closed sweep) must never be re-routed
    # into DISCHARGE/ESCALATE. The router returns NOOP for these.
    _NON_SCHEDULABLE = (
        NodeStatus.HARD_DISCHARGED, NodeStatus.BLOCKED, NodeStatus.FAILED,
        NodeStatus.DONE, NodeStatus.ESCALATED, NodeStatus.DISCHARGING,
        NodeStatus.REFINING,
    )
    if node.status in _NON_SCHEDULABLE:
        return RouterAction.NOOP, RationaleCode.NEEDS_HUMAN_INTERPRETATION

    has_hard_validator = (
        node.validator_ref is not None
        and node.validation_strength is ValidationStrength.HARD
    )

    # 1. A HARD validator is available -> discharge (checked before FAIL on
    #    attempts so a still-dischargeable node isn't prematurely failed; depth
    #    exhaustion only blocks *refinement*, not a ready discharge).
    if has_hard_validator and node.status not in (
        NodeStatus.AWAITING_ACCEPTANCE,
    ):
        return RouterAction.DISCHARGE, RationaleCode.HARD_VALIDATOR_AVAILABLE

    # 2. An explicit acceptance point (top node / awaiting acceptance, no HARD
    #    oracle) -> escalate to HITL rather than loop.
    if node.status is NodeStatus.AWAITING_ACCEPTANCE or (
        node.parent_id is None and not has_hard_validator
        and node.status is not NodeStatus.PENDING
    ):
        return RouterAction.ESCALATE, RationaleCode.NEEDS_HUMAN_INTERPRETATION

    # 3. Can we still refine? Depth cap blocks deeper decomposition.
    if depth >= budget.max_depth:
        return RouterAction.FAIL, RationaleCode.BUDGET_EXHAUSTED

    # 4. Attempts exhausted with no discharge -> no-progress FAIL.
    if attempts >= budget.max_attempts:
        return RouterAction.FAIL, RationaleCode.NO_REFINEMENT_PROGRESS

    # 5. Otherwise decompose.
    return RouterAction.REFINE, RationaleCode.NO_VALIDATOR_YET
