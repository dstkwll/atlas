"""Deterministic morning digest (Q7 / #7 shape, sol-recommended fully-deterministic v0).

Reads all open cards from the vault board, re-activates expired snoozes, ranks
deterministically, and prints an action-first two-tier digest. NO LLM: ranked
action lines cannot hallucinate deadlines/inclusion/order. Prose synthesis can
be layered later, validated against this manifest.

Under a no_agent cron job, this script's stdout IS the Discord message.
Respects one_nag_cap + max_age escalation; updates surfaced_count/last_surfaced.
"""

from __future__ import annotations

import datetime as _dt
import glob
import json
import os

from ..poller.config import load_config, vault_state_dir
from ..contract.card_schema import from_markdown, to_markdown, gmail_link
from ..contract.ranking import rank_cards


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _iso(dt: _dt.datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _cards_root(state_dir: str) -> str:
    return os.path.join(os.path.dirname(state_dir), "cards")


def _digests_dir(state_dir: str) -> str:
    return os.path.join(state_dir, "digests")


def _make_digest_id(now: _dt.datetime) -> str:
    """Human-legible, date-scoped, unique: 2026-07-21-HHMMSS."""
    return now.strftime("%Y-%m-%d-%H%M%S")


def _write_manifest(state_dir: str, now: _dt.datetime, digest_id: str, rows: list[dict]) -> None:
    """Persist an IMMUTABLE per-digest manifest keyed by digest_id (sol's staleness fix).

    A positional number is only meaningful WITHIN a specific digest. Replies must
    resolve against the digest they answer, never a mutable 'latest'. We also drop a
    latest.json pointer for display/debug only (NOT authoritative for mutations)."""
    digests_dir = _digests_dir(state_dir)
    os.makedirs(digests_dir, exist_ok=True)
    payload = {"schema": 1, "digest_id": digest_id, "created_at": _iso(now), "items": rows}
    snap = os.path.join(digests_dir, f"{digest_id}.json")
    tmp = snap + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    os.replace(tmp, snap)
    # display-only pointer to the newest digest
    ptr = os.path.join(state_dir, "latest_digest.json")
    tmpp = ptr + ".tmp"
    with open(tmpp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    os.replace(tmpp, ptr)


def _load_column(cards_root: str, col: str) -> list[tuple[str, dict, str]]:
    out = []
    for path in glob.glob(os.path.join(cards_root, col, "*.md")):
        try:
            card, body = from_markdown(open(path, encoding="utf-8").read())
            out.append((path, card, body))
        except Exception:
            continue
    return out


def _short_sender(frm: str) -> str:
    frm = frm or ""
    if "<" in frm:
        frm = frm.split("<")[0].strip().strip('"')
    return (frm or "unknown")[:28]


def _subject_of(card: dict, body: str) -> str:
    """Prefer the card's frontmatter `title` (single source of truth); fall back
    to scanning the body for pre-title cards."""
    t = (card.get("title") or "").strip()
    if t:
        return t[:60]
    for line in body.splitlines():
        if line.startswith("**Subject:**"):
            return line.replace("**Subject:**", "").strip()[:60]
    return "(no subject)"


def _reactivate_snoozes(cards_root: str, now: _dt.datetime) -> int:
    """Move queued cards whose snooze_until has passed back to inbox."""
    moved = 0
    inbox = os.path.join(cards_root, "inbox")
    os.makedirs(inbox, exist_ok=True)
    for path, card, body in _load_column(cards_root, "queued"):
        snooze = card.get("snooze_until")
        if not snooze:
            continue
        try:
            due = _dt.datetime.strptime(snooze, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)
        except Exception:
            continue
        if due <= now:
            card["status"] = "inbox"
            card["entered_state_at"] = _iso(now)
            card.pop("snooze_until", None)
            dest = os.path.join(inbox, os.path.basename(path))
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write(to_markdown(card, body))
            if os.path.abspath(dest) != os.path.abspath(path):
                os.remove(path)
            moved += 1
    return moved


def run(env: dict | None = None) -> str:
    cfg = load_config(env)
    state_dir = vault_state_dir(env)
    cards_root = _cards_root(state_dir)
    now = _utc_now()
    digest_id = _make_digest_id(now)
    one_nag_cap = (cfg.get("surfacing", {}) or {}).get("one_nag_cap", 1)
    max_age_days = (cfg.get("surfacing", {}) or {}).get("max_age_days_escalate", 3)

    _reactivate_snoozes(cards_root, now)

    # actionable = inbox + queued (queued that isn't snoozed into the future)
    entries = _load_column(cards_root, "inbox") + _load_column(cards_root, "queued")
    cards = [c for (_p, c, _b) in entries]
    ranked = rank_cards(cards, cfg)
    by_id = {c["card_id"]: (p, c, b) for (p, c, b) in entries}

    date_str = now.strftime("%a %b %-d")
    if not ranked:
        _write_manifest(state_dir, now, digest_id, [])
        return f"📥 Comms digest — {date_str}\nAll clear — nothing needs you. ✅"

    lines = [f"📥 Comms digest — {date_str}", "", f"NEEDS YOU ({len(ranked)})"]
    manifest_rows = []
    for i, card in enumerate(ranked, 1):
        path, _c, body = by_id[card["card_id"]]
        tier = card.get("consequence_tier", "T1")
        hier = card.get("priority_hierarchy", "projects")
        deadline = card.get("deadline")
        dl = f"·due {deadline}" if deadline else ""
        review = " ⚑review" if "needs-review" in (card.get("flags") or []) else ""
        subject = _subject_of(card, body)
        sender = _short_sender(card.get("_from") or "")
        gl = gmail_link(card.get("source_ref"))
        link = f" · [open](<{gl}>)" if gl else ""
        lines.append(f"{i}. [{tier}·{hier}{dl}]{review} {subject}{link}")
        manifest_rows.append({"n": i, "card_id": card["card_id"], "subject": subject})
        # update surfaced bookkeeping
        card["surfaced_count"] = int(card.get("surfaced_count", 0)) + 1
        card["last_surfaced"] = _iso(now)
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(to_markdown(card, body))
        except Exception:
            pass

    _write_manifest(state_dir, now, digest_id, manifest_rows)
    lines.append("")
    lines.append("Reply: <n> done | <n> snooze <when> | <n> dismiss | <n> ack")
    lines.append(f"Digest: {digest_id}")
    return "\n".join(lines)


def main(argv=None) -> int:
    print(run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
