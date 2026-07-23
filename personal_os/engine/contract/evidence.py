"""Task 0.4 — Evidence + ResidualUncertainty (frozen contract data).

``Evidence`` is a proposal a worker cites and a validator checks. Its
``source_handle`` is an OPAQUE handle (invariant 9), never a filesystem path;
each adapter resolves the handle to its own substrate. ``sha256`` is optional
(a citation may reference a handle whose bytes aren't content-addressed yet).

``ResidualUncertainty`` is the honest record of what a refine node could NOT
prove — carried upward and rendered into synthesis, but (v0) it does not gate
scheduling (Simplifier Y4 / OpenQ1 deferred).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Evidence:
    """A cited, checkable artifact reference (opaque handle, not a path)."""

    claim_id: str
    kind: str
    source_handle: str
    sha256: Optional[str]
    accessed_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "kind": self.kind,
            "source_handle": self.source_handle,
            "sha256": self.sha256,
            "accessed_at": self.accessed_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Evidence":
        return cls(
            claim_id=d["claim_id"],
            kind=d["kind"],
            source_handle=d["source_handle"],
            sha256=d.get("sha256"),
            accessed_at=d["accessed_at"],
        )


@dataclass
class ResidualUncertainty:
    """What a node could not deterministically prove (carried upward)."""

    node_id: str
    statement: str
    why_unprovable: str
    impact_if_wrong: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "statement": self.statement,
            "why_unprovable": self.why_unprovable,
            "impact_if_wrong": self.impact_if_wrong,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ResidualUncertainty":
        return cls(
            node_id=d["node_id"],
            statement=d["statement"],
            why_unprovable=d["why_unprovable"],
            impact_if_wrong=d["impact_if_wrong"],
        )
