#!/usr/bin/env python3
"""Deterministic controller for Atlas downstream planning state."""
from __future__ import annotations

import argparse
import copy
import contextlib
import hashlib
import json
import os
import re
import secrets
import stat
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Callable, Iterator, Optional

import yaml
from markdown_it import MarkdownIt

import atlas_repository
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


SECURE_DIR_FD_EVIDENCE_INSTALL = all(
    function in os.supports_dir_fd for function in (os.open, os.unlink, os.link)
)


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
PROGRAM_DESIGN_FILE = "40-program-design.md"
TICKET_GRAPH_FILE = "50-ticket-graph.json"
CURRENT_TICKET_GRAPH_VERSION = 2
SYSTEM_DESIGN_FIELDS = {
    "run", "version", "status", "gate_ready", "participation", "opened", "source_binding",
}
PROGRAM_DESIGN_FIELDS = {
    "run", "version", "status", "gate_ready", "opened", "source_binding",
}
TICKET_GRAPH_FIELDS = {
    "version", "run", "status", "gate_ready", "source_bindings",
    "repository_baselines", "preferred_order", "tracer_ticket", "tickets",
}
TICKET_GRAPH_ENTRY_FIELDS = {"id", "path", "sha256"}
TICKET_FIELDS = {
    "id", "kind", "status", "repository", "blocked_by", "tracer", "enabling",
    "context", "external_prerequisites", "validators", "outcomes", "reviews",
}
TICKET_DEPENDENCY_FIELDS = {"ticket", "establishes"}
TICKET_CONTEXT_FIELDS = {"sources"}
TICKET_CONTEXT_SOURCE_FIELDS = {"kind", "sections", "purpose"}
TICKET_VALIDATOR_FIELDS = {"id", "command", "success"}
TICKET_OUTCOME_FIELDS = {"id", "promise", "acceptance", "validator_ids"}
TICKET_ENABLING_FIELDS = {"consumer", "rationale"}
TICKET_EXTERNAL_FIELDS = {"id", "condition", "satisfaction"}
TICKET_COMMAND_SATISFACTION_FIELDS = {"kind", "command", "success"}
TICKET_HUMAN_SATISFACTION_FIELDS = {"kind", "authority", "statement", "provenance"}
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
PROGRAM_DESIGN_SECTIONS = (
    "Repository grounding",
    "Upstream commitment realization",
    "File-tree diff",
    "Types and boundary signatures",
    "Call and data flow",
    "State, locking, concurrency, and lifetime",
    "Migration and local failure-path implementation",
    "Test seams and validation plan",
    "Least-confident decisions",
    "Implementation constraints and sequencing",
)
SYSTEM_DESIGN_REVIEW_REFERENCE = "reviews/system-design-v1.json"
PROGRAM_DESIGN_REVIEW_REFERENCE = "reviews/program-design-v1.json"
TICKET_GRAPH_REVIEW_REFERENCE = "reviews/ticket-graph-v1.json"
UPSTREAM_BLOCK_REVIEW_REFERENCE = "reviews/program-design-upstream-block-v1.json"
SYSTEM_DESIGN_REVIEW_FIELDS = {
    "version", "run", "stage", "policy", "candidate_version", "candidate_sha256",
    "repository_baselines", "materiality", "semantic_review",
}
SYSTEM_DESIGN_REPAIR_REVIEW_FIELDS = SYSTEM_DESIGN_REVIEW_FIELDS | {"repair_context"}
SYSTEM_REPAIR_CONTEXT_FIELDS = {
    "episode_started_from_revision", "superseded_system_design",
    "contradiction_review_reference", "contradiction_review_sha256",
    "contradiction_finding", "attempts_used", "acceptance_revision",
}
PROGRAM_DESIGN_REVIEW_FIELDS = {
    "version", "run", "stage", "policy", "candidate_version", "candidate_sha256",
    "repository_baselines", "semantic_review",
}
TICKET_GRAPH_REVIEW_FIELDS = {
    "version", "run", "stage", "policy", "candidate_version", "candidate_sha256",
    "source_bindings", "repository_baselines", "semantic_review",
}
UPSTREAM_BLOCK_REVIEW_FIELDS = {
    "version", "run", "stage", "planning_revision", "verdict",
    "system_design_acceptance", "repository_baselines", "finding", "review_evidence",
}
UPSTREAM_BLOCK_FINDING_FIELDS = {
    "code", "dimension", "problem", "upstream_source", "upstream_issue",
    "resume_boundary", "resume_action", "code_evidence",
}
CODE_EVIDENCE_FIELDS = {"repository", "baseline", "path", "evidence"}
REPAIR_EPISODE_FIELDS = {
    "kind", "state", "started_from_revision", "review_reference", "review_sha256",
    "superseded_system_design", "attempts_used", "current_attempt",
    "initial_program_candidate_sha256",
}
REPAIR_ATTEMPT_FIELDS = {"number", "stage", "candidate_sha256_before"}
SYSTEM_DESIGN_DIMENSIONS = (
    "responsibilities_and_system_seams",
    "authoritative_data_ownership",
    "cross_module_external_contracts_and_dependencies",
    "target_schema_protocol",
    "end_to_end_lifecycle_failure_recovery",
    "compatibility_guarantees",
    "trust_security_operational_commitments",
)
PROGRAM_DESIGN_DIMENSIONS = (
    "upstream_commitment_realization",
    "repository_grounding_and_feasibility",
    "files_packages_types_and_responsibilities",
    "signatures_call_and_data_flow",
    "state_locking_concurrency_and_lifetime",
    "migration_and_local_failure_path_implementation",
    "testability_and_compilation_readiness",
)
TICKET_GRAPH_DIMENSIONS = (
    "selected_path_applicability_and_no_redesign",
    "vertical_outcomes_and_required_boundaries",
    "enabling_ticket_justification",
    "dependency_truth_and_preferred_order",
    "external_readiness_and_design_blocking",
    "deterministic_behavior_proof",
    "execution_handoff_completeness",
)
SEMANTIC_REVIEW_FIELDS = {"verdict", "dimensions", "gaps"}
DIMENSION_REVIEW_FIELDS = {"dimension", "result", "evidence"}
SEMANTIC_GAP_FIELDS = {"code", "dimension", "problem", "resume_action"}
DESIGN_BLOCKED_GAP_FIELDS = {
    "code", "dimension", "problem", "upstream_source", "upstream_issue",
    "resume_boundary", "resume_action",
}
MATERIALITY_FIELDS = {"dimensions", "unavailable_reason"}


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def json_equal_exact(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, separators=(",", ":")) == json.dumps(
        right, sort_keys=True, separators=(",", ":")
    )


def is_intentional_system_revision(planning: dict[str, Any]) -> bool:
    gates = planning.get("gates")
    acceptances = planning.get("acceptances")
    if not isinstance(gates, dict) or not isinstance(acceptances, dict):
        return False
    return (
        planning.get("status") == "PLANNING"
        and planning.get("phase") == "system_design"
        and planning.get("blocked_reason") is None
        and gates.get("system_design") == "STALE"
        and isinstance(acceptances.get("system_design"), dict)
        and gates.get("program_design") == "PENDING"
        and acceptances.get("program_design") is None
        and gates.get("tickets") in {"PENDING", "NOT_REQUIRED"}
        and acceptances.get("tickets") is None
    )


def valid_repair_attempt(value: Any, attempts_used: Any, stage: str) -> bool:
    return (
        type(attempts_used) is int
        and isinstance(value, dict)
        and set(value) == REPAIR_ATTEMPT_FIELDS
        and type(value.get("number")) is int
        and value["number"] == attempts_used
        and value.get("stage") == stage
        and (
            value.get("candidate_sha256_before") is None
            or (
                type(value.get("candidate_sha256_before")) is str
                and re.fullmatch(r"[0-9a-f]{64}", value["candidate_sha256_before"]) is not None
            )
        )
    )


def contains_machine_local_path(value: Any) -> bool:
    if isinstance(value, str):
        without_https_urls = re.sub(
            r"\bhttps://[^\s\"'`<>]+",
            "",
            value,
            flags=re.IGNORECASE,
        )
        return bool(
            re.search(
                r"(?<![A-Za-z0-9+.-])[A-Za-z][A-Za-z0-9+.-]*:(?=[^\s\"'`<>])",
                without_https_urls,
            )
            or re.search(r"(?<!:)//[^/\s\"'`<>]+/[^\s\"'`<>]+", without_https_urls)
            or re.search(r"(?<![A-Za-z0-9_])/(?!/)[^\s\"'`<>]+", without_https_urls)
            or re.search(r"(?<!\\)\\\\[^\\\s]+\\[^\\\s]+", without_https_urls)
            or re.search(r"(?<![A-Za-z0-9])[A-Za-z]:", without_https_urls)
        )
    if isinstance(value, list):
        return any(contains_machine_local_path(item) for item in value)
    if isinstance(value, dict):
        return any(contains_machine_local_path(item) for item in value.values())
    return False


