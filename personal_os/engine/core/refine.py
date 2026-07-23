"""Task 2.4 / 2.5 — the refiner core (selection + decomposition).

``select_failure(candidates)`` (Task 2.4) deterministically picks the worst
failure by ``FailureClass`` total order, tiebreaking on a RUN-RELATIVE locator
(absolute locators are rejected — Skeptic E6). No LLM.

``refine(node, worker, run_dir, journal)`` (Task 2.5) runs the research track:
worker (REFINE) → ``AdmissibilityValidator`` → ``select_failure`` →
``compile_leaf_contract`` an execution child **from the selected evidenced
failure** (compiled from evidence, never preselected). It commits a
CHILDREN_ADDED event. The compiled execution child's contract fingerprint
equals the Phase-1 leaf's (proven by Task 2.2 parity).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List

from personal_os.engine.contract.enums import FailureClass


def select_failure(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pick the worst candidate failure deterministically.

    Order: ``FailureClass`` severity (worst first), then lexicographic
    run-relative ``locator``. A candidate with an absolute locator is rejected
    (invariant: selection tiebreaks never depend on an absolute path).
    """
    if not candidates:
        raise ValueError("no candidate failures to select from")

    def sort_key(cand: Dict[str, Any]):
        fc_name = cand.get("failure_class")
        try:
            severity = FailureClass[fc_name].severity
        except KeyError:
            severity = FailureClass.UNKNOWN.severity
        locator = cand.get("locator", "")
        if os.path.isabs(locator):
            raise ValueError(f"locator must be run-relative, got absolute: {locator!r}")
        return (severity, locator)

    return sorted(candidates, key=sort_key)[0]


@dataclass
class RefineResult:
    admissible: bool
    children: List[Dict[str, Any]]
    receipt: Any


def refine(node, worker, run_dir, journal) -> "RefineResult":
    """Run the research track: propose → admit → select → compile exec child.

    1. worker (REFINE) proposes a research decomposition (untrusted data),
    2. ``AdmissibilityValidator`` proves it well-formed (never correct),
    3. on admissibility, ``select_failure`` picks the worst evidenced failure,
    4. ``compile_leaf_contract`` builds the execution child FROM that selected,
       evidenced failure (compiled from evidence, never preselected),
    5. commit a CHILDREN_ADDED event.

    Returns the children (research + at most one execution) and the
    admissibility receipt. If the proposal is inadmissible, no execution child
    is emitted.
    """
    from personal_os.engine.contract.enums import NodeStatus
    from personal_os.engine.contract.journal import EventType
    from personal_os.engine.core.contract_compiler import compile_leaf_contract
    from personal_os.engine.ports.worker import WorkKind, WorkRequest
    from personal_os.engine.ports.conformance import assert_workresult_contract
    from personal_os.engine.validators.admissibility import AdmissibilityValidator

    journal.append(EventType.NODE_STATUS, node_id=node.id,
                   payload={"status": NodeStatus.REFINING.value})

    request = WorkRequest(
        kind=WorkKind.REFINE,
        run_id=run_dir.run_id,
        node_id=node.id,
        attempt=1,
        objective=node.objective,
        contract=dict(node.done_contract),
    )
    result = worker.execute(request)
    assert_workresult_contract(result, run_dir)

    # The refiner's proposal rides in the (untrusted) evidence_proposals; Core
    # extracts it as DATA and validates it before acting.
    proposal = {}
    for ev in result.evidence_proposals:
        if ev.get("claim_id") == "refine-proposal":
            proposal = ev.get("proposal", {})
            break

    receipt = AdmissibilityValidator().validate(
        run_dir, node=node, config={"proposal": proposal})

    # The research child is always recorded (it IS the decomposition step).
    children: List[Dict[str, Any]] = [
        {"id": f"{node.id}-research", "parent_id": node.id, "role": "research",
         "objective": "inspect project + gather clean-run evidence"},
    ]

    if receipt.passed:
        chosen = select_failure(proposal.get("candidate_failures", []))
        # Compile the execution child's contract FROM the selected evidenced
        # failure (never preselected). The refiner's proposal carries the
        # command evidence the contract is built from.
        exec_contract = compile_leaf_contract(proposal["execution_contract"])
        children.append({
            "id": f"{node.id}-exec", "parent_id": node.id, "role": "execution",
            "objective": exec_contract["objective"],
            "contract": exec_contract,
            "selected_failure": chosen,
        })

    journal.append(EventType.CHILDREN_ADDED, node_id=node.id,
                   payload={"children": [c["id"] for c in children]})

    return RefineResult(admissible=receipt.passed, children=children, receipt=receipt)
