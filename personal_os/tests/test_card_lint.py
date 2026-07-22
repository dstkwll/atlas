"""card_lint: catches the two invisible-failure classes from v0 —
YAML-unsafe frontmatter (Bases silently drops) and status/folder drift."""
import os

from personal_os.agent.card_lint import lint
from personal_os.contract.card_schema import new_card, to_markdown


def _write(cards_root, col, title, status=None):
    d = os.path.join(cards_root, col)
    os.makedirs(d, exist_ok=True)
    c = new_card(source_ref="<x>", source_key="k", captured_at="2026-07-21T00:00:00Z")
    c["status"] = status or col
    c["title"] = title
    p = os.path.join(d, f"{c['card_id']}.md")
    open(p, "w").write(to_markdown(c, "body"))
    return p


def test_clean_cards_pass(tmp_path):
    root = str(tmp_path / "cards")
    _write(root, "inbox", "Reminder: Malcolm's 2-year checkup Thu 9:00 AM")  # tricky but quoted now
    _write(root, "queued", "Yellowstone dates — can you confirm the cabin?")
    r = lint(root)
    assert r["ok"] is True
    assert not r["yaml_bad"] and not r["drift"]


def test_detects_yaml_unsafe_frontmatter(tmp_path):
    root = str(tmp_path / "cards")
    d = os.path.join(root, "inbox")
    os.makedirs(d)
    # hand-write a card with a BARE colon-space title (the pre-fix bug shape)
    bad = (
        "---\n"
        "status: inbox\n"
        "title: Reminder: Malcolm checkup at 9:00 AM\n"   # bare colon-space → invalid YAML
        "task_type: comms.email\n"
        "---\n\nbody\n"
    )
    open(os.path.join(d, "bad.md"), "w").write(bad)
    r = lint(root)
    assert r["ok"] is False
    assert any("bad.md" in name for name, _ in r["yaml_bad"])


def test_detects_and_fixes_status_folder_drift(tmp_path):
    root = str(tmp_path / "cards")
    p = _write(root, "inbox", "Health Beat", status="done")   # field says done, lives in inbox
    r = lint(root, fix=False)
    assert any(status == "done" and col == "inbox" for _n, status, col in r["drift"])

    r2 = lint(root, fix=True)
    assert r2["fixed"]
    from personal_os.contract.card_schema import from_markdown
    c, _ = from_markdown(open(p).read())
    assert c["status"] == "inbox"   # aligned to folder
