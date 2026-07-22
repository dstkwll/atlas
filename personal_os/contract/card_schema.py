"""Canonical personal-comms card contract (Q4).

One card = one markdown note in the vault. Frontmatter = truth; body = email
excerpt + trace. EVERY actor (poller, agent, tests, plugin) binds to THIS
module and never to another actor -- this is the single abstraction boundary
that keeps the decoupled components from drifting.

Stdlib-only (no pyyaml): the poller must stay dependency-free and portable.
"""

from __future__ import annotations

import base64
import os
import time

from .schema_version import SCHEMA_VERSION

# ---- controlled vocabularies -------------------------------------------------
VALID_STATUS = {"inbox", "queued", "working", "review", "done"}
VALID_TIER = {"T1", "T2", "T3"}            # v0: LLM caps at T2; T3 is label/surface-only
VALID_SENSITIVITY = {"normal", "sensitive"}
VALID_AUTONOMY = {"surface-only"}           # v0 HARD FLOOR -- the only permitted value
VALID_HIERARCHY = {"family", "health", "home", "money", "work", "projects"}
VALID_STOP = {"notified", "acknowledged", "externally-confirmed"}

REQUIRED_FIELDS = [
    "schema_version", "card_id", "source_ref", "source_key",
    "status", "flags", "task_type", "consequence_tier", "sensitivity_class",
    "autonomy_mode", "priority_hierarchy", "deadline", "malcolm_flag",
    "surfaced_count", "last_surfaced", "entered_state_at", "done_contract",
    "captured_at",
]

# Scalar fields whose values are written/parsed verbatim in frontmatter.
# (`flags` is the only list field; handled specially.)
_SCALAR_FIELDS = [f for f in REQUIRED_FIELDS if f != "flags"]


def _ulid() -> str:
    """Stdlib-only, lexicographically-sortable id: 6 bytes ms-timestamp + 10 random,
    base32 (Crockford-ish via std base32, padding stripped)."""
    ts = int(time.time() * 1000).to_bytes(6, "big")
    rand = os.urandom(10)
    return base64.b32encode(ts + rand).decode("ascii").rstrip("=")


def build_title(subject: str | None, sender: str | None = None, *, max_len: int = 80) -> str:
    """Human-readable card heading from an email's subject (+ sender fallback).

    Single source of truth for card titles so the board, digest, and mobile
    notifications all read identically. Collapses whitespace, strips common
    reply/forward prefixes, and truncates with an ellipsis. Falls back to a
    cleaned sender, then to "(no subject)" so a card is never title-less.
    """
    import re

    subj = (subject or "").strip()
    subj = re.sub(r"\s+", " ", subj)
    subj = re.sub(r"^(?:(re|fwd|fw)\s*:\s*)+", "", subj, flags=re.IGNORECASE).strip()
    if not subj:
        s = (sender or "").strip()
        # prefer a display name over a bare address: "Name <a@b>" -> "Name"
        m = re.match(r"^\s*\"?([^\"<]+?)\"?\s*<", s)
        subj = (m.group(1).strip() if m else s) or "(no subject)"
    if len(subj) > max_len:
        subj = subj[: max_len - 1].rstrip() + "…"
    return subj


def gmail_link(source_ref: str | None, gm_msgid: str | int | None = None) -> str:
    """Deep link to open the email in Gmail.

    Two tiers, best first:
      1. If `gm_msgid` (Gmail's X-GM-MSGID, a decimal uint64 from IMAP) is
         present, build a true message permalink:
         https://mail.google.com/mail/u/0/#all/<hex>  — opens the exact message
         (not a search). This is the only link that targets a specific message.
      2. Else fall back to the RFC822 Message-ID via Gmail's `rfc822msgid:`
         search operator — resolves to the message on desktop web, but renders
         as a search view.

    Note: Gmail's iOS/Android app universal-link handoff is unreliable and not
    guaranteed by Google; the permalink still opens the right message on web.
    Returns "" when no id is available.
    """
    import urllib.parse

    if gm_msgid not in (None, "", 0, "0"):
        try:
            hexid = format(int(gm_msgid), "x")
            return f"https://mail.google.com/mail/u/0/#all/{hexid}"
        except (ValueError, TypeError):
            pass

    mid = (source_ref or "").strip().strip("<>").strip()
    if not mid:
        return ""
    q = urllib.parse.quote(f"rfc822msgid:{mid}", safe="")
    return f"https://mail.google.com/mail/u/0/#search/{q}"


def gmail_search_link(subject: str | None, sender: str | None = None) -> str:
    """Fallback link: open Gmail with a search for this subject/sender.

    Gmail mobile web won't honor a message-anchor URL (it drops you at the
    inbox), but it DOES honor a #search/ query — so this lands you on a short
    result list containing the email, one tap from the message. Best-effort:
    quotes the subject and adds a from: filter when we can parse an address.
    """
    import re
    import urllib.parse

    terms = []
    subj = re.sub(r"^(?:(re|fwd|fw)\s*:\s*)+", "", (subject or "").strip(), flags=re.IGNORECASE).strip()
    if subj:
        terms.append(f'subject:"{subj}"')
    m = re.search(r"<([^>]+@[^>]+)>", sender or "") or re.search(r"([^\s<]+@[^\s>]+)", sender or "")
    if m:
        terms.append(f"from:{m.group(1)}")
    if not terms:
        return ""
    q = urllib.parse.quote(" ".join(terms), safe="")
    return f"https://mail.google.com/mail/u/0/#search/{q}"


