"""Task 2.3 — the ADMISSIBILITY validator (well-formedness ONLY).

This validator proves a research/refine proposal is **well-formed and
internally consistent** — NOT that it is correct, and emphatically NOT that any
command executed (invariant 3 / Panel P0-D1). It checks:

- every citation's ``source_handle`` RESOLVES in the run (the cited artifact
  exists) — this proves the citation is well-formed, not that its content is
  true or sufficient;
- every declared command *record* is schema-valid + self-consistent (has a
  ``cmd``, an integer ``exit_code``, and a ``log_handle`` that resolves) — this
  proves the record is well-formed, NOT that the command actually ran (a record
  is data a worker supplied; only a Core-run HARD validator can attest
  execution);
- candidate failures carry a valid ``FailureClass`` and a locator;
- children trace to the declared parent;
- a coverage map and residue are present.

It returns a Core-minted ADMISSIBILITY receipt. Because its strength is
ADMISSIBILITY, ``can_discharge_hard`` is always False on its output — a passing
admissibility receipt can never discharge a HARD obligation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from personal_os.engine.contract import ENGINE_SCHEMA_VERSION
from personal_os.engine.contract.enums import FailureClass, ValidationStrength
from personal_os.engine.contract.receipt import Receipt
from personal_os.engine.contract.run_dir import ArtifactHandle, RunDir

_VALID_FAILURE_CLASSES = {f.name for f in FailureClass}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AdmissibilityValidator:
    """Structural/provenance well-formedness check. Never attests execution."""

    id = "admissibility"
    version = "0.1.0"
    strength = ValidationStrength.ADMISSIBILITY

    def validate(self, workspace: RunDir, node: Any, config: Optional[Dict[str, Any]] = None) -> Receipt:
        config = config or {}
        proposal = config.get("proposal", {})
        run_dir = workspace
        reasons: List[str] = []

        # 0. The proposal itself must be a dict (fail closed, don't crash).
        if not isinstance(proposal, dict):
            reasons.append("proposal is not a dict")
            proposal = {}

        parent_id = proposal.get("parent_id")

        # 1. Citations: each must be a dict with a resolving source_handle.
        for cite in _as_list(proposal.get("citations")):
            if not isinstance(cite, dict):
                reasons.append("citation is not a dict")
                continue
            if not cite.get("claim_id"):
                reasons.append("citation missing claim_id")
            self._require_resolves(run_dir, cite.get("source_handle"), reasons,
                                   "citation source_handle")

        # 2. Command RECORDS are schema-valid + self-consistent — proves
        #    well-formedness, NOT that the command executed (invariant 3).
        if "command_records" not in proposal:
            reasons.append("missing command_records")
        for rec in _as_list(proposal.get("command_records")):
            if not isinstance(rec, dict):
                reasons.append("command record is not a dict")
                continue
            if not rec.get("cmd"):
                reasons.append("command record missing cmd")
            # type() is int (NOT isinstance) so a bool exit_code is rejected —
            # isinstance(True, int) is True (sol-11).
            if type(rec.get("exit_code")) is not int:
                reasons.append("command record missing/invalid exit_code")
            self._require_resolves(run_dir, rec.get("log_handle"), reasons,
                                   "command record log_handle")

        # 3. Candidate failures carry a valid FailureClass + a locator.
        if not proposal.get("candidate_failures"):
            reasons.append("missing candidate_failures")
        for cand in _as_list(proposal.get("candidate_failures")):
            if not isinstance(cand, dict):
                reasons.append("candidate failure is not a dict")
                continue
            if cand.get("failure_class") not in _VALID_FAILURE_CLASSES:
                reasons.append(f"invalid failure_class: {cand.get('failure_class')!r}")
            if not cand.get("locator"):
                reasons.append("candidate failure missing locator")

        # 4. Children trace to the parent.
        for child in _as_list(proposal.get("children")):
            if not isinstance(child, dict):
                reasons.append("child is not a dict")
                continue
            if child.get("parent_id") != parent_id:
                reasons.append(
                    f"child {child.get('id')!r} does not trace to parent {parent_id!r}"
                )

        # 5. Coverage map + residue present.
        if "coverage_map" not in proposal:
            reasons.append("missing coverage_map")
        if "residue" not in proposal:
            reasons.append("missing residue")

        passed = not reasons

        # Record the reasons as an admissibility artifact (auditable), but NEVER
        # any exit_codes claiming a command ran — this receipt cannot attest
        # execution by construction (empty exit_codes, ADMISSIBILITY strength).
        residual = [{"admissibility_reason": r} for r in reasons]

        return Receipt(
            node_id=getattr(node, "id", "") if node is not None else "",
            validator_id=self.id,
            validator_version=self.version,
            strength=self.strength,
            ran=True,
            passed=passed,
            workspace_id=f"run:{run_dir.run_id}",  # audit identity (no state attested)
            commands=[],       # admissibility runs no commands
            exit_codes=[],     # and therefore attests NO execution (invariant 3)
            artifact_hashes={},
            evidence=[{"schema_version": ENGINE_SCHEMA_VERSION,
                       "checked": "admissibility"}],
            residual=residual,
            ts=_now_iso(),
        )

    @staticmethod
    def _require_resolves(run_dir: RunDir, handle_str, reasons: List[str], label: str) -> None:
        if not handle_str:
            reasons.append(f"{label} missing")
            return
        if not isinstance(handle_str, str):
            reasons.append(f"{label} is not a string handle")
            return
        try:
            run_dir.resolve_handle(ArtifactHandle.from_str(handle_str))
        except (ValueError, KeyError):
            reasons.append(f"{label} does not resolve: {handle_str!r}")


def _as_list(value) -> list:
    """Coerce a proposal field to a list; a non-list becomes empty (fail closed)."""
    return value if isinstance(value, list) else []
