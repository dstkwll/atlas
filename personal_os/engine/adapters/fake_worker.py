"""Task 1.5 — FakeWorker: a deterministic, no-LLM ``WorkerPort``.

For an EXECUTE request it emits the KNOWN-good one-line import fix for the
brokencli fixture as a patch payload (``{"target", "content"}`` — the schema
``core.staging.apply_patch`` consumes), stores it as a content-addressed
artifact in the RunDir, and returns a well-formed ``WorkResult`` referencing
that handle. No receipt, no pass bit (invariant 1): Core validates the artifact
and mints the receipt.

The proposed ``content`` is the full corrected ``cli.py`` (whole-file replace),
derived deterministically from the fixture source with the bad import line
swapped for the vendored path — so the same patch bytes always
content-address to the same handle (proven in the deterministic test).
"""

from __future__ import annotations

import json

from personal_os.engine.contract.run_dir import RunDir
from personal_os.engine.ports.worker import WorkRequest, WorkResult
from personal_os.tests.engine.fixtures.broken_cli_fixture import fixture_root

_BAD_IMPORT = "from tinyfmt import leftpad  # noqa: F401  (BUG: wrong module path)"
_GOOD_IMPORT = "from brokencli.vendor.tinyfmt import leftpad"


def _known_good_cli() -> str:
    """The full fixed ``cli.py`` content (deterministic from the fixture)."""
    import os

    src = os.path.join(fixture_root(), "brokencli", "cli.py")
    with open(src) as f:
        content = f.read()
    return content.replace(_BAD_IMPORT, _GOOD_IMPORT)


class FakeWorker:
    """A canned worker that proposes the correct brokencli patch, no LLM."""

    def __init__(self, run_dir: RunDir) -> None:
        self._run_dir = run_dir

    def execute(self, request: WorkRequest) -> WorkResult:
        target = request.contract.get("target", "brokencli/cli.py")
        payload = {
            "target": target,
            "content": _known_good_cli(),
        }
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        handle = self._run_dir.put_artifact(data)
        return WorkResult(
            status="ok",
            artifact_handles=[handle],
            evidence_proposals=[
                {
                    "claim_id": "fix-import",
                    "kind": "patch",
                    "source_handle": handle.to_str(),
                }
            ],
            usage={"llm_calls": 0},
            failure=None,
        )


# The canonical execution-leaf contract proposal the refiner emits — the same
# shape the compiler normalizes and the Phase-1 leaf fulfills (parity).
_EXECUTION_CONTRACT_PROPOSAL = {
    "target": "brokencli/cli.py",
    "objective": "make brokencli reproducibly runnable",
    "install_cmd": "pip install --no-index --no-build-isolation .",
    "run_cmd": "python -m brokencli.cli hello 8",
    "test_cmd": "python -m unittest discover -p test_*.py",
}


class FakeRefiner:
    """A canned REFINE worker: emits a well-formed research proposal, no LLM.

    The proposal cites a real (resolving) evidence artifact, declares a
    schema-valid command record, lists candidate failures, traces its children
    to the parent, and carries the canonical ``execution_contract`` the refiner
    would compile the execution child from. ``make_inadmissible`` drops a
    required field so the admissibility gate blocks the execution child.
    """

    def __init__(self, run_dir: RunDir, make_inadmissible: bool = False,
                 exec_locator: str = "brokencli/cli.py") -> None:
        self._run_dir = run_dir
        self._make_inadmissible = make_inadmissible
        self._exec_locator = exec_locator

    def execute(self, request: WorkRequest) -> WorkResult:
        parent_id = request.node_id
        # A real evidence artifact so citations/log handles resolve.
        ev_handle = self._run_dir.put_artifact(
            b"clean run: `brokencli` -> ModuleNotFoundError: No module named 'tinyfmt'"
        )
        proposal = {
            "parent_id": parent_id,
            "citations": [
                {"claim_id": "readme", "source_handle": ev_handle.to_str()},
            ],
            "command_records": [
                {"cmd": "python -m brokencli.cli hello 8", "exit_code": 1,
                 "log_handle": ev_handle.to_str()},
            ],
            "candidate_failures": [
                {"failure_class": "CLEAN_INSTALL_BLOCKER",
                 "locator": self._exec_locator},
            ],
            "children": [
                {"id": f"{parent_id}-exec", "parent_id": parent_id,
                 "objective": "fix the import"},
            ],
            "coverage_map": {"import_bug": f"{parent_id}-exec"},
            "residue": ["other latent failures possible"],
            "execution_contract": dict(_EXECUTION_CONTRACT_PROPOSAL),
        }
        if self._make_inadmissible:
            # Break admissibility: remove the required coverage_map.
            del proposal["coverage_map"]

        return WorkResult(
            status="ok",
            artifact_handles=[ev_handle],
            evidence_proposals=[
                {"claim_id": "refine-proposal", "kind": "decomposition",
                 "source_handle": ev_handle.to_str(), "proposal": proposal},
            ],
            usage={"llm_calls": 0},
            failure=None,
        )
