import json
import os

from personal_os.agent import digest
from personal_os.contract.card_schema import new_card, to_markdown


def _env(tmp_path):
    cfg_dir = tmp_path / "personal-os"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config.json").write_text(json.dumps({
        "surfacing": {"one_nag_cap": 1, "max_age_days_escalate": 3},
        "priority": {"hierarchy_order": ["family", "health", "home", "money", "work", "projects"]},
    }))
    return {"PERSONAL_OS_CONFIG": str(cfg_dir / "config.json"),
            "EMAIL_ADDRESS": "d@e.com", "GOOGLE_APP_PASSWORD": "pw"}


def _put_card(env, col, **over):
    root = os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "cards", col)
    os.makedirs(root, exist_ok=True)
    c = new_card(source_ref=over.get("source_ref", "<x>"),
                 source_key=over.get("source_key", "k"),
                 captured_at="2026-07-21T00:00:00Z")
    c.update({k: v for k, v in over.items() if k in c})
    body = f"**Subject:** {over.get('subject','Test subj')}\n"
    with open(os.path.join(root, f"{c['card_id']}.md"), "w") as fh:
        fh.write(to_markdown(c, body))
    return c


def test_empty_board_all_clear(tmp_path):
    env = _env(tmp_path)
    out = digest.run(env=env)
    assert "All clear" in out


def test_ranked_two_tier_digest(tmp_path):
    env = _env(tmp_path)
    _put_card(env, "inbox", source_ref="<bill>", source_key="k1",
              consequence_tier="T2", priority_hierarchy="money", deadline="2026-07-25",
              subject="Bill due")
    _put_card(env, "inbox", source_ref="<fyi>", source_key="k2",
              consequence_tier="T1", priority_hierarchy="projects", subject="Minor note")
    out = digest.run(env=env)
    assert "NEEDS YOU (2)" in out
    # bill (T2) ranks above the T1 note
    lines = [l for l in out.splitlines() if l.startswith(("1.", "2."))]
    assert "Bill due" in lines[0]
    assert "due 2026-07-25" in lines[0]


def test_needs_review_flag_shown(tmp_path):
    env = _env(tmp_path)
    _put_card(env, "inbox", source_ref="<r>", source_key="k", consequence_tier="T2",
              flags=["needs-review"], subject="Delivery today")
    out = digest.run(env=env)
    assert "review" in out.lower()


def test_surfaced_count_increments(tmp_path):
    env = _env(tmp_path)
    c = _put_card(env, "inbox", source_ref="<s>", source_key="k", subject="x")
    digest.run(env=env)
    # reload card
    from personal_os.contract.card_schema import from_markdown
    root = os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "cards", "inbox")
    card, _ = from_markdown(open(os.path.join(root, f"{c['card_id']}.md")).read())
    assert card["surfaced_count"] == 1
    assert card["last_surfaced"] is not None
