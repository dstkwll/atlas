import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "plugins" / "atlas" / "tools"
CONTROL_PATH = TOOLS_DIR / "atlas_control.py"
PLANNING_PATH = TOOLS_DIR / "atlas_planning.py"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
STAGE_LABEL = "Product Definition Approval"
ACTION_TEXT = "Approve the product definition"
HELPER_TEXT = "Confirm the PRD and recorded decisions are complete enough to begin System Design."
HISTORICAL_LABEL = "Product " "Closure"
TERMINOLOGY_NOTE_PATH = Path("architecture/README.md")
TERMINOLOGY_NOTE = (
    f"Historical decision and provenance records retain the former user-facing label "
    f"`{HISTORICAL_LABEL}` unchanged."
)
OLD_PROSE = re.compile(r"\bproduct(?:[\s-]+)closure\b", re.IGNORECASE)

HISTORICAL_EXACT_RECORDS = {
    Path("architecture/10-decisions-and-open-questions.md"),
    Path("architecture/16-learnings-and-course-corrections.md"),
    Path("architecture/20-v0.5-decisions.md"),
    Path("architecture/21-v0.6-decisions.md"),
    Path("architecture/22-v0.7-decisions.md"),
    Path("architecture/23-v0.8-decisions.md"),
    Path("architecture/25-v0.10-decisions.md"),
    Path("architecture/26-v0.11-decisions.md"),
    Path("plugins/atlas/references/gazetteer-behavior-inventory.md"),
    Path("plugins/atlas/references/gazetteer-verification.md"),
}
GENERATED_FROM_HISTORICAL_RECORDS = {Path("architecture/rolling-monolith.md")}
HISTORICAL_PROVENANCE_TESTS = {Path("tests/test_design_architecture.py")}

LIVE_USER_FACING_DOCS = (
    Path("architecture/02-workflow.md"),
    Path("architecture/03-artifact-model.md"),
    Path("architecture/04-control-plane.md"),
    Path("architecture/06-review-and-validation.md"),
    Path("plugins/atlas/README.md"),
    Path("plugins/atlas/skills/discovery/SKILL.md"),
    Path("plugins/atlas/skills/control-run/SKILL.md"),
    Path("plugins/atlas/skills/system-design/SKILL.md"),
    Path("plugins/atlas/skills/program-design/SKILL.md"),
    Path("plugins/atlas/skills/compile-tickets/SKILL.md"),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProductDefinitionApprovalCompatibilityTests(unittest.TestCase):
    def test_live_docs_and_skills_use_the_settled_stage_label(self):
        for relative in LIVE_USER_FACING_DOCS:
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(STAGE_LABEL, text)
                self.assertIsNone(OLD_PROSE.search(text))

        control_skill = (
            ROOT / "plugins" / "atlas" / "skills" / "control-run" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn(ACTION_TEXT, control_skill)
        self.assertIn(HELPER_TEXT, control_skill)

        terminology = (ROOT / TERMINOLOGY_NOTE_PATH).read_text(encoding="utf-8")
        self.assertIn(TERMINOLOGY_NOTE, terminology)
        for alias in (
            "`product_closure`",
            "`reviews/product_closure-v<version>.json`",
            "`kind: product_closure`",
            "`stage: product_closure`",
        ):
            self.assertIn(alias, terminology)

    def test_cli_help_uses_the_settled_user_facing_copy(self):
        top_level = subprocess.run(
            [sys.executable, str(CONTROL_PATH), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        advance = subprocess.run(
            [sys.executable, str(CONTROL_PATH), "advance", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(top_level.returncode, 0, top_level.stderr)
        self.assertEqual(advance.returncode, 0, advance.stderr)
        self.assertIn(STAGE_LABEL, top_level.stdout)
        self.assertIn(HELPER_TEXT, top_level.stdout)
        self.assertIn(ACTION_TEXT, advance.stdout)
        self.assertNotRegex(top_level.stdout + advance.stdout, OLD_PROSE)

    def test_machine_and_serialized_product_closure_identifiers_are_unchanged(self):
        control = load_module("atlas_control_product_definition_test", CONTROL_PATH)
        planning = load_module("atlas_planning_product_definition_test", PLANNING_PATH)
        self.assertEqual(control.EXIT_BOUNDARY, {"discovery": "product_closure"})
        self.assertEqual(planning.PRODUCT_CLOSURE_FIELDS, {"version", "sha256"})

        control_skill = (
            ROOT / "plugins" / "atlas" / "skills" / "control-run" / "SKILL.md"
        ).read_text(encoding="utf-8")
        review = (
            ROOT
            / "plugins"
            / "atlas"
            / "skills"
            / "control-run"
            / "references"
            / "boundary-review.md"
        ).read_text(encoding="utf-8")
        system_design_shape = (
            ROOT
            / "plugins"
            / "atlas"
            / "skills"
            / "system-design"
            / "references"
            / "system-design-file.md"
        ).read_text(encoding="utf-8")
        self.assertIn("reviews/product_closure-v<version>.json", control_skill)
        self.assertIn('"stage": "product_closure"', review)
        self.assertIn("kind: product_closure", system_design_shape)

    def test_every_old_prose_survivor_is_classified_compatibility_or_provenance(self):
        allowed = (
            HISTORICAL_EXACT_RECORDS
            | GENERATED_FROM_HISTORICAL_RECORDS
            | HISTORICAL_PROVENANCE_TESTS
        )
        listed = subprocess.run(
            ["git", "ls-files", "-co", "--exclude-standard"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.splitlines()
        defects = []
        for name in listed:
            relative = Path(name)
            path = ROOT / relative
            if not path.is_file() or relative in allowed:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if relative == TERMINOLOGY_NOTE_PATH:
                self.assertEqual(text.count(TERMINOLOGY_NOTE), 1)
                text = text.replace(TERMINOLOGY_NOTE, "", 1)
            for match in OLD_PROSE.finditer(text):
                defects.append(f"{relative}:{text.count(chr(10), 0, match.start()) + 1}")
        self.assertEqual(defects, [])

        for relative in HISTORICAL_EXACT_RECORDS:
            with self.subTest(historical_record=relative):
                self.assertRegex((ROOT / relative).read_text(encoding="utf-8"), OLD_PROSE)

        monolith = (ROOT / "architecture" / "rolling-monolith.md").read_text(encoding="utf-8")
        self.assertIn(STAGE_LABEL, monolith)
        self.assertRegex(monolith, OLD_PROSE)


if __name__ == "__main__":
    unittest.main()
