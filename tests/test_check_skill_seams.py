import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_skill_seams.py"
SPEC = importlib.util.spec_from_file_location("check_skill_seams", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
SEAMS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SEAMS)

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
SYSTEM_DESIGN_VIEWS = (
    "current-topology",
    "proposed-topology",
    "seam-ownership",
    "interface-contract",
    "lifecycle-sequence-data-flow",
    "schema-protocol",
    "failure-recovery",
    "open-decisions",
    "rejected-alternatives",
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


class SkillSeamHardeningTests(unittest.TestCase):
    def copy_plugin(self, root: Path) -> Path:
        plugin = root / "plugins" / "atlas"
        shutil.copytree(ROOT / "plugins" / "atlas", plugin)
        return plugin / "skills"

    def test_program_design_producer_metadata_and_inventory_are_exact(self):
        plugin = ROOT / "plugins" / "atlas"
        skill_path = plugin / "skills" / "program-design" / "SKILL.md"
        agent_path = plugin / "skills" / "program-design" / "agents" / "openai.yaml"
        readme_path = plugin / "README.md"

        self.assertTrue(skill_path.is_file())
        self.assertTrue(agent_path.is_file())
        agent = SEAMS.yaml.safe_load(agent_path.read_text(encoding="utf-8"))
        self.assertEqual(agent["interface"], {
            "display_name": "Atlas Program Design",
            "short_description": "Produce Stage 4 and hand it to planning control",
            "default_prompt": (
                "Use $program-design to produce the exact Atlas Program Design candidate "
                "and continue its internal control handoff."
            ),
        })
        self.assertFalse(agent["policy"]["allow_implicit_invocation"])
        skill = skill_path.read_text(encoding="utf-8")
        self.assertIn("name: program-design", skill)
        self.assertIn("disable-model-invocation: true", skill)
        readme = readme_path.read_text(encoding="utf-8")
        self.assertIn(
            "| `program-design` | Produce the exact Stage 4 candidate, record readiness, and continue the internal control handoff. |",
            readme,
        )

        findings = SEAMS.cross_skill_contracts(plugin / "skills")
        self.assertFalse([item for item in findings if item[0] == "cross"], findings)

    def test_program_design_inspects_actual_target_repository_before_drafting(self):
        plugin = ROOT / "plugins" / "atlas"
        skill_path = plugin / "skills" / "program-design" / "SKILL.md"
        skill = skill_path.read_text(encoding="utf-8")
        grounding = (
            "Before drafting anything, require a readable repository for every stable identity and prove the exact frozen baseline commit/tree is available"
        )
        self.assertIn(grounding, skill)
        self.assertLess(skill.index(grounding), skill.index("## 3. Produce the Stage 4 candidate"))
        self.assertIn("Inspect those frozen-baseline bytes for language and tooling conventions, relevant implementations, and tests", skill)
        self.assertIn("current HEAD and working-tree state only as drift/context", skill)
        self.assertIn("neither may silently replace the frozen baseline as design truth", skill)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(grounding, "Before drafting anything, reason about the target repository", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("repository grounding before drafting" in message for _, message in findings), findings)

    def test_program_design_selects_exactly_one_of_three_upstream_sources_from_selected_stages(self):
        plugin = ROOT / "plugins" / "atlas"
        skill_path = plugin / "skills" / "program-design" / "SKILL.md"
        skill = skill_path.read_text(encoding="utf-8")
        selection = (
            "Derive the applicable branch only from effective selected stages, never from candidate prose or artifact presence"
        )
        self.assertIn(selection, skill)
        self.assertIn("Read exactly one applicable upstream source and do not read either omitted source", skill)
        for clause in (
            "System Design selected: read exact accepted `30-system-design.md`",
            "System Design omitted and Product Closure selected: read exact accepted `20-prd.md`",
            "both upstream semantic boundaries omitted: read frozen effective Stage 0 `run.yaml` and its recorded effective configuration binding",
        ):
            self.assertIn(clause, skill)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(selection, "Choose a likely source from the candidate", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("exact three-source selection" in message for _, message in findings), findings)

    def test_program_design_candidate_template_is_exact_without_participation_or_html(self):
        plugin = ROOT / "plugins" / "atlas"
        skill = (plugin / "skills" / "program-design" / "SKILL.md").read_text(encoding="utf-8")
        template_path = plugin / "skills" / "program-design" / "references" / "program-design-file.md"
        self.assertTrue(template_path.is_file())
        template = template_path.read_text(encoding="utf-8")
        planning = (plugin / "tools" / "atlas_planning.py").read_text(encoding="utf-8")

        candidate_maps = [
            item for item in SEAMS.frontmatter_maps(template)
            if {"run", "version", "status", "gate_ready"}.issubset(item)
        ]
        self.assertEqual(len(candidate_maps), 1)
        self.assertEqual(set(candidate_maps[0]), set(SEAMS.assigned_literal(planning, "PROGRAM_DESIGN_FIELDS")))
        self.assertEqual(candidate_maps[0]["version"], 1)
        self.assertEqual(candidate_maps[0]["status"], "draft")
        self.assertIs(candidate_maps[0]["gate_ready"], True)
        headings = tuple(re.findall(r"(?m)^## ([^\n]+?)\s*$", template))
        self.assertEqual(headings, PROGRAM_DESIGN_SECTIONS)
        self.assertIn("references/program-design-file.md", skill)
        self.assertIn("cite every upstream commitment", skill)
        self.assertNotIn("participation:", (skill + template).lower())
        self.assertNotIn("40-program-design.html", (skill + template).lower())

        findings = SEAMS.cross_skill_contracts(plugin / "skills")
        self.assertFalse([item for item in findings if item[0] == "cross"], findings)

    def test_program_design_normal_path_owns_candidate_and_readiness_only(self):
        plugin = ROOT / "plugins" / "atlas"
        skill_path = plugin / "skills" / "program-design" / "SKILL.md"
        skill = skill_path.read_text(encoding="utf-8")
        ownership = (
            "On the normal path, write only canonical `40-program-design.md` candidate/readiness bytes"
        )
        self.assertIn(ownership, skill)
        self.assertIn("never create or modify `reviews/program-design-v1.json`", skill)
        self.assertIn("never write `planning-control.json`", skill)
        self.assertIn("never rewrite an upstream artifact", skill)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(ownership, "Write the Program Design outputs", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("candidate-only ownership" in message for _, message in findings), findings)

    def test_program_design_producer_design_blocked_is_structured_read_only_and_pre_readiness(self):
        plugin = ROOT / "plugins" / "atlas"
        skill_path = plugin / "skills" / "program-design" / "SKILL.md"
        skill = skill_path.read_text(encoding="utf-8")
        stop = (
            "Before writing candidate or readiness bytes, return structured read-only `DESIGN_BLOCKED` and stop"
        )
        self.assertIn(stop, skill)
        for field in ("upstream_source", "upstream_issue", "resume_boundary", "resume_action"):
            self.assertIn(f"`{field}`", skill)
        self.assertIn("nonempty `upstream_issue`", skill)
        self.assertIn("both equal the actual selected source-binding kind", skill)
        self.assertIn("smallest upstream decision or change required", skill)
        self.assertIn("creates no review file", skill)
        self.assertIn("does not rewrite any upstream artifact", skill)
        self.assertIn("does not mutate planning state", skill)
        self.assertIn("Reviewer-discovered `DESIGN_BLOCKED` belongs only in a fresh `reviews/program-design-v1.json`", skill)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(stop, "Return `DESIGN_BLOCKED` when appropriate", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("pre-readiness DESIGN_BLOCKED stop" in message for _, message in findings), findings)

    def test_program_design_mechanical_pass_performs_one_exact_internal_handoff(self):
        plugin = ROOT / "plugins" / "atlas"
        skill_path = plugin / "skills" / "program-design" / "SKILL.md"
        skill = skill_path.read_text(encoding="utf-8")
        handoff = (
            "After mechanical `PASS`, perform the exact named internal handoff to `atlas:control-planning`"
        )
        self.assertIn(handoff, skill)
        self.assertEqual(skill.count("atlas:control-planning"), 1)
        self.assertIn("without asking the user to issue a second routing command", skill)
        self.assertIn("unchanged `<run-directory>` and explicit stage `program_design`", skill)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(handoff, "After mechanical `PASS`, report readiness", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("exact internal control-planning handoff" in message for _, message in findings), findings)

    def test_control_planning_supports_only_two_explicit_stages_and_loads_program_authority(self):
        plugin = ROOT / "plugins" / "atlas"
        control_path = plugin / "skills" / "control-planning" / "SKILL.md"
        agent_path = plugin / "skills" / "control-planning" / "agents" / "openai.yaml"
        control = control_path.read_text(encoding="utf-8")
        self.assertIn("supports exactly the explicit stages `system_design` and `program_design`", control)
        self.assertIn("never discovers, infers, or reroutes a stage", control)
        self.assertIn("references/system-design-authority.md", control)
        self.assertIn("references/program-design-authority.md", control)
        self.assertIn("## Program Design branch", control)
        self.assertIn("configured `AGENT_REVIEW` or `HUMAN` authority", control)
        self.assertIn("fresh exact PASS review", control)
        self.assertIn("reviews/program-design-v1.json", control)
        for command in (
            'check --run "<run-directory>" --stage program_design',
            'advance --run "<run-directory>" --stage program_design --review reviews/program-design-v1.json --date "<YYYY-MM-DD>"',
            'advance --run "<run-directory>" --stage program_design --review reviews/program-design-v1.json --approval human --date "<YYYY-MM-DD>"',
        ):
            self.assertIn(command, control)
        agent = SEAMS.yaml.safe_load(agent_path.read_text(encoding="utf-8"))
        self.assertEqual(agent["interface"]["short_description"], "Apply configured System or Program Design authority once")
        self.assertIn("explicit system_design or program_design boundary once", agent["interface"]["default_prompt"])

        findings = SEAMS.cross_skill_contracts(plugin / "skills")
        self.assertFalse([item for item in findings if item[0] == "cross"], findings)

    def test_control_planning_runs_only_the_check_for_the_explicit_stage(self):
        plugin = ROOT / "plugins" / "atlas"
        control_path = plugin / "skills" / "control-planning" / "SKILL.md"
        control = control_path.read_text(encoding="utf-8")
        selector = "Run exactly one mechanical check selected by the explicit stage; never run both commands"
        self.assertIn(selector, control)
        self.assertIn(
            "For explicit stage `system_design`, run only:", control
        )
        self.assertIn(
            "For explicit stage `program_design`, run only:", control
        )

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "control-planning" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(selector, "Run the mechanical checks below", 1),
                encoding="utf-8",
            )
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(
                any("explicit-stage-only check selection" in message for _, message in findings),
                findings,
            )

    def test_program_design_authority_dimensions_are_bound_to_the_controller(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            reference = (
                skills / "control-planning" / "references" / "program-design-authority.md"
            )
            source = reference.read_text(encoding="utf-8")
            self.assertIn("testability_and_compilation_readiness", source)
            reference.write_text(
                source.replace(
                    "testability_and_compilation_readiness",
                    "drifted_stage4_dimension",
                    1,
                ),
                encoding="utf-8",
            )

            findings = SEAMS.cross_skill_contracts(skills)

            self.assertTrue(
                any(
                    "Program Design semantic review dimensions" in message
                    for _, message in findings
                ),
                findings,
            )

    def test_program_design_authority_defining_filename_is_bound_to_the_controller(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            reference = (
                skills / "control-planning" / "references" / "program-design-authority.md"
            )
            source = reference.read_text(encoding="utf-8")
            exact = "`reviews/program-design-v1.json` is the one exact run-relative envelope."
            self.assertIn(exact, source)
            reference.write_text(
                source.replace(
                    exact,
                    "`reviews/drifted-program-design.json` is the one exact run-relative envelope.",
                    1,
                ),
                encoding="utf-8",
            )

            findings = SEAMS.cross_skill_contracts(skills)

            self.assertTrue(
                any("Program Design authority filename" in message for _, message in findings),
                findings,
            )

    def test_start_run_routes_program_design_internally_and_stops_honestly_at_tickets(self):
        plugin = ROOT / "plugins" / "atlas"
        start_path = plugin / "skills" / "start-run" / "SKILL.md"
        start = start_path.read_text(encoding="utf-8")
        for clause in (
            "If validated planning phase is `system_design`, invoke `atlas:system-design` internally",
            "If validated planning phase is `program_design`, invoke `atlas:program-design` internally",
            "If validated planning phase is `tickets`, stop loudly",
            "no first-party ticket producer exists",
            "Preserve the existing Product Closure and System Design paths",
        ):
            self.assertIn(clause, start)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "start-run" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("invoke `atlas:program-design` internally", "report Program Design", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("Program Design route and tickets stop" in message for _, message in findings), findings)

    def test_program_design_packaged_commands_are_caller_cwd_independent(self):
        plugin = ROOT / "plugins" / "atlas"
        program_path = plugin / "skills" / "program-design" / "SKILL.md"
        control_path = plugin / "skills" / "control-planning" / "SKILL.md"
        program = program_path.read_text(encoding="utf-8")
        control = control_path.read_text(encoding="utf-8")
        resolver = "it is the third parent of this file (`SKILL.md` → `program-design/` → `skills/` → plugin root)"
        self.assertIn(resolver, program)
        self.assertEqual(program_path.parents[2], plugin)
        check = 'python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage program_design'
        self.assertIn(check, program)
        self.assertIn(check, control)
        for command in (
            'python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage program_design --review reviews/program-design-v1.json --date "<YYYY-MM-DD>"',
            'python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage program_design --review reviews/program-design-v1.json --approval human --date "<YYYY-MM-DD>"',
        ):
            self.assertIn(command, control)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(resolver, "find the plugin root", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("caller-CWD-independent Program Design skill root" in message for _, message in findings), findings)

    def test_readme_exposes_the_single_program_design_producer_and_stage4_flow(self):
        plugin = ROOT / "plugins" / "atlas"
        readme_path = plugin / "README.md"
        readme = readme_path.read_text(encoding="utf-8")
        self.assertIn("First-party Stage 0–4 skills", readme)
        self.assertIn(
            "| `program-design` | Produce the exact Stage 4 candidate, record readiness, and continue the internal control handoff. |",
            readme,
        )
        self.assertIn("tickets remain intentionally unsupported", readme)
        self.assertNotIn("Program Design, ticket compilation/acceptance", readme)

    def test_readme_protects_automatic_program_design_orchestration_not_user_routing(self):
        plugin = ROOT / "plugins" / "atlas"
        readme = (plugin / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("The user invokes `atlas:program-design` once", readme)
        start = (plugin / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")
        program = (plugin / "skills" / "program-design" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("invoke `atlas:program-design` internally", start)
        self.assertIn("If validated planning phase is `tickets`, stop loudly", start)
        self.assertIn("exact named internal handoff to `atlas:control-planning`", program)
        self.assertIn("without asking the user to issue a second routing command", program)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "start-run" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace("invoke `atlas:program-design` internally", "report Program Design", 1),
                encoding="utf-8",
            )
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("Program Design route and tickets stop" in message for _, message in findings), findings)

    def test_operational_runbooks_are_owned_and_reachable_without_new_stage_skills(self):
        plugin = ROOT / "plugins" / "atlas"
        setup = (plugin / "skills" / "setup-atlas" / "SKILL.md").read_text(encoding="utf-8")
        start = (plugin / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")
        program = (plugin / "skills" / "program-design" / "SKILL.md").read_text(encoding="utf-8")
        control = (plugin / "skills" / "control-planning" / "SKILL.md").read_text(encoding="utf-8")
        commissioning = plugin / "skills" / "setup-atlas" / "references" / "installed-host-calibration.md"
        blocked = plugin / "references" / "program-design-blocked.md"

        self.assertTrue(commissioning.is_file())
        self.assertTrue(blocked.is_file())
        self.assertIn("references/installed-host-calibration.md", setup)
        self.assertIn("description: Create or resume an Atlas run", start)
        self.assertIn("../../references/program-design-blocked.md", program)
        self.assertIn("../../references/program-design-blocked.md", control)
        commissioning_text = commissioning.read_text(encoding="utf-8")
        blocked_text = blocked.read_text(encoding="utf-8")
        setup_agent = SEAMS.yaml.safe_load(
            (plugin / "skills" / "setup-atlas" / "agents" / "openai.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            setup_agent["interface"]["short_description"],
            "Configure or verify Atlas on this machine",
        )
        start_agent = SEAMS.yaml.safe_load(
            (plugin / "skills" / "start-run" / "agents" / "openai.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            start_agent["interface"]["short_description"],
            "Create or resume an Atlas run from authoritative state",
        )
        for clause in (
            "installation bytes",
            "deterministic runtime readiness",
            "host recognition",
            "skill discovery",
            "procedure completion",
            "cross-skill handoff",
            "dated calibration",
            "PASS/FAIL/UNVERIFIED",
            "session.skills_loaded",
            "tools/atlas_planning.py",
            "using that same launcher",
            "Without this run plus oracle, procedure completion is `UNVERIFIED`",
            "without changing a byte-equality PASS",
        ):
            self.assertIn(clause, commissioning_text)
        for clause in (
            "producer pre-readiness",
            "reviewer evidence",
            "`planning-control.json` remains `PENDING`",
            "no supported reopen or replacement-acceptance path",
            "frozen repository baseline cannot be located and read",
            "does not decide where a future repository binding lives",
            "Do not prescribe a `run.yaml` field, Stage 0 amendment/effective-configuration field",
        ):
            self.assertIn(clause, blocked_text)

    def test_least_confident_decisions_are_resolved_before_stage5(self):
        plugin = ROOT / "plugins" / "atlas"
        program = (plugin / "skills" / "program-design" / "SKILL.md").read_text(encoding="utf-8")
        template = (
            plugin / "skills" / "program-design" / "references" / "program-design-file.md"
        ).read_text(encoding="utf-8")
        authority = (
            plugin / "skills" / "control-planning" / "references" / "program-design-authority.md"
        ).read_text(encoding="utf-8")
        for text in (program, template, authority):
            self.assertIn("Stage 5 receives no design question it must answer", text)
        self.assertIn("settled Stage 4 decisions with bounded residual uncertainty", program)
        self.assertIn("unresolved local code-shape choice is `BLOCKED`", authority)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "references" / "program-design-file.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "Stage 5 receives no design question it must answer",
                    "Stage 5 may settle remaining design questions",
                    1,
                ),
                encoding="utf-8",
            )
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("resolved-only Stage 4 decisions" in message for _, message in findings), findings)

    def test_program_design_resumes_exact_frozen_boundary_without_participation(self):
        plugin = ROOT / "plugins" / "atlas"
        skill = (plugin / "skills" / "program-design" / "SKILL.md").read_text(encoding="utf-8")
        for clause in (
            "Read immutable `run.yaml`, authoritative Stage 0 `control.json`, and `planning-control.json`",
            "Require current phase `program_design`, gate `PENDING`, and exact configured authority `AGENT_REVIEW` or `HUMAN`",
            "Program Design never asks a participation question",
        ):
            self.assertIn(clause, skill)
        self.assertNotIn("HUMAN_IF_CHANGED", skill)
        self.assertNotRegex(skill, r"(?m)^.*Program Design.*\bAUTO\b.*$")

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("Program Design never asks a participation question", "Participation is optional", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("frozen boundary without participation" in message for _, message in findings), findings)

    def test_program_design_agent_metadata_structure_drift_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "program-design" / "agents" / "openai.yaml"
            text = path.read_text(encoding="utf-8")
            self.assertIn("interface:\n", text)
            path.write_text(text.replace("interface:\n", "stale_interface:\n", 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("Program Design model metadata" in message for _, message in findings), findings)

    def test_system_design_authority_reference_binds_exact_schema_dimensions_and_matrix(self):
        plugin = ROOT / "plugins" / "atlas"
        reference_path = plugin / "skills" / "control-planning" / "references" / "system-design-authority.md"
        self.assertTrue(reference_path.is_file())
        reference = reference_path.read_text(encoding="utf-8")
        control = (plugin / "skills" / "control-planning" / "SKILL.md").read_text(encoding="utf-8")
        planning = (plugin / "tools" / "atlas_planning.py").read_text(encoding="utf-8")

        for dimension in SYSTEM_DESIGN_DIMENSIONS:
            self.assertIn(dimension, reference)
            self.assertIn(dimension, planning)
        for field in (
            "version", "run", "stage", "policy", "candidate_version", "candidate_sha256",
            "repository_baselines", "materiality", "semantic_review",
        ):
            self.assertIn(f'"{field}"', reference)
        self.assertIn("reviews/system-design-v1.json", reference)
        self.assertIn("fresh read-only classifier", control)
        self.assertIn("distinct fresh semantic reviewer", control)
        self.assertIn("invoker assembles", control.lower())
        for command in (
            '--approval human --date "<YYYY-MM-DD>"',
            '--review reviews/system-design-v1.json --date "<YYYY-MM-DD>"',
            '--review reviews/system-design-v1.json --approval human --date "<YYYY-MM-DD>"',
        ):
            self.assertIn(command, control)

        findings = SEAMS.cross_skill_contracts(plugin / "skills")
        self.assertFalse([item for item in findings if item[0] == "cross"], findings)

    def test_system_design_authority_schema_dimension_filename_and_matrix_drift_are_detected(self):
        cases = (
            ("dimension", "responsibilities_and_system_seams", "responsibilities_and_seams", "dimensions"),
            ('schema', '  "policy": "HUMAN_IF_CHANGED",\n', "", "envelope"),
            ("filename", "reviews/system-design-v1.json", "reviews/system-design-v2.json", "filename"),
            (
                "matrix",
                'python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --date "<YYYY-MM-DD>"\n',
                "",
                "authority-matrix",
            ),
        )
        for name, old, new, expected in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                skills = self.copy_plugin(Path(td))
                target = (
                    skills / "control-planning" / "SKILL.md"
                    if name == "matrix"
                    else skills / "control-planning" / "references" / "system-design-authority.md"
                )
                text = target.read_text(encoding="utf-8")
                self.assertIn(old, text)
                target.write_text(
                    text.replace(old, new) if name == "filename" else text.replace(old, new, 1),
                    encoding="utf-8",
                )

                findings = SEAMS.cross_skill_contracts(skills)
                messages = "\n".join(message for kind, message in findings if kind == "cross")

                self.assertIn(expected, messages.lower())

    def test_system_design_and_control_planning_form_one_explicit_internal_handoff(self):
        plugin = ROOT / "plugins" / "atlas"
        system_path = plugin / "skills" / "system-design" / "SKILL.md"
        control_path = plugin / "skills" / "control-planning" / "SKILL.md"
        template_path = plugin / "skills" / "system-design" / "references" / "system-design-file.md"
        system = system_path.read_text(encoding="utf-8")
        control = control_path.read_text(encoding="utf-8")
        template = template_path.read_text(encoding="utf-8")

        self.assertTrue(70 <= len(system.splitlines()) <= 110)
        self.assertTrue(70 <= len(control.splitlines()) <= 110)
        for text in (system, control):
            self.assertIn("disable-model-invocation: true", text)
            self.assertIn("third parent of this file", text)
            self.assertIn('python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design', text)
        self.assertIn("reads the frozen value and never asks again", system)
        self.assertIn("agent_led", system)
        self.assertIn("co_design", system)
        self.assertIn("Slice 2", system)
        self.assertIn("exact named internal handoff to `atlas:control-planning`", system)
        self.assertIn("without asking the user to issue a second command", system)
        self.assertIn("writes readiness, never acceptance", system)
        self.assertIn("never routes", control)
        self.assertIn("never synthesizes", control)
        self.assertIn("never edits", control)
        self.assertIn("never grades prose", control)
        self.assertIn("explicit human approval", control)
        self.assertIn("calls `advance` exactly once", control)
        self.assertIn('advance --run "<run-directory>" --stage system_design --approval human --date "<YYYY-MM-DD>"', control)
        self.assertIn("re-read `planning-control.json`", control)
        self.assertIn("AGENT_REVIEW", control)
        self.assertIn("HUMAN_IF_CHANGED", control)
        self.assertIn("Slice 2", control)
        self.assertNotIn("boundary-review", system + control + template)
        self.assertNotRegex(template.lower(), r"\b(must|never|required)\b")
        for heading in SYSTEM_DESIGN_SECTIONS:
            self.assertIn(f"## {heading}", template)
        for agent in (
            plugin / "skills" / "system-design" / "agents" / "openai.yaml",
            plugin / "skills" / "control-planning" / "agents" / "openai.yaml",
        ):
            self.assertIn("allow_implicit_invocation: false", agent.read_text(encoding="utf-8"))

    def test_model_metadata_describes_current_participation_and_authority_without_slice1_priming(self):
        plugin = ROOT / "plugins" / "atlas"
        system_path = plugin / "skills" / "system-design" / "agents" / "openai.yaml"
        control_path = plugin / "skills" / "control-planning" / "agents" / "openai.yaml"
        system_data = SEAMS.yaml.safe_load(system_path.read_text(encoding="utf-8"))
        control_data = SEAMS.yaml.safe_load(control_path.read_text(encoding="utf-8"))
        system_prompt = system_data["interface"]["default_prompt"]
        control_text = " ".join(control_data["interface"].values())

        self.assertIn("frozen agent_led or co_design participation", system_prompt)
        self.assertIn("candidate", system_prompt)
        self.assertIn("internal control handoff", system_prompt)
        self.assertNotIn("current agent-led", system_prompt.lower())
        self.assertIn(
            "configured HUMAN, AGENT_REVIEW, or HUMAN_IF_CHANGED System Design boundary once",
            control_text,
        )
        self.assertNotIn("HUMAN handoff", control_text)
        self.assertFalse(system_data["policy"]["allow_implicit_invocation"])
        self.assertFalse(control_data["policy"]["allow_implicit_invocation"])

        cases = (
            (
                "system-design/agents/openai.yaml",
                "frozen agent_led or co_design participation",
                "current agent-led participation",
                "stale Slice 1 agent-led",
            ),
            (
                "control-planning/agents/openai.yaml",
                "configured HUMAN, AGENT_REVIEW, or HUMAN_IF_CHANGED System Design boundary once",
                "current HUMAN System Design boundary once",
                "stale Slice 1 HUMAN-only",
            ),
        )
        for relative, old, new, expected in cases:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as td:
                skills = self.copy_plugin(Path(td))
                path = skills / relative
                text = path.read_text(encoding="utf-8")
                self.assertIn(old, text)
                path.write_text(text.replace(old, new, 1), encoding="utf-8")
                findings = SEAMS.cross_skill_contracts(skills)
                self.assertTrue(any(expected in message for _, message in findings), findings)

    def test_system_design_board_renderer_and_skill_contracts_are_bound(self):
        plugin = ROOT / "plugins" / "atlas"
        renderer_path = plugin / "tools" / "render_system_design.py"
        board_path = plugin / "skills" / "system-design" / "references" / "system-design-board.md"
        system = (plugin / "skills" / "system-design" / "SKILL.md").read_text(encoding="utf-8")
        control = (plugin / "skills" / "control-planning" / "SKILL.md").read_text(encoding="utf-8")
        readme = (plugin / "README.md").read_text(encoding="utf-8")

        self.assertTrue(renderer_path.is_file())
        self.assertTrue(board_path.is_file())
        renderer = renderer_path.read_text(encoding="utf-8")
        board = board_path.read_text(encoding="utf-8")
        for command in (
            'render_system_design.py" write --run "<run-directory>" --draft .30-system-design.next.md',
            'render_system_design.py" render --run "<run-directory>"',
            'render_system_design.py" verify --run "<run-directory>"',
        ):
            self.assertIn(command, system)
        self.assertIn("reads the frozen value and never asks again", system)
        self.assertIn("one system seam or decision at a time", system)
        self.assertIn("two or three concrete alternatives", system)
        self.assertIn("strongest counterargument", system)
        self.assertIn("exact named internal handoff to `atlas:control-planning`", system)
        self.assertIn("agent_led", control)
        self.assertIn("co_design", control)
        self.assertIn("explicit human approval", control)
        self.assertIn("never treat conversational agreement as approval", control.lower())
        self.assertIn("Slice 2B", readme)
        self.assertIn("co_design", readme)
        self.assertIn("render_system_design.py", readme)
        self.assertIn("non-authoritative", readme)
        self.assertIn("AGENT_REVIEW", readme)
        self.assertIn("HUMAN_IF_CHANGED", readme)
        self.assertNotIn("boundary-review", system + control + board)
        for label in SYSTEM_DESIGN_VIEWS:
            self.assertIn(label, renderer)
            self.assertIn(label, board)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            renderer_copy = skills.parent / "tools" / "render_system_design.py"
            renderer_copy.write_text(
                renderer_copy.read_text(encoding="utf-8").replace("current-topology", "current-shape"),
                encoding="utf-8",
            )
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("System Design board views" in message for _, message in findings), findings)

    def test_downstream_system_design_template_and_internal_handoff_drift_are_detected(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            template = skills / "system-design" / "references" / "system-design-file.md"
            template.write_text(
                template.read_text(encoding="utf-8").replace("gate_ready: false\n", "", 1),
                encoding="utf-8",
            )
            producer = skills / "system-design" / "SKILL.md"
            producer.write_text(
                producer.read_text(encoding="utf-8").replace(
                    "atlas:control-planning", "atlas:control-run"
                ),
                encoding="utf-8",
            )

            findings = SEAMS.cross_skill_contracts(skills)
            messages = "\n".join(message for _, message in findings)

            self.assertIn("System Design candidate schema", messages)
            self.assertIn("internal control-planning handoff", messages)

    def test_discovery_candidate_template_field_deletion_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            reference = skills / "discovery" / "references" / "run-layout.md"
            reference.write_text(
                reference.read_text(encoding="utf-8").replace("version: 1\n", "", 1),
                encoding="utf-8",
            )
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("decision-log schema" in message for _, message in findings))

    def test_prd_candidate_template_field_deletion_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            reference = skills / "discovery" / "references" / "prd-file.md"
            reference.write_text(
                reference.read_text(encoding="utf-8").replace("gate_ready: false\n", "", 1),
                encoding="utf-8",
            )
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("discovery candidate schema" in message for _, message in findings))

    def test_controller_and_renderer_version_contract_cannot_drift(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            renderer = skills.parent / "tools" / "render_prd.py"
            renderer.write_text(
                renderer.read_text(encoding="utf-8").replace(
                    'RENDERER_VERSION = "1.0.0"', 'RENDERER_VERSION = "9.9.9"'
                ),
                encoding="utf-8",
            )

            findings = SEAMS.cross_skill_contracts(skills)

            self.assertTrue(any("renderer version" in message.lower() for _, message in findings))

    def test_control_projection_template_requires_base_hash_and_acceptance_bindings(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            reference = skills / "start-run" / "references" / "state-file.md"
            text = reference.read_text(encoding="utf-8")
            text = text.replace('  "base_run_sha256": "<sha256>",\n', "")
            text = text.replace(
                '  "blocked_reason": null,\n  "acceptances": {\n    "discovery": null\n  }\n',
                '  "blocked_reason": null\n',
            )
            reference.write_text(text, encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("base_run_sha256" in message for _, message in findings))
            self.assertTrue(any("acceptances" in message for _, message in findings))

    def test_boundary_review_schema_field_deletion_is_detected(self):
        for needle, expected in (
            ('  "run": "<feature-slug>",\n', "boundary review schema"),
            ('      "code": "<stable-gap-code>",\n', "boundary review gap schema"),
        ):
            with self.subTest(needle=needle), tempfile.TemporaryDirectory() as td:
                skills = self.copy_plugin(Path(td))
                reference = skills / "control-run" / "references" / "boundary-review.md"
                text = reference.read_text(encoding="utf-8").replace(needle, "")
                reference.write_text(text, encoding="utf-8")
                findings = SEAMS.cross_skill_contracts(skills)
                self.assertTrue(any(expected in message for _, message in findings))

    def test_shared_intake_correction_reference_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            (skills.parent / "references" / "intake-correction.md").unlink()

            findings = SEAMS.cross_skill_contracts(skills)

            self.assertTrue(any("intake-correction" in message for _, message in findings))

    def test_start_and_control_run_share_ensure_handoff_with_recovery_ownership(self):
        plugin = ROOT / "plugins" / "atlas"
        command = (
            'python3 "<atlas-plugin-root>/tools/atlas_planning.py" '
            'ensure --run "<run-directory>"'
        )
        start = (plugin / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")
        control = (plugin / "skills" / "control-run" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn(command, start)
        self.assertIn(command, control)
        self.assertIn("already names `system_design`, `program_design`, or `tickets`", control)
        self.assertIn("do not rerun Product Closure", control)
        self.assertIn("After a successful Product Closure transition", control)
        self.assertIn("re-read `control.json`", control)
        self.assertFalse([
            item for item in SEAMS.cross_skill_contracts(plugin / "skills")
            if item[0] == "cross"
        ])

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            control_path = skills / "control-run" / "SKILL.md"
            text = control_path.read_text(encoding="utf-8")
            control_path.write_text(text.replace(command, command.replace("ensure", "initialize"), 1), encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("shared planning ensure command" in message for _, message in findings), findings)

    def test_start_run_resume_uses_live_downstream_cursor_and_recovers_missing_state(self):
        plugin = ROOT / "plugins" / "atlas"
        start_path = plugin / "skills" / "start-run" / "SKILL.md"
        command = (
            'python3 "<atlas-plugin-root>/tools/atlas_planning.py" '
            'ensure --run "<run-directory>"'
        )
        start = start_path.read_text(encoding="utf-8")
        collision_section = start.split("## 1. Resolve and accept intake", 1)[0]
        handoff_section = start.split("## 3. Hand off", 1)[1]

        self.assertIn(command, collision_section)
        self.assertIn("If authoritative `control.json.phase` is `discovery`", collision_section)
        self.assertIn(
            "validated `planning-control.json.phase` is the actual current planning phase",
            collision_section,
        )
        self.assertIn(
            "validated `planning-control.json.phase` is the actual current planning phase",
            handoff_section,
        )
        self.assertNotIn(
            "A `PLANNING` run resumes at current `control.json.phase`",
            start,
        )

        cases = (
            (
                "planning-control.json.phase` is the actual current planning phase",
                "control.json.phase` is the actual current planning phase",
                "live downstream resume cursor",
            ),
            (
                command,
                command.replace("ensure", "initialize"),
                "interrupted downstream resume recovery",
            ),
        )
        for old, new, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as td:
                skills = self.copy_plugin(Path(td))
                path = skills / "start-run" / "SKILL.md"
                text = path.read_text(encoding="utf-8")
                self.assertIn(old, text)
                path.write_text(text.replace(old, new, 1), encoding="utf-8")
                findings = SEAMS.cross_skill_contracts(skills)
                self.assertTrue(any(expected in message for _, message in findings), findings)

    def test_downstream_run_schema_and_packaged_command_seams_are_checked(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            run_file = skills / "start-run" / "references" / "run-file.md"
            run_file.write_text(
                run_file.read_text(encoding="utf-8").replace(
                    "system_design_participation: agent_led  # agent_led | co_design when system_design is selected; otherwise null\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            start = skills / "start-run" / "SKILL.md"
            start.write_text(
                start.read_text(encoding="utf-8").replace("atlas_planning.py", "missing_planning.py", 1),
                encoding="utf-8",
            )
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("run.yaml v2 template" in message for _, message in findings), findings)
            self.assertTrue(any("interrupted downstream resume recovery" in message for _, message in findings), findings)

    def test_canonical_run_file_hic_dimensions_match_planning_literal_and_drift_is_detected(self):
        plugin = ROOT / "plugins" / "atlas"
        run_file = (plugin / "skills" / "start-run" / "references" / "run-file.md").read_text(
            encoding="utf-8"
        )
        maps = [
            value for _, block in SEAMS.template_blocks(run_file)
            if isinstance((value := SEAMS.yaml.safe_load(block)), dict) and value.get("version") == 2
        ]
        self.assertEqual(len(maps), 1)
        dimensions = tuple(maps[0]["gates"]["system_design"]["material_dimensions"])
        planning_dimensions = tuple(SEAMS.assigned_literal(
            (plugin / "tools" / "atlas_planning.py").read_text(encoding="utf-8"),
            "SYSTEM_DESIGN_DIMENSIONS",
        ))
        self.assertEqual(dimensions, planning_dimensions)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills / "start-run" / "references" / "run-file.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "      - responsibilities_and_system_seams\n",
                    "      - stale_slice_one_dimension\n",
                    1,
                ),
                encoding="utf-8",
            )
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("canonical run-file HUMAN_IF_CHANGED dimensions" in message for _, message in findings), findings)

    def test_classifier_contract_never_recommends_or_selects_participation(self):
        start = (ROOT / "plugins" / "atlas" / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")
        run_file = (
            ROOT / "plugins" / "atlas" / "skills" / "start-run" / "references" / "run-file.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ask once", start.lower())
        self.assertIn("present `agent_led` and `co_design` neutrally", start)
        self.assertIn("classifier neither recommends nor chooses", start)
        self.assertIn("version: 2", run_file)
        self.assertIn("system_design_participation: agent_led", run_file)
        self.assertIn("downstream system design reads the frozen value and never asks again", run_file.lower())

    def test_start_run_hands_off_from_the_current_authoritative_phase(self):
        text = (ROOT / "plugins" / "atlas" / "skills" / "start-run" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("When discovery is selected", text)
        self.assertIn("If its current phase is `discovery`, it owns the live cursor", text)
        self.assertIn("validated `planning-control.json.phase` is the actual current planning phase", text)
        self.assertIn("Hand off to that owner, not to the frozen downstream handoff phase", text)

    def test_stage_admission_architecture_matches_the_initializer(self):
        text = (ROOT / "architecture" / "02-workflow.md").read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        self.assertNotIn("This does not change the shipped Stage 0–2 initializer", normalized)
        self.assertIn("When discovery is selected, initialization creates its mutable gate", normalized)
        self.assertIn("When discovery is omitted, initialization creates no discovery gate or acceptance", normalized)

    def test_packaged_boundary_review_carries_the_exact_nine_product_closure_questions(self):
        review_path = (
            ROOT / "plugins" / "atlas" / "skills" / "control-run" / "references" / "boundary-review.md"
        )
        canonical_path = ROOT / "architecture" / "06-review-and-validation.md"
        review_text = review_path.read_text(encoding="utf-8")
        canonical_text = canonical_path.read_text(encoding="utf-8")
        review_section = review_text.split("## Product-closure semantic questions\n", 1)[1].split(
            "\nThese are the packaged questions", 1
        )[0]
        canonical_section = canonical_text.split("**Semantic questions, in order:**\n", 1)[1].split(
            "\nFailure resumes at discovery", 1
        )[0]
        review_questions = tuple(re.findall(r"(?m)^[1-9]\. (.+\?)$", review_section))
        canonical_questions = tuple(re.findall(r"(?m)^[1-9]\. (.+\?)$", canonical_section))
        self.assertEqual(len(review_questions), 9)
        self.assertEqual(review_questions, canonical_questions)
        review = " ".join(review_text.lower().split())
        self.assertIn("every material gap", review)
        self.assertIn("must not repair", review)

    def test_discovery_skill_stays_below_400_lines_without_substituting_filler_for_precise_ownership(self):
        discovery = ROOT / "plugins" / "atlas" / "skills" / "discovery" / "SKILL.md"
        lines = discovery.read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 400)
        text = "\n".join(lines)
        self.assertIn("10-decisions.md", text)
        self.assertIn("20-prd.md", text)
        self.assertIn("references/decision-record.md", text)
        self.assertIn("references/run-layout.md", text)
        self.assertIn("render_prd.py", text)
        self.assertIn("--draft .20-prd.next.md", text)
        self.assertIn("Never edit canonical `20-prd.md` directly", text)

        # These are the load-bearing conversation mechanics that were present before
        # the Stage 0–2 authority simplification. References preserve artifact shape;
        # the always-loaded skill must still explain how to conduct discovery.
        for clause in (
            "The **frontier** is every open question whose prerequisites are already settled",
            "Work in rounds",
            "Only **grill** questions go to the user",
            "never manufacture a recommendation",
            "strongest counterargument",
            "**The problem test.**",
            "**The announcement test.**",
            "Propose candidate shapes",
            "File names, function signatures, and schemas are later stages",
            "**Nothing important exists only in the conversation.**",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            discovery_copy = skills / "discovery" / "SKILL.md"
            discovery_copy.write_text(
                "\n".join(line for line in discovery_copy.read_text(encoding="utf-8").splitlines() if "references/" not in line),
                encoding="utf-8",
            )
            trimmed = discovery_copy.read_text(encoding="utf-8").splitlines()
            self.assertLessEqual(len(trimmed), 400)
            self.assertNotIn("references/decision-record.md", "\n".join(trimmed))

    def test_discovery_requires_agent_evidence_and_an_executable_cold_read(self):
        skill = (ROOT / "plugins" / "atlas" / "skills" / "discovery" / "SKILL.md").read_text(encoding="utf-8")
        decisions = (
            ROOT / "plugins" / "atlas" / "skills" / "discovery" / "references" / "decision-record.md"
        ).read_text(encoding="utf-8")

        self.assertIn("cite the evidence that resolved it", skill)
        self.assertIn("Give the fresh reader only `10-decisions.md`", skill)
        self.assertIn("unaddressed consequence", skill)
        self.assertIn("unsupported by its own reasoning or evidence", skill)
        self.assertIn("reports findings and never repairs", skill)
        self.assertIn("justified recommendation or explicitly says that none is supportable", decisions)

    def test_start_run_refuses_to_overwrite_existing_immutable_intake(self):
        start = (ROOT / "plugins" / "atlas" / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")

        # initialize refuses an existing control.json only after run.yaml has been written.
        # The human-facing producer must therefore resolve collisions before any write.
        for clause in (
            "Never overwrite an existing `run.yaml`",
            "Resume from the controller that currently owns the live cursor",
            "choose a different slug",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, start)

    def test_start_run_preserves_classification_scope_and_handoff_procedure(self):
        start = (ROOT / "plugins" / "atlas" / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")

        for clause in (
            "Stage 0 is recommend-only",
            "`trivial`",
            "`normal`",
            "`architectural`",
            "`fog_of_war`",
            "Inspect the current Git repository",
            "every other repository already known to be affected",
            "short, descriptive, stable",
            "no first-party Atlas owner",
            "never substitute an incubator skill",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, start)

        self.assertIn("does not imply an exact stage sequence or gate map", start)
        self.assertIn("ask rather than invent policy", start)

    def test_packaged_tool_commands_do_not_depend_on_the_callers_working_directory(self):
        plugin = ROOT / "plugins" / "atlas"
        for name in ("start-run", "discovery", "control-run", "setup-atlas"):
            with self.subTest(skill=name):
                skill_path = plugin / "skills" / name / "SKILL.md"
                text = skill_path.read_text(encoding="utf-8")
                self.assertIn("third parent of this file", text)
                self.assertEqual(skill_path.parents[2], plugin)

        for path in plugin.rglob("*.md"):
            with self.subTest(reference=str(path.relative_to(plugin))):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("python3 tools/", text)
                self.assertNotIn("plugins/atlas/requirements.txt", text)

        with tempfile.TemporaryDirectory() as td:
            for tool in ("atlas_control.py", "atlas_planning.py"):
                with self.subTest(tool=tool):
                    result = subprocess.run(
                        [sys.executable, str(plugin / "tools" / tool), "--help"],
                        cwd=td,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_start_run_resolves_a_safe_contained_target_before_writing(self):
        start = (ROOT / "plugins" / "atlas" / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")
        for clause in (
            "resolve-run-path",
            "lowercase letters, digits, and single hyphens",
            "Absolute paths, separators, `.`, and `..` are invalid",
            "Use `path` exactly as the target",
            "pass the unchanged device/inode values",
            "--prepared-device",
            "--prepared-inode",
            "before writing `run.yaml`",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, start)

    def test_start_run_routes_existing_authoritative_terminal_and_recovery_states(self):
        start = (ROOT / "plugins" / "atlas" / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8")
        for clause in (
            "If authoritative `control.json.phase` is `discovery`",
            "validated `planning-control.json.phase` is the actual current planning phase",
            "interrupted Product Closure → planning handoff",
            "`STALE`",
            "intake-correction.md",
            "`REJECTED`",
            "terminal",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, start)

    def test_control_run_preserves_failure_authority_and_rejection_handoffs(self):
        control = (ROOT / "plugins" / "atlas" / "skills" / "control-run" / "SKILL.md").read_text(encoding="utf-8")

        for clause in (
            "report the exact error and stop",
            "never emulate transition logic",
            "run.yaml.gates.discovery.authority",
            "python3 \"<atlas-plugin-root>/tools/atlas_control.py\" reject --run \"<run-directory>\" --reason \"<reason>\"",
            "never claim progression from an intended command",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause.lower(), control.lower())

        self.assertIn("structured `BLOCKED`", control)
        self.assertIn("expected check outcome", control)

    def test_setup_and_spike_preserve_disclosed_costs_and_limits(self):
        setup = (ROOT / "plugins" / "atlas" / "skills" / "setup-atlas" / "SKILL.md").read_text(encoding="utf-8")
        spike = (ROOT / "plugins" / "atlas" / "skills" / "spike" / "SKILL.md").read_text(encoding="utf-8")
        findings = (
            ROOT / "plugins" / "atlas" / "skills" / "spike" / "references" / "findings-file.md"
        ).read_text(encoding="utf-8")

        self.assertIn("atomic contract-plus-code commits", setup)
        self.assertIn("no executable spike runner", spike)
        self.assertIn("agent-enforced procedure", spike)
        self.assertIn("**Confidence:**", findings)
        self.assertIn("state confidence", spike)

    def test_actual_pre_restoration_contract_is_rejected(self):
        fixture = ROOT / "tests" / "fixtures" / "reduced-skill-contracts"
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            plugin = skills.parent
            for source in fixture.rglob("*.md"):
                if source.name == "README.md":
                    continue
                destination = plugin / source.relative_to(fixture)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

            findings = SEAMS.cross_skill_contracts(skills)
            messages = "\n".join(message for _, message in findings)
            for name in ("discovery", "start", "control", "setup", "spike"):
                with self.subTest(contract=name):
                    self.assertIn(f"{name}: missing operating contract", messages)
            self.assertIn("caller-CWD-dependent", messages)

    def test_checker_rejects_each_restored_operating_contract_cluster(self):
        cases = (
            ("discovery/SKILL.md", "Work in rounds"),
            ("start-run/SKILL.md", "Never overwrite an existing `run.yaml`"),
            ("control-run/SKILL.md", "Never emulate transition logic"),
            ("setup-atlas/SKILL.md", "atomic contract-plus-code commits"),
            ("spike/SKILL.md", "no executable spike runner"),
            ("spike/references/findings-file.md", "**Confidence:**"),
        )
        for relative, needle in cases:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as td:
                skills = self.copy_plugin(Path(td))
                path = skills / relative
                text = path.read_text(encoding="utf-8")
                self.assertIn(needle, text)
                path.write_text(text.replace(needle, "[removed operating contract]", 1), encoding="utf-8")
                findings = SEAMS.cross_skill_contracts(skills)
                self.assertTrue(
                    any("missing operating contract" in message for _, message in findings),
                    findings,
                )

    def test_to_spec_is_deleted_from_packaging_and_seam_contracts(self):
        self.assertFalse((ROOT / "plugins" / "atlas" / "skills" / "to-spec").exists())
        for manifest in (
            ROOT / "plugins" / "atlas" / "plugin.json",
            ROOT / "plugins" / "atlas" / ".codex-plugin" / "plugin.json",
        ):
            text = manifest.read_text(encoding="utf-8").lower()
            self.assertNotIn("behavioural specification", text)
            self.assertNotIn("behavioral specification", text)
            self.assertNotIn("to-spec", text)

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            (skills / "to-spec").mkdir()
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("to-spec remains" in message for _, message in findings))

    def test_atlas_manifests_describe_the_current_stage0_through_stage4_surface(self):
        manifests = (
            ROOT / "plugins" / "atlas" / "plugin.json",
            ROOT / "plugins" / "atlas" / ".codex-plugin" / "plugin.json",
        )
        descriptions = [
            json.loads(path.read_text(encoding="utf-8"))["description"] for path in manifests
        ]
        self.assertEqual(len(set(descriptions)), 1)
        for clause in ("Stage 0", "System", "Program Design", "Stage 4"):
            self.assertIn(clause, descriptions[0])

        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            path = skills.parent / ".codex-plugin" / "plugin.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["description"] = "Atlas setup and discovery skills."
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            findings = SEAMS.cross_skill_contracts(skills)
            self.assertTrue(any("plugin manifest descriptions" in message for _, message in findings), findings)

    def test_immutable_run_mutation_is_detected_but_negation_is_not(self):
        for sentence, expected in (
            ("Revise run.yaml with the new scope.", True),
            ("Never revise run.yaml.", False),
        ):
            with self.subTest(sentence=sentence), tempfile.TemporaryDirectory() as td:
                skills = self.copy_plugin(Path(td))
                discovery = skills / "discovery" / "SKILL.md"
                discovery.write_text(discovery.read_text(encoding="utf-8") + "\n" + sentence, encoding="utf-8")
                findings = SEAMS.cross_skill_contracts(skills)
                found = any("may not mutate immutable run.yaml" in message for _, message in findings)
                self.assertEqual(found, expected)

    def test_spike_cannot_restore_projection_as_authority(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            spike = skills / "spike" / "SKILL.md"
            text = spike.read_text(encoding="utf-8").replace(
                "authoritative `control.json`",
                "authoritative `00-state.md`",
            )
            spike.write_text(text, encoding="utf-8")

            findings = SEAMS.cross_skill_contracts(skills)

            self.assertTrue(any("spike" in message and "control.json" in message for _, message in findings))


if __name__ == "__main__":
    unittest.main()
