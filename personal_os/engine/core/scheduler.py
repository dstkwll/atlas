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

import dataclasses
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from personal_os.engine.contract.enums import (
    NodeStatus,
    RouterAction,
    ValidationStrength,
)
from personal_os.engine.contract.journal import EventType, Journal, replay
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.run_dir import ArtifactHandle, RunDir
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
        # The journal is authoritative for BOTH lifecycle and attempts. A stale
        # caller object must not restart a node that the durable projection has
        # already moved to a terminal or transitional state.
        proj = replay(self._rd.events_path)
        self._statuses = {
            node_id: NodeStatus(status) for node_id, status in proj.node_status.items()
        }
        top = self._with_journal_state(top, proj)
        action, rationale = route(top, proj)
        if top.id not in proj.node_status and action is not RouterAction.NOOP:
            self._journal.append(EventType.NODE_CREATED, node_id=top.id,
                                 payload={"status": top.status.value})
        self._statuses[top.id] = top.status

        if action is RouterAction.REFINE:
            top_status = self._handle_refine(top)
        elif action is RouterAction.DISCHARGE:
            top_status = self._discharge_node(top)
        elif action is RouterAction.FAIL:
            top_status = NodeStatus.FAILED
            self._set(top.id, top_status)
        elif action is RouterAction.ESCALATE:
            top_status = NodeStatus.ESCALATED
            self._set(top.id, top_status)
        elif action is RouterAction.NOOP:
            top_status = top.status
        else:
            raise AssertionError(f"unhandled router action: {action}")

        return RunOutcome(top_status=top_status, node_statuses=dict(self._statuses))

    def _handle_refine(self, top: ProofObligationNode) -> NodeStatus:
        attempt = replay(self._rd.events_path).attempt_counts.get(top.id, 0) + 1
        self._journal.append(EventType.ATTEMPT, node_id=top.id,
                             payload={"attempt": attempt})
        result = refine(top, self._refiner, self._rd, self._journal, attempt=attempt)

        if not result.admissible:
            # Refine may have already terminalized a worker failure (or another
            # malformed negative path) as BLOCKED. Preserve that Core-owned
            # terminal status instead of reclassifying it from the depth budget.
            durable_status = replay(self._rd.events_path).node_status.get(top.id)
            if durable_status == NodeStatus.BLOCKED.value:
                self._statuses[top.id] = NodeStatus.BLOCKED
                return NodeStatus.BLOCKED

            # No admissible decomposition -> nothing to discharge. If the depth
            # budget is exhausted (can't refine deeper), it's a hard FAILED;
            # otherwise BLOCKED (no stronger refinement appeared).
            depth = int(top.provenance.get("depth", 0))
            if depth >= top.budget.max_depth - 1:
                top_status = NodeStatus.FAILED
            else:
                top_status = NodeStatus.BLOCKED
            self._set(top.id, top_status)
            return top_status

        exec_discharged = False
        for child in result.children:
            child_id = child["id"]
            proj = replay(self._rd.events_path)
            if child_id not in proj.node_status:
                self._journal.append(EventType.NODE_CREATED, node_id=child_id,
                                     payload={"status": NodeStatus.PENDING.value})
                self._statuses[child_id] = NodeStatus.PENDING
            else:
                self._statuses[child_id] = NodeStatus(proj.node_status[child_id])
            role = child.get("role")
            if role == "research":
                # The research child's admissibility already passed (it IS the
                # decomposition the refiner produced) -> ADMISSIBILITY_PASSED.
                # This can NEVER discharge a HARD obligation (invariant 5).
                if self._statuses[child_id] is NodeStatus.PENDING:
                    self._set(child_id, NodeStatus.ADMISSIBILITY_PASSED)
            elif role == "execution":
                # F10 (invariant 5): the ROUTER — not the role string — decides
                # the verb. Build the node, ask route(), and only discharge if
                # the router authorizes DISCHARGE. The scheduler never
                # self-selects a verb from role.
                node = self._with_journal_state(
                    self._build_execution_node(child), replay(self._rd.events_path),
                )
                action, _rationale = route(node, self._projection())
                if action is RouterAction.DISCHARGE:
                    status = self._discharge_node(node)
                    if status is NodeStatus.HARD_DISCHARGED:
                        exec_discharged = True
                elif action is RouterAction.FAIL:
                    self._set(child_id, NodeStatus.FAILED)
                elif action is RouterAction.ESCALATE:
                    self._set(child_id, NodeStatus.ESCALATED)
                elif action is RouterAction.REFINE:
                    # No deeper recursion in v0.
                    self._set(child_id, NodeStatus.BLOCKED)
                elif action is RouterAction.NOOP:
                    if node.status is NodeStatus.HARD_DISCHARGED:
                        exec_discharged = True
                else:
                    raise AssertionError(f"unhandled router action: {action}")

        # A parent is eligible only if its execution child actually
        # HARD-discharged (a BLOCKED child cannot make it eligible — Skeptic E5).
        if exec_discharged:
            top_status = NodeStatus.AWAITING_ACCEPTANCE
        else:
            top_status = NodeStatus.BLOCKED
        self._set(top.id, top_status)
        return top_status

    def _projection(self) -> "LifecycleProjection":
        """A LifecycleProjection view of the scheduler's current statuses."""
        proj = LifecycleProjection()
        proj.node_status = {nid: st.value for nid, st in self._statuses.items()}
        return proj

    @staticmethod
    def _with_journal_state(
        node: ProofObligationNode,
        projection: LifecycleProjection,
    ) -> ProofObligationNode:
        """Return ``node`` with durable status and attempt count injected."""
        provenance = dict(node.provenance)
        provenance["attempts"] = projection.attempt_counts.get(node.id, 0)
        status = NodeStatus(projection.node_status[node.id]) \
            if node.id in projection.node_status else node.status
        return dataclasses.replace(node, status=status, provenance=provenance)

    def _build_execution_node(self, child: Dict[str, Any]) -> ProofObligationNode:
        """Build a HARD execution node from a compiled child (does NOT discharge)."""
        contract = child["contract"]
        return ProofObligationNode(
            id=child["id"], parent_id=child["parent_id"],
            objective=child["objective"], done_contract=dict(contract),
            admissible_evidence=[], validator_ref=self._hard.id,
            validation_strength=ValidationStrength.HARD,
            budget=Budget(max_depth=1, max_children=0, max_attempts=1),
            status=NodeStatus.PENDING, provenance={"depth": 1, "attempts": 0},
        )

    def _discharge_node(self, node: ProofObligationNode) -> NodeStatus:
        result = discharge(node, self._worker, self._hard, self._rd, self._journal)
        # discharge already journaled the status; mirror into our projection.
        self._statuses[node.id] = result.status
        return result.status