def markdown_h2_sections(body: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    lines = body.splitlines()
    tokens = MarkdownIt("commonmark").parse(body)
    headings = [
        (tokens[index + 1].content, token.map)
        for index, token in enumerate(tokens[:-1])
        if token.type == "heading_open"
        and token.tag == "h2"
        and tokens[index + 1].type == "inline"
        and token.map is not None
    ]
    sections = []
    for index, (name, line_map) in enumerate(headings):
        start = line_map[1]
        end = headings[index + 1][1][0] if index + 1 < len(headings) else len(lines)
        sections.append((
            name,
            tuple(line.strip() for line in lines[start:end] if line.strip()),
        ))
    return tuple(sections)


def markdown_h2_headings(body: str) -> tuple[str, ...]:
    return tuple(name for name, _ in markdown_h2_sections(body))


def program_design_headings(body: str) -> tuple[str, ...]:
    return markdown_h2_headings(body)


def expected_ticket_execution_context_lines(sources: list[dict[str, Any]]) -> tuple[str, ...]:
    lines = []
    for source in sources:
        sections = source["sections"]
        rendered_sections = (
            "; ".join(f"`{section}`" for section in sections)
            if sections
            else "none"
        )
        purpose = " ".join(source["purpose"].split())
        lines.append(
            f"- `{source['kind']}` — sections: {rendered_sections} — purpose: {purpose}"
        )
    return tuple(lines)


def ticket_execution_context_lines(body: str) -> tuple[str, ...]:
    matches = [
        lines
        for name, lines in markdown_h2_sections(body)
        if name == "Execution context"
    ]
    return matches[0] if len(matches) == 1 else ()


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


def expected_system_repair_context(
    run_dir: Path,
    planning: dict[str, Any],
    acceptance_revision: Optional[int],
) -> dict[str, Any]:
    episode = planning.get("blocked_reason")
    state = episode.get("state") if isinstance(episode, dict) else None
    if (
        not isinstance(episode, dict)
        or set(episode) != REPAIR_EPISODE_FIELDS
        or episode.get("kind") != "SYSTEM_DESIGN_REPAIR"
        or type(episode.get("started_from_revision")) is not int
        or episode.get("review_reference") != UPSTREAM_BLOCK_REVIEW_REFERENCE
        or not re.fullmatch(r"[0-9a-f]{64}", str(episode.get("review_sha256", "")))
        or not isinstance(episode.get("superseded_system_design"), dict)
        or type(episode.get("attempts_used")) is not int
    ):
        raise ControlError("System Design repair context requires the active stale episode")
    if state == "SYSTEM_DESIGN_STALE":
        expected_acceptance_revision = planning["revision"] + 1
        if (
            type(acceptance_revision) is not int
            or acceptance_revision != expected_acceptance_revision
        ):
            raise ControlError("System Design repair context requires the active stale episode")
        context_attempts = episode["attempts_used"]
        context_acceptance_revision = acceptance_revision
    elif state == "PROGRAM_DESIGN_RESUMED":
        system_acceptance = planning.get("acceptances", {}).get("system_design")
        if (
            not isinstance(system_acceptance, dict)
            or system_acceptance.get("review_reference") != SYSTEM_DESIGN_REVIEW_REFERENCE
            or type(system_acceptance.get("review_sha256")) is not str
        ):
            raise ControlError("accepted System Design repair evidence is unavailable")
        review_path = managed_path(run_dir, SYSTEM_DESIGN_REVIEW_REFERENCE)
        try:
            review_bytes = review_path.read_bytes()
            review = load_json(review_bytes.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ControlError("accepted System Design repair evidence is unavailable") from exc
        persisted_context = review.get("repair_context") if isinstance(review, dict) else None
        if (
            hashlib.sha256(review_bytes).hexdigest() != system_acceptance["review_sha256"]
            or not isinstance(persisted_context, dict)
            or set(persisted_context) != SYSTEM_REPAIR_CONTEXT_FIELDS
        ):
            raise ControlError("accepted System Design repair evidence is not current")
        context_attempts = persisted_context.get("attempts_used")
        context_acceptance_revision = persisted_context.get("acceptance_revision")
        if (
            type(context_attempts) is not int
            or not 1 <= context_attempts <= episode["attempts_used"]
            or type(context_acceptance_revision) is not int
            or context_acceptance_revision
            != episode["started_from_revision"] + 2 + context_attempts
        ):
            raise ControlError("accepted System Design repair context is incoherent")
    else:
        raise ControlError("System Design repair context requires an active repair episode")
    contradiction_path = managed_path(run_dir, episode["review_reference"])
    try:
        contradiction_bytes = contradiction_path.read_bytes()
        contradiction = load_json(contradiction_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ControlError("System Design repair contradiction evidence is unavailable") from exc
    if (
        hashlib.sha256(contradiction_bytes).hexdigest() != episode["review_sha256"]
        or not isinstance(contradiction, dict)
        or not isinstance(contradiction.get("finding"), dict)
        or not json_equal_exact(
            contradiction.get("system_design_acceptance"),
            episode["superseded_system_design"],
        )
    ):
        raise ControlError("System Design repair contradiction evidence is not current")
    return {
        "episode_started_from_revision": episode["started_from_revision"],
        "superseded_system_design": copy.deepcopy(episode["superseded_system_design"]),
        "contradiction_review_reference": episode["review_reference"],
        "contradiction_review_sha256": episode["review_sha256"],
        "contradiction_finding": copy.deepcopy(contradiction["finding"]),
        "attempts_used": context_attempts,
        "acceptance_revision": context_acceptance_revision,
    }


def persisted_system_repair_context(
    run_dir: Path,
    planning: dict[str, Any],
    effective: dict[str, Any],
) -> Optional[dict[str, Any]]:
    current = planning.get("acceptances", {}).get("system_design")
    if not isinstance(current, dict) or current.get("candidate_version") == 1:
        return None
    review_reference = current.get("review_reference")
    review_sha256 = current.get("review_sha256")
    if review_reference is None and review_sha256 is None:
        return None
    if review_reference != SYSTEM_DESIGN_REVIEW_REFERENCE or type(review_sha256) is not str:
        raise ControlError("accepted System Design repair evidence is unavailable")
    review_path = managed_path(run_dir, SYSTEM_DESIGN_REVIEW_REFERENCE)
    try:
        review_bytes = review_path.read_bytes()
        review = load_json(review_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ControlError("accepted System Design repair evidence is unavailable") from exc
    if hashlib.sha256(review_bytes).hexdigest() != review_sha256 or not isinstance(review, dict):
        raise ControlError("accepted System Design repair evidence is not current")
    if "repair_context" not in review:
        return None
    context = review.get("repair_context")
    if not isinstance(context, dict) or set(context) != SYSTEM_REPAIR_CONTEXT_FIELDS:
        raise ControlError("accepted System Design repair evidence is not current")
    predecessor = context.get("superseded_system_design")
    attempts = context.get("attempts_used")
    started = context.get("episode_started_from_revision")
    acceptance_revision = context.get("acceptance_revision")
    if (
        not isinstance(predecessor, dict)
        or set(predecessor) != PLANNING_ACCEPTANCE_FIELDS
        or type(predecessor.get("candidate_version")) is not int
        or context.get("contradiction_review_reference") != UPSTREAM_BLOCK_REVIEW_REFERENCE
        or type(attempts) is not int
        or not 1 <= attempts <= 4
        or type(started) is not int
        or type(acceptance_revision) is not int
        or acceptance_revision != started + 2 + attempts
        or current.get("candidate_version") != predecessor.get("candidate_version", 0) + 1
        or current.get("candidate_sha256") == predecessor.get("candidate_sha256")
        or not json_equal_exact(current.get("source_bindings"), predecessor.get("source_bindings"))
    ):
        raise ControlError("accepted System Design repair context is incoherent")
    validate_system_design_acceptance(
        run_dir, planning["stage0_anchor"], effective, predecessor, historical=True
    )
    contradiction_path = managed_path(run_dir, str(context.get("contradiction_review_reference")))
    try:
        contradiction_bytes = contradiction_path.read_bytes()
        contradiction = load_json(contradiction_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ControlError("accepted System Design repair contradiction evidence is unavailable") from exc
    if hashlib.sha256(contradiction_bytes).hexdigest() != context.get("contradiction_review_sha256"):
        raise ControlError("accepted System Design repair contradiction evidence is not current")
    validate_upstream_block_review(
        contradiction,
        run=planning["run"],
        planning_revision=started,
        system_acceptance=predecessor,
        effective=effective,
        repository_verification=None,
    )
    if (
        contradiction.get("verdict") != "CONFIRMED_UPSTREAM_CONTRADICTION"
        or not json_equal_exact(contradiction.get("finding"), context.get("contradiction_finding"))
    ):
        raise ControlError("accepted System Design repair contradiction evidence is not confirmed")
    return context


def load_system_design_review(
    run_dir: Path,
    effective: dict[str, Any],
    candidate_version: int,
    candidate_sha256: str,
    review_reference: Any,
    repair_context: Optional[dict[str, Any]] = None,
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
    expected_fields = (
        SYSTEM_DESIGN_REPAIR_REVIEW_FIELDS
        if repair_context is not None
        else SYSTEM_DESIGN_REVIEW_FIELDS
    )
    if not isinstance(envelope, dict) or set(envelope) != expected_fields:
        raise ControlError("System Design review envelope does not match its exact schema")
    policy = effective.get("gates", {}).get("system_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    if (
        type(envelope.get("version")) is not int
        or envelope.get("version") != 1
        or envelope.get("run") != effective["run"]
        or envelope.get("stage") != "system_design"
        or envelope.get("policy") != configured
        or configured not in ({"HUMAN", "AGENT_REVIEW", "HUMAN_IF_CHANGED"} if repair_context is not None else {"AGENT_REVIEW", "HUMAN_IF_CHANGED"})
        or type(envelope.get("candidate_version")) is not int
        or envelope.get("candidate_version") != candidate_version
        or envelope.get("candidate_sha256") != candidate_sha256
        or envelope.get("repository_baselines") != effective["repos"]
    ):
        raise ControlError("System Design review evidence does not match current policy, candidate, or baselines")
    if repair_context is not None and (
        not isinstance(envelope.get("repair_context"), dict)
        or set(envelope["repair_context"]) != SYSTEM_REPAIR_CONTEXT_FIELDS
        or not json_equal_exact(envelope["repair_context"], repair_context)
    ):
        raise ControlError("System Design review repair_context does not match the active episode")
    if configured == "HUMAN":
        if envelope.get("materiality") is not None or envelope.get("semantic_review") is not None:
            raise ControlError("direct HUMAN repair evidence requires null review judgments")
        mapped = "HUMAN"
    elif configured == "AGENT_REVIEW":
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


def validate_program_design_semantic_review(review: Any, source_kind: str) -> None:
    if not isinstance(review, dict) or set(review) != SEMANTIC_REVIEW_FIELDS:
        raise ControlError("Program Design semantic_review does not match its exact schema")
    verdict = review.get("verdict")
    rows = review.get("dimensions")
    gaps = review.get("gaps")
    if verdict not in {"PASS", "BLOCKED", "DESIGN_BLOCKED"} or not isinstance(rows, list) or not isinstance(gaps, list):
        raise ControlError("Program Design semantic_review is malformed")
    if (
        len(rows) != len(PROGRAM_DESIGN_DIMENSIONS)
        or any(not isinstance(row, dict) or set(row) != DIMENSION_REVIEW_FIELDS for row in rows)
        or any(row.get("dimension") not in PROGRAM_DESIGN_DIMENSIONS for row in rows)
        or len({row.get("dimension") for row in rows}) != len(PROGRAM_DESIGN_DIMENSIONS)
        or any(row.get("result") not in {"PASS", "BLOCKED", "DESIGN_BLOCKED"} for row in rows)
        or any(not nonempty_string(row.get("evidence")) for row in rows)
    ):
        raise ControlError("Program Design semantic_review must cover the exact seven Stage 4 dimensions")
    results = {row["dimension"]: row["result"] for row in rows}
    expected_verdict = (
        "DESIGN_BLOCKED"
        if "DESIGN_BLOCKED" in results.values()
        else "BLOCKED"
        if "BLOCKED" in results.values()
        else "PASS"
    )
    if verdict != expected_verdict:
        raise ControlError("Program Design verdict must be derived from its dimension rows")
    nonpass = {dimension for dimension, result in results.items() if result != "PASS"}
    if len(gaps) != len(nonpass) or {item.get("dimension") for item in gaps if isinstance(item, dict)} != nonpass:
        raise ControlError("Program Design gaps must exactly cover every non-PASS dimension")
    for item in gaps:
        dimension = item.get("dimension") if isinstance(item, dict) else None
        result = results.get(dimension)
        expected_fields = DESIGN_BLOCKED_GAP_FIELDS if result == "DESIGN_BLOCKED" else SEMANTIC_GAP_FIELDS
        if not isinstance(item, dict) or set(item) != expected_fields:
            raise ControlError("Program Design gap does not match the exact result-specific schema")
        required = expected_fields - {"dimension"}
        if any(not nonempty_string(item.get(field)) for field in required):
            raise ControlError("Program Design gaps require nonempty evidence fields")
        if result == "DESIGN_BLOCKED":
            if dimension != "upstream_commitment_realization":
                raise ControlError("Program Design DESIGN_BLOCKED belongs to upstream_commitment_realization")
            if item.get("upstream_source") != source_kind or item.get("resume_boundary") != source_kind:
                raise ControlError("Program Design DESIGN_BLOCKED must resume at the actual source boundary")


def load_program_design_review(
    run_dir: Path,
    effective: dict[str, Any],
    candidate_version: int,
    candidate_sha256: str,
    source_kind: str,
    review_reference: Any,
) -> tuple[dict[str, Any], str]:
    if review_reference != PROGRAM_DESIGN_REVIEW_REFERENCE:
        raise ControlError(f"Program Design review must use exact {PROGRAM_DESIGN_REVIEW_REFERENCE}")
    path = managed_path(run_dir, review_reference)
    if not path.is_file():
        raise ControlError("Program Design review evidence is missing or not a real file")
    try:
        review_bytes = path.read_bytes()
        envelope = load_json(review_bytes.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ControlError("Program Design review evidence is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ControlError("Program Design review evidence is not valid duplicate-safe JSON") from exc
    review_sha256 = hashlib.sha256(review_bytes).hexdigest()
    if not isinstance(envelope, dict) or set(envelope) != PROGRAM_DESIGN_REVIEW_FIELDS:
        raise ControlError("Program Design review envelope does not match its exact schema")
    policy = effective.get("gates", {}).get("program_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    if (
        type(envelope.get("version")) is not int
        or envelope.get("version") != 1
        or envelope.get("run") != effective["run"]
        or envelope.get("stage") != "program_design"
        or configured not in {"AGENT_REVIEW", "HUMAN"}
        or envelope.get("policy") != configured
        or type(envelope.get("candidate_version")) is not int
        or envelope.get("candidate_version") != candidate_version
        or envelope.get("candidate_sha256") != candidate_sha256
        or envelope.get("repository_baselines") != effective["repos"]
    ):
        raise ControlError("Program Design review evidence does not match current policy, candidate, or baselines")
    validate_program_design_semantic_review(envelope.get("semantic_review"), source_kind)
    if envelope["semantic_review"]["verdict"] != "PASS":
        raise ControlError(f"Program Design semantic review is {envelope['semantic_review']['verdict']}")
    return envelope, review_sha256


def validate_ticket_graph_semantic_review(review: Any, source_kinds: set[str]) -> None:
    if not isinstance(review, dict) or set(review) != SEMANTIC_REVIEW_FIELDS:
        raise ControlError("ticket-graph semantic_review does not match its exact schema")
    verdict = review.get("verdict")
    rows = review.get("dimensions")
    gaps = review.get("gaps")
    if verdict not in {"PASS", "BLOCKED"} or not isinstance(rows, list) or not isinstance(gaps, list):
        raise ControlError("ticket-graph semantic_review is malformed")
    if (
        len(rows) != len(TICKET_GRAPH_DIMENSIONS)
        or any(not isinstance(row, dict) or set(row) != DIMENSION_REVIEW_FIELDS for row in rows)
        or any(row.get("dimension") not in TICKET_GRAPH_DIMENSIONS for row in rows)
        or len({row.get("dimension") for row in rows}) != len(TICKET_GRAPH_DIMENSIONS)
        or any(row.get("result") not in {"PASS", "BLOCKED", "DESIGN_BLOCKED"} for row in rows)
        or any(not nonempty_string(row.get("evidence")) for row in rows)
    ):
        raise ControlError("ticket-graph semantic_review must cover the exact seven Stage 5 dimensions")
    results = {row["dimension"]: row["result"] for row in rows}
    expected_verdict = "PASS" if all(result == "PASS" for result in results.values()) else "BLOCKED"
    if verdict != expected_verdict:
        raise ControlError("ticket-graph verdict must be derived from its dimension rows")
    nonpass = {dimension for dimension, result in results.items() if result != "PASS"}
    if any(
        not isinstance(item, dict)
        or not nonempty_string(item.get("dimension"))
        for item in gaps
    ):
        raise ControlError("ticket-graph gaps must exactly cover every non-PASS dimension")
    if len(gaps) != len(nonpass) or {item["dimension"] for item in gaps} != nonpass:
        raise ControlError("ticket-graph gaps must exactly cover every non-PASS dimension")
    for item in gaps:
        dimension = item.get("dimension") if isinstance(item, dict) else None
        result = results.get(dimension)
        expected_fields = DESIGN_BLOCKED_GAP_FIELDS if result == "DESIGN_BLOCKED" else SEMANTIC_GAP_FIELDS
        if not isinstance(item, dict) or set(item) != expected_fields:
            raise ControlError("ticket-graph gap does not match the exact result-specific schema")
        if any(not nonempty_string(item.get(field)) for field in expected_fields - {"dimension"}):
            raise ControlError("ticket-graph gaps require nonempty evidence fields")
        if result == "DESIGN_BLOCKED" and (
            item.get("upstream_source") not in source_kinds
            or item.get("resume_boundary") != item.get("upstream_source")
        ):
            raise ControlError("ticket-graph DESIGN_BLOCKED must resume at an applicable source boundary")


def load_ticket_graph_review(
    run_dir: Path,
    effective: dict[str, Any],
    candidate_version: int,
    candidate_sha256: str,
    source_bindings: list[dict[str, Any]],
    review_reference: Any,
) -> tuple[dict[str, Any], str]:
    if review_reference != TICKET_GRAPH_REVIEW_REFERENCE:
        raise ControlError(f"ticket-graph review must use exact {TICKET_GRAPH_REVIEW_REFERENCE}")
    path = managed_path(run_dir, review_reference)
    if not path.is_file() or path.is_symlink():
        raise ControlError("ticket-graph review evidence is missing or not a real file")
    try:
        review_bytes = path.read_bytes()
        envelope = load_json(review_bytes.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ControlError("ticket-graph review evidence is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ControlError("ticket-graph review evidence is not valid duplicate-safe JSON") from exc
    review_sha256 = hashlib.sha256(review_bytes).hexdigest()
    if not isinstance(envelope, dict) or set(envelope) != TICKET_GRAPH_REVIEW_FIELDS:
        raise ControlError("ticket-graph review envelope does not match its exact schema")
    policy = effective.get("gates", {}).get("tickets", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    if (
        type(envelope.get("version")) is not int
        or envelope.get("version") != 1
        or envelope.get("run") != effective["run"]
        or envelope.get("stage") != "tickets"
        or configured not in {"AGENT_REVIEW", "HUMAN"}
        or envelope.get("policy") != configured
        or type(envelope.get("candidate_version")) is not int
        or envelope.get("candidate_version") != candidate_version
        or envelope.get("candidate_sha256") != candidate_sha256
        or not json_equal_exact(envelope.get("source_bindings"), source_bindings)
        or envelope.get("repository_baselines") != effective["repos"]
    ):
        raise ControlError("ticket-graph review evidence does not match current policy, candidate, sources, or baselines")
    validate_ticket_graph_semantic_review(
        envelope.get("semantic_review"),
        {item["kind"] for item in source_bindings},
    )
    if envelope["semantic_review"]["verdict"] != "PASS":
        raise ControlError("ticket-graph semantic review is BLOCKED")
    return envelope, review_sha256


def validate_upstream_block_review(
    envelope: Any,
    *,
    run: str,
    planning_revision: int,
    system_acceptance: Any,
    effective: dict[str, Any],
    repository_verification: Optional[atlas_repository.Verification],
) -> None:
    if not isinstance(envelope, dict) or set(envelope) != UPSTREAM_BLOCK_REVIEW_FIELDS:
        raise ControlError("Program Design upstream-block envelope does not match its exact schema")
    if (
        type(envelope.get("version")) is not int
        or envelope.get("version") != 1
        or envelope.get("run") != run
        or envelope.get("stage") != "program_design"
        or type(envelope.get("planning_revision")) is not int
        or envelope.get("planning_revision") != planning_revision
        or envelope.get("verdict") not in {
            "CONFIRMED_UPSTREAM_CONTRADICTION", "NOT_CONFIRMED", "UNAVAILABLE",
        }
        or envelope.get("repository_baselines") != effective["repos"]
        or not nonempty_string(envelope.get("review_evidence"))
    ):
        raise ControlError("Program Design upstream-block evidence is not current")
    if contains_machine_local_path(envelope):
        raise ControlError("Program Design upstream-block evidence contains a machine-local path")
    predecessor = envelope.get("system_design_acceptance")
    if (
        not isinstance(predecessor, dict)
        or not json_equal_exact(predecessor, system_acceptance)
    ):
        raise ControlError(
            "Program Design upstream-block evidence does not bind the complete current System Design acceptance"
        )
    finding = envelope.get("finding")
    if not isinstance(finding, dict) or set(finding) != UPSTREAM_BLOCK_FINDING_FIELDS:
        raise ControlError("Program Design upstream-block finding does not match its exact schema")
    if (
        finding.get("dimension") != "upstream_commitment_realization"
        or finding.get("upstream_source") != "system_design"
        or finding.get("resume_boundary") != "system_design"
        or any(
            not nonempty_string(finding.get(field))
            for field in UPSTREAM_BLOCK_FINDING_FIELDS - {"dimension", "code_evidence"}
        )
    ):
        raise ControlError("Program Design upstream-block finding is not a System Design contradiction")
    code_evidence = finding.get("code_evidence")
    valid_pairs = {(item["repository"], item["baseline"]) for item in effective["repos"]}
    repositories = (
        {
            repository.identity: repository
            for repository in repository_verification.repositories
        }
        if repository_verification is not None
        else {}
    )
    if not isinstance(code_evidence, list) or not code_evidence:
        raise ControlError("Program Design upstream-block finding requires code evidence")
    for item in code_evidence:
        if not isinstance(item, dict) or set(item) != CODE_EVIDENCE_FIELDS:
            raise ControlError("Program Design upstream-block code evidence is malformed")
        relative = item.get("path")
        if not isinstance(relative, str):
            raise ControlError("Program Design upstream-block code evidence is not portable or current")
        path = PurePosixPath(relative)
        if (
            (item.get("repository"), item.get("baseline")) not in valid_pairs
            or repository_verification is not None and item.get("repository") not in repositories
            or path.is_absolute()
            or PureWindowsPath(relative).is_absolute()
            or not path.parts
            or any(part in {"", ".", ".."} for part in path.parts)
            or "\\" in relative
            or not nonempty_string(item.get("evidence"))
        ):
            raise ControlError("Program Design upstream-block code evidence is not portable or current")
        if repository_verification is not None:
            try:
                atlas_repository.read_tree_path(repositories[item["repository"]], relative)
            except atlas_repository.RepositoryBlocked as exc:
                raise ControlError(
                    f"Program Design upstream-block code evidence is unavailable: {exc.code}: {exc.problem}"
                ) from exc


def load_upstream_block_review_input(
    run_dir: Path,
    review_input: Path,
    planning: dict[str, Any],
    effective: dict[str, Any],
    repository_verification: atlas_repository.Verification,
) -> tuple[bytes, dict[str, Any], str]:
    path = managed_path(run_dir, str(review_input))
    if not path.is_file():
        raise ControlError("Program Design upstream-block input is missing or not a real file")
    try:
        review_bytes = path.read_bytes()
        envelope = load_json(review_bytes.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ControlError("Program Design upstream-block input is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ControlError("Program Design upstream-block input is not valid duplicate-safe JSON") from exc
    validate_upstream_block_review(
        envelope,
        run=planning["run"],
        planning_revision=planning["revision"],
        system_acceptance=planning["acceptances"]["system_design"],
        effective=effective,
        repository_verification=repository_verification,
    )
    return review_bytes, envelope, hashlib.sha256(review_bytes).hexdigest()


@contextlib.contextmanager
def retained_upstream_block_evidence(
    run_dir: Path,
    review_bytes: bytes,
) -> Iterator[tuple[Path, Path, int, tuple[int, int]]]:
    canonical = managed_path(run_dir, UPSTREAM_BLOCK_REVIEW_REFERENCE)
    parent = canonical.parent
    parent.mkdir(mode=0o700, exist_ok=True)
    if not SECURE_DIR_FD_EVIDENCE_INSTALL:
        raise ControlError("platform cannot securely install upstream-block evidence")
    before = os.stat(parent, follow_symlinks=False)
    if not stat.S_ISDIR(before.st_mode):
        raise ControlError("upstream-block evidence parent is not a real directory")
    parent_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        parent_fd = os.open(parent, parent_flags)
    except OSError as exc:
        raise ControlError("upstream-block evidence parent changed during validation") from exc
    leaf = Path(UPSTREAM_BLOCK_REVIEW_REFERENCE).name
    identity = (before.st_dev, before.st_ino)
    try:
        opened = os.fstat(parent_fd)
        after = os.stat(parent, follow_symlinks=False)
        if (
            not stat.S_ISDIR(opened.st_mode)
            or not stat.S_ISDIR(after.st_mode)
            or (opened.st_dev, opened.st_ino) != identity
            or (after.st_dev, after.st_ino) != identity
        ):
            raise ControlError("upstream-block evidence parent changed during validation")
        read_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            existing_fd = os.open(leaf, read_flags, dir_fd=parent_fd)
        except FileNotFoundError:
            existing_fd = None
        if existing_fd is not None:
            with os.fdopen(existing_fd, "rb") as handle:
                existing = handle.read()
            if existing != review_bytes:
                raise ControlError("canonical Program Design upstream-block evidence already exists with different bytes")
        else:
            write_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            temp_leaf = None
            fd = None
            for _ in range(16):
                candidate = f".{leaf}.{os.getpid()}.{secrets.token_hex(8)}.tmp"
                try:
                    fd = os.open(candidate, write_flags, 0o600, dir_fd=parent_fd)
                except FileExistsError:
                    continue
                temp_leaf = candidate
                break
            if fd is None or temp_leaf is None:
                raise ControlError("could not reserve temporary upstream-block evidence")
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(review_bytes)
                    handle.flush()
                    os.fsync(handle.fileno())
                try:
                    os.link(
                        temp_leaf,
                        leaf,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                        follow_symlinks=False,
                    )
                except FileExistsError:
                    existing_fd = os.open(leaf, read_flags, dir_fd=parent_fd)
                    with os.fdopen(existing_fd, "rb") as handle:
                        existing = handle.read()
                    if existing != review_bytes:
                        raise ControlError("canonical Program Design upstream-block evidence was created concurrently")
                os.fsync(parent_fd)
            finally:
                try:
                    os.unlink(temp_leaf, dir_fd=parent_fd)
                except FileNotFoundError:
                    pass
        yield canonical, parent, parent_fd, identity
    finally:
        with contextlib.suppress(OSError):
            os.close(parent_fd)


def verify_retained_upstream_block_evidence(
    parent: Path,
    parent_fd: int,
    identity: tuple[int, int],
    review_bytes: bytes,
) -> None:
    try:
        opened = os.fstat(parent_fd)
        current = os.stat(parent, follow_symlinks=False)
    except OSError as exc:
        raise ControlError("upstream-block evidence parent changed at the write boundary") from exc
    if (
        not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(current.st_mode)
        or (opened.st_dev, opened.st_ino) != identity
        or (current.st_dev, current.st_ino) != identity
    ):
        raise ControlError("upstream-block evidence parent changed at the write boundary")
    leaf = Path(UPSTREAM_BLOCK_REVIEW_REFERENCE).name
    read_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        evidence_fd = os.open(leaf, read_flags, dir_fd=parent_fd)
        with os.fdopen(evidence_fd, "rb") as handle:
            current_bytes = handle.read()
        after_read = os.stat(parent, follow_symlinks=False)
    except OSError as exc:
        raise ControlError("upstream-block evidence changed at the write boundary") from exc
    if (
        current_bytes != review_bytes
        or not stat.S_ISDIR(after_read.st_mode)
        or (after_read.st_dev, after_read.st_ino) != identity
    ):
        raise ControlError("upstream-block evidence changed at the write boundary")


def install_upstream_block_evidence(run_dir: Path, review_bytes: bytes) -> Path:
    with retained_upstream_block_evidence(run_dir, review_bytes) as installation:
        return installation[0]


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


def planning_control_bytes(planning: dict[str, Any]) -> bytes:
    return (json.dumps(planning, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_planning_control_bytes_atomic(
    run_dir: Path,
    content: bytes,
    *,
    precondition: Optional[Callable[[], None]] = None,
) -> None:
    path = managed_path(run_dir, PLANNING_FILE)
    fd, name = tempfile.mkstemp(prefix=".planning-control.json.", dir=run_dir)
    temp = Path(name)
    published = False
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if precondition is not None:
            precondition()
        os.replace(temp, path)
        published = True
        directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        directory_fd = os.open(run_dir, directory_flags)
        try:
            os.fsync(directory_fd)
        finally:
            with contextlib.suppress(OSError):
                os.close(directory_fd)
    finally:
        if not published:
            temp.unlink(missing_ok=True)


def write_planning_control_atomic(
    run_dir: Path,
    planning: dict[str, Any],
    *,
    precondition: Optional[Callable[[], None]] = None,
) -> None:
    content = planning_control_bytes(planning)
    write_planning_control_bytes_atomic(run_dir, content, precondition=precondition)


def validate_system_design_acceptance(
    run_dir: Path,
    anchor: dict[str, Any],
    effective: dict[str, Any],
    record: Any,
    repair_context: Optional[dict[str, Any]] = None,
    historical: bool = False,
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
    expected_version = (
        repair_context["superseded_system_design"]["candidate_version"] + 1
        if repair_context is not None
        else None
    )
    candidate_version = record.get("candidate_version")
    if (
        type(candidate_version) is not int
        or candidate_version < 1
        or (expected_version is not None and candidate_version != expected_version)
        or not re.fullmatch(r"[0-9a-f]{64}", str(record.get("candidate_sha256", "")))
        or record.get("authority") not in {"HUMAN", "AGENT_REVIEW"}
        or not json_equal_exact(record.get("source_bindings"), [expected_source])
        or record.get("repository_baselines") != []
    ):
        raise ControlError("planning-control.json System Design acceptance is malformed")
    policy = effective.get("gates", {}).get("system_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    if historical:
        if (
            configured == "HUMAN"
            and (
                record["authority"] != "HUMAN"
                or record.get("review_reference") is not None
                or record.get("review_sha256") is not None
            )
        ):
            raise ControlError("historical System Design acceptance is malformed")
        if configured in {"AGENT_REVIEW", "HUMAN_IF_CHANGED"} and (
            record["authority"] not in {"HUMAN", "AGENT_REVIEW"}
            or record.get("review_reference") != SYSTEM_DESIGN_REVIEW_REFERENCE
            or type(record.get("review_sha256")) is not str
            or re.fullmatch(r"[0-9a-f]{64}", record["review_sha256"]) is None
        ):
            raise ControlError("historical System Design acceptance is malformed")
        return
    if configured == "HUMAN":
        if record["authority"] != "HUMAN":
            raise ControlError("planning-control.json System Design acceptance is malformed")
        if repair_context is None:
            if record.get("review_reference") is not None or record.get("review_sha256") is not None:
                raise ControlError("planning-control.json System Design acceptance is malformed")
        else:
            _, review_sha256, mapped = load_system_design_review(
                run_dir,
                effective,
                record["candidate_version"],
                record["candidate_sha256"],
                record.get("review_reference"),
                repair_context,
            )
            if mapped != "HUMAN" or record.get("review_sha256") != review_sha256:
                raise ControlError("planning-control.json System Design repair evidence is not current")
    elif configured in {"AGENT_REVIEW", "HUMAN_IF_CHANGED"}:
        _, review_sha256, mapped = load_system_design_review(
            run_dir,
            effective,
            record["candidate_version"],
            record["candidate_sha256"],
            record.get("review_reference"),
            repair_context,
        )
        if record["authority"] != mapped or record.get("review_sha256") != review_sha256:
            raise ControlError("planning-control.json System Design acceptance evidence is not current")
    else:
        raise ControlError("planning-control.json System Design acceptance uses an unsupported policy")


def expected_program_design_source(
    planning: dict[str, Any], effective: dict[str, Any]
) -> dict[str, Any]:
    if "system_design" in effective["stages"]:
        system = planning["acceptances"].get("system_design")
        if not isinstance(system, dict):
            raise ControlError("Program Design requires an accepted System Design source")
        return {
            "kind": "system_design",
            "artifact": SYSTEM_DESIGN_FILE,
            "version": system["candidate_version"],
            "sha256": system["candidate_sha256"],
        }
    product = planning["stage0_anchor"].get("product_closure")
    if "discovery" in effective["stages"]:
        if not isinstance(product, dict):
            raise ControlError("Program Design requires an accepted Product Definition Approval source")
        return {
            "kind": "product_closure",
            "artifact": "20-prd.md",
            "version": product["version"],
            "sha256": product["sha256"],
        }
    anchor = planning["stage0_anchor"]
    return {
        "kind": "stage0",
        "artifact": "run.yaml",
        "sha256": anchor["base_run_sha256"],
        "effective_config_hash": anchor["effective_config_hash"],
        "effective_config_revision": anchor["effective_config_revision"],
    }


def expected_ticket_graph_sources(
    planning: dict[str, Any], effective: dict[str, Any]
) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    stages = effective["stages"]
    product = planning["stage0_anchor"].get("product_closure")
    if "discovery" in stages:
        if not isinstance(product, dict):
            raise ControlError("ticket graph requires an accepted Product Definition Approval source")
        sources.append({
            "kind": "product_closure",
            "artifact": "20-prd.md",
            "version": product["version"],
            "sha256": product["sha256"],
        })
    if "system_design" in stages:
        system = planning["acceptances"].get("system_design")
        if not isinstance(system, dict):
            raise ControlError("ticket graph requires an accepted System Design source")
        sources.append({
            "kind": "system_design",
            "artifact": SYSTEM_DESIGN_FILE,
            "version": system["candidate_version"],
            "sha256": system["candidate_sha256"],
        })
    if "program_design" in stages:
        program = planning["acceptances"].get("program_design")
        if not isinstance(program, dict):
            raise ControlError("ticket graph requires an accepted Program Design source")
        if "discovery" not in stages and "system_design" not in stages:
            anchor = planning["stage0_anchor"]
            sources.append({
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            })
        sources.append({
            "kind": "program_design",
            "artifact": PROGRAM_DESIGN_FILE,
            "version": program["candidate_version"],
            "sha256": program["candidate_sha256"],
        })
    if not any(stage in stages for stage in ("discovery", "system_design", "program_design")):
        anchor = planning["stage0_anchor"]
        sources.append({
            "kind": "stage0",
            "artifact": "run.yaml",
            "sha256": anchor["base_run_sha256"],
            "effective_config_hash": anchor["effective_config_hash"],
            "effective_config_revision": anchor["effective_config_revision"],
        })
    return sources


def require_program_design_repository_access(run_dir: Path) -> atlas_repository.Verification:
    verification = atlas_repository.verify_run(run_dir)
    if verification.gaps:
        details = "; ".join(
            f"{item.code}"
            + (f" for {item.repository}" if item.repository is not None else "")
            + f": {item.problem}"
            for item in verification.gaps
        )
        raise ControlError(f"Program Design repository verification is BLOCKED: {details}")
    return verification


def validate_program_design_acceptance(
    run_dir: Path,
    planning: dict[str, Any],
    effective: dict[str, Any],
    record: Any,
) -> None:
    require_program_design_repository_access(run_dir)
    if not isinstance(record, dict) or set(record) != PLANNING_ACCEPTANCE_FIELDS:
        raise ControlError("planning-control.json Program Design acceptance is malformed")
    try:
        canonical_date(record.get("accepted"), "Program Design acceptance date")
    except ControlError as exc:
        raise ControlError("planning-control.json Program Design acceptance is malformed") from exc
    expected_source = expected_program_design_source(planning, effective)
    policy = effective.get("gates", {}).get("program_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    expected_authority = "HUMAN" if configured == "HUMAN" else "AGENT_REVIEW"
    if (
        type(record.get("candidate_version")) is not int
        or record["candidate_version"] != 1
        or not re.fullmatch(r"[0-9a-f]{64}", str(record.get("candidate_sha256", "")))
        or configured not in {"AGENT_REVIEW", "HUMAN"}
        or record.get("authority") != expected_authority
        or record.get("review_reference") != PROGRAM_DESIGN_REVIEW_REFERENCE
        or not json_equal_exact(record.get("source_bindings"), [expected_source])
        or record.get("repository_baselines") != effective["repos"]
    ):
        raise ControlError("planning-control.json Program Design acceptance is malformed")
    _, review_sha256 = load_program_design_review(
        run_dir,
        effective,
        record["candidate_version"],
        record["candidate_sha256"],
        expected_source["kind"],
        record["review_reference"],
    )
    if record.get("review_sha256") != review_sha256:
        raise ControlError("planning-control.json Program Design acceptance evidence is not current")


def validate_ticket_graph_acceptance(
    run_dir: Path,
    planning: dict[str, Any],
    effective: dict[str, Any],
    record: Any,
) -> None:
    if isinstance(record, dict) and record.get("candidate_version") == 1:
        raise ControlError(
            "planning-control.json contains a ticket-graph v1 acceptance retained as raw historical evidence only; "
            "it is not loadable or factory-executable and must not be converted in place"
        )
    if not isinstance(record, dict) or set(record) != PLANNING_ACCEPTANCE_FIELDS:
        raise ControlError("planning-control.json ticket-graph acceptance is malformed")
    try:
        canonical_date(record.get("accepted"), "ticket-graph acceptance date")
    except ControlError as exc:
        raise ControlError("planning-control.json ticket-graph acceptance is malformed") from exc
    expected_sources = expected_ticket_graph_sources(planning, effective)
    expected_authority = effective["gates"]["tickets"]["authority"]
    if (
        type(record.get("candidate_version")) is not int
        or record["candidate_version"] != CURRENT_TICKET_GRAPH_VERSION
        or re.fullmatch(r"[0-9a-f]{64}", str(record.get("candidate_sha256", ""))) is None
        or record.get("authority") != expected_authority
        or record.get("review_reference") != TICKET_GRAPH_REVIEW_REFERENCE
        or not json_equal_exact(record.get("source_bindings"), expected_sources)
        or record.get("repository_baselines") != effective["repos"]
    ):
        raise ControlError("planning-control.json ticket-graph acceptance is malformed")
    report = ticket_graph_report(run_dir, planning, effective)
    if (
        report.get("verdict") != "PASS"
        or report.get("candidate_version") != record["candidate_version"]
        or report.get("candidate_sha256") != record["candidate_sha256"]
        or not json_equal_exact(report.get("source_bindings"), expected_sources)
    ):
        raise ControlError("accepted ticket graph is not current")
    _, review_sha256 = load_ticket_graph_review(
        run_dir,
        effective,
        record["candidate_version"],
        record["candidate_sha256"],
        expected_sources,
        record["review_reference"],
    )
    if record.get("review_sha256") != review_sha256:
        raise ControlError("planning-control.json ticket-graph acceptance evidence is not current")


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
        or any(value not in {"PENDING", "NOT_REQUIRED", "HUMAN_APPROVED", "AGENT_APPROVED", "STALE"} for value in gates.values())
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
        raise ControlError("planning-control.json Product Definition Approval anchor is malformed")
    _, effective = verified_state(run_dir)
    validate_run(effective)
    selected = {stage for stage in DOWNSTREAM_STAGES if stage in effective["stages"]}
    if any((stage in selected) != (gates[stage] != "NOT_REQUIRED") for stage in DOWNSTREAM_STAGES):
        raise ControlError("planning-control.json gates do not match selected downstream stages")

    blocked_reason = planning.get("blocked_reason")
    intentional_system_revision = is_intentional_system_revision(planning)
    repair_episode = blocked_reason if isinstance(blocked_reason, dict) else {}
    repair_attempts = repair_episode.get("attempts_used")
    system_acceptance_repair_context = (
        expected_system_repair_context(run_dir, planning, None)
        if repair_episode.get("state") == "PROGRAM_DESIGN_RESUMED"
        else persisted_system_repair_context(run_dir, planning, effective)
        if blocked_reason is None and acceptances.get("program_design") is not None
        else None
    )
    system_candidate_may_diverge = intentional_system_revision or (
        gates["system_design"] == "STALE"
        and type(repair_attempts) is int
        and repair_attempts > 0
        and valid_repair_attempt(
            repair_episode.get("current_attempt"),
            repair_attempts,
            "system_design",
        )
    )

    approved_stages: list[str] = []
    for stage in DOWNSTREAM_STAGES:
        record = acceptances[stage]
        approved = gates[stage] in {"HUMAN_APPROVED", "AGENT_APPROVED"}
        stale = stage == "system_design" and gates[stage] == "STALE"
        if (approved or stale) != (record is not None):
            raise ControlError("planning-control.json gate/acceptance coherence is invalid")
        if record is not None:
            if stage == "system_design":
                validate_system_design_acceptance(
                    run_dir,
                    anchor,
                    effective,
                    record,
                    system_acceptance_repair_context,
                    gates["system_design"] == "STALE",
                )
            elif stage == "program_design":
                validate_program_design_acceptance(run_dir, planning, effective, record)
            elif stage == "tickets":
                validate_ticket_graph_acceptance(run_dir, planning, effective, record)
            else:  # pragma: no cover
                raise ControlError("planning-control.json contains an unsupported downstream acceptance")
            expected_gate = (
                "HUMAN_APPROVED" if record["authority"] == "HUMAN" else "AGENT_APPROVED"
            )
            if approved and gates[stage] != expected_gate:
                raise ControlError("planning-control.json gate label does not match acceptance authority")
            if approved:
                approved_stages.append(stage)

    record = acceptances["system_design"]
    if record is not None:
        candidate_path = managed_path(run_dir, SYSTEM_DESIGN_FILE)
        if (
            not system_candidate_may_diverge
            and (
                not candidate_path.is_file()
                or file_sha256(candidate_path) != record["candidate_sha256"]
            )
        ):
            raise ControlError("accepted System Design candidate bytes no longer match recorded provenance")
        if product_closure is not None:
            product_path = managed_path(run_dir, "20-prd.md")
            if not product_path.is_file() or file_sha256(product_path) != product_closure["sha256"]:
                raise ControlError("accepted System Design product source no longer matches recorded provenance")

    program_record = acceptances["program_design"]
    if program_record is not None:
        candidate_path = managed_path(run_dir, PROGRAM_DESIGN_FILE)
        if not candidate_path.is_file() or file_sha256(candidate_path) != program_record["candidate_sha256"]:
            raise ControlError("accepted Program Design candidate bytes no longer match recorded provenance")
        source = program_record["source_bindings"][0]
        if source["kind"] == "product_closure":
            product_path = managed_path(run_dir, "20-prd.md")
            if not product_path.is_file() or file_sha256(product_path) != source["sha256"]:
                raise ControlError("accepted Program Design product source no longer matches recorded provenance")
        elif source["kind"] == "system_design":
            system_path = managed_path(run_dir, SYSTEM_DESIGN_FILE)
            if not system_path.is_file() or file_sha256(system_path) != source["sha256"]:
                raise ControlError("accepted Program Design System Design source no longer matches recorded provenance")

    if (
        type(planning.get("version")) is not int
        or planning.get("version") != 1
        or not isinstance(planning.get("run"), str)
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", planning["run"])
        or planning["run"] != effective["run"]
        or type(planning.get("revision")) is not int
    ):
        raise ControlError("planning-control.json values are not a coherent current planning state")

    blocked_reason = planning.get("blocked_reason")
    if blocked_reason is not None:
        expected_started_revision = 1 + sum(
            record is not None for record in acceptances.values()
        )
        expected_ticket_gate = "PENDING" if "tickets" in selected else "NOT_REQUIRED"
        if (
            not isinstance(blocked_reason, dict)
            or set(blocked_reason) != REPAIR_EPISODE_FIELDS
            or blocked_reason.get("kind") != "SYSTEM_DESIGN_REPAIR"
            or blocked_reason.get("state") not in {"SYSTEM_DESIGN_STALE", "PROGRAM_DESIGN_RESUMED"}
            or type(blocked_reason.get("started_from_revision")) is not int
            or blocked_reason["started_from_revision"] != expected_started_revision
            or blocked_reason.get("review_reference") != UPSTREAM_BLOCK_REVIEW_REFERENCE
            or not re.fullmatch(r"[0-9a-f]{64}", str(blocked_reason.get("review_sha256", "")))
            or not isinstance(blocked_reason.get("superseded_system_design"), dict)
            or set(blocked_reason["superseded_system_design"]) != PLANNING_ACCEPTANCE_FIELDS
            or (
                blocked_reason.get("initial_program_candidate_sha256") is not None
                and (
                    type(blocked_reason.get("initial_program_candidate_sha256")) is not str
                    or re.fullmatch(
                        r"[0-9a-f]{64}",
                        blocked_reason["initial_program_candidate_sha256"],
                    ) is None
                )
            )
            or type(blocked_reason.get("attempts_used")) is not int
            or not 0 <= blocked_reason["attempts_used"] <= 4
            or planning.get("status") != "BLOCKED"
            or gates["program_design"] != "PENDING"
            or gates["tickets"] != expected_ticket_gate
            or acceptances["program_design"] is not None
            or acceptances["tickets"] is not None
        ):
            raise ControlError("planning-control.json repair episode is malformed")
        program_candidate_reserved = (
            blocked_reason["state"] == "PROGRAM_DESIGN_RESUMED"
            and valid_repair_attempt(
                blocked_reason.get("current_attempt"),
                blocked_reason["attempts_used"],
                "program_design",
            )
        )
        if (
            not program_candidate_reserved
            and repair_candidate_sha256_before(run_dir, "program_design")
            != blocked_reason.get("initial_program_candidate_sha256")
        ):
            raise ControlError(
                "initial Program Design candidate changed before its first producer reservation"
            )
        if blocked_reason["state"] == "SYSTEM_DESIGN_STALE":
            if (
                not json_equal_exact(
                    blocked_reason["superseded_system_design"],
                    acceptances["system_design"],
                )
                or (
                    blocked_reason["attempts_used"] == 0
                    and blocked_reason.get("current_attempt") is not None
                )
                or (
                    blocked_reason["attempts_used"] > 0
                    and not valid_repair_attempt(
                        blocked_reason.get("current_attempt"),
                        blocked_reason["attempts_used"],
                        "system_design",
                    )
                )
                or (
                    blocked_reason["attempts_used"] == 1
                    and blocked_reason["current_attempt"]["candidate_sha256_before"]
                    != acceptances["system_design"]["candidate_sha256"]
                )
                or planning.get("phase") != "system_design"
                or gates["system_design"] != "STALE"
                or planning["revision"] != (
                    blocked_reason["started_from_revision"]
                    + 1
                    + blocked_reason["attempts_used"]
                )
            ):
                raise ControlError("planning-control.json stale System Design repair episode is malformed")
        else:
            current_system = acceptances["system_design"]
            superseded = blocked_reason["superseded_system_design"]
            system_attempts = (
                system_acceptance_repair_context.get("attempts_used")
                if isinstance(system_acceptance_repair_context, dict)
                else None
            )
            program_attempts = (
                blocked_reason["attempts_used"] - system_attempts
                if type(system_attempts) is int
                else -1
            )
            if (
                not isinstance(current_system, dict)
                or current_system["candidate_version"] != superseded["candidate_version"] + 1
                or current_system["candidate_sha256"] == superseded["candidate_sha256"]
                or not json_equal_exact(
                    current_system["source_bindings"],
                    superseded["source_bindings"],
                )
                or blocked_reason["attempts_used"] < 1
                or program_attempts < 0
                or (
                    program_attempts == 0
                    and blocked_reason.get("current_attempt") is not None
                )
                or (
                    program_attempts > 0
                    and not valid_repair_attempt(
                        blocked_reason.get("current_attempt"),
                        blocked_reason["attempts_used"],
                        "program_design",
                    )
                )
                or planning.get("phase") != "program_design"
                or gates["system_design"] not in {"HUMAN_APPROVED", "AGENT_APPROVED"}
                or planning["revision"] != (
                    blocked_reason["started_from_revision"]
                    + 2
                    + blocked_reason["attempts_used"]
                )
            ):
                raise ControlError("planning-control.json resumed Program Design repair episode is malformed")
        review_path = managed_path(run_dir, UPSTREAM_BLOCK_REVIEW_REFERENCE)
        if not review_path.is_file():
            raise ControlError("planning-control.json repair evidence is missing")
        try:
            review_bytes = review_path.read_bytes()
            envelope = load_json(review_bytes.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ControlError("planning-control.json repair evidence is not valid UTF-8") from exc
        except json.JSONDecodeError as exc:
            raise ControlError("planning-control.json repair evidence is not valid duplicate-safe JSON") from exc
        if hashlib.sha256(review_bytes).hexdigest() != blocked_reason["review_sha256"]:
            raise ControlError("planning-control.json repair evidence hash is not current")
        validate_upstream_block_review(
            envelope,
            run=planning["run"],
            planning_revision=blocked_reason["started_from_revision"],
            system_acceptance=blocked_reason["superseded_system_design"],
            effective=effective,
            repository_verification=None,
        )
        if envelope["verdict"] != "CONFIRMED_UPSTREAM_CONTRADICTION":
            raise ControlError("planning-control.json repair evidence is not confirmed")
        return planning

    if intentional_system_revision:
        prior_version = acceptances["system_design"]["candidate_version"]
        expected_revision = (
            2
            + sum(record is not None for record in acceptances.values())
            + 2 * (prior_version - 1)
        )
        if planning.get("revision") != expected_revision:
            raise ControlError("planning-control.json intentional System Design revision is malformed")
        return planning

    pending = [stage for stage in DOWNSTREAM_STAGES if gates[stage] == "PENDING"]
    repaired_revision_delta = (
        planning["revision"] - system_acceptance_repair_context["acceptance_revision"] - 1
        if system_acceptance_repair_context is not None
        else None
    )
    repaired_attempts_remaining = (
        4 - system_acceptance_repair_context["attempts_used"]
        if system_acceptance_repair_context is not None
        else None
    )
    system_version = (
        acceptances["system_design"].get("candidate_version")
        if isinstance(acceptances.get("system_design"), dict)
        else 1
    )
    intentional_revision_delta = (
        2 * (system_version - 1)
        if type(system_version) is int and system_version >= 1 and system_acceptance_repair_context is None
        else 0
    )
    normal_revision_is_coherent = (
        planning["revision"] == 1 + len(approved_stages) + intentional_revision_delta
    )
    planning_revision_is_coherent = (
        normal_revision_is_coherent
        if repaired_revision_delta is None
        else (
            repaired_attempts_remaining is not None
            and 1 <= repaired_revision_delta <= repaired_attempts_remaining
        )
    )
    ready_revision_is_coherent = (
        normal_revision_is_coherent
        if repaired_revision_delta is None
        else (
            repaired_attempts_remaining is not None
            and 2 <= repaired_revision_delta <= repaired_attempts_remaining + 1
        )
    )
    ready_for_execution = (
        planning.get("status") == "READY_FOR_EXECUTION"
        and planning.get("phase") == "tickets"
        and not pending
        and gates["tickets"] in {"HUMAN_APPROVED", "AGENT_APPROVED"}
        and acceptances["tickets"] is not None
        and "STALE" not in gates.values()
        and ready_revision_is_coherent
    )
    if ready_for_execution:
        return planning
    if (
        planning.get("status") != "PLANNING"
        or "STALE" in gates.values()
        or not pending
        or planning.get("phase") != pending[0]
        or not planning_revision_is_coherent
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
    if (
        not isinstance(policy, dict)
        or set(policy) != {"authority"}
        or policy.get("authority") not in {"HUMAN", "AGENT_REVIEW"}
    ):
        raise ControlError("tickets supports only configured AGENT_REVIEW or HUMAN authority")


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
            raise ControlError("selected discovery lacks accepted Product Definition Approval provenance")
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
            raise ControlError("selected discovery lacks accepted Product Definition Approval provenance")
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


def return_to_system_design(run_dir: Path, review_input: Path) -> str:
    planning, _, effective = verified_planning_state(run_dir)
    planning_path = managed_path(run_dir, PLANNING_FILE)
    planning_bytes = planning_path.read_bytes()
    try:
        byte_snapshot = load_json(planning_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ControlError("planning-control.json changed while its bytes were captured") from exc
    if not json_equal_exact(byte_snapshot, planning):
        raise ControlError("planning-control.json changed while its bytes were captured")
    if (
        planning["status"] != "PLANNING"
        or planning["phase"] != "program_design"
        or planning["gates"]["program_design"] != "PENDING"
        or planning["acceptances"]["program_design"] is not None
        or planning["gates"]["system_design"] not in {"HUMAN_APPROVED", "AGENT_APPROVED"}
        or "system_design" not in effective["stages"]
    ):
        raise ControlError("upstream repair requires pending Program Design sourced from accepted System Design")
    expected_source = expected_program_design_source(planning, effective)
    if expected_source.get("kind") != "system_design":
        raise ControlError("upstream repair supports only selected System Design")
    repository_verification = require_program_design_repository_access(run_dir)
    review_bytes, envelope, review_sha256 = load_upstream_block_review_input(
        run_dir, review_input, planning, effective, repository_verification
    )
    if envelope["verdict"] != "CONFIRMED_UPSTREAM_CONTRADICTION":
        raise ControlError(f"upstream contradiction review is {envelope['verdict']}")
    with retained_upstream_block_evidence(run_dir, review_bytes) as installation:
        _, evidence_parent, evidence_parent_fd, evidence_identity = installation
        final_planning = copy.deepcopy(planning)
        final_planning["status"] = "BLOCKED"
        final_planning["phase"] = "system_design"
        final_planning["gates"]["system_design"] = "STALE"
        final_planning["revision"] += 1
        final_planning["blocked_reason"] = {
            "kind": "SYSTEM_DESIGN_REPAIR",
            "state": "SYSTEM_DESIGN_STALE",
            "started_from_revision": planning["revision"],
            "review_reference": UPSTREAM_BLOCK_REVIEW_REFERENCE,
            "review_sha256": review_sha256,
            "superseded_system_design": copy.deepcopy(planning["acceptances"]["system_design"]),
            "attempts_used": 0,
            "current_attempt": None,
            "initial_program_candidate_sha256": repair_candidate_sha256_before(
                run_dir, "program_design"
            ),
        }
        final_bytes = planning_control_bytes(final_planning)

        def revalidate_immediately_before_replace() -> None:
            current, _, current_effective = verified_planning_state(run_dir)
            current_repository_verification = require_program_design_repository_access(run_dir)
            current_bytes, current_envelope, current_sha256 = load_upstream_block_review_input(
                run_dir, review_input, current, current_effective, current_repository_verification
            )
            verify_retained_upstream_block_evidence(
                evidence_parent,
                evidence_parent_fd,
                evidence_identity,
                review_bytes,
            )
            if (
                current != planning
                or planning_path.read_bytes() != planning_bytes
                or current_bytes != review_bytes
                or current_envelope != envelope
                or current_sha256 != review_sha256
                or repair_candidate_sha256_before(run_dir, "program_design")
                != final_planning["blocked_reason"]["initial_program_candidate_sha256"]
            ):
                raise ControlError("planning state or upstream-block evidence changed at the write boundary")

        try:
            write_planning_control_atomic(
                run_dir,
                final_planning,
                precondition=revalidate_immediately_before_replace,
            )
            require_program_design_repository_access(run_dir)
            verify_retained_upstream_block_evidence(
                evidence_parent,
                evidence_parent_fd,
                evidence_identity,
                review_bytes,
            )
            committed = load_planning_control(run_dir)
            if committed != final_planning:
                raise ControlError("committed upstream-repair state does not match the requested transition")
        except BaseException as exc:
            try:
                current_planning_bytes = planning_path.read_bytes()
            except BaseException as inspection_exc:
                raise ControlError(
                    "upstream-repair transition failed and resulting planning state could not be inspected"
                ) from inspection_exc
            if current_planning_bytes == final_bytes:
                try:
                    write_planning_control_bytes_atomic(run_dir, planning_bytes)
                    if planning_path.read_bytes() != planning_bytes:
                        raise ControlError("prior planning bytes did not survive rollback")
                except BaseException as rollback_exc:
                    raise ControlError(
                        "upstream-repair transition failed and prior state could not be restored"
                    ) from rollback_exc
                if isinstance(exc, Exception):
                    raise ControlError(
                        f"upstream-repair transition failed final validation and was rolled back: {exc}"
                    ) from exc
                raise
            if current_planning_bytes != planning_bytes:
                raise ControlError(
                    "upstream-repair transition failed after planning state changed independently"
                ) from exc
            raise
    return f"returned program_design -> system_design; planning-control revision {final_planning['revision']}"


def repair_candidate_sha256_before(run_dir: Path, stage: str) -> Optional[str]:
    relative = {
        "system_design": SYSTEM_DESIGN_FILE,
        "program_design": PROGRAM_DESIGN_FILE,
    }.get(stage)
    if relative is None:
        raise ControlError("repair attempts support only System Design or Program Design")
    candidate = managed_path(run_dir, relative)
    if not candidate.exists():
        return None
    if not candidate.is_file():
        raise ControlError(f"repair candidate {relative} is not a real file")
    return file_sha256(candidate)


def reserve_repair_attempt(run_dir: Path, stage: str) -> dict[str, Any]:
    planning, _, _ = verified_planning_state(run_dir)
    episode = planning.get("blocked_reason")
    episode_data = episode if isinstance(episode, dict) else {}
    episode_state = episode_data.get("state")
    expected_stage = (
        {
            "SYSTEM_DESIGN_STALE": "system_design",
            "PROGRAM_DESIGN_RESUMED": "program_design",
        }.get(episode_state)
        if isinstance(episode_state, str)
        else None
    )
    if (
        planning.get("status") != "BLOCKED"
        or expected_stage is None
        or planning.get("phase") != expected_stage
        or stage != expected_stage
    ):
        raise ControlError("repair attempt reservation requires the matching active repair phase")
    attempts_used = episode_data.get("attempts_used")
    if type(attempts_used) is not int or not 0 <= attempts_used <= 4:
        raise ControlError("repair attempt budget is malformed")
    if attempts_used == 4:
        raise ControlError("repair producer attempt budget is exhausted")

    planning_path = managed_path(run_dir, PLANNING_FILE)
    planning_bytes = planning_path.read_bytes()
    candidate_before = repair_candidate_sha256_before(run_dir, stage)
    attempt_number = attempts_used + 1
    updated = copy.deepcopy(planning)
    updated["revision"] += 1
    updated_episode = updated["blocked_reason"]
    updated_episode["attempts_used"] = attempt_number
    updated_episode["current_attempt"] = {
        "number": attempt_number,
        "stage": stage,
        "candidate_sha256_before": candidate_before,
    }

    def revalidate_before_reservation() -> None:
        current = load_planning_control(run_dir)
        if (
            current != planning
            or planning_path.read_bytes() != planning_bytes
            or repair_candidate_sha256_before(run_dir, stage) != candidate_before
        ):
            raise ControlError("repair state or candidate changed at the reservation boundary")

    updated_bytes = planning_control_bytes(updated)
    try:
        write_planning_control_atomic(
            run_dir,
            updated,
            precondition=revalidate_before_reservation,
        )
        committed = load_planning_control(run_dir)
        if not json_equal_exact(committed, updated):
            raise ControlError("committed repair attempt reservation is not current")
    except BaseException as exc:
        try:
            current_bytes = planning_path.read_bytes()
        except BaseException as inspection_exc:
            raise ControlError(
                "repair attempt reservation failed and resulting planning state could not be inspected"
            ) from inspection_exc
        if current_bytes == updated_bytes:
            try:
                write_planning_control_bytes_atomic(run_dir, planning_bytes)
                if planning_path.read_bytes() != planning_bytes:
                    raise ControlError("prior planning bytes did not survive rollback")
            except BaseException as rollback_exc:
                raise ControlError(
                    "repair attempt reservation failed and prior state could not be restored"
                ) from rollback_exc
            if isinstance(exc, Exception):
                raise ControlError(
                    f"repair attempt reservation failed final validation and was rolled back: {exc}"
                ) from exc
            raise
        if current_bytes != planning_bytes:
            raise ControlError(
                "repair attempt reservation failed after planning state changed independently"
            ) from exc
        raise
    if repair_candidate_sha256_before(run_dir, stage) != candidate_before:
        raise ControlError(
            f"repair candidate changed during reservation; attempt {attempt_number} remains consumed"
        )
    return {
        "attempt": attempt_number,
        "stage": stage,
        "candidate_sha256_before": candidate_before,
        "planning_revision": updated["revision"],
    }


def begin_system_design_revision(run_dir: Path) -> str:
    planning, _, effective = verified_planning_state(run_dir)
    gates = planning["gates"]
    acceptances = planning["acceptances"]
    if (
        planning.get("status") != "PLANNING"
        or planning.get("phase") != "program_design"
        or planning.get("blocked_reason") is not None
        or gates.get("system_design") not in {"HUMAN_APPROVED", "AGENT_APPROVED"}
        or not isinstance(acceptances.get("system_design"), dict)
        or gates.get("program_design") != "PENDING"
        or acceptances.get("program_design") is not None
        or acceptances.get("tickets") is not None
        or "program_design" not in effective["stages"]
    ):
        raise ControlError(
            "intentional System Design revision requires pending Program Design immediately after an accepted System Design"
        )
    prior = copy.deepcopy(acceptances["system_design"])
    updated = copy.deepcopy(planning)
    updated["phase"] = "system_design"
    updated["gates"]["system_design"] = "STALE"
    updated["revision"] += 1

    def revalidate_immediately_before_replace() -> None:
        current, _, _ = verified_planning_state(run_dir)
        if current != planning:
            raise ControlError("planning state changed before intentional System Design revision")

    write_planning_control_atomic(
        run_dir,
        updated,
        precondition=revalidate_immediately_before_replace,
    )
    loaded = load_planning_control(run_dir)
    if not is_intentional_system_revision(loaded) or loaded["acceptances"]["system_design"] != prior:
        raise ControlError("intentional System Design revision transition did not preserve prior acceptance")
    return (
        "began intentional System Design revision; retained version "
        f"{prior['candidate_version']} acceptance as stale provenance; "
        f"planning-control revision {updated['revision']}"
    )


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
    repair_episode = planning.get("blocked_reason")
    repair_data = repair_episode if isinstance(repair_episode, dict) else {}
    intentional_revision = is_intentional_system_revision(planning)
    system_repair = (
        planning.get("status") == "BLOCKED"
        and planning.get("phase") == "system_design"
        and planning["gates"]["system_design"] == "STALE"
        and repair_data.get("state") == "SYSTEM_DESIGN_STALE"
        and valid_repair_attempt(
            repair_data.get("current_attempt"),
            repair_data.get("attempts_used"),
            "system_design",
        )
    )
    normal_system = (
        planning.get("status") == "PLANNING"
        and planning.get("phase") == "system_design"
        and planning["gates"]["system_design"] == "PENDING"
    )
    if not normal_system and not system_repair and not intentional_revision:
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
    expected_version = (
        repair_data["superseded_system_design"]["candidate_version"] + 1
        if system_repair
        else planning["acceptances"]["system_design"]["candidate_version"] + 1
        if intentional_revision
        else 1
    )
    if type(frontmatter.get("version")) is not int or frontmatter.get("version") != expected_version:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            f"candidate version must equal integer {expected_version}",
            "system_design",
            f"write candidate version {expected_version}",
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

    headings = markdown_h2_headings(body)
    if headings != SYSTEM_DESIGN_SECTIONS:
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "System Design section sequence does not match the exact Stage 3 shape",
            "system_design",
            "restore each required System Design section exactly once and in order",
        ))

    candidate_sha256 = report["candidate_sha256"]
    predecessor = (
        repair_data["superseded_system_design"]
        if system_repair
        else planning["acceptances"]["system_design"]
        if intentional_revision
        else None
    )
    if predecessor is not None and (
        candidate_sha256 == predecessor["candidate_sha256"]
        or (
            system_repair
            and candidate_sha256 == repair_data["current_attempt"]["candidate_sha256_before"]
        )
    ):
        gaps.append(gap(
            SYSTEM_DESIGN_FILE,
            "revision candidate bytes must differ from the superseded design"
            + " and reserved pre-write candidate" if system_repair else "revision candidate bytes must differ from the superseded design",
            "system_design",
            "write a changed N+1 System Design candidate",
        ))

    source = frontmatter.get("source_binding")
    source_valid = False
    product = planning["stage0_anchor"]["product_closure"]
    if system_repair or intentional_revision:
        if not isinstance(predecessor, dict):  # pragma: no cover - guarded by branch predicates
            raise ControlError("System Design revision predecessor is unavailable")
        expected = predecessor["source_bindings"][0]
        if (
            not isinstance(source, dict)
            or set(source) != set(expected)
            or not json_equal_exact(source, expected)
        ):
            gaps.append(gap(
                SYSTEM_DESIGN_FILE,
                "source_binding does not match the superseded System Design source",
                "system_design",
                "preserve the superseded System Design source binding unchanged",
            ))
        else:
            source_valid = True
    elif product is not None:
        expected = {
            "kind": "product_closure",
            "artifact": "20-prd.md",
            "version": product["version"],
            "sha256": product["sha256"],
        }
        if not isinstance(source, dict) or set(source) != PRODUCT_SOURCE_FIELDS or source != expected:
            gaps.append(gap(
                SYSTEM_DESIGN_FILE,
                "source_binding does not match the exact accepted Product Definition Approval source",
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


def program_design_report(
    run_dir: Path,
    planning: dict[str, Any],
    effective: dict[str, Any],
) -> dict[str, Any]:
    gaps: list[dict[str, str]] = []
    report: dict[str, Any] = {
        "version": 1,
        "run": planning["run"],
        "verdict": "BLOCKED",
        "stage": "program_design",
        "boundary": "program_design",
        "repository_baselines": effective["repos"],
        "gaps": gaps,
    }
    repository_verification = atlas_repository.verify_run(run_dir)
    for item in repository_verification.gaps:
        artifact = (
            f"repository:{item.repository}"
            if item.repository is not None
            else "repositories.bindings"
        )
        gaps.append(gap(
            artifact,
            f"{item.code}: {item.problem}",
            "program_design",
            item.resume_action,
        ))
    if planning["phase"] != "program_design" or planning["gates"]["program_design"] != "PENDING":
        gaps.append(gap(
            PLANNING_FILE,
            "program_design is not the current pending planning boundary",
            "program_design",
            "resume the current planning-control phase",
        ))
    try:
        path = managed_path(run_dir, PROGRAM_DESIGN_FILE)
    except ControlError as exc:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            str(exc),
            "program_design",
            "replace the candidate with a real run-local file",
        ))
        return report
    if not path.is_file():
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "candidate file is missing",
            "program_design",
            f"produce {PROGRAM_DESIGN_FILE}",
        ))
        return report
    report["candidate_sha256"] = file_sha256(path)
    try:
        frontmatter, body = read_frontmatter(path)
    except (ControlError, yaml.YAMLError, UnicodeError) as exc:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            str(exc),
            "program_design",
            "repair candidate frontmatter",
        ))
        return report
    candidate_version = frontmatter.get("version")
    if type(candidate_version) is int:
        report["candidate_version"] = candidate_version
    if set(frontmatter) != PROGRAM_DESIGN_FIELDS:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "candidate frontmatter does not match its exact schema",
            "program_design",
            "repair candidate frontmatter",
        ))
    if "participation" in frontmatter:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "Program Design candidate must not declare participation",
            "program_design",
            "remove participation from Program Design frontmatter",
        ))
    if frontmatter.get("run") != planning["run"]:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "candidate run identity does not match planning-control.json",
            "program_design",
            "bind the candidate to this run",
        ))
    if type(frontmatter.get("version")) is not int or frontmatter.get("version") != 1:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "candidate version must equal integer 1",
            "program_design",
            "write candidate version 1",
        ))
    if frontmatter.get("status") != "draft":
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "producer candidate status must remain draft",
            "program_design",
            "record readiness without acceptance",
        ))
    if frontmatter.get("gate_ready") is not True:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "producer has not recorded gate readiness",
            "program_design",
            "finish the candidate and set gate_ready true",
        ))
    try:
        candidate_opened = canonical_date(frontmatter.get("opened"), "candidate opened")
        intake_opened = canonical_date(effective.get("opened"), "intake opened")
    except ControlError:
        candidate_opened = intake_opened = None
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "candidate opened date is not canonical YYYY-MM-DD",
            "program_design",
            "copy the canonical intake opened date",
        ))
    if candidate_opened is not None and candidate_opened != intake_opened:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "candidate opened date differs from frozen intake",
            "program_design",
            "copy the intake opened date",
        ))

    headings = program_design_headings(body)
    if headings != PROGRAM_DESIGN_SECTIONS:
        gaps.append(gap(
            PROGRAM_DESIGN_FILE,
            "Program Design section sequence does not match the exact Stage 4 shape",
            "program_design",
            "restore each required Program Design section exactly once and in order",
        ))

    source = frontmatter.get("source_binding")
    source_valid = False
    system_acceptance = planning["acceptances"]["system_design"]
    if "system_design" in effective["stages"]:
        expected = {
            "kind": "system_design",
            "artifact": SYSTEM_DESIGN_FILE,
            "version": system_acceptance["candidate_version"] if isinstance(system_acceptance, dict) else None,
            "sha256": system_acceptance["candidate_sha256"] if isinstance(system_acceptance, dict) else None,
        }
        if (
            not isinstance(system_acceptance, dict)
            or not isinstance(source, dict)
            or set(source) != PRODUCT_SOURCE_FIELDS
            or type(source.get("version")) is not int
            or source != expected
        ):
            gaps.append(gap(
                PROGRAM_DESIGN_FILE,
                "source_binding does not match the exact accepted System Design",
                "program_design",
                "bind source_binding to the accepted 30-system-design.md version and sha256",
            ))
        else:
            source_valid = True
    elif "discovery" in effective["stages"]:
        product = planning["stage0_anchor"]["product_closure"]
        expected = {
            "kind": "product_closure",
            "artifact": "20-prd.md",
            "version": product["version"] if isinstance(product, dict) else None,
            "sha256": product["sha256"] if isinstance(product, dict) else None,
        }
        if (
            not isinstance(product, dict)
            or not isinstance(source, dict)
            or set(source) != PRODUCT_SOURCE_FIELDS
            or type(source.get("version")) is not int
            or source != expected
        ):
            gaps.append(gap(
                PROGRAM_DESIGN_FILE,
                "source_binding does not match the exact accepted Product Definition Approval source",
                "program_design",
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
        if (
            not isinstance(source, dict)
            or set(source) != STAGE0_SOURCE_FIELDS
            or type(source.get("effective_config_revision")) is not int
            or source != expected
        ):
            gaps.append(gap(
                PROGRAM_DESIGN_FILE,
                "source_binding does not match the exact frozen Stage 0 admission",
                "program_design",
                "bind source_binding to run.yaml and the effective configuration",
            ))
        else:
            source_valid = True
    report["source_binding"] = source if source_valid else None
    report["verdict"] = "PASS" if not gaps else "BLOCKED"
    return report


def ticket_graph_report(
    run_dir: Path,
    planning: dict[str, Any],
    effective: dict[str, Any],
) -> dict[str, Any]:
    gaps: list[dict[str, str]] = []
    report: dict[str, Any] = {
        "version": 1,
        "run": planning["run"],
        "verdict": "BLOCKED",
        "stage": "tickets",
        "boundary": "tickets",
        "repository_baselines": effective["repos"],
        "gaps": gaps,
    }
    repository_verification = atlas_repository.verify_run(run_dir)
    for item in repository_verification.gaps:
        artifact = f"repository:{item.repository}" if item.repository is not None else "repositories.bindings"
        gaps.append(gap(artifact, f"{item.code}: {item.problem}", "tickets", item.resume_action))
    pending_tickets = (
        planning.get("status") == "PLANNING"
        and planning.get("phase") == "tickets"
        and planning["gates"].get("tickets") == "PENDING"
    )
    accepted_tickets = (
        planning.get("status") == "READY_FOR_EXECUTION"
        and planning.get("phase") == "tickets"
        and planning["gates"].get("tickets") in {"HUMAN_APPROVED", "AGENT_APPROVED"}
        and planning["acceptances"].get("tickets") is not None
    )
    if not pending_tickets and not accepted_tickets:
        gaps.append(gap(
            PLANNING_FILE,
            "tickets is not the current pending planning boundary",
            "tickets",
            "resume the current planning-control phase",
        ))
    manifest_path = managed_path(run_dir, TICKET_GRAPH_FILE)
    if not manifest_path.is_file() or manifest_path.is_symlink():
        gaps.append(gap(
            TICKET_GRAPH_FILE,
            "ticket-graph manifest is missing or not a real file",
            "tickets",
            f"produce {TICKET_GRAPH_FILE}",
        ))
        return report
    report["candidate_sha256"] = file_sha256(manifest_path)
    try:
        manifest = load_json(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        gaps.append(gap(TICKET_GRAPH_FILE, str(exc), "tickets", "repair the duplicate-safe JSON manifest"))
        return report
    if not isinstance(manifest, dict) or set(manifest) != TICKET_GRAPH_FIELDS:
        gaps.append(gap(
            TICKET_GRAPH_FILE,
            "ticket-graph manifest does not match its exact schema",
            "tickets",
            "repair the exact manifest fields",
        ))
        return report
    candidate_version = manifest.get("version")
    if type(candidate_version) is int:
        report["candidate_version"] = candidate_version
    if type(candidate_version) is not int or candidate_version != CURRENT_TICKET_GRAPH_VERSION:
        problem = (
            "graph version 1 is raw historical evidence only and is not loadable or factory-executable"
            if candidate_version == 1
            else f"graph version must equal integer {CURRENT_TICKET_GRAPH_VERSION}"
        )
        gaps.append(gap(
            TICKET_GRAPH_FILE,
            problem,
            "tickets",
            f"compile a current graph at version {CURRENT_TICKET_GRAPH_VERSION}",
        ))
    if manifest.get("run") != planning["run"]:
        gaps.append(gap(TICKET_GRAPH_FILE, "graph run does not match planning-control.json", "tickets", "bind the graph to this run"))
    if manifest.get("status") != "draft":
        gaps.append(gap(TICKET_GRAPH_FILE, "producer graph status must remain draft", "tickets", "record readiness without acceptance"))
    if manifest.get("gate_ready") is not True:
        gaps.append(gap(TICKET_GRAPH_FILE, "producer has not recorded graph readiness", "tickets", "finish the graph and set gate_ready true"))

    expected_sources = expected_ticket_graph_sources(planning, effective)
    source_bindings = manifest.get("source_bindings")
    if not isinstance(source_bindings, list) or not json_equal_exact(source_bindings, expected_sources):
        gaps.append(gap(
            TICKET_GRAPH_FILE,
            "source_bindings do not match every applicable accepted selected-path source",
            "tickets",
            "bind the graph to the exact applicable accepted sources",
        ))
        report["source_bindings"] = None
    else:
        report["source_bindings"] = source_bindings
    if manifest.get("repository_baselines") != effective["repos"]:
        gaps.append(gap(
            TICKET_GRAPH_FILE,
            "repository_baselines do not match frozen effective repositories",
            "tickets",
            "bind every target repository to its exact frozen baseline",
        ))

    entries = manifest.get("tickets")
    if not isinstance(entries, list) or not entries:
        gaps.append(gap(TICKET_GRAPH_FILE, "graph must contain at least one ticket", "tickets", "compile the complete ticket set"))
        return report
    raw_entry_ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    entry_ids = [ticket_id for ticket_id in raw_entry_ids if isinstance(ticket_id, str)]
    if (
        len(entry_ids) != len(entries)
        or len(set(entry_ids)) != len(entry_ids)
        or any(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ticket_id) is None for ticket_id in entry_ids)
    ):
        gaps.append(gap(TICKET_GRAPH_FILE, "ticket identities must be unique stable slugs", "tickets", "repair ticket identities"))
    preferred_order = manifest.get("preferred_order")
    if (
        not isinstance(preferred_order, list)
        or any(not isinstance(ticket_id, str) for ticket_id in preferred_order)
        or len(set(preferred_order)) != len(preferred_order)
        or set(preferred_order) != set(entry_ids)
    ):
        gaps.append(gap(TICKET_GRAPH_FILE, "preferred_order must contain every ticket exactly once", "tickets", "write the canonical preferred order"))

    expected_paths: set[str] = set()
    tickets: dict[str, dict[str, Any]] = {}
    source_kinds = {item["kind"] for item in expected_sources}
    source_sections: dict[str, set[str]] = {"stage0": set()}
    for source in expected_sources:
        source_kind = source["kind"]
        if source_kind == "stage0":
            continue
        source_path = managed_path(run_dir, source["artifact"])
        try:
            _, source_body = read_frontmatter(source_path)
        except (ControlError, yaml.YAMLError, UnicodeError) as exc:
            gaps.append(gap(
                source["artifact"],
                f"accepted source cannot resolve ticket reference sections: {exc}",
                "tickets",
                "restore the exact accepted source bytes",
            ))
            source_sections[source_kind] = set()
        else:
            source_sections[source_kind] = set(markdown_h2_headings(source_body))
    repositories = {item["repository"] for item in effective["repos"]}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != TICKET_GRAPH_ENTRY_FIELDS:
            gaps.append(gap(TICKET_GRAPH_FILE, "ticket index entry does not match its exact schema", "tickets", "repair every ticket index entry"))
            continue
        ticket_id = entry.get("id")
        if not isinstance(ticket_id, str):
            continue
        expected_path = f"tickets/{ticket_id}.md"
        if entry.get("path") != expected_path:
            gaps.append(gap(TICKET_GRAPH_FILE, f"ticket {ticket_id} path is not canonical", "tickets", f"use {expected_path}"))
            continue
        expected_paths.add(expected_path)
        if re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))) is None:
            gaps.append(gap(TICKET_GRAPH_FILE, f"ticket {ticket_id} hash is malformed", "tickets", "record the exact ticket SHA-256"))
        try:
            ticket_path = managed_path(run_dir, expected_path)
        except ControlError as exc:
            gaps.append(gap(expected_path, str(exc), "tickets", "replace the ticket with a managed run-local file"))
            continue
        if not ticket_path.is_file() or ticket_path.is_symlink():
            gaps.append(gap(expected_path, "ticket is missing or not a real file", "tickets", "write the exact indexed ticket file"))
            continue
        if file_sha256(ticket_path) != entry.get("sha256"):
            gaps.append(gap(expected_path, "ticket bytes do not match the manifest hash", "tickets", "recompile the manifest from exact ticket bytes"))
        try:
            frontmatter, body = read_frontmatter(ticket_path)
        except (ControlError, yaml.YAMLError, UnicodeError) as exc:
            gaps.append(gap(expected_path, str(exc), "tickets", "repair ticket frontmatter"))
            continue
        if not isinstance(frontmatter, dict) or set(frontmatter) != TICKET_FIELDS:
            gaps.append(gap(expected_path, "ticket frontmatter does not match its exact schema", "tickets", "repair ticket frontmatter"))
            continue
        tickets[ticket_id] = frontmatter
        if frontmatter.get("id") != ticket_id:
            gaps.append(gap(expected_path, "ticket identity does not match its index entry", "tickets", "bind the file to its indexed identity"))
        if frontmatter.get("kind") not in {"vertical", "enabling"}:
            gaps.append(gap(expected_path, "ticket kind must be vertical or enabling", "tickets", "classify the ticket exactly"))
        if frontmatter.get("status") != "ready":
            gaps.append(gap(expected_path, "ticket planning status must be ready", "tickets", "finish the ticket contract"))
        if frontmatter.get("repository") not in repositories:
            gaps.append(gap(expected_path, "ticket repository is not a frozen target", "tickets", "use one exact frozen repository identity"))
        if type(frontmatter.get("tracer")) is not bool:
            gaps.append(gap(expected_path, "ticket tracer must be boolean", "tickets", "record explicit tracer identity"))
        headings = markdown_h2_headings(body)
        if headings != ("What becomes true", "Acceptance", "Execution context"):
            gaps.append(gap(expected_path, "ticket body does not match the exact human-readable shape", "tickets", "restore What becomes true, Acceptance, and Execution context"))

        dependencies = frontmatter.get("blocked_by")
        if not isinstance(dependencies, list) or any(
            not isinstance(item, dict)
            or set(item) != TICKET_DEPENDENCY_FIELDS
            or not nonempty_string(item.get("ticket"))
            or not nonempty_string(item.get("establishes"))
            for item in dependencies or []
        ):
            gaps.append(gap(expected_path, "blocked_by must contain exact prerequisite identities and reasons", "tickets", "repair truthful dependency entries"))
        elif len({item["ticket"] for item in dependencies}) != len(dependencies):
            gaps.append(gap(expected_path, "blocked_by contains duplicate prerequisites", "tickets", "deduplicate prerequisite edges"))

        context = frontmatter.get("context")
        context_sources = (
            context.get("sources")
            if isinstance(context, dict) and set(context) == TICKET_CONTEXT_FIELDS
            else None
        )
        raw_context_kinds = [
            item.get("kind") for item in context_sources or [] if isinstance(item, dict)
        ]
        context_kinds = [kind for kind in raw_context_kinds if isinstance(kind, str)]
        context_is_valid = not (
            not isinstance(context_sources, list)
            or not context_sources
            or any(
                not isinstance(item, dict)
                or set(item) != TICKET_CONTEXT_SOURCE_FIELDS
                or not nonempty_string(item.get("kind"))
                or item.get("kind") not in source_kinds
                or not isinstance(item.get("sections"), list)
                or any(not nonempty_string(section) for section in item.get("sections", []))
                or len(item.get("sections", [])) != len(set(item.get("sections", [])))
                or not nonempty_string(item.get("purpose"))
                or (item.get("kind") == "stage0" and item.get("sections") != [])
                or (
                    item.get("kind") != "stage0"
                    and (
                        not item.get("sections")
                        or any(
                            section not in source_sections.get(str(item.get("kind")), set())
                            for section in item.get("sections", [])
                        )
                    )
                )
                for item in context_sources or []
            )
            or len(context_kinds) != len(context_sources or [])
            or len(context_kinds) != len(set(context_kinds))
            or set(context_kinds) != source_kinds
        )
        if not context_is_valid:
            gaps.append(gap(
                expected_path,
                "ticket context source declarations must exactly cover applicable sources with resolved sections and nonempty purpose",
                "tickets",
                "declare each applicable selected-path context source exactly once",
            ))
        elif (
            isinstance(context_sources, list)
            and ticket_execution_context_lines(body)
            != expected_ticket_execution_context_lines(context_sources)
        ):
            gaps.append(gap(
                expected_path,
                "ticket Execution context must exactly mirror the ordered context.sources declarations",
                "tickets",
                "render one exact Execution context line per declared source, including its sections and purpose",
            ))

        validators = frontmatter.get("validators")
        validator_ids = [item.get("id") for item in validators or [] if isinstance(item, dict)]
        valid_validator_ids = {item for item in validator_ids if isinstance(item, str)}
        if (
            not isinstance(validators, list)
            or not validators
            or any(
                not isinstance(item, dict)
                or set(item) != TICKET_VALIDATOR_FIELDS
                or not nonempty_string(item.get("id"))
                or not nonempty_string(item.get("command"))
                or item.get("success") != "exit_zero"
                for item in validators or []
            )
            or len(set(validator_ids)) != len(validator_ids)
        ):
            gaps.append(gap(expected_path, "validators must be unique deterministic exit-zero commands", "tickets", "declare sufficient deterministic validators"))
        outcomes = frontmatter.get("outcomes")
        outcome_ids = [item.get("id") for item in outcomes or [] if isinstance(item, dict)]
        if (
            not isinstance(outcomes, list)
            or not outcomes
            or any(
                not isinstance(item, dict)
                or set(item) != TICKET_OUTCOME_FIELDS
                or not nonempty_string(item.get("id"))
                or not nonempty_string(item.get("promise"))
                or not isinstance(item.get("acceptance"), list)
                or not item.get("acceptance")
                or any(not nonempty_string(value) for value in item.get("acceptance", []))
                or not isinstance(item.get("validator_ids"), list)
                or not item.get("validator_ids")
                or any(
                    not isinstance(value, str)
                    or value not in valid_validator_ids
                    for value in item.get("validator_ids", [])
                )
                for item in outcomes or []
            )
            or len(set(outcome_ids)) != len(outcome_ids)
        ):
            gaps.append(gap(expected_path, "every promised outcome requires observable acceptance and deterministic validator proof", "tickets", "bind each promised outcome to sufficient deterministic validators"))

        reviews = frontmatter.get("reviews")
        if (
            not isinstance(reviews, list)
            or any(
                not isinstance(item, str)
                or item not in {"semantic", "design", "quality"}
                for item in reviews or []
            )
            or len(set(reviews)) != len(reviews)
        ):
            gaps.append(gap(expected_path, "reviews must use unique supplemental review kinds", "tickets", "declare only semantic, design, or quality review obligations"))
        externals = frontmatter.get("external_prerequisites")
        if not isinstance(externals, list):
            gaps.append(gap(expected_path, "external_prerequisites must be a list", "tickets", "declare observable external readiness conditions"))
        else:
            external_ids: list[str] = []
            for item in externals:
                if not isinstance(item, dict) or set(item) != TICKET_EXTERNAL_FIELDS:
                    gaps.append(gap(expected_path, "external prerequisite does not match its exact schema", "tickets", "repair the external prerequisite"))
                    continue
                external_id = item.get("id")
                if isinstance(external_id, str):
                    external_ids.append(external_id)
                satisfaction = item.get("satisfaction")
                valid_satisfaction = False
                if isinstance(satisfaction, dict) and satisfaction.get("kind") == "command":
                    valid_satisfaction = (
                        set(satisfaction) == TICKET_COMMAND_SATISFACTION_FIELDS
                        and nonempty_string(satisfaction.get("command"))
                        and satisfaction.get("success") == "exit_zero"
                    )
                elif isinstance(satisfaction, dict) and satisfaction.get("kind") == "human_assertion":
                    valid_satisfaction = (
                        set(satisfaction) == TICKET_HUMAN_SATISFACTION_FIELDS
                        and satisfaction.get("authority") == "HUMAN"
                        and nonempty_string(satisfaction.get("statement"))
                        and nonempty_string(satisfaction.get("provenance"))
                    )
                if not nonempty_string(external_id) or not nonempty_string(item.get("condition")) or not valid_satisfaction:
                    gaps.append(gap(expected_path, "external prerequisite lacks an observable satisfaction rule", "tickets", "declare a command or provenance-bearing HUMAN assertion"))
            if len(external_ids) != len(set(external_ids)):
                gaps.append(gap(expected_path, "external prerequisite identities are duplicated", "tickets", "deduplicate external prerequisites"))

        enabling = frontmatter.get("enabling")
        if frontmatter.get("kind") == "vertical" and enabling is not None:
            gaps.append(gap(expected_path, "vertical ticket must not declare enabling metadata", "tickets", "remove enabling metadata"))
        if frontmatter.get("kind") == "enabling" and (
            not isinstance(enabling, dict)
            or set(enabling) != TICKET_ENABLING_FIELDS
            or not nonempty_string(enabling.get("consumer"))
            or not nonempty_string(enabling.get("rationale"))
        ):
            gaps.append(gap(expected_path, "enabling ticket must name its imminent consumer and inlining rationale", "tickets", "bind the enabling ticket to one imminent vertical consumer"))

    tickets_dir = managed_path(run_dir, "tickets")
    if not tickets_dir.is_dir() or tickets_dir.is_symlink():
        gaps.append(gap("tickets", "tickets directory is missing or not a real directory", "tickets", "write the indexed ticket directory"))
    else:
        actual_paths = {
            path.relative_to(run_dir).as_posix()
            for path in tickets_dir.iterdir()
            if path.is_file() or path.is_symlink()
        }
        if actual_paths != expected_paths:
            gaps.append(gap("tickets", "ticket directory contents do not exactly match the manifest", "tickets", "remove unindexed tickets and restore missing indexed tickets"))

    all_ids = set(entry_ids)
    for ticket_id, ticket in tickets.items():
        dependencies = ticket.get("blocked_by")
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            dependency_id = dependency.get("ticket") if isinstance(dependency, dict) else None
            if not isinstance(dependency_id, str):
                continue
            if dependency_id == ticket_id:
                gaps.append(gap(f"tickets/{ticket_id}.md", "ticket cannot depend on itself", "tickets", "remove the self-dependency"))
            elif dependency_id not in all_ids:
                gaps.append(gap(f"tickets/{ticket_id}.md", f"dependency {dependency_id} is not in the graph", "tickets", "repair the dependency reference"))
        if ticket.get("kind") == "enabling" and isinstance(ticket.get("enabling"), dict):
            consumer_id = ticket["enabling"].get("consumer")
            consumer = tickets.get(consumer_id) if isinstance(consumer_id, str) else None
            consumer_dependencies = consumer.get("blocked_by") if isinstance(consumer, dict) else None
            if (
                not isinstance(consumer, dict)
                or consumer.get("kind") != "vertical"
                or not isinstance(consumer_dependencies, list)
                or ticket_id not in {
                    item.get("ticket")
                    for item in consumer_dependencies
                    if isinstance(item, dict) and isinstance(item.get("ticket"), str)
                }
            ):
                gaps.append(gap(f"tickets/{ticket_id}.md", "enabling ticket does not block its named imminent vertical consumer", "tickets", "make the named vertical consumer depend on this enabling ticket"))

    visiting: set[str] = set()
    visited: set[str] = set()
    cycle = False
    def visit(ticket_id: str) -> None:
        nonlocal cycle
        if ticket_id in visiting:
            cycle = True
            return
        if ticket_id in visited:
            return
        visiting.add(ticket_id)
        ticket = tickets.get(ticket_id, {})
        for dependency in ticket.get("blocked_by", []) if isinstance(ticket, dict) else []:
            dependency_id = dependency.get("ticket") if isinstance(dependency, dict) else None
            if isinstance(dependency_id, str) and dependency_id in all_ids:
                visit(dependency_id)
        visiting.remove(ticket_id)
        visited.add(ticket_id)
    for ticket_id in entry_ids:
        visit(ticket_id)
    if cycle:
        gaps.append(gap(TICKET_GRAPH_FILE, "ticket dependency graph contains a cycle", "tickets", "remove the cyclic prerequisite edge"))

    tracer_ticket = manifest.get("tracer_ticket")
    tracer_ids = [
        ticket_id
        for ticket_id, ticket in tickets.items()
        if ticket.get("tracer") is True
    ]
    if tracer_ticket is None:
        if tracer_ids:
            gaps.append(gap(TICKET_GRAPH_FILE, "graph has tracer tickets but no tracer_ticket identity", "tickets", "record the one tracer identity in the manifest"))
    elif (
        not isinstance(tracer_ticket, str)
        or len(tracer_ids) != 1
        or tracer_ids[0] != tracer_ticket
        or tracer_ticket not in tickets
        or tickets[tracer_ticket].get("kind") != "vertical"
    ):
        gaps.append(gap(TICKET_GRAPH_FILE, "tracer_ticket must name exactly one real vertical tracer", "tickets", "bind tracer_ticket to the graph's one explicit vertical tracer"))
    if not any(stage in effective["stages"] for stage in ("discovery", "system_design", "program_design")) and len(entries) != 1:
        gaps.append(gap(TICKET_GRAPH_FILE, "trivial path must compile exactly one one-node ticket graph", "tickets", "compile one ticket directly from frozen Stage 0"))

    report["preferred_order"] = preferred_order
    report["tracer_ticket"] = tracer_ticket
    report["verdict"] = "PASS" if not gaps else "BLOCKED"
    return report


