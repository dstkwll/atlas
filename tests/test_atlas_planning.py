import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from tests.test_atlas_control import (
    advance_discovery,
    initialize_cli,
    read_control,
    run_cli,
    run_config as control_run_config,
    sha256,
    write_discovery,
    write_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
PLANNING_CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_planning.py"
SYSTEM_RENDERER = ROOT / "plugins" / "atlas" / "tools" / "render_system_design.py"
REAL_GIT = shutil.which("git")
if REAL_GIT is None:  # pragma: no cover - the test environment requires Git
    raise RuntimeError("git is required")
assert REAL_GIT is not None
_TEST_REPOSITORY_BASELINES = None
_TEST_REPOSITORY_SOURCES: dict[str, Path] = {}
if str(PLANNING_CLI.parent) not in sys.path:
    sys.path.insert(0, str(PLANNING_CLI.parent))
PLANNING_SPEC = importlib.util.spec_from_file_location("atlas_planning", PLANNING_CLI)
assert PLANNING_SPEC is not None and PLANNING_SPEC.loader is not None
PLANNING = importlib.util.module_from_spec(PLANNING_SPEC)
PLANNING_SPEC.loader.exec_module(PLANNING)


def run_config():
    config = control_run_config()
    if _TEST_REPOSITORY_BASELINES is not None:
        config["repos"] = [dict(item) for item in _TEST_REPOSITORY_BASELINES]
    return config


def git(repo: Path, *args: str) -> str:
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": "Atlas Planning Test",
        "GIT_AUTHOR_EMAIL": "atlas-planning@example.invalid",
        "GIT_COMMITTER_NAME": "Atlas Planning Test",
        "GIT_COMMITTER_EMAIL": "atlas-planning@example.invalid",
    })
    result = subprocess.run(
        [REAL_GIT, "-C", str(repo), *args],
        env=env,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def create_repository(path: Path, content: str) -> str:
    path.mkdir()
    result = subprocess.run(
        [REAL_GIT, "init", "-q", str(path)], text=True, capture_output=True
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    (path / "source.txt").write_text(content, encoding="utf-8")
    git(path, "add", "--", "source.txt")
    git(path, "commit", "-q", "-m", "planning fixture baseline")
    return git(path, "rev-parse", "HEAD")


def write_repository_bindings(bindings: dict[str, Path]) -> Path:
    path = Path(os.environ["XDG_CONFIG_HOME"]) / "atlas" / "config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({
        "repositories": {
            "bindings": {identity: str(source) for identity, source in bindings.items()}
        }
    }, sort_keys=False), encoding="utf-8")
    return path


def planning_cli(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(PLANNING_CLI), *map(str, args)],
        cwd=cwd,
        text=True,
        capture_output=True,
    )


def render_system_board(run: Path):
    return subprocess.run(
        [sys.executable, str(SYSTEM_RENDERER), "render", "--run", str(run)],
        text=True,
        capture_output=True,
    )


