import importlib.util
import json
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
    run_config,
    sha256,
    write_discovery,
    write_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
PLANNING_CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_planning.py"
SYSTEM_RENDERER = ROOT / "plugins" / "atlas" / "tools" / "render_system_design.py"
if str(PLANNING_CLI.parent) not in sys.path:
    sys.path.insert(0, str(PLANNING_CLI.parent))
PLANNING_SPEC = importlib.util.spec_from_file_location("atlas_planning", PLANNING_CLI)
assert PLANNING_SPEC is not None and PLANNING_SPEC.loader is not None
PLANNING = importlib.util.module_from_spec(PLANNING_SPEC)
PLANNING_SPEC.loader.exec_module(PLANNING)


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


class AtlasPlanningTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
