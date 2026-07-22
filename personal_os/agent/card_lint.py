"""Card lint — health guard for the vault card store (personal-os).

Two invisible-failure classes bit us during v0 and this catches both:

  1. YAML-unsafe frontmatter → Obsidian Bases SILENTLY drops the card from the
     board (no error, the card just vanishes). We re-parse every card's
     frontmatter with a strict YAML load and flag any that would be dropped.

  2. status/folder drift → a card whose `status` field disagrees with the
     column folder it physically lives in renders in the "wrong" board column
     (board groups by the `status` field, humans move files by folder). This is
     mechanical and safe to auto-fix (folder is the human's intent; align the
     field to it) — but only under --fix.

Design: read-only by default (report + non-zero exit if issues). `--fix`
performs only the SAFE remediation (status←folder); it never touches YAML it
can't confidently repair — those are reported for a human.

Usage:
  python -m personal_os.agent.card_lint          # report only, exit 1 if issues
  python -m personal_os.agent.card_lint --fix    # also align status→folder
  python -m personal_os.agent.card_lint --quiet  # print only on problems (cron)
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

from ..poller.config import load_config, vault_state_dir
from ..contract.card_schema import from_markdown, to_markdown, VALID_STATUS

# Columns whose folder name is a valid lifecycle status (drift is checkable).
_STATUS_COLUMNS = {"inbox", "queued", "working", "review", "done"}


def _cards_root(state_dir: str) -> str:
    return os.path.join(os.path.dirname(state_dir), "cards")


def _strict_yaml_ok(frontmatter: str):
    """Return (ok, error_str). Prefer PyYAML (matches Bases' strict parser);
    fall back to our own parser's round-trip if PyYAML isn't installed."""
    try:
        import yaml  # noqa
        try:
            yaml.safe_load(frontmatter)
            return True, ""
        except Exception as e:  # pragma: no cover - message varies
            return False, str(e).splitlines()[0][:120]
    except ImportError:
        # Fallback: our from_markdown is lenient, so approximate the check by
        # scanning for the two failure shapes we know Bases rejects.
        for ln in frontmatter.splitlines():
            s = ln.strip()
            if not s:
                continue
            if s.startswith("- "):
                return False, f"list item in block mapping: {s[:40]}"
        return True, ""


def lint(cards_root: str, fix: bool = False) -> dict:
    """Scan every card. Returns a report dict; applies safe status←folder fixes
    when fix=True."""
    yaml_bad, drift, fixed, unreadable = [], [], [], []

    for col in sorted(_STATUS_COLUMNS):
        for path in sorted(glob.glob(os.path.join(cards_root, col, "*.md"))):
            name = os.path.relpath(path, cards_root)
            raw = open(path, encoding="utf-8").read()

            # (1) strict-YAML check on the frontmatter block
            fm = raw.split("---", 2)[1] if raw.startswith("---") else ""
            ok, err = _strict_yaml_ok(fm)
            if not ok:
                yaml_bad.append((name, err))

            # (2) status/folder drift
            try:
                card, body = from_markdown(raw)
            except Exception as e:
                unreadable.append((name, str(e)[:80]))
                continue
            status = card.get("status")
            if status in VALID_STATUS and status != col:
                drift.append((name, status, col))
                if fix:
                    card["status"] = col           # folder = human intent
                    open(path, "w", encoding="utf-8").write(to_markdown(card, body))
                    fixed.append((name, status, col))

    return {
        "yaml_bad": yaml_bad,
        "drift": drift,
        "fixed": fixed,
        "unreadable": unreadable,
        "ok": not (yaml_bad or drift or unreadable),
    }


def format_report(r: dict) -> str:
    lines = []
    if r["ok"]:
        return "✅ card lint: all cards valid, no status/folder drift."
    if r["yaml_bad"]:
        lines.append(f"❌ YAML-unsafe frontmatter ({len(r['yaml_bad'])}) — these VANISH from the board:")
        for name, err in r["yaml_bad"]:
            lines.append(f"   • {name} — {err}")
    if r["unreadable"]:
        lines.append(f"❌ unreadable cards ({len(r['unreadable'])}):")
        for name, err in r["unreadable"]:
            lines.append(f"   • {name} — {err}")
    if r["fixed"]:
        lines.append(f"🔧 status→folder aligned ({len(r['fixed'])}):")
        for name, was, now in r["fixed"]:
            lines.append(f"   • {name} — status {was} → {now}")
    elif r["drift"]:
        lines.append(f"⚠️  status/folder drift ({len(r['drift'])}) — run with --fix:")
        for name, status, col in r["drift"]:
            lines.append(f"   • {name} — status={status} but in {col}/")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lint personal-os cards (YAML safety + status/folder drift)")
    ap.add_argument("--fix", action="store_true", help="align status field to folder (safe auto-fix)")
    ap.add_argument("--quiet", action="store_true", help="print only when there are problems (cron)")
    args = ap.parse_args(argv)

    load_config()  # validates env; raises on misconfig
    cards_root = _cards_root(vault_state_dir())
    r = lint(cards_root, fix=args.fix)

    # YAML problems always remain a failure even after --fix (we don't auto-edit YAML).
    hard_fail = bool(r["yaml_bad"] or r["unreadable"])
    residual_drift = bool(r["drift"]) and not args.fix

    if not args.quiet or hard_fail or residual_drift or r["fixed"]:
        print(format_report(r))
    return 1 if (hard_fail or residual_drift) else 0


if __name__ == "__main__":
    sys.exit(main())
