"""Task 2.4 / 2.5 — the refiner core (selection + decomposition).

``select_failure(candidates)`` (Task 2.4) deterministically picks the worst
failure by ``FailureClass`` total order, tiebreaking on a RUN-RELATIVE locator
(absolute locators are rejected — Skeptic E6). No LLM.

``refine(node, worker, run_dir, journal, attempt=1)`` (Task 2.5) runs the research track:
worker (REFINE) → ``AdmissibilityValidator`` → ``select_failure`` →
``compile_leaf_contract`` an execution child **from the selected evidenced
failure** (compiled from evidence, never preselected). It commits a
CHILDREN_ADDED event. The compiled execution child's contract fingerprint
equals the Phase-1 leaf's (proven by Task 2.2 parity).
"""

from __future__ import annotations

import json
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


def refine(node, worker, run_dir, journal, attempt: int = 1) -> "RefineResult":
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
        attempt=attempt,
        objective=node.objective,
        contract=dict(node.done_contract),
    )
    try:
        result = worker.execute(request)
    except Exception:
        # A detached refiner may fail without returning a WorkResult. Treat that
        # as a normal negative outcome so the durable lifecycle is not stranded
        # in REFINING.
        result = None

    if result is not None:
        assert_workresult_contract(result, run_dir)

    if result is None or result.status != "ok":
        # Only a successful refiner result may reach proposal validation and
        # child compilation. Core mints and persists the negative receipt before
        # terminalizing the node, exactly as at the discharge worker seam.
        receipt = AdmissibilityValidator().validate(
            run_dir, node=node, config={"proposal": {}})
        receipt_bytes = json.dumps(receipt.to_dict(), sort_keys=True).encode("utf-8")
        receipt_handle = run_dir.put_artifact(receipt_bytes)
        journal.append(
            EventType.RECEIPT_WRITTEN,
            node_id=node.id,
            payload={
                "receipt_handle": receipt_handle.to_str(),
                "passed": receipt.passed,
                "validator_id": receipt.validator_id,
            },
        )
        journal.append(
            EventType.NODE_STATUS,
            node_id=node.id,
            payload={"status": NodeStatus.BLOCKED.value,
                     "rationale": "refiner_worker_failed"},
        )
        return RefineResult(admissible=False, children=[], receipt=receipt)

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

    def block_malformed_proposal() -> "RefineResult":
        """Fail closed if malformed data slips past the validator boundary."""
        journal.append(
            EventType.NODE_STATUS,
            node_id=node.id,
            payload={
                "status": NodeStatus.BLOCKED.value,
                "rationale": "malformed_admitted_refine_proposal",
            },
        )
        return RefineResult(admissible=False, children=[], receipt=receipt)

    if receipt.passed:
        candidates = proposal.get("candidate_failures")
        execution_contract = proposal.get("execution_contract")
        if (
            not isinstance(candidates, list)
            or not candidates
            or not all(isinstance(candidate, dict) for candidate in candidates)
            or not isinstance(execution_contract, dict)
        ):
            return block_malformed_proposal()

        try:
            chosen = select_failure(candidates)
            locator = chosen.get("locator")
            if not isinstance(locator, str) or not locator:
                return block_malformed_proposal()
            contract_fields = dict(execution_contract)
            contract_fields["target"] = locator
            exec_contract = compile_leaf_contract(contract_fields)
        except (KeyError, TypeError, ValueError):
            return block_malformed_proposal()
        # Compile the execution child's contract FROM the selected evidenced
        # failure: the failure's run-relative locator BECOMES the contract
        # target (derived, never lifted from a preselected target). The refiner
        # supplies the command scaffold (install/run/test) as evidence; Core
        # binds the target to what selection actually chose.
        children.append({
            "id": f"{node.id}-exec", "parent_id": node.id, "role": "execution",
            "objective": exec_contract["objective"],
            "contract": exec_contract,
            "selected_failure": chosen,
        })

    # F13/sol-10: enforce max_children BEFORE committing CHILDREN_ADDED. If the
    # compiled child set exceeds the node's budget, fail closed (no children
    # emitted, admissible=False) rather than silently overrunning the budget.
    if len(children) > node.budget.max_children:
        journal.append(EventType.NODE_STATUS, node_id=node.id,
                       payload={"status": NodeStatus.BLOCKED.value,
                                "rationale": "max_children_exceeded"})
        return RefineResult(admissible=False, children=[], receipt=receipt)

    journal.append(EventType.CHILDREN_ADDED, node_id=node.id,
                   payload={"children": [c["id"] for c in children]})

    return RefineResult(admissible=receipt.passed, children=children, receipt=receipt)
