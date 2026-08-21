#!/usr/bin/env python3
"""Deterministic Slice-0 initializer for Atlas downstream planning state."""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator, Optional

import yaml

from atlas_control import (
    ControlError,
    file_sha256,
    load_json,
    managed_path,
    resolve_existing_run_directory,
    validate_run,
    verified_state,
)

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


def write_planning_control_atomic(run_dir: Path, planning: dict[str, Any]) -> None:
    path = managed_path(run_dir, PLANNING_FILE)
    content = json.dumps(planning, indent=2, sort_keys=True) + "\n"
    fd, name = tempfile.mkstemp(prefix=".planning-control.json.", dir=run_dir)
    temp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


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
    if (
        not isinstance(gates, dict)
        or set(gates) != set(DOWNSTREAM_STAGES)
        or any(value not in {"PENDING", "NOT_REQUIRED"} for value in gates.values())
        or not isinstance(acceptances, dict)
        or set(acceptances) != set(DOWNSTREAM_STAGES)
        or any(value is not None for value in acceptances.values())
    ):
        raise ControlError("planning-control.json initial gates or acceptances are malformed")
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
    if (
        planning.get("version") != 1
        or isinstance(planning.get("version"), bool)
        or not isinstance(planning.get("run"), str)
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", planning["run"])
        or planning.get("status") != "PLANNING"
        or planning.get("phase") not in DOWNSTREAM_STAGES
        or gates.get(planning.get("phase")) != "PENDING"
        or not any(value == "PENDING" for value in gates.values())
        or planning.get("revision") != 1
        or isinstance(planning.get("revision"), bool)
        or planning.get("blocked_reason") is not None
    ):
        raise ControlError("planning-control.json initial values are malformed")
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
        or not dimensions
        or any(not isinstance(item, str) or not item.strip() for item in dimensions)
    ):
        raise ControlError("system_design HUMAN_IF_CHANGED requires nonempty material_dimensions and AGENT_REVIEW otherwise")


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    initialize = sub.add_parser("initialize")
    initialize.add_argument("--run", required=True, type=Path)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run_dir = resolve_existing_run_directory(args.run)
        with planning_lock(run_dir):
            print(initialize_planning(run_dir))
        return 0
    except (ControlError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"atlas-planning: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
