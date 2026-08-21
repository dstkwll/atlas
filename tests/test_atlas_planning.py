import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
