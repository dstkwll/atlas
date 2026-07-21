from personal_os.contract.ranking import rank_cards


def _card(**kw):
    base = {
        "consequence_tier": "T1",
        "deadline": None,
        "priority_hierarchy": "projects",
        "malcolm_flag": False,
    }
    base.update(kw)
    base["card_id"] = kw.get("card_id", str(id(kw)))
    return base


CFG = {"priority": {"hierarchy_order": ["family", "health", "home", "money", "work", "projects"]}}


def test_past_due_bill_outranks_optional_family_rsvp():
    bill = _card(card_id="bill", consequence_tier="T2", deadline="2026-07-20",
                 priority_hierarchy="money")
    rsvp = _card(card_id="rsvp", consequence_tier="T1", priority_hierarchy="family",
                 malcolm_flag=True)  # identity alone -- weak
    out = rank_cards([rsvp, bill], CFG)
    assert [c["card_id"] for c in out] == ["bill", "rsvp"]


def test_higher_tier_wins():
    a = _card(card_id="a", consequence_tier="T1")
    b = _card(card_id="b", consequence_tier="T3")
    out = rank_cards([a, b], CFG)
    assert out[0]["card_id"] == "b"


def test_deadline_breaks_tier_tie():
    a = _card(card_id="a", consequence_tier="T2", deadline="2026-07-25")
    b = _card(card_id="b", consequence_tier="T2", deadline="2026-07-22")
    out = rank_cards([a, b], CFG)
    assert [c["card_id"] for c in out] == ["b", "a"]


def test_none_deadline_sorts_last_within_tier():
    a = _card(card_id="a", consequence_tier="T2", deadline=None)
    b = _card(card_id="b", consequence_tier="T2", deadline="2026-07-22")
    out = rank_cards([a, b], CFG)
    assert [c["card_id"] for c in out] == ["b", "a"]


def test_hierarchy_breaks_tier_and_deadline_tie():
    fam = _card(card_id="fam", consequence_tier="T2", priority_hierarchy="family")
    work = _card(card_id="work", consequence_tier="T2", priority_hierarchy="work")
    out = rank_cards([work, fam], CFG)
    assert [c["card_id"] for c in out] == ["fam", "work"]


def test_malcolm_weak_tiebreak_only_among_equals():
    plain = _card(card_id="plain", consequence_tier="T2", priority_hierarchy="home")
    malc = _card(card_id="malc", consequence_tier="T2", priority_hierarchy="home",
                 malcolm_flag=True)
    out = rank_cards([plain, malc], CFG)
    assert out[0]["card_id"] == "malc"


def test_does_not_mutate_input():
    cards = [_card(card_id="a"), _card(card_id="b")]
    original = list(cards)
    rank_cards(cards, CFG)
    assert cards == original
