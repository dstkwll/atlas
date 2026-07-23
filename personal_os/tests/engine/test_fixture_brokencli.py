"""Task 1.2 — the brokencli fixture is genuinely broken in a clean offline venv.

This is a real (non-mocked) install+run against a fresh venv, so it's slower
than the pure-contract tests. It proves the fixture actually fails before any
engine work happens (a happy-path-only fixture would make the whole HARD-leaf
milestone vacuous).
"""

from __future__ import annotations

import os

from personal_os.tests.engine.fixtures.broken_cli_fixture import (
    clean_install_and_check,
    fixture_root,
)


def test_fixture_files_exist():
    root = fixture_root()
    assert os.path.isfile(os.path.join(root, "setup.py"))
    assert os.path.isfile(os.path.join(root, "README.md"))
    assert os.path.isfile(os.path.join(root, "test_brokencli.py"))
    assert os.path.isfile(os.path.join(root, "brokencli", "cli.py"))
    assert os.path.isfile(os.path.join(root, "brokencli", "vendor", "tinyfmt.py"))


def test_fixture_is_genuinely_broken_offline(tmp_path):
    out = clean_install_and_check(fixture_root(), str(tmp_path / "venv"))
    # It installs cleanly but the documented command / tests FAIL.
    assert out.ran is True
    assert out.passed is False
    # The failure is the wrong-import-path bug, surfaced offline.
    combined = "\n".join(out.logs.values())
    assert "tinyfmt" in combined
    assert "ModuleNotFoundError" in combined
