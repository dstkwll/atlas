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
    run_config,
    sha256,
    write_discovery,
)


ROOT = Path(__file__).resolve().parents[1]
PLANNING_CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_planning.py"
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
    initialized = planning_cli("initialize", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    return accepted


def initialize_direct_planning(run: Path) -> dict:
    write_stage0_run(run, direct_config())
    initialized = planning_cli("initialize", "--run", run)
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    return json.loads((run / "planning-control.json").read_text(encoding="utf-8"))


class AtlasPlanningTests(unittest.TestCase):
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

    def test_initialize_planning_binds_exact_accepted_product_closure(self):
        with tempfile.TemporaryDirectory() as td:
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

            result = planning_cli("initialize", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)
            planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
            self.assertEqual(planning["stage0_anchor"]["product_closure"], {
                "version": accepted["candidate_version"],
                "sha256": accepted["candidate_sha256"],
            })

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
                "material_dimensions": ["system seams"],
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
                            PLANNING.advance_boundary(run, "system_design", "human", "2026-08-21")

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
                        PLANNING.advance_boundary(run, "system_design", "human", "2026-08-21")

            self.assertEqual((run / "planning-control.json").read_bytes(), before)
            persisted = json.loads(before)
            self.assertEqual((persisted["revision"], persisted["gates"]["system_design"]), (1, "PENDING"))

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

    def test_slice1_rejects_co_design_and_non_human_system_design_authority(self):
        cases = (
            ("co_design", {"authority": "HUMAN"}, "co_design"),
            ("agent_led", {"authority": "AGENT_REVIEW"}, "AGENT_REVIEW"),
            (
                "agent_led",
                {
                    "authority": "HUMAN_IF_CHANGED",
                    "material_dimensions": ["system seams"],
                    "otherwise": "AGENT_REVIEW",
                },
                "HUMAN_IF_CHANGED",
            ),
        )
        for participation, policy, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = direct_config(participation=participation)
                config["gates"]["system_design"] = policy
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
                }, participation=participation)
                before = (run / "planning-control.json").read_bytes()

                result = planning_cli(
                    "advance", "--run", run, "--stage", "system_design",
                    "--approval", "human", "--date", "2026-08-21",
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn(expected, result.stderr)
                self.assertIn("Slice-2", result.stderr)
                self.assertEqual((run / "planning-control.json").read_bytes(), before)

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
