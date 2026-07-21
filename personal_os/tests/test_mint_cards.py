import json
import os

from personal_os.agent import mint_cards
from personal_os.contract.card_schema import new_card, from_markdown


def _env(tmp_path):
    cfg_dir = tmp_path / "personal-os"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config.json").write_text(json.dumps({"mailbox": "INBOX"}))
    return {
        "PERSONAL_OS_CONFIG": str(cfg_dir / "config.json"),
        "EMAIL_ADDRESS": "d@e.com",
        "GOOGLE_APP_PASSWORD": "pw",
    }


def _handoff(tmp_path, env, recs):
    state = os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "state", "handoff")
    os.makedirs(state)
    p = os.path.join(state, "batch.jsonl")
    with open(p, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return p


def _rec(ref, key, subject):
    stub = new_card(source_ref=ref, source_key=key, captured_at="2026-07-21T00:00:00Z")
    return {"card_stub": stub, "meta": {"from": "x@y.com", "subject": subject,
                                        "date": "d", "snippet": "hello"}}


def test_mints_actionable_and_traces_nonactionable(tmp_path):
    env = _env(tmp_path)
    hp = _handoff(tmp_path, env, [
        _rec("<a@x>", "k1", "Bill due"),
        _rec("<b@x>", "k2", "FYI newsletter"),
    ])
    decisions = {
        "<a@x>": {"actionable": True, "consequence_tier": "T2", "priority_hierarchy": "money",
                  "deadline": "2026-07-25", "why": "bill"},
        "<b@x>": {"actionable": False, "reason": "FYI"},
    }
    receipt = mint_cards.run(hp, decisions, env=env)
    assert receipt["minted"] == 1
    assert receipt["not_actionable"] == 1
    # card written + valid + enriched
    card, body = from_markdown(open(receipt["cards"][0]).read())
    assert card["consequence_tier"] == "T2"
    assert card["priority_hierarchy"] == "money"
    assert card["autonomy_mode"] == "surface-only"
    assert "bill" in body
    # handoff consumed
    assert not os.path.exists(hp)


def test_dedup_skips_existing_source_ref(tmp_path):
    env = _env(tmp_path)
    # first batch mints
    hp1 = _handoff(tmp_path, env, [_rec("<a@x>", "k1", "Bill")])
    mint_cards.run(hp1, {"<a@x>": {"actionable": True, "consequence_tier": "T2"}}, env=env)
    # second batch same source_ref -> deduped
    state = os.path.join(os.path.dirname(env["PERSONAL_OS_CONFIG"]), "state", "handoff")
    hp2 = os.path.join(state, "batch2.jsonl")
    open(hp2, "w").write(json.dumps(_rec("<a@x>", "k1", "Bill")) + "\n")
    receipt = mint_cards.run(hp2, {"<a@x>": {"actionable": True, "consequence_tier": "T2"}}, env=env)
    assert receipt["deduped"] == 1
    assert receipt["minted"] == 0


def test_t3_label_allowed_but_capped_semantics(tmp_path):
    env = _env(tmp_path)
    hp = _handoff(tmp_path, env, [_rec("<c@x>", "k3", "Wire transfer")])
    receipt = mint_cards.run(hp, {"<c@x>": {"actionable": True, "consequence_tier": "T3",
                                            "priority_hierarchy": "money"}}, env=env)
    card, _ = from_markdown(open(receipt["cards"][0]).read())
    assert card["consequence_tier"] == "T3"  # label preserved; action-gating enforced elsewhere
    assert card["autonomy_mode"] == "surface-only"
