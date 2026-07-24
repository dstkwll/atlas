"""Task 2.5 — refiner core: proposal → admissibility → select → compile child.

``refine`` runs the research track with a fake refiner worker and asserts it
emits a research child + one execution child whose compiled contract
fingerprint == the Phase-1 leaf contract's fingerprint. No LLM.
"""

from __future__ import annotations

from personal_os.engine.contract.enums import NodeStatus, ValidationStrength
from personal_os.engine.contract.journal import EventType, Journal, replay
from personal_os.engine.contract.node import Budget, ProofObligationNode
from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.core.contract_compiler import compile_leaf_contract, fingerprint
from personal_os.engine.core.refine import refine
from personal_os.engine.adapters.fake_worker import FakeRefiner


def _top():
    return ProofObligationNode(
        id="top", parent_id=None, objective="make brokencli reproducibly runnable",
        done_contract={}, admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=2, max_children=4, max_attempts=2),
        status=NodeStatus.PENDING, provenance={},
    )


def test_refine_enforces_max_children(tmp_path):
    # F13/sol-10: a node whose budget allows fewer children than refine would
    # emit must fail closed (no children, not admissible), not overrun.
    rd = new_run(str(tmp_path))
    journal = Journal(rd.events_path, run_id=rd.run_id)
    tight = ProofObligationNode(
        id="top", parent_id=None, objective="make brokencli reproducibly runnable",
        done_contract={}, admissible_evidence=[], validator_ref=None,
        validation_strength=ValidationStrength.HARD,
        budget=Budget(max_depth=2, max_children=1, max_attempts=2),
        status=NodeStatus.PENDING, provenance={},
    )
    result = refine(tight, FakeRefiner(rd), rd, journal)
    assert result.admissible is False
    assert result.children == []


def test_refine_emits_execution_child_matching_phase1_leaf(tmp_path):
    rd = new_run(str(tmp_path))
    journal = Journal(rd.events_path, run_id=rd.run_id)
    result = refine(_top(), FakeRefiner(rd), rd, journal)

    # It produced children and they were journaled.
    assert result.children
    proj = replay(rd.events_path)
    assert any(c.get("id") for c in result.children)

    # Exactly one execution child, and its contract fingerprint equals the
    # canonical Phase-1 leaf contract fingerprint.
    exec_children = [c for c in result.children if c.get("role") == "execution"]
    assert len(exec_children) == 1
    expected = compile_leaf_contract({
        "target": "brokencli/cli.py",
        "objective": "make brokencli reproducibly runnable",
        "install_cmd": "pip install --no-index --no-build-isolation .",
        "run_cmd": "python -m brokencli.cli hello 8",
        "test_cmd": "python -m unittest discover -p test_*.py",
    })
    assert fingerprint(exec_children[0]["contract"]) == fingerprint(expected)


def test_refine_emits_a_research_child(tmp_path):
    rd = new_run(str(tmp_path))
    journal = Journal(rd.events_path, run_id=rd.run_id)
    result = refine(_top(), FakeRefiner(rd), rd, journal)
    assert any(c.get("role") == "research" for c in result.children)


def test_refine_admissibility_gated(tmp_path):
    # If the refiner proposal is inadmissible, refine does NOT emit an execution
    # child (the admissibility gate blocks it).
    rd = new_run(str(tmp_path))
    journal = Journal(rd.events_path, run_id=rd.run_id)
    result = refine(_top(), FakeRefiner(rd, make_inadmissible=True), rd, journal)
    assert result.admissible is False
    exec_children = [c for c in result.children if c.get("role") == "execution"]
    assert not exec_children


def test_refine_journals_children_added(tmp_path):
    rd = new_run(str(tmp_path))
    journal = Journal(rd.events_path, run_id=rd.run_id)
    refine(_top(), FakeRefiner(rd), rd, journal)
    # A CHILDREN_ADDED event exists in the journal.
    import json
    with open(rd.events_path) as f:
        types = [json.loads(line)["type"] for line in f if line.strip()]
    assert "CHILDREN_ADDED" in types


def test_exec_child_target_derived_from_selected_failure(tmp_path):
    # P2 fidelity (sol sequencing): the execution child's contract target must
    # be DERIVED FROM the selected evidenced failure's locator, not lifted from
    # a refiner-preselected block. Make the selected failure point at a distinct
    # locator and assert the compiled contract target follows it.
    rd = new_run(str(tmp_path))
    journal = Journal(rd.events_path, run_id=rd.run_id)
    result = refine(_top(), FakeRefiner(rd, exec_locator="brokencli/cli.py"), rd, journal)
    exec_children = [c for c in result.children if c.get("role") == "execution"]
    assert len(exec_children) == 1
    # The contract target equals the selected failure locator.
    assert exec_children[0]["contract"]["target"] == exec_children[0]["selected_failure"]["locator"]
    assert exec_children[0]["contract"]["target"] == "brokencli/cli.py"
