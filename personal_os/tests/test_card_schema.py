import pytest

from personal_os.contract.card_schema import (
    new_card, validate_card, to_markdown, from_markdown, REQUIRED_FIELDS,
)
from personal_os.contract.schema_version import SCHEMA_VERSION


def _c():
    return new_card(
        source_ref="<msgid@mail.gmail.com>",
        source_key="abc123",
        captured_at="2026-07-21T09:00:00Z",
    )


def test_new_card_has_all_required_fields():
    c = _c()
    for f in REQUIRED_FIELDS:
        assert f in c, f"missing {f}"
    assert c["schema_version"] == SCHEMA_VERSION
    assert c["status"] == "inbox"
    assert c["autonomy_mode"] == "surface-only"   # v0 hard floor
    assert c["surfaced_count"] == 0
    assert c["flags"] == []


def test_validate_rejects_bad_status():
    c = _c()
    c["status"] = "bogus"
    with pytest.raises(ValueError):
        validate_card(c)


def test_validate_rejects_autonomy_escalation():
    c = _c()
    c["autonomy_mode"] = "auto-send"   # must never be allowed in v0
    with pytest.raises(ValueError):
        validate_card(c)


def test_validate_rejects_schema_mismatch():
    c = _c()
    c["schema_version"] = "9.9.9"
    with pytest.raises(ValueError):
        validate_card(c)


def test_markdown_round_trip_scalars():
    c = _c()
    c["consequence_tier"] = "T2"
    c["priority_hierarchy"] = "family"
    c["malcolm_flag"] = True
    c["deadline"] = "2026-07-25"
    c["flags"] = ["blocked", "needs-input"]
    md = to_markdown(c, body="Email excerpt here.\nSecond line.")
    assert md.startswith("---")
    parsed, body = from_markdown(md)
    assert parsed == c
    assert body == "Email excerpt here.\nSecond line."


def test_markdown_round_trip_empty_flags_and_nulls():
    c = _c()
    md = to_markdown(c, body="")
    parsed, body = from_markdown(md)
    assert parsed == c
    assert parsed["deadline"] is None
    assert parsed["flags"] == []
    assert body == ""
