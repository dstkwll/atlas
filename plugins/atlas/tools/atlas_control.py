#!/usr/bin/env python3
"""Deterministic Atlas run-state transitions.

Requires PyYAML. Stage skills prepare candidate artifacts; this program is the
single writer for authoritative gate and phase transitions after Stage 0.
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
from typing import Any, Iterator

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


CANDIDATES = {"discovery": "10-decisions.md", "spec": "20-spec.md"}
AMENDABLE = {"repos"}
AMENDMENT_FIELDS = {
    "version", "amendment", "applies_to", "status", "accepted", "reason",
    "previous", "prior_effective_hash", "changes", "effective_config_revision",
}
CANDIDATE_FIELDS = {
    "discovery": {
        "run", "version", "status", "gate_ready", "intake_stale", "cold_read",
        "approved", "approved_authority", "approved_copy", "approved_sha256",
        "effective_config_revision", "opened", "repos",
    },
    "spec": {
        "run", "version", "status", "gate_ready", "approved", "approved_authority",
        "approved_copy", "approved_sha256", "supersedes", "amendment", "derived-from",
        "effective_config_revision",
    },
}
REOPENED_DISCOVERY_FIELDS = {
    "run", "version", "status", "gate_ready", "intake_stale", "cold_read",
    "approved", "approved_authority", "approved_copy", "approved_sha256",
    "effective_config_revision", "opened", "repos", "supersedes",
}
SPEC_REQUIRED_SECTIONS = (
    "Problem", "Requirements", "Prohibitions", "Constraints", "Invariants",
    "Out of scope", "Edge coverage", "Open questions",
)
SPEC_EDGE_CATEGORIES = (
    "boundary", "adjacency", "empty", "encoding", "ordering", "precision",
    "idempotency", "concurrency",
)
RUN_FIELDS = {
    "version", "run", "opened", "goal", "planning_root", "run_path",
    "recommendation", "workflow", "stages", "governance", "gates",
    "execution_policy", "environment_policy", "roster", "risk", "repos",
    "overrides",
}
RECOMMENDATION_FIELDS = {
    "workflow", "governance", "execution_policy", "environment_policy", "roster",
    "gates", "reasons",
}
RISK_FIELDS = {
    "scope", "reversibility", "architecture_change", "schema_change",
    "public_contract_change", "security_sensitive", "operational_impact", "testability",
}
STATE_FIELDS = {
    "feature", "status", "phase", "revision", "effective_config_revision",
    "effective_config_hash", "base_run_sha256", "repos", "gates", "active_ticket",
    "blocked_reason", "pending_amendment", "approved_artifacts", "accepted_amendments",
}
GATE_AUTHORITIES = {"AUTO", "AGENT_REVIEW", "HUMAN", "CONDITIONAL", "HUMAN_IF_CHANGED"}
GATE_STATES = {
    "NOT_REQUIRED", "PENDING", "AGENT_APPROVED", "HUMAN_APPROVED", "REJECTED", "STALE",
}


class ControlError(RuntimeError):
    pass


def read_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ControlError(f"missing YAML frontmatter: {path}")
    raw, body = text[4:].split("\n---\n", 1)
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ControlError(f"frontmatter is not a map: {path}")
    return data, body


def render_frontmatter(data: dict[str, Any], body: str) -> str:
    raw = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).rstrip()
    return f"---\n{raw}\n---\n{body}"


def replace_section(body: str, heading: str, content: str) -> str:
    marker = f"## {heading}\n"
    start = body.find(marker)
    if start < 0:
        return body.rstrip() + f"\n\n{marker}\n{content.rstrip()}\n"
    content_start = start + len(marker)
    next_heading = body.find("\n## ", content_start)
    end = len(body) if next_heading < 0 else next_heading
    return body[:content_start] + "\n" + content.rstrip() + "\n" + body[end:]


TRANSACTION_FILE = ".atlas-control-transaction.json"
LOCK_FILE = ".atlas-control.lock"


@contextlib.contextmanager
def run_lock(run_dir: Path) -> Iterator[None]:
    """Hold the run's single-writer lock across recovery, validation, and commit."""
    lock_path = managed_path(run_dir, LOCK_FILE)
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
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
            else:  # pragma: no cover - unsupported platform
                raise ControlError("this platform has no supported run-lock primitive")
            acquired = True
        except (BlockingIOError, OSError) as exc:
            raise ControlError("another atlas-control process is active for this run") from exc
        yield
    finally:
        if acquired:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif msvcrt is not None:  # pragma: no cover - Windows fallback
                os.lseek(fd, 0, os.SEEK_SET)
                getattr(msvcrt, "locking")(fd, getattr(msvcrt, "LK_UNLCK"), 1)
        os.close(fd)


