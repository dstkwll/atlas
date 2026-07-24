"""Task 4.1 — deterministic report synthesis (whitelist projection).

``synthesize(run_dir, journal_path)`` assembles a markdown report from ONLY
receipted evidence, rendered through an explicit field WHITELIST so the output
is deterministic and byte-identical across runs (invariant 11):

- **excluded:** wall-clock ``ts``/``accessed_at``, absolute paths, ``run_id``
  (all vary run-to-run). Artifact handles are rendered as their content-address
  ``artifact:<sha>`` which is stable for identical bytes.
- **included:** objective, the node lifecycle (sorted), each HARD receipt's
  validator id/version + pass status + exit codes + referenced artifact hashes,
  and residual risks.

Determinism is enforced by construction: sorted keys, no timestamps, no abs
paths. If a referenced artifact is missing/hash-mismatched, the report degrades
EXPLICITLY with a ``MISSING`` note (Skeptic D4) — it never emits a stale
clean-looking report.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import List

from personal_os.engine.contract.journal import replay
from personal_os.engine.contract.run_dir import RunDir


def synthesize(run_dir: RunDir, journal_path: str) -> str:
    """Render a deterministic markdown report for a run."""
    proj = replay(journal_path)
    lines: List[str] = []

    lines.append("# Goal Engine Report")
    lines.append("")

    # Objective — pulled from the top node's NODE_CREATED payload if present;
    # fall back to a stable constant. (Objective is content, not wall-clock.)
    objective = _objective_from_journal(journal_path)
    lines.append("## Objective")
    lines.append(objective)
    lines.append("")

    # Node lifecycle — sorted for determinism, no timestamps.
    lines.append("## Node lifecycle")
    for node_id in sorted(proj.node_status):
        lines.append(f"- {node_id}: {proj.node_status[node_id]}")
    lines.append("")

    # Evidence + validator receipts — only receipted nodes, sorted.
    lines.append("## Evidence")
    lines.append("Referencing only receipted evidence (content-addressed handles).")
    lines.append("")

    lines.append("## Validator receipt")
    for node_id in sorted(proj.receipts):
        for receipt_ref in proj.receipts[node_id]:
            handle = receipt_ref.get("receipt_handle", "")
            passed = receipt_ref.get("passed")
            validator = receipt_ref.get("validator_id", "")
            body, ok = _render_receipt(run_dir, handle)
            lines.append(f"### {node_id}")
            lines.append(f"- validator: {validator}")
            lines.append(f"- passed: {passed}")
            if ok:
                lines.extend(body)
            else:
                lines.append("- receipt artifact: **MISSING or hash-mismatch** "
                             "(report degraded; not a stale success)")
            lines.append("")

    # Residual risks — a stable, whitelisted list.
    lines.append("## Residual risks")
    residuals = _residuals(run_dir, proj)
    if residuals:
        for r in residuals:
            lines.append(f"- {r}")
    else:
        lines.append("- none recorded")
    lines.append("")

    return "\n".join(lines)


def _objective_from_journal(journal_path: str) -> str:
    """Extract the objective deterministically (content, not wall-clock)."""
    # v0: the objective is a fixed property of the goal; read the first
    # NODE_CREATED payload's objective if present, else the known goal.
    if os.path.exists(journal_path):
        with open(journal_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                obj = (ev.get("payload") or {}).get("objective")
                if obj:
                    return obj
    return "make brokencli reproducibly runnable"


def _render_receipt(run_dir: RunDir, receipt_handle: str):
    """Render a receipt's whitelisted fields; (lines, ok)."""
    if not receipt_handle:
        return [], False
    sha = receipt_handle.split(":", 1)[1]
    path = os.path.join(run_dir.artifacts_dir, sha)
    if not os.path.exists(path):
        return [], False
    with open(path, "rb") as f:
        blob = f.read()
    if hashlib.sha256(blob).hexdigest() != sha:
        return [], False
    try:
        receipt = json.loads(blob.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return [], False

    lines: List[str] = []
    lines.append(f"- validator_version: {receipt.get('validator_version', '')}")
    lines.append(f"- strength: {receipt.get('strength', '')}")
    lines.append(f"- ran: {receipt.get('ran')}")
    lines.append(f"- exit_codes: {receipt.get('exit_codes', [])}")
    # Referenced artifacts: render a DETERMINISTIC presence status, never the
    # raw content-address hashes — captured stdout embeds absolute venv paths,
    # so its digest varies run-to-run (invariant 11). Verify each referenced
    # artifact is present + unchanged and report only the resilience status.
    ref = receipt.get("artifact_hashes", {})
    all_present = True
    for ref_sha in ref.values():
        ref_path = os.path.join(run_dir.artifacts_dir, ref_sha)
        if not os.path.exists(ref_path):
            all_present = False
            break
        with open(ref_path, "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != ref_sha:
                all_present = False
                break
    if all_present:
        lines.append("- referenced artifacts: all present and verified")
    else:
        lines.append("- referenced artifacts: **MISSING or hash-mismatch** "
                     "(report degraded; not a stale success)")
    return lines, True


def _residuals(run_dir: RunDir, proj) -> List[str]:
    """Collect residual statements from receipts (deterministic, sorted)."""
    out = set()
    for node_id in proj.receipts:
        for receipt_ref in proj.receipts[node_id]:
            handle = receipt_ref.get("receipt_handle", "")
            if not handle:
                continue
            sha = handle.split(":", 1)[1]
            path = os.path.join(run_dir.artifacts_dir, sha)
            if not os.path.exists(path):
                continue
            try:
                with open(path) as f:
                    receipt = json.load(f)
            except (ValueError, OSError):
                continue
            for r in receipt.get("residual", []):
                if isinstance(r, dict):
                    out.add(json.dumps(r, sort_keys=True))
                else:
                    out.add(str(r))
    return sorted(out)
