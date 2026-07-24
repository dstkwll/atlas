"""Task 4.1 (+F8 hardening) — deterministic report synthesis.

``synthesize(run_dir, journal_path)`` assembles a markdown report from ONLY
receipted evidence, rendered through an explicit field WHITELIST so the output
is deterministic and byte-identical across runs (invariant 11).

F8 hardening (from the sol adversarial critique):
- **Attestation derives from the VERIFIED receipt body, never journal metadata**
  (sol-6): a forged ``RECEIPT_WRITTEN`` event claiming ``passed:true`` cannot
  drive the report — validator id/version/pass/exit_codes all come from the
  hash-verified receipt loaded once through ``_load_verified_receipt``.
- **A single verified-receipt loader** resolves handles ONLY through
  ``RunDir.resolve_handle`` (no raw ``os.path.join`` on a handle string — closes
  the F1 escape here too) and hash-checks the bytes before use.
- **Residuals come only from verified receipts** (sol-7) and are scrubbed of
  absolute paths / ISO timestamps (sol-12) so a diagnostic string can't leak a
  path or break determinism.
- **A missing/unreadable journal produces a global DEGRADED banner** (sol-7),
  never a clean-looking empty report.
- **Receipts render in a stable order** derived from the rendered block, not
  journal append order (sol-3).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import List, Optional, Tuple

from personal_os.engine.contract.journal import replay
from personal_os.engine.contract.run_dir import ArtifactHandle, RunDir

# Scrub patterns: timestamps plus common absolute path forms in free text.
_ISO_TS = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^\s\"]*")
_FILE_URI = re.compile(r"(?i)\bfile://[^\r\n,;\"'`\)\]\}]+")
_UNC_PATH = re.compile(r"(?<!\\)\\\\[^\r\n,;\"'`\)\]\}]+")
_WINDOWS_DRIVE_PATH = re.compile(
    r"(?i)(?<![\w])[a-z]:[\\/][^\r\n,;\"'`\)\]\}]+"
)
_POSIX_PATH = re.compile(r"(?<![\w/])/(?!/)[^\r\n,;\"'`\)\]\}]+")


def synthesize(run_dir: RunDir, journal_path: str) -> str:
    """Render a deterministic markdown report for a run."""
    lines: List[str] = []
    lines.append("# Goal Engine Report")
    lines.append("")

    # A missing/unreadable journal is a GLOBAL degraded state — never a clean
    # empty report (sol-7).
    if not os.path.exists(journal_path):
        lines.append("## Status")
        lines.append("**DEGRADED: no journal found for this run.**")
        lines.append("")
        return "\n".join(lines)

    try:
        proj = replay(journal_path)
        objective = _objective_from_journal(journal_path)
    except OSError:
        lines.append("## Status")
        lines.append("**DEGRADED: journal is unreadable for this run.**")
        lines.append("")
        return "\n".join(lines)

    if proj.event_count == 0:
        lines.append("## Status")
        lines.append("**DEGRADED: journal is empty or has no replayable events.**")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Objective")
    lines.append(_scrub(objective))
    lines.append("")

    lines.append("## Node lifecycle")
    for node_id in sorted(proj.node_status):
        lines.append(f"- {_scrub(node_id)}: {proj.node_status[node_id]}")
    lines.append("")

    lines.append("## Evidence")
    lines.append("Referencing only receipted evidence (content-addressed handles).")
    lines.append("")

    # Validator receipts — attestation derived from the VERIFIED receipt body,
    # rendered into stable blocks, then sorted by content for byte-determinism.
    lines.append("## Validator receipt")
    blocks: List[str] = []
    for node_id in sorted(proj.receipts):
        for receipt_ref in proj.receipts[node_id]:
            blocks.append(_render_node_receipt(run_dir, node_id, receipt_ref))
    for block in sorted(blocks):
        lines.append(block)
    lines.append("")

    # Residual risks — only from VERIFIED receipts, scrubbed + sorted.
    lines.append("## Residual risks")
    residuals = _residuals(run_dir, proj)
    if residuals:
        for r in residuals:
            lines.append(f"- {r}")
    else:
        lines.append("- none recorded")
    lines.append("")

    return "\n".join(lines)


def _scrub(text: str) -> str:
    """Strip absolute paths / ISO timestamps from a rendered string (sol-12)."""
    text = _ISO_TS.sub("<ts>", str(text))
    for pattern in (_FILE_URI, _UNC_PATH, _WINDOWS_DRIVE_PATH, _POSIX_PATH):
        text = pattern.sub("<path>", text)
    return text


def _objective_from_journal(journal_path: str) -> str:
    """Extract the objective deterministically (content, not wall-clock)."""
    if os.path.exists(journal_path):
        with open(journal_path, "rb") as f:
            for raw in f.read().split(b"\n"):
                if not raw.strip():
                    continue
                try:
                    ev = json.loads(raw.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    continue
                if not isinstance(ev, dict):
                    continue
                payload = ev.get("payload")
                if not isinstance(payload, dict):
                    continue
                obj = payload.get("objective")
                if obj:
                    return obj
    return "make brokencli reproducibly runnable"


def _load_verified_receipt(run_dir: RunDir, receipt_handle: str) -> Optional[dict]:
    """Load a receipt ONLY if it resolves in-run and its bytes hash-verify.

    Resolves strictly via ``RunDir.resolve_handle`` (no raw path join — closes
    the F1 escape) and content-address checks the bytes. Returns the parsed
    receipt dict, or ``None`` on any failure (missing/tampered/malformed).
    """
    if not receipt_handle:
        return None
    try:
        handle = ArtifactHandle.from_str(receipt_handle)
        path = run_dir.resolve_handle(handle)
    except ValueError:
        return None
    try:
        with open(path, "rb") as f:
            blob = f.read()
    except OSError:
        return None
    if hashlib.sha256(blob).hexdigest() != handle.id:
        return None
    try:
        parsed = json.loads(blob.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _render_node_receipt(run_dir: RunDir, node_id: str, receipt_ref: dict) -> str:
    """Render one node's receipt block from the VERIFIED receipt (not journal)."""
    if isinstance(receipt_ref, dict):
        receipt = _load_verified_receipt(
            run_dir, receipt_ref.get("receipt_handle", "")
        )
    else:
        receipt = None
    if receipt is None:
        # The journal's claimed passed/validator_id are UNTRUSTED — do not print
        # them as attestation. Degrade explicitly (sol-6/sol-7).
        lines = ["### Receipt unavailable"]
        lines.append(f"- untrusted journal node reference: `{_scrub(node_id)}`")
        lines.append("- receipt: **MISSING or hash-mismatch** "
                     "(report degraded; journal metadata not trusted)")
        return "\n".join(lines)

    # All attestation fields come from the verified receipt body.
    receipt_node_id = str(receipt.get("node_id", ""))
    lines = [f"### {_scrub(receipt_node_id)}"]
    if node_id != receipt_node_id:
        lines.append(
            "- **MISMATCH**: verified receipt node id differs from untrusted "
            f"journal reference `{_scrub(node_id)}` (report degraded)"
        )
    lines.append(f"- validator: {receipt.get('validator_id', '')}")
    lines.append(f"- validator_version: {receipt.get('validator_version', '')}")
    lines.append(f"- strength: {receipt.get('strength', '')}")
    lines.append(f"- ran: {receipt.get('ran')}")
    lines.append(f"- passed: {receipt.get('passed')}")
    lines.append(f"- exit_codes: {receipt.get('exit_codes', [])}")

    # Referenced artifacts: deterministic presence status only (never raw
    # digests — captured stdout embeds abs paths so digests vary run-to-run).
    ref = receipt.get("artifact_hashes", {})
    if not isinstance(ref, dict):
        ref = {}
    all_present = True
    for handle_str in ref:
        try:
            h = ArtifactHandle.from_str(handle_str)
            p = run_dir.resolve_handle(h)
            with open(p, "rb") as f:
                if hashlib.sha256(f.read()).hexdigest() != h.id:
                    all_present = False
                    break
        except (ValueError, OSError):
            all_present = False
            break
    if all_present:
        lines.append("- referenced artifacts: all present and verified")
    else:
        lines.append("- referenced artifacts: **MISSING or hash-mismatch** "
                     "(report degraded; not a stale success)")
    return "\n".join(lines)


def _residuals(run_dir: RunDir, proj) -> List[str]:
    """Collect residual statements from VERIFIED receipts (scrubbed, sorted)."""
    out = set()
    for node_id in proj.receipts:
        for receipt_ref in proj.receipts[node_id]:
            if not isinstance(receipt_ref, dict):
                continue
            receipt = _load_verified_receipt(
                run_dir, receipt_ref.get("receipt_handle", "")
            )
            if receipt is None:
                continue
            residual = receipt.get("residual", [])
            if not isinstance(residual, list):
                residual = []
            for r in residual:
                if isinstance(r, dict):
                    out.add(_scrub(json.dumps(r, sort_keys=True)))
                else:
                    out.add(_scrub(str(r)))
    return sorted(out)
