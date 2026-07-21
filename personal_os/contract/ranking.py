"""Deterministic ranking (T10 / Q7). NO LLM in the sort.

The LLM (stage-2) only *sets* the fields on each card; ordering is a pure
function so it is testable and reproducible. Sort key, in priority order:

  1. consequence_tier   (T3 > T2 > T1)
  2. deadline           (soonest first; None sorts last)
  3. hierarchy rank     (family > health > home > money > work > projects, per config)
  4. malcolm conjunction: identity ALONE is a weak tiebreak (so an optional RSVP
     can't outrank a past-due bill); identity AND a real consequence signal
     (tier >= T2) is applied upstream by the LLM as a tier jump, not here.

Returns a NEW ordered list; does not mutate input.
"""

from __future__ import annotations

_TIER_ORDER = {"T3": 0, "T2": 1, "T1": 2}
_DEFAULT_HIERARCHY = ["family", "health", "home", "money", "work", "projects"]


def _hierarchy_rank(card: dict, order: list[str]) -> int:
    h = card.get("priority_hierarchy", "projects")
    return order.index(h) if h in order else len(order)


def rank_cards(cards: list[dict], config: dict | None = None) -> list[dict]:
    config = config or {}
    order = (config.get("priority", {}) or {}).get("hierarchy_order", _DEFAULT_HIERARCHY)

    def key(card: dict):
        tier = _TIER_ORDER.get(card.get("consequence_tier", "T1"), 2)
        deadline = card.get("deadline")
        # None deadline sorts after any real deadline
        deadline_key = (1, "") if deadline is None else (0, deadline)
        hier = _hierarchy_rank(card, order)
        # weak tiebreak: a malcolm card edges ahead only among otherwise-equal cards
        malcolm = 0 if card.get("malcolm_flag") else 1
        return (tier, deadline_key, hier, malcolm)

    return sorted(cards, key=key)
