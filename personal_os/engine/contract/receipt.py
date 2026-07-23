"""Task 0.5 — the Core-minted ``Receipt`` (frozen contract data).

A ``Receipt`` is the ONLY object that attests a validator ran and what it
proved. It is constructed exclusively by validator/Core code — NEVER from
worker output (invariant 1: workers propose artifacts+evidence, Core mints the
receipt). No worker-supplied "passed" bit is ever trusted.

``can_discharge_hard(receipt)`` is the single predicate the router uses to
decide a HARD discharge: True iff ``strength == HARD and passed``. An
ADMISSIBILITY receipt — even a passed one — can NEVER discharge a HARD
obligation (invariant 3/5): structural well-formedness is not correctness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .enums import ValidationStrength


@dataclass
class Receipt:
    """Core-minted proof that a validator ran. Never built from worker output."""

    node_id: str
    validator_id: str
    validator_version: str
    strength: ValidationStrength
    ran: bool
    passed: bool
    workspace_id: str
    commands: List[str] = field(default_factory=list)
    exit_codes: List[int] = field(default_factory=list)
    artifact_hashes: Dict[str, str] = field(default_factory=dict)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    residual: List[Dict[str, Any]] = field(default_factory=list)
    ts: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "validator_id": self.validator_id,
            "validator_version": self.validator_version,
            "strength": self.strength.value,
            "ran": self.ran,
            "passed": self.passed,
            "workspace_id": self.workspace_id,
            "commands": list(self.commands),
            "exit_codes": list(self.exit_codes),
            "artifact_hashes": dict(self.artifact_hashes),
            "evidence": list(self.evidence),
            "residual": list(self.residual),
            "ts": self.ts,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Receipt":
        return cls(
            node_id=d["node_id"],
            validator_id=d["validator_id"],
            validator_version=d["validator_version"],
            strength=ValidationStrength(d["strength"]),
            ran=bool(d["ran"]),
            passed=bool(d["passed"]),
            workspace_id=d["workspace_id"],
            commands=list(d.get("commands", [])),
            exit_codes=list(d.get("exit_codes", [])),
            artifact_hashes=dict(d.get("artifact_hashes", {})),
            evidence=list(d.get("evidence", [])),
            residual=list(d.get("residual", [])),
            ts=d.get("ts", ""),
        )


def can_discharge_hard(receipt: Receipt) -> bool:
    """True iff this receipt discharges a HARD obligation.

    The single gate the router consults. ADMISSIBILITY never discharges HARD,
    even when passed (invariant 3/5).
    """
    return receipt.strength is ValidationStrength.HARD and receipt.passed