def new_card(*, source_ref: str, source_key: str, captured_at: str) -> dict:
    """Poller mints an INBOX card at capture with T6 @capture defaults.

    The LLM stage-2 enriches the classification/ranking fields later
    (consequence_tier, sensitivity_class, priority_hierarchy, deadline,
    malcolm_flag, done_contract).
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "card_id": _ulid(),
        "title": "",                       # human-readable card heading (subject-derived);
                                           # every surface (board/digest/mobile) titles from this.
                                           # Optional in the contract so pre-title cards still validate.
        "source_ref": source_ref,          # gmail Message-ID -- layer-1 (literal) dedup
        "source_key": source_key,          # hash(sender|norm-subject) -- layer-2 semantic dedup
        "status": "inbox",
        "flags": [],
        "task_type": "comms.email",
        "consequence_tier": "T1",          # LLM may raise to T2; T3 surfaces-only
        "sensitivity_class": "normal",
        "autonomy_mode": "surface-only",
        "priority_hierarchy": "projects",  # LLM overrides
        "deadline": None,
        "malcolm_flag": False,
        "surfaced_count": 0,
        "last_surfaced": None,
        "entered_state_at": captured_at,
        "done_contract": "notified",       # v0 stop_condition floor
        "captured_at": captured_at,
    }


def validate_card(c: dict) -> None:
    """Raise ValueError on any contract violation. Called before mint and after parse."""
    for f in REQUIRED_FIELDS:
        if f not in c:
            raise ValueError(f"card missing required field: {f}")
    if c["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema mismatch: {c['schema_version']} != {SCHEMA_VERSION}")
    if c["status"] not in VALID_STATUS:
        raise ValueError(f"bad status: {c['status']}")
    if c["consequence_tier"] not in VALID_TIER:
        raise ValueError(f"bad consequence_tier: {c['consequence_tier']}")
    if c["sensitivity_class"] not in VALID_SENSITIVITY:
        raise ValueError(f"bad sensitivity_class: {c['sensitivity_class']}")
    if c["autonomy_mode"] not in VALID_AUTONOMY:
        raise ValueError(
            f"autonomy_mode must be surface-only in v0 (zero-send floor): {c['autonomy_mode']}"
        )
    if c["priority_hierarchy"] not in VALID_HIERARCHY:
        raise ValueError(f"bad priority_hierarchy: {c['priority_hierarchy']}")
    if c["done_contract"] not in VALID_STOP:
        raise ValueError(f"bad done_contract: {c['done_contract']}")
    if not isinstance(c["flags"], list):
        raise ValueError("flags must be a list")


# ---- markdown <-> dict serialization (stdlib-only, deterministic) ------------
# A bare YAML scalar is unsafe when it starts with an indicator char or contains
# ": " / " #" etc. We double-quote such strings and escape "\ so Bases' strict
# YAML parser accepts them. Without this, a title like `Malcolm's checkup: 9 AM`
# (colon-space) is invalid YAML and Bases silently drops the whole card.
_YAML_INDICATORS = set("!&*[]{}>|%@`\"'#,?:-")


def _needs_quote(s: str) -> bool:
    if s == "" or s != s.strip():
        return True
    if s[0] in _YAML_INDICATORS:
        return True
    if ": " in s or " #" in s or s.endswith(":"):
        return True
    # values that would otherwise parse as a non-string type must be quoted to
    # stay strings (e.g. a title that is literally "true" or "42")
    if s in ("null", "true", "false", "~") or s.isdigit():
        return True
    return False


def _fmt_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    s = str(v)
    if _needs_quote(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _parse_scalar(s: str):
    s = s.strip()
    if s == "null" or s == "~" or s == "":
        return None
    if s == "true":
        return True
    if s == "false":
        return False
    # double-quoted string: unescape
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    # single-quoted string: YAML unescapes '' -> '
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if s.isdigit():
        return int(s)
    return s


def to_markdown(card: dict, body: str = "") -> str:
    """Render a card as a markdown note with a deterministic (sorted) frontmatter block."""
    validate_card(card)
    # Serialize required fields plus any extra optional scalar fields (e.g.
    # snooze_until) so lifecycle metadata added downstream is not silently lost.
    extra_keys = [k for k in card.keys() if k not in REQUIRED_FIELDS
                  and not isinstance(card[k], (list, dict))]
    lines = ["---"]
    for k in sorted(REQUIRED_FIELDS) + sorted(extra_keys):
        # Defense: never emit a key that isn't a safe bare YAML mapping key
        # (e.g. a corrupted '- needs-review' leaked from a bad flags write would
        # produce an invalid block-mapping line and make Bases drop the card).
        if k != "flags" and (not isinstance(k, str) or _needs_quote(k) or k.startswith("-")):
            continue
        if k == "flags":
            inline = ", ".join(_fmt_scalar(x) for x in card["flags"])
            lines.append(f"flags: [{inline}]")
        else:
            lines.append(f"{k}: {_fmt_scalar(card[k])}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


def from_markdown(text: str):
    """Parse a card note back to (card_dict, body). Inverse of to_markdown for scalars."""
    if not text.startswith("---"):
        raise ValueError("not a frontmatter note")
    parts = text.split("\n")
    if parts[0].strip() != "---":
        raise ValueError("missing opening frontmatter fence")
    # find closing fence
    close = None
    for i in range(1, len(parts)):
        if parts[i].strip() == "---":
            close = i
            break
    if close is None:
        raise ValueError("missing closing frontmatter fence")

    card: dict = {}
    for line in parts[1:close]:
        if not line.strip():
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        if key == "flags":
            inner = raw.strip()
            if inner.startswith("[") and inner.endswith("]"):
                inner = inner[1:-1].strip()
            card["flags"] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
        else:
            card[key] = _parse_scalar(raw)

    # body is everything after the closing fence, with the single leading blank line stripped
    body_lines = parts[close + 1:]
    if body_lines and body_lines[0] == "":
        body_lines = body_lines[1:]
    body = "\n".join(body_lines)
    return card, body