def check_boundary(run_dir: Path, stage: str) -> dict[str, Any]:
    planning, _, effective = verified_planning_state(run_dir)
    if stage == "system_design":
        return system_design_report(run_dir, planning, effective)
    if stage == "program_design":
        return program_design_report(run_dir, planning, effective)
    if stage == "tickets":
        return ticket_graph_report(run_dir, planning, effective)
    raise ControlError("check supports only --stage system_design, program_design, or tickets")


def resolve_system_design_authority(
    run_dir: Path,
    effective: dict[str, Any],
    candidate_version: int,
    candidate_sha256: str,
    approval: Optional[str],
    review_reference: Optional[str],
    repair_context: Optional[dict[str, Any]] = None,
) -> tuple[str, Optional[str]]:
    policy = effective.get("gates", {}).get("system_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    if configured == "HUMAN":
        if repair_context is None and review_reference is not None:
            raise ControlError("configured HUMAN System Design gate does not accept --review")
        if approval != "human":
            raise ControlError("HUMAN System Design gate requires explicit --approval human")
        if repair_context is None:
            return "HUMAN", None
        _, review_sha256, mapped = load_system_design_review(
            run_dir,
            effective,
            candidate_version,
            candidate_sha256,
            review_reference,
            repair_context,
        )
        if mapped != "HUMAN":
            raise ControlError("direct HUMAN repair evidence cannot grant a different authority")
        return "HUMAN", review_sha256
    if configured in {"AGENT_REVIEW", "HUMAN_IF_CHANGED"}:
        _, review_sha256, mapped = load_system_design_review(
            run_dir,
            effective,
            candidate_version,
            candidate_sha256,
            review_reference,
            repair_context,
        )
        if mapped == "AGENT_REVIEW":
            if approval is not None:
                raise ControlError(f"configured {configured} System Design gate does not fall back to human approval")
        elif approval != "human":
            raise ControlError("HUMAN_IF_CHANGED mapped HUMAN requires explicit --approval human")
        return mapped, review_sha256
    raise ControlError(f"system_design authority {configured} is an intentionally unimplemented Slice-2B capability")


def resolve_program_design_authority(
    run_dir: Path,
    effective: dict[str, Any],
    candidate_version: int,
    candidate_sha256: str,
    source_kind: str,
    approval: Optional[str],
    review_reference: Optional[str],
) -> tuple[str, str]:
    require_program_design_repository_access(run_dir)
    policy = effective.get("gates", {}).get("program_design", {})
    configured = policy.get("authority") if isinstance(policy, dict) else None
    _, review_sha256 = load_program_design_review(
        run_dir,
        effective,
        candidate_version,
        candidate_sha256,
        source_kind,
        review_reference,
    )
    if configured == "AGENT_REVIEW":
        if approval is not None:
            raise ControlError("configured AGENT_REVIEW Program Design gate does not accept human approval")
        return "AGENT_REVIEW", review_sha256
    if configured == "HUMAN":
        if approval != "human":
            raise ControlError("HUMAN Program Design gate requires explicit --approval human after PASS review")
        return "HUMAN", review_sha256
    raise ControlError("Program Design supports only configured AGENT_REVIEW or HUMAN authority")


def resolve_ticket_graph_authority(
    run_dir: Path,
    effective: dict[str, Any],
    candidate_version: int,
    candidate_sha256: str,
    source_bindings: list[dict[str, Any]],
    approval: Optional[str],
    review_reference: Optional[str],
) -> tuple[str, str]:
    _, review_sha256 = load_ticket_graph_review(
        run_dir,
        effective,
        candidate_version,
        candidate_sha256,
        source_bindings,
        review_reference,
    )
    authority = effective["gates"]["tickets"]["authority"]
    if authority == "AGENT_REVIEW":
        if approval is not None:
            raise ControlError("AGENT_REVIEW tickets gate does not accept human approval")
    elif authority == "HUMAN":
        if approval != "human":
            raise ControlError("HUMAN tickets gate requires explicit --approval human after PASS review")
    else:  # pragma: no cover - policy validation restricts outcomes
        raise ControlError("tickets policy mapped to an unsupported authority")
    return authority, review_sha256


def advance_ticket_graph_boundary(
    run_dir: Path,
    approval: Optional[str],
    review_reference: Optional[str],
    accepted: str,
) -> str:
    planning, _, effective = verified_planning_state(run_dir)
    if (
        planning.get("status") != "PLANNING"
        or planning.get("phase") != "tickets"
        or planning["gates"].get("tickets") != "PENDING"
        or planning["acceptances"].get("tickets") is not None
    ):
        raise ControlError("tickets is not the current pending planning boundary")
    report = ticket_graph_report(run_dir, planning, effective)
    if report["verdict"] != "PASS":
        raise ControlError("mechanical tickets boundary check is BLOCKED")
    accepted = canonical_date(accepted, "acceptance date")
    candidate_version: int = report["candidate_version"]
    candidate_sha256: str = report["candidate_sha256"]
    source_bindings: list[dict[str, Any]] = report["source_bindings"]
    authority, review_sha256 = resolve_ticket_graph_authority(
        run_dir,
        effective,
        candidate_version,
        candidate_sha256,
        source_bindings,
        approval,
        review_reference,
    )

    final_report = ticket_graph_report(run_dir, planning, effective)
    if (
        final_report.get("verdict") != "PASS"
        or final_report.get("candidate_version") != candidate_version
        or final_report.get("candidate_sha256") != candidate_sha256
        or not json_equal_exact(final_report.get("source_bindings"), source_bindings)
    ):
        raise ControlError("ticket graph or source bindings changed before acceptance")
    try:
        final_planning, _, final_effective = verified_planning_state(run_dir)
        final_authority = resolve_ticket_graph_authority(
            run_dir,
            final_effective,
            candidate_version,
            candidate_sha256,
            source_bindings,
            approval,
            review_reference,
        )
    except ControlError as exc:
        raise ControlError("ticket graph, source bindings, policy, or review changed before acceptance") from exc
    if final_planning != planning or final_authority != (authority, review_sha256):
        raise ControlError("planning-control.json, policy, or review changed before ticket-graph acceptance")

    def revalidate_immediately_before_replace() -> None:
        current_planning, _, current_effective = verified_planning_state(run_dir)
        current_report = ticket_graph_report(run_dir, current_planning, current_effective)
        current_authority = resolve_ticket_graph_authority(
            run_dir,
            current_effective,
            candidate_version,
            candidate_sha256,
            source_bindings,
            approval,
            review_reference,
        )
        if (
            current_planning != planning
            or current_report.get("verdict") != "PASS"
            or current_report.get("candidate_version") != candidate_version
            or current_report.get("candidate_sha256") != candidate_sha256
            or not json_equal_exact(current_report.get("source_bindings"), source_bindings)
            or current_authority != (authority, review_sha256)
        ):
            raise ControlError("ticket graph, source bindings, policy, or review changed at the write boundary")

    final_planning["acceptances"]["tickets"] = {
        "candidate_version": candidate_version,
        "candidate_sha256": candidate_sha256,
        "authority": authority,
        "accepted": accepted,
        "review_reference": review_reference,
        "review_sha256": review_sha256,
        "source_bindings": source_bindings,
        "repository_baselines": final_effective["repos"],
    }
    final_planning["gates"]["tickets"] = (
        "HUMAN_APPROVED" if authority == "HUMAN" else "AGENT_APPROVED"
    )
    final_planning["status"] = "READY_FOR_EXECUTION"
    final_planning["phase"] = "tickets"
    final_planning["revision"] += 1
    write_planning_control_atomic(
        run_dir,
        final_planning,
        precondition=revalidate_immediately_before_replace,
    )
    load_planning_control(run_dir)
    return f"accepted tickets -> READY_FOR_EXECUTION; planning-control revision {final_planning['revision']}"


def advance_program_design_boundary(
    run_dir: Path,
    approval: Optional[str],
    review_reference: Optional[str],
    accepted: str,
) -> str:
    planning, _, effective = verified_planning_state(run_dir)
    report = program_design_report(run_dir, planning, effective)
    if report["verdict"] != "PASS":
        raise ControlError("mechanical program_design boundary check is BLOCKED")
    accepted = canonical_date(accepted, "acceptance date")
    candidate_version: int = report["candidate_version"]
    candidate_sha256: str = report["candidate_sha256"]
    source_binding = report["source_binding"]
    authority, review_sha256 = resolve_program_design_authority(
        run_dir,
        effective,
        candidate_version,
        candidate_sha256,
        source_binding["kind"],
        approval,
        review_reference,
    )

    selected = [item for item in DOWNSTREAM_STAGES if item in effective["stages"]]
    index = selected.index("program_design")
    if index + 1 >= len(selected) or selected[index + 1] != "tickets":
        raise ControlError("program_design has no selected later tickets boundary")

    final_report = program_design_report(run_dir, planning, effective)
    if (
        final_report.get("verdict") != "PASS"
        or final_report.get("candidate_version") != candidate_version
        or final_report.get("candidate_sha256") != candidate_sha256
        or final_report.get("source_binding") != source_binding
    ):
        raise ControlError("candidate or source binding changed before Program Design acceptance")
    try:
        final_planning, _, final_effective = verified_planning_state(run_dir)
        final_authority = resolve_program_design_authority(
            run_dir,
            final_effective,
            candidate_version,
            candidate_sha256,
            source_binding["kind"],
            approval,
            review_reference,
        )
    except ControlError as exc:
        raise ControlError("candidate, source binding, policy, or review changed before Program Design acceptance") from exc
    if final_planning != planning or final_authority != (authority, review_sha256):
        raise ControlError("planning-control.json, policy, or review changed before Program Design acceptance")

    def revalidate_immediately_before_replace() -> None:
        current_planning, _, current_effective = verified_planning_state(run_dir)
        current_report = program_design_report(run_dir, current_planning, current_effective)
        current_authority = resolve_program_design_authority(
            run_dir,
            current_effective,
            candidate_version,
            candidate_sha256,
            source_binding["kind"],
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
            raise ControlError("candidate, source binding, policy, or review changed at the Program Design write boundary")

    final_planning["acceptances"]["program_design"] = {
        "candidate_version": candidate_version,
        "candidate_sha256": candidate_sha256,
        "authority": authority,
        "accepted": accepted,
        "review_reference": review_reference,
        "review_sha256": review_sha256,
        "source_bindings": [source_binding],
        "repository_baselines": final_effective["repos"],
    }
    final_planning["gates"]["program_design"] = (
        "HUMAN_APPROVED" if authority == "HUMAN" else "AGENT_APPROVED"
    )
    final_planning["phase"] = "tickets"
    final_planning["revision"] += 1
    repair_episode = planning.get("blocked_reason")
    if (
        isinstance(repair_episode, dict)
        and repair_episode.get("state") == "PROGRAM_DESIGN_RESUMED"
    ):
        final_planning["status"] = "PLANNING"
        final_planning["blocked_reason"] = None
    write_planning_control_atomic(
        run_dir,
        final_planning,
        precondition=revalidate_immediately_before_replace,
    )
    load_planning_control(run_dir)
    return f"advanced program_design -> tickets; planning-control revision {final_planning['revision']}"


def advance_boundary(
    run_dir: Path,
    stage: str,
    approval: Optional[str],
    review_reference: Optional[str],
    accepted: str,
) -> str:
    if stage == "tickets":
        return advance_ticket_graph_boundary(run_dir, approval, review_reference, accepted)
    if stage == "program_design":
        return advance_program_design_boundary(run_dir, approval, review_reference, accepted)
    if stage != "system_design":
        raise ControlError("advance supports only system_design, program_design, or tickets acceptance")
    planning, _, effective = verified_planning_state(run_dir)
    planning_path = managed_path(run_dir, PLANNING_FILE)
    planning_bytes = planning_path.read_bytes()
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
    repair_episode = planning.get("blocked_reason")
    repair_context = (
        expected_system_repair_context(run_dir, planning, planning["revision"] + 1)
        if isinstance(repair_episode, dict)
        and repair_episode.get("state") == "SYSTEM_DESIGN_STALE"
        else None
    )
    authority, review_sha256 = resolve_system_design_authority(
        run_dir,
        effective,
        candidate_version,
        candidate_sha256,
        approval,
        review_reference,
        repair_context,
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
            repair_context,
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
            repair_context,
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
    if repair_context is not None:
        final_planning["status"] = "BLOCKED"
        final_planning["blocked_reason"]["state"] = "PROGRAM_DESIGN_RESUMED"
        final_planning["blocked_reason"]["current_attempt"] = None
    if repair_context is None:
        write_planning_control_atomic(
            run_dir,
            final_planning,
            precondition=revalidate_immediately_before_replace,
        )
        load_planning_control(run_dir)
    else:
        final_bytes = planning_control_bytes(final_planning)
        try:
            write_planning_control_atomic(
                run_dir,
                final_planning,
                precondition=revalidate_immediately_before_replace,
            )
            load_planning_control(run_dir)
        except BaseException as exc:
            try:
                current_bytes = planning_path.read_bytes()
            except BaseException as inspection_exc:
                raise ControlError(
                    "System Design repair acceptance failed and resulting planning state could not be inspected"
                ) from inspection_exc
            if current_bytes == final_bytes:
                try:
                    write_planning_control_bytes_atomic(run_dir, planning_bytes)
                    if planning_path.read_bytes() != planning_bytes:
                        raise ControlError("prior planning bytes did not survive rollback")
                except BaseException as rollback_exc:
                    raise ControlError(
                        "System Design repair acceptance failed and prior state could not be restored"
                    ) from rollback_exc
                if isinstance(exc, Exception):
                    raise ControlError(
                        f"System Design repair acceptance failed final validation and was rolled back: {exc}"
                    ) from exc
                raise
            if current_bytes != planning_bytes:
                raise ControlError(
                    "System Design repair acceptance failed after planning state changed independently"
                ) from exc
            raise
    return f"advanced system_design -> {next_stage}; planning-control revision {final_planning['revision']}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    initialize = sub.add_parser("initialize")
    initialize.add_argument("--run", required=True, type=Path)
    ensure = sub.add_parser("ensure")
    ensure.add_argument("--run", required=True, type=Path)
    revise_system = sub.add_parser("begin-system-design-revision")
    revise_system.add_argument("--run", required=True, type=Path)
    inspect = sub.add_parser("check")
    inspect.add_argument("--run", required=True, type=Path)
    inspect.add_argument("--stage", required=True, choices=("system_design", "program_design", "tickets"))
    advance = sub.add_parser("advance")
    advance.add_argument("--run", required=True, type=Path)
    advance.add_argument("--stage", required=True, choices=("system_design", "program_design", "tickets"))
    advance.add_argument("--approval", choices=("human",))
    advance.add_argument("--review")
    advance.add_argument("--date", required=True)
    return_upstream = sub.add_parser("return-upstream")
    return_upstream.add_argument("--run", required=True, type=Path)
    return_upstream.add_argument("--review-input", required=True, type=Path)
    reserve_attempt = sub.add_parser("reserve-repair-attempt")
    reserve_attempt.add_argument("--run", required=True, type=Path)
    reserve_attempt.add_argument(
        "--stage",
        required=True,
        choices=("system_design", "program_design"),
    )
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
            elif args.command == "begin-system-design-revision":
                print(begin_system_design_revision(run_dir))
            elif args.command == "advance":
                print(advance_boundary(run_dir, args.stage, args.approval, args.review, args.date))
            elif args.command == "return-upstream":
                print(return_to_system_design(run_dir, args.review_input))
            elif args.command == "reserve-repair-attempt":
                print(json.dumps(reserve_repair_attempt(run_dir, args.stage), sort_keys=True))
            else:  # pragma: no cover
                return 2
        return 0
    except (ControlError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"atlas-planning: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
