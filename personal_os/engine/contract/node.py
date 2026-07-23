"""Task 0.3 — ``ProofObligationNode`` + ``Budget`` (frozen contract data).

The ``ProofObligationNode`` is the ONE recursive unit of work. It deliberately
has **no ``kind`` / ``is_leaf`` field** — its absence is load-bearing
(Architect one-primitive check): the router is the sole authority that maps
``validation_strength`` to a verb (DISCHARGE/REFINE/...), so a node never
self-declares whether it is a leaf.

``Budget`` ships three dimensions in v0: ``max_depth``, ``max_children``,
``max_attempts`` (token/cost/seconds deferred — Simplifier Y1). These are the
caps that enforce termination (invariant / anti-pathological-decomposition).

Serialization is deterministic: ``to_dict``/``from_dict`` round-trip and the
dict is JSON-serializable with stable key order via ``sort_keys`` at write
sites. Unknown enum values are rejected at ``from_dict`` time (fail-closed).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .enums import NodeStatus, ValidationStrength


@dataclass
class Budget:
    """Termination caps (3 dims in v0)."""

    max_depth: int
    max_children: int
    max_attempts: int

    def to_dict(self) -> Dict[str, int]:
        return {
            "max_depth": self.max_depth,
            "max_children": self.max_children,
            "max_attempts": self.max_attempts,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Budget":
        return cls(
            max_depth=int(d["max_depth"]),
            max_children=int(d["max_children"]),
            max_attempts=int(d["max_attempts"]),
        )


@dataclass
class ProofObligationNode:
    """The one recursive unit of work. NO ``kind``/``is_leaf`` — by design."""

    id: str
    parent_id: Optional[str]
    objective: str
    done_contract: Dict[str, Any]
    admissible_evidence: List[Any]
    validator_ref: Optional[str]
    validation_strength: ValidationStrength
    budget: Budget
    status: NodeStatus
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "objective": self.objective,
            "done_contract": self.done_contract,
            "admissible_evidence": self.admissible_evidence,
            "validator_ref": self.validator_ref,
            "validation_strength": self.validation_strength.value,
            "budget": self.budget.to_dict(),
            "status": self.status.value,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProofObligationNode":
        # Enum coercion fails closed on unknown values (raises ValueError).
        return cls(
            id=d["id"],
            parent_id=d["parent_id"],
            objective=d["objective"],
            done_contract=dict(d["done_contract"]),
            admissible_evidence=list(d["admissible_evidence"]),
            validator_ref=d["validator_ref"],
            validation_strength=ValidationStrength(d["validation_strength"]),
            budget=Budget.from_dict(d["budget"]),
            status=NodeStatus(d["status"]),
            provenance=dict(d.get("provenance", {})),
        )
