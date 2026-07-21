import json
import os

from personal_os.agent import classify
from personal_os.contract.card_schema import from_markdown, new_card


def _env(tmp_path, classify_config=None):
    cfg_dir = tmp_path / "personal-os"
    cfg_dir.mkdir(parents=True)
    config = {"mailbox": "INBOX"}
    if classify_config is not None:
        config["classify"] = classify_config
    (cfg_dir / "config.json").write_text(json.dumps(config))
    return {
        "PERSONAL_OS_CONFIG": str(cfg_dir / "config.json"),
        "EMAIL_ADDRESS": "d@e.com",
        "GOOGLE_APP_PASSWORD": "pw",
    }


def _rec(ref, key, subject, snippet="hello"):
    stub = new_card(
        source_ref=ref, source_key=key, captured_at="2026-07-21T00:00:00Z",
    )
    return {
        "card_stub": stub,
        "meta": {
            "uid": 1, "from": "x@y.com", "subject": subject,
            "date": "2026-07-21", "snippet": snippet,
        },
    }


def _handoff(env, name, records):
    handoff_dir = os.path.join(
        os.path.dirname(env["PERSONAL_OS_CONFIG"]), "state", "handoff",
    )
    os.makedirs(handoff_dir, exist_ok=True)
    path = os.path.join(handoff_dir, name)
    with open(path, "w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record) + "\n")
    return path


def _cards(env):
    inbox = os.path.join(
        os.path.dirname(env["PERSONAL_OS_CONFIG"]), "cards", "inbox",
    )
    if not os.path.isdir(inbox):
        return []
    return [
        from_markdown(open(os.path.join(inbox, name), encoding="utf-8").read())[0]
        for name in os.listdir(inbox)
    ]


def test_atomic_lease_and_mixed_verdicts_mint_correctly(tmp_path, monkeypatch):
    env = _env(tmp_path)
    original = _handoff(env, "batch.jsonl", [
        _rec("<a@x>", "k1", "Please respond"),
        _rec("<b@x>", "k2", "Newsletter"),
        _rec("<c@x>", "k3", "Unclear request"),
    ])
    monkeypatch.setattr(classify, "classify_batch", lambda records, cfg: {
        "<a@x>": {
            "verdict": "actionable", "consequence_tier": "T2",
            "priority_hierarchy": "work", "why": "reply requested",
        },
        "<b@x>": {"verdict": "not_actionable", "reason": "FYI"},
        "<c@x>": {"verdict": "needs_review", "reason": "ambiguous"},
    })
    leased_paths = []
    real_mint = classify.mint_cards.run

    def observe_lease(path, decisions, env=None):
        leased_paths.append(path)
        assert os.path.exists(path)
        return real_mint(path, decisions, env=env)

    monkeypatch.setattr(classify.mint_cards, "run", observe_lease)
    receipt = classify.run(env=env)

    assert not os.path.exists(original)
    assert len(leased_paths) == 1
    assert os.path.basename(os.path.dirname(leased_paths[0])) == "processing"
    assert receipt["minted"] == 2
    assert receipt["not_actionable"] == 1
    assert receipt["needs_review"] == 1
    cards = {card["source_ref"]: card for card in _cards(env)}
    assert cards["<a@x>"]["flags"] == []
    assert cards["<c@x>"]["flags"] == ["needs-review"]


def test_missing_verdict_fails_open_to_needs_review(tmp_path, monkeypatch):
    env = _env(tmp_path)
    _handoff(env, "missing.jsonl", [_rec("<missing@x>", "missing", "A note")])
    monkeypatch.setattr(classify, "classify_batch", lambda records, cfg: {})

    receipt = classify.run(env=env)

    assert receipt["minted"] == 1
    assert receipt["needs_review"] == 1
    assert _cards(env)[0]["flags"] == ["needs-review"]


def test_money_signal_forces_not_actionable_to_needs_review(tmp_path, monkeypatch):
    env = _env(tmp_path)
    _handoff(env, "money.jsonl", [
        _rec("<money@x>", "money", "Payment due tomorrow"),
    ])
    monkeypatch.setattr(classify, "classify_batch", lambda records, cfg: {
        "<money@x>": {"verdict": "not_actionable", "reason": "looks automated"},
    })

    receipt = classify.run(env=env)

    assert receipt["minted"] == 1
    assert receipt["not_actionable"] == 0
    assert receipt["needs_review"] == 1
    assert _cards(env)[0]["flags"] == ["needs-review"]


def test_failed_batch_retries_then_fails_open_without_data_loss(tmp_path, monkeypatch):
    env = _env(tmp_path, {"batch_size": 2})
    _handoff(env, "failure.jsonl", [
        _rec("<one@x>", "one", "First note"),
        _rec("<two@x>", "two", "Second note"),
    ])

    def fail(records, cfg):
        raise TimeoutError("model timed out")

    monkeypatch.setattr(classify, "classify_batch", fail)
    receipt = classify.run(env=env)

    assert receipt["minted"] == 2
    assert receipt["needs_review"] == 2
    assert len(receipt["errors"]) == 3
    assert {card["source_ref"] for card in _cards(env)} == {"<one@x>", "<two@x>"}
    assert all(card["flags"] == ["needs-review"] for card in _cards(env))


def test_main_always_emits_receipt_shape(monkeypatch, capsys):
    expected_keys = {
        "minted", "needs_review", "not_actionable", "deduped",
        "quarantined", "errors",
    }
    monkeypatch.setattr(classify, "run", classify._empty_receipt)

    assert classify.main([]) == 0
    emitted = json.loads(capsys.readouterr().out)
    assert set(emitted) == expected_keys


def test_mint_failure_quarantines_and_continues(tmp_path, monkeypatch):
    env = _env(tmp_path)
    _handoff(env, "bad.jsonl", [_rec("<bad@x>", "bad", "A request")])
    monkeypatch.setattr(classify, "classify_batch", lambda records, cfg: {
        "<bad@x>": {"verdict": "actionable", "why": "reply"},
    })

    def fail_mint(path, decisions, env=None):
        raise ValueError("broken handoff")

    monkeypatch.setattr(classify.mint_cards, "run", fail_mint)
    receipt = classify.run(env=env)

    quarantine = os.path.join(
        os.path.dirname(env["PERSONAL_OS_CONFIG"]),
        "state", "handoff", "quarantine", "bad.jsonl",
    )
    assert receipt["quarantined"] == 1
    assert receipt["minted"] == 0
    assert receipt["errors"]
    assert os.path.exists(quarantine)
