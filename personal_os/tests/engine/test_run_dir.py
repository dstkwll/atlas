"""Task 0.8 — run-dir manager + ArtifactHandle (isolation, invariant 10).

``new_run(root)`` mints a fresh ``RunDir`` (uuid4 run_id) with ``staging/``,
``venv/``, ``artifacts/`` (content-addressed ``artifacts/<sha256>``), and
``events.jsonl``. It refuses to reuse a non-empty run dir. ``ArtifactHandle``
is the OPAQUE token that crosses the port (invariant 9) — it resolves to
``artifacts/<sha256>`` ONLY within its own RunDir.
"""

from __future__ import annotations

import os

import pytest

from personal_os.engine.contract.run_dir import ArtifactHandle, RunDir, new_run


def test_new_run_creates_subpaths(tmp_path):
    rd = new_run(str(tmp_path))
    assert rd.run_id
    for sub in ("staging", "venv", "artifacts"):
        assert os.path.isdir(os.path.join(rd.path, sub))
    assert rd.events_path.endswith("events.jsonl")


def test_two_runs_get_distinct_dirs(tmp_path):
    a = new_run(str(tmp_path))
    b = new_run(str(tmp_path))
    assert a.run_id != b.run_id
    assert a.path != b.path


def test_reusing_populated_run_dir_raises(tmp_path):
    rd = new_run(str(tmp_path))
    # Force a collision: try to re-adopt the SAME run_id with content present.
    (os.path.join(rd.path, "artifacts"))
    with open(os.path.join(rd.path, "artifacts", "junk"), "w") as f:
        f.write("x")
    with pytest.raises(ValueError):
        RunDir.adopt(rd.path, rd.run_id, require_empty=True)


def test_reusing_run_dir_with_stale_journal_raises(tmp_path):
    # P2-1 hardening: a leftover top-level events.jsonl from a prior aborted run
    # must make the dir non-adoptable even when the subdirs are empty.
    rd = new_run(str(tmp_path))
    with open(rd.events_path, "w") as f:
        f.write('{"event_id":"stale"}\n')
    with pytest.raises(ValueError):
        RunDir.adopt(rd.path, rd.run_id, require_empty=True)


def test_put_artifact_is_content_addressed(tmp_path):
    rd = new_run(str(tmp_path))
    h = rd.put_artifact(b"hello world")
    assert isinstance(h, ArtifactHandle)
    resolved = rd.resolve_handle(h)
    assert os.path.exists(resolved)
    with open(resolved, "rb") as f:
        assert f.read() == b"hello world"


def test_same_bytes_same_handle(tmp_path):
    rd = new_run(str(tmp_path))
    h1 = rd.put_artifact(b"same")
    h2 = rd.put_artifact(b"same")
    assert h1.id == h2.id


def test_handle_resolves_only_inside_its_rundir(tmp_path):
    a = new_run(str(tmp_path))
    b = new_run(str(tmp_path))
    h = a.put_artifact(b"payload")
    # b never stored this artifact -> resolving a's handle in b raises.
    with pytest.raises(ValueError):
        b.resolve_handle(h)


def test_handle_round_trips_opaque(tmp_path):
    rd = new_run(str(tmp_path))
    h = rd.put_artifact(b"data")
    h2 = ArtifactHandle.from_str(h.to_str())
    assert h2.id == h.id
    # The handle is opaque: not an absolute path.
    assert not h.to_str().startswith("/")


def test_from_str_rejects_non_hex_id():
    # F1 (VERIFIED security hole): a handle id must be exactly 64 lowercase hex
    # chars. An absolute path or traversal id would let os.path.join escape the
    # artifacts root.
    for bad in ("artifact:/tmp/outside.json", "artifact:../escape",
                "artifact:..", "artifact:", "artifact:ABC", "artifact:xyz",
                "artifact:" + "a" * 63, "artifact:" + "a" * 65,
                "artifact:" + "g" * 64):
        with pytest.raises(ValueError):
            ArtifactHandle.from_str(bad)


def test_from_str_accepts_valid_sha256():
    good = "artifact:" + "a" * 64
    assert ArtifactHandle.from_str(good).id == "a" * 64


def test_put_artifact_yields_valid_hex_handle(tmp_path):
    rd = new_run(str(tmp_path))
    h = rd.put_artifact(b"x")
    # Round-trips through the strict validator.
    assert ArtifactHandle.from_str(h.to_str()).id == h.id


def test_resolve_handle_rejects_escape_id(tmp_path):
    # Even if an attacker constructs an ArtifactHandle with a poisoned id
    # directly, resolve_handle must not escape the artifacts dir.
    rd = new_run(str(tmp_path))
    outside = tmp_path / "outside.json"
    outside.write_text("SECRET")
    poisoned = ArtifactHandle(id=str(outside))  # absolute path as id
    with pytest.raises(ValueError):
        rd.resolve_handle(poisoned)
    poisoned2 = ArtifactHandle(id="../../etc/passwd")
    with pytest.raises(ValueError):
        rd.resolve_handle(poisoned2)
