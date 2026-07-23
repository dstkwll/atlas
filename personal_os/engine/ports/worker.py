"""Task 1.1 — the WorkerPort contract (handles, not paths).

``WorkRequest``/``WorkResult`` are the harness-neutral payloads that cross the
``WorkerPort`` (invariant 9). They carry opaque ``ArtifactHandle``s only — the
adapter resolves a handle to its substrate; Core never mints a filesystem path
into a port payload.

``WorkResult`` deliberately has **no receipt and no pass bit**: a worker
returns *artifact + evidence proposals*; only Core/validator code mints a
``Receipt`` (invariant 1). The worker's output is untrusted until Core
validates it (invariant 2).

``WorkKind`` is harness-neutral verbs (Architect rec 5): REFINE (decompose),
EXECUTE (act against a validator), SYNTHESIZE (assemble). This is the operation
kind, not a node ``kind`` — nodes still carry no kind field.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from personal_os.engine.contract.run_dir import ArtifactHandle


class WorkKind(str, Enum):
    REFINE = "refine"
    EXECUTE = "execute"
    SYNTHESIZE = "synthesize"


@dataclass
class WorkRequest:
    """A harness-neutral unit of work handed to a worker adapter."""

    kind: WorkKind
    run_id: str
    node_id: str
    attempt: int
    objective: str
    contract: Dict[str, Any]
    input_handles: List[ArtifactHandle] = field(default_factory=list)
    output_handles: List[ArtifactHandle] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind.value,
            "run_id": self.run_id,
            "node_id": self.node_id,
            "attempt": self.attempt,
            "objective": self.objective,
            "contract": self.contract,
            "input_handles": [h.to_str() for h in self.input_handles],
            "output_handles": [h.to_str() for h in self.output_handles],
            "constraints": self.constraints,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WorkRequest":
        return cls(
            kind=WorkKind(d["kind"]),
            run_id=d["run_id"],
            node_id=d["node_id"],
            attempt=int(d["attempt"]),
            objective=d["objective"],
            contract=dict(d["contract"]),
            input_handles=[ArtifactHandle.from_str(s) for s in d.get("input_handles", [])],
            output_handles=[ArtifactHandle.from_str(s) for s in d.get("output_handles", [])],
            constraints=dict(d.get("constraints", {})),
        )


@dataclass
class WorkResult:
    """A worker's proposal: artifacts + evidence. NO receipt, NO pass bit."""

    status: str
    artifact_handles: List[ArtifactHandle] = field(default_factory=list)
    evidence_proposals: List[Dict[str, Any]] = field(default_factory=list)
    usage: Dict[str, Any] = field(default_factory=dict)
    failure: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "artifact_handles": [h.to_str() for h in self.artifact_handles],
            "evidence_proposals": list(self.evidence_proposals),
            "usage": dict(self.usage),
            "failure": self.failure,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WorkResult":
        return cls(
            status=d["status"],
            artifact_handles=[ArtifactHandle.from_str(s) for s in d.get("artifact_handles", [])],
            evidence_proposals=list(d.get("evidence_proposals", [])),
            usage=dict(d.get("usage", {})),
            failure=d.get("failure"),
        )


@runtime_checkable
class WorkerPort(Protocol):
    """The one seam the engine uses to invoke (untrusted) LLM/worker labor."""

    def execute(self, request: WorkRequest) -> WorkResult:
        """Perform the requested work; return proposals (never a receipt)."""
        ...