def resume(run_dir: RunDir, hard_validator) -> RunOutcome:
    """Resume a crashed run: rebuild projection + re-verify the frontier.

    Bounded, VERIFICATION-ONLY (invariant 8 / Skeptic D3):
    - rebuild the ``LifecycleProjection`` from the journal (torn tail tolerated,
      events deduped),
    - for each node the projection reports as ``HARD_DISCHARGED``, re-verify its
      receipt cheaply by re-hashing the receipted artifact: the receipt artifact
      must still be present AND its bytes must still content-address to the same
      handle,
    - a passing re-verify leaves the node ``HARD_DISCHARGED`` (no re-run, no
      attempt consumed),
    - a failing re-verify (missing/changed artifact) marks the node ``BLOCKED``
      with ``RESUME_REVERIFY_FAILED`` — it NEVER re-enters ``DISCHARGING`` and
      never fabricates a stale success.

    Returns a ``RunOutcome`` reflecting the reconciled projection.
    """
    from personal_os.engine.contract.enums import RationaleCode
    from personal_os.engine.contract.journal import Journal, replay

    proj = replay(run_dir.events_path)
    journal = Journal(run_dir.events_path, run_id=run_dir.run_id)

    statuses: Dict[str, NodeStatus] = {}
    for node_id, status_str in proj.node_status.items():
        statuses[node_id] = NodeStatus(status_str)

    # F11 (sol-2): fail-closed on interrupted transitional states. A crash
    # mid-DISCHARGING / mid-REFINING (or after RECEIPT_WRITTEN but before the
    # terminal status) leaves the node in a non-terminal transitional state.
    # Resume NEVER continues or infers success from an incomplete transition —
    # it marks every such node BLOCKED with a recovery rationale.
    _TRANSITIONAL = (NodeStatus.DISCHARGING, NodeStatus.REFINING)
    for node_id, status in list(statuses.items()):
        if status in _TRANSITIONAL:
            statuses[node_id] = NodeStatus.BLOCKED
            journal.append(
                EventType.NODE_STATUS, node_id=node_id,
                payload={"status": NodeStatus.BLOCKED.value,
                         "rationale": RationaleCode.RESUME_INTERRUPTED_TRANSITION.value},
            )

    # Re-verify every HARD_DISCHARGED node on the frontier (verification-only).
    for node_id, status in list(statuses.items()):
        if status is not NodeStatus.HARD_DISCHARGED:
            continue
        ok = _reverify_receipt(run_dir, proj, node_id)
        if not ok:
            statuses[node_id] = NodeStatus.BLOCKED
            journal.append(
                EventType.NODE_STATUS, node_id=node_id,
                payload={"status": NodeStatus.BLOCKED.value,
                         "rationale": RationaleCode.RESUME_REVERIFY_FAILED.value},
            )

    # Reconcile the top: if its execution child is no longer HARD_DISCHARGED, the
    # top can no longer be AWAITING_ACCEPTANCE (a BLOCKED child can't keep the
    # parent eligible — Skeptic E5).
    top_id = _find_top(proj)
    top_status = statuses.get(top_id, NodeStatus.PENDING)
    if top_status is NodeStatus.AWAITING_ACCEPTANCE:
        exec_ok = any(
            nid.startswith(top_id) and nid.endswith("-exec")
            and statuses.get(nid) is NodeStatus.HARD_DISCHARGED
            for nid in statuses
        )
        if not exec_ok:
            top_status = NodeStatus.BLOCKED
            statuses[top_id] = top_status
            journal.append(EventType.NODE_STATUS, node_id=top_id,
                           payload={"status": NodeStatus.BLOCKED.value,
                                    "rationale": RationaleCode.RESUME_REVERIFY_FAILED.value})

    return RunOutcome(top_status=top_status, node_statuses=statuses)


