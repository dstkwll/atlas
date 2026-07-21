import json
import os

import pytest

from personal_os.agent import apply_verb
from personal_os.contract.card_schema import new_card, to_markdown, from_markdown


def _env(tmp_path):
    cfg_dir = tmp_path / "personal-os"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config.json").write_text(json.dumps({"mailbox": "INBOX"}))
    return {"PERSONAL_OS_CONFIG": str(cfg_dir / "config.json"),
            "EMAIL_ADDRESS": "d@e.com", "GOOGLE_APP_PASSWORD": "pw"}


def _state_dir(env):
    return os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "state")


def _cards_root(env):
    return os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "cards")


def _put_card(env, col="inbox", subject="Test subj"):
    root = os.path.join(_cards_root(env), col)
    os.makedirs(root, exist_ok=True)
    c = new_card(source_ref="<x>", source_key="k", captured_at="2026-07-21T00:00:00Z")
    body = f"**Subject:** {subject}\n"
    with open(os.path.join(root, f"{c['card_id']}.md"), "w") as fh:
        fh.write(to_markdown(c, body))
    return c


def _write_manifest(env, rows):
    sd = _state_dir(env)
    os.makedirs(sd, exist_ok=True)
    json.dump({"issued_at": "t", "items": rows},
              open(os.path.join(sd, "digest_manifest.json"), "w"))


def _card_in(env, col, card_id):
    p = os.path.join(_cards_root(env), col, f"{card_id}.md")
    return os.path.exists(p)


def test_done_archives_card(tmp_path):
    env = _env(tmp_path)
    c = _put_card(env, "inbox")
    _write_manifest(env, [{"n": 1, "card_id": c["card_id"], "subject": "Test subj"}])
    r = apply_verb.apply_verb("done", "1", env=env)
    assert r["ok"] and r["verb"] == "done"
    assert not _card_in(env, "inbox", c["card_id"])
    assert _card_in(env, "done", c["card_id"])


def test_resolve_by_card_id_directly(tmp_path):
    env = _env(tmp_path)
    c = _put_card(env, "inbox")
    r = apply_verb.apply_verb("ack", c["card_id"], env=env)
    assert r["ok"] and r["card_id"] == c["card_id"]
    # ack keeps it in place
    assert _card_in(env, "inbox", c["card_id"])


def test_snooze_moves_to_queued_with_timestamp(tmp_path):
    env = _env(tmp_path)
    c = _put_card(env, "inbox")
    _write_manifest(env, [{"n": 1, "card_id": c["card_id"], "subject": "s"}])
    r = apply_verb.apply_verb("snooze", "1", when="2026-07-25T08:00:00Z", env=env)
    assert r["ok"]
    assert _card_in(env, "queued", c["card_id"])
    card, _ = from_markdown(open(os.path.join(_cards_root(env), "queued", f"{c['card_id']}.md")).read())
    assert card["snooze_until"] == "2026-07-25T08:00:00Z"
    assert card["surfaced_count"] == 0


def test_snooze_without_when_fails(tmp_path):
    env = _env(tmp_path)
    c = _put_card(env, "inbox")
    r = apply_verb.apply_verb("snooze", c["card_id"], env=env)
    assert not r["ok"] and "when" in r["message"].lower()


def test_dismiss_archives_and_marks(tmp_path):
    env = _env(tmp_path)
    c = _put_card(env, "inbox")
    r = apply_verb.apply_verb("dismiss", c["card_id"], env=env)
    assert r["ok"]
    assert _card_in(env, "done", c["card_id"])
    card, _ = from_markdown(open(os.path.join(_cards_root(env), "done", f"{c['card_id']}.md")).read())
    assert card.get("dismissed") is True


def test_missing_card_reports_already_handled(tmp_path):
    env = _env(tmp_path)
    _write_manifest(env, [{"n": 1, "card_id": "GONE", "subject": "s"}])
    r = apply_verb.apply_verb("done", "1", env=env)
    assert not r["ok"] and "not found" in r["message"]


def test_bad_number_not_in_manifest(tmp_path):
    env = _env(tmp_path)
    _put_card(env, "inbox")
    _write_manifest(env, [{"n": 1, "card_id": "x", "subject": "s"}])
    r = apply_verb.apply_verb("done", "9", env=env)
    assert not r["ok"]


def test_unknown_verb(tmp_path):
    env = _env(tmp_path)
    r = apply_verb.apply_verb("nuke", "1", env=env)
    assert not r["ok"]
