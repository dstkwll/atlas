"""Task 2.3 — ADMISSIBILITY validator: well-formedness ONLY (Panel P0-D1).

Checks a research proposal is well-formed + internally consistent (cited source
handles resolve, declared command *records* are schema-valid, candidate
failures follow FailureClass, children trace to parent, coverage+residue
present). It EXPLICITLY does NOT attest that any command executed (invariant 3):
its receipt is ADMISSIBILITY strength, so ``can_discharge_hard`` is False even
when passed.
"""

from __future__ import annotations

from personal_os.engine.contract.enums import ValidationStrength
from personal_os.engine.contract.receipt import can_discharge_hard
from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.validators.admissibility import AdmissibilityValidator


def _wellformed_proposal(rd):
    # A cited source handle that actually resolves in the run.
    src = rd.put_artifact(b"README says: run `brokencli`")
    return {
        "parent_id": "top",
        "citations": [{"claim_id": "c1", "source_handle": src.to_str()}],
        "command_records": [
            {"cmd": "python -m brokencli.cli", "exit_code": 1,
             "log_handle": src.to_str()},
        ],
        "candidate_failures": [
            {"failure_class": "CLEAN_INSTALL_BLOCKER", "locator": "brokencli/cli.py"},
        ],
        "children": [
            {"id": "child-1", "parent_id": "top", "objective": "fix import"},
        ],
        "coverage_map": {"import_bug": "child-1"},
        "residue": ["may be other latent failures"],
        "execution_contract": {
            "objective": "make brokencli reproducibly runnable",
            "install_cmd": "pip install --no-index --no-build-isolation .",
            "run_cmd": "python -m brokencli.cli hello 8",
            "test_cmd": "python -m unittest discover -p test_*.py",
        },
    }


def test_identity_is_admissibility():
    v = AdmissibilityValidator()
    assert v.strength is ValidationStrength.ADMISSIBILITY


def test_wellformed_proposal_passes(tmp_path):
    rd = new_run(str(tmp_path))
    v = AdmissibilityValidator()
    receipt = v.validate(rd, node=None, config={"proposal": _wellformed_proposal(rd)})
    assert receipt.ran is True
    assert receipt.passed is True
    assert receipt.strength is ValidationStrength.ADMISSIBILITY


def test_missing_citation_source_fails(tmp_path):
    rd = new_run(str(tmp_path))
    p = _wellformed_proposal(rd)
    p["citations"][0]["source_handle"] = "artifact:doesnotexist"
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": p})
    assert receipt.passed is False


def test_malformed_command_record_fails(tmp_path):
    rd = new_run(str(tmp_path))
    p = _wellformed_proposal(rd)
    del p["command_records"][0]["exit_code"]  # schema-invalid record
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": p})
    assert receipt.passed is False


def test_bad_failure_class_fails(tmp_path):
    rd = new_run(str(tmp_path))
    p = _wellformed_proposal(rd)
    p["candidate_failures"][0]["failure_class"] = "NOT_A_CLASS"
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": p})
    assert receipt.passed is False


def test_child_not_tracing_to_parent_fails(tmp_path):
    rd = new_run(str(tmp_path))
    p = _wellformed_proposal(rd)
    p["children"][0]["parent_id"] = "someone-else"
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": p})
    assert receipt.passed is False


def test_admissibility_receipt_cannot_discharge_hard(tmp_path):
    # THE load-bearing test (Panel P0-D1 / invariant 3): even a passing
    # admissibility receipt cannot discharge a HARD obligation, and does not
    # claim any command executed.
    rd = new_run(str(tmp_path))
    receipt = AdmissibilityValidator().validate(
        rd, node=None, config={"proposal": _wellformed_proposal(rd)})
    assert receipt.passed is True
    assert can_discharge_hard(receipt) is False
    # It must not claim execution: no HARD-style exit_codes attesting a run.
    assert receipt.strength is ValidationStrength.ADMISSIBILITY


def test_missing_coverage_or_residue_fails(tmp_path):
    rd = new_run(str(tmp_path))
    p = _wellformed_proposal(rd)
    del p["coverage_map"]
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": p})
    assert receipt.passed is False


def test_bool_exit_code_rejected(tmp_path):
    # F9/sol-11: isinstance(True, int) is True — a boolean exit_code must be
    # rejected (type() is int), not accepted as a valid record.
    rd = new_run(str(tmp_path))
    p = _wellformed_proposal(rd)
    p["command_records"][0]["exit_code"] = True
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": p})
    assert receipt.passed is False


def test_non_dict_member_does_not_crash(tmp_path):
    # A non-dict in a collection must become a reason, not raise AttributeError.
    rd = new_run(str(tmp_path))
    p = _wellformed_proposal(rd)
    p["citations"].append("not-a-dict")
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": p})
    assert receipt.passed is False  # degraded, not crashed


def test_non_string_handle_does_not_crash(tmp_path):
    rd = new_run(str(tmp_path))
    p = _wellformed_proposal(rd)
    p["citations"][0]["source_handle"] = 12345  # not a string
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": p})
    assert receipt.passed is False


def test_non_dict_proposal_does_not_crash(tmp_path):
    rd = new_run(str(tmp_path))
    receipt = AdmissibilityValidator().validate(rd, node=None, config={"proposal": "nope"})
    assert receipt.passed is False


def test_missing_execution_contract_fails_closed(tmp_path):
    rd = new_run(str(tmp_path))
    proposal = _wellformed_proposal(rd)
    del proposal["execution_contract"]
    receipt = AdmissibilityValidator().validate(
        rd, node=None, config={"proposal": proposal},
    )
    assert receipt.passed is False


def test_candidate_failures_wrong_collection_shape_fails_closed(tmp_path):
    rd = new_run(str(tmp_path))
    proposal = _wellformed_proposal(rd)
    proposal["candidate_failures"] = {
        "failure_class": "CLEAN_INSTALL_BLOCKER",
        "locator": "brokencli/cli.py",
    }
    receipt = AdmissibilityValidator().validate(
        rd, node=None, config={"proposal": proposal},
    )
    assert receipt.passed is False


def test_non_dict_candidate_failure_fails_closed(tmp_path):
    rd = new_run(str(tmp_path))
    proposal = _wellformed_proposal(rd)
    proposal["candidate_failures"] = ["not-a-candidate"]
    receipt = AdmissibilityValidator().validate(
        rd, node=None, config={"proposal": proposal},
    )
    assert receipt.passed is False
