"""Stage-2 deterministic mint helper (Q6 durable-fix).

The LLM agent supplies ONLY its classification JUDGMENT per survivor (actionable?
tier/sensitivity/hierarchy/deadline/malcolm). This script does everything
mechanical and error-prone: two-layer dedup, card enrichment, contract
validation, markdown minting, trace-logging non-actionables, and consuming the
handoff file. Keeps the fragile parts out of free-form agent code.

Usage (agent calls this):
  python -m personal_os.agent.mint_cards --handoff <path> --decisions <decisions.json>

decisions.json = {
  "<source_ref>": {
      "actionable": true,
      "consequence_tier": "T2", "sensitivity_class": "normal",
      "priority_hierarchy": "money", "deadline": "2026-07-25",
      "malcolm_flag": false, "done_contract": "notified",
      "why": "short reason surfaced in the card body"
  },
  "<source_ref2>": {"actionable": false, "reason": "automated FYI"}
}

Prints a JSON receipt: {minted, deduped, not_actionable, cards: [paths]}.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import sys

from ..poller.config import load_config, vault_state_dir
from ..contract.card_schema import (
    new_card, validate_card, to_markdown, from_markdown, build_title, gmail_link,
    VALID_TIER, VALID_SENSITIVITY, VALID_HIERARCHY, VALID_STOP,
)

_VALID_FLAGS = {"needs-review", "blocked", "needs-input"}


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cards_root(state_dir: str) -> str:
    return os.path.join(os.path.dirname(state_dir), "cards")


def _load_existing_keys(cards_root: str):
    """Return (set of source_ref, set of source_key) across all OPEN card columns."""
    refs, keys = set(), set()
    for col in ("inbox", "queued", "working", "review"):
        for path in glob.glob(os.path.join(cards_root, col, "*.md")):
            try:
                card, _ = from_markdown(open(path, encoding="utf-8").read())
                refs.add(card.get("source_ref"))
                keys.add(card.get("source_key"))
            except Exception:
                continue
    return refs, keys


def _cap_tier(t: str) -> str:
    # v0: action tier caps at T2; T3 is allowed as a LABEL (surfaces, never actioned)
    return t if t in VALID_TIER else "T1"


def run(handoff_path: str, decisions: dict, env: dict | None = None) -> dict:
    load_config(env)  # validates secret/env presence; raises on misconfig
    state_dir = vault_state_dir(env)
    cards_root = _cards_root(state_dir)
    inbox_dir = os.path.join(cards_root, "inbox")
    os.makedirs(inbox_dir, exist_ok=True)
    trace_path = os.path.join(state_dir, "traces", f"{_utc_now_iso()[:10]}.jsonl")

    existing_refs, existing_keys = _load_existing_keys(cards_root)

    minted, deduped, not_actionable = [], 0, 0
    ts = _utc_now_iso()

    with open(handoff_path, encoding="utf-8") as fh:
        lines = [json.loads(l) for l in fh if l.strip()]

    for rec in lines:
        stub = rec["card_stub"]
        meta = rec["meta"]
        ref = stub["source_ref"]
        key = stub["source_key"]
        decision = decisions.get(ref) or decisions.get(key) or {}

        # dedup (T6 two-layer)
        if ref in existing_refs or key in existing_keys:
            deduped += 1
            continue

        if not decision.get("actionable"):
            _append_trace(trace_path, {"ts": ts, "source_ref": ref, "verdict": "not-actionable",
                                       "reason": decision.get("reason", "unclassified"),
                                       "subject": meta.get("subject")})
            not_actionable += 1
            continue

        # enrich stub with the LLM's judgment (validated)
        stub["consequence_tier"] = _cap_tier(decision.get("consequence_tier", "T1"))
        stub["sensitivity_class"] = decision.get("sensitivity_class", "normal") \
            if decision.get("sensitivity_class") in VALID_SENSITIVITY else "normal"
        stub["priority_hierarchy"] = decision.get("priority_hierarchy", "projects") \
            if decision.get("priority_hierarchy") in VALID_HIERARCHY else "projects"
        stub["deadline"] = decision.get("deadline")
        stub["malcolm_flag"] = bool(decision.get("malcolm_flag", False))
        stub["done_contract"] = decision.get("done_contract", "notified") \
            if decision.get("done_contract") in VALID_STOP else "notified"
        flags = decision.get("flags", [])
        stub["flags"] = [flag for flag in flags if flag in _VALID_FLAGS] \
            if isinstance(flags, list) else []

        validate_card(stub)  # hard contract gate (incl. surface-only floor)

        stub["title"] = build_title(meta.get("subject"), meta.get("from"))

        gl = gmail_link(ref)
        open_line = f"\n**[📧 Open in Gmail]({gl})**\n" if gl else ""
        body = (
            f"**From:** {meta.get('from','')}\n"
            f"**Subject:** {meta.get('subject','')}\n"
            f"**Date:** {meta.get('date','')}\n"
            f"{open_line}\n"
            f"> {(''.join(meta.get('snippet','').splitlines()[:6]))[:500]}\n\n"
            f"_Why surfaced:_ {decision.get('why','actionable email')}\n"
        )
        card_path = os.path.join(inbox_dir, f"{stub['card_id']}.md")
        with open(card_path, "w", encoding="utf-8") as out:
            out.write(to_markdown(stub, body))
        minted.append(card_path)
        existing_refs.add(ref)
        existing_keys.add(key)

    # consume the handoff (processed)
    try:
        os.remove(handoff_path)
    except OSError:
        pass

    return {"minted": len(minted), "deduped": deduped,
            "not_actionable": not_actionable, "cards": minted}


def _append_trace(path: str, rec: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="stage-2 deterministic card minter")
    ap.add_argument("--handoff", required=True)
    ap.add_argument("--decisions", required=True, help="path to decisions JSON")
    args = ap.parse_args(argv)
    decisions = json.load(open(args.decisions, encoding="utf-8"))
    receipt = run(args.handoff, decisions)
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
