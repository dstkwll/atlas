"""Task 1.3 — staging + patch application (Core owns; handle-based).

``stage`` copies the fixture into ``run_dir/staging`` so the source tree is
never mutated. ``apply_patch`` resolves a worker's opaque patch handle and
applies it to the STAGED tree only; a patch targeting outside the staging root
is rejected (invariant 12 — the code-enforced filesystem wall).
"""

from __future__ import annotations

import json
import os

import pytest

from personal_os.engine.contract.run_dir import new_run
from personal_os.engine.core.staging import apply_patch, stage
from personal_os.tests.engine.fixtures.broken_cli_fixture import fixture_root


def _patch_handle(rd, target_relpath, new_content):
    payload = json.dumps({
        "target": target_relpath,
        "content": new_content,
    }).encode("utf-8")
    return rd.put_artifact(payload)


def test_stage_copies_and_leaves_source_untouched(tmp_path):
    rd = new_run(str(tmp_path))
    src = fixture_root()
    staged = stage(src, rd)
    # Staged copy exists and has the CLI.
    assert os.path.isfile(os.path.join(staged, "brokencli", "cli.py"))
    # Source still has the original (broken) import — untouched.
    with open(os.path.join(src, "brokencli", "cli.py")) as f:
        assert "from tinyfmt import leftpad" in f.read()


def test_apply_patch_edits_staged_tree(tmp_path):
    rd = new_run(str(tmp_path))
    staged = stage(fixture_root(), rd)
    fixed = "from brokencli.vendor.tinyfmt import leftpad\n"
    # Read the current cli.py, replace the bad import line.
    cli_rel = os.path.join("brokencli", "cli.py")
    with open(os.path.join(staged, cli_rel)) as f:
        content = f.read().replace(
            "from tinyfmt import leftpad  # noqa: F401  (BUG: wrong module path)",
            "from brokencli.vendor.tinyfmt import leftpad",
        )
    h = _patch_handle(rd, cli_rel, content)
    apply_patch(rd, h)
    with open(os.path.join(staged, cli_rel)) as f:
        assert "from brokencli.vendor.tinyfmt import leftpad" in f.read()


def test_apply_patch_rejects_out_of_root_target(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    h = _patch_handle(rd, "../escape.py", "x = 1\n")
    with pytest.raises(ValueError):
        apply_patch(rd, h)


def test_apply_patch_rejects_absolute_target(tmp_path):
    rd = new_run(str(tmp_path))
    stage(fixture_root(), rd)
    h = _patch_handle(rd, "/etc/evil", "x = 1\n")
    with pytest.raises(ValueError):
        apply_patch(rd, h)
