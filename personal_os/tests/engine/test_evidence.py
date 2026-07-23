"""Task 0.4 — Evidence + ResidualUncertainty round-trips.

Evidence carries an OPAQUE ``source_handle`` (invariant 9) — never a filesystem
path. ResidualUncertainty is the explicit "what a refine node could not prove"
record, carried upward and reported (but not scheduling-gating in v0).
"""

from __future__ import annotations

import json

from personal_os.engine.contract.evidence import Evidence, ResidualUncertainty


def test_evidence_round_trip():
    e = Evidence(
        claim_id="c1",
        kind="clean_run_log",
        source_handle="artifact:abc123",
        sha256="deadbeef",
        accessed_at="2026-07-23T00:00:00Z",
    )
    d = e.to_dict()
    assert Evidence.from_dict(d).to_dict() == d


def test_evidence_allows_none_sha():
    e = Evidence(claim_id="c1", kind="k", source_handle="artifact:x", sha256=None,
                 accessed_at="2026-07-23T00:00:00Z")
    assert Evidence.from_dict(e.to_dict()).sha256 is None


def test_evidence_source_handle_is_opaque_not_path():
    # A handle is an opaque id, not an absolute path. The contract stores it as
    # given; the point is Core never MINTS a path here (enforced at call sites).
    e = Evidence(claim_id="c1", kind="k", source_handle="artifact:sha",
                 sha256=None, accessed_at="t")
    assert not e.source_handle.startswith("/")


def test_residual_round_trip():
    r = ResidualUncertainty(
        node_id="n1",
        statement="sources may be insufficient",
        why_unprovable="no deterministic oracle for sufficiency",
        impact_if_wrong="report understates risk",
    )
    d = r.to_dict()
    assert ResidualUncertainty.from_dict(d).to_dict() == d


def test_residual_list_serializes_stably():
    rs = [
        ResidualUncertainty("n1", "s1", "w1", "i1"),
        ResidualUncertainty("n2", "s2", "w2", "i2"),
    ]
    payload = [r.to_dict() for r in rs]
    s1 = json.dumps(payload, sort_keys=True)
    s2 = json.dumps([ResidualUncertainty.from_dict(r).to_dict() for r in payload], sort_keys=True)
    assert s1 == s2
