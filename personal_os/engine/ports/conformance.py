"""Task 1.7 — the shared WorkResult contract oracle.

``assert_workresult_contract(result, run_dir)`` is the single conformance gate
that BOTH the FakeWorker and the real HermesWorker (Phase 2) must satisfy — it
is how we prove the fake→real substitution is safe (Panel P0-D2). It accepts a
``WorkResult`` or its ``to_dict()`` form (the latter lets a test smuggle a
forbidden ``receipt`` field to prove the oracle rejects self-certification).

Checks:
- ``status`` is one of the allowed values,
- every artifact handle RESOLVES inside ``run_dir`` (opaque handle, in-run),
- every ``evidence_proposal`` is a dict carrying at least ``claim_id``,
- NO ``receipt`` and NO pass bit is present anywhere (invariant 1 — workers
  never self-certify).

Raises ``AssertionError`` on any violation (so it reads naturally in tests and
fails closed in the discharge path).
"""

from __future__ import annotations

from typing import Any, Dict, Union

from personal_os.engine.contract.run_dir import ArtifactHandle, RunDir
from personal_os.engine.ports.worker import WorkResult

_ALLOWED_STATUS = {"ok", "failed", "error"}
_FORBIDDEN_KEYS = {"receipt", "passed", "pass"}


def assert_workresult_contract(
    result: Union[WorkResult, Dict[str, Any]],
    run_dir: RunDir,
    require_patch_handle: bool = False,
) -> None:
    """Assert ``result`` is a schema-valid, non-self-certifying WorkResult.

    When ``require_patch_handle`` is true, require at least one artifact handle
    before an EXECUTE caller can index or apply the proposed patch.
    """
    assert isinstance(result, (WorkResult, dict)), (
        "result must be a WorkResult or dict"
    )
    d = result.to_dict() if isinstance(result, WorkResult) else dict(result)

    # 1. No self-certification anywhere.
    _assert_no_forbidden_keys_deep(d)
    for key in _FORBIDDEN_KEYS:
        assert key not in d, f"WorkResult must not carry a {key!r} field (invariant 1)"

    # 2. Status is in the allowed set.
    assert d.get("status") in _ALLOWED_STATUS, f"bad status: {d.get('status')!r}"

    # 3. Artifact handles resolve inside the run.
    handles = d.get("artifact_handles", [])
    assert isinstance(handles, list), "artifact_handles must be a list"
    if require_patch_handle:
        assert handles, "EXECUTE result must include a patch artifact handle"
    for h in handles:
        assert isinstance(h, (str, ArtifactHandle)), (
            "artifact handle must be a string or ArtifactHandle"
        )
        try:
            handle = ArtifactHandle.from_str(h) if isinstance(h, str) else h
            run_dir.resolve_handle(handle)
        except ValueError as exc:
            raise AssertionError(f"artifact handle invalid or does not resolve: {exc}")

    # 4. Evidence proposals are well-formed (and carry no self-certification).
    evidence_proposals = d.get("evidence_proposals", [])
    assert isinstance(evidence_proposals, list), "evidence_proposals must be a list"
    for ev in evidence_proposals:
        assert isinstance(ev, dict), "evidence_proposal must be a dict"
        assert ev.get("claim_id"), "evidence_proposal missing claim_id"
        # Defense-in-depth: no forbidden self-certification key ANYWHERE in the
        # (arbitrarily nested) evidence proposal, incl. a nested `proposal` dict.
        _assert_no_forbidden_keys_deep(ev)


def _assert_no_forbidden_keys_deep(obj: Any) -> None:
    """Recursively assert no forbidden self-certification key appears."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert k not in _FORBIDDEN_KEYS, (
                f"nested {k!r} field is a forbidden self-certification (invariant 1)"
            )
            _assert_no_forbidden_keys_deep(v)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _assert_no_forbidden_keys_deep(item)
