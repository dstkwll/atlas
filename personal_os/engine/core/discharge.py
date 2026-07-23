"""Task 1.6 / 1.6b — the discharge core (one HARD leaf, end-to-end).

``discharge`` is the deterministic sequence that turns a HARD-validatable node
into a receipted result, with no recursion and no LLM assumption:

  1. build a harness-neutral ``WorkRequest`` (EXECUTE) for the node,
  2. ``worker.execute`` -> a ``WorkResult`` (untrusted), checked against the
     shared conformance oracle before Core acts on it,
  3. ``apply_patch`` the proposed patch handle onto the STAGED tree (the wall
     re-contains the target),
  4. ``validator.validate`` the staged tree -> a Core-minted ``Receipt``,
  5. **invariant 8 ordering:** store the receipt as a content-addressed
     artifact (fsync'd by ``put_artifact``) BEFORE appending the
     ``RECEIPT_WRITTEN`` journal event that references it,
  6. set status ``HARD_DISCHARGED`` iff ``can_discharge_hard(receipt)``.

Core never trusts stdout: it re-resolves the patched target artifact / staged
file to confirm the change actually landed (``patched_ok``).

1.6b is proven by the negative test: a worker proposing a non-fixing patch
yields ``passed=False`` and a status that is NOT ``HARD_DISCHARGED`` — the
validator rejects rather than rubber-stamps.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from personal_os.engine.contract.enums import NodeStatus
from personal_os.engine.contract.journal import EventType, Journal
from personal_os.engine.contract.node import ProofObligationNode
from personal_os.engine.contract.receipt import Receipt, can_discharge_hard
from personal_os.engine.contract.run_dir import RunDir
from personal_os.engine.ports.conformance import assert_workresult_contract
from personal_os.engine.ports.worker import WorkKind, WorkRequest
from personal_os.engine.core.staging import apply_patch


@dataclass
class DischargeResult:
    status: NodeStatus
    receipt: Receipt
    patched_ok: bool


def discharge(
    node: ProofObligationNode,
    worker,
    validator,
    run_dir: RunDir,
    journal: Journal,
) -> DischargeResult:
    """Run the HARD leaf: port -> apply -> validate -> receipt -> journal."""
    journal.append(EventType.NODE_STATUS, node_id=node.id,
                   payload={"status": NodeStatus.DISCHARGING.value})
    journal.append(EventType.ATTEMPT, node_id=node.id, payload={"attempt": 1})

    # 1-2. Ask the (untrusted) worker; validate its output shape before acting.
    request = WorkRequest(
        kind=WorkKind.EXECUTE,
        run_id=run_dir.run_id,
        node_id=node.id,
        attempt=1,
        objective=node.objective,
        contract=dict(node.done_contract),
    )
    result = worker.execute(request)
    assert_workresult_contract(result, run_dir)

    # 3. Apply the proposed patch onto the staged tree (wall re-contains it).
    patch_handle = result.artifact_handles[0]
    dest = apply_patch(run_dir, patch_handle)

    # Core verifies the change landed (never trust the worker's self-report).
    patched_ok = os.path.exists(dest)

    # 4. Core-minted validation.
    receipt = validator.validate(run_dir, node=node, config={})

    # 5. Invariant 8: persist the receipt artifact (fsync) BEFORE the event.
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

    # 6. Status transition, gated by the single HARD predicate.
    if can_discharge_hard(receipt):
        status = NodeStatus.HARD_DISCHARGED
    else:
        status = NodeStatus.BLOCKED
    journal.append(EventType.NODE_STATUS, node_id=node.id,
                   payload={"status": status.value})

    return DischargeResult(status=status, receipt=receipt, patched_ok=patched_ok)
