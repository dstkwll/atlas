"""Card title (human-readable heading) — contract + mint + surface behavior.

Regression guard for the mobile-unusable board bug: cards were titled by their
card_id ULID because no human-readable field existed. Every card must now carry
a subject-derived `title`, and the digest/apply_verb surfaces must prefer it.
"""
from personal_os.contract.card_schema import build_title, gmail_link, new_card, to_markdown, from_markdown


def test_build_title_from_subject():
    assert build_title("Order #6517383 - Delivery scheduled for today") == \
        "Order #6517383 - Delivery scheduled for today"


def test_build_title_strips_reply_prefixes_and_collapses_ws():
    assert build_title("Re:  Fwd: \t Your   receipt") == "Your receipt"


def test_build_title_truncates_long_subjects():
    t = build_title("x" * 200)
    assert len(t) == 80 and t.endswith("…")


def test_build_title_falls_back_to_sender_display_name():
    assert build_title("", '"Furniture Delivery" <DoNotReply@x.com>') == "Furniture Delivery"


def test_build_title_falls_back_to_no_subject():
    assert build_title("", "") == "(no subject)"
    assert build_title(None, None) == "(no subject)"


def test_new_card_has_title_field():
    c = new_card(source_ref="<x>", source_key="k", captured_at="2026-07-21T00:00:00Z")
    assert "title" in c  # present so the board never falls back to the ULID


def test_title_survives_markdown_roundtrip():
    c = new_card(source_ref="<x>", source_key="k", captured_at="2026-07-21T00:00:00Z")
    c["title"] = "Furniture Delivery — Order scheduled"
    parsed, _body = from_markdown(to_markdown(c, "body"))
    assert parsed["title"] == "Furniture Delivery — Order scheduled"


def test_gmail_link_from_message_id():
    url = gmail_link("<d6a0674e-a94c@furnituredelivery.gomwd.com>")
    assert url.startswith("https://mail.google.com/mail/u/0/#search/")
    # angle brackets stripped, rfc822msgid operator url-encoded
    assert "rfc822msgid" in url
    assert "d6a0674e-a94c%40furnituredelivery.gomwd.com" in url


def test_gmail_link_prefers_gm_msgid_permalink():
    # X-GM-MSGID (decimal) → hex permalink to the exact message, not a search
    url = gmail_link("<x@y>", gm_msgid="1770000000000000001")
    assert url == "https://mail.google.com/mail/u/0/#all/" + format(1770000000000000001, "x")
    assert "#all/" in url and "search" not in url


def test_gmail_link_gm_msgid_accepts_int_and_falls_back_on_garbage():
    assert gmail_link("<x@y>", gm_msgid=42) == "https://mail.google.com/mail/u/0/#all/2a"
    # non-numeric gm_msgid → fall back to rfc822msgid search
    assert "#search/" in gmail_link("<x@y>", gm_msgid="not-a-number")


def test_gmail_link_empty_when_no_ref():
    assert gmail_link("") == ""
    assert gmail_link(None) == ""
