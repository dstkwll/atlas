import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_skill_seams.py"
SPEC = importlib.util.spec_from_file_location("check_skill_seams", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
SEAMS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SEAMS)


class SkillSeamHardeningTests(unittest.TestCase):
    def copy_plugin(self, root: Path) -> Path:
        plugin = root / "plugins" / "atlas"
        shutil.copytree(ROOT / "plugins" / "atlas", plugin)
        return plugin / "skills"

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
        self.assertIn("10-decisions.md", "\n".join(lines))
        self.assertIn("20-prd.md", "\n".join(lines))
        self.assertIn("references/decision-record.md", "\n".join(lines))
        self.assertIn("references/run-layout.md", "\n".join(lines))
        self.assertIn("render_prd.py", "\n".join(lines))
        self.assertIn("--draft .20-prd.next.md", "\n".join(lines))
        self.assertIn("Never edit canonical `20-prd.md` directly", "\n".join(lines))

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