def _find_top(proj) -> str:
    """The top node id (a NODE_CREATED with no parent-derived suffix)."""
    # In v0 the top is the shortest node id (children are "<top>-role").
    if not proj.node_status:
        return "top"
    return min(proj.node_status.keys(), key=len)


def _reverify_receipt(run_dir: RunDir, proj, node_id: str) -> bool:
    """Cheaply re-verify a node's receipt: blob + every referenced artifact.

    Re-hashes (a) the receipt blob itself and (b) EVERY artifact the receipt
    references in ``artifact_hashes`` (captured stdout/stderr/patch). All must be
    present and content-address to their recorded hash. This is the spec's
    "re-hash the receipted artifacts" — one level deeper than the blob alone, so
    losing a referenced artifact (even with the receipt intact) trips re-verify.
    """
    import hashlib
    import json as _json

    receipts = proj.receipts.get(node_id, [])
    if not receipts:
        return False
    receipt_event = receipts[-1]
    if not isinstance(receipt_event, dict):
        return False
    handle_str = receipt_event.get("receipt_handle")
    if not handle_str:
        return False
    try:
        handle = ArtifactHandle.from_str(handle_str)
    except (TypeError, ValueError):
        return False
    sha = handle.id
    blob_path = os.path.join(run_dir.artifacts_dir, sha)
    if not os.path.exists(blob_path):
        return False
    with open(blob_path, "rb") as f:
        blob = f.read()
    if hashlib.sha256(blob).hexdigest() != sha:
        return False

    # Re-hash every artifact the receipt references.
    try:
        receipt = _json.loads(blob.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return False
    if not isinstance(receipt, dict):
        return False
    artifact_hashes = receipt.get("artifact_hashes", {})
    if not isinstance(artifact_hashes, dict):
        return False
    for ref_handle, ref_sha in artifact_hashes.items():
        if not isinstance(ref_handle, str) or not isinstance(ref_sha, str):
            return False
        try:
            parsed = ArtifactHandle.from_str(ref_handle)
        except (TypeError, ValueError):
            return False
        if parsed.id != ref_sha:
            return False
        try:
            ref_path = run_dir.resolve_handle(parsed)
        except (ValueError, KeyError):
            return False
        with open(ref_path, "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != ref_sha:
                return False

    # F12 (sol-5): re-verify the CERTIFIED STAGED OUTPUT, not just the receipt +
    # stdout blobs. The receipt binds ``workspace_id`` = the hash of the staged
    # tree at certification time. Re-hash the staged tree now; a changed/deleted
    # staged target yields a different hash even if the receipt + stdout blobs
    # are intact, so a stale HARD_DISCHARGED can't survive a tampered output.
    bound_ws = receipt.get("workspace_id")
    if not isinstance(bound_ws, str) or not bound_ws:
        return False
    from personal_os.engine.contract.workspace import Workspace
    try:
        current_ws = Workspace(run_dir.staging_dir).id
    except Exception:  # pragma: no cover - fail closed
        return False
    if current_ws != bound_ws:
        return False
    return True
