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
