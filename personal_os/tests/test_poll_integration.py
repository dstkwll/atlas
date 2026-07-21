"""End-to-end poll tick against a fake IMAP conn + temp vault. No network."""

import json
import os

from personal_os.poller import poll as pollmod
from personal_os.tests.test_imap_client import FakeIMAP, _raw_email


def _env(tmp_path):
    cfg_dir = tmp_path / "personal-os"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config.json").write_text(json.dumps({
        "mailbox": "INBOX",
        "imap_host": "imap.gmail.com",
        "noise_rules": {"sender_patterns": ["no-reply@"], "list_unsubscribe_header": True},
    }))
    return {
        "PERSONAL_OS_CONFIG": str(cfg_dir / "config.json"),
        "EMAIL_ADDRESS": "dan@example.com",
        "GOOGLE_APP_PASSWORD": "pw",
    }


def test_cold_start_baselines_and_emits_nothing(tmp_path):
    env = _env(tmp_path)
    fake = FakeIMAP({}, uidvalidity=111, uidnext=1000)
    summary = pollmod.run(env=env, _conn=fake)
    assert summary["mode"] == "cold-start-baseline"
    assert summary["baseline_uid"] == 999
    assert summary["survivors"] == 0
    # cursor written
    cur = json.load(open(os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "state", "cursor.json")))
    assert cur == {"uidvalidity": 111, "uid": 999}


def test_incremental_sieves_and_writes_handoff_and_traces(tmp_path):
    env = _env(tmp_path)
    state = os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "state")
    os.makedirs(state)
    json.dump({"uidvalidity": 111, "uid": 900}, open(os.path.join(state, "cursor.json"), "w"))

    msgs = {
        950: (_raw_email("no-reply@bank.com", "Statement", "<n@x>"), b"noise"),         # dropped
        960: (_raw_email("aunt@gmail.com", "Malcolm bday party", "<a@x>"), b"come!"),    # survives
        970: (_raw_email("boss@work.com", "Q3 review", "<b@x>"), b"see attached"),       # survives
    }
    fake = FakeIMAP(msgs, uidvalidity=111, uidnext=1000)
    summary = pollmod.run(env=env, _conn=fake)

    assert summary["mode"] == "incremental"
    assert summary["processed"] == 3
    assert summary["survivors"] == 2
    assert summary["cursor_to"] == 970

    # handoff has exactly the 2 survivors
    handoff_dir = os.path.join(state, "handoff")
    hf = os.listdir(handoff_dir)[0]
    lines = open(os.path.join(handoff_dir, hf)).read().strip().split("\n")
    assert len(lines) == 2
    subjects = {json.loads(l)["meta"]["subject"] for l in lines}
    assert subjects == {"Malcolm bday party", "Q3 review"}
    # each carries a valid inbox card stub
    for l in lines:
        stub = json.loads(l)["card_stub"]
        assert stub["status"] == "inbox"
        assert stub["autonomy_mode"] == "surface-only"

    # trace ledger has all 3 with verdicts
    trace_dir = os.path.join(state, "traces")
    tf = os.listdir(trace_dir)[0]
    tlines = [json.loads(l) for l in open(os.path.join(trace_dir, tf)).read().strip().split("\n")]
    assert len(tlines) == 3
    verdicts = {t["subject"]: t["verdict"] for t in tlines}
    assert verdicts["Statement"] == "dropped"
    assert verdicts["Q3 review"] == "survived"

    # cursor advanced
    cur = json.load(open(os.path.join(state, "cursor.json")))
    assert cur["uid"] == 970


def test_uidvalidity_reset_rebaselines(tmp_path):
    env = _env(tmp_path)
    state = os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "state")
    os.makedirs(state)
    json.dump({"uidvalidity": 111, "uid": 900}, open(os.path.join(state, "cursor.json"), "w"))
    fake = FakeIMAP({950: (_raw_email("x@y.com", "hi", "<c@x>"), b"b")},
                    uidvalidity=222, uidnext=1000)  # UIDVALIDITY changed
    summary = pollmod.run(env=env, _conn=fake)
    assert summary["mode"] == "uidvalidity-rebaseline"
    assert summary["survivors"] == 0
    cur = json.load(open(os.path.join(state, "cursor.json")))
    assert cur == {"uidvalidity": 222, "uid": 999}


def test_dry_run_writes_nothing(tmp_path):
    env = _env(tmp_path)
    fake = FakeIMAP({}, uidvalidity=111, uidnext=1000)
    summary = pollmod.run(env=env, dry_run=True, _conn=fake)
    assert summary["dry_run"] is True
    assert not os.path.exists(
        os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "state", "cursor.json")
    )
