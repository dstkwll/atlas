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

from personal_os.engine.contract.enums import NodeStatus
from personal_os.engine.contract.node import ProofObligationNode


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
