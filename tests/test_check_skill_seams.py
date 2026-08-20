import importlib.util
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

            self.assertTrue(any("discovery candidate schema" in message for _, message in findings))

    def test_reopened_discovery_schema_is_required_independently(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            reference = skills / "discovery" / "references" / "run-layout.md"
            text = reference.read_text(encoding="utf-8")
            marker = "## Reopened discovery candidate"
            if marker in text:
                text = text.split(marker, 1)[0]
            reference.write_text(text, encoding="utf-8")

            findings = SEAMS.cross_skill_contracts(skills)

            self.assertTrue(any("reopened discovery candidate schema" in message for _, message in findings))

    def test_spec_candidate_template_field_deletion_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            reference = skills / "to-spec" / "references" / "spec-file.md"
            reference.write_text(
                reference.read_text(encoding="utf-8").replace("supersedes: null\n", "", 1),
                encoding="utf-8",
            )

            findings = SEAMS.cross_skill_contracts(skills)

            self.assertTrue(any("spec candidate schema" in message for _, message in findings))

    def test_raw_base_hash_is_a_required_state_template_field(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self.copy_plugin(Path(td))
            reference = skills / "start-run" / "references" / "state-file.md"
            reference.write_text(
                reference.read_text(encoding="utf-8").replace("base_run_sha256: null\n", "", 1),
                encoding="utf-8",
            )

            findings = SEAMS.cross_skill_contracts(skills)

            self.assertTrue(any("base_run_sha256" in message for _, message in findings))

    def test_immutable_run_mutation_synonyms_are_detected_but_negations_are_not(self):
        for verb in ("Revise", "Amend", "Mutate"):
            with self.subTest(verb=verb), tempfile.TemporaryDirectory() as td:
                skills = self.copy_plugin(Path(td))
                discovery = skills / "discovery" / "SKILL.md"
                baseline = discovery.read_text(encoding="utf-8")
                discovery.write_text(
                    baseline + f"\n{verb} run.yaml with the new repository scope.\n",
                    encoding="utf-8",
                )
                findings = SEAMS.cross_skill_contracts(skills)
                self.assertTrue(any("may not mutate immutable run.yaml" in message for _, message in findings))

                discovery.write_text(
                    baseline + f"\nNever {verb.lower()} run.yaml.\n",
                    encoding="utf-8",
                )
                findings = SEAMS.cross_skill_contracts(skills)
                self.assertFalse(any("may not mutate immutable run.yaml" in message for _, message in findings))


if __name__ == "__main__":
    unittest.main()
