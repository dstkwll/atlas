#!/usr/bin/env python3
"""Read-only Atlas run inventory for the Gazetteer front door."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

import atlas_control
import atlas_planning
import atlas_repository


REPORT_VERSION = 1


def gap(
    code: str,
    problem: str,
    resume_action: str,
    **context: str,
) -> dict[str, str]:
    return {
        "code": code,
        "problem": problem,
        "resume_action": resume_action,
        **context,
    }


def _planning_root(config: Mapping[str, Any], cwd: Path) -> Path:
    artifacts = config.get("artifacts")
    raw = artifacts.get("planning_root") if isinstance(artifacts, dict) else None
    if not isinstance(raw, str) or not raw.strip():
        raise atlas_control.ControlError("machine config artifacts.planning_root is missing")
    root = Path(raw)
    if not root.is_absolute():
        try:
            repository_root_raw = atlas_repository._git_text(
                ("rev-parse", "--show-toplevel"),
                source=cwd,
                code="repository_unavailable",
                problem="current location is not inside a readable Git repository",
                resume_action="open the repository that owns the configured relative planning root",
            )
            repository_root = Path(repository_root_raw).resolve(strict=True)
        except atlas_repository.RepositoryBlocked as exc:
            raise atlas_control.ControlError(exc.problem) from exc
        root = repository_root / root
    if root.is_symlink():
        raise atlas_control.ControlError("planning root may not be a symlink")
    try:
        resolved = root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise atlas_control.ControlError(f"planning root is unavailable: {exc}") from exc
    if resolved != root or not root.is_dir():
        raise atlas_control.ControlError("planning root must be one canonical existing directory")
    return root


def _run_identity(effective: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    return {
        "run": effective["run"],
        "path": str(run_dir),
        "goal": effective["goal"],
        "repositories": [item["repository"] for item in effective["repos"]],
    }


def _accepted_boundaries(
    effective: dict[str, Any],
    control: dict[str, Any] | None,
    planning: dict[str, Any] | None,
) -> list[str]:
    accepted: set[str] = set()
    if control is not None:
        accepted.update(
            stage for stage, record in control["acceptances"].items() if record is not None
        )
    if planning is not None:
        accepted.update(
            stage for stage, record in planning["acceptances"].items() if record is not None
        )
    return [stage for stage in effective["stages"] if stage in accepted]


def _accepted_graph(run_dir: Path, planning: dict[str, Any]) -> dict[str, Any] | None:
    acceptance = planning["acceptances"]["tickets"]
    if acceptance is None:
        return None
    manifest_path = atlas_control.managed_path(run_dir, atlas_planning.TICKET_GRAPH_FILE)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "version": acceptance["candidate_version"],
        "sha256": acceptance["candidate_sha256"],
        "ticket_ids": [entry["id"] for entry in manifest["tickets"]],
    }


def _summarize_run(run_dir: Path) -> dict[str, Any]:
    control_path = atlas_control.managed_path(run_dir, "control.json")
    if not control_path.is_file():
        effective = atlas_control.load_run(run_dir)
        atlas_control.validate_run(effective)
        return {
            **_run_identity(effective, run_dir),
            "status": "INTERRUPTED",
            "phase": effective["stages"][0],
            "blocked_reason": None,
            "ready_for_execution": False,
            "continuation": "INITIALIZE",
            "accepted_boundaries": [],
            "accepted_graph": None,
        }

    control, effective = atlas_control.verified_state(run_dir)
    planning: dict[str, Any] | None = None
    if control["phase"] == "discovery":
        status = control["status"]
        phase = control["phase"]
        blocked_reason = control["blocked_reason"]
        ready = False
        continuation = "DISCOVERY" if status == "PLANNING" else "BLOCKED"
    elif not atlas_control.managed_path(run_dir, "planning-control.json").is_file():
        status = control["status"]
        phase = control["phase"]
        blocked_reason = control["blocked_reason"]
        ready = False
        continuation = "HANDOFF_REQUIRED"
    else:
        planning, _, effective = atlas_planning.verified_planning_state(run_dir)
        status = planning["status"]
        phase = planning["phase"]
        blocked_reason = planning["blocked_reason"]
        ready = status == "READY_FOR_EXECUTION"
        continuation = "READY_FOR_EXECUTION" if ready else status
    return {
        **_run_identity(effective, run_dir),
        "status": status,
        "phase": phase,
        "blocked_reason": blocked_reason,
        "ready_for_execution": ready,
        "continuation": continuation,
        "accepted_boundaries": _accepted_boundaries(effective, control, planning),
        "accepted_graph": _accepted_graph(run_dir, planning) if planning is not None else None,
    }


def inventory(cwd: Path) -> dict[str, Any]:
    config_path, config = atlas_repository.load_machine_config()
    if config_path is None:
        return {
            "version": REPORT_VERSION,
            "command": "inventory",
            "verdict": "NOT_CONFIGURED",
            "config_path": None,
            "planning_root": None,
            "runs": [],
            "gaps": [
                gap(
                    "config_missing",
                    "Atlas machine configuration is missing",
                    "configure Atlas through Gazetteer setup",
                )
            ],
        }
    root = _planning_root(config, cwd)
    _, bindings = atlas_repository.load_bindings()
    repository_location = atlas_repository.repository_identity_for_location(cwd, bindings)
    current_repository_identity = repository_location.identity
    runs: list[dict[str, Any]] = []
    gaps: list[dict[str, str]] = [
        gap(
            item.code,
            item.problem,
            item.resume_action,
            repository=item.repository,
        )
        for item in repository_location.gaps
        if item.repository is not None
    ]
    for child in sorted(root.iterdir(), key=lambda path: path.name):
        if not child.is_dir() or child.is_symlink() or not (child / "run.yaml").is_file():
            continue
        try:
            runs.append(_summarize_run(child))
        except (atlas_control.ControlError, OSError, UnicodeError, yaml.YAMLError) as exc:
            gaps.append(
                gap(
                    "invalid_run",
                    f"{child.name}: {exc}",
                    "restore the accepted run.yaml bytes or start a corrected new run",
                    run=child.name,
                )
            )
    unavailable_repositories = {
        item["repository"]
        for item in gaps
        if item.get("code") == "binding_unavailable" and "repository" in item
    }
    return {
        "version": REPORT_VERSION,
        "command": "inventory",
        "verdict": "PARTIAL" if gaps else "PASS",
        "config_path": str(config_path),
        "planning_root": str(root),
        "current_repository_identity": current_repository_identity,
        "repository_relevant_runs": [
            row["run"]
            for row in runs
            if current_repository_identity is not None
            and current_repository_identity in row["repositories"]
        ],
        "repository_blocked_runs": [
            row["run"]
            for row in runs
            if unavailable_repositories.intersection(row["repositories"])
        ],
        "runs": runs,
        "gaps": gaps,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inventory_parser = sub.add_parser("inventory", help="list validated Atlas runs")
    inventory_parser.add_argument("--cwd", type=Path, default=Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inventory":
        try:
            report = inventory(args.cwd.resolve())
        except atlas_repository.RepositoryBlocked as exc:
            config_path = atlas_repository.selected_config_path()
            report = {
                "version": REPORT_VERSION,
                "command": "inventory",
                "verdict": "BLOCKED",
                "config_path": str(config_path) if config_path is not None else None,
                "planning_root": None,
                "current_repository_identity": None,
                "repository_relevant_runs": [],
                "runs": [],
                "gaps": [gap(exc.code, exc.problem, exc.resume_action)],
            }
        except (atlas_control.ControlError, OSError) as exc:
            config_path = atlas_repository.selected_config_path()
            report = {
                "version": REPORT_VERSION,
                "command": "inventory",
                "verdict": "BLOCKED",
                "config_path": str(config_path) if config_path is not None else None,
                "planning_root": None,
                "current_repository_identity": None,
                "repository_relevant_runs": [],
                "runs": [],
                "gaps": [
                    gap(
                        "inventory_unavailable",
                        str(exc),
                        "repair the configured planning root before continuing",
                    )
                ],
            }
        print(json.dumps(report, sort_keys=True))
        return 1 if report["verdict"] == "BLOCKED" else 0
    raise AssertionError(args.command)  # pragma: no cover


if __name__ == "__main__":
    raise SystemExit(main())
