import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests.test_atlas_control import initialize_cli, run_config, sha256
from tests.test_atlas_planning import (
    create_repository,
    planning_cli,
    write_ticket_graph,
    write_ticket_review,
)


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_gazetteer.py"
PLANNING_CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_planning.py"


def run_cli(*args, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )


def run_planning_cli(*args, env=None):
    return subprocess.run(
        [sys.executable, str(PLANNING_CLI), *map(str, args)],
        env=env,
        text=True,
        capture_output=True,
    )


class AtlasGazetteerInventoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / "home"
        self.config_root = self.root / "config"
        self.cwd = self.root / "workspace"
        self.home.mkdir()
        self.config_root.mkdir()
        self.cwd.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def environment(self):
        env = os.environ.copy()
        env.update({"HOME": str(self.home), "XDG_CONFIG_HOME": str(self.config_root)})
        return env

    @property
    def native_config(self):
        return self.config_root / "atlas" / "config.yaml"

    def configure_external_root(self, planning_root, *, bindings=None):
        self.native_config.parent.mkdir(parents=True, exist_ok=True)
        self.native_config.write_text(
            yaml.safe_dump(
                {
                    "artifacts": {"planning_root": str(planning_root)},
                    "repositories": {"bindings": bindings or {}},
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

    def initialize_discovery_run(
        self,
        planning_root,
        *,
        slug="demo",
        goal="Make completion externally observable",
        root_mode="external",
        root_path=None,
        repositories=None,
    ):
        run = planning_root / slug
        run.mkdir()
        config = run_config()
        config["run"] = slug
        config["run_path"] = slug
        config["goal"] = goal
        config["planning_root"] = {
            "source": "artifacts.planning_root",
            "mode": root_mode,
            "path": str(planning_root if root_path is None else root_path),
        }
        if repositories is not None:
            config["repos"] = repositories
        (run / "run.yaml").write_text(
            yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
        )
        initialized = initialize_cli(run)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        return run

    def test_inventory_reports_not_configured_without_writing_state(self):
        atlas_config = self.config_root / "atlas" / "config.yaml"

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "version": 1,
                "command": "inventory",
                "verdict": "NOT_CONFIGURED",
                "config_path": None,
                "planning_root": None,
                "runs": [],
                "gaps": [
                    {
                        "code": "config_missing",
                        "problem": "Atlas machine configuration is missing",
                        "resume_action": "configure Atlas through Gazetteer setup",
                    }
                ],
            },
        )
        self.assertFalse(atlas_config.exists())
        self.assertEqual(list(self.cwd.iterdir()), [])

    def test_inventory_reports_malformed_config_as_structured_blocker(self):
        self.native_config.parent.mkdir(parents=True, exist_ok=True)
        self.native_config.write_text("not: [valid\n", encoding="utf-8")

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertEqual(report["runs"], [])
        self.assertEqual(report["gaps"][0]["code"], "invalid_config")
        self.assertIn("machine config is unreadable or malformed", report["gaps"][0]["problem"])
        self.assertNotIn("Traceback", result.stderr)

    @unittest.skipIf(os.name == "nt", "POSIX directory mode bits are not enforced on Windows")
    def test_unreadable_planning_root_is_structured_global_blocker(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        self.configure_external_root(planning_root)
        planning_root.chmod(0)
        try:
            result = run_cli(
                "inventory", "--cwd", self.cwd,
                cwd=self.cwd,
                env=self.environment(),
            )
        finally:
            planning_root.chmod(0o700)

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertEqual(report["gaps"][0]["code"], "inventory_unavailable")
        self.assertEqual(report["runs"], [])
        self.assertNotIn("Traceback", result.stderr)

    def test_inventory_validates_and_summarizes_one_discovery_run_read_only(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        self.configure_external_root(planning_root)
        run = self.initialize_discovery_run(planning_root)
        immutable_before = {
            "run.yaml": sha256(run / "run.yaml"),
            "control.json": sha256(run / "control.json"),
        }

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["config_path"], str(self.native_config))
        self.assertEqual(report["planning_root"], str(planning_root))
        self.assertEqual(report["gaps"], [])
        self.assertEqual(
            report["runs"],
            [
                {
                    "run": "demo",
                    "path": str(run),
                    "goal": "Make completion externally observable",
                    "repositories": ["fixture"],
                    "status": "PLANNING",
                    "phase": "discovery",
                    "blocked_reason": None,
                    "ready_for_execution": False,
                    "continuation": "DISCOVERY",
                    "accepted_boundaries": [],
                    "accepted_graph": None,
                }
            ],
        )
        self.assertEqual(
            {"run.yaml": sha256(run / "run.yaml"), "control.json": sha256(run / "control.json")},
            immutable_before,
        )
        self.assertFalse((run / "planning-control.json").exists())

    def test_repository_relative_inventory_returns_all_runs_without_selecting_one(self):
        subprocess.run(["git", "init", "-q", self.cwd], check=True)
        planning_root = self.cwd / ".planning"
        planning_root.mkdir()
        self.native_config.parent.mkdir(parents=True, exist_ok=True)
        self.native_config.write_text(
            yaml.safe_dump(
                {
                    "artifacts": {"planning_root": ".planning"},
                    "repositories": {"bindings": {}},
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        self.initialize_discovery_run(
            planning_root,
            slug="retry-policy",
            goal="Decide retry policy",
            root_mode="repository-relative",
            root_path=".planning",
        )
        self.initialize_discovery_run(
            planning_root,
            slug="job-cancellation",
            goal="Add job cancellation",
            root_mode="repository-relative",
            root_path=".planning",
        )

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["planning_root"], str(planning_root))
        self.assertEqual([item["run"] for item in report["runs"]], ["job-cancellation", "retry-policy"])
        self.assertNotIn("selected_run", report)

    def test_external_inventory_marks_exact_current_repository_relevance(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        repository_a = self.root / "repository-a"
        repository_b = self.root / "repository-b"
        baseline_a = create_repository(repository_a, "repository a\n")
        baseline_b = create_repository(repository_b, "repository b\n")
        self.configure_external_root(
            planning_root,
            bindings={"repo-a": str(repository_a), "repo-b": str(repository_b)},
        )
        self.initialize_discovery_run(
            planning_root,
            slug="for-a",
            goal="Change repository A",
            repositories=[{"repository": "repo-a", "baseline": baseline_a}],
        )
        self.initialize_discovery_run(
            planning_root,
            slug="for-b",
            goal="Change repository B",
            repositories=[{"repository": "repo-b", "baseline": baseline_b}],
        )

        result = run_cli(
            "inventory", "--cwd", repository_a,
            cwd=repository_a,
            env=self.environment(),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["current_repository_identity"], "repo-a")
        self.assertEqual(report["repository_relevant_runs"], ["for-a"])
        self.assertNotIn("selected_run", report)

    def test_unrelated_stale_binding_is_diagnostic_not_global_blocker(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        repository = self.root / "repository"
        baseline = create_repository(repository, "current repository\n")
        self.configure_external_root(
            planning_root,
            bindings={
                "current": str(repository),
                "stale": str(self.root / "missing-repository"),
            },
        )
        self.initialize_discovery_run(
            planning_root,
            slug="current-run",
            repositories=[{"repository": "current", "baseline": baseline}],
        )
        self.initialize_discovery_run(
            planning_root,
            slug="stale-run",
            repositories=[{"repository": "stale", "baseline": baseline}],
        )

        result = run_cli(
            "inventory", "--cwd", repository,
            cwd=repository,
            env=self.environment(),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["verdict"], "PARTIAL")
        self.assertEqual(report["current_repository_identity"], "current")
        self.assertEqual(report["repository_relevant_runs"], ["current-run"])
        self.assertEqual(report["repository_blocked_runs"], ["stale-run"])
        self.assertEqual(report["gaps"][0]["code"], "binding_unavailable")
        self.assertEqual(report["gaps"][0]["repository"], "stale")

    def test_ambiguous_current_repository_bindings_block_inventory(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        repository = self.root / "repository"
        create_repository(repository, "ambiguous repository\n")
        self.configure_external_root(
            planning_root,
            bindings={"one": str(repository), "two": str(repository)},
        )

        result = run_cli(
            "inventory", "--cwd", repository,
            cwd=repository,
            env=self.environment(),
        )

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertEqual(report["gaps"][0]["code"], "ambiguous_binding")
        self.assertEqual(report["runs"], [])

    def test_inventory_uses_validated_planning_cursor_for_downstream_run(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        self.configure_external_root(planning_root)
        run = planning_root / "execution-kernel"
        run.mkdir()
        config = run_config()
        config.update(
            {
                "version": 2,
                "run": "execution-kernel",
                "run_path": "execution-kernel",
                "goal": "Build the execution kernel",
                "planning_root": {
                    "source": "artifacts.planning_root",
                    "mode": "external",
                    "path": str(planning_root),
                },
                "system_design_participation": None,
                "stages": ["program_design", "tickets", "execute"],
            }
        )
        config["gates"].pop("discovery")
        config["gates"]["program_design"] = {"authority": "AGENT_REVIEW"}
        config["gates"]["tickets"] = {"authority": "HUMAN"}
        config["recommendation"]["gates"] = config["gates"]
        (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        initialized = initialize_cli(run)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        planning_initialized = planning_cli("initialize", "--run", run)
        self.assertEqual(planning_initialized.returncode, 0, planning_initialized.stderr)
        before = {
            name: sha256(run / name)
            for name in ("run.yaml", "control.json", "planning-control.json")
        }

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 0, result.stderr)
        [summary] = json.loads(result.stdout)["runs"]
        self.assertEqual(
            (summary["run"], summary["status"], summary["phase"], summary["continuation"]),
            ("execution-kernel", "PLANNING", "program_design", "PLANNING"),
        )
        self.assertFalse(summary["ready_for_execution"])
        self.assertEqual(
            {name: sha256(run / name) for name in before},
            before,
        )

    def test_inventory_surfaces_supported_interrupted_run_recovery(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        self.configure_external_root(planning_root)

        uninitialized = planning_root / "uninitialized"
        uninitialized.mkdir()
        uninitialized_config = run_config()
        uninitialized_config.update(
            {
                "run": "uninitialized",
                "run_path": "uninitialized",
                "goal": "Resume intake initialization",
                "planning_root": {
                    "source": "artifacts.planning_root",
                    "mode": "external",
                    "path": str(planning_root),
                },
            }
        )
        (uninitialized / "run.yaml").write_text(
            yaml.safe_dump(uninitialized_config, sort_keys=False), encoding="utf-8"
        )

        handoff = planning_root / "handoff"
        handoff.mkdir()
        handoff_config = run_config()
        handoff_config.update(
            {
                "version": 2,
                "run": "handoff",
                "run_path": "handoff",
                "goal": "Recover planning handoff",
                "planning_root": {
                    "source": "artifacts.planning_root",
                    "mode": "external",
                    "path": str(planning_root),
                },
                "system_design_participation": None,
                "stages": ["program_design", "tickets", "execute"],
            }
        )
        handoff_config["gates"].pop("discovery")
        handoff_config["gates"]["program_design"] = {"authority": "AGENT_REVIEW"}
        handoff_config["gates"]["tickets"] = {"authority": "HUMAN"}
        handoff_config["recommendation"]["gates"] = handoff_config["gates"]
        (handoff / "run.yaml").write_text(
            yaml.safe_dump(handoff_config, sort_keys=False), encoding="utf-8"
        )
        initialized = initialize_cli(handoff)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        before = {
            "uninitialized": sha256(uninitialized / "run.yaml"),
            "handoff-run": sha256(handoff / "run.yaml"),
            "handoff-control": sha256(handoff / "control.json"),
        }

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 0, result.stderr)
        rows = {row["run"]: row for row in json.loads(result.stdout)["runs"]}
        self.assertEqual(
            (rows["uninitialized"]["status"], rows["uninitialized"]["phase"], rows["uninitialized"]["continuation"]),
            ("INTERRUPTED", "discovery", "INITIALIZE"),
        )
        self.assertEqual(
            (rows["handoff"]["status"], rows["handoff"]["phase"], rows["handoff"]["continuation"]),
            ("PLANNING", "program_design", "HANDOFF_REQUIRED"),
        )
        self.assertEqual(
            {
                "uninitialized": sha256(uninitialized / "run.yaml"),
                "handoff-run": sha256(handoff / "run.yaml"),
                "handoff-control": sha256(handoff / "control.json"),
            },
            before,
        )
        self.assertFalse((handoff / "planning-control.json").exists())

    def test_invalid_run_is_diagnostic_and_never_exposed_as_valid(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        self.configure_external_root(planning_root)
        run = self.initialize_discovery_run(planning_root)
        with (run / "run.yaml").open("a", encoding="utf-8") as handle:
            handle.write("# tampered\n")
        before = {name: (run / name).read_bytes() for name in ("run.yaml", "control.json")}

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["verdict"], "PARTIAL")
        self.assertEqual(report["runs"], [])
        self.assertEqual(
            report["gaps"],
            [
                {
                    "code": "invalid_run",
                    "problem": "demo: base run.yaml byte hash mismatch",
                    "resume_action": "restore the accepted run.yaml bytes or start a corrected new run",
                    "run": "demo",
                }
            ],
        )
        self.assertEqual(
            {name: (run / name).read_bytes() for name in before},
            before,
        )

    def test_invalid_run_does_not_poison_valid_unrelated_run(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        self.configure_external_root(planning_root)
        invalid = self.initialize_discovery_run(planning_root, slug="invalid")
        valid = self.initialize_discovery_run(planning_root, slug="valid")
        valid_before = {
            "run.yaml": sha256(valid / "run.yaml"),
            "control.json": sha256(valid / "control.json"),
        }
        with (invalid / "run.yaml").open("a", encoding="utf-8") as handle:
            handle.write("# tampered\n")

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["verdict"], "PARTIAL")
        self.assertEqual([row["run"] for row in report["runs"]], ["valid"])
        self.assertEqual(report["gaps"][0]["run"], "invalid")
        self.assertEqual(report["gaps"][0]["code"], "invalid_run")
        self.assertEqual(
            {
                "run.yaml": sha256(valid / "run.yaml"),
                "control.json": sha256(valid / "control.json"),
            },
            valid_before,
        )

    def test_ready_inventory_exposes_exact_accepted_graph_and_ticket_ids_without_execution(self):
        planning_root = self.root / "planning"
        planning_root.mkdir()
        repository = self.root / "repository"
        baseline = create_repository(repository, "accepted ticket baseline\n")
        self.configure_external_root(planning_root, bindings={"fixture": str(repository)})
        run = planning_root / "demo"
        run.mkdir()
        config = run_config()
        config.update(
            {
                "version": 2,
                "system_design_participation": None,
                "planning_root": {
                    "source": "artifacts.planning_root",
                    "mode": "external",
                    "path": str(planning_root),
                },
                "stages": ["tickets", "execute"],
                "gates": {"tickets": {"authority": "AGENT_REVIEW"}},
                "repos": [{"repository": "fixture", "baseline": baseline}],
            }
        )
        config["recommendation"]["gates"] = config["gates"]
        (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        initialized = initialize_cli(run)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        planning_initialized = run_planning_cli(
            "initialize", "--run", run, env=self.environment()
        )
        self.assertEqual(planning_initialized.returncode, 0, planning_initialized.stderr)
        planning = json.loads((run / "planning-control.json").read_text(encoding="utf-8"))
        anchor = planning["stage0_anchor"]
        source = {
            "kind": "stage0",
            "artifact": "run.yaml",
            "sha256": anchor["base_run_sha256"],
            "effective_config_hash": anchor["effective_config_hash"],
            "effective_config_revision": anchor["effective_config_revision"],
        }
        manifest_path = write_ticket_graph(run, [source])
        review_path = write_ticket_review(run, policy="AGENT_REVIEW")
        accepted = run_planning_cli(
            "advance", "--run", run, "--stage", "tickets",
            "--review", review_path.relative_to(run), "--date", "2026-08-24",
            env=self.environment(),
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        before = {
            name: sha256(run / name)
            for name in ("run.yaml", "control.json", "planning-control.json", "50-ticket-graph.json")
        }

        result = run_cli("inventory", "--cwd", self.cwd, cwd=self.cwd, env=self.environment())

        self.assertEqual(result.returncode, 0, result.stderr)
        [summary] = json.loads(result.stdout)["runs"]
        self.assertEqual(summary["status"], "READY_FOR_EXECUTION")
        self.assertTrue(summary["ready_for_execution"])
        self.assertEqual(summary["continuation"], "READY_FOR_EXECUTION")
        self.assertEqual(
            summary["accepted_graph"],
            {
                "version": 1,
                "sha256": sha256(manifest_path),
                "ticket_ids": ["demo-01"],
            },
        )
        self.assertEqual(summary["accepted_boundaries"], ["tickets"])
        self.assertNotIn("execution", summary)
        self.assertNotIn("ticket_ready", summary)
        self.assertEqual(
            {name: sha256(run / name) for name in before},
            before,
        )


class AtlasGazetteerSkillContractTest(unittest.TestCase):
    @property
    def skill_path(self):
        return ROOT / "plugins" / "atlas" / "skills" / "gazetteer" / "SKILL.md"

    @property
    def agent_path(self):
        return ROOT / "plugins" / "atlas" / "skills" / "gazetteer" / "agents" / "openai.yaml"

    def test_gazetteer_is_the_discoverable_public_front_door(self):
        self.assertTrue(self.skill_path.is_file())
        self.assertTrue(self.agent_path.is_file())
        skill = self.skill_path.read_text(encoding="utf-8")
        _, raw_frontmatter, body = skill.split("---", 2)
        frontmatter = yaml.safe_load(raw_frontmatter)
        agent = yaml.safe_load(self.agent_path.read_text(encoding="utf-8"))
        self.assertEqual(frontmatter["name"], "gazetteer")
        self.assertNotEqual(frontmatter.get("disable-model-invocation"), True)
        self.assertIn("canonical user-facing entry point", body)
        self.assertIn("Gazetteer may decide which safe Atlas entry point applies", body)
        self.assertIn("It never decides workflow truth", body)
        self.assertEqual(agent["policy"]["allow_implicit_invocation"], True)
        self.assertEqual(agent["interface"]["display_name"], "Atlas Gazetteer")
        self.assertIn("authoritative Atlas state", agent["interface"]["default_prompt"])

        for sibling in sorted((ROOT / "plugins" / "atlas" / "skills").iterdir()):
            if not sibling.is_dir() or sibling.name == "gazetteer":
                continue
            sibling_text = (sibling / "SKILL.md").read_text(encoding="utf-8")
            _, sibling_frontmatter, _ = sibling_text.split("---", 2)
            sibling_metadata = yaml.safe_load(sibling_frontmatter)
            sibling_agent = yaml.safe_load(
                (sibling / "agents" / "openai.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(
                sibling_metadata.get("disable-model-invocation"),
                True,
                f"{sibling.name} must resist accidental model invocation",
            )
            self.assertEqual(
                sibling_agent["policy"]["allow_implicit_invocation"],
                False,
                f"{sibling.name} must remain non-implicit",
            )

    def test_gazetteer_resolves_intent_and_runs_without_creating_authority(self):
        body = self.skill_path.read_text(encoding="utf-8")
        required = (
            'python3 "<atlas-plugin-root>/tools/atlas_gazetteer.py" inventory --cwd "<current-working-directory>"',
            "NEW_GOAL",
            "CONTINUE",
            "INSPECT",
            "ACT_ON_NAMED_WORK",
            "PROVIDE_JUDGMENT",
            "exact run explicitly named by the user",
            "session-local conversational focus",
            "exactly one structurally relevant active run",
            "present a concise candidate selection",
            "Semantic similarity may rank or suggest candidates; it never silently binds",
            "return to the original request after setup",
            "Never tell a normal user to invoke `setup-atlas` or `start-run`",
            "offer one natural-language continue affordance through Gazetteer",
            "pass the fuzzy goal to `atlas:start-run` only for new intake",
            "carry run identity and explicit new user judgments, not the original fuzzy prompt",
            "Status and orientation are read-only",
            "Treat `PARTIAL` as an inventory with isolated diagnostics",
            "do not let an unrelated run or binding diagnostic block orientation",
            "If the explicitly named, session-focused, or otherwise selected run appears in `gaps[].run`",
        )
        for clause in required:
            with self.subTest(clause=clause):
                self.assertIn(clause, body)

    def test_gazetteer_continuity_preserves_authority_and_human_boundaries(self):
        plugin = ROOT / "plugins" / "atlas"
        gazetteer = self.skill_path.read_text(encoding="utf-8")
        start = (plugin / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")
        discovery = (plugin / "skills" / "discovery" / "SKILL.md").read_text(encoding="utf-8")
        control = (plugin / "skills" / "control-run" / "SKILL.md").read_text(encoding="utf-8")
        gazetteer_clauses = (
            "`INTERACTIVE` is the default continuation posture",
            "`AUTO_CONTINUE` only from an explicit current user request or supported host posture",
            "Never derive continuation posture from `governance: autonomous`",
            "new goal → `atlas:start-run`",
            "existing planning run → `atlas:start-run`",
            "Gazetteer never invokes Discovery or a downstream producer directly",
            "Every existing run enters `atlas:start-run` first",
            "After the entered owner returns, re-run inventory and re-read authoritative state",
            "Mechanical internal handoffs continue in either posture",
            "Prefer the host's safe nested skill invocation mechanism",
            "load the exact installed sibling `SKILL.md` as the current owner procedure",
            "calibrated procedure-load fallback",
            "A required HUMAN judgment always stops and asks",
            "A HUMAN gate stops at its approval surface after the selected producer has prepared its candidate",
            "does not block entry into that already-selected producer",
            "`BLOCKED` or `DESIGN_BLOCKED` always stops",
            "`READY_FOR_EXECUTION`",
            "no first-party execution owner exists",
            "Continuation is never acceptance or approval",
            "prefer the strongest configured reasoning worker",
            "Never hard-code a provider or model name",
        )
        for clause in gazetteer_clauses:
            with self.subTest(clause=clause):
                self.assertIn(clause, gazetteer)
        start_clauses = (
            "invoke `atlas:discovery` internally",
            "Prefer the host's safe nested skill invocation mechanism",
            "load the exact installed sibling `SKILL.md` as the current owner procedure",
            "After Discovery and its internal Product Closure handoff return, re-read authoritative `control.json`",
            "invocation-local continuation posture",
            "must enter the next selected producer even when that producer's configured gate is HUMAN",
            "Never stop merely because the newly entered phase will eventually require HUMAN acceptance",
            "never converts continuation into approval",
        )
        for clause in start_clauses:
            with self.subTest(clause=clause):
                self.assertIn(clause, start)
        self.assertIn(
            "perform the exact named internal handoff to `atlas:control-run` without asking the user to issue a second routing command",
            discovery,
        )
        self.assertIn("return to the invoking continuation owner", discovery)
        self.assertIn("Return the freshly validated phase/status to the invoking continuation owner", control)
        self.assertIn("Do not invoke a downstream producer from `control-run`", control)

    def test_package_help_and_calibration_expose_gazetteer_as_the_start(self):
        plugin = ROOT / "plugins" / "atlas"
        readme = (plugin / "README.md").read_text(encoding="utf-8")
        manifests = [
            json.loads((plugin / "plugin.json").read_text(encoding="utf-8")),
            json.loads((plugin / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")),
        ]
        marketplace_paths = (
            ROOT / ".agents" / "plugins" / "marketplace.json",
            ROOT / ".github" / "plugin" / "marketplace.json",
        )
        marketplace_descriptions = []
        for path in marketplace_paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            [atlas] = [item for item in data["plugins"] if item["name"] == "atlas"]
            marketplace_descriptions.append(atlas["description"])
        calibration = (
            plugin / "skills" / "setup-atlas" / "references" / "installed-host-calibration.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Start here", readme)
        self.assertIn("**Gazetteer is Atlas's canonical entry point.**", readme)
        for example in (
            "/atlas:gazetteer Add cancellation support to queued jobs",
            "/atlas:gazetteer continue",
            "/atlas:gazetteer what's next?",
            "/atlas:gazetteer where are we on cancellation?",
        ):
            self.assertIn(example, readme)
        self.assertIn("## Internal/direct skills", readme)
        self.assertEqual(manifests[0]["description"], manifests[1]["description"])
        self.assertEqual(
            [manifests[0]["description"], *marketplace_descriptions],
            [manifests[0]["description"]] * 3,
        )
        self.assertIn("Gazetteer", manifests[0]["description"])
        self.assertIn("tools/atlas_gazetteer.py", calibration)
        self.assertIn("all six packaged CLIs", calibration)
        self.assertIn("`disable-model-invocation: true` is present on every internal/direct sibling", calibration)
        self.assertIn("On hosts that honor Atlas's `agents/openai.yaml` invocation policy", calibration)
        self.assertIn("implicit activation remains host policy", calibration)
        self.assertIn("Gazetteer is the documented canonical front door on every host", calibration)


if __name__ == "__main__":
    unittest.main()
