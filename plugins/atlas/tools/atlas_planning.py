#!/usr/bin/env python3
"""Deterministic controller for Atlas downstream planning state."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterator, Optional

import yaml

from atlas_control import (
    ControlError,
    canonical_date,
    file_sha256,
    gap,
    load_json,
    managed_path,
    read_frontmatter,
    resolve_existing_run_directory,
    validate_run,
    verified_state,
)
from render_system_design import verify as verify_system_design_board

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - POSIX
    msvcrt = None


PLANNING_FILE = "planning-control.json"
PLANNING_LOCK_FILE = ".atlas-planning.lock"
DOWNSTREAM_STAGES = ("system_design", "program_design", "tickets")
PLANNING_FIELDS = {
    "version", "run", "status", "phase", "revision", "stage0_anchor",
    "gates", "acceptances", "blocked_reason",
}
STAGE0_ANCHOR_FIELDS = {
    "control_sha256", "control_revision", "base_run_sha256", "effective_config_hash",
    "effective_config_revision", "product_closure",
}
PRODUCT_CLOSURE_FIELDS = {"version", "sha256"}
SYSTEM_DESIGN_FILE = "30-system-design.md"
SYSTEM_DESIGN_FIELDS = {
    "run", "version", "status", "gate_ready", "participation", "opened", "source_binding",
}
PRODUCT_SOURCE_FIELDS = {"kind", "artifact", "version", "sha256"}
STAGE0_SOURCE_FIELDS = {
    "kind", "artifact", "sha256", "effective_config_hash", "effective_config_revision",
}
PLANNING_ACCEPTANCE_FIELDS = {
    "candidate_version", "candidate_sha256", "authority", "accepted", "review_reference",
    "review_sha256", "source_bindings", "repository_baselines",
}
SYSTEM_DESIGN_SECTIONS = (
    "Current system",
    "Proposed system",
    "Responsibilities and seams",
    "Authoritative data ownership",
    "Contracts and interfaces",
    "Schema and protocol",
    "Lifecycle and data flow",
    "Failure and recovery",
    "Compatibility",
    "Trust, security, and operations",
    "Rejected alternatives",
    "Open decisions",
)
SYSTEM_DESIGN_REVIEW_REFERENCE = "reviews/system-design-v1.json"
SYSTEM_DESIGN_REVIEW_FIELDS = {
    "version", "run", "stage", "policy", "candidate_version", "candidate_sha256",
    "repository_baselines", "materiality", "semantic_review",
}
SYSTEM_DESIGN_DIMENSIONS = (
    "responsibilities_and_system_seams",
    "authoritative_data_ownership",
    "cross_module_external_contracts_and_dependencies",
    "target_schema_protocol",
    "end_to_end_lifecycle_failure_recovery",
    "compatibility_guarantees",
    "trust_security_operational_commitments",
)
SEMANTIC_REVIEW_FIELDS = {"verdict", "dimensions", "gaps"}
DIMENSION_REVIEW_FIELDS = {"dimension", "result", "evidence"}
SEMANTIC_GAP_FIELDS = {"code", "dimension", "problem", "resume_action"}
MATERIALITY_FIELDS = {"dimensions", "unavailable_reason"}


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_semantic_review(review: Any) -> None:
    if not isinstance(review, dict) or set(review) != SEMANTIC_REVIEW_FIELDS:
        raise ControlError("System Design semantic_review does not match its exact schema")
    verdict = review.get("verdict")
    rows = review.get("dimensions")
    gaps = review.get("gaps")
    if verdict not in {"PASS", "BLOCKED"} or not isinstance(rows, list) or not isinstance(gaps, list):
        raise ControlError("System Design semantic_review is malformed")
    if (
        len(rows) != len(SYSTEM_DESIGN_DIMENSIONS)
        or any(not isinstance(row, dict) or set(row) != DIMENSION_REVIEW_FIELDS for row in rows)
        or any(row.get("dimension") not in SYSTEM_DESIGN_DIMENSIONS for row in rows)
        or len({row.get("dimension") for row in rows}) != len(SYSTEM_DESIGN_DIMENSIONS)
        or any(row.get("result") not in {"PASS", "BLOCKED"} for row in rows)
        or any(not nonempty_string(row.get("evidence")) for row in rows)
    ):
        raise ControlError("System Design semantic_review must cover the exact seven dimensions")
    blocked = {row["dimension"] for row in rows if row["result"] == "BLOCKED"}
    if verdict == "PASS":
        if blocked or gaps:
            raise ControlError("System Design semantic PASS requires seven PASS rows and no gaps")
        return
    if not blocked or not gaps:
        raise ControlError("System Design semantic BLOCKED requires blocked dimensions and gaps")
    if (
        any(not isinstance(item, dict) or set(item) != SEMANTIC_GAP_FIELDS for item in gaps)
        or any(item.get("dimension") not in blocked for item in gaps)
        or len({item.get("dimension") for item in gaps}) != len(gaps)
        or {item.get("dimension") for item in gaps} != blocked
        or any(not all(nonempty_string(item.get(field)) for field in ("code", "problem", "resume_action")) for item in gaps)
    ):
        raise ControlError("System Design semantic BLOCKED gaps must exactly cover blocked dimensions")


def validate_complete_materiality(materiality: Any) -> str:
    if not isinstance(materiality, dict) or set(materiality) != MATERIALITY_FIELDS:
        raise ControlError("System Design materiality does not match its exact schema")
    rows = materiality.get("dimensions")
    unavailable_reason = materiality.get("unavailable_reason")
    if unavailable_reason is not None:
        if not isinstance(rows, list) or not nonempty_string(unavailable_reason):
            raise ControlError("System Design fail-closed materiality requires a nonempty unavailable_reason")
        return "HUMAN"
    if (
        not isinstance(rows, list)
        or len(rows) != len(SYSTEM_DESIGN_DIMENSIONS)
        or any(not isinstance(row, dict) or set(row) != DIMENSION_REVIEW_FIELDS for row in rows)
        or any(row.get("dimension") not in SYSTEM_DESIGN_DIMENSIONS for row in rows)
        or len({row.get("dimension") for row in rows}) != len(SYSTEM_DESIGN_DIMENSIONS)
        or any(row.get("result") not in {"MATERIAL", "NOT_MATERIAL", "UNAVAILABLE"} for row in rows)
        or any(not nonempty_string(row.get("evidence")) for row in rows)
    ):
        raise ControlError("System Design materiality must classify the exact seven dimensions")
    return (
        "HUMAN"
        if any(row["result"] in {"MATERIAL", "UNAVAILABLE"} for row in rows)
        else "AGENT_REVIEW"
    )


def load_system_design_review(
    run_dir: Path,
    effective: dict[str, Any],
    candidate_version: int,
    candidate_sha256: str,
    review_reference: Any,
) -> tuple[dict[str, Any], str, str]:
    if review_reference != SYSTEM_DESIGN_REVIEW_REFERENCE:
        raise ControlError(f"System Design review must use exact {SYSTEM_DESIGN_REVIEW_REFERENCE}")
    path = managed_path(run_dir, review_reference)
    if not path.is_file():
        raise ControlError("System Design review evidence is missing or not a real file")
    try:
        review_bytes = path.read_bytes()
        envelope = load_json(review_bytes.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ControlError("System Design review evidence is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ControlError("System Design review evidence is not valid duplicate-safe JSON") from exc
    review_sha256 = hashlib.sha256(review_bytes).hexdigest()
    if not isinstance(envelope, dict) or set(envelope) != SYSTEM_DESIGN_REVIEW_FIELDS:
        raise ControlError("System Design review envelope does not match its exact schema")
    policy = effective.get("gates", {}).get("system_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    if (
        type(envelope.get("version")) is not int
        or envelope.get("version") != 1
        or envelope.get("run") != effective["run"]
        or envelope.get("stage") != "system_design"
        or envelope.get("policy") != configured
        or configured not in {"AGENT_REVIEW", "HUMAN_IF_CHANGED"}
        or type(envelope.get("candidate_version")) is not int
        or envelope.get("candidate_version") != candidate_version
        or envelope.get("candidate_sha256") != candidate_sha256
        or envelope.get("repository_baselines") != effective["repos"]
    ):
        raise ControlError("System Design review evidence does not match current policy, candidate, or baselines")
    if configured == "AGENT_REVIEW":
        if envelope.get("materiality") is not None:
            raise ControlError("direct AGENT_REVIEW requires null materiality")
        mapped = "AGENT_REVIEW"
    else:
        mapped = validate_complete_materiality(envelope.get("materiality"))
    if mapped == "AGENT_REVIEW":
        validate_semantic_review(envelope.get("semantic_review"))
        if envelope["semantic_review"]["verdict"] != "PASS":
            raise ControlError("System Design semantic review is BLOCKED")
    elif envelope.get("semantic_review") is not None:
        raise ControlError("HUMAN-mapped System Design evidence requires null semantic_review")
    return envelope, review_sha256, mapped


@contextlib.contextmanager
def planning_lock(run_dir: Path) -> Iterator[None]:
    path = managed_path(run_dir, PLANNING_LOCK_FILE)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    acquired = False
    try:
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            elif msvcrt is not None:  # pragma: no cover - Windows fallback
                if os.fstat(fd).st_size == 0:
                    os.write(fd, b"0")
                os.lseek(fd, 0, os.SEEK_SET)
                getattr(msvcrt, "locking")(fd, getattr(msvcrt, "LK_NBLCK"), 1)
            else:  # pragma: no cover
                raise ControlError("this platform has no supported planning-lock primitive")
            acquired = True
        except (BlockingIOError, OSError) as exc:
            raise ControlError("another atlas-planning process is active for this run") from exc
        yield
    finally:
        if acquired:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif msvcrt is not None:  # pragma: no cover
                os.lseek(fd, 0, os.SEEK_SET)
                getattr(msvcrt, "locking")(fd, getattr(msvcrt, "LK_UNLCK"), 1)
        os.close(fd)


def write_planning_control_atomic(
    run_dir: Path,
    planning: dict[str, Any],
    *,
    precondition: Optional[Callable[[], None]] = None,
) -> None:
    path = managed_path(run_dir, PLANNING_FILE)
    content = json.dumps(planning, indent=2, sort_keys=True) + "\n"
    fd, name = tempfile.mkstemp(prefix=".planning-control.json.", dir=run_dir)
    temp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        if precondition is not None:
            precondition()
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def validate_system_design_acceptance(
    run_dir: Path,
    anchor: dict[str, Any],
    effective: dict[str, Any],
    record: Any,
) -> None:
    if not isinstance(record, dict) or set(record) != PLANNING_ACCEPTANCE_FIELDS:
        raise ControlError("planning-control.json System Design acceptance is malformed")
    try:
        canonical_date(record.get("accepted"), "System Design acceptance date")
    except ControlError as exc:
        raise ControlError("planning-control.json System Design acceptance is malformed") from exc
    product = anchor.get("product_closure")
    expected_source = (
        {
            "kind": "product_closure",
            "artifact": "20-prd.md",
            "version": product["version"],
            "sha256": product["sha256"],
        }
        if isinstance(product, dict)
        else {
            "kind": "stage0",
            "artifact": "run.yaml",
            "sha256": anchor["base_run_sha256"],
            "effective_config_hash": anchor["effective_config_hash"],
            "effective_config_revision": anchor["effective_config_revision"],
        }
    )
    if (
        type(record.get("candidate_version")) is not int
        or record["candidate_version"] != 1
        or not re.fullmatch(r"[0-9a-f]{64}", str(record.get("candidate_sha256", "")))
        or record.get("authority") not in {"HUMAN", "AGENT_REVIEW"}
        or record.get("source_bindings") != [expected_source]
        or record.get("repository_baselines") != []
    ):
        raise ControlError("planning-control.json System Design acceptance is malformed")
    policy = effective.get("gates", {}).get("system_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    if configured == "HUMAN":
        if (
            record["authority"] != "HUMAN"
            or record.get("review_reference") is not None
            or record.get("review_sha256") is not None
        ):
            raise ControlError("planning-control.json System Design acceptance is malformed")
    elif configured in {"AGENT_REVIEW", "HUMAN_IF_CHANGED"}:
        _, review_sha256, mapped = load_system_design_review(
            run_dir,
            effective,
            record["candidate_version"],
            record["candidate_sha256"],
            record.get("review_reference"),
        )
        if record["authority"] != mapped or record.get("review_sha256") != review_sha256:
            raise ControlError("planning-control.json System Design acceptance evidence is not current")
    else:
        raise ControlError("planning-control.json System Design acceptance uses an unsupported policy")


def load_planning_control(run_dir: Path) -> dict[str, Any]:
    path = managed_path(run_dir, PLANNING_FILE)
    try:
        planning = load_json(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControlError("planning-control.json is not valid JSON") from exc
    if not isinstance(planning, dict) or set(planning) != PLANNING_FIELDS:
        raise ControlError("planning-control.json fields do not match version-1 schema")
    anchor = planning.get("stage0_anchor")
    gates = planning.get("gates")
    acceptances = planning.get("acceptances")
    if not isinstance(anchor, dict) or set(anchor) != STAGE0_ANCHOR_FIELDS:
        raise ControlError("planning-control.json Stage 0 anchor is malformed")
    if (
        not re.fullmatch(r"[0-9a-f]{64}", str(anchor.get("control_sha256", "")))
        or not isinstance(anchor.get("control_revision"), int)
        or isinstance(anchor.get("control_revision"), bool)
        or anchor["control_revision"] < 1
        or not re.fullmatch(r"[0-9a-f]{64}", str(anchor.get("base_run_sha256", "")))
        or not re.fullmatch(r"[0-9a-f]{64}", str(anchor.get("effective_config_hash", "")))
        or not isinstance(anchor.get("effective_config_revision"), int)
        or isinstance(anchor.get("effective_config_revision"), bool)
        or anchor["effective_config_revision"] < 0
    ):
        raise ControlError("planning-control.json Stage 0 anchor is malformed")
    for relative, field in (("run.yaml", "base_run_sha256"), ("control.json", "control_sha256")):
        source_path = managed_path(run_dir, relative)
        if not source_path.is_file() or file_sha256(source_path) != anchor[field]:
            raise ControlError(f"planning-control.json Stage 0 provenance no longer matches {relative}")
    if (
        not isinstance(gates, dict)
        or set(gates) != set(DOWNSTREAM_STAGES)
        or any(value not in {"PENDING", "NOT_REQUIRED", "HUMAN_APPROVED", "AGENT_APPROVED"} for value in gates.values())
        or not isinstance(acceptances, dict)
        or set(acceptances) != set(DOWNSTREAM_STAGES)
    ):
        raise ControlError("planning-control.json gates or acceptances are malformed")
    product_closure = anchor.get("product_closure")
    if product_closure is not None and (
        not isinstance(product_closure, dict)
        or set(product_closure) != PRODUCT_CLOSURE_FIELDS
        or not isinstance(product_closure.get("version"), int)
        or isinstance(product_closure.get("version"), bool)
        or product_closure["version"] < 1
        or not re.fullmatch(r"[0-9a-f]{64}", str(product_closure.get("sha256", "")))
    ):
        raise ControlError("planning-control.json product-closure anchor is malformed")
    _, effective = verified_state(run_dir)
    validate_run(effective)
    selected = {stage for stage in DOWNSTREAM_STAGES if stage in effective["stages"]}
    if any((stage in selected) != (gates[stage] != "NOT_REQUIRED") for stage in DOWNSTREAM_STAGES):
        raise ControlError("planning-control.json gates do not match selected downstream stages")

    approved_stages: list[str] = []
    for stage in DOWNSTREAM_STAGES:
        record = acceptances[stage]
        approved = gates[stage] in {"HUMAN_APPROVED", "AGENT_APPROVED"}
        if approved != (record is not None):
            raise ControlError("planning-control.json gate/acceptance coherence is invalid")
        if record is not None:
            if stage != "system_design":
                raise ControlError("planning-control.json contains an unsupported downstream acceptance")
            validate_system_design_acceptance(run_dir, anchor, effective, record)
            expected_gate = (
                "HUMAN_APPROVED" if record["authority"] == "HUMAN" else "AGENT_APPROVED"
            )
            if gates[stage] != expected_gate:
                raise ControlError("planning-control.json gate label does not match acceptance authority")
            approved_stages.append(stage)

    record = acceptances["system_design"]
    if record is not None:
        candidate_path = managed_path(run_dir, SYSTEM_DESIGN_FILE)
        if not candidate_path.is_file() or file_sha256(candidate_path) != record["candidate_sha256"]:
            raise ControlError("accepted System Design candidate bytes no longer match recorded provenance")
        if product_closure is not None:
            product_path = managed_path(run_dir, "20-prd.md")
            if not product_path.is_file() or file_sha256(product_path) != product_closure["sha256"]:
                raise ControlError("accepted System Design product source no longer matches recorded provenance")
        if effective.get("system_design_participation") == "co_design":
            try:
                verify_system_design_board(run_dir)
            except (OSError, SystemExit, UnicodeError) as exc:
                raise ControlError(f"accepted co-design board projection is not current: {exc}") from exc

    pending = [stage for stage in DOWNSTREAM_STAGES if gates[stage] == "PENDING"]
    if (
        type(planning.get("version")) is not int
        or planning.get("version") != 1
        or not isinstance(planning.get("run"), str)
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", planning["run"])
        or planning["run"] != effective["run"]
        or planning.get("status") != "PLANNING"
        or not pending
        or planning.get("phase") != pending[0]
        or type(planning.get("revision")) is not int
        or planning["revision"] != 1 + len(approved_stages)
        or planning.get("blocked_reason") is not None
    ):
        raise ControlError("planning-control.json values are not a coherent current planning state")
    return planning


def validate_basic_policy(policy: Any, stage: str, allowed: set[str]) -> None:
    if not isinstance(policy, dict) or set(policy) != {"authority"} or policy.get("authority") not in allowed:
        raise ControlError(f"{stage} gate policy is incomplete or uses an illegal authority")


def validate_system_design_policy(policy: Any) -> None:
    if isinstance(policy, dict) and policy.get("authority") in {"HUMAN", "AGENT_REVIEW"}:
        validate_basic_policy(policy, "system_design", {"HUMAN", "AGENT_REVIEW"})
        return
    if not isinstance(policy, dict) or set(policy) != {"authority", "material_dimensions", "otherwise"}:
        raise ControlError("system_design gate policy is incomplete or uses an illegal authority")
    dimensions = policy.get("material_dimensions")
    if (
        policy.get("authority") != "HUMAN_IF_CHANGED"
        or policy.get("otherwise") != "AGENT_REVIEW"
        or not isinstance(dimensions, list)
        or dimensions != list(SYSTEM_DESIGN_DIMENSIONS)
    ):
        raise ControlError("system_design HUMAN_IF_CHANGED requires the exact seven material_dimensions and AGENT_REVIEW otherwise")


def validate_tickets_policy(policy: Any) -> None:
    if isinstance(policy, dict) and policy.get("authority") in {"HUMAN", "AGENT_REVIEW"}:
        validate_basic_policy(policy, "tickets", {"HUMAN", "AGENT_REVIEW"})
        return
    if not isinstance(policy, dict) or set(policy) != {"authority", "conditions", "otherwise"}:
        raise ControlError("tickets gate policy is incomplete or uses an illegal authority")
    conditions = policy.get("conditions")
    outcomes = {"HUMAN", "AGENT_REVIEW"}
    if (
        policy.get("authority") != "CONDITIONAL"
        or policy.get("otherwise") not in outcomes
        or not isinstance(conditions, list)
        or not conditions
        or any(
            not isinstance(item, dict)
            or set(item) != {"when", "then"}
            or not isinstance(item.get("when"), str)
            or not item["when"].strip()
            or item.get("then") not in outcomes
            for item in conditions
        )
    ):
        raise ControlError("tickets CONDITIONAL requires complete ordered conditions and otherwise")


def validate_downstream_policies(effective: dict[str, Any]) -> None:
    stages = effective["stages"]
    gates = effective["gates"]
    for stage in DOWNSTREAM_STAGES:
        selected = stage in stages
        if selected != (stage in gates):
            raise ControlError(f"{stage} gate must exist exactly when the stage is selected")
        if not selected:
            continue
        if stage == "system_design":
            validate_system_design_policy(gates[stage])
        elif stage == "program_design":
            validate_basic_policy(gates[stage], stage, {"HUMAN", "AGENT_REVIEW"})
        else:
            validate_tickets_policy(gates[stage])


def validate_downstream_order(stages: list[str]) -> list[str]:
    selected = [stage for stage in stages if stage in DOWNSTREAM_STAGES]
    expected = [stage for stage in DOWNSTREAM_STAGES if stage in selected]
    if selected != expected:
        raise ControlError("selected downstream stages are not in system_design, program_design, tickets order")
    if "execute" in stages:
        execute_index = stages.index("execute")
        if "tickets" not in selected or stages.index("tickets") > execute_index:
            raise ControlError("tickets must be selected before execute")
        if any(stages.index(stage) > execute_index for stage in selected):
            raise ControlError("all selected downstream planning boundaries must precede execute")
    return selected


def initialize_planning(run_dir: Path) -> str:
    if managed_path(run_dir, PLANNING_FILE).exists():
        raise ControlError("planning-control.json already exists")
    control, effective = verified_state(run_dir)
    validate_run(effective)
    stages = effective["stages"]
    if effective.get("version") == 1 and "system_design" in stages:
        raise ControlError("version-1 System Design run lacks explicit participation provenance")
    validate_downstream_policies(effective)
    selected = validate_downstream_order(stages)
    if not selected:
        raise ControlError("run selects no downstream planning boundary")
    if control.get("phase") != selected[0]:
        raise ControlError("Stage 0 control has not handed off at the earliest selected downstream boundary")
    discovery_selected = "discovery" in stages
    product_closure = None
    if discovery_selected:
        acceptance = control.get("acceptances", {}).get("discovery")
        if not isinstance(acceptance, dict):
            raise ControlError("selected discovery lacks accepted product-closure provenance")
        product_closure = {
            "version": acceptance["candidate_version"],
            "sha256": acceptance["candidate_sha256"],
        }
    planning = {
        "version": 1,
        "run": effective["run"],
        "status": "PLANNING",
        "phase": selected[0],
        "revision": 1,
        "stage0_anchor": {
            "control_sha256": file_sha256(managed_path(run_dir, "control.json")),
            "control_revision": control["revision"],
            "base_run_sha256": control["base_run_sha256"],
            "effective_config_hash": control["effective_config_hash"],
            "effective_config_revision": control["effective_config_revision"],
            "product_closure": product_closure,
        },
        "gates": {
            stage: "PENDING" if stage in selected else "NOT_REQUIRED"
            for stage in DOWNSTREAM_STAGES
        },
        "acceptances": {stage: None for stage in DOWNSTREAM_STAGES},
        "blocked_reason": None,
    }
    write_planning_control_atomic(run_dir, planning)
    load_planning_control(run_dir)
    return "initialized planning-control.json revision 1"


def current_stage0_anchor(run_dir: Path, control: dict[str, Any], effective: dict[str, Any]) -> dict[str, Any]:
    product_closure = None
    if "discovery" in effective["stages"]:
        acceptance = control.get("acceptances", {}).get("discovery")
        if not isinstance(acceptance, dict):
            raise ControlError("selected discovery lacks accepted product-closure provenance")
        product_closure = {
            "version": acceptance["candidate_version"],
            "sha256": acceptance["candidate_sha256"],
        }
    return {
        "control_sha256": file_sha256(managed_path(run_dir, "control.json")),
        "control_revision": control["revision"],
        "base_run_sha256": control["base_run_sha256"],
        "effective_config_hash": control["effective_config_hash"],
        "effective_config_revision": control["effective_config_revision"],
        "product_closure": product_closure,
    }


def verified_planning_state(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    control, effective = verified_state(run_dir)
    validate_run(effective)
    validate_downstream_policies(effective)
    selected_order = validate_downstream_order(effective["stages"])
    if not selected_order:
        raise ControlError("run selects no downstream planning boundary")
    if control.get("phase") != selected_order[0]:
        raise ControlError("Stage 0 control does not preserve the earliest downstream handoff")
    planning = load_planning_control(run_dir)
    if planning["run"] != effective["run"]:
        raise ControlError("planning-control.json run identity does not match frozen intake")
    selected = {stage for stage in DOWNSTREAM_STAGES if stage in effective["stages"]}
    for stage in DOWNSTREAM_STAGES:
        if (stage in selected) == (planning["gates"][stage] == "NOT_REQUIRED"):
            raise ControlError("planning-control.json gates do not match selected downstream stages")
    if planning["stage0_anchor"] != current_stage0_anchor(run_dir, control, effective):
        raise ControlError("planning-control.json Stage 0 anchor no longer matches the frozen handoff")
    return planning, control, effective


def ensure_planning(run_dir: Path) -> str:
    if not managed_path(run_dir, PLANNING_FILE).exists():
        return initialize_planning(run_dir)
    planning, _, _ = verified_planning_state(run_dir)
    return (
        f"planning-control.json already initialized at {planning['phase']}; "
        f"revision {planning['revision']}"
    )


def system_design_report(
    run_dir: Path,
    planning: dict[str, Any],
    effective: dict[str, Any],
) -> dict[str, Any]:
    gaps: list[dict[str, str]] = []
    report: dict[str, Any] = {
        "version": 1,
        "run": planning["run"],
        "verdict": "BLOCKED",
        "stage": "system_design",
        "boundary": "system_design",
        "gaps": gaps,
    }
    if planning["phase"] != "system_design" or planning["gates"]["system_design"] != "PENDING":
        gaps.append(gap(
            PLANNING_FILE,
            "system_design is not the current pending planning boundary",
            "system_design",
            "resume the current planning-control phase",
        ))
    try:
        path = managed_path(run_dir, SYSTEM_DESIGN_FILE)
    except ControlError as exc:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            str(exc),
            "system_design",
            "replace the candidate with a real run-local file",
        ))
        return report
    if not path.is_file():
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "candidate file is missing",
            "system_design",
            f"produce {SYSTEM_DESIGN_FILE}",
        ))
        return report
    report["candidate_sha256"] = file_sha256(path)
    try:
        frontmatter, body = read_frontmatter(path)
    except (ControlError, yaml.YAMLError, UnicodeError) as exc:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            str(exc),
            "system_design",
            "repair candidate frontmatter",
        ))
        return report
    candidate_version = frontmatter.get("version")
    if type(candidate_version) is int:
        report["candidate_version"] = candidate_version
    if set(frontmatter) != SYSTEM_DESIGN_FIELDS:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "candidate frontmatter does not match its exact schema",
            "system_design",
            "repair candidate frontmatter",
        ))
    if frontmatter.get("run") != planning["run"]:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "candidate run identity does not match planning-control.json",
            "system_design",
            "bind the candidate to this run",
        ))
    if type(frontmatter.get("version")) is not int or frontmatter.get("version") != 1:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "candidate version must equal integer 1",
            "system_design",
            "write candidate version 1",
        ))
    if frontmatter.get("status") != "draft":
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "producer candidate status must remain draft",
            "system_design",
            "record readiness without acceptance",
        ))
    if frontmatter.get("gate_ready") is not True:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "producer has not recorded gate readiness",
            "system_design",
            "finish the candidate and set gate_ready true",
        ))
    if frontmatter.get("participation") != effective.get("system_design_participation"):
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "candidate participation does not match frozen run.yaml",
            "system_design",
            "copy the frozen System Design participation without re-asking",
        ))
    if effective.get("system_design_participation") == "co_design":
        try:
            verify_system_design_board(run_dir)
        except (OSError, SystemExit, UnicodeError) as exc:
            gaps.append(gap(
                "30-system-design.html",
                f"30-system-design.html board verification failed: {exc}",
                "system_design",
                "regenerate the board from the reserved System Design draft and rerun the check",
            ))
    try:
        candidate_opened = canonical_date(frontmatter.get("opened"), "candidate opened")
        intake_opened = canonical_date(effective.get("opened"), "intake opened")
    except ControlError:
        candidate_opened = intake_opened = None
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "candidate opened date is not canonical YYYY-MM-DD",
            "system_design",
            "copy the canonical intake opened date",
        ))
    if candidate_opened is not None and candidate_opened != intake_opened:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "candidate opened date differs from frozen intake",
            "system_design",
            "copy the intake opened date",
        ))

    headings = tuple(re.findall(r"(?m)^## ([^\n]+?)\s*$", body))
    if headings != SYSTEM_DESIGN_SECTIONS:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "System Design section sequence does not match the exact Stage 3 shape",
            "system_design",
            "restore each required System Design section exactly once and in order",
        ))

    source = frontmatter.get("source_binding")
    source_valid = False
    product = planning["stage0_anchor"]["product_closure"]
    if product is not None:
        expected = {
            "kind": "product_closure",
            "artifact": "20-prd.md",
            "version": product["version"],
            "sha256": product["sha256"],
        }
        if not isinstance(source, dict) or set(source) != PRODUCT_SOURCE_FIELDS or source != expected:
            gaps.append(gap(
                SYSTEM_DESIGN_FILE,
                "source_binding does not match the exact accepted product closure",
                "system_design",
                "bind source_binding to the accepted 20-prd.md version and sha256",
            ))
        else:
            source_valid = True
    else:
        anchor = planning["stage0_anchor"]
        expected = {
            "kind": "stage0",
            "artifact": "run.yaml",
            "sha256": anchor["base_run_sha256"],
            "effective_config_hash": anchor["effective_config_hash"],
            "effective_config_revision": anchor["effective_config_revision"],
        }
        if not isinstance(source, dict) or set(source) != STAGE0_SOURCE_FIELDS or source != expected:
            gaps.append(gap(
                SYSTEM_DESIGN_FILE,
                "source_binding does not match the exact frozen Stage 0 admission",
                "system_design",
                "bind source_binding to run.yaml and the effective configuration",
            ))
        else:
            source_valid = True
    report["source_binding"] = source if source_valid else None
    report["verdict"] = "PASS" if not gaps else "BLOCKED"
    return report


def check_boundary(run_dir: Path, stage: str) -> dict[str, Any]:
    if stage != "system_design":
        raise ControlError("Slice 1 supports only --stage system_design")
    planning, _, effective = verified_planning_state(run_dir)
    return system_design_report(run_dir, planning, effective)


def resolve_system_design_authority(
    run_dir: Path,
    effective: dict[str, Any],
    candidate_version: int,
    candidate_sha256: str,
    approval: Optional[str],
    review_reference: Optional[str],
) -> tuple[str, Optional[str]]:
    policy = effective.get("gates", {}).get("system_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    if configured == "HUMAN":
        if review_reference is not None:
            raise ControlError("configured HUMAN System Design gate does not accept --review")
        if approval != "human":
            raise ControlError("HUMAN System Design gate requires explicit --approval human")
        return "HUMAN", None
    if configured in {"AGENT_REVIEW", "HUMAN_IF_CHANGED"}:
        _, review_sha256, mapped = load_system_design_review(
            run_dir, effective, candidate_version, candidate_sha256, review_reference
        )
        if mapped == "AGENT_REVIEW":
            if approval is not None:
                raise ControlError(f"configured {configured} System Design gate does not fall back to human approval")
        elif approval != "human":
            raise ControlError("HUMAN_IF_CHANGED mapped HUMAN requires explicit --approval human")
        return mapped, review_sha256
    raise ControlError(f"system_design authority {configured} is an intentionally unimplemented Slice-2B capability")


def advance_boundary(
    run_dir: Path,
    stage: str,
    approval: Optional[str],
    review_reference: Optional[str],
    accepted: str,
) -> str:
    if stage != "system_design":
        raise ControlError("Slice 2B supports only system_design acceptance")
    planning, _, effective = verified_planning_state(run_dir)
    participation = effective.get("system_design_participation")
    if participation not in {"agent_led", "co_design"}:
        raise ControlError(f"unsupported frozen System Design participation: {participation}")
    report = system_design_report(run_dir, planning, effective)
    if report["verdict"] != "PASS":
        raise ControlError("mechanical system_design boundary check is BLOCKED")
    accepted = canonical_date(accepted, "acceptance date")
    candidate_version: int = report["candidate_version"]
    candidate_sha256: str = report["candidate_sha256"]
    source_binding = report["source_binding"]
    authority, review_sha256 = resolve_system_design_authority(
        run_dir,
        effective,
        candidate_version,
        candidate_sha256,
        approval,
        review_reference,
    )

    final_report = system_design_report(run_dir, planning, effective)
    if (
        final_report.get("verdict") != "PASS"
        or final_report.get("candidate_version") != candidate_version
        or final_report.get("candidate_sha256") != candidate_sha256
        or final_report.get("source_binding") != source_binding
    ):
        raise ControlError("candidate or source binding changed before System Design acceptance")
    try:
        final_planning, _, final_effective = verified_planning_state(run_dir)
        final_authority = resolve_system_design_authority(
            run_dir,
            final_effective,
            candidate_version,
            candidate_sha256,
            approval,
            review_reference,
        )
    except ControlError as exc:
        raise ControlError("candidate, source binding, policy, or review changed before System Design acceptance") from exc
    if final_planning != planning or final_authority != (authority, review_sha256):
        raise ControlError("planning-control.json, policy, or review changed before System Design acceptance")

    selected = [item for item in DOWNSTREAM_STAGES if item in final_effective["stages"]]
    index = selected.index("system_design")
    if index + 1 >= len(selected):
        raise ControlError("system_design has no selected downstream boundary")
    next_stage = selected[index + 1]

    def revalidate_immediately_before_replace() -> None:
        current_planning, _, current_effective = verified_planning_state(run_dir)
        current_report = system_design_report(run_dir, current_planning, current_effective)
        current_authority = resolve_system_design_authority(
            run_dir,
            current_effective,
            candidate_version,
            candidate_sha256,
            approval,
            review_reference,
        )
        if (
            current_planning != planning
            or current_report.get("verdict") != "PASS"
            or current_report.get("candidate_version") != candidate_version
            or current_report.get("candidate_sha256") != candidate_sha256
            or current_report.get("source_binding") != source_binding
            or current_authority != (authority, review_sha256)
        ):
            raise ControlError("candidate, source binding, policy, or review changed at the System Design write boundary")

    final_planning["acceptances"]["system_design"] = {
        "candidate_version": candidate_version,
        "candidate_sha256": candidate_sha256,
        "authority": authority,
        "accepted": accepted,
        "review_reference": review_reference,
        "review_sha256": review_sha256,
        "source_bindings": [source_binding],
        "repository_baselines": [],
    }
    final_planning["gates"]["system_design"] = (
        "HUMAN_APPROVED" if authority == "HUMAN" else "AGENT_APPROVED"
    )
    final_planning["phase"] = next_stage
    final_planning["revision"] += 1
    write_planning_control_atomic(
        run_dir,
        final_planning,
        precondition=revalidate_immediately_before_replace,
    )
    load_planning_control(run_dir)
    return f"advanced system_design -> {next_stage}; planning-control revision {final_planning['revision']}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    initialize = sub.add_parser("initialize")
    initialize.add_argument("--run", required=True, type=Path)
    ensure = sub.add_parser("ensure")
    ensure.add_argument("--run", required=True, type=Path)
    inspect = sub.add_parser("check")
    inspect.add_argument("--run", required=True, type=Path)
    inspect.add_argument("--stage", required=True, choices=("system_design",))
    advance = sub.add_parser("advance")
    advance.add_argument("--run", required=True, type=Path)
    advance.add_argument("--stage", required=True, choices=("system_design",))
    advance.add_argument("--approval", choices=("human",))
    advance.add_argument("--review")
    advance.add_argument("--date", required=True)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run_dir = resolve_existing_run_directory(args.run)
        if args.command == "check":
            report = check_boundary(run_dir, args.stage)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["verdict"] == "PASS" else 1
        with planning_lock(run_dir):
            if args.command == "initialize":
                print(initialize_planning(run_dir))
            elif args.command == "ensure":
                print(ensure_planning(run_dir))
            elif args.command == "advance":
                print(advance_boundary(run_dir, args.stage, args.approval, args.review, args.date))
            else:  # pragma: no cover
                return 2
        return 0
    except (ControlError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"atlas-planning: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
