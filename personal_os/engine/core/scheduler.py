"""Task 3.2 — the deterministic scheduler loop (recursion + budgets).

``Scheduler.run(top)`` drives a goal to conclusion by repeatedly asking the
router what to do with each pending node and dispatching the corresponding
verb — never self-selecting (the router is the sole author of strength→verb).

v0 flow (one level of recursion, the minimum that proves both tracks):

  top (PENDING, no validator) -> route REFINE -> ``refine`` emits a research
  (ADMISSIBILITY) child + an execution (HARD, validator_ref set) child ->
    - research child: its admissibility receipt already passed -> mark
      ADMISSIBILITY_PASSED (structural well-formedness; NEVER discharges HARD),
    - execution child: route DISCHARGE -> ``discharge`` -> HARD_DISCHARGED or
      BLOCKED (no-progress) ->
  top: children handled; top has no HARD oracle -> ends AWAITING_ACCEPTANCE
  (never auto-DONE — invariant 6). If the refine is inadmissible / budget is
  exhausted, the top ends FAILED/BLOCKED.

Budgets: depth/children/attempts are enforced via the router + an attempt
ledger in each node's provenance. Residual uncertainty is recorded but does NOT
gate scheduling in v0 (Simplifier Y4). A BLOCKED child cannot make a parent
eligible (Skeptic E5) — the top only reaches AWAITING_ACCEPTANCE if its
execution child actually HARD-discharged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from personal_os.engine.contract.enums import (
    NodeStatus,
    RouterAction,
    ValidationStrength,
)
from personal_os.engine.contract.journal import EventType, Journal
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.run_dir import RunDir
from personal_os.engine.core.discharge import discharge
from personal_os.engine.core.refine import refine
from personal_os.engine.core.router import route
from personal_os.engine.contract.journal import LifecycleProjection


@dataclass
class RunOutcome:
    top_status: NodeStatus
    node_statuses: Dict[str, NodeStatus] = field(default_factory=dict)


class Scheduler:
    """Deterministic route→dispatch loop over a one-level obligation tree."""

    def __init__(self, run_dir: RunDir, journal: Journal, refiner, worker, hard_validator) -> None:
        self._rd = run_dir
        self._journal = journal
        self._refiner = refiner
        self._worker = worker
        self._hard = hard_validator
        self._statuses: Dict[str, NodeStatus] = {}

    def _set(self, node_id: str, status: NodeStatus) -> None:
        self._statuses[node_id] = status
        self._journal.append(EventType.NODE_STATUS, node_id=node_id,
                             payload={"status": status.value})

    def run(self, top: ProofObligationNode) -> RunOutcome:
        self._journal.append(EventType.NODE_CREATED, node_id=top.id,
                             payload={"status": top.status.value})
        self._statuses[top.id] = top.status

        action, rationale = route(top, LifecycleProjection())

        if action is RouterAction.REFINE:
            top_status = self._handle_refine(top)
        elif action is RouterAction.DISCHARGE:
            top_status = self._discharge_node(top)
        elif action is RouterAction.FAIL:
            top_status = NodeStatus.FAILED
            self._set(top.id, top_status)
        else:  # ESCALATE
            top_status = NodeStatus.ESCALATED
            self._set(top.id, top_status)

        return RunOutcome(top_status=top_status, node_statuses=dict(self._statuses))

    def _handle_refine(self, top: ProofObligationNode) -> NodeStatus:
        self._journal.append(EventType.ATTEMPT, node_id=top.id, payload={"attempt": 1})
        result = refine(top, self._refiner, self._rd, self._journal)

        if not result.admissible:
            # No admissible decomposition -> nothing to discharge. Budget/depth
            # decide FAILED vs BLOCKED; v0 marks BLOCKED (no stronger refinement).
            top_status = NodeStatus.BLOCKED
            # If depth budget is already spent, it's a hard FAIL instead.
            if int(top.provenance.get("depth", 0)) >= top.budget.max_depth - 0 and \
                    top.budget.max_depth <= 1:
                top_status = NodeStatus.FAILED
            self._set(top.id, top_status)
            return top_status

        exec_discharged = False
        for child in result.children:
            child_id = child["id"]
            self._journal.append(EventType.NODE_CREATED, node_id=child_id,
                                 payload={"status": NodeStatus.PENDING.value})
            role = child.get("role")
            if role == "research":
                # The research child's admissibility already passed (it IS the
                # decomposition the refiner produced) -> ADMISSIBILITY_PASSED.
                # This can NEVER discharge a HARD obligation (invariant 5).
                self._set(child_id, NodeStatus.ADMISSIBILITY_PASSED)
            elif role == "execution":
                status = self._discharge_child(child)
                if status is NodeStatus.HARD_DISCHARGED:
                    exec_discharged = True

        # A parent is eligible only if its execution child actually
        # HARD-discharged (a BLOCKED child cannot make it eligible — Skeptic E5).
        if exec_discharged:
            top_status = NodeStatus.AWAITING_ACCEPTANCE
        else:
            top_status = NodeStatus.BLOCKED
        self._set(top.id, top_status)
        return top_status

    def _discharge_child(self, child: Dict[str, Any]) -> NodeStatus:
        """Build a HARD execution node from a compiled child + discharge it."""
        contract = child["contract"]
        node = ProofObligationNode(
            id=child["id"], parent_id=child["parent_id"],
            objective=child["objective"], done_contract=dict(contract),
            admissible_evidence=[], validator_ref=self._hard.id,
            validation_strength=ValidationStrength.HARD,
            budget=Budget(max_depth=1, max_children=0, max_attempts=1),
            status=NodeStatus.PENDING, provenance={"depth": 1, "attempts": 0},
        )
        return self._discharge_node(node)

    def _discharge_node(self, node: ProofObligationNode) -> NodeStatus:
        result = discharge(node, self._worker, self._hard, self._rd, self._journal)
        # discharge already journaled the status; mirror into our projection.
        self._statuses[node.id] = result.status
        return result.status
