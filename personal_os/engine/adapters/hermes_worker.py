"""Task 2.6 — the real Hermes worker adapter (behind the proven port).

``HermesWorker`` implements ``WorkerPort`` by shelling out to a detached
``hermes -z -m opus --provider copilot -t web,file --yolo`` process. It is the
Phase-1 port's first *real* adapter, and it must pass the exact same
``assert_workresult_contract`` oracle the FakeWorker does (Panel P0-D2).

Two load-bearing behaviors (both spike-proven traps, see design.md §9):

1. **Absolute-path injection.** The Hermes file tool resolves relative paths
   against its OWN cwd (home), not ``$PWD``. So the adapter allocates an
   output path INSIDE the run, resolves it to an ABSOLUTE path, and injects
   that absolute path into the prompt — telling the worker exactly where to
   write. This path-resolution is the adapter's private concern; it never
   crosses the port (Core only ever sees the opaque handle the adapter mints
   AFTER verifying the artifact).

2. **Verify-at-handle, never trust stdout.** A detached worker can print
   ``WORKER_DONE`` and exit 0 without writing anything (the 13-second phantom).
   So on return the adapter checks the artifact actually exists at the absolute
   path; only then does it read the bytes, content-address them into the run
   (minting an opaque handle), and return a well-formed ``WorkResult``. If the
   artifact is absent, it returns ``status="failed"`` with a failure record —
   no phantom handle.

The detached subprocess call is injectable (``_run_hermes``) so the unit tests
run without spawning hermes; the real call lives in a ``@pytest.mark.integration``
nightly test.
"""

from __future__ import annotations

import os
import subprocess
from typing import Callable, Optional, Tuple

from personal_os.engine.contract.run_dir import RunDir
from personal_os.engine.ports.worker import WorkRequest, WorkResult

# Signature: (cmd, prompt, out_abs_path, timeout_s) -> (returncode, stdout)
RunHermes = Callable[[list, str, str, int], Tuple[int, str]]

_DEFAULT_TIMEOUT = 900
_HERMES_CMD = [
    "hermes", "-z", "-m", "opus", "--provider", "copilot",
    "-t", "web,file", "--yolo",
]


def _default_run_hermes(cmd: list, prompt: str, out_abs_path: str, timeout_s: int) -> Tuple[int, str]:
    """Spawn a detached hermes with the prompt; perl-alarm timeout wrapper."""
    wrapped = ["perl", "-e", f"alarm {timeout_s}; exec @ARGV", *cmd, prompt]
    proc = subprocess.run(
        wrapped,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout_s + 30,
    )
    return proc.returncode, proc.stdout or ""


class HermesWorker:
    """A real ``WorkerPort`` backed by a detached hermes tool-worker."""

    def __init__(self, run_dir: RunDir, _run_hermes: Optional[RunHermes] = None) -> None:
        self._run_dir = run_dir
        self._run_hermes = _run_hermes or _default_run_hermes

    def execute(self, request: WorkRequest) -> WorkResult:
        # Allocate an output path inside the run and resolve to ABSOLUTE — the
        # file-tool cwd trap fix. This path is the adapter's private substrate;
        # it never crosses the port.
        out_rel = os.path.join("worker_out", f"{request.node_id}.attempt{request.attempt}.json")
        out_abs = os.path.join(self._run_dir.path, out_rel)
        os.makedirs(os.path.dirname(out_abs), exist_ok=True)

        prompt = self._build_prompt(request, out_abs)
        timeout_s = int(request.constraints.get("deadline_s", _DEFAULT_TIMEOUT))

        code, stdout = self._run_hermes(_HERMES_CMD, prompt, out_abs, timeout_s)

        # Verify-at-handle: never trust stdout/exit-0. The artifact must exist.
        if not os.path.exists(out_abs):
            return WorkResult(
                status="failed",
                artifact_handles=[],
                evidence_proposals=[],
                usage={"returncode": code},
                failure={
                    "reason": "artifact_absent_at_path",
                    "detail": "worker exited without writing the artifact",
                    "stdout_tail": stdout[-500:],
                },
            )

        # The artifact exists: read its bytes and content-address into the run,
        # minting the opaque handle that DOES cross the port.
        with open(out_abs, "rb") as f:
            data = f.read()
        handle = self._run_dir.put_artifact(data)

        return WorkResult(
            status="ok",
            artifact_handles=[handle],
            evidence_proposals=[
                {"claim_id": "hermes-artifact", "kind": "patch",
                 "source_handle": handle.to_str()},
            ],
            usage={"returncode": code},
            failure=None,
        )

    @staticmethod
    def _build_prompt(request: WorkRequest, out_abs: str) -> str:
        """Build the worker prompt, injecting the ABSOLUTE output path."""
        target = request.contract.get("target", "")
        return (
            f"Objective: {request.objective}\n"
            f"Target file to fix: {target}\n"
            f"Write your proposed patch as JSON "
            f'{{"target": "<run-relative path>", "content": "<full new file text>"}} '
            f"to this EXACT absolute path (use the file tool with this absolute "
            f"path, do not use a relative path): {out_abs}\n"
            f"When done, print WORKER_DONE."
        )
