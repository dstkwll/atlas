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

    def validate(self, workspace: RunDir, node: Any, config: Optional[Dict[str, Any]] = None) -> Receipt:
        """Run the HARD checks against ``workspace`` (a RunDir); mint a receipt.

        ``config`` may carry ``timeout_s`` (per-subprocess). A 0 timeout forces
        an immediate timeout on every step (used to prove the ran/passed
        semantics deterministically).
        """
        config = config or {}
        timeout_s = int(config.get("timeout_s", _DEFAULT_TIMEOUT))

        run_dir = workspace
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

        commands: List[str] = []
        exit_codes: List[int] = []
        artifact_hashes: Dict[str, str] = {}
        passed = True

        try:
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
            # ANY validator-internal error (OSError, hashing failure, etc.)
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

        A timeout is reported as exit code 124 with the partial output (never a
        silent None). A missing executable is 127.
        """
        try:
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout_s,
                text=True,
            )
            return (proc.stdout or ""), proc.returncode
        except subprocess.TimeoutExpired as exc:
            partial = exc.output or ""
            if isinstance(partial, bytes):
                partial = partial.decode("utf-8", "replace")
            return partial + f"\n[TIMEOUT after {timeout_s}s]", 124
        except FileNotFoundError as exc:
            return f"[missing executable: {exc}]", 127
