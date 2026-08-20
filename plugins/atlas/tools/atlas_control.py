#!/usr/bin/env python3
"""Tiny deterministic controller for Atlas planning Stages 0–2.

Producers write candidates. ``check`` performs read-only mechanical checks.
Configured HUMAN or AGENT_REVIEW authority supplies semantic acceptance. This
program alone replaces the feature's authoritative ``control.json``.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime
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
CANDIDATES = {"discovery": "10-decisions.md", "spec": "20-spec.md"}
CANDIDATE_FIELDS = {
    "discovery": {
        "run", "version", "status", "gate_ready", "intake_stale", "cold_read",
        "effective_config_revision", "opened", "repos",
    },
    "spec": {
        "run", "version", "status", "gate_ready", "effective_config_revision",
        "derived_from",
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
SPEC_SECTIONS = (
    "Problem", "Requirements", "Prohibitions", "Constraints", "Invariants",
    "Out of scope", "Edge coverage", "Open questions",
)
DECISION_FIELDS = {
    "id", "route", "findings", "status", "decided", "origin", "confidence", "unblocked",
    "blocked_by", "supersedes", "contribution",
}


class ControlError(RuntimeError):
    pass


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
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ControlError(f"frontmatter is not a map: {path.name}")
    return data, body


def load_run(run_dir: Path) -> dict[str, Any]:
    path = managed_path(run_dir, "run.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
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


def validate_run(config: dict[str, Any]) -> None:
    if set(config) != RUN_FIELDS:
        raise ControlError("run.yaml fields do not match version-1 schema")
    if config.get("version") != 1 or isinstance(config.get("version"), bool):
        raise ControlError("run.yaml version must be 1")
    run = require_string(config.get("run"), "run.yaml run")
    if config.get("run_path") != run:
        raise ControlError("run.yaml run_path must equal run")
    canonical_date(config.get("opened"), "run.yaml opened")
    require_string(config.get("goal"), "run.yaml goal")
    validate_repos(config.get("repos"))
    stages = config.get("stages")
    if not isinstance(stages, list) or not stages or len(stages) != len(set(stages)):
        raise ControlError("run.yaml stages must be a non-empty unique list")
    gates = config.get("gates")
    if not isinstance(gates, dict) or any(stage in stages and stage not in gates for stage in CANDIDATES):
        raise ControlError("run.yaml gates must cover selected Stage 0–2 boundaries")
    for stage, policy in gates.items():
        if not isinstance(policy, dict) or not isinstance(policy.get("authority"), str):
            raise ControlError(f"run.yaml gate policy is malformed: {stage}")
    for stage in ("discovery", "spec"):
        if stage in stages and gates[stage].get("authority") not in {"AGENT_REVIEW", "HUMAN"}:
            raise ControlError(f"the semantic {stage} boundary requires AGENT_REVIEW or HUMAN")
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
        control = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControlError("control.json is not valid JSON") from exc
    if not isinstance(control, dict):
        raise ControlError("control.json is not a map")
    if set(control) != CONTROL_FIELDS:
        raise ControlError("control.json fields do not match version-1 schema")
    acceptances = control.get("acceptances")
    if not isinstance(acceptances, dict) or set(acceptances) != set(CANDIDATES) or any(
        record is not None and (not isinstance(record, dict) or set(record) != ACCEPTANCE_FIELDS)
        for record in acceptances.values()
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
        if (gate_state in approved_states) != (record is not None):
            if not (gate_state == "STALE" and record is not None):
                raise ControlError("control.json gate/acceptance coherence is invalid")
        if record is not None and gate_state != "STALE":
            expected_gate = "HUMAN_APPROVED" if record["authority"] == "HUMAN" else "AGENT_APPROVED"
            if gate_state != expected_gate:
                raise ControlError("control.json authority/gate coherence is invalid")
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
    if managed_path(run_dir, "10-decisions.md").exists() or amendment_paths(run_dir):
        raise ControlError("initialize must run before discovery or amendments")
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
        "acceptances": {"discovery": None, "spec": None},
    }
    commit(run_dir, control)
    return "initialized control.json revision 1"


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


def section(body: str, heading: str) -> Optional[str]:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", body)
    return match.group(1) if match else None


def discovery_ids_and_gaps(body: str, artifact: str) -> tuple[set[str], list[dict[str, str]]]:
    gaps: list[dict[str, str]] = []
    matches = list(re.finditer(r"(?m)^### (D-[0-9]{3})\s+—\s+.+$", body))
    identifiers = [match.group(1) for match in matches]
    if not identifiers:
        gaps.append(gap(artifact, "no decision identifiers are present", "discovery", "record settled decisions"))
    if len(identifiers) != len(set(identifiers)):
        gaps.append(gap(artifact, "decision identifiers are not unique", "discovery", "assign unique D-NNN identifiers"))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        record_text = body[match.end():end]
        fenced = re.search(r"```yaml\n(.*?)```", record_text, re.S)
        if not fenced:
            gaps.append(gap(artifact, f"{match.group(1)} has no YAML record", "discovery", "add the required decision record fields"))
            continue
        try:
            record = yaml.safe_load(fenced.group(1))
        except yaml.YAMLError:
            record = None
        if not isinstance(record, dict) or not DECISION_FIELDS.issubset(record) or record.get("id") != match.group(1):
            gaps.append(gap(artifact, f"{match.group(1)} record fields are incomplete or mismatched", "discovery", "repair the decision record"))
        elif record.get("status") not in {"settled", "superseded"}:
            gaps.append(gap(artifact, f"{match.group(1)} is not settled or superseded", "discovery", "settle or supersede the decision"))
    frontier = section(body, "Open frontier")
    if frontier is None:
        gaps.append(gap(artifact, "Open frontier section is absent", "discovery", "record the open frontier"))
    else:
        rows = [
            line for line in frontier.splitlines() if line.lstrip().startswith("|")
            and "Question" not in line and not re.fullmatch(r"\s*\|?[-:| ]+\|?\s*", line)
        ]
        if rows:
            gaps.append(gap(artifact, "open frontier still contains unresolved entries", "discovery", "resolve every frontier entry"))
    return set(identifiers), gaps


def candidate_report(run_dir: Path, control: dict[str, Any], effective: dict[str, Any]) -> dict[str, Any]:
    stage = control.get("phase")
    artifact = CANDIDATES.get(stage)
    gaps: list[dict[str, str]] = []
    report: dict[str, Any] = {"version": 1, "run": control["run"], "verdict": "BLOCKED", "stage": stage, "gaps": gaps}
    if artifact is None:
        gaps.append(gap(CONTROL_FILE, f"{stage} is outside the Stage 0–2 controller", str(stage), "use the next-stage controller"))
        return report
    path = managed_path(run_dir, artifact)
    if not path.is_file():
        gaps.append(gap(artifact, "candidate file is missing", stage, f"produce {artifact}"))
        return report
    report["candidate_sha256"] = file_sha256(path)
    try:
        candidate, body = read_frontmatter(path)
    except (ControlError, yaml.YAMLError) as exc:
        gaps.append(gap(artifact, str(exc), stage, "repair candidate frontmatter"))
        return report
    report["candidate_version"] = candidate.get("version")
    expected = expected_candidate_version(control, stage)
    if set(candidate) != CANDIDATE_FIELDS[stage]:
        gaps.append(gap(artifact, "candidate frontmatter does not match its exact schema", stage, "repair candidate frontmatter"))
    if candidate.get("run") != control.get("run"):
        gaps.append(gap(artifact, "candidate run identity does not match control.json", stage, "bind the candidate to this run"))
    if candidate.get("version") != expected:
        gaps.append(gap(artifact, f"candidate must use version {expected}", stage, f"write candidate version {expected}"))
    if candidate.get("status") != "draft":
        gaps.append(gap(artifact, "producer candidate status must remain draft", stage, "record readiness without approval"))
    if candidate.get("gate_ready") is not True:
        gaps.append(gap(artifact, "producer has not recorded gate readiness", stage, "finish the candidate and set gate_ready true"))
    if candidate.get("effective_config_revision") != control.get("effective_config_revision"):
        gaps.append(gap(artifact, "candidate uses a stale effective configuration revision", stage, "revalidate against effective intake"))

    if stage == "discovery":
        if candidate.get("intake_stale") is not False:
            gaps.append(gap(artifact, "discovery reports stale intake", "intake", "apply the next repository/baseline amendment"))
        if candidate.get("cold_read") != "complete":
            gaps.append(gap(artifact, "cold-read evidence is incomplete", stage, "complete and disposition the cold read"))
        cold_read = section(body, "Cold-read evidence")
        if cold_read is None or not cold_read.strip():
            gaps.append(gap(artifact, "Cold-read evidence section is absent or empty", stage, "record baseline findings and their disposition"))
        expected_repos = [item["repository"] for item in effective.get("repos", [])]
        if candidate.get("repos") != expected_repos:
            gaps.append(gap(artifact, "declared repository scope differs from effective intake", stage, "revalidate repository scope"))
        if canonical_value(candidate.get("opened")) != canonical_value(effective.get("opened")):
            gaps.append(gap(artifact, "candidate opened date differs from intake", stage, "copy the intake opened date"))
        _, body_gaps = discovery_ids_and_gaps(body, artifact)
        gaps.extend(body_gaps)
    else:
        predecessor = latest_acceptance(control, "discovery")
        source_path = managed_path(run_dir, CANDIDATES["discovery"])
        if predecessor is None:
            gaps.append(gap(artifact, "accepted discovery provenance is absent", "discovery", "accept discovery first"))
        else:
            expected_source = {
                "stage": "discovery",
                "candidate_version": predecessor.get("candidate_version"),
                "candidate_sha256": predecessor.get("candidate_sha256"),
            }
            if candidate.get("derived_from") != expected_source:
                gaps.append(gap(artifact, "derived_from does not bind the accepted discovery version/hash", stage, "bind the spec to accepted discovery"))
            if not source_path.is_file() or file_sha256(source_path) != predecessor.get("candidate_sha256"):
                gaps.append(gap(CANDIDATES["discovery"], "current discovery bytes no longer match accepted discovery provenance", "discovery", "reopen discovery and accept a new version"))
        for heading in SPEC_SECTIONS:
            if len(re.findall(rf"(?m)^## {re.escape(heading)}\s*$", body)) != 1:
                gaps.append(gap(artifact, f"required section {heading} must appear exactly once", stage, f"repair section {heading}"))
        normative = re.findall(r"(?m)^### ([RPCIX]-[0-9]{3})\s+—\s+", body)
        if not normative:
            gaps.append(gap(artifact, "no normative identifiers are present", str(stage), "record at least one normative R/P/C/I/X-NNN obligation"))
        if len(normative) != len(set(normative)):
            gaps.append(gap(artifact, "normative identifiers are not unique", stage, "assign unique normative identifiers"))
        if re.search(r"(?im)^## (Work Items|Files|Classes|Methods|Implementation|Tickets)\s*$", body):
            gaps.append(gap(artifact, "spec contains an internal design or ticket section", stage, "move internal shape downstream"))
        open_questions = section(body, "Open questions") or ""
        if re.search(r"(?im)^(?:\s*Blocking\s*:|\s*\|.*\bblocking\b.*\|)", open_questions):
            gaps.append(gap(artifact, "spec contains a blocking open question", "discovery", "resolve the behavior-changing question"))
        decision_ids, _ = discovery_ids_and_gaps(
            managed_path(run_dir, CANDIDATES["discovery"]).read_text(encoding="utf-8") if managed_path(run_dir, CANDIDATES["discovery"]).is_file() else "",
            CANDIDATES["discovery"],
        )
        refs = set(re.findall(r"\bD-[0-9]{3}\b", body))
        if refs - decision_ids:
            gaps.append(gap(artifact, f"decision references do not resolve: {sorted(refs - decision_ids)}", stage, "repair decision references"))
    report["verdict"] = "PASS" if not gaps else "BLOCKED"
    return report


def check(run_dir: Path) -> dict[str, Any]:
    control, effective = verified_state(run_dir)
    return candidate_report(run_dir, control, effective)


def validate_review(run_dir: Path, relative: str, report: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    path = managed_path(run_dir, relative)
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControlError("review envelope is not valid JSON") from exc
    if not isinstance(review, dict) or set(review) != REVIEW_FIELDS:
        raise ControlError("review envelope fields do not match version-1 schema")
    if review.get("version") != 1 or review.get("run") != report.get("run") or review.get("stage") != report.get("stage"):
        raise ControlError("review envelope stage/version is invalid")
    if review.get("candidate_version") != report.get("candidate_version") or review.get("candidate_sha256") != report.get("candidate_sha256"):
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


def reopen(run_dir: Path, target: str, reason: str) -> str:
    control, effective = verified_state(run_dir)
    require_planning(control)
    require_string(reason, "reopen reason")
    if control.get("phase") != "spec" or target != "discovery":
        raise ControlError("the only Stage 0–2 reopen is spec -> discovery")
    if latest_acceptance(control, "discovery") is None:
        raise ControlError("discovery has no accepted provenance to reopen")
    control["phase"] = "discovery"
    control["gates"]["discovery"] = "STALE"
    control["gates"]["spec"] = "STALE"
    control["revision"] += 1
    control["blocked_reason"] = None
    commit(run_dir, control)
    return f"reopened spec -> discovery; next candidate version {expected_candidate_version(control, 'discovery')}"


def mark_stale(run_dir: Path, reason: str) -> str:
    control, effective = verified_state(run_dir)
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
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("initialize")
    init.add_argument("--run", required=True, type=Path)
    inspect = sub.add_parser("check")
    inspect.add_argument("--run", required=True, type=Path)
    cmd = sub.add_parser("advance")
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
    back = sub.add_parser("reopen")
    back.add_argument("--run", required=True, type=Path)
    back.add_argument("--to", required=True, choices=("discovery",))
    back.add_argument("--reason", required=True)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run_dir = args.run.resolve()
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
            elif args.command == "reopen":
                print(reopen(run_dir, args.to, args.reason))
            else:  # pragma: no cover
                return 2
        return 0
    except (ControlError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"atlas-control: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
