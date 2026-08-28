#!/usr/bin/env python3
"""Tiny deterministic controller for Atlas planning Stages 0–2.

Discovery continuously authors the decision log and living PRD. ``check`` is
read-only and validates the Product Definition Approval boundary mechanically. HUMAN or
AGENT_REVIEW authority supplies semantic acceptance. This program alone
replaces the feature's authoritative ``control.json``.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterator, Optional

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - POSIX
    msvcrt = None

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment failure
    raise SystemExit("atlas_control requires PyYAML (`python -m pip install pyyaml`)") from exc


CONTROL_FILE = "control.json"
LOCK_FILE = ".atlas-control.lock"
DECISIONS_FILE = "10-decisions.md"
PRD_FILE = "20-prd.md"
PRD_HTML_FILE = "20-prd.html"
RENDERER_VERSION = "1.0.0"
CANDIDATES = {"discovery": PRD_FILE}
EXIT_BOUNDARY = {"discovery": "product_closure"}
PRODUCT_DEFINITION_STAGE_LABEL = "Product Definition Approval"
PRODUCT_DEFINITION_ACTION = "Approve the product definition"
PRODUCT_DEFINITION_HELPER = (
    "Confirm the PRD and recorded decisions are complete enough to begin System Design."
)
CANDIDATE_FIELDS = {
    "discovery": {
        "run", "version", "status", "gate_ready", "intake_stale", "cold_read",
        "effective_config_revision", "opened", "repos", "derived_from",
    },
}
CONTROL_FIELDS = {
    "version", "run", "status", "phase", "revision", "base_run_sha256",
    "effective_config_hash", "effective_config_revision", "accepted_amendment_count",
    "gates", "blocked_reason", "acceptances",
}
ACCEPTANCE_FIELDS = {
    "candidate_version", "candidate_sha256", "authority", "accepted",
    "review_reference", "review_sha256",
}
REVIEW_FIELDS = {
    "version", "run", "stage", "candidate_version", "candidate_sha256", "verdict", "gaps",
}
GAP_FIELDS = {"code", "artifact", "problem", "resume_stage", "resume_action"}
AMENDMENT_FIELDS = {
    "version", "amendment", "applies_to", "status", "accepted", "reason", "changes",
}
RUN_FIELDS = {
    "version", "run", "opened", "goal", "planning_root", "run_path", "recommendation",
    "workflow", "stages", "governance", "gates", "execution_policy", "environment_policy",
    "roster", "risk", "repos", "overrides",
}
RUN_V2_FIELDS = {
    "version", "run", "opened", "goal", "planning_root", "run_path", "recommendation",
    "workflow", "stages", "system_design_participation", "governance", "gates",
    "execution_policy", "environment_policy", "roster", "risk", "repos", "overrides",
}
PRD_SECTIONS = (
    "Problem", "Goals and outcomes", "Non-goals", "Actors", "Scenarios",
    "Requirements", "Invariants", "Contracts and interfaces",
    "Edge and failure cases", "Observability", "Acceptance outcomes", "Open questions",
)
DECISION_FIELDS = {
    "id", "route", "findings", "status", "decided", "origin", "confidence", "unblocked",
    "blocked_by", "supersedes", "contribution",
}
DECISION_LOG_FIELDS = {"run", "version"}
RUN_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class ControlError(RuntimeError):
    pass


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable YAML key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate YAML key: {key}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def load_yaml(text: str) -> Any:
    return yaml.load(text, Loader=UniqueKeyLoader)


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ControlError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=reject_duplicate_json_keys)


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.duplicates: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "meta":
            return
        pairs = {key.lower(): value or "" for key, value in attrs}
        name = pairs.get("name")
        if name in {
            "atlas-source", "atlas-source-sha256", "atlas-renderer-version",
        }:
            if name in self.meta:
                self.duplicates.add(name)
            self.meta[name] = pairs.get("content", "")


def canonical_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ControlError("canonical maps require string keys")
        return {key: canonical_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [canonical_value(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ControlError(f"unsupported canonical value: {type(value).__name__}")


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        canonical_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ControlError(f"{field} must be a non-empty string")
    return value


def canonical_date(value: Any, field: str) -> str:
    value = canonical_value(value)
    try:
        if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError as exc:
        raise ControlError(f"{field} must be canonical YYYY-MM-DD") from exc
    return value


def managed_path(run_dir: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise ControlError(f"managed path escapes the run: {relative}")
    current = run_dir
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ControlError(f"managed path uses a symlink: {relative}")
    if not current.resolve(strict=False).is_relative_to(run_dir.resolve()):
        raise ControlError(f"managed path escapes the run: {relative}")
    return current


def read_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ControlError(f"missing YAML frontmatter: {path.name}")
    raw, body = text[4:].split("\n---\n", 1)
    data = load_yaml(raw)
    if not isinstance(data, dict):
        raise ControlError(f"frontmatter is not a map: {path.name}")
    return data, body


def load_run(run_dir: Path) -> dict[str, Any]:
    path = managed_path(run_dir, "run.yaml")
    data = load_yaml(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ControlError("run.yaml is not a map")
    return data


def validate_repos(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ControlError("repos must be a non-empty list")
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != {"repository", "baseline"}:
            raise ControlError("repos entries must be exact repository/baseline maps")
        repository = item.get("repository")
        baseline = item.get("baseline")
        if not isinstance(repository, str) or not repository.strip() or repository in seen:
            raise ControlError("repository identities must be non-empty and unique")
        if not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-fA-F]{7,64}", baseline):
            raise ControlError("repository baseline must be a 7-64 character commit SHA")
        seen.add(repository)
    return value


def validate_run_slug(value: Any) -> str:
    slug = require_string(value, "run slug")
    if not RUN_SLUG.fullmatch(slug):
        raise ControlError("run slug must use lowercase letters, digits, and single hyphens")
    return slug


def resolve_run_path(planning_root: Path, slug_value: Any) -> dict[str, Any]:
    slug = validate_run_slug(slug_value)
    if not planning_root.is_absolute():
        raise ControlError("planning root must be an absolute path")
    if planning_root.is_symlink():
        raise ControlError("planning root may not be a symlink")
    if not planning_root.is_dir():
        raise ControlError("planning root must already exist as a directory")
    root = planning_root.resolve(strict=True)
    target = root / slug
    if target.is_symlink():
        raise ControlError("run target may not be a symlink")
    try:
        target.mkdir(mode=0o700)
    except FileExistsError:
        if target.is_symlink() or not target.is_dir():
            raise ControlError("existing run target must be a real directory")
    resolved = target.resolve(strict=False)
    if resolved.parent != root:
        raise ControlError("run target must remain directly beneath the planning root")
    identity = os.stat(resolved, follow_symlinks=False)
    return {
        "path": str(resolved),
        "device": identity.st_dev,
        "inode": identity.st_ino,
    }


def resolve_existing_run_directory(
    path: Path,
    *,
    prepared_device: Optional[int] = None,
    prepared_inode: Optional[int] = None,
) -> Path:
    if path.is_symlink():
        raise ControlError("run directory may not be a symlink")
    try:
        before = os.stat(path, follow_symlinks=False)
    except FileNotFoundError as exc:
        raise ControlError("run directory does not exist") from exc
    if not stat.S_ISDIR(before.st_mode):
        raise ControlError("run path must be a directory")
    if (prepared_device is None) != (prepared_inode is None):
        raise ControlError("prepared directory identity is incomplete")
    if prepared_device is not None:
        if prepared_device < 0 or prepared_inode is None or prepared_inode <= 0:
            raise ControlError("prepared directory identity is invalid")
        if (before.st_dev, before.st_ino) != (prepared_device, prepared_inode):
            raise ControlError("run path no longer matches the prepared directory identity")
    resolved = path.resolve(strict=True)
    after = os.stat(resolved, follow_symlinks=False)
    if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
        raise ControlError("run directory changed while it was being opened")
    return resolved


def system_design_participation(config: dict[str, Any]) -> Optional[str]:
    participation = config.get("system_design_participation")
    selected = "system_design" in config.get("stages", [])
    if selected:
        if participation not in {"agent_led", "co_design"}:
            raise ControlError("selected system_design requires explicit agent_led or co_design participation")
        return participation
    if participation is not None:
        raise ControlError("omitted system_design requires null participation")
    return None


def validate_run(config: dict[str, Any]) -> None:
    version = config.get("version")
    if type(version) is not int or version not in {1, 2}:
        raise ControlError("run.yaml version must be integer 1 or 2")
    expected_fields = RUN_FIELDS if version == 1 else RUN_V2_FIELDS
    if set(config) != expected_fields:
        raise ControlError(f"run.yaml fields do not match version-{version} schema")
    run = validate_run_slug(config.get("run"))
    if config.get("run_path") != run:
        raise ControlError("run.yaml run_path must equal run")
    canonical_date(config.get("opened"), "run.yaml opened")
    require_string(config.get("goal"), "run.yaml goal")
    validate_repos(config.get("repos"))
    stages = config.get("stages")
    if (
        not isinstance(stages, list)
        or not stages
        or any(not isinstance(stage, str) or not stage.strip() for stage in stages)
        or len(stages) != len(set(stages))
        or "spec" in stages
    ):
        raise ControlError("run.yaml stages must be a non-empty unique string list and may not contain legacy spec")
    gates = config.get("gates")
    if (
        not isinstance(gates, dict)
        or "spec" in gates
    ):
        raise ControlError("run.yaml gates must be a map and may not contain legacy spec")
    discovery_selected = "discovery" in stages
    if version == 2:
        system_design_participation(config)
    if discovery_selected and stages[0] != "discovery":
        raise ControlError("selected discovery must be the first stage")
    if discovery_selected != ("discovery" in gates):
        raise ControlError("run.yaml discovery gate must exist exactly when discovery is selected")
    for stage, policy in gates.items():
        if not isinstance(policy, dict) or not isinstance(policy.get("authority"), str):
            raise ControlError(f"run.yaml gate policy is malformed: {stage}")
    if discovery_selected and gates["discovery"].get("authority") not in {"AGENT_REVIEW", "HUMAN"}:
        raise ControlError("the semantic discovery boundary requires AGENT_REVIEW or HUMAN")
    tickets_policy = gates.get("tickets")
    if tickets_policy is not None and (
        set(tickets_policy) != {"authority"}
        or tickets_policy.get("authority") not in {"AGENT_REVIEW", "HUMAN"}
    ):
        raise ControlError("tickets supports only AGENT_REVIEW or HUMAN")
    root = config.get("planning_root")
    if not isinstance(root, dict) or set(root) != {"source", "mode", "path"}:
        raise ControlError("run.yaml planning_root is malformed")
    if root.get("source") != "artifacts.planning_root" or root.get("mode") not in {
        "repository-relative", "external",
    }:
        raise ControlError("run.yaml planning_root is invalid")


def amendment_paths(run_dir: Path) -> list[Path]:
    directory = managed_path(run_dir, "amendments")
    return sorted(directory.glob("[0-9][0-9][0-9]-*.md")) if directory.is_dir() else []


def apply_amendment_data(effective: dict[str, Any], path: Path, number: int) -> dict[str, Any]:
    if path.is_symlink():
        raise ControlError(f"amendment may not be a symlink: {path.name}")
    data, _ = read_frontmatter(path)
    if set(data) != AMENDMENT_FIELDS:
        raise ControlError(f"amendment fields do not match version-1 schema: {path.name}")
    if not path.name.startswith(f"{number:03d}-") or data.get("amendment") != number:
        raise ControlError(f"expected contiguous amendment {number:03d}-*.md")
    if data.get("version") != 1 or data.get("applies_to") != "run.yaml" or data.get("status") != "accepted":
        raise ControlError(f"amendment {path.name} is not accepted for run.yaml")
    canonical_date(data.get("accepted"), "amendment accepted")
    require_string(data.get("reason"), "amendment reason")
    changes = data.get("changes")
    if not isinstance(changes, dict) or set(changes) != {"repos"}:
        raise ControlError("Stage 0 amendments may replace only repos")
    validate_repos(changes["repos"])
    updated = dict(effective)
    updated["repos"] = changes["repos"]
    return updated


def effective_run(run_dir: Path, count: int) -> dict[str, Any]:
    effective = load_run(run_dir)
    paths = amendment_paths(run_dir)
    if len(paths) < count:
        raise ControlError("accepted amendment count exceeds available ordered amendments")
    for number, path in enumerate(paths[:count], 1):
        effective = apply_amendment_data(effective, path, number)
    return effective


def load_control(run_dir: Path) -> dict[str, Any]:
    path = managed_path(run_dir, CONTROL_FILE)
    try:
        control = load_json(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControlError("control.json is not valid JSON") from exc
    if not isinstance(control, dict):
        raise ControlError("control.json is not a map")
    if set(control) != CONTROL_FIELDS:
        raise ControlError("control.json fields do not match version-1 schema")
    gates = control.get("gates")
    acceptances = control.get("acceptances")
    if (
        not isinstance(gates, dict)
        or not isinstance(acceptances, dict)
        or set(acceptances) != set(gates)
        or any(
            record is not None and (not isinstance(record, dict) or set(record) != ACCEPTANCE_FIELDS)
            for record in acceptances.values()
        )
    ):
        raise ControlError("control.json acceptances are malformed")
    if (
        not isinstance(control.get("run"), str)
        or not control["run"]
        or control.get("status") not in {"PLANNING", "BLOCKED"}
        or not isinstance(control.get("phase"), str)
        or not isinstance(control.get("revision"), int)
        or isinstance(control.get("revision"), bool)
        or control["revision"] < 1
        or not re.fullmatch(r"[0-9a-f]{64}", str(control.get("base_run_sha256", "")))
        or not re.fullmatch(r"[0-9a-f]{64}", str(control.get("effective_config_hash", "")))
        or not isinstance(control.get("gates"), dict)
        or control.get("blocked_reason") is not None and not isinstance(control.get("blocked_reason"), str)
    ):
        raise ControlError("control.json values are malformed")
    for record in acceptances.values():
        if record is None:
            continue
        try:
            date.fromisoformat(record.get("accepted", ""))
        except (TypeError, ValueError) as exc:
            raise ControlError("control.json acceptance is malformed") from exc
        authority = record.get("authority")
        review_ref = record.get("review_reference")
        review_sha = record.get("review_sha256")
        if (
            not isinstance(record.get("candidate_version"), int)
            or isinstance(record.get("candidate_version"), bool)
            or record["candidate_version"] < 1
            or not re.fullmatch(r"[0-9a-f]{64}", str(record.get("candidate_sha256", "")))
            or authority not in {"HUMAN", "AGENT_REVIEW"}
            or (authority == "HUMAN" and (review_ref is not None or review_sha is not None))
            or (authority == "AGENT_REVIEW" and (
                not isinstance(review_ref, str)
                or not re.fullmatch(r"[0-9a-f]{64}", str(review_sha or ""))
            ))
        ):
            raise ControlError("control.json acceptance is malformed")
    return control


def section(body: str, heading: str) -> Optional[str]:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", body)
    return match.group(1) if match else None


def gap(artifact: str, problem: str, stage: str, action: str) -> dict[str, str]:
    slug = re.sub(r"[^a-z0-9]+", "-", problem.lower()).strip("-")[:48]
    return {
        "code": f"{stage}-{slug}",
        "artifact": artifact,
        "problem": problem,
        "resume_stage": stage,
        "resume_action": action,
    }


def expected_candidate_version(control: dict[str, Any], stage: str) -> int:
    record = control.get("acceptances", {}).get(stage)
    return record["candidate_version"] + 1 if isinstance(record, dict) else 1


def latest_acceptance(control: dict[str, Any], stage: str) -> Optional[dict[str, Any]]:
    record = control.get("acceptances", {}).get(stage)
    return record if isinstance(record, dict) else None


def parse_meta(path: Path) -> dict[str, str]:
    parser = MetaParser()
    parser.feed(path.read_text(encoding="utf-8"))
    if parser.duplicates:
        raise ControlError(f"duplicate atlas metadata: {sorted(parser.duplicates)}")
    return parser.meta


def parse_decision_records(body: str) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    gaps: list[dict[str, str]] = []
    matches = list(re.finditer(r"(?m)^### (D-[0-9]{3})\s+—\s+.+$", body))
    identifiers = [match.group(1) for match in matches]
    if not identifiers:
        gaps.append(gap(DECISIONS_FILE, "no decision identifiers are present", "discovery", "record settled decisions"))
        return {}, gaps
    if len(identifiers) != len(set(identifiers)):
        gaps.append(gap(DECISIONS_FILE, "decision identifiers are not unique", "discovery", "assign unique D-NNN identifiers"))
    decisions: dict[str, dict[str, Any]] = {}
    superseded_targets: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        fenced = re.search(r"```yaml\n(.*?)```", body[match.end():end], re.S)
        if not fenced:
            gaps.append(gap(DECISIONS_FILE, f"{match.group(1)} has no YAML record", "discovery", "add the required decision record fields"))
            continue
        try:
            record = load_yaml(fenced.group(1))
        except yaml.YAMLError as exc:
            gaps.append(gap(DECISIONS_FILE, f"{match.group(1)} has invalid YAML: {exc}", "discovery", "repair the decision record"))
            continue
        decision_id = match.group(1)
        if not isinstance(record, dict) or set(record) != DECISION_FIELDS or record.get("id") != decision_id:
            gaps.append(gap(DECISIONS_FILE, f"{decision_id} record fields are incomplete or mismatched", "discovery", "repair the decision record"))
            continue
        if record.get("status") not in {"settled", "superseded"}:
            gaps.append(gap(DECISIONS_FILE, f"{decision_id} is not settled or superseded", "discovery", "settle or supersede the decision"))
        if record.get("contribution") not in {"load-bearing", "minor", "irrelevant"}:
            gaps.append(gap(DECISIONS_FILE, f"{decision_id} contribution grade is invalid", "discovery", "grade contribution as load-bearing, minor, or irrelevant"))
        supersedes = record.get("supersedes")
        if supersedes is not None and not re.fullmatch(r"D-[0-9]{3}", str(supersedes)):
            gaps.append(gap(DECISIONS_FILE, f"{decision_id} supersedes field is invalid", "discovery", "repair the supersedes field"))
            supersedes = None
        if isinstance(supersedes, str):
            if supersedes not in identifiers[:index]:
                gaps.append(gap(DECISIONS_FILE, f"{decision_id} supersedes must name an earlier distinct decision", "discovery", "repair supersession ordering"))
            else:
                superseded_targets.append(supersedes)
        decisions[decision_id] = record
    for target in superseded_targets:
        target_record = decisions.get(target)
        if target_record is None:
            gaps.append(gap(DECISIONS_FILE, f"{target} is named in supersedes but no such decision exists", "discovery", "repair supersession references"))
        elif target_record.get("status") != "superseded":
            gaps.append(gap(DECISIONS_FILE, f"{target} is superseded by a later decision but still marked settled", "discovery", "mark the earlier decision superseded"))
    frontier = section(body, "Open frontier")
    if frontier is None:
        gaps.append(gap(DECISIONS_FILE, "Open frontier section is absent", "discovery", "record the open frontier"))
    else:
        table_lines = [line.strip() for line in frontier.splitlines() if line.strip().startswith("|")]
        expected_header = ("Question", "Route", "Blocked by")
        malformed = len(table_lines) < 2
        if not malformed:
            header_cells = tuple(cell.strip() for cell in table_lines[0].split("|")[1:-1])
            separator_cells = [cell.strip() for cell in table_lines[1].split("|")[1:-1]]
            malformed = (
                header_cells != expected_header
                or len(separator_cells) != 3
                or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in separator_cells)
            )
        if malformed:
            gaps.append(gap(DECISIONS_FILE, "Open frontier table is malformed", "discovery", "restore the exact frontier table"))
        elif table_lines[2:]:
            gaps.append(gap(DECISIONS_FILE, "open frontier still contains unresolved entries", "discovery", "resolve every frontier entry"))
    cold_read = section(body, "Cold-read evidence")
    if cold_read is None:
        gaps.append(gap(DECISIONS_FILE, "Cold-read evidence section is absent", "discovery", "record baseline findings and their disposition"))
    else:
        table_lines = [line.strip() for line in cold_read.splitlines() if line.strip().startswith("|")]
        malformed = len(table_lines) < 3
        if not malformed:
            header_cells = tuple(cell.strip() for cell in table_lines[0].split("|")[1:-1])
            separator_cells = [cell.strip() for cell in table_lines[1].split("|")[1:-1]]
            rows = [tuple(cell.strip() for cell in line.split("|")[1:-1]) for line in table_lines[2:]]
            placeholder_values = {"pending", "pending.", "todo", "tbd", "—", "-"}
            malformed = (
                header_cells != ("Finding", "Disposition")
                or len(separator_cells) != 2
                or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in separator_cells)
                or any(len(row) != 2 or not row[0] or not row[1] for row in rows)
                or any(cell.strip().lower() in placeholder_values for row in rows for cell in row)
                or len({row[0] for row in rows}) != len(rows)
            )
        if malformed:
            gaps.append(gap(DECISIONS_FILE, "Cold-read evidence table is malformed", "discovery", "record one unique row per finding with a non-empty disposition"))
    return decisions, gaps


def parse_retrospective(body: str) -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    gaps: list[dict[str, str]] = []
    headings = re.findall(r"(?m)^## ([^\n]+?)\s*$", body)
    retrospective_count = headings.count("PRD alignment retrospective")
    if retrospective_count != 1:
        gaps.append(gap(DECISIONS_FILE, "PRD alignment retrospective must appear exactly once", "discovery", "keep one retrospective table"))
    if headings and headings[-1] != "PRD alignment retrospective":
        gaps.append(gap(DECISIONS_FILE, "PRD alignment retrospective must be the final section", "discovery", "move trailing material before the retrospective"))
    retrospective = section(body, "PRD alignment retrospective")
    if retrospective is None:
        gaps.append(gap(DECISIONS_FILE, "PRD alignment retrospective section is absent", "discovery", "rebuild the retrospective table"))
        return {}, gaps
    lines = [line.strip() for line in retrospective.splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if len(table_lines) < 2:
        gaps.append(gap(DECISIONS_FILE, "PRD alignment retrospective table is malformed", "discovery", "rebuild the retrospective table"))
        return {}, gaps
    expected_header = (
        "Decision",
        "Disposition",
        "PRD identifiers",
        "Reason (required iff NO_NORMATIVE_EFFECT)",
    )
    header_cells = tuple(cell.strip() for cell in table_lines[0].split("|")[1:-1])
    separator_cells = [cell.strip() for cell in table_lines[1].split("|")[1:-1]]
    if header_cells != expected_header:
        gaps.append(gap(DECISIONS_FILE, "PRD alignment retrospective table header is not exact", "discovery", "restore the required retrospective columns"))
    if len(separator_cells) != 4 or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in separator_cells):
        gaps.append(gap(DECISIONS_FILE, "PRD alignment retrospective table separator is malformed", "discovery", "repair the retrospective table separator"))
    rows = table_lines[2:]
    parsed: dict[str, dict[str, str]] = {}
    for line in rows:
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 4:
            gaps.append(gap(DECISIONS_FILE, "PRD alignment retrospective row is malformed", "discovery", "repair the retrospective row"))
            continue
        decision_id, disposition, prd_ids, reason = cells
        if not re.fullmatch(r"D-[0-9]{3}", decision_id):
            gaps.append(gap(DECISIONS_FILE, f"retrospective names an invalid decision identifier: {decision_id}", "discovery", "repair the retrospective row"))
            continue
        if decision_id in parsed:
            gaps.append(gap(DECISIONS_FILE, f"retrospective duplicates decision {decision_id}", "discovery", "keep exactly one row per live decision"))
            continue
        if disposition not in {"NORMATIVE", "NO_NORMATIVE_EFFECT"}:
            gaps.append(gap(DECISIONS_FILE, f"retrospective disposition is invalid for {decision_id}", "discovery", "use NORMATIVE or NO_NORMATIVE_EFFECT"))
            continue
        parsed[decision_id] = {
            "decision": decision_id,
            "disposition": disposition,
            "prd_ids": prd_ids,
            "reason": reason,
        }
    return parsed, gaps


def parse_prd_items(body: str) -> tuple[dict[str, set[str]], list[dict[str, str]]]:
    gaps: list[dict[str, str]] = []
    section_sequence = tuple(re.findall(r"(?m)^## ([^\n]+?)\s*$", body))
    if section_sequence != PRD_SECTIONS:
        gaps.append(gap(PRD_FILE, "PRD section sequence does not match the exact product contract", "discovery", "restore the required PRD sections and order"))
    for heading in PRD_SECTIONS:
        if len(re.findall(rf"(?m)^## {re.escape(heading)}\s*$", body)) != 1:
            gaps.append(gap(PRD_FILE, f"required section {heading} must appear exactly once", "discovery", f"repair section {heading}"))
    if re.search(r"(?im)^## (Work Items|Files|Classes|Methods|Implementation|Tickets)\s*$", body):
        gaps.append(gap(PRD_FILE, "PRD contains an internal design or ticket section", "discovery", "move internal shape downstream"))
    open_questions = section(body, "Open questions") or ""
    if re.search(
        r"(?im)^[ \t]*(?:(?:[-+*]|[0-9]+[.)]|>)[ \t]*)?(?:[*_]{1,2})?blocking(?:[*_]{1,2})?[ \t]*:",
        open_questions,
    ) or re.search(r"(?im)^\s*\|.*\bblocking\b.*\|", open_questions):
        gaps.append(gap(PRD_FILE, "PRD contains a blocking open question", "discovery", "resolve the behavior-changing question"))

    matches = list(re.finditer(r"(?m)^### ([RPCIX]-[0-9]{3})\s+—\s+.+$", body))
    identifiers = [match.group(1) for match in matches]
    if not identifiers:
        gaps.append(gap(PRD_FILE, "no normative identifiers are present", "discovery", "record at least one normative R/P/C/I/X-NNN obligation"))
        return {}, gaps
    if len(identifiers) != len(set(identifiers)):
        gaps.append(gap(PRD_FILE, "normative identifiers are not unique", "discovery", "assign unique normative identifiers"))
    items: dict[str, set[str]] = {}
    for match in matches:
        trailing = body[match.end():]
        next_heading = re.search(r"(?m)^#{1,3}\s+", trailing)
        end = match.end() + next_heading.start() if next_heading else len(body)
        block = body[match.end():end]
        derived_matches = re.findall(r"(?mi)^\*\*Derived from:\*\*\s*(.+?)\s*$", block)
        item_id = match.group(1)
        if not derived_matches:
            gaps.append(gap(PRD_FILE, f"{item_id} is missing a Derived from list", "discovery", "cite one or more live decisions"))
            continue
        if len(derived_matches) != 1:
            gaps.append(gap(PRD_FILE, f"{item_id} must contain exactly one Derived from list", "discovery", "keep one exact citation line"))
            continue
        derived_value = derived_matches[0]
        cited = {
            token for token in re.findall(r"\bD-[0-9]{3}\b", derived_value)
        }
        if not cited:
            gaps.append(gap(PRD_FILE, f"{item_id} must cite one or more live decisions", "discovery", "cite one or more live decisions"))
            continue
        items[item_id] = cited
    return items, gaps


def validate_html_projection(run_dir: Path, markdown_hash: str) -> list[dict[str, str]]:
    path = managed_path(run_dir, PRD_HTML_FILE)
    gaps: list[dict[str, str]] = []
    if not path.is_file():
        gaps.append(gap(PRD_HTML_FILE, "20-prd.html is missing", "discovery", "render the PRD HTML projection"))
        return gaps
    try:
        meta = parse_meta(path)
    except (ControlError, OSError, UnicodeError) as exc:
        gaps.append(gap(PRD_HTML_FILE, str(exc), "discovery", "rerender the PRD HTML projection"))
        return gaps
    if meta.get("atlas-source") != PRD_FILE:
        gaps.append(gap(PRD_HTML_FILE, "20-prd.html does not declare 20-prd.md as its source", "discovery", "rerender the PRD HTML projection"))
    if meta.get("atlas-source-sha256") != markdown_hash:
        gaps.append(gap(PRD_HTML_FILE, "20-prd.html source sha256 does not match the current PRD bytes", "discovery", "rerender the PRD HTML projection"))
    if meta.get("atlas-renderer-version") != RENDERER_VERSION:
        gaps.append(gap(PRD_HTML_FILE, "20-prd.html renderer version is missing or unknown", "discovery", "rerender with the installed renderer"))
    return gaps


def accepted_source_gaps(run_dir: Path, record: dict[str, Any]) -> list[str]:
    prd_path = managed_path(run_dir, PRD_FILE)
    decisions_path = managed_path(run_dir, DECISIONS_FILE)
    problems: list[str] = []
    if not prd_path.is_file() or file_sha256(prd_path) != record.get("candidate_sha256"):
        problems.append("accepted PRD bytes no longer match recorded discovery provenance")
        return problems
    try:
        prd_frontmatter, _ = read_frontmatter(prd_path)
    except (ControlError, yaml.YAMLError) as exc:
        problems.append(str(exc))
        return problems
    derived_from = prd_frontmatter.get("derived_from")
    if not isinstance(derived_from, dict):
        problems.append("accepted PRD derived_from binding is malformed")
        return problems
    if not decisions_path.is_file():
        problems.append("accepted PRD decision source is missing")
        return problems
    try:
        decisions_frontmatter, _ = read_frontmatter(decisions_path)
    except (ControlError, yaml.YAMLError) as exc:
        problems.append(str(exc))
        return problems
    if (
        derived_from.get("artifact") != DECISIONS_FILE
        or derived_from.get("version") != decisions_frontmatter.get("version")
        or derived_from.get("sha256") != file_sha256(decisions_path)
    ):
        problems.append("accepted PRD no longer matches its bound decision source")
    if record.get("authority") == "AGENT_REVIEW":
        try:
            review_path = managed_path(run_dir, str(record.get("review_reference", "")))
        except ControlError as exc:
            problems.append(f"accepted review evidence path is invalid: {exc}")
        else:
            if not review_path.is_file():
                problems.append("accepted review evidence is missing")
            elif file_sha256(review_path) != record.get("review_sha256"):
                problems.append("accepted review evidence bytes no longer match recorded provenance")
    return problems


def verified_state(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    control = load_control(run_dir)
    if control.get("version") != 1:
        raise ControlError("unsupported control.json version")
    if file_sha256(managed_path(run_dir, "run.yaml")) != control.get("base_run_sha256"):
        raise ControlError("base run.yaml byte hash mismatch")
    count = control.get("accepted_amendment_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ControlError("accepted amendment count is invalid")
    effective = effective_run(run_dir, count)
    if canonical_hash(effective) != control.get("effective_config_hash"):
        raise ControlError("effective configuration hash mismatch")
    if control.get("effective_config_revision") != count:
        raise ControlError("effective configuration revision mismatch")
    if control.get("run") != effective.get("run"):
        raise ControlError("control run identity mismatch")
    stages = effective.get("stages", [])
    controlled_stages = {stage for stage in stages if stage in CANDIDATES}
    if set(control.get("gates", {})) != controlled_stages or control.get("phase") not in stages:
        raise ControlError("control.json gates/phase do not match the Stage 0–2 run boundary")
    allowed_gate_states = {"PENDING", "AGENT_APPROVED", "HUMAN_APPROVED", "REJECTED", "STALE"}
    if any(value not in allowed_gate_states for value in control["gates"].values()):
        raise ControlError("control.json gate state is invalid")
    approved_states = {"AGENT_APPROVED", "HUMAN_APPROVED"}
    for stage, record in control["acceptances"].items():
        gate_state = control["gates"].get(stage)
        if gate_state == "STALE" and record is not None:
            raise ControlError("STALE gate cannot retain an acceptance after reopen removal")
        if (gate_state in approved_states) != (record is not None):
            raise ControlError("control.json gate/acceptance coherence is invalid")
        if record is not None:
            expected_gate = "HUMAN_APPROVED" if record["authority"] == "HUMAN" else "AGENT_APPROVED"
            if gate_state != expected_gate:
                raise ControlError("control.json authority/gate coherence is invalid")
            for problem in accepted_source_gaps(run_dir, record):
                raise ControlError(problem)
    phase_index = stages.index(control["phase"])
    for stage, record in control["acceptances"].items():
        if stage in stages and stages.index(stage) < phase_index and record is None:
            raise ControlError("control.json phase/acceptance coherence is invalid")
        if stage in stages and stages.index(stage) > phase_index and record is not None:
            raise ControlError("control.json phase/acceptance coherence is invalid")
        if stage in stages and stages.index(stage) == phase_index and record is not None and control["gates"][stage] != "STALE":
            raise ControlError("control.json phase/acceptance coherence is invalid")
    if (control["status"] == "PLANNING") != (control["blocked_reason"] is None):
        raise ControlError("control.json status/block reason coherence is invalid")
    return control, effective


@contextlib.contextmanager
def run_lock(run_dir: Path) -> Iterator[None]:
    path = managed_path(run_dir, LOCK_FILE)
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
                raise ControlError("this platform has no supported run-lock primitive")
            acquired = True
        except (BlockingIOError, OSError) as exc:
            raise ControlError("another atlas-control process is active for this run") from exc
        yield
    finally:
        if acquired:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif msvcrt is not None:  # pragma: no cover
                os.lseek(fd, 0, os.SEEK_SET)
                getattr(msvcrt, "locking")(fd, getattr(msvcrt, "LK_UNLCK"), 1)
        os.close(fd)


def write_control_atomic(run_dir: Path, control: dict[str, Any]) -> None:
    path = managed_path(run_dir, CONTROL_FILE)
    content = json.dumps(control, indent=2, sort_keys=True) + "\n"
    fd, name = tempfile.mkstemp(prefix=".control.json.", dir=run_dir)
    temp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def projection_text(control: dict[str, Any]) -> str:
    projected = {
        "source": CONTROL_FILE,
        "feature": control["run"],
        "status": control["status"],
        "phase": control["phase"],
        "revision": control["revision"],
        "effective_config_revision": control["effective_config_revision"],
        "effective_config_hash": control["effective_config_hash"],
        "base_run_sha256": control["base_run_sha256"],
        "gates": control["gates"],
        "blocked_reason": control["blocked_reason"],
        "accepted_amendment_count": control["accepted_amendment_count"],
        "acceptances": control["acceptances"],
    }
    return "---\n" + yaml.safe_dump(projected, sort_keys=False) + "---\n\n# Atlas state projection\n"


def project_best_effort(run_dir: Path, control: dict[str, Any]) -> None:
    try:
        managed_path(run_dir, "00-state.md").write_text(projection_text(control), encoding="utf-8")
    except (ControlError, OSError) as exc:
        print(f"atlas-control: warning: state projection was not regenerated: {exc}", file=sys.stderr)


def commit(run_dir: Path, control: dict[str, Any]) -> None:
    write_control_atomic(run_dir, control)
    project_best_effort(run_dir, control)


def initialize(run_dir: Path) -> str:
    if managed_path(run_dir, CONTROL_FILE).exists():
        raise ControlError("control.json already exists")
    config = load_run(run_dir)
    validate_run(config)
    if managed_path(run_dir, DECISIONS_FILE).exists() or amendment_paths(run_dir):
        raise ControlError("initialize must run before decision records or amendments")
    stages = config["stages"]
    control = {
        "version": 1,
        "run": config["run"],
        "status": "PLANNING",
        "phase": stages[0],
        "revision": 1,
        "base_run_sha256": file_sha256(managed_path(run_dir, "run.yaml")),
        "effective_config_hash": canonical_hash(config),
        "effective_config_revision": 0,
        "accepted_amendment_count": 0,
        "gates": {stage: "PENDING" for stage in stages if stage in CANDIDATES},
        "blocked_reason": None,
        "acceptances": {stage: None for stage in stages if stage in CANDIDATES},
    }
    commit(run_dir, control)
    return "initialized control.json revision 1"


def candidate_report(run_dir: Path, control: dict[str, Any], effective: dict[str, Any]) -> dict[str, Any]:
    stage = str(control["phase"])
    artifact = CANDIDATES.get(stage)
    gaps: list[dict[str, str]] = []
    report: dict[str, Any] = {
        "version": 1,
        "run": control["run"],
        "verdict": "BLOCKED",
        "stage": stage,
        "boundary": EXIT_BOUNDARY.get(str(stage)),
        "gaps": gaps,
    }
    if artifact is None:
        gaps.append(gap(CONTROL_FILE, f"{stage} is outside the Stage 0–2 controller", str(stage), "use the next-stage controller"))
        return report
    prd_path = managed_path(run_dir, artifact)
    decisions_path = managed_path(run_dir, DECISIONS_FILE)
    if not prd_path.is_file():
        gaps.append(gap(artifact, "candidate file is missing", stage, f"produce {artifact}"))
        return report
    report["candidate_sha256"] = file_sha256(prd_path)
    try:
        prd_frontmatter, prd_body = read_frontmatter(prd_path)
    except (ControlError, yaml.YAMLError) as exc:
        gaps.append(gap(artifact, str(exc), stage, "repair candidate frontmatter"))
        return report
    candidate_version = prd_frontmatter.get("version")
    report["candidate_version"] = candidate_version
    expected = expected_candidate_version(control, stage)
    if not isinstance(candidate_version, int) or isinstance(candidate_version, bool) or candidate_version < 1:
        gaps.append(gap(artifact, "candidate version must be a positive integer", stage, f"write candidate version {expected}"))
    if set(prd_frontmatter) != CANDIDATE_FIELDS[stage]:
        gaps.append(gap(artifact, "candidate frontmatter does not match its exact schema", stage, "repair candidate frontmatter"))
    if prd_frontmatter.get("run") != control.get("run"):
        gaps.append(gap(artifact, "candidate run identity does not match control.json", stage, "bind the candidate to this run"))
    if prd_frontmatter.get("version") != expected:
        gaps.append(gap(artifact, f"candidate must use version {expected}", stage, f"write candidate version {expected}"))
    if prd_frontmatter.get("status") != "draft":
        gaps.append(gap(artifact, "producer candidate status must remain draft", stage, "record readiness without approval"))
    if prd_frontmatter.get("gate_ready") is not True:
        gaps.append(gap(artifact, "producer has not recorded gate readiness", stage, "finish the candidate and set gate_ready true"))
    effective_config_revision = prd_frontmatter.get("effective_config_revision")
    if (
        not isinstance(effective_config_revision, int)
        or isinstance(effective_config_revision, bool)
        or effective_config_revision != control.get("effective_config_revision")
    ):
        gaps.append(gap(artifact, "candidate uses a stale effective configuration revision", stage, "revalidate against effective intake"))
    if prd_frontmatter.get("intake_stale") is not False:
        gaps.append(gap(artifact, "discovery reports stale intake", "intake", "apply the next repository/baseline amendment"))
    if prd_frontmatter.get("cold_read") != "complete":
        gaps.append(gap(artifact, "cold-read evidence is incomplete", stage, "complete and disposition the cold read"))
    expected_repos = [item["repository"] for item in effective.get("repos", [])]
    if prd_frontmatter.get("repos") != expected_repos:
        gaps.append(gap(artifact, "declared repository scope differs from effective intake", stage, "revalidate repository scope"))
    if canonical_value(prd_frontmatter.get("opened")) != canonical_value(effective.get("opened")):
        gaps.append(gap(artifact, "candidate opened date differs from intake", stage, "copy the intake opened date"))

    if not decisions_path.is_file():
        gaps.append(gap(DECISIONS_FILE, "decision log is missing", stage, f"produce {DECISIONS_FILE}"))
        report["verdict"] = "BLOCKED"
        return report
    try:
        decisions_frontmatter, decisions_body = read_frontmatter(decisions_path)
    except (ControlError, yaml.YAMLError) as exc:
        gaps.append(gap(DECISIONS_FILE, str(exc), stage, "repair decision-log frontmatter"))
        report["verdict"] = "BLOCKED"
        return report

    if set(decisions_frontmatter) != DECISION_LOG_FIELDS:
        gaps.append(gap(DECISIONS_FILE, "decision-log frontmatter does not match its exact schema", stage, "repair decision-log frontmatter"))
    if decisions_frontmatter.get("run") != control.get("run"):
        gaps.append(gap(DECISIONS_FILE, "decision-log frontmatter run identity does not match control.json", stage, "bind the decision log to this run"))
    decision_log_version = decisions_frontmatter.get("version")
    if not isinstance(decision_log_version, int) or isinstance(decision_log_version, bool) or decision_log_version < 1:
        gaps.append(gap(DECISIONS_FILE, "decision-log frontmatter version must be a positive integer", stage, "repair decision-log frontmatter"))

    decisions, decision_gaps = parse_decision_records(decisions_body)
    gaps.extend(decision_gaps)
    retrospective_rows, retrospective_gaps = parse_retrospective(decisions_body)
    gaps.extend(retrospective_gaps)
    prd_items, prd_gaps = parse_prd_items(prd_body)
    gaps.extend(prd_gaps)
    gaps.extend(validate_html_projection(run_dir, report["candidate_sha256"]))

    derived_from = prd_frontmatter.get("derived_from")
    if not isinstance(derived_from, dict) or set(derived_from) != {"artifact", "version", "sha256"}:
        gaps.append(gap(PRD_FILE, "derived_from frontmatter is malformed", stage, "bind the PRD to the decision log bytes"))
    else:
        if derived_from.get("artifact") != DECISIONS_FILE:
            gaps.append(gap(PRD_FILE, "derived_from.artifact must equal 10-decisions.md", stage, "bind the PRD to the decision log"))
        derived_version = derived_from.get("version")
        if not isinstance(derived_version, int) or isinstance(derived_version, bool) or derived_version < 1:
            gaps.append(gap(PRD_FILE, "derived_from.version must be a positive integer", stage, "repair the derived_from version"))
        elif derived_version != decisions_frontmatter.get("version"):
            gaps.append(gap(PRD_FILE, "derived_from.version does not match the decision-log version", stage, "update the derived_from version"))
        if derived_from.get("sha256") != file_sha256(decisions_path):
            gaps.append(gap(PRD_FILE, "derived_from does not bind the current decision-log bytes", stage, "update the derived_from sha256"))

    live_decisions = {
        decision_id: record for decision_id, record in decisions.items()
        if record.get("status") == "settled"
    }
    if set(retrospective_rows) != set(live_decisions):
        missing = sorted(set(live_decisions) - set(retrospective_rows))
        extra = sorted(set(retrospective_rows) - set(live_decisions))
        if missing:
            gaps.append(gap(DECISIONS_FILE, f"retrospective is missing live decisions: {missing}", stage, "rebuild the retrospective table"))
        if extra:
            gaps.append(gap(DECISIONS_FILE, f"retrospective names nonexistent or superseded decisions: {extra}", stage, "remove invalid retrospective rows"))

    prd_ids = set(prd_items)
    for decision_id, row in retrospective_rows.items():
        identifier_tokens = re.findall(r"\b[RPCIX]-[0-9]{3}\b", row["prd_ids"])
        identifiers = set(identifier_tokens)
        if row["disposition"] == "NORMATIVE":
            if row["prd_ids"] != ", ".join(identifier_tokens) or len(identifier_tokens) != len(identifiers):
                gaps.append(gap(DECISIONS_FILE, f"retrospective PRD identifier list is malformed for {decision_id}", stage, "use a unique comma-space separated PRD identifier list"))
            if not identifiers:
                gaps.append(gap(DECISIONS_FILE, f"retrospective NORMATIVE row {decision_id} must cite one or more PRD identifiers", stage, "repair the retrospective row"))
            if row["reason"]:
                gaps.append(gap(DECISIONS_FILE, f"retrospective NORMATIVE row {decision_id} must leave reason empty", stage, "repair the retrospective row"))
        else:
            if row["prd_ids"]:
                gaps.append(gap(DECISIONS_FILE, f"retrospective NO_NORMATIVE_EFFECT row {decision_id} must leave PRD identifiers empty", stage, "repair the retrospective row"))
            if not row["reason"]:
                gaps.append(gap(DECISIONS_FILE, f"retrospective NO_NORMATIVE_EFFECT row {decision_id} must include a reason", stage, "repair the retrospective row"))
        unresolved_prd_ids = sorted(identifiers - prd_ids)
        if unresolved_prd_ids:
            gaps.append(gap(DECISIONS_FILE, f"retrospective cites nonexistent PRD identifiers for {decision_id}: {unresolved_prd_ids}", stage, "repair the retrospective row"))
        for item_id in sorted(identifiers & prd_ids):
            if decision_id not in prd_items[item_id]:
                gaps.append(gap(DECISIONS_FILE, f"retrospective points {decision_id} to {item_id}, but that PRD item does not cite {decision_id}", stage, "repair the retrospective and PRD citations"))

    for item_id, cited in prd_items.items():
        unresolved = sorted(cited - set(live_decisions))
        if unresolved:
            gaps.append(gap(PRD_FILE, f"{item_id} cites nonexistent or superseded decisions: {unresolved}", stage, "repair the PRD citations"))
            continue
        for decision_id in cited:
            row = retrospective_rows.get(decision_id)
            if row is None or row["disposition"] != "NORMATIVE":
                gaps.append(gap(PRD_FILE, f"{item_id} cites {decision_id} but the retrospective does not mark it NORMATIVE", stage, "repair the retrospective and PRD citations"))
                continue
            identifiers = {token for token in re.findall(r"\b[RPCIX]-[0-9]{3}\b", row["prd_ids"])}
            if item_id not in identifiers:
                gaps.append(gap(PRD_FILE, f"{item_id} cites {decision_id} but the retrospective does not point back to it", stage, "repair the retrospective and PRD citations"))

    report["verdict"] = "PASS" if not gaps else "BLOCKED"
    return report


def check(run_dir: Path) -> dict[str, Any]:
    control, effective = verified_state(run_dir)
    return candidate_report(run_dir, control, effective)


def validate_review(run_dir: Path, relative: str, report: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    expected_reference = f"reviews/product_closure-v{report.get('candidate_version')}.json"
    if relative != expected_reference:
        raise ControlError(f"review reference must equal {expected_reference}")
    path = managed_path(run_dir, relative)
    try:
        review = load_json(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControlError("review envelope is not valid JSON") from exc
    if not isinstance(review, dict) or set(review) != REVIEW_FIELDS:
        raise ControlError("review envelope fields do not match version-1 schema")
    review_version = review.get("version")
    if (
        review_version != 1
        or isinstance(review_version, bool)
        or review.get("run") != report.get("run")
        or review.get("stage") != report.get("boundary")
    ):
        raise ControlError("review envelope stage/version is invalid")
    review_candidate_version = review.get("candidate_version")
    if (
        not isinstance(review_candidate_version, int)
        or isinstance(review_candidate_version, bool)
        or review_candidate_version < 1
    ):
        raise ControlError("review envelope candidate version must be a positive integer")
    if review_candidate_version != report.get("candidate_version") or review.get("candidate_sha256") != report.get("candidate_sha256"):
        raise ControlError("review envelope is not bound to the current candidate version/hash")
    gaps = review.get("gaps")
    if (
        not isinstance(gaps, list)
        or any(not isinstance(item, dict) or set(item) != GAP_FIELDS for item in gaps)
        or any(
            any(not isinstance(item[field], str) or not item[field].strip() for field in GAP_FIELDS)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["code"])
            for item in gaps
        )
    ):
        raise ControlError("review envelope gaps are malformed")
    verdict = review.get("verdict")
    if verdict == "PASS" and gaps:
        raise ControlError("PASS review envelope must have no gaps")
    if verdict == "BLOCKED" and not gaps:
        raise ControlError("BLOCKED review envelope must contain exhaustive gaps")
    if verdict not in {"PASS", "BLOCKED"}:
        raise ControlError("review verdict must be PASS or BLOCKED")
    return review, relative, file_sha256(path)


def require_planning(control: dict[str, Any]) -> None:
    if control.get("status") != "PLANNING" or control.get("blocked_reason") is not None:
        raise ControlError("run is not in unblocked PLANNING state")
    if control.get("gates", {}).get(control.get("phase")) not in {"PENDING", "STALE"}:
        raise ControlError("current gate is not pending or stale")


def advance(run_dir: Path, approval: Optional[str], review_ref: Optional[str], accepted: str) -> str:
    control, effective = verified_state(run_dir)
    require_planning(control)
    report = candidate_report(run_dir, control, effective)
    if report["verdict"] != "PASS":
        raise ControlError("mechanical boundary check is BLOCKED")
    stage = control["phase"]
    authority = effective.get("gates", {}).get(stage, {}).get("authority")
    review_reference = review_sha256 = None
    if authority == "HUMAN":
        if approval != "human" or review_ref is not None:
            raise ControlError("HUMAN gate requires explicit --approval human")
    elif authority == "AGENT_REVIEW":
        if approval is not None or review_ref is None:
            raise ControlError("AGENT_REVIEW gate requires --review")
        review, review_reference, review_sha256 = validate_review(run_dir, review_ref, report)
        if review["verdict"] != "PASS":
            raise ControlError("review envelope is BLOCKED")
    else:
        raise ControlError(f"authority {authority} is unavailable for this boundary")
    final_report = candidate_report(run_dir, control, effective)
    if (
        final_report.get("candidate_sha256") != report.get("candidate_sha256")
        or final_report.get("candidate_version") != report.get("candidate_version")
    ):
        raise ControlError("candidate bytes changed after review and before acceptance")
    if final_report.get("verdict") != "PASS":
        raise ControlError("candidate dependencies changed after review and before acceptance")
    if review_reference is not None:
        review_path = managed_path(run_dir, review_reference)
        if not review_path.is_file() or file_sha256(review_path) != review_sha256:
            raise ControlError("review evidence changed after validation and before acceptance")
    accepted = canonical_date(accepted, "acceptance date")
    stages = effective.get("stages", [])
    index = stages.index(stage)
    if index + 1 >= len(stages):
        raise ControlError(f"stage {stage} has no next stage")
    control["acceptances"][stage] = {
        "candidate_version": report["candidate_version"],
        "candidate_sha256": report["candidate_sha256"],
        "authority": authority,
        "accepted": accepted,
        "review_reference": review_reference,
        "review_sha256": review_sha256,
    }
    control["gates"][stage] = "HUMAN_APPROVED" if authority == "HUMAN" else "AGENT_APPROVED"
    control["phase"] = stages[index + 1]
    control["revision"] += 1
    control["blocked_reason"] = None
    commit(run_dir, control)
    return f"advanced {stage} -> {control['phase']}; control revision {control['revision']}"


def reject(run_dir: Path, reason: str) -> str:
    control, effective = verified_state(run_dir)
    require_planning(control)
    stage = control["phase"]
    authority = effective.get("gates", {}).get(stage, {}).get("authority")
    if authority != "HUMAN":
        raise ControlError("only explicit HUMAN authority can record a terminal rejection")
    blocked_reason = require_string(reason, "reject reason")
    control["gates"][stage] = "REJECTED"
    control["status"] = "BLOCKED"
    control["blocked_reason"] = blocked_reason
    control["revision"] += 1
    commit(run_dir, control)
    return f"rejected {stage}; control revision {control['revision']}"


def mark_stale(run_dir: Path, reason: str) -> str:
    control, _ = verified_state(run_dir)
    require_planning(control)
    require_string(reason, "mark-stale reason")
    if control.get("phase") != "discovery":
        raise ControlError("only discovery can mark Stage 0 intake stale")
    candidate, _ = read_frontmatter(managed_path(run_dir, CANDIDATES["discovery"]))
    if candidate.get("run") != control.get("run") or candidate.get("version") != expected_candidate_version(control, "discovery"):
        raise ControlError("stale discovery candidate identity/version is invalid")
    if candidate.get("intake_stale") is not True or candidate.get("gate_ready") is not False:
        raise ControlError("discovery must record intake_stale true and gate_ready false")
    control["status"] = "BLOCKED"
    control["gates"]["discovery"] = "STALE"
    control["blocked_reason"] = reason.strip()
    control["revision"] += 1
    commit(run_dir, control)
    return f"marked intake stale; next amendment {control['accepted_amendment_count'] + 1:03d}-*.md"


def apply_amendment(run_dir: Path) -> str:
    control, effective = verified_state(run_dir)
    if control.get("phase") != "discovery" or control.get("status") != "BLOCKED" or control.get("gates", {}).get("discovery") != "STALE":
        raise ControlError("control state does not authorize a Stage 0 amendment")
    number = control["accepted_amendment_count"] + 1
    matches = [path for path in amendment_paths(run_dir) if path.name.startswith(f"{number:03d}-")]
    if len(matches) != 1:
        raise ControlError(f"expected exactly one contiguous amendment {number:03d}-*.md")
    updated = apply_amendment_data(effective, matches[0], number)
    control["accepted_amendment_count"] = number
    control["effective_config_revision"] = number
    control["effective_config_hash"] = canonical_hash(updated)
    control["status"] = "PLANNING"
    control["gates"]["discovery"] = "PENDING"
    control["blocked_reason"] = None
    control["revision"] += 1
    commit(run_dir, control)
    return f"applied amendment {number:03d}; control revision {control['revision']}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"{PRODUCT_DEFINITION_STAGE_LABEL}\n{PRODUCT_DEFINITION_HELPER}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    locate = sub.add_parser("resolve-run-path")
    locate.add_argument("--planning-root", required=True, type=Path)
    locate.add_argument("--slug", required=True)
    init = sub.add_parser("initialize")
    init.add_argument("--run", required=True, type=Path)
    init.add_argument("--prepared-device", required=True, type=int)
    init.add_argument("--prepared-inode", required=True, type=int)
    inspect = sub.add_parser(
        "check",
        help=f"check {PRODUCT_DEFINITION_STAGE_LABEL}",
    )
    inspect.add_argument("--run", required=True, type=Path)
    cmd = sub.add_parser(
        "advance",
        help=PRODUCT_DEFINITION_ACTION,
        description=f"{PRODUCT_DEFINITION_ACTION}.\n{PRODUCT_DEFINITION_HELPER}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    cmd.add_argument("--run", required=True, type=Path)
    cmd.add_argument("--approval", choices=("human",))
    cmd.add_argument("--review")
    cmd.add_argument("--date", default=date.today().isoformat())
    denied = sub.add_parser("reject")
    denied.add_argument("--run", required=True, type=Path)
    denied.add_argument("--reason", required=True)
    stale = sub.add_parser("mark-stale")
    stale.add_argument("--run", required=True, type=Path)
    stale.add_argument("--reason", required=True)
    amend = sub.add_parser("apply-amendment")
    amend.add_argument("--run", required=True, type=Path)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "resolve-run-path":
            print(json.dumps(resolve_run_path(args.planning_root, args.slug), sort_keys=True))
            return 0
        if args.command == "initialize":
            run_dir = resolve_existing_run_directory(
                args.run,
                prepared_device=args.prepared_device,
                prepared_inode=args.prepared_inode,
            )
        else:
            run_dir = resolve_existing_run_directory(args.run)
        if args.command == "check":
            report = check(run_dir)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["verdict"] == "PASS" else 1
        with run_lock(run_dir):
            if args.command == "initialize":
                print(initialize(run_dir))
            elif args.command == "advance":
                print(advance(run_dir, args.approval, args.review, args.date))
            elif args.command == "reject":
                print(reject(run_dir, args.reason))
            elif args.command == "mark-stale":
                print(mark_stale(run_dir, args.reason))
            elif args.command == "apply-amendment":
                print(apply_amendment(run_dir))
            else:  # pragma: no cover
                return 2
        return 0
    except (ControlError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"atlas-control: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
