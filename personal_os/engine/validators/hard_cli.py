"""Task 1.4 — the HARD CLI validator (Core-minted receipt, timeouts).

``HardCliValidator`` is the deterministic oracle for "this tiny CLI is
reproducibly runnable in a clean environment." It runs, against the STAGED
tree, inside a FRESH per-run venv:

  1. build a venv from ``sys.executable`` (py3.9 + setuptools — NOT system
     ``python3``, which on this host is a setuptools-less 3.14 that cannot
     build offline),
  2. ``pip install --no-index --no-build-isolation`` the staged tree (offline),
  3. the documented run command (``python -m brokencli.cli hello 8``),
  4. the stdlib ``unittest`` suite (no third-party runner needed offline).

EVERY subprocess is wrapped in a timeout (Skeptic E3). A timeout or
validator-internal error yields a ``ran=True, passed=False`` receipt carrying
the captured partial artifacts — never a silent ``None`` (Skeptic E3/E4).

Captured stdout/stderr for each step is written to CONTENT-ADDRESSED artifacts
in the RunDir; the receipt records ``artifact:<sha256> -> <sha256>`` so a
resume can re-verify by re-hashing (invariant 4/8). The receipt is minted here
in Core validator code — never from worker output (invariant 1).
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from personal_os.engine.contract import ENGINE_SCHEMA_VERSION
from personal_os.engine.contract.enums import ValidationStrength
from personal_os.engine.contract.receipt import Receipt
from personal_os.engine.contract.run_dir import RunDir
from personal_os.engine.contract.workspace import Workspace

_DEFAULT_TIMEOUT = 120


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class HardCliValidator:
    """Clean-env install + documented run + tests → Core-minted HARD receipt."""

    id = "hard_cli"
    version = "0.1.0"
    strength = ValidationStrength.HARD

    @staticmethod
    def expected_contract_fields():
        """The canonical leaf-contract fields this validator consumes (SSOT).

        Derived from the compiler's ``LEAF_CONTRACT_FIELDS`` — the validator has
        no independent hand-mirrored schema, so it can't drift (Task 2.1a).
        """
        from personal_os.engine.core.contract_compiler import LEAF_CONTRACT_FIELDS

        return tuple(LEAF_CONTRACT_FIELDS)

    def validate_contract(self, contract: Dict[str, Any]) -> None:
        """Fail-closed check of a leaf contract against the canonical schema.

        Raises ``ValueError`` on any missing OR unknown field (ignoring the
        ``schema_version`` stamp the compiler adds).
        """
        expected = set(self.expected_contract_fields())
        provided = {k for k in contract if k != "schema_version"}
        extra = provided - expected
        if extra:
            raise ValueError(f"contract has unknown field(s): {sorted(extra)}")
        missing = expected - provided
        if missing:
            raise ValueError(f"contract missing field(s): {sorted(missing)}")

    def validate(self, workspace: RunDir, node: Any, config: Optional[Dict[str, Any]] = None) -> Receipt:
        """Run the HARD checks against ``workspace`` (a RunDir); mint a receipt.

        ``config`` may carry ``timeout_s`` (per-subprocess). A 0 timeout forces
        an immediate timeout on every step (used to prove the ran/passed
        semantics deterministically).
        """
        config = config or {}
        run_dir = workspace

        # F6: initialize receipt accumulators FIRST, then do ALL fallible work
        # (config parse, path construction, step build, execution) inside the
        # guard — so even a bad timeout_s or path error mints a failed receipt
        # rather than propagating (sol-5 / invariant 4).
        commands: List[str] = []
        exit_codes: List[int] = []
        artifact_hashes: Dict[str, str] = {}
        passed = True
        workspace_id = ""

        try:
            raw_timeout = config.get("timeout_s", _DEFAULT_TIMEOUT)
            timeout_s = int(raw_timeout)
            if timeout_s < 0:
                raise ValueError(f"timeout_s must be >= 0, got {raw_timeout!r}")

            staged = run_dir.staging_dir
            venv_dir = os.path.join(run_dir.venv_dir, "hard_cli")
            py = os.path.join(venv_dir, "bin", "python")
            pip = os.path.join(venv_dir, "bin", "pip")

            steps = [
                ("venv", [sys.executable, "-m", "venv", venv_dir], os.getcwd()),
                ("install", [pip, "install", "--no-index", "--no-build-isolation", staged], staged),
                ("run", [py, "-m", "brokencli.cli", "hello", "8"], staged),
                ("test", [py, "-m", "unittest", "discover", "-p", "test_*.py"], staged),
            ]

            for label, cmd, cwd in steps:
                commands.append(" ".join(cmd))
                output, code = self._run_step(cmd, cwd, timeout_s)
                handle = run_dir.put_artifact(output.encode("utf-8"))
                artifact_hashes[handle.to_str()] = handle.id
                exit_codes.append(code)
                if code != 0:
                    passed = False
                    break  # first failing step short-circuits

            # workspace_id is the deterministic hash of the staged tree.
            workspace_id = Workspace(staged).id
        except Exception as exc:  # noqa: BLE001 - fail closed to a receipt
            # ANY validator-internal error (OSError, bad config, hashing, etc.)
            # must still mint a ran=True, passed=False receipt — never a silent
            # None and never a propagated raw exception (invariant 4 / Task 1.4).
            try:
                err_handle = run_dir.put_artifact(
                    f"[validator-internal error: {exc!r}]".encode("utf-8")
                )
                artifact_hashes[err_handle.to_str()] = err_handle.id
            except Exception:  # pragma: no cover - last-ditch
                pass
            return Receipt(
                node_id=getattr(node, "id", "") if node is not None else "",
                validator_id=self.id,
                validator_version=self.version,
                strength=self.strength,
                ran=True,
                passed=False,
                workspace_id="",
                commands=commands,
                exit_codes=exit_codes,
                artifact_hashes=artifact_hashes,
                evidence=[{"schema_version": ENGINE_SCHEMA_VERSION,
                           "internal_error": repr(exc)}],
                residual=[],
                ts=_now_iso(),
            )

        return Receipt(
            node_id=getattr(node, "id", "") if node is not None else "",
            validator_id=self.id,
            validator_version=self.version,
            strength=self.strength,
            ran=True,
            passed=passed,
            workspace_id=workspace_id,
            commands=commands,
            exit_codes=exit_codes,
            artifact_hashes=artifact_hashes,
            evidence=[{"schema_version": ENGINE_SCHEMA_VERSION}],
            residual=[],
            ts=_now_iso(),
        )

    @staticmethod
    def _run_step(cmd: List[str], cwd: str, timeout_s: int):
        """Run one subprocess with a hard timeout; return (combined_output, code).

        F7: the child is started in its OWN process group/session
        (``start_new_session=True``); on timeout the ENTIRE group is killed, so
        grandchildren spawned by pip/build/test can't survive and mutate the
        staging/venv after a timeout receipt is minted. Output is captured as
        BYTES and decoded explicitly as UTF-8 with replacement (locale-default
        text mode can raise on undecodable output and lose the partial log).

        A timeout is exit code 124 with the partial output; a missing
        executable is 127. Never returns a silent None.
        """
        import signal

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                start_new_session=True,  # new process group for group-kill
            )
        except FileNotFoundError as exc:
            return f"[missing executable: {exc}]", 127

        try:
            out_bytes, _ = proc.communicate(timeout=timeout_s)
            text = (out_bytes or b"").decode("utf-8", "replace")
            return text, proc.returncode
        except subprocess.TimeoutExpired:
            # Kill the WHOLE process group (child + any grandchildren).
            HardCliValidator._kill_group(proc, signal)
            try:
                out_bytes, _ = proc.communicate(timeout=10)
            except Exception:  # pragma: no cover - best effort drain
                out_bytes = b""
            text = (out_bytes or b"").decode("utf-8", "replace")
            return text + f"\n[TIMEOUT after {timeout_s}s]", 124

    @staticmethod
    def _kill_group(proc, signal_mod) -> None:
        """Best-effort kill of the child's entire process group."""
        try:
            pgid = os.getpgid(proc.pid)
            os.killpg(pgid, signal_mod.SIGKILL)
        except (ProcessLookupError, OSError, AttributeError):
            try:
                proc.kill()
            except Exception:  # pragma: no cover - last-ditch
                pass
