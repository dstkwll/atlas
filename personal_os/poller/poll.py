"""Stage-1 capture edge entrypoint (Q6). Dumb, stdlib-only, cron-invoked.

Flow each tick:
  load config+secret -> connect IMAP (TLS) -> EXAMINE mailbox (readonly)
  -> cold-start? baseline cursor to UIDNEXT, emit nothing
  -> UIDVALIDITY changed? re-baseline (self-heal), emit nothing
  -> else fetch UID>cursor -> stage-1 sieve (fail-open)
     -> survivors: mint inbox-card stub + snippet -> handoff JSONL
     -> every processed msg (survived|dropped+reason) -> append trace JSONL
  -> advance + save cursor
  -> print one-line receipt to stdout (the cron surface)

The LLM stage-2 (classify/mint-real-cards/rank/digest) is a SEPARATE Hermes
agent that consumes the handoff file. This script never calls an LLM and never
mutates the mailbox.

Usage:
  python -m personal_os.poller.poll            # normal tick
  python -m personal_os.poller.poll --dry-run  # connect+baseline+report, write nothing
"""

from __future__ import annotations

import argparse
import datetime as _dt
import imaplib
import json
import os
import sys

from .config import load_config, vault_state_dir, ConfigError
from .cursor import load_cursor, save_cursor, needs_rebaseline
from .imap_client import fetch_since, get_uidvalidity, get_uidnext
from .sieve import is_noise
from ..contract.card_schema import new_card


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: str, record: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _connect(cfg: dict) -> imaplib.IMAP4_SSL:
    conn = imaplib.IMAP4_SSL(cfg["imap_host"], cfg.get("imap_port", 993))
    conn.login(cfg["_secret"]["address"], cfg["_secret"]["password"])
    return conn


def run(env: dict | None = None, dry_run: bool = False, _conn=None) -> dict:
    """Run one poll tick. Returns a summary dict (also the basis for the stdout receipt).

    `_conn` lets tests inject a fake IMAP connection; production connects via TLS.
    """
    cfg = load_config(env)
    mailbox = cfg.get("mailbox", "INBOX")
    noise_rules = cfg.get("noise_rules", {})
    state_dir = vault_state_dir(env)
    cursor_path = os.path.join(state_dir, "cursor.json")
    ts = _utc_now_iso()

    conn = _conn if _conn is not None else _connect(cfg)
    try:
        live_uidvalidity = get_uidvalidity(conn, mailbox)
        stored = load_cursor(cursor_path)

        # --- cold start: baseline to UIDNEXT, quarantine backlog, emit nothing
        if stored is None:
            uidnext = get_uidnext(conn, mailbox)
            baseline_uid = uidnext - 1
            if not dry_run:
                save_cursor(cursor_path, live_uidvalidity, baseline_uid)
            return {"mode": "cold-start-baseline", "baseline_uid": baseline_uid,
                    "uidvalidity": live_uidvalidity, "survivors": 0, "processed": 0,
                    "dry_run": dry_run, "ts": ts}

        # --- UIDVALIDITY reset: self-heal re-baseline, emit nothing
        if needs_rebaseline(stored, live_uidvalidity):
            uidnext = get_uidnext(conn, mailbox)
            baseline_uid = uidnext - 1
            if not dry_run:
                save_cursor(cursor_path, live_uidvalidity, baseline_uid)
            return {"mode": "uidvalidity-rebaseline", "baseline_uid": baseline_uid,
                    "old_uidvalidity": stored["uidvalidity"], "uidvalidity": live_uidvalidity,
                    "survivors": 0, "processed": 0, "dry_run": dry_run, "ts": ts}

        # --- normal incremental fetch
        after_uid = stored["uid"]
        messages = fetch_since(conn, mailbox, after_uid)
    finally:
        if _conn is None:
            try:
                conn.logout()
            except Exception:
                pass

    handoff_path = os.path.join(state_dir, "handoff", f"{ts.replace(':', '')}.jsonl")
    trace_path = os.path.join(state_dir, "traces", f"{ts[:10]}.jsonl")

    survivors = 0
    max_uid = after_uid
    for m in messages:
        max_uid = max(max_uid, m["uid"])
        drop, reason = is_noise(m, noise_rules)
        trace_rec = {"ts": ts, "uid": m["uid"], "from": m["from"], "subject": m["subject"],
                     "message_id": m["message_id"], "source_key": m["source_key"],
                     "verdict": "dropped" if drop else "survived", "reason": reason}
        if not dry_run:
            _append_jsonl(trace_path, trace_rec)
        if drop:
            continue
        survivors += 1
        stub = new_card(source_ref=m["message_id"], source_key=m["source_key"], captured_at=ts)
        handoff_rec = {"card_stub": stub, "meta": {
            "uid": m["uid"], "from": m["from"], "subject": m["subject"],
            "date": m["date"], "snippet": m["snippet"]}}
        if not dry_run:
            _append_jsonl(handoff_path, handoff_rec)

    if not dry_run and messages:
        save_cursor(cursor_path, live_uidvalidity, max_uid)

    return {"mode": "incremental", "processed": len(messages), "survivors": survivors,
            "cursor_from": after_uid, "cursor_to": max_uid, "uidvalidity": live_uidvalidity,
            "handoff": handoff_path if survivors and not dry_run else None,
            "dry_run": dry_run, "ts": ts}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="personal-os stage-1 email poller")
    parser.add_argument("--dry-run", action="store_true",
                        help="connect, baseline/report only; write nothing")
    args = parser.parse_args(argv)
    try:
        summary = run(dry_run=args.dry_run)
    except ConfigError as e:
        print(f"[poller] CONFIG ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 -- cron needs a clean nonzero, not a traceback dump
        print(f"[poller] ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"[poller] {json.dumps(summary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