def write_stage0_run(run: Path, config: dict) -> None:
    (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    result = initialize_cli(run)
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def direct_config(*, version=2, participation="agent_led"):
    config = run_config()
    config["version"] = version
    config["stages"] = ["system_design", "tickets", "execute"]
    config["gates"].pop("discovery")
    config["gates"].pop("program_design")
    config["gates"]["system_design"] = {"authority": "HUMAN"}
    config["gates"]["tickets"] = {"authority": "HUMAN"}
    if version == 2:
        config["system_design_participation"] = participation
    return config


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
SYSTEM_DESIGN_DIMENSIONS = (
    "responsibilities_and_system_seams",
    "authoritative_data_ownership",
    "cross_module_external_contracts_and_dependencies",
    "target_schema_protocol",
    "end_to_end_lifecycle_failure_recovery",
    "compatibility_guarantees",
    "trust_security_operational_commitments",
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
PROGRAM_DESIGN_DIMENSIONS = (
    "upstream_commitment_realization",
    "repository_grounding_and_feasibility",
    "files_packages_types_and_responsibilities",
    "signatures_call_and_data_flow",
    "state_locking_concurrency_and_lifetime",
    "migration_and_local_failure_path_implementation",
    "testability_and_compilation_readiness",
)


def write_system_design(run: Path, source_binding: dict, **overrides) -> None:
    frontmatter = {
        "run": "demo",
        "version": 1,
        "status": "draft",
        "gate_ready": True,
        "participation": "agent_led",
        "opened": "2026-08-20",
        "source_binding": source_binding,
    }
    frontmatter.update(overrides)
    body = "# System design — Demo\n\n" + "\n".join(
        f"## {heading}\n\nConcrete {heading.lower()} decisions.\n"
        for heading in SYSTEM_DESIGN_SECTIONS
    )
    from tests.test_atlas_control import write_markdown
    write_markdown(run / "30-system-design.md", frontmatter, body)


def write_program_design(run: Path, source_binding: dict, **overrides) -> None:
    frontmatter = {
        "run": "demo",
        "version": 1,
        "status": "draft",
        "gate_ready": True,
        "opened": "2026-08-20",
        "source_binding": source_binding,
    }
    frontmatter.update(overrides)
    body = "# Program design — Demo\n\n" + "\n".join(
        f"## {heading}\n\nConcrete {heading.lower()} mechanics.\n"
        for heading in PROGRAM_DESIGN_SECTIONS
    )
    write_markdown(run / "40-program-design.md", frontmatter, body)


def initialize_program_after_system(run: Path) -> dict:
    config = direct_config()
    config["stages"].insert(1, "program_design")
    config["gates"]["program_design"] = {"authority": "AGENT_REVIEW"}
    write_stage0_run(run, config)
    initialized = planning_cli("initialize", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
    anchor = planning["stage0_anchor"]
    write_system_design(run, {
        "kind": "stage0",
        "artifact": "run.yaml",
        "sha256": anchor["base_run_sha256"],
        "effective_config_hash": anchor["effective_config_hash"],
        "effective_config_revision": anchor["effective_config_revision"],
    })
    accepted = planning_cli(
        "advance", "--run", run, "--stage", "system_design",
        "--approval", "human", "--date", "2026-08-21",
    )
    if accepted.returncode != 0:
        raise AssertionError(accepted.stderr)
    return json.loads((run / "planning-control.json").read_text(encoding="utf-8"))


def initialize_direct_program(run: Path, *, authority="AGENT_REVIEW", repos=None) -> dict:
    config = run_config()
    config["version"] = 2
    config["system_design_participation"] = None
    config["stages"] = ["program_design", "tickets", "execute"]
    config["gates"].pop("discovery")
    config["gates"]["program_design"] = {"authority": authority}
    config["gates"]["tickets"] = {"authority": "HUMAN"}
    if repos is not None:
        config["repos"] = repos
    write_stage0_run(run, config)
    initialized = planning_cli("initialize", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    return json.loads((run / "planning-control.json").read_text(encoding="utf-8"))


def initialize_product_program(run: Path, *, authority="AGENT_REVIEW") -> dict:
    config = run_config()
    config["version"] = 2
    config["system_design_participation"] = None
    config["stages"] = ["discovery", "program_design", "tickets", "execute"]
    config["gates"]["program_design"] = {"authority": authority}
    config["gates"]["tickets"] = {"authority": "HUMAN"}
    write_stage0_run(run, config)
    write_discovery(run)
    accepted = advance_discovery(run)
    initialized = planning_cli("ensure", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    return accepted


def initialize_product_system_program(run: Path, *, authority="AGENT_REVIEW") -> dict:
    config = run_config()
    config["version"] = 2
    config["system_design_participation"] = "agent_led"
    config["stages"] = ["discovery", "system_design", "program_design", "tickets", "execute"]
    config["gates"]["system_design"] = {"authority": "HUMAN"}
    config["gates"]["program_design"] = {"authority": authority}
    config["gates"]["tickets"] = {"authority": "HUMAN"}
    write_stage0_run(run, config)
    write_discovery(run)
    accepted_product = advance_discovery(run)
    initialized = planning_cli("ensure", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
    write_system_design(run, {
        "kind": "product_closure",
        "artifact": "20-prd.md",
        "version": accepted_product["candidate_version"],
        "sha256": accepted_product["candidate_sha256"],
    })
    accepted_system = planning_cli(
        "advance", "--run", run, "--stage", "system_design",
        "--approval", "human", "--date", "2026-08-21",
    )
    if accepted_system.returncode != 0:
        raise AssertionError(accepted_system.stderr)
    return json.loads((run / "planning-control.json").read_text(encoding="utf-8"))


def initialize_product_planning(run: Path) -> dict:
    config = run_config()
    config["version"] = 2
    config["system_design_participation"] = "agent_led"
    config["stages"] = ["discovery", "system_design", "tickets", "execute"]
    config["gates"].pop("program_design")
    config["gates"]["system_design"] = {"authority": "HUMAN"}
    config["gates"]["tickets"] = {"authority": "HUMAN"}
    write_stage0_run(run, config)
    write_discovery(run)
    accepted = advance_discovery(run)
    initialized = planning_cli("ensure", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    return accepted


def initialize_direct_planning(run: Path) -> dict:
    write_stage0_run(run, direct_config())
    initialized = planning_cli("initialize", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    return json.loads((run / "planning-control.json").read_text(encoding="utf-8"))


def system_policy(authority: str) -> dict:
    if authority == "HUMAN_IF_CHANGED":
        return {
            "authority": authority,
            "material_dimensions": list(SYSTEM_DESIGN_DIMENSIONS),
            "otherwise": "AGENT_REVIEW",
        }
    return {"authority": authority}


def initialize_authority_planning(run: Path, authority: str, *, participation="agent_led") -> tuple[dict, dict]:
    config = direct_config(participation=participation)
    config["gates"]["system_design"] = system_policy(authority)
    write_stage0_run(run, config)
    initialized = planning_cli("initialize", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
    anchor = planning["stage0_anchor"]
    source = {
        "kind": "stage0",
        "artifact": "run.yaml",
        "sha256": anchor["base_run_sha256"],
        "effective_config_hash": anchor["effective_config_hash"],
        "effective_config_revision": anchor["effective_config_revision"],
    }
    write_system_design(run, source, participation=participation)
    return planning, source


def semantic_review(*, verdict="PASS", blocked_dimensions=()) -> dict:
    blocked = set(blocked_dimensions)
    rows = [
        {
            "dimension": dimension,
            "result": "BLOCKED" if dimension in blocked else "PASS",
            "evidence": f"Independent review evidence for {dimension}.",
        }
        for dimension in SYSTEM_DESIGN_DIMENSIONS
    ]
    gaps = [
        {
            "code": f"gap-{index}",
            "dimension": dimension,
            "problem": f"Unresolved {dimension} commitment.",
            "resume_action": f"Repair {dimension} in 30-system-design.md.",
        }
        for index, dimension in enumerate(blocked_dimensions, 1)
    ]
    return {"verdict": verdict, "dimensions": rows, "gaps": gaps}


def materiality(*, results=None, unavailable_reason=None) -> dict:
    results = results or {}
    return {
        "dimensions": [
            {
                "dimension": dimension,
                "result": results.get(dimension, "NOT_MATERIAL"),
                "evidence": f"Classification evidence for {dimension}.",
            }
            for dimension in SYSTEM_DESIGN_DIMENSIONS
        ],
        "unavailable_reason": unavailable_reason,
    }


def write_system_review(run: Path, *, policy: str, materiality, review=None) -> Path:
    config = yaml.safe_load((run / "run.yaml").read_text(encoding="utf-8"))
    path = run / "reviews" / "system-design-v1.json"
    path.parent.mkdir()
    path.write_text(json.dumps({
        "version": 1,
        "run": config["run"],
        "stage": "system_design",
        "policy": policy,
        "candidate_version": 1,
        "candidate_sha256": sha256(run / "30-system-design.md"),
        "repository_baselines": config["repos"],
        "materiality": materiality,
        "semantic_review": review,
    }, indent=2) + "\n", encoding="utf-8")
    return path


def program_semantic_review(*, results=None, source_kind="stage0", verdict=None) -> dict:
    results = results or {}
    rows = [
        {
            "dimension": dimension,
            "result": results.get(dimension, "PASS"),
            "evidence": f"Independent Stage 4 evidence for {dimension}.",
        }
        for dimension in PROGRAM_DESIGN_DIMENSIONS
    ]
    gaps = []
    for index, row in enumerate(rows, 1):
        if row["result"] == "BLOCKED":
            gaps.append({
                "code": f"program-gap-{index}",
                "dimension": row["dimension"],
                "problem": f"Local implementation defect in {row['dimension']}.",
                "resume_action": f"Repair {row['dimension']} in 40-program-design.md.",
            })
        elif row["result"] == "DESIGN_BLOCKED":
            gaps.append({
                "code": f"upstream-gap-{index}",
                "dimension": row["dimension"],
                "problem": "Accepted upstream truth cannot be realized.",
                "upstream_source": source_kind,
                "upstream_issue": "The accepted guarantee is conflicting or missing.",
                "resume_boundary": source_kind,
                "resume_action": f"Resolve the upstream issue at {source_kind}.",
            })
    derived = (
        "DESIGN_BLOCKED"
        if any(row["result"] == "DESIGN_BLOCKED" for row in rows)
        else "BLOCKED"
        if any(row["result"] == "BLOCKED" for row in rows)
        else "PASS"
    )
    return {"verdict": verdict or derived, "dimensions": rows, "gaps": gaps}


def write_program_review(run: Path, *, policy: str, review=None) -> Path:
    config = yaml.safe_load((run / "run.yaml").read_text(encoding="utf-8"))
    path = run / "reviews" / "program-design-v1.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({
        "version": 1,
        "run": config["run"],
        "stage": "program_design",
        "policy": policy,
        "candidate_version": 1,
        "candidate_sha256": sha256(run / "40-program-design.md"),
        "repository_baselines": config["repos"],
        "semantic_review": review if review is not None else program_semantic_review(),
    }, indent=2) + "\n", encoding="utf-8")
    return path


def write_upstream_block_review_input(run: Path, planning: dict, *, verdict="CONFIRMED_UPSTREAM_CONTRADICTION") -> Path:
    acceptance = planning["acceptances"]["system_design"]
    assert isinstance(acceptance, dict)
    assert isinstance(_TEST_REPOSITORY_BASELINES, list)
    source_binding = acceptance["source_bindings"][0]
    path = run / "reviews" / ".program-design-upstream-block.input.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({
        "version": 1,
        "run": planning["run"],
        "stage": "program_design",
        "planning_revision": planning["revision"],
        "verdict": verdict,
        "system_design_binding": {
            "artifact": "30-system-design.md",
            "version": acceptance["candidate_version"],
            "sha256": acceptance["candidate_sha256"],
            "source_binding": source_binding,
        },
        "repository_baselines": _TEST_REPOSITORY_BASELINES,
        "finding": {
            "code": "EXACT_CODE_CONTRADICTION",
            "dimension": "upstream_commitment_realization",
            "problem": "The accepted synchronous guarantee cannot be realized by the baseline API.",
            "upstream_source": "system_design",
            "upstream_issue": "The accepted guarantee requires a capability the baseline does not expose.",
            "resume_boundary": "system_design",
            "resume_action": "Replace the guarantee with the smallest realizable contract.",
            "code_evidence": [{
                "repository": _TEST_REPOSITORY_BASELINES[0]["repository"],
                "baseline": _TEST_REPOSITORY_BASELINES[0]["baseline"],
                "path": "source.txt",
                "evidence": "The baseline exposes no synchronous operation.",
            }],
        },
        "review_evidence": "Exact accepted design and baseline code cannot both be honored.",
    }, indent=2) + "\n", encoding="utf-8")
    return path


def initialize_program_source(run: Path, source_kind: str, *, authority="AGENT_REVIEW") -> dict:
    if source_kind == "stage0":
        planning = initialize_direct_program(run, authority=authority)
        anchor = planning["stage0_anchor"]
        source = {
            "kind": "stage0",
            "artifact": "run.yaml",
            "sha256": anchor["base_run_sha256"],
            "effective_config_hash": anchor["effective_config_hash"],
            "effective_config_revision": anchor["effective_config_revision"],
        }
    elif source_kind == "product_closure":
        accepted = initialize_product_program(run, authority=authority)
        source = {
            "kind": "product_closure",
            "artifact": "20-prd.md",
            "version": accepted["candidate_version"],
            "sha256": accepted["candidate_sha256"],
        }
    elif source_kind == "system_design":
        planning = initialize_product_system_program(run, authority=authority)
        accepted = planning["acceptances"]["system_design"]
        source = {
            "kind": "system_design",
            "artifact": "30-system-design.md",
            "version": accepted["candidate_version"],
            "sha256": accepted["candidate_sha256"],
        }
    else:
        raise AssertionError(f"unsupported test source kind: {source_kind}")
    write_program_design(run, source)
    return source


def actual_source_path(run: Path, source_kind: str) -> Path:
    return run / {
        "stage0": "run.yaml",
        "product_closure": "20-prd.md",
        "system_design": "30-system-design.md",
    }[source_kind]


class AtlasPlanningTests(unittest.TestCase):
    def setUp(self):
        global _TEST_REPOSITORY_BASELINES, _TEST_REPOSITORY_SOURCES
        self.machine_temp = tempfile.TemporaryDirectory()
        self.machine_root = Path(self.machine_temp.name).resolve()
        self.home = self.machine_root / "home"
        self.xdg_config = self.machine_root / "xdg-config"
        self.home.mkdir()
        self.xdg_config.mkdir()
        self.environment = mock.patch.dict(os.environ, {
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.xdg_config),
        })
        self.environment.start()

        fixture = self.machine_root / "fixture-repository"
        fixture_two = self.machine_root / "fixture-two-repository"
        baseline = create_repository(fixture, "fixture baseline\n")
        baseline_two = create_repository(fixture_two, "fixture two baseline\n")
        rebound = self.machine_root / "fixture-rebound.git"
        cloned = subprocess.run(
            [REAL_GIT, "clone", "-q", "--bare", str(fixture), str(rebound)],
            text=True,
            capture_output=True,
        )
        if cloned.returncode != 0:
            raise AssertionError(cloned.stderr)
        _TEST_REPOSITORY_BASELINES = [{"repository": "fixture", "baseline": baseline}]
        _TEST_REPOSITORY_SOURCES = {
            "fixture": fixture,
            "fixture-two": fixture_two,
            "fixture-rebound": rebound,
        }
        self.fixture_baseline = baseline
        self.fixture_two_baseline = baseline_two
        self.rebound_repository = rebound
        write_repository_bindings({
            "fixture": fixture,
            "fixture-two": fixture_two,
        })

    def tearDown(self):
        global _TEST_REPOSITORY_BASELINES, _TEST_REPOSITORY_SOURCES
        _TEST_REPOSITORY_BASELINES = None
        _TEST_REPOSITORY_SOURCES = {}
        self.environment.stop()
        self.machine_temp.cleanup()

    def test_program_design_check_blocks_missing_binding_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            repositories = [
                {"repository": "fixture", "baseline": self.fixture_baseline},
                {"repository": "fixture-two", "baseline": self.fixture_two_baseline},
            ]
            planning = initialize_direct_program(run, repos=repositories)
            anchor = planning["stage0_anchor"]
            source = {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            }
            write_program_design(run, source)
            before = (run / "planning-control.json").read_bytes()
            artifacts_before = {
                path.relative_to(run).as_posix(): path.read_bytes()
                for path in run.rglob("*")
                if path.is_file()
            }
            write_repository_bindings({})

            result = planning_cli("check", "--run", run, "--stage", "program_design")

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["verdict"], "BLOCKED")
            self.assertEqual(report["source_binding"], source)
            self.assertEqual(report["repository_baselines"], repositories)
            self.assertEqual(len(report["gaps"]), 2)
            self.assertEqual(
                {item["artifact"] for item in report["gaps"]},
                {"repository:fixture", "repository:fixture-two"},
            )
            self.assertTrue(all("missing_binding" in item["problem"] for item in report["gaps"]))
            self.assertEqual((run / "planning-control.json").read_bytes(), before)
            self.assertEqual({
                path.relative_to(run).as_posix(): path.read_bytes()
                for path in run.rglob("*")
                if path.is_file()
            }, artifacts_before)

    def test_program_design_acceptance_revalidates_repository_access_at_every_write_boundary(self):
        boundaries = (
            ("program_design_report", 1),
            ("resolve_program_design_authority", 1),
            ("program_design_report", 2),
            ("resolve_program_design_authority", 2),
            ("program_design_report", 3),
            ("resolve_program_design_authority", 3),
        )
        invalid_bindings = {
            "missing-binding": {"fixture-two": _TEST_REPOSITORY_SOURCES["fixture-two"]},
            "invalid-source": {"fixture": self.machine_root / "missing-repository"},
            "missing-commit": {"fixture": _TEST_REPOSITORY_SOURCES["fixture-two"]},
        }
        valid_bindings = {
            "fixture": _TEST_REPOSITORY_SOURCES["fixture"],
            "fixture-two": _TEST_REPOSITORY_SOURCES["fixture-two"],
        }
        for function_name, target_call in boundaries:
            for defect, invalid in invalid_bindings.items():
                with self.subTest(boundary=(function_name, target_call), defect=defect), tempfile.TemporaryDirectory() as td:
                    write_repository_bindings(valid_bindings)
                    run = Path(td)
                    initialize_program_source(run, "stage0")
                    write_program_review(run, policy="AGENT_REVIEW")
                    before = (run / "planning-control.json").read_bytes()
                    original = getattr(PLANNING, function_name)
                    calls = 0

                    def invalidate_only_during_boundary(*args, **kwargs):
                        nonlocal calls
                        calls += 1
                        if calls != target_call:
                            return original(*args, **kwargs)
                        write_repository_bindings(invalid)
                        try:
                            return original(*args, **kwargs)
                        finally:
                            write_repository_bindings(valid_bindings)

                    with mock.patch.object(
                        PLANNING, function_name, side_effect=invalidate_only_during_boundary
                    ):
                        with PLANNING.planning_lock(run):
                            with self.assertRaisesRegex(
                                PLANNING.ControlError,
                                "repository|binding|source|baseline|candidate|boundary",
                            ):
                                PLANNING.advance_boundary(
                                    run,
                                    "program_design",
                                    None,
                                    "reviews/program-design-v1.json",
                                    "2026-08-21",
                                )

                    self.assertGreaterEqual(calls, target_call)
                    self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_program_design_allows_rebound_source_with_same_exact_commit(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            initialize_program_source(run, "stage0")
            review = write_program_review(run, policy="AGENT_REVIEW")
            original = PLANNING.program_design_report
            calls = 0

            def rebound_after_initial_check(*args, **kwargs):
                nonlocal calls
                report = original(*args, **kwargs)
                calls += 1
                if calls == 1:
                    write_repository_bindings({
                        "fixture": self.rebound_repository,
                        "fixture-two": _TEST_REPOSITORY_SOURCES["fixture-two"],
                    })
                return report

            self.assertEqual(git(self.rebound_repository, "rev-parse", "HEAD"), self.fixture_baseline)
            with mock.patch.object(
                PLANNING, "program_design_report", side_effect=rebound_after_initial_check
            ):
                with PLANNING.planning_lock(run):
                    PLANNING.advance_boundary(
                        run,
                        "program_design",
                        None,
                        "reviews/program-design-v1.json",
                        "2026-08-21",
                    )

            record = PLANNING.load_planning_control(run)["acceptances"]["program_design"]
            self.assertEqual(record["repository_baselines"], _TEST_REPOSITORY_BASELINES)
            self.assertEqual(record["review_sha256"], sha256(review))
            self.assertNotIn(str(self.rebound_repository), json.dumps(record))

    def test_existing_program_design_acceptance_requires_exact_repository_baselines(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            initialize_program_source(run, "stage0")
            write_program_review(run, policy="AGENT_REVIEW")
            accepted = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            planning_path = run / "planning-control.json"
            state = json.loads(planning_path.read_text(encoding="utf-8"))
            self.assertEqual(
                state["acceptances"]["program_design"]["repository_baselines"],
                _TEST_REPOSITORY_BASELINES,
            )

            state["acceptances"]["program_design"]["repository_baselines"] = []
            planning_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            before = planning_path.read_bytes()

            with self.assertRaisesRegex(PLANNING.ControlError, "Program Design acceptance.*malformed"):
                PLANNING.load_planning_control(run)
            self.assertEqual(planning_path.read_bytes(), before)

    def test_program_design_without_selected_tickets_fails_loudly_before_transition(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            config["version"] = 2
            config["system_design_participation"] = None
            config["stages"] = ["program_design"]
            config["gates"] = {"program_design": {"authority": "AGENT_REVIEW"}}
            config["recommendation"]["gates"] = config["gates"]
            write_stage0_run(run, config)
            initialized = planning_cli("initialize", "--run", run)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
            anchor = planning["stage0_anchor"]
            write_program_design(run, {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            })
            write_program_review(run, policy="AGENT_REVIEW")
            before = (run / "planning-control.json").read_bytes()

            result = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tickets", result.stderr)
            self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_program_design_acceptance_advances_once_to_tickets_without_launching_tickets(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_direct_program(run)
            anchor = planning["stage0_anchor"]
            write_program_design(run, {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            })
            write_program_review(run, policy="AGENT_REVIEW")
            control_before = (run / "control.json").read_bytes()
            files_before = {path.relative_to(run).as_posix() for path in run.rglob("*") if path.is_file()}

            result = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("advanced program_design -> tickets", result.stdout)
            updated = PLANNING.load_planning_control(run)
            self.assertEqual((updated["phase"], updated["revision"]), ("tickets", 2))
            self.assertEqual((run / "control.json").read_bytes(), control_before)
            self.assertEqual(
                {path.relative_to(run).as_posix() for path in run.rglob("*") if path.is_file()},
                files_before,
            )
            for forbidden in ("50-tickets.json", "tickets", "ticket-graph.json"):
                self.assertFalse((run / forbidden).exists())

            before_repeat = (run / "planning-control.json").read_bytes()
            repeated = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
            )
            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual((run / "planning-control.json").read_bytes(), before_repeat)

    def test_accepted_program_design_revalidates_all_currency_across_source_paths(self):
        for source_kind in ("stage0", "product_closure", "system_design"):
            for mutation in (
                "candidate", "source", "review", "repository-baselines", "repository-access",
            ):
                with self.subTest(source_kind=source_kind, mutation=mutation), tempfile.TemporaryDirectory() as td:
                    write_repository_bindings({
                        "fixture": _TEST_REPOSITORY_SOURCES["fixture"],
                        "fixture-two": _TEST_REPOSITORY_SOURCES["fixture-two"],
                    })
                    run = Path(td)
                    initialize_program_source(run, source_kind)
                    review = write_program_review(run, policy="AGENT_REVIEW")
                    accepted = planning_cli(
                        "advance", "--run", run, "--stage", "program_design",
                        "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
                    )
                    self.assertEqual(accepted.returncode, 0, accepted.stderr)
                    PLANNING.load_planning_control(run)

                    if mutation == "candidate":
                        target = run / "40-program-design.md"
                        target.write_bytes(target.read_bytes() + b"\nchanged accepted candidate\n")
                        expected = "candidate"
                    elif mutation == "source":
                        target = actual_source_path(run, source_kind)
                        marker = (
                            b"\n# changed accepted source\n"
                            if source_kind == "stage0"
                            else b"\nchanged accepted source\n"
                        )
                        target.write_bytes(target.read_bytes() + marker)
                        expected = "source|provenance|Stage 0|System Design|product"
                    elif mutation == "review":
                        review.write_bytes(review.read_bytes() + b" \n")
                        expected = "review|evidence"
                    elif mutation == "repository-baselines":
                        envelope = json.loads(review.read_text(encoding="utf-8"))
                        envelope["repository_baselines"] = [{
                            "repository": "fixture", "baseline": "changed-baseline",
                        }]
                        review.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
                        planning_path = run / "planning-control.json"
                        state = json.loads(planning_path.read_text(encoding="utf-8"))
                        state["acceptances"]["program_design"]["review_sha256"] = sha256(review)
                        planning_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
                        expected = "baselines"
                    else:
                        write_repository_bindings({
                            "fixture-two": _TEST_REPOSITORY_SOURCES["fixture-two"]
                        })
                        expected = "repository|binding"
                    planning_before_refusal = (run / "planning-control.json").read_bytes()

                    with self.assertRaisesRegex(PLANNING.ControlError, expected):
                        PLANNING.load_planning_control(run)
                    self.assertEqual(
                        (run / "planning-control.json").read_bytes(), planning_before_refusal
                    )

    def test_program_design_final_write_revalidates_all_currency_across_source_paths(self):
        for source_kind in ("stage0", "product_closure", "system_design"):
            for mutation in ("candidate", "source", "review", "effective-repositories"):
                with self.subTest(source_kind=source_kind, mutation=mutation), tempfile.TemporaryDirectory() as td:
                    run = Path(td)
                    initialize_program_source(run, source_kind)
                    review = write_program_review(run, policy="AGENT_REVIEW")
                    before = (run / "planning-control.json").read_bytes()
                    original_write = PLANNING.write_planning_control_atomic

                    def mutate_at_write_boundary(*args, **kwargs):
                        if mutation == "candidate":
                            target = run / "40-program-design.md"
                            target.write_bytes(target.read_bytes() + b"\nwrite-boundary candidate drift\n")
                        elif mutation == "source":
                            target = actual_source_path(run, source_kind)
                            marker = (
                                b"\n# write-boundary source drift\n"
                                if source_kind == "stage0"
                                else b"\nwrite-boundary source drift\n"
                            )
                            target.write_bytes(target.read_bytes() + marker)
                        elif mutation == "review":
                            review.write_bytes(review.read_bytes() + b" \n")
                        else:
                            config = yaml.safe_load((run / "run.yaml").read_text(encoding="utf-8"))
                            config["repos"] = [{
                                "repository": "fixture", "baseline": "write-boundary-baseline",
                            }]
                            (run / "run.yaml").write_text(
                                yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
                            )
                        return original_write(*args, **kwargs)

                    with mock.patch.object(
                        PLANNING,
                        "write_planning_control_atomic",
                        side_effect=mutate_at_write_boundary,
                    ):
                        with PLANNING.planning_lock(run):
                            with self.assertRaisesRegex(
                                PLANNING.ControlError,
                                "candidate|source|review|policy|provenance|boundary|baseline|Stage 0|base run.yaml",
                            ):
                                PLANNING.advance_boundary(
                                    run,
                                    "program_design",
                                    None,
                                    "reviews/program-design-v1.json",
                                    "2026-08-21",
                                )

                    self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_program_design_upstream_guarantee_objection_is_design_blocked_not_stage4_blocked(self):
        local_dimension = "migration_and_local_failure_path_implementation"
        semantic = program_semantic_review(
            results={
                "upstream_commitment_realization": "DESIGN_BLOCKED",
                local_dimension: "BLOCKED",
            },
            source_kind="system_design",
        )

        PLANNING.validate_program_design_semantic_review(semantic, "system_design")
        self.assertEqual(semantic["verdict"], "DESIGN_BLOCKED")
        gaps = {gap["dimension"]: gap for gap in semantic["gaps"]}
        self.assertEqual(set(gaps["upstream_commitment_realization"]), {
            "code", "dimension", "problem", "upstream_source", "upstream_issue",
            "resume_boundary", "resume_action",
        })
        self.assertEqual(set(gaps[local_dimension]), {
            "code", "dimension", "problem", "resume_action",
        })

        misrouted = program_semantic_review(
            results={local_dimension: "DESIGN_BLOCKED"},
            source_kind="system_design",
        )
        with self.assertRaisesRegex(PLANNING.ControlError, "upstream_commitment_realization"):
            PLANNING.validate_program_design_semantic_review(misrouted, "system_design")

    def test_program_design_rejects_each_wrong_actual_source_boundary_field(self):
        source_kinds = ("system_design", "product_closure", "stage0")
        for source_kind in source_kinds:
            for field in ("upstream_source", "resume_boundary"):
                with self.subTest(source_kind=source_kind, field=field), tempfile.TemporaryDirectory() as td:
                    run = Path(td)
                    initialize_program_source(run, source_kind)
                    semantic = program_semantic_review(
                        results={"upstream_commitment_realization": "DESIGN_BLOCKED"},
                        source_kind=source_kind,
                    )
                    wrong_boundary = next(kind for kind in source_kinds if kind != source_kind)
                    semantic["gaps"][0][field] = wrong_boundary
                    write_program_review(
                        run, policy="AGENT_REVIEW", review=semantic
                    )
                    before = (run / "planning-control.json").read_bytes()

                    result = planning_cli(
                        "advance", "--run", run, "--stage", "program_design",
                        "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
                    )

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("actual source boundary", result.stderr)
                    self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_program_design_verdict_must_be_derived_from_dimension_rows(self):
        cases = (
            (program_semantic_review(verdict="BLOCKED"), "stage0"),
            (
                program_semantic_review(
                    results={"files_packages_types_and_responsibilities": "BLOCKED"},
                    verdict="PASS",
                ),
                "stage0",
            ),
            (
                program_semantic_review(
                    results={
                        "upstream_commitment_realization": "DESIGN_BLOCKED",
                        "testability_and_compilation_readiness": "BLOCKED",
                    },
                    source_kind="stage0",
                    verdict="BLOCKED",
                ),
                "stage0",
            ),
        )
        for semantic, source_kind in cases:
            with self.subTest(verdict=semantic["verdict"]):
                with self.assertRaisesRegex(PLANNING.ControlError, "derived"):
                    PLANNING.validate_program_design_semantic_review(semantic, source_kind)

    def test_program_design_design_blocked_requires_exact_upstream_issue_and_resume_boundary(self):
        semantic = program_semantic_review(
            results={"upstream_commitment_realization": "DESIGN_BLOCKED"},
            source_kind="stage0",
        )
        PLANNING.validate_program_design_semantic_review(semantic, "stage0")

        for mutation in ("missing-issue", "empty-issue", "missing-resume", "extra-field"):
            with self.subTest(mutation=mutation):
                malformed = json.loads(json.dumps(semantic))
                gap = malformed["gaps"][0]
                if mutation == "missing-issue":
                    gap.pop("upstream_issue")
                elif mutation == "empty-issue":
                    gap["upstream_issue"] = "  "
                elif mutation == "missing-resume":
                    gap.pop("resume_boundary")
                else:
                    gap["omitted_boundary"] = "system_design"

                with self.assertRaises(PLANNING.ControlError):
                    PLANNING.validate_program_design_semantic_review(malformed, "stage0")

    def test_program_design_blocked_verdicts_never_advance_or_mutate_state(self):
        cases = (
            ("BLOCKED", "files_packages_types_and_responsibilities"),
            ("DESIGN_BLOCKED", "upstream_commitment_realization"),
        )
        for authority, approval in (("AGENT_REVIEW", ()), ("HUMAN", ("--approval", "human"))):
            for verdict, blocked_dimension in cases:
                with self.subTest(authority=authority, verdict=verdict), tempfile.TemporaryDirectory() as td:
                    run = Path(td)
                    source = initialize_program_source(run, "stage0", authority=authority)
                    write_program_review(
                        run,
                        policy=authority,
                        review=program_semantic_review(
                            results={blocked_dimension: verdict}, source_kind=source["kind"]
                        ),
                    )
                    before = (run / "planning-control.json").read_bytes()

                    result = planning_cli(
                        "advance", "--run", run, "--stage", "program_design",
                        "--review", "reviews/program-design-v1.json", *approval,
                        "--date", "2026-08-21",
                    )

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        f"Program Design semantic review is {verdict}", result.stderr
                    )
                    self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_valid_program_design_review_ingestion_advances(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            initialize_program_source(run, "stage0")
            review = write_program_review(run, policy="AGENT_REVIEW")

            result = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state = PLANNING.load_planning_control(run)
            self.assertEqual((state["phase"], state["revision"]), ("tickets", 2))
            self.assertEqual(
                state["acceptances"]["program_design"]["review_sha256"], sha256(review)
            )

    def test_program_design_review_rejects_wrong_paths_symlink_encoding_and_duplicate_json(self):
        for mutation, expected in (
            ("wrong-reference", "must use exact reviews/program-design-v1.json"),
            ("escaping-reference", "must use exact reviews/program-design-v1.json"),
            ("symlink", "managed path uses a symlink"),
            ("invalid-utf8", "not valid UTF-8"),
            ("duplicate-json-key", "duplicate JSON key: version"),
        ):
            with (
                self.subTest(mutation=mutation),
                tempfile.TemporaryDirectory() as td,
                tempfile.TemporaryDirectory() as outside_td,
            ):
                run = Path(td)
                initialize_program_source(run, "stage0")
                review = write_program_review(run, policy="AGENT_REVIEW")
                review_reference = "reviews/program-design-v1.json"
                if mutation == "wrong-reference":
                    wrong = review.with_name("program-design-v2.json")
                    review.replace(wrong)
                    review_reference = "reviews/program-design-v2.json"
                elif mutation == "escaping-reference":
                    review_reference = "../program-design-v1.json"
                elif mutation == "symlink":
                    outside = Path(outside_td) / "program-review.json"
                    outside.write_bytes(review.read_bytes())
                    review.unlink()
                    review.symlink_to(outside)
                elif mutation == "invalid-utf8":
                    review.write_bytes(b'{"version": 1, "invalid": "\xff"}')
                elif mutation == "duplicate-json-key":
                    review.write_text(
                        review.read_text(encoding="utf-8").replace(
                            '  "version": 1,', '  "version": 1,\n  "version": 1,', 1
                        ),
                        encoding="utf-8",
                    )
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "program_design",
                    "--review", review_reference, "--date", "2026-08-21",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_program_design_review_requires_exact_top_level_schema(self):
        base_fields = (
            "version", "run", "stage", "policy", "candidate_version", "candidate_sha256",
            "repository_baselines", "semantic_review",
        )
        mutations = tuple((f"missing-{field}", field) for field in base_fields) + (
            ("extra-field", None),
            ("forbidden-materiality", None),
        )
        for mutation, missing in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                initialize_program_source(run, "stage0")
                review = write_program_review(run, policy="AGENT_REVIEW")
                envelope = json.loads(review.read_text(encoding="utf-8"))
                if missing is not None:
                    envelope.pop(missing)
                elif mutation == "forbidden-materiality":
                    envelope["materiality"] = None
                else:
                    envelope["unexpected"] = "field"
                review.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "program_design",
                    "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "Program Design review envelope does not match its exact schema",
                    result.stderr,
                )
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_program_design_review_rejects_each_wrong_current_binding(self):
        repos = [
            {"repository": "fixture", "baseline": self.fixture_baseline},
            {"repository": "fixture-two", "baseline": self.fixture_two_baseline},
        ]
        mutations = {
            "run": lambda envelope: envelope.__setitem__("run", "other-run"),
            "stage": lambda envelope: envelope.__setitem__("stage", "system_design"),
            "policy": lambda envelope: envelope.__setitem__("policy", "HUMAN"),
            "version": lambda envelope: envelope.__setitem__("version", 2),
            "bool-version": lambda envelope: envelope.__setitem__("version", True),
            "candidate-version": lambda envelope: envelope.__setitem__("candidate_version", 2),
            "bool-candidate-version": lambda envelope: envelope.__setitem__("candidate_version", True),
            "candidate-hash": lambda envelope: envelope.__setitem__("candidate_sha256", "0" * 64),
            "repository-order": lambda envelope: envelope.__setitem__(
                "repository_baselines", list(reversed(envelope["repository_baselines"]))
            ),
            "repository-contents": lambda envelope: envelope["repository_baselines"][0].__setitem__(
                "baseline", "fffffff"
            ),
        }
        for mutation, mutate in mutations.items():
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_direct_program(run, repos=repos)
                anchor = planning["stage0_anchor"]
                write_program_design(run, {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": anchor["base_run_sha256"],
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                })
                review = write_program_review(run, policy="AGENT_REVIEW")
                envelope = json.loads(review.read_text(encoding="utf-8"))
                mutate(envelope)
                review.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "program_design",
                    "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "Program Design review evidence does not match current policy, candidate, or baselines",
                    result.stderr,
                )
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_program_design_review_rejects_null_non_dict_and_malformed_semantic_review(self):
        cases = {
            "null": None,
            "non-dict": [],
            "unknown-field": {
                **program_semantic_review(),
                "reviewer_notes": "extra semantic-review fields are forbidden",
            },
            "malformed": {"verdict": "PASS", "dimensions": None, "gaps": []},
        }
        for mutation, semantic in cases.items():
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                initialize_program_source(run, "stage0")
                review = write_program_review(run, policy="AGENT_REVIEW")
                envelope = json.loads(review.read_text(encoding="utf-8"))
                envelope["semantic_review"] = semantic
                review.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "program_design",
                    "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Program Design semantic_review", result.stderr)
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_program_design_review_uses_exact_seven_stage4_dimensions(self):
        mutations = ("missing", "duplicate", "unknown", "extra-field", "bad-result", "empty-evidence")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_direct_program(run)
                anchor = planning["stage0_anchor"]
                write_program_design(run, {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": anchor["base_run_sha256"],
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                })
                semantic = program_semantic_review()
                rows = semantic["dimensions"]
                if mutation == "missing":
                    rows.pop()
                elif mutation == "duplicate":
                    rows[-1] = dict(rows[0])
                elif mutation == "unknown":
                    rows[-1]["dimension"] = "stage3_materiality"
                elif mutation == "extra-field":
                    rows[-1]["confidence"] = "high"
                elif mutation == "bad-result":
                    rows[-1]["result"] = "MATERIAL"
                else:
                    rows[-1]["evidence"] = ""
                write_program_review(run, policy="AGENT_REVIEW", review=semantic)
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "program_design",
                    "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
                )

                self.assertNotEqual(result.returncode, 0, mutation)
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

        reordered = program_semantic_review()
        reordered["dimensions"][0], reordered["dimensions"][1] = (
            reordered["dimensions"][1], reordered["dimensions"][0]
        )
        PLANNING.validate_program_design_semantic_review(reordered, "stage0")

    def test_human_program_design_requires_fresh_pass_review_plus_explicit_approval(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_direct_program(run, authority="HUMAN")
            anchor = planning["stage0_anchor"]
            source = {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            }
            write_program_design(run, source)
            before = (run / "planning-control.json").read_bytes()

            bypass = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--approval", "human", "--date", "2026-08-21",
            )
            self.assertNotEqual(bypass.returncode, 0)
            self.assertEqual((run / "planning-control.json").read_bytes(), before)

            review = write_program_review(run, policy="HUMAN")
            no_approval = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
            )
            self.assertNotEqual(no_approval.returncode, 0)
            self.assertEqual((run / "planning-control.json").read_bytes(), before)

            accepted = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--review", "reviews/program-design-v1.json", "--approval", "human",
                "--date", "2026-08-21",
            )

            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            updated = PLANNING.load_planning_control(run)
            self.assertEqual(updated["gates"]["program_design"], "HUMAN_APPROVED")
            record = updated["acceptances"]["program_design"]
            self.assertEqual(record["authority"], "HUMAN")
            self.assertEqual(record["review_reference"], "reviews/program-design-v1.json")
            self.assertEqual(record["review_sha256"], sha256(review))

    def test_program_design_acceptance_records_effective_repository_baselines(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as caller_td:
            run = Path(td)
            planning = initialize_direct_program(run)
            anchor = planning["stage0_anchor"]
            source = {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            }
            write_program_design(run, source)
            review = write_program_review(run, policy="AGENT_REVIEW")

            result = planning_cli(
                "advance", "--run", run, "--stage", "program_design",
                "--review", "reviews/program-design-v1.json", "--date", "2026-08-21",
                cwd=caller_td,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            updated = PLANNING.load_planning_control(run)
            self.assertEqual((updated["phase"], updated["revision"]), ("tickets", 2))
            self.assertEqual(updated["gates"]["program_design"], "AGENT_APPROVED")
            self.assertEqual(updated["acceptances"]["program_design"], {
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "40-program-design.md"),
                "authority": "AGENT_REVIEW",
                "accepted": "2026-08-21",
                "review_reference": "reviews/program-design-v1.json",
                "review_sha256": sha256(review),
                "source_bindings": [source],
                "repository_baselines": _TEST_REPOSITORY_BASELINES,
            })

    def test_direct_agent_review_pass_records_exact_evidence_acceptance(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as caller_td:
            run = Path(td)
            _, source = initialize_authority_planning(run, "AGENT_REVIEW")
            review = write_system_review(
                run,
                policy="AGENT_REVIEW",
                materiality=None,
                review=semantic_review(),
            )

            result = planning_cli(
                "advance", "--run", run, "--stage", "system_design",
                "--review", "reviews/system-design-v1.json", "--date", "2026-08-21",
                cwd=caller_td,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            updated = PLANNING.load_planning_control(run)
            self.assertEqual(updated["gates"]["system_design"], "AGENT_APPROVED")
            self.assertEqual(updated["phase"], "tickets")
            self.assertEqual(updated["acceptances"]["system_design"], {
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "30-system-design.md"),
                "authority": "AGENT_REVIEW",
                "accepted": "2026-08-21",
                "review_reference": "reviews/system-design-v1.json",
                "review_sha256": sha256(review),
                "source_bindings": [source],
                "repository_baselines": [],
            })
            planning_path = run / "planning-control.json"
            before_resume = planning_path.read_bytes()

            resumed = planning_cli("ensure", "--run", run, cwd=caller_td)

            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertEqual(
                resumed.stdout.strip(),
                "planning-control.json already initialized at tickets; revision 2",
            )
            self.assertEqual(planning_path.read_bytes(), before_resume)

    def test_accepted_loader_rejects_gate_label_authority_mismatch(self):
        cases = (
            ("AGENT_REVIEW", None, semantic_review(), None, "HUMAN_APPROVED"),
            (
                "HUMAN_IF_CHANGED",
                materiality(results={SYSTEM_DESIGN_DIMENSIONS[0]: "MATERIAL"}),
                None,
                "human",
                "AGENT_APPROVED",
            ),
        )
        for policy, materiality_value, review_value, approval, wrong_gate in cases:
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                initialize_authority_planning(run, policy)
                write_system_review(
                    run,
                    policy=policy,
                    materiality=materiality_value,
                    review=review_value,
                )
                args = [
                    "advance", "--run", run, "--stage", "system_design",
                    "--review", "reviews/system-design-v1.json",
                    "--date", "2026-08-21",
                ]
                if approval is not None:
                    args.extend(("--approval", approval))
                accepted = planning_cli(*args)
                self.assertEqual(accepted.returncode, 0, accepted.stderr)
                planning_path = run / "planning-control.json"
                state = json.loads(planning_path.read_text(encoding="utf-8"))
                state["gates"]["system_design"] = wrong_gate
                planning_path.write_text(json.dumps(state), encoding="utf-8")

                with self.assertRaisesRegex(PLANNING.ControlError, "gate.*authority"):
                    PLANNING.load_planning_control(run)

    def test_direct_agent_review_rejects_materiality_classification(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            initialize_authority_planning(run, "AGENT_REVIEW")
            write_system_review(
                run,
                policy="AGENT_REVIEW",
                materiality=materiality(),
                review=semantic_review(),
            )
            before = (run / "planning-control.json").read_bytes()

            result = planning_cli(
                "advance", "--run", run, "--stage", "system_design",
                "--review", "reviews/system-design-v1.json", "--date", "2026-08-21",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("null materiality", result.stderr)
            self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_human_if_changed_all_clear_maps_to_agent_review(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            initialize_authority_planning(run, "HUMAN_IF_CHANGED")
            write_system_review(
                run,
                policy="HUMAN_IF_CHANGED",
                materiality=materiality(),
                review=semantic_review(),
            )

            result = planning_cli(
                "advance", "--run", run, "--stage", "system_design",
                "--review", "reviews/system-design-v1.json", "--date", "2026-08-21",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            record = PLANNING.load_planning_control(run)["acceptances"]["system_design"]
            self.assertEqual(record["authority"], "AGENT_REVIEW")
            self.assertEqual(record["review_reference"], "reviews/system-design-v1.json")
            self.assertRegex(record["review_sha256"], r"^[0-9a-f]{64}$")

    def test_human_if_changed_material_dimension_requires_review_and_explicit_human(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            initialize_authority_planning(run, "HUMAN_IF_CHANGED")
            review = write_system_review(
                run,
                policy="HUMAN_IF_CHANGED",
                materiality=materiality(results={SYSTEM_DESIGN_DIMENSIONS[0]: "MATERIAL"}),
                review=None,
            )

            result = planning_cli(
                "advance", "--run", run, "--stage", "system_design",
                "--review", "reviews/system-design-v1.json", "--approval", "human",
                "--date", "2026-08-21",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            updated = PLANNING.load_planning_control(run)
            self.assertEqual(updated["gates"]["system_design"], "HUMAN_APPROVED")
            record = updated["acceptances"]["system_design"]
            self.assertEqual(record["authority"], "HUMAN")
            self.assertEqual(record["review_reference"], "reviews/system-design-v1.json")
            self.assertEqual(record["review_sha256"], sha256(review))

    def test_human_if_changed_explained_classifier_failures_route_human(self):
        mutations = {
            "unavailable": lambda rows: [],
            "missing": lambda rows: rows[:-1],
            "duplicate": lambda rows: rows[:-1] + [dict(rows[0])],
            "unknown": lambda rows: rows[:-1] + [{
                "dimension": "unknown_dimension", "result": "NOT_MATERIAL", "evidence": "Unknown output.",
            }],
            "malformed": lambda rows: rows[:-1] + [{
                "dimension": SYSTEM_DESIGN_DIMENSIONS[-1], "result": "NOT_MATERIAL",
            }],
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                initialize_authority_planning(run, "HUMAN_IF_CHANGED")
                evidence = materiality(unavailable_reason=f"Classifier {name} prevented complete classification.")
                evidence["dimensions"] = mutate(evidence["dimensions"])
                write_system_review(
                    run,
                    policy="HUMAN_IF_CHANGED",
                    materiality=evidence,
                    review=None,
                )

                result = planning_cli(
                    "advance", "--run", run, "--stage", "system_design",
                    "--review", "reviews/system-design-v1.json", "--approval", "human",
                    "--date", "2026-08-21",
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                record = PLANNING.load_planning_control(run)["acceptances"]["system_design"]
                self.assertEqual(record["authority"], "HUMAN")

    def test_human_if_changed_requires_canonical_policy_and_rejects_unexplained_bad_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = direct_config()
            config["gates"]["system_design"] = {
                "authority": "HUMAN_IF_CHANGED",
                "material_dimensions": ["system seams"],
                "otherwise": "AGENT_REVIEW",
            }
            write_stage0_run(run, config)

            initialized = planning_cli("initialize", "--run", run)

            self.assertNotEqual(initialized.returncode, 0)
            self.assertIn("exact", initialized.stderr.lower())
            self.assertFalse((run / "planning-control.json").exists())

        for reason in (None, ""):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                initialize_authority_planning(run, "HUMAN_IF_CHANGED")
                evidence = materiality(unavailable_reason=reason)
                evidence["dimensions"] = evidence["dimensions"][:-1]
                write_system_review(
                    run, policy="HUMAN_IF_CHANGED", materiality=evidence, review=None
                )
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "system_design",
                    "--review", "reviews/system-design-v1.json", "--approval", "human",
                    "--date", "2026-08-21",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_system_design_review_uses_effective_repos_after_accepted_intake_amendment(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            config["version"] = 2
            config["system_design_participation"] = "agent_led"
            config["stages"] = ["discovery", "system_design", "tickets", "execute"]
            config["gates"].pop("program_design")
            config["gates"]["system_design"] = {"authority": "AGENT_REVIEW"}
            config["gates"]["tickets"] = {"authority": "HUMAN"}
            write_stage0_run(run, config)
            write_discovery(run, ready=False, stale=True)
            marked = run_cli("mark-stale", "--run", run, "--reason", "baseline corrected")
            self.assertEqual(marked.returncode, 0, marked.stderr)
            corrected_repos = [{"repository": "fixture", "baseline": "def4567"}]
            amendments = run / "amendments"
            amendments.mkdir()
            write_markdown(amendments / "001-repository-baseline.md", {
                "version": 1,
                "amendment": 1,
                "applies_to": "run.yaml",
                "status": "accepted",
                "accepted": "2026-08-20",
                "reason": "Discovery proved the original baseline was wrong",
                "changes": {"repos": corrected_repos},
            }, "# Repository baseline correction\n")
            amended = run_cli("apply-amendment", "--run", run)
            self.assertEqual(amended.returncode, 0, amended.stderr)
            write_discovery(run, revision=1)
            accepted = advance_discovery(run)
            ensured = planning_cli("ensure", "--run", run)
            self.assertEqual(ensured.returncode, 0, ensured.stderr)
            planning = PLANNING.load_planning_control(run)
            self.assertEqual(planning["phase"], "system_design")
            write_system_design(run, {
                "kind": "product_closure",
                "artifact": "20-prd.md",
                "version": accepted["candidate_version"],
                "sha256": accepted["candidate_sha256"],
            })
            review = write_system_review(
                run, policy="AGENT_REVIEW", materiality=None, review=semantic_review()
            )
            _, effective = PLANNING.verified_state(run)

            with self.assertRaisesRegex(PLANNING.ControlError, "baselines"):
                PLANNING.load_system_design_review(
                    run, effective, 1, sha256(run / "30-system-design.md"),
                    "reviews/system-design-v1.json",
                )

            envelope = json.loads(review.read_text(encoding="utf-8"))
            envelope["repository_baselines"] = corrected_repos
            review.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
            _, review_hash, mapped = PLANNING.load_system_design_review(
                run, effective, 1, sha256(run / "30-system-design.md"),
                "reviews/system-design-v1.json",
            )

            self.assertEqual(review_hash, sha256(review))
            self.assertEqual(mapped, "AGENT_REVIEW")

    def test_downstream_initialize_rejects_legacy_system_design_run_without_participation(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            write_stage0_run(run, direct_config(version=1))

            result = planning_cli("initialize", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("participation", result.stderr.lower())
            self.assertFalse((run / "planning-control.json").exists())

    def test_initialize_planning_materializes_selected_and_not_required_boundaries(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as caller_td:
            run = Path(td)
            write_stage0_run(run, direct_config())
            control_before = (run / "control.json").read_bytes()
            stage0 = read_control(run)

            result = planning_cli("initialize", "--run", run, cwd=caller_td)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((run / "control.json").read_bytes(), control_before)
            planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
            self.assertEqual(set(planning), {
                "version", "run", "status", "phase", "revision", "stage0_anchor",
                "gates", "acceptances", "blocked_reason",
            })
            self.assertEqual(
                (planning["version"], planning["run"], planning["status"], planning["phase"], planning["revision"]),
                (1, "demo", "PLANNING", "system_design", 1),
            )
            self.assertEqual(planning["gates"], {
                "system_design": "PENDING",
                "program_design": "NOT_REQUIRED",
                "tickets": "PENDING",
            })
            self.assertEqual(planning["acceptances"], {
                "system_design": None,
                "program_design": None,
                "tickets": None,
            })
            self.assertEqual(planning["blocked_reason"], None)
            self.assertEqual(planning["stage0_anchor"], {
                "control_sha256": sha256(run / "control.json"),
                "control_revision": stage0["revision"],
                "base_run_sha256": stage0["base_run_sha256"],
                "effective_config_hash": stage0["effective_config_hash"],
                "effective_config_revision": stage0["effective_config_revision"],
                "product_closure": None,
            })
            self.assertTrue((run / ".atlas-planning.lock").is_file())
            self.assertFalse((run / "approved").exists())
            self.assertFalse((run / "history.json").exists())
            self.assertFalse((run / "journal.json").exists())

    def test_ensure_planning_after_product_closure_is_idempotent_and_exact(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as caller_td:
            run = Path(td)
            config = run_config()
            config["version"] = 2
            config["system_design_participation"] = "agent_led"
            config["stages"] = ["discovery", "system_design", "tickets", "execute"]
            config["gates"].pop("program_design")
            config["gates"]["system_design"] = {"authority": "HUMAN"}
            config["gates"]["tickets"] = {"authority": "HUMAN"}
            write_stage0_run(run, config)
            write_discovery(run)
            accepted = advance_discovery(run)

            first = planning_cli("ensure", "--run", run, cwd=caller_td)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout.strip(), "initialized planning-control.json revision 1")
            planning_path = run / "planning-control.json"
            planning = json.loads(planning_path.read_text(encoding="utf-8"))
            self.assertEqual(planning["phase"], "system_design")
            self.assertEqual(planning["stage0_anchor"]["product_closure"], {
                "version": accepted["candidate_version"],
                "sha256": accepted["candidate_sha256"],
            })
            before = planning_path.read_bytes()

            second = planning_cli("ensure", "--run", run, cwd=caller_td)

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(
                second.stdout.strip(),
                "planning-control.json already initialized at system_design; revision 1",
            )
            self.assertEqual(planning_path.read_bytes(), before)

            strict = planning_cli("initialize", "--run", run, cwd=caller_td)
            self.assertNotEqual(strict.returncode, 0)
            self.assertIn("already exists", strict.stderr)
            self.assertEqual(planning_path.read_bytes(), before)

            malformed = json.loads(before)
            malformed["phase"] = "tickets"
            planning_path.write_text(json.dumps(malformed), encoding="utf-8")
            malformed_before = planning_path.read_bytes()
            rejected = planning_cli("ensure", "--run", run, cwd=caller_td)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(planning_path.read_bytes(), malformed_before)

    def test_ensure_rejects_existing_state_that_bypasses_initialization_order(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = direct_config()
            config["stages"] = ["tickets", "system_design", "execute"]
            write_stage0_run(run, config)
            control, effective = PLANNING.verified_state(run)
            planning = {
                "version": 1,
                "run": effective["run"],
                "status": "PLANNING",
                "phase": "system_design",
                "revision": 1,
                "stage0_anchor": PLANNING.current_stage0_anchor(run, control, effective),
                "gates": {
                    "system_design": "PENDING",
                    "program_design": "NOT_REQUIRED",
                    "tickets": "PENDING",
                },
                "acceptances": {
                    "system_design": None,
                    "program_design": None,
                    "tickets": None,
                },
                "blocked_reason": None,
            }
            planning_path = run / "planning-control.json"
            planning_path.write_text(json.dumps(planning, indent=2) + "\n", encoding="utf-8")
            before = planning_path.read_bytes()

            result = planning_cli("ensure", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("order", result.stderr.lower())
            self.assertEqual(planning_path.read_bytes(), before)

    def test_ensure_rejects_existing_state_that_bypasses_policy_validation(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = direct_config()
            config["gates"]["system_design"] = {
                "authority": "HUMAN_IF_CHANGED",
                "material_dimensions": ["stale_slice_one_dimension"],
                "otherwise": "AGENT_REVIEW",
            }
            write_stage0_run(run, config)
            control, effective = PLANNING.verified_state(run)
            planning = {
                "version": 1,
                "run": effective["run"],
                "status": "PLANNING",
                "phase": "system_design",
                "revision": 1,
                "stage0_anchor": PLANNING.current_stage0_anchor(run, control, effective),
                "gates": {
                    "system_design": "PENDING",
                    "program_design": "NOT_REQUIRED",
                    "tickets": "PENDING",
                },
                "acceptances": {
                    "system_design": None,
                    "program_design": None,
                    "tickets": None,
                },
                "blocked_reason": None,
            }
            planning_path = run / "planning-control.json"
            planning_path.write_text(json.dumps(planning, indent=2) + "\n", encoding="utf-8")
            before = planning_path.read_bytes()

            result = planning_cli("ensure", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exact seven", result.stderr.lower())
            self.assertEqual(planning_path.read_bytes(), before)

    def test_downstream_initialize_rejects_missing_or_malformed_selected_stage_gate_policy(self):
        cases = {
            "missing tickets": (None, None),
            "system AUTO": ("system_design", {"authority": "AUTO"}),
            "system HUMAN_IF_CHANGED missing dimensions": (
                "system_design", {"authority": "HUMAN_IF_CHANGED", "material_dimensions": [], "otherwise": "AGENT_REVIEW"}
            ),
            "system HUMAN_IF_CHANGED wrong otherwise": (
                "system_design", {"authority": "HUMAN_IF_CHANGED", "material_dimensions": ["seams"], "otherwise": "HUMAN"}
            ),
            "program AUTO": ("program_design", {"authority": "AUTO"}),
            "program CONDITIONAL": (
                "program_design", {"authority": "CONDITIONAL", "conditions": [{"when": "changed", "then": "HUMAN"}], "otherwise": "AGENT_REVIEW"}
            ),
            "tickets AUTO": ("tickets", {"authority": "AUTO"}),
            "tickets CONDITIONAL missing conditions": (
                "tickets", {"authority": "CONDITIONAL", "conditions": [], "otherwise": "AGENT_REVIEW"}
            ),
            "tickets CONDITIONAL incomplete condition": (
                "tickets", {"authority": "CONDITIONAL", "conditions": [{"when": "large"}], "otherwise": "AGENT_REVIEW"}
            ),
        }
        for name, (stage, policy) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = direct_config()
                if stage == "program_design":
                    config["stages"].insert(1, "program_design")
                if name == "missing tickets":
                    config["gates"].pop("tickets")
                else:
                    config["gates"][stage] = policy
                write_stage0_run(run, config)

                result = planning_cli("initialize", "--run", run)

                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertFalse((run / "planning-control.json").exists())

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = direct_config()
            config["gates"]["system_design"] = {
                "authority": "HUMAN_IF_CHANGED",
                "material_dimensions": list(SYSTEM_DESIGN_DIMENSIONS),
                "otherwise": "AGENT_REVIEW",
            }
            config["gates"]["tickets"] = {
                "authority": "CONDITIONAL",
                "conditions": [
                    {"when": "multi_repository", "then": "HUMAN"},
                    {"when": "single_repository", "then": "AGENT_REVIEW"},
                ],
                "otherwise": "AGENT_REVIEW",
            }
            write_stage0_run(run, config)

            result = planning_cli("initialize", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_downstream_initialize_requires_tickets_before_execute_and_preserves_selected_order(self):
        invalid_orders = (
            ["system_design", "execute", "tickets"],
            ["program_design", "execute"],
            ["tickets", "program_design", "execute"],
        )
        for stages in invalid_orders:
            with self.subTest(stages=stages), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = run_config()
                config["version"] = 2
                config["stages"] = stages
                config["system_design_participation"] = "agent_led" if "system_design" in stages else None
                config["gates"] = {
                    stage: {"authority": "HUMAN"}
                    for stage in ("system_design", "program_design", "tickets")
                    if stage in stages
                }
                config["recommendation"]["gates"] = config["gates"]
                write_stage0_run(run, config)

                result = planning_cli("initialize", "--run", run)

                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertFalse((run / "planning-control.json").exists())

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            config["version"] = 2
            config["system_design_participation"] = None
            config["stages"] = ["program_design", "tickets", "execute"]
            config["gates"] = {
                "program_design": {"authority": "AGENT_REVIEW"},
                "tickets": {"authority": "HUMAN"},
            }
            config["recommendation"]["gates"] = config["gates"]
            write_stage0_run(run, config)

            result = planning_cli("initialize", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)
            planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
            self.assertEqual(planning["phase"], "program_design")
            self.assertEqual(planning["gates"], {
                "system_design": "NOT_REQUIRED",
                "program_design": "PENDING",
                "tickets": "PENDING",
            })

    def test_program_design_after_system_design_requires_exact_accepted_system_binding(self):
        mutations = (None, "kind", "artifact", "version", "sha256", "extra")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_program_after_system(run)
                accepted = planning["acceptances"]["system_design"]
                source = {
                    "kind": "system_design",
                    "artifact": "30-system-design.md",
                    "version": accepted["candidate_version"],
                    "sha256": accepted["candidate_sha256"],
                }
                if mutation == "kind":
                    source["kind"] = "product_closure"
                elif mutation == "artifact":
                    source["artifact"] = "20-prd.md"
                elif mutation == "version":
                    source["version"] += 1
                elif mutation == "sha256":
                    source["sha256"] = "0" * 64
                elif mutation == "extra":
                    source["effective_config_hash"] = "0" * 64
                write_program_design(run, source)

                result = planning_cli("check", "--run", run, "--stage", "program_design")

                self.assertEqual(result.returncode == 0, mutation is None, result.stderr or result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["verdict"], "PASS" if mutation is None else "BLOCKED")
                if mutation is not None:
                    self.assertTrue(any("System Design" in item["problem"] for item in report["gaps"]))

    def test_program_design_prefers_accepted_system_when_discovery_and_system_are_selected(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_product_system_program(run)
            product = planning["stage0_anchor"]["product_closure"]
            write_program_design(run, {
                "kind": "product_closure",
                "artifact": "20-prd.md",
                "version": product["version"],
                "sha256": product["sha256"],
            })

            rejected = planning_cli("check", "--run", run, "--stage", "program_design")

            self.assertEqual(rejected.returncode, 1, rejected.stderr or rejected.stdout)
            rejected_report = json.loads(rejected.stdout)
            self.assertEqual(rejected_report["verdict"], "BLOCKED")
            self.assertTrue(any("System Design" in gap["problem"] for gap in rejected_report["gaps"]))

            accepted = planning["acceptances"]["system_design"]
            write_program_design(run, {
                "kind": "system_design",
                "artifact": "30-system-design.md",
                "version": accepted["candidate_version"],
                "sha256": accepted["candidate_sha256"],
            })

            passed = planning_cli("check", "--run", run, "--stage", "program_design")

            self.assertEqual(passed.returncode, 0, passed.stderr or passed.stdout)
            passed_report = json.loads(passed.stdout)
            self.assertEqual(passed_report["verdict"], "PASS")
            self.assertEqual(passed_report["source_binding"]["kind"], "system_design")

    def test_program_design_check_does_not_grade_semantic_quality(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_direct_program(run)
            anchor = planning["stage0_anchor"]
            source = {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            }
            write_program_design(run, source)
            candidate = run / "40-program-design.md"
            frontmatter_text = candidate.read_text(encoding="utf-8").split("\n---\n", 1)[0]
            body_parts = ["# Program design — intentionally poor"]
            for heading in PROGRAM_DESIGN_SECTIONS:
                body_parts.append(f"## {heading}\n\nTODO; vague and possibly contradictory.")
                if heading == "File-tree diff":
                    body_parts.append(
                        "```text\n## Not a real section\nline-by-line pseudocode with no evidence\n```"
                    )
            candidate.write_text(
                frontmatter_text + "\n---\n\n" + "\n\n".join(body_parts) + "\n",
                encoding="utf-8",
            )

            result = planning_cli("check", "--run", run, "--stage", "program_design")

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["verdict"], "PASS")
            self.assertEqual(report["gaps"], [])
            self.assertEqual(report["source_binding"], source)

    def test_program_design_rejects_symlink_extra_fields_duplicate_keys_and_wrong_sections(self):
        mutations = (
            "symlink", "frontmatter-extra", "source-extra", "duplicate-key",
            "duplicate-source-key", "wrong-sections", "boolean-config-revision",
        )
        for mutation in mutations:
            with (
                self.subTest(mutation=mutation),
                tempfile.TemporaryDirectory() as td,
                tempfile.TemporaryDirectory() as outside_td,
            ):
                run = Path(td)
                planning = initialize_direct_program(run)
                anchor = planning["stage0_anchor"]
                source = {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": anchor["base_run_sha256"],
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                }
                if mutation == "source-extra":
                    source["version"] = 1
                elif mutation == "boolean-config-revision":
                    self.assertEqual(anchor["effective_config_revision"], 0)
                    source["effective_config_revision"] = False
                write_program_design(
                    run,
                    source,
                    **({"unexpected": "field"} if mutation == "frontmatter-extra" else {}),
                )
                candidate = run / "40-program-design.md"
                if mutation == "symlink":
                    outside = Path(outside_td) / "candidate.md"
                    outside.write_bytes(candidate.read_bytes())
                    candidate.unlink()
                    candidate.symlink_to(outside)
                elif mutation == "duplicate-key":
                    candidate.write_text(
                        candidate.read_text(encoding="utf-8").replace(
                            "run: demo", "run: demo\nrun: demo", 1
                        ),
                        encoding="utf-8",
                    )
                elif mutation == "duplicate-source-key":
                    candidate.write_text(
                        candidate.read_text(encoding="utf-8").replace(
                            "  kind: stage0", "  kind: stage0\n  kind: stage0", 1
                        ),
                        encoding="utf-8",
                    )
                elif mutation == "wrong-sections":
                    candidate.write_text(
                        candidate.read_text(encoding="utf-8").replace(
                            "## Implementation constraints and sequencing",
                            "## Vertical slices",
                        ),
                        encoding="utf-8",
                    )

                result = planning_cli("check", "--run", run, "--stage", "program_design")

                self.assertEqual(result.returncode, 1, result.stderr or result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["verdict"], "BLOCKED")
                problems = " ".join(item["problem"] for item in report["gaps"]).lower()
                expected = {
                    "symlink": "symlink",
                    "frontmatter-extra": "schema",
                    "source-extra": "stage 0",
                    "duplicate-key": "duplicate yaml key",
                    "duplicate-source-key": "duplicate yaml key",
                    "wrong-sections": "section",
                    "boolean-config-revision": "stage 0",
                }[mutation]
                self.assertIn(expected, problems)

    def test_program_design_check_reports_all_mechanical_gaps_without_mutation(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as caller_td:
            run = Path(td)
            planning = initialize_direct_program(run)
            anchor = planning["stage0_anchor"]
            write_program_design(
                run,
                {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": "0" * 64,
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                },
                version=False,
                status="accepted",
                gate_ready=False,
                opened="21-08-2026",
                participation="agent_led",
            )
            candidate = run / "40-program-design.md"
            candidate.write_text(
                candidate.read_text(encoding="utf-8")
                .replace("run: demo", "run: other-run", 1)
                .replace(
                    "## Implementation constraints and sequencing",
                    "## Vertical slices",
                ),
                encoding="utf-8",
            )
            before = {
                path.relative_to(run).as_posix(): path.read_bytes()
                for path in run.rglob("*")
                if path.is_file()
            }

            result = planning_cli(
                "check", "--run", run, "--stage", "program_design", cwd=caller_td
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            problems = [item["problem"].lower() for item in report["gaps"]]
            for expected in (
                "frontmatter", "run identity", "version", "status", "readiness",
                "participation", "opened date", "section", "stage 0",
            ):
                self.assertTrue(any(expected in problem for problem in problems), expected)
            self.assertTrue(all(item["resume_action"] for item in report["gaps"]))
            self.assertIsNone(report["source_binding"])
            self.assertEqual(
                {
                    path.relative_to(run).as_posix(): path.read_bytes()
                    for path in run.rglob("*")
                    if path.is_file()
                },
                before,
            )

    def test_direct_program_design_requires_exact_frozen_stage0_binding(self):
        mutations = (
            None, "kind", "artifact", "sha256", "config_hash", "config_revision", "version",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_direct_program(run)
                anchor = planning["stage0_anchor"]
                source = {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": anchor["base_run_sha256"],
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                }
                if mutation == "kind":
                    source["kind"] = "product_closure"
                elif mutation == "artifact":
                    source["artifact"] = "20-prd.md"
                elif mutation == "sha256":
                    source["sha256"] = "0" * 64
                elif mutation == "config_hash":
                    source["effective_config_hash"] = "0" * 64
                elif mutation == "config_revision":
                    source["effective_config_revision"] += 1
                elif mutation == "version":
                    source["version"] = 1
                write_program_design(run, source)

                result = planning_cli("check", "--run", run, "--stage", "program_design")

                self.assertEqual(result.returncode == 0, mutation is None, result.stderr or result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["verdict"], "PASS" if mutation is None else "BLOCKED")
                if mutation is not None:
                    self.assertTrue(any("Stage 0" in item["problem"] for item in report["gaps"]))

    def test_program_design_without_system_design_requires_exact_accepted_product_binding(self):
        mutations = (None, "kind", "artifact", "version", "sha256", "extra")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                accepted = initialize_product_program(run)
                source = {
                    "kind": "product_closure",
                    "artifact": "20-prd.md",
                    "version": accepted["candidate_version"],
                    "sha256": accepted["candidate_sha256"],
                }
                if mutation == "kind":
                    source["kind"] = "system_design"
                elif mutation == "artifact":
                    source["artifact"] = "30-system-design.md"
                elif mutation == "version":
                    source["version"] += 1
                elif mutation == "sha256":
                    source["sha256"] = "0" * 64
                elif mutation == "extra":
                    source["effective_config_revision"] = 0
                write_program_design(run, source)

                result = planning_cli("check", "--run", run, "--stage", "program_design")

                self.assertEqual(result.returncode == 0, mutation is None, result.stderr or result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["verdict"], "PASS" if mutation is None else "BLOCKED")
                if mutation is not None:
                    self.assertTrue(any("product closure" in item["problem"] for item in report["gaps"]))

    def test_system_design_product_path_requires_exact_accepted_prd_binding(self):
        for mutation, expected_success in ((None, True), ("wrong-hash", False)):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                accepted = initialize_product_planning(run)
                source_binding = {
                    "kind": "product_closure",
                    "artifact": "20-prd.md",
                    "version": accepted["candidate_version"],
                    "sha256": accepted["candidate_sha256"],
                }
                if mutation == "wrong-hash":
                    source_binding["sha256"] = "0" * 64
                write_system_design(run, source_binding)
                before = {
                    path.name: path.read_bytes()
                    for path in run.iterdir()
                    if path.is_file()
                }

                result = planning_cli("check", "--run", run, "--stage", "system_design")

                self.assertEqual(result.returncode == 0, expected_success, result.stderr or result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["verdict"], "PASS" if expected_success else "BLOCKED")
                self.assertEqual(
                    {path.name: path.read_bytes() for path in run.iterdir() if path.is_file()},
                    before,
                )

    def test_system_design_direct_path_requires_exact_stage_zero_binding_without_prd(self):
        for mutation in (None, "prd-field", "wrong-sha", "wrong-config-hash", "wrong-config-revision", "wrong-artifact"):
            expected_success = mutation is None
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_direct_planning(run)
                anchor = planning["stage0_anchor"]
                source_binding = {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": anchor["base_run_sha256"],
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                }
                if mutation == "prd-field":
                    source_binding["version"] = 1
                elif mutation == "wrong-sha":
                    source_binding["sha256"] = "0" * 64
                elif mutation == "wrong-config-hash":
                    source_binding["effective_config_hash"] = "0" * 64
                elif mutation == "wrong-config-revision":
                    source_binding["effective_config_revision"] += 1
                elif mutation == "wrong-artifact":
                    source_binding["artifact"] = "20-prd.md"
                write_system_design(run, source_binding)

                result = planning_cli("check", "--run", run, "--stage", "system_design")

                self.assertEqual(result.returncode == 0, expected_success, result.stderr or result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["verdict"], "PASS" if expected_success else "BLOCKED")
                if not expected_success:
                    self.assertTrue(any("Stage 0" in item["problem"] for item in report["gaps"]))

    def test_system_design_check_is_read_only_and_reports_all_mechanical_gaps(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_direct_planning(run)
            anchor = planning["stage0_anchor"]
            write_system_design(
                run,
                {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": "0" * 64,
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                },
                status="accepted",
                gate_ready=False,
                participation="co_design",
            )
            candidate = run / "30-system-design.md"
            candidate.write_text(
                candidate.read_text(encoding="utf-8").replace("## Open decisions", "## Loose ends"),
                encoding="utf-8",
            )
            before = {path.name: path.read_bytes() for path in run.iterdir() if path.is_file()}

            result = planning_cli("check", "--run", run, "--stage", "system_design")

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            problems = {item["problem"] for item in report["gaps"]}
            self.assertTrue(any("status" in item for item in problems))
            self.assertTrue(any("readiness" in item for item in problems))
            self.assertTrue(any("participation" in item for item in problems))
            self.assertTrue(any("section" in item for item in problems))
            self.assertTrue(any("Stage 0" in item for item in problems))
            self.assertTrue(all(item["resume_action"] for item in report["gaps"]))
            self.assertEqual(
                {path.name: path.read_bytes() for path in run.iterdir() if path.is_file()},
                before,
            )

        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside_td:
            run = Path(td)
            initialize_direct_planning(run)
            outside = Path(outside_td) / "candidate.md"
            outside.write_text("not a managed candidate", encoding="utf-8")
            (run / "30-system-design.md").symlink_to(outside)

            result = planning_cli("check", "--run", run, "--stage", "system_design")

            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["verdict"], "BLOCKED")
            self.assertTrue(any("symlink" in item["problem"] for item in report["gaps"]))

    def test_co_design_check_blocks_without_or_with_stale_board_and_passes_when_current(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = direct_config(participation="co_design")
            write_stage0_run(run, config)
            initialized = planning_cli("initialize", "--run", run)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
            anchor = planning["stage0_anchor"]
            write_system_design(run, {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            }, participation="co_design")

            missing = planning_cli("check", "--run", run, "--stage", "system_design")
            self.assertEqual(missing.returncode, 1, missing.stderr)
            missing_report = json.loads(missing.stdout)
            self.assertEqual(missing_report["verdict"], "BLOCKED")
            self.assertTrue(any("30-system-design.html" in item["problem"] for item in missing_report["gaps"]))
            self.assertTrue(all(item["resume_action"] for item in missing_report["gaps"]))

            rendered = render_system_board(run)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            current = planning_cli("check", "--run", run, "--stage", "system_design")
            self.assertEqual(current.returncode, 0, current.stderr)
            self.assertEqual(json.loads(current.stdout)["verdict"], "PASS")

            with (run / "30-system-design.md").open("a", encoding="utf-8") as handle:
                handle.write("\nstale board source\n")
            stale = planning_cli("check", "--run", run, "--stage", "system_design")
            self.assertEqual(stale.returncode, 1, stale.stderr)
            stale_report = json.loads(stale.stdout)
            self.assertEqual(stale_report["verdict"], "BLOCKED")
            self.assertTrue(any("sha256" in item["problem"].lower() for item in stale_report["gaps"]))

    def test_human_system_design_acceptance_records_exact_binding_and_advances_one_phase(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_direct_planning(run)
            anchor = planning["stage0_anchor"]
            source_binding = {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            }
            write_system_design(run, source_binding)
            candidate_before = (run / "30-system-design.md").read_bytes()
            control_before = (run / "control.json").read_bytes()
            run_before = (run / "run.yaml").read_bytes()

            result = planning_cli(
                "advance", "--run", run, "--stage", "system_design",
                "--approval", "human", "--date", "2026-08-21",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("advanced system_design -> tickets", result.stdout)
            updated = PLANNING.load_planning_control(run)
            self.assertEqual((updated["phase"], updated["revision"]), ("tickets", 2))
            self.assertEqual(updated["gates"], {
                "system_design": "HUMAN_APPROVED",
                "program_design": "NOT_REQUIRED",
                "tickets": "PENDING",
            })
            self.assertEqual(updated["acceptances"]["system_design"], {
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "30-system-design.md"),
                "authority": "HUMAN",
                "accepted": "2026-08-21",
                "review_reference": None,
                "review_sha256": None,
                "source_bindings": [source_binding],
                "repository_baselines": [],
            })
            self.assertEqual((run / "30-system-design.md").read_bytes(), candidate_before)
            self.assertEqual((run / "control.json").read_bytes(), control_before)
            self.assertEqual((run / "run.yaml").read_bytes(), run_before)
            for forbidden in ("approved", "history.json", "events.json", "journal.json"):
                self.assertFalse((run / forbidden).exists())

    def test_co_design_human_acceptance_requires_current_board_and_keeps_html_non_authoritative(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = direct_config(participation="co_design")
            write_stage0_run(run, config)
            initialized = planning_cli("initialize", "--run", run)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
            anchor = planning["stage0_anchor"]
            source_binding = {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            }
            write_system_design(run, source_binding, participation="co_design")
            rendered = render_system_board(run)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            html_before = (run / "30-system-design.html").read_bytes()

            accepted = planning_cli(
                "advance", "--run", run, "--stage", "system_design",
                "--approval", "human", "--date", "2026-08-21",
            )

            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            updated = PLANNING.load_planning_control(run)
            record = updated["acceptances"]["system_design"]
            self.assertEqual(record["candidate_sha256"], sha256(run / "30-system-design.md"))
            self.assertEqual(record["authority"], "HUMAN")
            self.assertEqual(record["source_bindings"], [source_binding])
            self.assertNotIn("html", " ".join(record).lower())
            self.assertEqual((run / "30-system-design.html").read_bytes(), html_before)
            self.assertEqual(updated["phase"], "tickets")

    def test_accepted_co_design_loader_requires_a_current_board_projection(self):
        for mutation in ("missing", "metadata", "body"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = direct_config(participation="co_design")
                write_stage0_run(run, config)
                initialized = planning_cli("initialize", "--run", run)
                self.assertEqual(initialized.returncode, 0, initialized.stderr)
                planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
                anchor = planning["stage0_anchor"]
                write_system_design(run, {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": anchor["base_run_sha256"],
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                }, participation="co_design")
                self.assertEqual(render_system_board(run).returncode, 0)
                accepted = planning_cli(
                    "advance", "--run", run, "--stage", "system_design",
                    "--approval", "human", "--date", "2026-08-21",
                )
                self.assertEqual(accepted.returncode, 0, accepted.stderr)

                board = run / "30-system-design.html"
                if mutation == "missing":
                    board.unlink()
                elif mutation == "metadata":
                    board.write_text(
                        board.read_text(encoding="utf-8").replace(
                            'content="30-system-design.md"', 'content="wrong.md"', 1
                        ),
                        encoding="utf-8",
                    )
                else:
                    board.write_text(
                        board.read_text(encoding="utf-8").replace(
                            "Concrete current system decisions.", "Tampered topology.", 1
                        ),
                        encoding="utf-8",
                    )

                with self.assertRaisesRegex(PLANNING.ControlError, "board|projection"):
                    PLANNING.load_planning_control(run)

    def test_human_system_design_acceptance_rechecks_candidate_and_source_under_lock(self):
        for changed_artifact in ("30-system-design.md", "20-prd.md"):
            with self.subTest(changed_artifact=changed_artifact), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                accepted = initialize_product_planning(run)
                write_system_design(run, {
                    "kind": "product_closure",
                    "artifact": "20-prd.md",
                    "version": accepted["candidate_version"],
                    "sha256": accepted["candidate_sha256"],
                })
                planning_before = (run / "planning-control.json").read_bytes()
                original_report = PLANNING.system_design_report
                calls = 0

                def change_after_first_report(*args, **kwargs):
                    nonlocal calls
                    report = original_report(*args, **kwargs)
                    calls += 1
                    if calls == 1:
                        target = run / changed_artifact
                        target.write_bytes(target.read_bytes() + b"\nchanged during acceptance\n")
                    return report

                with mock.patch.object(PLANNING, "system_design_report", side_effect=change_after_first_report):
                    with PLANNING.planning_lock(run):
                        with self.assertRaisesRegex(PLANNING.ControlError, "changed"):
                            PLANNING.advance_boundary(run, "system_design", "human", None, "2026-08-21")

                self.assertGreaterEqual(calls, 2)
                self.assertEqual((run / "planning-control.json").read_bytes(), planning_before)

    def test_human_system_design_acceptance_rechecks_at_atomic_write_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_direct_planning(run)
            anchor = planning["stage0_anchor"]
            write_system_design(run, {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            })
            before = (run / "planning-control.json").read_bytes()
            original_write = PLANNING.write_planning_control_atomic

            def mutate_immediately_before_write(*args, **kwargs):
                candidate = run / "30-system-design.md"
                candidate.write_bytes(candidate.read_bytes() + b"\nchanged at write boundary\n")
                return original_write(*args, **kwargs)

            with mock.patch.object(
                PLANNING,
                "write_planning_control_atomic",
                side_effect=mutate_immediately_before_write,
            ):
                with PLANNING.planning_lock(run):
                    with self.assertRaises(PLANNING.ControlError):
                        PLANNING.advance_boundary(run, "system_design", "human", None, "2026-08-21")

            self.assertEqual((run / "planning-control.json").read_bytes(), before)
            persisted = json.loads(before)
            self.assertEqual((persisted["revision"], persisted["gates"]["system_design"]), (1, "PENDING"))

    def test_review_parse_and_recorded_hash_use_one_byte_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            initialize_authority_planning(run, "AGENT_REVIEW")
            review = write_system_review(
                run, policy="AGENT_REVIEW", materiality=None, review=semantic_review()
            )
            original_bytes = review.read_bytes()
            replacement = json.loads(original_bytes)
            replacement["semantic_review"]["dimensions"][0]["evidence"] = "Different valid evidence."
            replacement_bytes = (json.dumps(replacement, indent=2) + "\n").encode("utf-8")
            real_file_sha256 = PLANNING.file_sha256
            changed = False

            def mutate_between_parse_and_hash(path):
                nonlocal changed
                if Path(path) == review and not changed:
                    changed = True
                    review.write_bytes(replacement_bytes)
                return real_file_sha256(path)

            with mock.patch.object(PLANNING, "file_sha256", side_effect=mutate_between_parse_and_hash):
                with PLANNING.planning_lock(run):
                    PLANNING.advance_boundary(
                        run,
                        "system_design",
                        None,
                        "reviews/system-design-v1.json",
                        "2026-08-21",
                    )

            self.assertFalse(changed)
            self.assertEqual(review.read_bytes(), original_bytes)
            record = PLANNING.load_planning_control(run)["acceptances"]["system_design"]
            self.assertEqual(record["review_sha256"], sha256(review))

    def test_agent_review_acceptance_rechecks_envelope_at_atomic_write_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            initialize_authority_planning(run, "AGENT_REVIEW")
            review = write_system_review(
                run, policy="AGENT_REVIEW", materiality=None, review=semantic_review()
            )
            before = (run / "planning-control.json").read_bytes()
            original_write = PLANNING.write_planning_control_atomic

            def mutate_review_immediately_before_write(*args, **kwargs):
                review.write_bytes(review.read_bytes() + b" \n")
                return original_write(*args, **kwargs)

            with mock.patch.object(
                PLANNING,
                "write_planning_control_atomic",
                side_effect=mutate_review_immediately_before_write,
            ):
                with PLANNING.planning_lock(run):
                    with self.assertRaisesRegex(PLANNING.ControlError, "review|evidence|boundary"):
                        PLANNING.advance_boundary(
                            run,
                            "system_design",
                            None,
                            "reviews/system-design-v1.json",
                            "2026-08-21",
                        )

            self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_direct_accepted_state_loader_rejects_stage_zero_source_drift(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_direct_planning(run)
            anchor = planning["stage0_anchor"]
            write_system_design(run, {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            })
            accepted = planning_cli(
                "advance", "--run", run, "--stage", "system_design",
                "--approval", "human", "--date", "2026-08-21",
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            with (run / "run.yaml").open("a", encoding="utf-8") as handle:
                handle.write("# direct source drift\n")

            with self.assertRaisesRegex(PLANNING.ControlError, "Stage 0|run.yaml|provenance"):
                PLANNING.load_planning_control(run)

    def test_direct_agent_review_blocked_no_fallback_and_exact_semantic_rows_and_gaps(self):
        def valid_blocked():
            return semantic_review(
                verdict="BLOCKED", blocked_dimensions=(SYSTEM_DESIGN_DIMENSIONS[0],)
            )

        cases = {
            "blocked": (valid_blocked(), []),
            "no-human-fallback": (semantic_review(), ["--approval", "human"]),
            "missing-row": (semantic_review(), []),
            "duplicate-row": (semantic_review(), []),
            "unknown-row": (semantic_review(), []),
            "empty-evidence": (semantic_review(), []),
            "blocked-without-gap": (valid_blocked(), []),
            "blocked-wrong-gap-dimension": (valid_blocked(), []),
            "blocked-missing-one-gap": (
                semantic_review(
                    verdict="BLOCKED",
                    blocked_dimensions=(SYSTEM_DESIGN_DIMENSIONS[0], SYSTEM_DESIGN_DIMENSIONS[1]),
                ),
                [],
            ),
        }
        cases["missing-row"][0]["dimensions"].pop()
        cases["duplicate-row"][0]["dimensions"][-1] = dict(cases["duplicate-row"][0]["dimensions"][0])
        cases["unknown-row"][0]["dimensions"][-1]["dimension"] = "unknown_dimension"
        cases["empty-evidence"][0]["dimensions"][-1]["evidence"] = ""
        cases["blocked-without-gap"][0]["gaps"] = []
        cases["blocked-wrong-gap-dimension"][0]["gaps"][0]["dimension"] = SYSTEM_DESIGN_DIMENSIONS[1]
        cases["blocked-missing-one-gap"][0]["gaps"].pop()

        for name, (semantic, extra) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                initialize_authority_planning(run, "AGENT_REVIEW")
                write_system_review(
                    run, policy="AGENT_REVIEW", materiality=None, review=semantic
                )
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "system_design",
                    "--review", "reviews/system-design-v1.json", *extra,
                    "--date", "2026-08-21",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_semantic_review_gap_coverage_is_exact_before_blocked_outcome(self):
        malformed = semantic_review(
            verdict="BLOCKED",
            blocked_dimensions=(SYSTEM_DESIGN_DIMENSIONS[0], SYSTEM_DESIGN_DIMENSIONS[1]),
        )
        malformed["gaps"].pop()

        with self.assertRaisesRegex(PLANNING.ControlError, "exactly cover"):
            PLANNING.validate_semantic_review(malformed)

    def test_system_design_review_rejects_wrong_bindings_paths_symlinks_and_duplicate_keys(self):
        mutations = (
            "candidate", "baseline", "policy", "wrong-filename", "escape", "symlink", "duplicate-key",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside_td:
                run = Path(td)
                initialize_authority_planning(run, "AGENT_REVIEW")
                review = write_system_review(
                    run, policy="AGENT_REVIEW", materiality=None, review=semantic_review()
                )
                review_ref = "reviews/system-design-v1.json"
                if mutation in {"candidate", "baseline", "policy"}:
                    envelope = json.loads(review.read_text(encoding="utf-8"))
                    if mutation == "candidate":
                        envelope["candidate_sha256"] = "0" * 64
                    elif mutation == "baseline":
                        envelope["repository_baselines"][0]["baseline"] = "def4567"
                    else:
                        envelope["policy"] = "HUMAN_IF_CHANGED"
                    review.write_text(json.dumps(envelope), encoding="utf-8")
                elif mutation == "wrong-filename":
                    wrong = review.with_name("system-design-v2.json")
                    review.replace(wrong)
                    review_ref = "reviews/system-design-v2.json"
                elif mutation == "escape":
                    review_ref = "../system-design-v1.json"
                elif mutation == "symlink":
                    outside = Path(outside_td) / "review.json"
                    outside.write_bytes(review.read_bytes())
                    review.unlink()
                    review.symlink_to(outside)
                else:
                    text = review.read_text(encoding="utf-8")
                    review.write_text(text.replace('  "version": 1,', '  "version": 1,\n  "version": 1,', 1), encoding="utf-8")
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "system_design",
                    "--review", review_ref, "--date", "2026-08-21",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

    def test_accepted_loader_requires_current_evidence_for_agent_and_hic_human_authorities(self):
        cases = (
            ("AGENT_REVIEW", None, semantic_review(), []),
            (
                "HUMAN_IF_CHANGED",
                materiality(results={SYSTEM_DESIGN_DIMENSIONS[0]: "MATERIAL"}),
                None,
                ["--approval", "human"],
            ),
        )
        for configured, classification, semantic, extra in cases:
            with self.subTest(configured=configured), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                initialize_authority_planning(run, configured)
                review = write_system_review(
                    run, policy=configured, materiality=classification, review=semantic
                )
                accepted = planning_cli(
                    "advance", "--run", run, "--stage", "system_design",
                    "--review", "reviews/system-design-v1.json", *extra,
                    "--date", "2026-08-21",
                )
                self.assertEqual(accepted.returncode, 0, accepted.stderr)
                PLANNING.load_planning_control(run)

                review.write_bytes(review.read_bytes() + b" \n")

                with self.assertRaisesRegex(PLANNING.ControlError, "evidence|review"):
                    PLANNING.load_planning_control(run)

    def test_planning_loader_rejects_gate_acceptance_incoherence(self):
        for mutation in ("record-with-pending-gate", "approved-gate-without-record"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_direct_planning(run)
                anchor = planning["stage0_anchor"]
                write_system_design(run, {
                    "kind": "stage0",
                    "artifact": "run.yaml",
                    "sha256": anchor["base_run_sha256"],
                    "effective_config_hash": anchor["effective_config_hash"],
                    "effective_config_revision": anchor["effective_config_revision"],
                })
                accepted = planning_cli(
                    "advance", "--run", run, "--stage", "system_design",
                    "--approval", "human", "--date", "2026-08-21",
                )
                self.assertEqual(accepted.returncode, 0, accepted.stderr)
                planning_path = run / "planning-control.json"
                state = json.loads(planning_path.read_text(encoding="utf-8"))
                if mutation == "record-with-pending-gate":
                    state["gates"]["system_design"] = "PENDING"
                    state["phase"] = "system_design"
                else:
                    state["acceptances"]["system_design"] = None
                    state["revision"] = 1
                planning_path.write_text(json.dumps(state), encoding="utf-8")

                with self.assertRaisesRegex(PLANNING.ControlError, "gate/acceptance"):
                    PLANNING.load_planning_control(run)

    def test_planning_loader_rejects_phase_and_revision_incoherence(self):
        for field, value, expected in (
            ("phase", "tickets", "coherent current planning state"),
            ("revision", 2, "coherent current planning state"),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                initialize_direct_planning(run)
                planning_path = run / "planning-control.json"
                state = json.loads(planning_path.read_text(encoding="utf-8"))
                state[field] = value
                planning_path.write_text(json.dumps(state), encoding="utf-8")

                with self.assertRaisesRegex(PLANNING.ControlError, expected):
                    PLANNING.load_planning_control(run)

    def test_planning_loader_accepts_only_current_initial_or_human_accepted_system_design_state(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_direct_planning(run)
            anchor = planning["stage0_anchor"]
            write_system_design(run, {
                "kind": "stage0",
                "artifact": "run.yaml",
                "sha256": anchor["base_run_sha256"],
                "effective_config_hash": anchor["effective_config_hash"],
                "effective_config_revision": anchor["effective_config_revision"],
            })
            accepted = planning_cli(
                "advance", "--run", run, "--stage", "system_design",
                "--approval", "human", "--date", "2026-08-21",
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            PLANNING.load_planning_control(run)

            candidate = run / "30-system-design.md"
            candidate.write_bytes(candidate.read_bytes() + b"\nstale\n")

            with self.assertRaisesRegex(PLANNING.ControlError, "candidate"):
                PLANNING.load_planning_control(run)

    def test_planning_load_rejects_non_integer_state_version(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            write_stage0_run(run, direct_config())
            result = planning_cli("initialize", "--run", run)
            self.assertEqual(result.returncode, 0, result.stderr)
            planning_path = run / "planning-control.json"
            planning = json.loads(planning_path.read_text(encoding="utf-8"))
            planning["version"] = 1.0
            planning_path.write_text(json.dumps(planning), encoding="utf-8")

            with self.assertRaisesRegex(PLANNING.ControlError, "values"):
                PLANNING.load_planning_control(run)

    def test_planning_load_rejects_duplicate_keys_and_non_exact_schema(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            write_stage0_run(run, direct_config())
            result = planning_cli("initialize", "--run", run)
            self.assertEqual(result.returncode, 0, result.stderr)
            planning_path = run / "planning-control.json"
            original = planning_path.read_text(encoding="utf-8")

            malformed = json.loads(original)
            malformed["stage0_anchor"]["control_sha256"] = "not-a-hash"
            planning_path.write_text(json.dumps(malformed), encoding="utf-8")
            with self.assertRaisesRegex(PLANNING.ControlError, "anchor"):
                PLANNING.load_planning_control(run)

            duplicate = original.replace('  "run": "demo",', '  "run": "demo",\n  "run": "demo",', 1)
            planning_path.write_text(duplicate, encoding="utf-8")
            with self.assertRaisesRegex(PLANNING.ControlError, "duplicate JSON key"):
                PLANNING.load_planning_control(run)

            extra = json.loads(original)
            extra["history"] = []
            planning_path.write_text(json.dumps(extra), encoding="utf-8")
            with self.assertRaisesRegex(PLANNING.ControlError, "fields"):
                PLANNING.load_planning_control(run)

    def test_confirmed_upstream_contradiction_atomically_stales_system_design(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_program_after_system(run)
            review_input = write_upstream_block_review_input(run, planning)
            review_bytes = review_input.read_bytes()
            control_before = (run / "control.json").read_bytes()
            run_before = (run / "run.yaml").read_bytes()
            system_before = (run / "30-system-design.md").read_bytes()
            program_path = run / "40-program-design.md"
            program_path.write_text("provisional Program Design bytes\n", encoding="utf-8")
            program_before = program_path.read_bytes()
            acceptance_before = planning["acceptances"]["system_design"]

            result = planning_cli(
                "return-upstream", "--run", run,
                "--review-input", review_input.relative_to(run),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            canonical_review = run / "reviews" / "program-design-upstream-block-v1.json"
            self.assertEqual(canonical_review.read_bytes(), review_bytes)
            updated = PLANNING.load_planning_control(run)
            self.assertEqual(updated["status"], "BLOCKED")
            self.assertEqual(updated["phase"], "system_design")
            self.assertEqual(updated["revision"], planning["revision"] + 1)
            self.assertEqual(updated["gates"]["system_design"], "STALE")
            self.assertEqual(updated["gates"]["program_design"], "PENDING")
            self.assertEqual(updated["acceptances"]["system_design"], acceptance_before)
            self.assertIsNone(updated["acceptances"]["program_design"])
            self.assertEqual(updated["blocked_reason"]["kind"], "SYSTEM_DESIGN_REPAIR")
            self.assertEqual(updated["blocked_reason"]["state"], "SYSTEM_DESIGN_STALE")
            self.assertEqual(updated["blocked_reason"]["review_reference"], "reviews/program-design-upstream-block-v1.json")
            self.assertEqual(updated["blocked_reason"]["review_sha256"], hashlib.sha256(review_bytes).hexdigest())
            self.assertEqual(updated["blocked_reason"]["superseded_system_design"], acceptance_before)
            self.assertEqual(updated["blocked_reason"]["attempts_used"], 0)
            self.assertIsNone(updated["blocked_reason"]["current_attempt"])
            self.assertEqual((run / "control.json").read_bytes(), control_before)
            self.assertEqual((run / "run.yaml").read_bytes(), run_before)
            self.assertEqual((run / "30-system-design.md").read_bytes(), system_before)
            self.assertEqual(program_path.read_bytes(), program_before)

    def test_not_confirmed_and_unavailable_upstream_reviews_do_not_mutate_state(self):
        for verdict in ("NOT_CONFIRMED", "UNAVAILABLE"):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_program_after_system(run)
                review_input = write_upstream_block_review_input(run, planning, verdict=verdict)
                planning_before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "return-upstream", "--run", run,
                    "--review-input", review_input.relative_to(run),
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(verdict, result.stderr)
                self.assertEqual((run / "planning-control.json").read_bytes(), planning_before)
                self.assertFalse((run / "reviews" / "program-design-upstream-block-v1.json").exists())

    def test_upstream_review_rejects_malformed_stale_and_wrong_source_evidence(self):
        def add_extra(envelope):
            envelope["extra"] = True

        def add_candidate_binding(envelope):
            envelope["candidate_sha256"] = "0" * 64

        def stale_revision(envelope):
            envelope["planning_revision"] -= 1

        def wrong_system(envelope):
            envelope["system_design_binding"]["sha256"] = "0" * 64

        def wrong_repositories(envelope):
            envelope["repository_baselines"] = []

        def wrong_source(envelope):
            envelope["finding"]["upstream_source"] = "product_closure"

        def machine_path(envelope):
            envelope["finding"]["code_evidence"][0]["path"] = "/machine/private.py"

        def windows_machine_path(envelope):
            envelope["finding"]["code_evidence"][0]["path"] = "C:/machine/private.py"

        def nonexistent_path(envelope):
            envelope["finding"]["code_evidence"][0]["path"] = "does-not-exist.py"

        def prose_machine_path(envelope):
            envelope["review_evidence"] = "Confirmed from /home/example/private.py"

        def unknown_verdict(envelope):
            envelope["verdict"] = "MAYBE"

        for name, mutate in (
            ("extra", add_extra),
            ("candidate-binding", add_candidate_binding),
            ("stale-revision", stale_revision),
            ("wrong-system", wrong_system),
            ("wrong-repositories", wrong_repositories),
            ("wrong-source", wrong_source),
            ("machine-path", machine_path),
            ("windows-machine-path", windows_machine_path),
            ("nonexistent-path", nonexistent_path),
            ("prose-machine-path", prose_machine_path),
            ("unknown-verdict", unknown_verdict),
        ):
            with self.subTest(case=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_program_after_system(run)
                review_input = write_upstream_block_review_input(run, planning)
                envelope = json.loads(review_input.read_text(encoding="utf-8"))
                mutate(envelope)
                review_input.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
                planning_before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "return-upstream", "--run", run,
                    "--review-input", review_input.relative_to(run),
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((run / "planning-control.json").read_bytes(), planning_before)
                self.assertFalse((run / "reviews" / "program-design-upstream-block-v1.json").exists())

    def test_upstream_review_install_is_no_clobber_and_recovers_only_identical_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_program_after_system(run)
            review_input = write_upstream_block_review_input(run, planning)
            review_bytes = review_input.read_bytes()
            planning_before = (run / "planning-control.json").read_bytes()

            with mock.patch.object(
                PLANNING,
                "write_planning_control_atomic",
                side_effect=OSError("simulated crash after evidence install"),
            ):
                with self.assertRaisesRegex(OSError, "simulated crash"), PLANNING.planning_lock(run):
                    PLANNING.return_to_system_design(run, review_input.relative_to(run))

            canonical = run / "reviews" / "program-design-upstream-block-v1.json"
            self.assertEqual(canonical.read_bytes(), review_bytes)
            self.assertEqual((run / "planning-control.json").read_bytes(), planning_before)

            with PLANNING.planning_lock(run):
                PLANNING.return_to_system_design(run, review_input.relative_to(run))
            self.assertEqual(canonical.read_bytes(), review_bytes)

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_program_after_system(run)
            review_input = write_upstream_block_review_input(run, planning)
            canonical = run / "reviews" / "program-design-upstream-block-v1.json"
            canonical.write_text("different bytes\n", encoding="utf-8")
            planning_before = (run / "planning-control.json").read_bytes()

            result = planning_cli(
                "return-upstream", "--run", run,
                "--review-input", review_input.relative_to(run),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("different bytes", result.stderr)
            self.assertEqual(canonical.read_text(encoding="utf-8"), "different bytes\n")
            self.assertEqual((run / "planning-control.json").read_bytes(), planning_before)

    def test_return_revalidates_repository_access_at_write_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_program_after_system(run)
            review_input = write_upstream_block_review_input(run, planning)
            planning_before = (run / "planning-control.json").read_bytes()
            original_write = PLANNING.write_planning_control_atomic

            def remove_binding_before_write(*args, **kwargs):
                write_repository_bindings({})
                return original_write(*args, **kwargs)

            with mock.patch.object(
                PLANNING,
                "write_planning_control_atomic",
                side_effect=remove_binding_before_write,
            ):
                with self.assertRaisesRegex(PLANNING.ControlError, "repository|binding"), PLANNING.planning_lock(run):
                    PLANNING.return_to_system_design(run, review_input.relative_to(run))

            self.assertEqual((run / "planning-control.json").read_bytes(), planning_before)

    def test_upstream_evidence_install_rejects_parent_symlink_swap(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = root / "run"
            outside = root / "outside"
            (run / "reviews").mkdir(parents=True)
            outside.mkdir()
            real_managed_path = PLANNING.managed_path
            swapped = False

            def swap_parent_after_validation(run_dir, relative):
                nonlocal swapped
                path = real_managed_path(run_dir, relative)
                if relative == PLANNING.UPSTREAM_BLOCK_REVIEW_REFERENCE and not swapped:
                    (run / "reviews").rmdir()
                    (run / "reviews").symlink_to(outside, target_is_directory=True)
                    swapped = True
                return path

            with mock.patch.object(PLANNING, "managed_path", side_effect=swap_parent_after_validation):
                with self.assertRaises((PLANNING.ControlError, OSError)):
                    PLANNING.install_upstream_block_evidence(run, b"trusted review bytes\n")

            self.assertFalse((outside / "program-design-upstream-block-v1.json").exists())

    def test_upstream_evidence_install_publishes_only_complete_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            (run / "reviews").mkdir()
            review_bytes = b"complete trusted review bytes\n"
            real_link = os.link
            observed = []

            def fail_before_publish(source, destination, **kwargs):
                source_fd = os.open(source, os.O_RDONLY, dir_fd=kwargs["src_dir_fd"])
                try:
                    with os.fdopen(source_fd, "rb") as handle:
                        observed.append(handle.read())
                finally:
                    pass
                raise OSError("simulated death before canonical publication")

            with mock.patch.object(PLANNING.os, "link", side_effect=fail_before_publish):
                with self.assertRaisesRegex(OSError, "simulated death"):
                    PLANNING.install_upstream_block_evidence(run, review_bytes)

            canonical = run / "reviews" / "program-design-upstream-block-v1.json"
            self.assertEqual(observed, [review_bytes])
            self.assertFalse(canonical.exists())

            with mock.patch.object(PLANNING.os, "link", wraps=real_link):
                PLANNING.install_upstream_block_evidence(run, review_bytes)
            self.assertEqual(canonical.read_bytes(), review_bytes)

    def test_repair_state_rejects_bool_and_impossible_tuples(self):
        for case in ("boolean-attempts", "boolean-system-version", "stale-tickets", "forged-revisions"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                planning = initialize_program_after_system(run)
                review_input = write_upstream_block_review_input(run, planning)
                result = planning_cli(
                    "return-upstream", "--run", run,
                    "--review-input", review_input.relative_to(run),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                planning_path = run / "planning-control.json"
                state = json.loads(planning_path.read_text(encoding="utf-8"))

                if case == "boolean-attempts":
                    state["blocked_reason"]["attempts_used"] = False
                elif case == "boolean-system-version":
                    review = run / "reviews" / "program-design-upstream-block-v1.json"
                    envelope = json.loads(review.read_text(encoding="utf-8"))
                    envelope["system_design_binding"]["version"] = True
                    review.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
                    state["blocked_reason"]["review_sha256"] = sha256(review)
                elif case == "stale-tickets":
                    state["gates"]["tickets"] = "STALE"
                else:
                    state["blocked_reason"]["started_from_revision"] = 100
                    state["revision"] = 101
                    review = run / "reviews" / "program-design-upstream-block-v1.json"
                    envelope = json.loads(review.read_text(encoding="utf-8"))
                    envelope["planning_revision"] = 100
                    review.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
                    state["blocked_reason"]["review_sha256"] = sha256(review)
                planning_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

                with self.assertRaisesRegex(
                    PLANNING.ControlError,
                    "repair episode|does not bind current System Design",
                ):
                    PLANNING.load_planning_control(run)

    def test_upstream_review_input_rejects_duplicate_keys_escape_and_symlink(self):
        for case in ("duplicate", "escape", "symlink"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                run = root / "run"
                run.mkdir()
                planning = initialize_program_after_system(run)
                review_input = write_upstream_block_review_input(run, planning)
                if case == "duplicate":
                    text = review_input.read_text(encoding="utf-8")
                    review_input.write_text(
                        text.replace('  "run": "demo",', '  "run": "demo",\n  "run": "demo",', 1),
                        encoding="utf-8",
                    )
                    argument = review_input.relative_to(run)
                else:
                    outside = root / "outside.json"
                    outside.write_bytes(review_input.read_bytes())
                    if case == "escape":
                        argument = Path("../outside.json")
                    else:
                        review_input.unlink()
                        review_input.symlink_to(outside)
                        argument = review_input.relative_to(run)
                planning_before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "return-upstream", "--run", run, "--review-input", argument,
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((run / "planning-control.json").read_bytes(), planning_before)
                self.assertFalse((run / "reviews" / "program-design-upstream-block-v1.json").exists())

    def test_return_rejects_unsupported_sources_and_accepted_program_design(self):
        for source_kind in ("stage0", "product_closure", "accepted_program_design"):
            with self.subTest(source_kind=source_kind), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                if source_kind == "stage0":
                    planning = initialize_direct_program(run)
                    review_input = run / "reviews" / ".upstream-input.json"
                    review_input.parent.mkdir()
                    review_input.write_text("{}\n", encoding="utf-8")
                elif source_kind == "product_closure":
                    initialize_product_program(run)
                    planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
                    review_input = run / "reviews" / ".upstream-input.json"
                    review_input.parent.mkdir(exist_ok=True)
                    review_input.write_text("{}\n", encoding="utf-8")
                else:
                    initialize_program_source(run, "system_design")
                    planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
                    write_program_review(run, policy="AGENT_REVIEW")
                    accepted = planning_cli(
                        "advance", "--run", run, "--stage", "program_design",
                        "--review", "reviews/program-design-v1.json", "--date", "2026-08-22",
                    )
                    self.assertEqual(accepted.returncode, 0, accepted.stderr)
                    planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
                    review_input = write_upstream_block_review_input(run, planning)
                planning_before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "return-upstream", "--run", run,
                    "--review-input", review_input.relative_to(run),
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((run / "planning-control.json").read_bytes(), planning_before)

    def test_concurrent_return_requests_have_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            planning = initialize_program_after_system(run)
            review_input = write_upstream_block_review_input(run, planning)
            command = [
                sys.executable,
                str(PLANNING_CLI),
                "return-upstream",
                "--run",
                str(run),
                "--review-input",
                str(review_input.relative_to(run)),
            ]
            first = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            second = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            first_output = first.communicate(timeout=30)
            second_output = second.communicate(timeout=30)

            self.assertEqual(sorted((first.returncode, second.returncode)), [0, 1], (first_output, second_output))
            updated = PLANNING.load_planning_control(run)
            self.assertEqual((updated["status"], updated["phase"]), ("BLOCKED", "system_design"))
            canonical = run / "reviews" / "program-design-upstream-block-v1.json"
            self.assertEqual(canonical.read_bytes(), review_input.read_bytes())


if __name__ == "__main__":
    unittest.main()
