"""Frozen enums for the goal engine (Task 0.2).

Controlled vocabularies for validator strength, node lifecycle, router
outcomes, failure taxonomy, and machine-checkable router rationale codes.

Design notes:
- **No SEMANTIC strength in v0** (Simplifier S3): v0 ships ``accept()`` only,
  no advisory assessor. Re-add ``SEMANTIC`` when a second goal needs it.
- Every ``NodeStatus`` is reached by a Phase-3 task (prove-or-cut) — no
  aspirational states.
- ``FailureClass`` carries an explicit, total, stable severity order so
  deterministic failure selection (Task 2.4) is reproducible: lower
  ``severity`` == worse, so a plain ``sorted(..., key=severity)`` yields
  worst-first.
"""

from __future__ import annotations

from enum import Enum


class ValidationStrength(str, Enum):
    """What a validator's receipt is allowed to prove.

    HARD discharges a done-contract (an executable test passed). ADMISSIBILITY
    proves *well-formedness* only (schema/citation/internal-consistency of a
    proposal) and can NEVER attest that a command executed nor discharge a HARD
    obligation (invariant 3/5).
    """

    HARD = "hard"
    ADMISSIBILITY = "admissibility"


class NodeStatus(str, Enum):
    """Lifecycle of a ``ProofObligationNode`` (a journal projection, invariant 7)."""

    PENDING = "pending"
    REFINING = "refining"
    DISCHARGING = "discharging"
    ADMISSIBILITY_PASSED = "admissibility_passed"
    HARD_DISCHARGED = "hard_discharged"
    ESCALATED = "escalated"
    AWAITING_ACCEPTANCE = "awaiting_acceptance"
    BLOCKED = "blocked"
    FAILED = "failed"
    DONE = "done"


class RouterAction(str, Enum):
    """The four outcomes of the one per-node routing decision."""

    DISCHARGE = "discharge"
    REFINE = "refine"
    ESCALATE = "escalate"
    FAIL = "fail"


class FailureClass(str, Enum):
    """Candidate-failure taxonomy, worst -> least.

    ``severity`` is the total-order rank (lower == worse). Deterministic
    selection sorts candidates by ``severity`` then a run-relative tiebreak.
    """

    CLEAN_INSTALL_BLOCKER = "clean_install_blocker"
    DOCUMENTED_COMMAND_FAILURE = "documented_command_failure"
    TEST_FAILURE = "test_failure"
    UNKNOWN = "unknown"

    @property
    def severity(self) -> int:
        """Total-order rank; lower is worse (sorts worst-first)."""
        return _FAILURE_SEVERITY[self]

    @classmethod
    def worst_to_least(cls) -> "list[FailureClass]":
        """The canonical worst->least ordering."""
        return sorted(cls, key=lambda f: f.severity)


# Explicit, total, stable severity map. Distinct ints => no ties => total order.
_FAILURE_SEVERITY = {
    FailureClass.CLEAN_INSTALL_BLOCKER: 0,
    FailureClass.DOCUMENTED_COMMAND_FAILURE: 1,
    FailureClass.TEST_FAILURE: 2,
    FailureClass.UNKNOWN: 3,
}


class RationaleCode(str, Enum):
    """Machine-checkable reasons the router emits alongside its action."""

    NO_VALIDATOR_YET = "no_validator_yet"
    HARD_VALIDATOR_AVAILABLE = "hard_validator_available"
    BUDGET_EXHAUSTED = "budget_exhausted"
    NO_REFINEMENT_PROGRESS = "no_refinement_progress"
    NEEDS_HUMAN_INTERPRETATION = "needs_human_interpretation"
    RESUME_REVERIFY_FAILED = "resume_reverify_failed"
