"""Task 4.2 — HITL acceptance: the single DONE writer (Panel P1-C2).

``mark_done`` is the ONE choke-point that transitions a node to ``DONE``. It
asserts the prior state is ``AWAITING_ACCEPTANCE`` and raises otherwise, so:

- the top goal never auto-DONEs (the scheduler leaves it AWAITING_ACCEPTANCE),
- DONE is unreachable from PENDING/BLOCKED/FAILED/HARD_DISCHARGED/etc.,
- there is exactly one writer of DONE in the codebase (grep-guarded by a test).

v0 ships ``mark_done`` only — no SEMANTIC assessor (Simplifier S3). A human
(via the CLI ``--accept``) is the acceptance authority.
"""

from __future__ import annotations

from dataclasses import replace

from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.run_dir import RunDir


def mark_done(node: ProofObligationNode) -> ProofObligationNode:
    """Transition a node AWAITING_ACCEPTANCE -> DONE. The ONLY DONE writer.

    Raises ``ValueError`` if the prior state is anything other than
    ``AWAITING_ACCEPTANCE`` (a fail-closed choke-point).
    """
    if node.status is not NodeStatus.AWAITING_ACCEPTANCE:
        raise ValueError(
            f"mark_done requires AWAITING_ACCEPTANCE, got {node.status.value!r}"
        )
    return replace(node, status=NodeStatus.DONE)


def accept(run_dir: RunDir, node_id: str) -> NodeStatus:
    """Journal-authoritative acceptance (F14/sol-3): the ONLY safe accept path.

    Re-reads the node's CURRENT status from the journal projection (never trusts
    a caller-supplied in-memory node, which could be stale after a resume marked
    the node BLOCKED), gates through ``mark_done`` (AWAITING_ACCEPTANCE only),
    and appends the DONE transition itself. Returns the new status (DONE) or
    raises ``ValueError`` if the journal's current state isn't acceptable.
    """
    # Local imports to avoid a contract<-core import cycle at module load.
    from personal_os.engine.contract.journal import EventType, Journal, replay

    proj = replay(run_dir.events_path)
    status_str = proj.node_status.get(node_id)
    if status_str is None:
        raise ValueError(f"node {node_id!r} not found in run journal")

    # Build a minimal node carrying ONLY the journal-authoritative status and
    # gate it through the single mark_done writer.
    current = ProofObligationNode(
        id=node_id, parent_id=None, objective="", done_contract={},
        admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=1, max_children=0, max_attempts=1),
        status=NodeStatus(status_str), provenance={},
    )
    done = mark_done(current)  # raises unless AWAITING_ACCEPTANCE

    journal = Journal(run_dir.events_path, run_id=run_dir.run_id)
    journal.append(EventType.NODE_STATUS, node_id=node_id,
                   payload={"status": done.status.value})
    return done.status
