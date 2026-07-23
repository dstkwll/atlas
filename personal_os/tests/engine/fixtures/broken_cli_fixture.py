"""Task 1.2 — helpers to locate and clean-verify the brokencli fixture.

``fixture_root()`` returns the absolute path to the brokencli source tree.
``clean_install_and_check(src, venv_dir)`` builds a FRESH venv from the CURRENT
interpreter (``sys.executable`` — NOT system ``python3``, which on this host is
a setuptools-less 3.14 that can't build offline), installs the tree offline
(``--no-index --no-build-isolation``), runs the documented command + pytest, and
returns a structured result. It is the shared offline-exec primitive the HARD
validator (Task 1.4) reuses.

Everything is subprocess-timeout-wrapped (Skeptic E3): a hang becomes a
captured failure, never an indefinite block.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List

_DEFAULT_TIMEOUT = 120


def fixture_root() -> str:
    """Absolute path to the brokencli fixture source tree."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "brokencli")


@dataclass
class ExecOutcome:
    ran: bool
    passed: bool
    commands: List[str] = field(default_factory=list)
    exit_codes: List[int] = field(default_factory=list)
    logs: Dict[str, str] = field(default_factory=dict)  # label -> combined output


def _run(cmd: List[str], cwd: str, timeout: int) -> subprocess.CompletedProcess:
    """Run a subprocess with a hard timeout, capturing combined output."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        text=True,
    )


def clean_install_and_check(
    src: str,
    venv_dir: str,
    timeout: int = _DEFAULT_TIMEOUT,
) -> ExecOutcome:
    """Fresh-venv offline install + documented run + pytest against ``src``.

    Returns an ``ExecOutcome``; a timeout or nonzero exit yields
    ``passed=False`` with captured logs (never raises for a build/test failure).
    """
    commands: List[str] = []
    exit_codes: List[int] = []
    logs: Dict[str, str] = {}

    py = os.path.join(venv_dir, "bin", "python")
    pip = os.path.join(venv_dir, "bin", "pip")

    steps = [
        ("venv", [sys.executable, "-m", "venv", venv_dir], os.getcwd()),
        ("install", [pip, "install", "--no-index", "--no-build-isolation", src], src),
        ("run", [py, "-m", "brokencli.cli", "hello", "8"], src),
        ("test", [py, "-m", "unittest", "discover", "-p", "test_*.py"], src),
    ]

    ran_anything = False
    for label, cmd, cwd in steps:
        commands.append(" ".join(cmd))
        try:
            proc = _run(cmd, cwd=cwd, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            logs[label] = (exc.output or "") + f"\n[TIMEOUT after {timeout}s]"
            exit_codes.append(124)
            return ExecOutcome(ran=True, passed=False, commands=commands,
                               exit_codes=exit_codes, logs=logs)
        except FileNotFoundError as exc:
            logs[label] = f"[missing executable: {exc}]"
            exit_codes.append(127)
            return ExecOutcome(ran=ran_anything, passed=False, commands=commands,
                               exit_codes=exit_codes, logs=logs)
        ran_anything = True
        exit_codes.append(proc.returncode)
        logs[label] = proc.stdout or ""
        if proc.returncode != 0:
            # First failing step short-circuits; still a "ran" outcome.
            return ExecOutcome(ran=True, passed=False, commands=commands,
                               exit_codes=exit_codes, logs=logs)

    return ExecOutcome(ran=True, passed=True, commands=commands,
                       exit_codes=exit_codes, logs=logs)
