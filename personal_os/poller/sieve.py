"""Stage-1 deterministic noise sieve (pure functions, no I/O).

Block-list driven, FAIL-OPEN (Q4a): only drop on an explicit rule match;
anything unmatched survives to the LLM stage. With a 12.7k-unread backlog the
risk we protect against is *missing* real mail, not seeing junk -- false-junk
gets pruned later by adding a rule (compounding patch-on-discovery from the
trace ledger).
"""

from __future__ import annotations


def is_noise(msg_meta: dict, noise_rules: dict) -> tuple[bool, str]:
    """Return (drop?, reason). Fail-open: returns (False, "") when nothing matches.

    msg_meta expects: {"from": str, "subject": str, "headers": {lowercased: value}}
    noise_rules expects any of:
        sender_patterns: [substr, ...]      matched (ci) against `from`
        subject_patterns: [substr, ...]     matched (ci) against `subject`
        list_unsubscribe_header: bool       drop if a List-Unsubscribe header present
    """
    sender = (msg_meta.get("from") or "").lower()
    subject = (msg_meta.get("subject") or "").lower()
    headers = {k.lower(): v for k, v in (msg_meta.get("headers") or {}).items()}

    for pat in noise_rules.get("sender_patterns", []):
        if pat.lower() in sender:
            return True, f"sender matched noise pattern: {pat}"

    for pat in noise_rules.get("subject_patterns", []):
        if pat.lower() in subject:
            return True, f"subject matched noise pattern: {pat}"

    if noise_rules.get("list_unsubscribe_header") and "list-unsubscribe" in headers:
        return True, "carries list-unsubscribe header"

    return False, ""
