"""Task 0.7 / 0.7b — Workspace containment wall + negative cases.

``Workspace`` wraps an absolute run root and only ever resolves paths that stay
inside it. ``resolve(relpath)`` raises on ``..`` traversal, absolute-path
escape, and symlink escape (invariant 12). Its ``id`` is a hash of the
canonicalized run-relative structure — NOT the absolute root — so
``workspace_id`` is deterministic across machines/runs (invariant 11).

``fail_closed_if_synced(root)`` raises if the root resolves inside a known
cloud-synced location (the confidentiality wall is CODE, not hygiene).
"""

from __future__ import annotations

import os

import pytest

from personal_os.engine.contract.workspace import Workspace, fail_closed_if_synced


def test_in_root_resolves(tmp_path):
    ws = Workspace(str(tmp_path))
    p = ws.resolve("staging/file.txt")
    assert p.startswith(str(tmp_path))
    assert p.endswith("staging/file.txt")


def test_dotdot_traversal_raises(tmp_path):
    ws = Workspace(str(tmp_path))
    with pytest.raises(ValueError):
        ws.resolve("../escape.txt")


def test_absolute_escape_raises(tmp_path):
    ws = Workspace(str(tmp_path))
    with pytest.raises(ValueError):
        ws.resolve("/etc/passwd")


def test_symlink_escape_raises(tmp_path):
    ws = Workspace(str(tmp_path))
    # Create a symlink inside the root pointing OUT of the root.
    outside = tmp_path.parent / "outside_dir"
    outside.mkdir()
    link = tmp_path / "link"
    os.symlink(str(outside), str(link))
    with pytest.raises(ValueError):
        ws.resolve("link/secret.txt")


def test_workspace_id_is_deterministic_not_abs_root(tmp_path):
    # Two roots at different absolute paths but identical run-relative structure
    # produce the SAME workspace_id.
    a = tmp_path / "a"
    b = tmp_path / "b"
    for root in (a, b):
        (root / "staging").mkdir(parents=True)
        (root / "staging" / "x.txt").write_text("same")
    id_a = Workspace(str(a)).id
    id_b = Workspace(str(b)).id
    assert id_a == id_b
    # And it is not simply the absolute path.
    assert str(a) not in id_a


def test_fail_closed_if_synced_trips_on_synced_root(tmp_path, monkeypatch):
    synced = tmp_path / "Library" / "Mobile Documents" / "work"
    synced.mkdir(parents=True)
    with pytest.raises(ValueError):
        fail_closed_if_synced(str(synced))


def test_fail_closed_if_synced_allows_plain_root(tmp_path):
    # A plain non-synced temp root does not trip the guard.
    fail_closed_if_synced(str(tmp_path))


def test_workspace_id_does_not_follow_outward_file_symlink(tmp_path):
    # F3/sol-8: a symlinked FILE inside the root must not be followed when
    # hashing — otherwise the workspace id depends on external content and
    # reads outside the containment wall. Changing the external target must NOT
    # change the workspace id.
    root = tmp_path / "ws"
    root.mkdir()
    (root / "real.txt").write_text("real")
    external = tmp_path / "external.txt"
    external.write_text("v1")
    os.symlink(str(external), str(root / "link.txt"))

    id_before = Workspace(str(root)).id
    external.write_text("v2-CHANGED-EXTERNALLY")
    id_after = Workspace(str(root)).id
    # The id must be stable against external file mutation (symlink not followed).
    assert id_before == id_after