def fsync_dir(path: Path) -> None:
    # Windows cannot open directories through os.open; file fsync + atomic os.replace
    # still provide the executable recovery protocol there.
    if os.name == "nt":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recover_transaction(run_dir: Path) -> bool:
    journal_path = managed_path(run_dir, TRANSACTION_FILE)
    if not journal_path.exists():
        return False
    try:
        journal = json.loads(journal_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ControlError("transaction journal is unreadable; manual recovery required") from exc
    operations = journal.get("operations") if isinstance(journal, dict) else None
    if not isinstance(operations, list) or not operations:
        raise ControlError("transaction journal is malformed; manual recovery required")
    for operation in operations:
        if not isinstance(operation, dict):
            raise ControlError("transaction operation is malformed")
        target_rel = operation.get("target")
        temp_rel = operation.get("temp")
        if not isinstance(target_rel, str) or not isinstance(temp_rel, str):
            raise ControlError("transaction operation paths are malformed")
        target = managed_path(run_dir, target_rel)
        temp = managed_path(run_dir, temp_rel)
        expected = operation.get("new_sha256")
        if target.is_file() and file_sha256(target) == expected:
            temp.unlink(missing_ok=True)
            continue
        if not temp.is_file() or file_sha256(temp) != expected:
            raise ControlError(f"transaction cannot recover {operation.get('target')}; manual recovery required")
        os.replace(temp, target)
        fsync_dir(target.parent)
    journal_path.unlink()
    fsync_dir(run_dir)
    return True


def write_files_atomic(run_dir: Path, pairs: list[tuple[Path, str]]) -> None:
    journal_path = managed_path(run_dir, TRANSACTION_FILE)
    if journal_path.exists():
        raise ControlError("an interrupted transaction must be recovered before another write")
    operations: list[dict[str, str]] = []
    temps: list[Path] = []
    journal_installed = False
    try:
        for path, content in pairs:
            relative = path.relative_to(run_dir).as_posix()
            managed = managed_path(run_dir, relative)
            managed.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=f".{managed.name}.txn-", dir=managed.parent)
            temp = Path(name)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            temps.append(temp)
            operations.append({
                "target": relative,
                "temp": temp.relative_to(run_dir).as_posix(),
                "new_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            })
        journal = json.dumps({"version": 1, "operations": operations}, sort_keys=True) + "\n"
        fd, name = tempfile.mkstemp(prefix=f".{TRANSACTION_FILE}.", dir=run_dir)
        journal_temp = Path(name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(journal)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(journal_temp, journal_path)
            fsync_dir(run_dir)
            journal_installed = True
        finally:
            journal_temp.unlink(missing_ok=True)

        crash_after = int(os.environ.get("ATLAS_CONTROL_TEST_CRASH_AFTER_REPLACES", "0"))
        for index, operation in enumerate(operations, 1):
            target = managed_path(run_dir, operation["target"])
            temp = managed_path(run_dir, operation["temp"])
            os.replace(temp, target)
            fsync_dir(target.parent)
            if crash_after and index == crash_after:
                os._exit(86)  # test-only deterministic crash injection
        journal_path.unlink()
        fsync_dir(run_dir)
    finally:
        if not journal_installed or not journal_path.exists():
            for temp in temps:
                temp.unlink(missing_ok=True)


def load_run(run_dir: Path) -> dict[str, Any]:
    data = yaml.safe_load(managed_path(run_dir, "run.yaml").read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ControlError("run.yaml is not a map")
    return data


def canonical_json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ControlError("canonical configuration maps require string keys")
        return {key: canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [canonical_json_value(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ControlError(f"unsupported canonical configuration value: {type(value).__name__}")


def canonical_hash(data: Any) -> str:
    encoded = json.dumps(
        canonical_json_value(data), sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_repos(repos: Any) -> list[dict[str, str]]:
    if not isinstance(repos, list) or not repos:
        raise ControlError("effective repos must be a non-empty list")
    identities: set[str] = set()
    for item in repos:
        if not isinstance(item, dict) or set(item) != {"repository", "baseline"}:
            raise ControlError("effective repos must contain exact repository-baseline maps")
        repository = item.get("repository")
        baseline = item.get("baseline")
        if (
            not isinstance(repository, str) or not repository.strip()
            or not isinstance(baseline, str) or not baseline.strip()
        ):
            raise ControlError("repository and baseline must be non-empty strings")
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", baseline):
            raise ControlError("repository baseline must be a 7-64 character commit SHA")
        if repository in identities:
            raise ControlError("repository identities must be unique")
        identities.add(repository)
    return repos


def require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ControlError(f"{field} must be a non-empty string")
    return value


def validate_gate_map(gates: Any, field: str) -> dict[str, Any]:
    if not isinstance(gates, dict) or not gates:
        raise ControlError(f"{field} must be a non-empty map")
    for name, policy in gates.items():
        require_nonempty_string(name, f"{field} gate name")
        if not isinstance(policy, dict):
            raise ControlError(f"{field}.{name} must be a map")
        authority = policy.get("authority")
        if authority not in GATE_AUTHORITIES:
            raise ControlError(f"{field}.{name} has invalid authority")
        optional = {"activation"} if "activation" in policy else set()
        if optional:
            activation = policy["activation"]
            if not isinstance(activation, dict) or set(activation) != {"when"}:
                raise ControlError(f"{field}.{name}.activation must contain only when")
            require_nonempty_string(activation["when"], f"{field}.{name}.activation.when")
        if authority == "CONDITIONAL":
            expected = {"authority", "conditions", "otherwise"} | optional
            conditions = policy.get("conditions")
            if not isinstance(conditions, list) or not conditions:
                raise ControlError(f"{field}.{name}.conditions must be a non-empty list")
            for condition in conditions:
                if not isinstance(condition, dict) or set(condition) != {"when", "then"}:
                    raise ControlError(f"{field}.{name}.conditions entries require when and then")
                require_nonempty_string(condition["when"], f"{field}.{name}.conditions.when")
                if condition["then"] not in GATE_AUTHORITIES - {"CONDITIONAL", "HUMAN_IF_CHANGED"}:
                    raise ControlError(f"{field}.{name}.conditions.then has invalid authority")
            if policy.get("otherwise") not in GATE_AUTHORITIES - {"CONDITIONAL", "HUMAN_IF_CHANGED"}:
                raise ControlError(f"{field}.{name}.otherwise has invalid authority")
        elif authority == "HUMAN_IF_CHANGED":
            expected = {"authority", "material_dimensions", "otherwise"} | optional
            dimensions = policy.get("material_dimensions")
            if not isinstance(dimensions, list) or not dimensions or any(
                not isinstance(item, str) or not item.strip() for item in dimensions
            ):
                raise ControlError(f"{field}.{name}.material_dimensions must be non-empty strings")
            if policy.get("otherwise") not in GATE_AUTHORITIES - {"CONDITIONAL", "HUMAN_IF_CHANGED"}:
                raise ControlError(f"{field}.{name}.otherwise has invalid authority")
        else:
            expected = {"authority"} | optional
        if set(policy) != expected:
            raise ControlError(f"{field}.{name} fields do not match its authority schema")
    return gates


def validate_stage_zero_schema(config: dict[str, Any], state: dict[str, Any]) -> None:
    if set(config) != RUN_FIELDS:
        missing = sorted(RUN_FIELDS - set(config))
        unexpected = sorted(set(config) - RUN_FIELDS)
        raise ControlError(
            f"run.yaml fields do not match version-1 schema; missing={missing}, unexpected={unexpected}"
        )
    if config.get("version") != 1 or isinstance(config.get("version"), bool):
        raise ControlError("run.yaml version must be 1")
    run_identity = require_nonempty_string(config.get("run"), "run.yaml run")
    if config.get("run_path") != run_identity:
        raise ControlError("run.yaml run_path must equal run")
    require_nonempty_string(config.get("goal"), "run.yaml goal")
    opened = canonical_json_value(config.get("opened"))
    try:
        if not isinstance(opened, str) or date.fromisoformat(opened).isoformat() != opened:
            raise ValueError
    except ValueError as exc:
        raise ControlError("run.yaml opened must be canonical YYYY-MM-DD") from exc

    planning_root = config.get("planning_root")
    if not isinstance(planning_root, dict) or set(planning_root) != {"source", "mode", "path"}:
        raise ControlError("run.yaml planning_root fields do not match version-1 schema")
    if planning_root.get("source") != "artifacts.planning_root":
        raise ControlError("run.yaml planning_root source is invalid")
    if planning_root.get("mode") not in {"repository-relative", "external"}:
        raise ControlError("run.yaml planning_root mode is invalid")
    require_nonempty_string(planning_root.get("path"), "run.yaml planning_root path")

    stages = config.get("stages")
    if not isinstance(stages, list) or not stages or any(
        not isinstance(item, str) or not item.strip() for item in stages
    ) or len(set(stages)) != len(stages):
        raise ControlError("run.yaml stages must be a non-empty unique string list")
    gates = validate_gate_map(config.get("gates"), "run.yaml gates")
    if any(stage not in gates for stage in stages):
        raise ControlError("run.yaml gates must cover every selected stage")
    for field_name in ("workflow", "governance", "execution_policy", "environment_policy", "roster"):
        require_nonempty_string(config.get(field_name), f"run.yaml {field_name}")

    recommendation = config.get("recommendation")
    if not isinstance(recommendation, dict) or set(recommendation) != RECOMMENDATION_FIELDS:
        raise ControlError("run.yaml recommendation fields do not match version-1 schema")
    for field_name in ("workflow", "governance", "execution_policy", "environment_policy", "roster"):
        require_nonempty_string(recommendation.get(field_name), f"run.yaml recommendation {field_name}")
    validate_gate_map(recommendation.get("gates"), "run.yaml recommendation gates")
    reasons = recommendation.get("reasons")
    if not isinstance(reasons, list) or not reasons:
        raise ControlError("run.yaml recommendation reasons must be a non-empty list")
    for reason in reasons:
        if not isinstance(reason, dict) or set(reason) != {"dimension", "evidence"}:
            raise ControlError("run.yaml recommendation reasons require dimension and evidence")
        require_nonempty_string(reason["dimension"], "recommendation reason dimension")
        require_nonempty_string(reason["evidence"], "recommendation reason evidence")

    risk = config.get("risk")
    if not isinstance(risk, dict) or set(risk) != RISK_FIELDS:
        raise ControlError("run.yaml risk fields do not match version-1 schema")
    boolean_risks = {
        "architecture_change", "schema_change", "public_contract_change", "security_sensitive",
    }
    for field_name in boolean_risks:
        if not isinstance(risk.get(field_name), bool):
            raise ControlError(f"run.yaml risk {field_name} must be a boolean")
    for field_name in RISK_FIELDS - boolean_risks:
        require_nonempty_string(risk.get(field_name), f"run.yaml risk {field_name}")
    repos = validate_repos(config.get("repos"))

    overrides = config.get("overrides")
    if not isinstance(overrides, list):
        raise ControlError("run.yaml overrides must be a list")
    for override in overrides:
        if not isinstance(override, dict) or set(override) != {"path", "from", "to", "reason"}:
            raise ControlError("run.yaml overrides entries require path, from, to, and reason")
        require_nonempty_string(override["path"], "run.yaml override path")
        require_nonempty_string(override["reason"], "run.yaml override reason")

    if set(state) != STATE_FIELDS:
        missing = sorted(STATE_FIELDS - set(state))
        unexpected = sorted(set(state) - STATE_FIELDS)
        raise ControlError(
            f"00-state.md fields do not match pristine version-1 schema; "
            f"missing={missing}, unexpected={unexpected}"
        )
    if state.get("feature") != run_identity or state.get("phase") != stages[0]:
        raise ControlError("pristine state identity or first phase does not match run.yaml")
    if state.get("status") != "PLANNING" or state.get("revision") != 1:
        raise ControlError("initialize requires pristine PLANNING revision-1 state")
    if state.get("effective_config_revision") != 0:
        raise ControlError("initialize requires effective-config revision 0")
    if state.get("effective_config_hash") is not None or state.get("base_run_sha256") is not None:
        raise ControlError("base run is already initialized")
    if state.get("repos") != [item["repository"] for item in repos]:
        raise ControlError("pristine state repos do not mirror run.yaml")
    state_gates = state.get("gates")
    if not isinstance(state_gates, dict) or set(state_gates) != set(gates):
        raise ControlError("pristine state gates do not mirror run.yaml gate names")
    if any(value not in GATE_STATES for value in state_gates.values()):
        raise ControlError("pristine state contains an invalid gate state")
    if any(state_gates[stage] != "PENDING" for stage in stages):
        raise ControlError("selected stages must begin PENDING")
    if any(state.get(field_name) is not None for field_name in (
        "active_ticket", "blocked_reason", "pending_amendment",
    )):
        raise ControlError("pristine state active/block/amendment fields must be null")
    if state.get("approved_artifacts") != {} or state.get("accepted_amendments") != {}:
        raise ControlError("initialize requires empty receipt ledgers")


def verify_effective_state(state: dict[str, Any], effective: dict[str, Any], revision: int) -> None:
    recorded = state.get("effective_config_hash")
    expected = canonical_hash(effective)
    if not isinstance(recorded, str) or recorded != expected:
        raise ControlError("state effective configuration hash does not match accepted intake")


def verify_base_run_bytes(run_dir: Path, state: dict[str, Any]) -> None:
    expected = state.get("base_run_sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ControlError("state is missing the sealed base run.yaml byte hash")
    if file_sha256(managed_path(run_dir, "run.yaml")) != expected:
        raise ControlError("base run.yaml byte hash mismatch")


def managed_path(run_dir: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ControlError(f"managed path escapes the run: {relative}")
    current = run_dir
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ControlError(f"managed path uses a symlink: {relative}")
    root = run_dir.resolve()
    resolved = current.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise ControlError(f"managed path escapes the run: {relative}")
    return current


def verify_approved_artifacts(run_dir: Path, state: dict[str, Any]) -> None:
    ledger = state.get("approved_artifacts", {})
    if not isinstance(ledger, dict):
        raise ControlError("approved_artifacts ledger is not a map")
    for relative, receipt in ledger.items():
        if not isinstance(relative, str) or not isinstance(receipt, dict):
            raise ControlError("approved artifact receipt is malformed")
        expected = receipt.get("sha256")
        path = managed_path(run_dir, relative)
        if not isinstance(expected, str) or not path.is_file():
            raise ControlError(f"approved artifact receipt is incomplete: {relative}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ControlError(f"approved artifact hash mismatch: {relative}")


def verify_accepted_amendments(run_dir: Path, state: dict[str, Any]) -> None:
    ledger = state.get("accepted_amendments", {})
    if not isinstance(ledger, dict):
        raise ControlError("accepted_amendments ledger is not a map")
    for relative, expected in ledger.items():
        if not isinstance(relative, str) or not re.fullmatch(
            r"amendments/run-config-[0-9]{3}\.yaml", relative
        ) or not isinstance(expected, str):
            raise ControlError("accepted amendment receipt is malformed")
        path = managed_path(run_dir, relative)
        if not path.is_file() or file_sha256(path) != expected:
            raise ControlError(f"accepted amendment hash mismatch: {relative}")


def load_effective_run(run_dir: Path) -> tuple[dict[str, Any], int]:
    effective = load_run(run_dir)
    amendment_dir = managed_path(run_dir, "amendments")
    paths = sorted(amendment_dir.glob("run-config-*.yaml")) if amendment_dir.exists() else []
    previous = None
    for revision, path in enumerate(paths, 1):
        expected_name = f"run-config-{revision:03d}"
        amendment = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(amendment, dict):
            raise ControlError(f"amendment is not a map: {path}")
        if set(amendment) != AMENDMENT_FIELDS:
            raise ControlError(f"amendment fields do not match version-1 schema: {path.name}")
        if amendment.get("version") != 1:
            raise ControlError(f"amendment version must be 1: {path.name}")
        if path.stem != expected_name or amendment.get("amendment") != expected_name:
            raise ControlError(f"non-contiguous amendment sequence at {path.name}")
        if amendment.get("status") != "accepted" or amendment.get("applies_to") != "run.yaml":
            raise ControlError(f"amendment is not accepted for run.yaml: {path.name}")
        accepted = amendment.get("accepted")
        try:
            if not isinstance(accepted, str) or date.fromisoformat(accepted).isoformat() != accepted:
                raise ValueError
        except ValueError as exc:
            raise ControlError(f"amendment accepted date must be canonical YYYY-MM-DD: {path.name}") from exc
        reason = amendment.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ControlError(f"amendment reason must be a non-empty string: {path.name}")
        if amendment.get("previous") != previous:
            raise ControlError(f"amendment previous link mismatch: {path.name}")
        if amendment.get("effective_config_revision") != revision:
            raise ControlError(f"amendment revision mismatch: {path.name}")
        if amendment.get("prior_effective_hash") != canonical_hash(effective):
            raise ControlError(f"amendment prior_effective_hash mismatch: {path.name}")
        changes = amendment.get("changes")
        if not isinstance(changes, dict) or not changes:
            raise ControlError(f"amendment has no changes: {path.name}")
        forbidden = set(changes) - AMENDABLE
        if forbidden:
            raise ControlError(f"amendment changes forbidden fields: {sorted(forbidden)}")
        effective.update(changes)
        validate_repos(effective.get("repos"))
        previous = expected_name
    return effective, len(paths)


def initialize(run_dir: Path) -> str:
    config = load_run(run_dir)
    state_path = managed_path(run_dir, "00-state.md")
    state, body = read_frontmatter(state_path)
    validate_stage_zero_schema(config, state)
    amendment_dir = managed_path(run_dir, "amendments")
    if amendment_dir.exists() and any(amendment_dir.iterdir()):
        raise ControlError("cannot initialize after amendments exist")
    if managed_path(run_dir, "10-decisions.md").exists():
        raise ControlError("cannot initialize after discovery has started")
    state["effective_config_hash"] = canonical_hash(config)
    state["base_run_sha256"] = file_sha256(managed_path(run_dir, "run.yaml"))
    write_files_atomic(run_dir, [(state_path, render_frontmatter(state, body))])
    return "initialized immutable base intake; state revision 1"


def require_unblocked_planning(state: dict[str, Any]) -> None:
    if state.get("status") != "PLANNING":
        raise ControlError(f"run status is not PLANNING: {state.get('status')}")
    if state.get("blocked_reason") is not None:
        raise ControlError("run has a blocked_reason")


def verify_run_state_identity(
    state: dict[str, Any], config: dict[str, Any], expected_config_revision: int
) -> str:
    run_identity = config.get("run")
    if not isinstance(run_identity, str) or state.get("feature") != run_identity:
        raise ControlError("state feature does not match run identity")
    if state.get("effective_config_revision") != expected_config_revision:
        raise ControlError("state does not match the latest accepted amendment")
    return run_identity


def verify_candidate_identity(
    candidate: dict[str, Any], state: dict[str, Any], run_identity: str
) -> None:
    if candidate.get("run") != run_identity:
        raise ControlError("candidate run identity does not match run.yaml")
    if candidate.get("effective_config_revision") != state.get("effective_config_revision"):
        raise ControlError("candidate and state use different effective-config revisions")


def latest_approved_candidate(
    run_dir: Path, state: dict[str, Any], phase: str
) -> tuple[str, dict[str, Any]] | None:
    ledger = state.get("approved_artifacts", {})
    if not isinstance(ledger, dict):
        raise ControlError("approved_artifacts ledger is not a map")
    pattern = re.compile(rf"approved/{re.escape(phase)}-r([1-9][0-9]*)\.md")
    matches = [
        (int(match.group(1)), relative)
        for relative, receipt in ledger.items()
        if isinstance(relative, str)
        and (match := pattern.fullmatch(relative))
        and isinstance(receipt, dict)
        and receipt.get("phase") == phase
    ]
    if not matches:
        return None
    _, relative = max(matches)
    candidate, _ = read_frontmatter(managed_path(run_dir, relative))
    return relative, candidate


def section_content(body: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", body,
    )
    return match.group(1).strip() if match else ""


def discovery_decision_ids(body: str) -> set[str]:
    identifiers = re.findall(r"(?m)^### (D-[0-9]{3})\s+—\s+\S", body)
    if len(identifiers) != len(set(identifiers)):
        raise ControlError("discovery body repeats a decision identifier")
    return set(identifiers)


def validate_discovery_body(body: str) -> None:
    if not re.search(r"(?m)^# Decisions(?:\s+—|\s+-|\s*$)", body):
        raise ControlError("discovery body must begin with a Decisions title")
    problem = section_content(body, "Problem test")
    if len(re.sub(r"\s+", " ", problem)) < 20 or re.search(
        r"\bPending\.?(?:\s|$)", problem, re.I,
    ):
        raise ControlError("discovery body requires a substantive resolved Problem test")
    frontier = section_content(body, "Open frontier")
    if not frontier:
        raise ControlError("discovery body requires an Open frontier section")
    unresolved_rows = [
        line for line in frontier.splitlines()
        if line.lstrip().startswith("|")
        and "Question" not in line
        and not re.fullmatch(r"\s*\|?[-:| ]+\|?\s*", line)
    ]
    if unresolved_rows:
        raise ControlError("gate-ready discovery body contains an unresolved frontier row")
    if not discovery_decision_ids(body):
        raise ControlError("discovery body requires at least one settled decision record")


def validate_spec_body(body: str) -> None:
    if not re.search(r"(?m)^# Spec(?:\s+—|\s+-|\s*$)", body):
        raise ControlError("spec body must begin with a Spec title")
    positions = []
    for heading in SPEC_REQUIRED_SECTIONS:
        match = re.search(rf"(?m)^## {re.escape(heading)}\s*$", body)
        if not match:
            raise ControlError(f"spec body is missing required section: {heading}")
        positions.append(match.start())
        content = section_content(body, heading)
        if not content or re.search(r"<[^>]+>|\bPending\.?(?:\s|$)", content, re.I):
            raise ControlError(f"spec body section is empty or placeholder-only: {heading}")
    if positions != sorted(positions):
        raise ControlError("spec body required sections are out of order")

    problem = section_content(body, "Problem")
    if len(re.sub(r"\s+", " ", problem)) < 20:
        raise ControlError("spec body Problem must state a substantive observable problem")

    field_contracts = {
        "R": ("Current", "Target", "Acceptance", "Derived from"),
        "P": ("Must never", "Acceptance", "Derived from"),
        "C": ("Constraint", "Derived from"),
        "I": ("Holds", "Derived from"),
    }
    normative_count = 0
    seen_ids: set[str] = set()
    for family, fields in field_contracts.items():
        pattern = re.compile(
            rf"(?ms)^### ({family}-[0-9]{{3}})\s+—\s+.+?\n(.*?)(?=^### |^## |\Z)"
        )
        for item in pattern.finditer(body):
            normative_count += 1
            item_id, item_body = item.groups()
            if item_id in seen_ids:
                raise ControlError(f"spec body repeats normative identifier: {item_id}")
            seen_ids.add(item_id)
            for field in fields:
                if not re.search(rf"(?m)^\*\*{re.escape(field)}:\*\*\s+\S", item_body):
                    raise ControlError(f"spec body {item_id} is missing required field: {field}")

    exclusions = re.findall(r"(?m)^\|\s*(X-[0-9]{3})\s*\|\s*([^|]+)\|\s*([^|]+)\|", section_content(body, "Out of scope"))
    reasoned_exclusions = [row for row in exclusions if row[1].strip() and row[2].strip()]
    if normative_count == 0 and not reasoned_exclusions:
        raise ControlError("spec body requires a normative item or a reasoned exclusion")

    edge_content = section_content(body, "Edge coverage").lower()
    missing_edges = [
        category for category in SPEC_EDGE_CATEGORIES
        if not re.search(rf"\b{re.escape(category)}\b", edge_content)
    ]
    if missing_edges:
        raise ControlError(f"spec body edge coverage is missing categories: {missing_edges}")

    questions = section_content(body, "Open questions")
    if re.search(r"(?im)^\|\s*Q-[0-9]{3}.*\bblocking\b", questions):
        raise ControlError("gate-ready spec body contains a blocking open question")


def validate_candidate_schema(
    phase: str,
    candidate: dict[str, Any],
    config: dict[str, Any],
    run_dir: Path,
    state: dict[str, Any],
    body: str,
) -> None:
    predecessor = latest_approved_candidate(run_dir, state, phase) if phase == "discovery" else None
    expected_fields = (
        REOPENED_DISCOVERY_FIELDS if phase == "discovery" and predecessor
        else CANDIDATE_FIELDS[phase]
    )
    if set(candidate) != expected_fields:
        missing = sorted(expected_fields - set(candidate))
        unexpected = sorted(set(candidate) - expected_fields)
        raise ControlError(
            f"{phase} candidate fields do not match version-1 schema; "
            f"missing={missing}, unexpected={unexpected}"
        )
    version = candidate.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ControlError(f"{phase} candidate version must be a positive integer")
    if not isinstance(candidate.get("gate_ready"), bool):
        raise ControlError(f"{phase} candidate gate_ready must be a boolean")
    if phase == "discovery":
        if not isinstance(candidate.get("intake_stale"), bool):
            raise ControlError("discovery candidate intake_stale must be a boolean")
        expected_repos = validate_repos(config.get("repos"))
        expected_opened = canonical_json_value(config.get("opened"))
        candidate_opened = canonical_json_value(candidate.get("opened"))
        if candidate.get("cold_read") != "complete":
            raise ControlError("discovery candidate cold_read must be complete")
        if not isinstance(expected_opened, str) or candidate_opened != expected_opened:
            raise ControlError("discovery candidate opened date does not match run.yaml")
        if candidate.get("repos") != [item["repository"] for item in expected_repos]:
            raise ControlError("discovery candidate repos do not match effective intake")
        if predecessor:
            predecessor_path, predecessor_candidate = predecessor
            if candidate.get("supersedes") != predecessor_path:
                raise ControlError("reopened discovery candidate must supersede the active approved copy")
            predecessor_version = predecessor_candidate.get("version")
            if not isinstance(predecessor_version, int) or candidate["version"] != predecessor_version + 1:
                raise ControlError("reopened discovery candidate version must follow its approved predecessor")
        elif candidate["version"] != 1:
            raise ControlError("initial discovery candidate version must be 1")
        validate_discovery_body(body)
    elif phase == "spec":
        if candidate["version"] != 1:
            raise ControlError("initial spec candidate version must be 1")
        if candidate.get("supersedes") is not None:
            raise ControlError("spec candidate supersedes must be null until amendments are implemented")
        if candidate.get("amendment") is not None:
            raise ControlError("spec candidate amendment must be null until amendments are implemented")
        if candidate.get("derived-from") != "10-decisions.md":
            raise ControlError("spec candidate must derive from 10-decisions.md")
        validate_spec_body(body)


def validate_spec_decision_references(
    run_dir: Path, state: dict[str, Any], config: dict[str, Any], spec_body: str
) -> None:
    discovery = verify_active_approval(run_dir, state, config, "discovery")
    approved_rel = discovery.get("approved_copy")
    if not isinstance(approved_rel, str):
        raise ControlError("approved discovery has no immutable copy path")
    _, approved_body = read_frontmatter(managed_path(run_dir, approved_rel))
    approved_ids = discovery_decision_ids(approved_body)
    references = set(re.findall(r"\bD-[0-9]{3}\b", spec_body))
    if not references:
        raise ControlError("spec body contains no decision references")
    missing = sorted(references - approved_ids)
    if missing:
        raise ControlError(
            f"spec decision references are not present in immutable approved discovery: {missing}"
        )


def verify_active_approval(
    run_dir: Path, state: dict[str, Any], config: dict[str, Any], phase: str
) -> dict[str, Any]:
    if phase not in CANDIDATES:
        raise ControlError(f"cannot verify predecessor {phase}: unsupported artifact")
    expected_states = {"HUMAN": "HUMAN_APPROVED", "AUTO": "AGENT_APPROVED"}
    candidate_path = managed_path(run_dir, CANDIDATES[phase])
    if not candidate_path.is_file():
        raise ControlError(f"predecessor {phase} candidate is missing")
    candidate, _ = read_frontmatter(candidate_path)
    if candidate.get("run") != config.get("run"):
        raise ControlError(f"predecessor {phase} candidate has wrong run identity")
    if candidate.get("status") != "approved":
        raise ControlError(f"predecessor {phase} candidate is not approved")
    if candidate.get("effective_config_revision") != state.get("effective_config_revision"):
        raise ControlError(f"predecessor {phase} uses a different effective-config revision")
    authority = candidate.get("approved_authority")
    if authority not in expected_states or state.get("gates", {}).get(phase) != expected_states[authority]:
        raise ControlError(f"predecessor {phase} gate state does not match its approval")
    approved = candidate.get("approved")
    try:
        if not isinstance(approved, str) or date.fromisoformat(approved).isoformat() != approved:
            raise ValueError
    except ValueError as exc:
        raise ControlError(f"predecessor {phase} approval date is invalid") from exc
    approved_rel = candidate.get("approved_copy")
    approved_hash = candidate.get("approved_sha256")
    if not isinstance(approved_rel, str) or not re.fullmatch(
        rf"approved/{re.escape(phase)}-r[1-9][0-9]*\.md", approved_rel
    ) or not isinstance(approved_hash, str):
        raise ControlError(f"predecessor {phase} has no valid immutable receipt")
    receipt = state.get("approved_artifacts", {}).get(approved_rel)
    if not isinstance(receipt, dict) or any((
        receipt.get("phase") != phase,
        receipt.get("sha256") != approved_hash,
        receipt.get("authority") != authority,
        receipt.get("approved") != approved,
    )):
        raise ControlError(f"predecessor {phase} receipt is missing or inconsistent")
    return candidate


def verify_predecessor_history(
    run_dir: Path, state: dict[str, Any], config: dict[str, Any], phase: str
) -> None:
    stages = config.get("stages")
    if not isinstance(stages, list) or phase not in stages:
        raise ControlError(f"phase {phase} is absent from stages")
    for predecessor in stages[:stages.index(phase)]:
        if not isinstance(predecessor, str):
            raise ControlError("stage names must be strings")
        verify_active_approval(run_dir, state, config, predecessor)


def require_gateable_candidate(
    run_dir: Path, state: dict[str, Any], config: dict[str, Any]
) -> tuple[str, Path, dict[str, Any], str]:
    require_unblocked_planning(state)
    phase = state.get("phase")
    if phase not in CANDIDATES:
        raise ControlError(f"unsupported current phase: {phase}")
    gate_state = state.get("gates", {}).get(phase)
    if gate_state not in ("PENDING", "STALE"):
        raise ControlError(f"{phase} gate is not pending or stale: {gate_state}")
    candidate_path = managed_path(run_dir, CANDIDATES[phase])
    candidate, candidate_body = read_frontmatter(candidate_path)
    run_identity = verify_run_state_identity(
        state, config, int(state.get("effective_config_revision", -1))
    )
    verify_candidate_identity(candidate, state, run_identity)
    if candidate.get("status") != "draft":
        raise ControlError("candidate status must be draft")
    if any(candidate.get(field) is not None for field in (
        "approved", "approved_authority", "approved_copy", "approved_sha256"
    )):
        raise ControlError("candidate already contains approval receipt fields")
    if candidate.get("gate_ready") is not True:
        raise ControlError(f"{candidate_path.name} is not gate-ready")
    if candidate.get("intake_stale") is True:
        raise ControlError("candidate reports stale intake")
    validate_candidate_schema(phase, candidate, config, run_dir, state, candidate_body)
    return phase, candidate_path, candidate, candidate_body


def advance(run_dir: Path, approval: str | None, accepted: str) -> str:
    config, config_revision = load_effective_run(run_dir)
    state_path = managed_path(run_dir, "00-state.md")
    state, state_body = read_frontmatter(state_path)
    if state.get("effective_config_revision") != config_revision:
        raise ControlError("state does not match the latest accepted amendment")
    verify_effective_state(state, config, config_revision)
    verify_base_run_bytes(run_dir, state)
    verify_approved_artifacts(run_dir, state)
    verify_accepted_amendments(run_dir, state)
    try:
        if date.fromisoformat(accepted).isoformat() != accepted:
            raise ValueError
    except ValueError as exc:
        raise ControlError("approval date must be canonical YYYY-MM-DD") from exc
    phase, candidate_path, candidate, candidate_body = require_gateable_candidate(run_dir, state, config)

    policy = config.get("gates", {}).get(phase)
    if not isinstance(policy, dict) or "authority" not in policy:
        raise ControlError(f"missing gate policy for {phase}")
    authority = policy["authority"]
    if authority == "HUMAN" and approval != "human":
        raise ControlError("HUMAN gate requires --approval human")
    if authority == "AUTO" and approval not in (None, "auto"):
        raise ControlError("AUTO gate does not accept human or agent approval")
    if authority not in ("HUMAN", "AUTO"):
        raise ControlError(f"authority {authority} is not implemented yet")

    stages = config.get("stages")
    if not isinstance(stages, list) or phase not in stages:
        raise ControlError(f"phase {phase} is absent from stages")
    index = stages.index(phase)
    verify_predecessor_history(run_dir, state, config, phase)
    if phase == "spec":
        validate_spec_decision_references(run_dir, state, config, candidate_body)
    if index + 1 >= len(stages):
        raise ControlError(f"phase {phase} has no next stage")
    next_phase = stages[index + 1]

    candidate["status"] = "approved"
    candidate["approved"] = accepted
    candidate["approved_authority"] = authority
    next_revision = int(state.get("revision", 0)) + 1
    approved_rel = f"approved/{phase}-r{next_revision}.md"
    approved_path = managed_path(run_dir, approved_rel)
    if approved_path.exists():
        raise ControlError(f"approved copy already exists: {approved_rel}")
    approved_text = render_frontmatter(candidate, candidate_body)
    candidate["approved_copy"] = approved_rel
    candidate["approved_sha256"] = hashlib.sha256(approved_text.encode("utf-8")).hexdigest()
    ledger = state.setdefault("approved_artifacts", {})
    if approved_rel in ledger:
        raise ControlError(f"approved receipt already exists: {approved_rel}")
    ledger[approved_rel] = {
        "phase": phase,
        "sha256": candidate["approved_sha256"],
        "authority": authority,
        "approved": accepted,
    }
    approval_state = "HUMAN_APPROVED" if authority == "HUMAN" else "AGENT_APPROVED"
    state.setdefault("gates", {})[phase] = approval_state
    state["phase"] = next_phase
    state["status"] = "PLANNING"
    state["revision"] = next_revision
    state["blocked_reason"] = None
    state["pending_amendment"] = None
    state_body = replace_section(
        state_body, "Next", f"{next_phase} is next. Authority: {config.get('gates', {}).get(next_phase, {}).get('authority', 'UNSPECIFIED')}."
    )
    state_body = replace_section(
        state_body, "Notes", f"- {phase} ({approved_rel}) {authority}-approved on {accepted}."
    )

    write_files_atomic(run_dir, [
        (approved_path, approved_text),
        (candidate_path, render_frontmatter(candidate, candidate_body)),
        (state_path, render_frontmatter(state, state_body)),
    ])
    return f"advanced {phase} -> {next_phase}; state revision {state['revision']}"


def apply_amendment(run_dir: Path) -> str:
    effective, config_revision = load_effective_run(run_dir)
    state_path = managed_path(run_dir, "00-state.md")
    state, body = read_frontmatter(state_path)
    verify_approved_artifacts(run_dir, state)
    verify_accepted_amendments(run_dir, state)
    verify_base_run_bytes(run_dir, state)
    current = int(state.get("effective_config_revision", 0))
    verify_run_state_identity(state, effective, current)
    if config_revision != current + 1:
        raise ControlError(
            f"expected exactly one pending accepted amendment after revision {current}; found {config_revision}"
        )
    expected_amendment = f"run-config-{config_revision:03d}"
    if state.get("status") != "BLOCKED" or state.get("pending_amendment") != expected_amendment:
        raise ControlError(f"state does not authorize pending amendment {expected_amendment}")
    if state.get("gates", {}).get("discovery") != "STALE":
        raise ControlError("discovery gate must be STALE before applying intake amendment")
    newest_rel = f"amendments/run-config-{config_revision:03d}.yaml"
    newest = managed_path(run_dir, newest_rel)
    newest_data = yaml.safe_load(newest.read_text(encoding="utf-8"))
    if state.get("effective_config_hash") != newest_data.get("prior_effective_hash"):
        raise ControlError("state effective configuration hash does not match amendment predecessor")
    repos = effective.get("repos")
    if not isinstance(repos, list) or any(
        not isinstance(item, dict) or "repository" not in item or "baseline" not in item
        for item in repos
    ):
        raise ControlError("effective repos must contain repository-baseline maps")
    state["effective_config_revision"] = config_revision
    state["effective_config_hash"] = canonical_hash(effective)
    amendment_ledger = state.setdefault("accepted_amendments", {})
    if newest_rel in amendment_ledger:
        raise ControlError(f"accepted amendment receipt already exists: {newest_rel}")
    amendment_ledger[newest_rel] = file_sha256(newest)
    state["repos"] = [item["repository"] for item in repos]
    state["status"] = "PLANNING"
    state["revision"] = int(state.get("revision", 0)) + 1
    state["blocked_reason"] = None
    state["pending_amendment"] = None
    body = replace_section(body, "Notes", f"- Accepted run-configuration amendment revision {config_revision}.")
    write_files_atomic(run_dir, [(state_path, render_frontmatter(state, body))])
    return f"applied amendment revision {config_revision}; state revision {state['revision']}"


def mark_stale(run_dir: Path, reason: str) -> str:
    effective, config_revision = load_effective_run(run_dir)
    state_path = managed_path(run_dir, "00-state.md")
    state, body = read_frontmatter(state_path)
    if state.get("effective_config_revision") != config_revision:
        raise ControlError("state does not match the latest accepted amendment")
    verify_effective_state(state, effective, config_revision)
    verify_base_run_bytes(run_dir, state)
    verify_approved_artifacts(run_dir, state)
    verify_accepted_amendments(run_dir, state)
    require_unblocked_planning(state)
    run_identity = verify_run_state_identity(state, effective, config_revision)
    gate_state = state.get("gates", {}).get("discovery")
    predecessor = latest_approved_candidate(run_dir, state, "discovery")
    if state.get("phase") != "discovery" or not (
        gate_state == "PENDING" or (gate_state == "STALE" and predecessor is not None)
    ):
        raise ControlError("only a pending or legally reopened discovery gate can mark intake stale")
    candidate, candidate_body = read_frontmatter(managed_path(run_dir, CANDIDATES["discovery"]))
    verify_candidate_identity(candidate, state, run_identity)
    if candidate.get("status") != "draft":
        raise ControlError("candidate status must be draft")
    validate_candidate_schema(
        "discovery", candidate, effective, run_dir, state, candidate_body
    )
    if candidate.get("intake_stale") is not True or candidate.get("gate_ready") is not False:
        raise ControlError("discovery candidate must persist intake_stale: true and gate_ready: false")
    if not reason.strip():
        raise ControlError("mark-stale requires a non-empty reason")
    pending = f"run-config-{config_revision + 1:03d}"
    state["status"] = "BLOCKED"
    state["gates"]["discovery"] = "STALE"
    state["blocked_reason"] = reason.strip()
    state["pending_amendment"] = pending
    state["revision"] = int(state.get("revision", 0)) + 1
    body = replace_section(body, "Next", f"Stage 0 must accept and write {pending}; then apply it through atlas-control.")
    body = replace_section(body, "Notes", f"- Discovery marked intake stale: {reason.strip()}")
    write_files_atomic(run_dir, [(state_path, render_frontmatter(state, body))])
    return f"marked discovery intake stale; pending {pending}; state revision {state['revision']}"


def reopen(run_dir: Path, target: str, reason: str) -> str:
    effective, config_revision = load_effective_run(run_dir)
    state_path = managed_path(run_dir, "00-state.md")
    state, state_body = read_frontmatter(state_path)
    if state.get("effective_config_revision") != config_revision:
        raise ControlError("state does not match the latest accepted amendment")
    verify_effective_state(state, effective, config_revision)
    verify_base_run_bytes(run_dir, state)
    verify_approved_artifacts(run_dir, state)
    verify_accepted_amendments(run_dir, state)
    require_unblocked_planning(state)
    verify_run_state_identity(state, effective, config_revision)
    if state.get("phase") != "spec" or target != "discovery":
        raise ControlError("the only implemented backtrack is spec -> discovery")
    verify_predecessor_history(run_dir, state, effective, "spec")
    if not reason.strip():
        raise ControlError("reopen requires a non-empty reason")

    decisions_path = managed_path(run_dir, "10-decisions.md")
    decisions, decisions_body = read_frontmatter(decisions_path)
    approved_rel = decisions.get("approved_copy")
    approved_hash = decisions.get("approved_sha256")
    if not isinstance(approved_rel, str) or not isinstance(approved_hash, str):
        raise ControlError("discovery has no immutable approved-copy receipt")
    if not re.fullmatch(r"approved/discovery-r[1-9][0-9]*\.md", approved_rel):
        raise ControlError("discovery approved-copy path is invalid")
    approved_path = managed_path(run_dir, approved_rel)
    if not approved_path.is_file() or hashlib.sha256(approved_path.read_bytes()).hexdigest() != approved_hash:
        raise ControlError("discovery approved-copy hash mismatch")
    ledger_receipt = state.get("approved_artifacts", {}).get(approved_rel)
    if not isinstance(ledger_receipt, dict) or ledger_receipt.get("sha256") != approved_hash:
        raise ControlError("discovery approved-copy receipt is absent from state ledger")

    spec_path = managed_path(run_dir, "20-spec.md")
    spec_pair: tuple[Path, str] | None = None
    if spec_path.exists():
        spec, spec_body = read_frontmatter(spec_path)
        spec["status"] = "stale"
        spec["gate_ready"] = False
        spec["approved"] = None
        spec["approved_authority"] = None
        spec_pair = (spec_path, render_frontmatter(spec, spec_body))
    decisions["version"] = int(decisions.get("version", 1)) + 1
    decisions["status"] = "draft"
    decisions["gate_ready"] = False
    decisions["approved"] = None
    decisions["approved_authority"] = None
    decisions["approved_copy"] = None
    decisions["approved_sha256"] = None
    decisions["supersedes"] = approved_rel

    state["phase"] = "discovery"
    state["status"] = "PLANNING"
    state["revision"] = int(state.get("revision", 0)) + 1
    state.setdefault("gates", {})["discovery"] = "STALE"
    state["gates"]["spec"] = "STALE"
    state["blocked_reason"] = None
    state_body = replace_section(state_body, "Next", "discovery is next. Resolve the persisted backtrack reason and produce a new candidate version.")
    state_body = replace_section(state_body, "Notes", f"- Reopened spec -> discovery: {reason.strip()}")
    pairs = [
        (decisions_path, render_frontmatter(decisions, decisions_body)),
        (state_path, render_frontmatter(state, state_body)),
    ]
    if spec_pair is not None:
        pairs.insert(1, spec_pair)
    write_files_atomic(run_dir, pairs)
    return f"reopened spec -> discovery; state revision {state['revision']}"


def reject(run_dir: Path, reason: str) -> str:
    effective, config_revision = load_effective_run(run_dir)
    state_path = managed_path(run_dir, "00-state.md")
    state, body = read_frontmatter(state_path)
    if state.get("effective_config_revision") != config_revision:
        raise ControlError("state does not match the latest accepted amendment")
    verify_effective_state(state, effective, config_revision)
    verify_base_run_bytes(run_dir, state)
    verify_approved_artifacts(run_dir, state)
    verify_accepted_amendments(run_dir, state)
    phase, _, _, _ = require_gateable_candidate(run_dir, state, effective)
    if not reason.strip():
        raise ControlError("reject requires a non-empty reason")
    state.setdefault("gates", {})[phase] = "REJECTED"
    state["status"] = "BLOCKED"
    state["blocked_reason"] = reason.strip()
    state["revision"] = int(state.get("revision", 0)) + 1
    body = replace_section(body, "Next", f"{phase} is blocked by a rejected gate. Reopen only through an explicit recovery decision.")
    body = replace_section(body, "Notes", f"- Rejected {phase}: {reason.strip()}")
    write_files_atomic(run_dir, [(state_path, render_frontmatter(state, body))])
    return f"rejected {phase}; state revision {state['revision']}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("initialize", help="seal the immutable base intake in pristine state")
    init.add_argument("--run", required=True, type=Path)
    cmd = sub.add_parser("advance", help="apply one gate and advance one phase")
    cmd.add_argument("--run", required=True, type=Path)
    cmd.add_argument("--approval", choices=("human", "agent", "auto"))
    cmd.add_argument("--date", default=date.today().isoformat())
    amend = sub.add_parser("apply-amendment", help="apply one accepted run-config amendment to state")
    amend.add_argument("--run", required=True, type=Path)
    back = sub.add_parser("reopen", help="apply one legal backward transition")
    back.add_argument("--run", required=True, type=Path)
    back.add_argument("--to", required=True, choices=("discovery",))
    back.add_argument("--reason", required=True)
    denied = sub.add_parser("reject", help="persist one rejected gate outcome")
    denied.add_argument("--run", required=True, type=Path)
    denied.add_argument("--reason", required=True)
    stale = sub.add_parser("mark-stale", help="persist discovery's stale-intake transition")
    stale.add_argument("--run", required=True, type=Path)
    stale.add_argument("--reason", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run_dir = args.run.resolve()
        with run_lock(run_dir):
            if recover_transaction(run_dir):
                print(
                    "recovered an interrupted transaction; no requested operation was executed; inspect state before retrying",
                    file=sys.stderr,
                )
                return 1
            if args.command == "initialize":
                print(initialize(run_dir))
                return 0
            if args.command == "advance":
                print(advance(run_dir, args.approval, args.date))
                return 0
            if args.command == "apply-amendment":
                print(apply_amendment(run_dir))
                return 0
            if args.command == "reopen":
                print(reopen(run_dir, args.to, args.reason))
                return 0
            if args.command == "reject":
                print(reject(run_dir, args.reason))
                return 0
            if args.command == "mark-stale":
                print(mark_stale(run_dir, args.reason))
                return 0
    except (ControlError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"atlas-control: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
