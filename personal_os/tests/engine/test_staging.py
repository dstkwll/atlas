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


@pytest.mark.parametrize("target_kind", ["inside", "outside"])
def test_stage_rejects_source_symlinks_without_dereferencing(tmp_path, target_kind):
    """Staging fails closed on every link and never copies linked bytes."""
    source = tmp_path / "source"
    source.mkdir()
    (source / "plain.txt").write_text("plain")
    if target_kind == "inside":
        target = source / "plain.txt"
    else:
        target = tmp_path / "outside.txt"
        target.write_text("outside-secret")
    os.symlink(str(target), str(source / "link.txt"))
    rd = new_run(str(tmp_path / "runs"))

    with pytest.raises(ValueError, match="symlink"):
        stage(str(source), rd)

    staged_link = os.path.join(rd.staging_dir, "link.txt")
    assert not (os.path.lexists(staged_link) and not os.path.islink(staged_link))


def test_stage_rejects_root_source_tree_symlink_without_materializing_bytes(tmp_path):
    """The source_tree path itself must not be dereferenced when it is a link."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.bin").write_bytes(b"outside-secret")
    source_link = tmp_path / "source-link"
    os.symlink(str(outside), str(source_link))
    rd = new_run(str(tmp_path / "runs"))

    with pytest.raises(ValueError, match="source_tree must not be a symlink"):
        stage(str(source_link), rd)

    assert not os.path.exists(os.path.join(rd.staging_dir, "secret.bin"))


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


def test_apply_patch_refuses_to_write_through_symlink(tmp_path):
    # F2/sol-2: if the staged target path is (or becomes) a symlink pointing
    # outside staging, the write must NOT follow it and land outside the wall.
    rd = new_run(str(tmp_path))
    staged = stage(fixture_root(), rd)
    outside = tmp_path / "outside_target.py"
    # Place a symlink INSIDE staging that points OUT of staging.
    link_rel = "sneaky.py"
    os.symlink(str(outside), os.path.join(staged, link_rel))
    h = _patch_handle(rd, link_rel, "PWNED = 1\n")
    with pytest.raises(ValueError):
        apply_patch(rd, h)
    # The outside target must NOT have been created/written.
    assert not outside.exists()


def test_apply_patch_rejects_symlink_in_intermediate_component(tmp_path):
    """Every directory component is opened descriptor-relative, without follow."""
    rd = new_run(str(tmp_path))
    staged = stage(fixture_root(), rd)
    real_dir = os.path.join(staged, "real-dir")
    os.mkdir(real_dir)
    os.symlink(real_dir, os.path.join(staged, "linked-dir"))
    h = _patch_handle(rd, "linked-dir/escaped.py", "PWNED = 1\n")

    with pytest.raises(ValueError):
        apply_patch(rd, h)

    assert not os.path.exists(os.path.join(real_dir, "escaped.py"))


def test_apply_patch_replaces_shared_inode_without_modifying_outside_file(tmp_path):
    """A staged hard link must be replaced, never truncated in place."""
    rd = new_run(str(tmp_path))
    staged = stage(fixture_root(), rd)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside-original")
    staged_leaf = os.path.join(staged, "shared.txt")
    os.link(str(outside), staged_leaf)
    original_inode = os.stat(outside).st_ino

    apply_patch(rd, _patch_handle(rd, "shared.txt", "staged-new"))

    assert outside.read_text() == "outside-original"
    with open(staged_leaf) as f:
        assert f.read() == "staged-new"
    assert os.stat(staged_leaf).st_ino != original_inode
