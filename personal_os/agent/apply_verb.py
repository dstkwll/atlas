"""Deterministic reply-verb applier (Q7 interactive path).

The interactive agent parses Dan's free-text reply into a structured verb, then
calls THIS script to mutate card state. All email-untouching, all deterministic:
the agent supplies intent, the script owns the state machine.

Verbs (state-only — NEVER touches Gmail):
  done         -> archive card off-board (move to cards/done/), lifecycle ends.
  snooze WHEN  -> set snooze_until, move to queued; the digest reactivates on due.
  dismiss      -> drop as not-actionable-after-all (move to cards/done/, mark dismissed).
  ack          -> acknowledge: reset the nag counter for one cycle, keep in place.

Resolution: a target is either an integer (looked up in the latest digest
manifest -> card_id) or a card_id string directly.

Usage:
  python -m personal_os.agent.apply_verb --verb done --target 2
  python -m personal_os.agent.apply_verb --verb snooze --target 3 --when 2026-07-25T08:00:00Z
Prints a JSON receipt: {ok, verb, card_id, subject, message}.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os

from ..poller.config import load_config, vault_state_dir
from ..contract.card_schema import from_markdown, to_markdown

_LIVE_COLUMNS = ("inbox", "queued", "working", "review")
VALID_VERBS = {"done", "snooze", "dismiss", "ack"}


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _iso(dt: _dt.datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _cards_root(state_dir: str) -> str:
    return os.path.join(os.path.dirname(state_dir), "cards")


def _snapshot_path(state_dir: str, digest_id: str) -> str:
    return os.path.join(state_dir, "digests", f"{digest_id}.json")


def resolve_target(target: str, state_dir: str, digest_id: str | None = None) -> str:
    """Return a card_id.
    A positional NUMBER is only meaningful within a specific immutable digest, so a
    numbered target REQUIRES digest_id and resolves against that snapshot only —
    never a mutable 'latest' (sol's staleness invariant). A non-numeric target is
    assumed to already be a card_id.
    """
    target = str(target).strip()
    if not target.isdigit():
        return target  # already a card_id
    if not digest_id:
        raise ValueError("a numbered target requires --digest-id (which digest are you replying to?)")
    path = _snapshot_path(state_dir, digest_id)
    if not os.path.exists(path):
        raise ValueError(f"digest {digest_id} not found; cannot resolve number {target}")
    manifest = json.load(open(path, encoding="utf-8"))
    for row in manifest.get("items", []):
        if int(row["n"]) == int(target):
            return row["card_id"]
    raise ValueError(f"number {target} not in digest {digest_id}")


def _find_card(card_id: str, cards_root: str):
    """Return (path, card, body, column) for a card_id across live columns, or None."""
    for col in _LIVE_COLUMNS:
        for path in glob.glob(os.path.join(cards_root, col, "*.md")):
            try:
                card, body = from_markdown(open(path, encoding="utf-8").read())
            except Exception:
                continue
            if card.get("card_id") == card_id:
                return path, card, body, col
    return None


def _move_card(path: str, card: dict, body: str, dest_col: str, cards_root: str,
               now: _dt.datetime) -> str:
    card["status"] = dest_col
    card["entered_state_at"] = _iso(now)
    dest_dir = os.path.join(cards_root, dest_col)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(path))
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(to_markdown(card, body))
    if os.path.abspath(dest) != os.path.abspath(path):
        os.remove(path)
    return dest


def apply_verb(verb: str, target: str, when: str | None = None, env: dict | None = None,
               digest_id: str | None = None) -> dict:
    if verb not in VALID_VERBS:
        return {"ok": False, "message": f"unknown verb: {verb}"}
    load_config(env)
    state_dir = vault_state_dir(env)
    cards_root = _cards_root(state_dir)
    now = _utc_now()

    try:
        card_id = resolve_target(target, state_dir, digest_id)
    except ValueError as e:
        return {"ok": False, "message": str(e)}

    found = _find_card(card_id, cards_root)
    if not found:
        # Idempotent: a card already off-board is a truthful no-op, not an error
        # (sol: done-on-done returns a truthful no-op receipt).
        return {"ok": True, "noop": True, "verb": verb, "card_id": card_id,
                "message": f"↩️ Already handled — “{card_id}” is no longer on the board."}
    path, card, body, col = found
    subject = _subject_of(card, body)
    msg = ""

    if verb == "done":
        _move_card(path, card, body, "done", cards_root, now)
        msg = f"✅ Done — archived “{subject}”."
    elif verb == "dismiss":
        card["flags"] = sorted(set((card.get("flags") or []) + []))  # keep flags list valid
        card["dismissed"] = True
        _move_card(path, card, body, "done", cards_root, now)
        msg = f"🗑️ Dismissed “{subject}” (not actionable)."
    elif verb == "snooze":
        if not when:
            return {"ok": False, "message": "snooze needs a --when timestamp (ISO UTC)"}
        card["snooze_until"] = when
        card["surfaced_count"] = 0  # reset nag so it re-surfaces fresh when due
        _move_card(path, card, body, "queued", cards_root, now)
        msg = f"💤 Snoozed “{subject}” until {when}."
    elif verb == "ack":
        card["surfaced_count"] = 0  # one-cycle nag reset, stays in place
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(to_markdown(card, body))
        msg = f"👍 Acknowledged “{subject}” — will hold quietly."

    return {"ok": True, "verb": verb, "card_id": card_id, "subject": subject, "message": msg}


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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="personal-os reply-verb applier")
    ap.add_argument("--verb", required=True, choices=sorted(VALID_VERBS))
    ap.add_argument("--target", required=True, help="digest number or card_id")
    ap.add_argument("--when", help="ISO UTC timestamp for snooze")
    ap.add_argument("--digest-id", dest="digest_id",
                    help="digest the number refers to (required for numbered targets)")
    args = ap.parse_args(argv)
    receipt = apply_verb(args.verb, args.target, when=args.when, digest_id=args.digest_id)
    print(json.dumps(receipt))
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
