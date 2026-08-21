import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "architecture"


def read(name):
    return (ARCH / name).read_text(encoding="utf-8")


def normalized(name):
    return " ".join(read(name).split())


def codesign_classifier_violations(text):
    actions = r"recommend(?:s|ed|ing)?|select(?:s|ed|ing)?|choose|chooses|chose|nudge(?:s|d|ing)?|route(?:s|d|ing)?|determine(?:s|d|ing)?"
    normalized_text = text.lower().replace("co-design", "co_design")
    violations = []
    for sentence in re.split(r"(?:\n\s*\n|(?<=[.!?])\s+)", normalized_text):
        sentence = " ".join(sentence.split())
        if "classifier" not in sentence or "co_design" not in sentence:
            continue
        if not re.search(actions, sentence):
            continue
        safe = (
            re.search(rf"classifier\s+(?:does not|never)\s+(?:\w+\s+){{0,8}}(?:{actions})", sentence)
            or re.search(rf"classifier\s+(?:must|should|may|can|shall|will)\s+not\s+(?:\w+\s+){{0,8}}(?:{actions})", sentence)
            or re.search(rf"classifier\s+cannot\s+(?:\w+\s+){{0,8}}(?:{actions})", sentence)
            or re.search(rf"classifier\s+neither\s+(?:\w+\s+){{0,8}}(?:{actions})", sentence)
            or re.search(rf"co_design.{{0,100}}(?:never|not).{{0,60}}(?:{actions}).{{0,60}}classifier", sentence)
            or "not a classifier output" in sentence
        )
        if not safe:
            violations.append(sentence)
    return violations


def human_if_changed_mapping(text):
    text = " ".join(text.split())
    any_change = re.search(r"any material dimension.{0,100}?`?(HUMAN|AGENT_REVIEW)`?", text)
    no_change = re.search(r"no material dimensions.{0,100}?`?(HUMAN|AGENT_REVIEW)`?", text)
    if not any_change or not no_change:
        return None
    return any_change.group(1), no_change.group(1)


class PairedDesignArchitectureTests(unittest.TestCase):
    def test_v07_is_the_declared_baseline_and_has_a_decision_record(self):
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        architecture_readme = read("README.md")
        decisions = read("22-v0.7-decisions.md")

        self.assertIn("architecture/22-v0.7-decisions.md", root_readme)
        self.assertIn("**v0.7**", root_readme)
        self.assertIn("**v0.7**", architecture_readme)
        for identifier in ("D-071", "D-072", "D-073", "D-074", "D-075", "D-076"):
            self.assertIn(identifier, decisions)

    def test_codesign_is_user_selected_participation_not_gate_authority(self):
        control = normalized("04-control-plane.md")

        self.assertIn("agent_led", control)
        self.assertIn("co_design", control)
        self.assertRegex(control, r"participation.{0,160}authority|authority.{0,160}participation")
        self.assertRegex(control, r"user.{0,100}(select|choose).{0,100}co_design")
        self.assertIn("prompt", control.lower())
        self.assertIn("classifier does not recommend or select", control.lower())
        self.assertRegex(control, r"(never|must not|does not).{0,100}(silently.{0,100})?(select|route|determine).{0,100}co_design")

    def test_classifier_never_recommends_or_nudges_toward_codesign(self):
        canonical = [path for path in ARCH.glob("*.md") if path.name != "rolling-monolith.md"]
        for path in canonical:
            with self.subTest(path=path.name):
                self.assertEqual(codesign_classifier_violations(path.read_text(encoding="utf-8")), [])

        for statement in (
            "The classifier recommends co_design.",
            "The classifier may choose co_design.",
            "The classifier nudges toward co_design.",
            "The classifier should recommend co-design.",
            "The classifier routes the user to co_design.",
        ):
            with self.subTest(forbidden=statement):
                self.assertTrue(codesign_classifier_violations(statement))

        for statement in (
            "The classifier recommends workflow depth and governance.",
            "The classifier does not recommend or select co_design.",
            "The classifier must not recommend co_design.",
            "The classifier should not recommend co_design.",
            "The classifier may not choose co_design.",
            "The classifier cannot route the user to co_design.",
            "The classifier neither recommends nor selects co_design.",
            "co_design is not a classifier output.",
        ):
            with self.subTest(permitted=statement):
                self.assertEqual(codesign_classifier_violations(statement), [])

        for name in ("01-principles.md", "02-workflow.md", "04-control-plane.md", "16-learnings-and-course-corrections.md", "22-v0.7-decisions.md"):
            text = normalized(name).lower()
            self.assertRegex(text, r"classifier.{0,140}(does not|neither|never).{0,120}recommend")

    def test_codesign_requires_a_non_authoritative_visual_board(self):
        artifact = normalized("03-artifact-model.md")

        self.assertIn("30-system-design.html", artifact)
        self.assertIn("co_design", artifact)
        self.assertRegex(artifact, r"mandatory|required")
        self.assertRegex(artifact, r"non-authoritative|never authoritative")
        self.assertIn("source SHA-256", artifact)
        self.assertIn("renderer version", artifact)
        for view in ("topology", "ownership", "schema", "failure", "rejected alternatives"):
            self.assertIn(view, artifact)

    def test_stage_three_and_four_have_one_decision_ownership_rule(self):
        workflow = normalized("02-workflow.md")

        self.assertIn("coordinated change across a seam", workflow)
        self.assertRegex(workflow, r"caller.{0,200}Stage 4|Stage 4.{0,200}caller")
        self.assertRegex(workflow, r"Composite decisions.{0,200}split")
        self.assertRegex(workflow, r"Stage 3.{0,300}Stage 4")

    def test_paired_drafting_keeps_separate_sequential_acceptance(self):
        workflow = normalized("02-workflow.md")
        review = normalized("06-review-and-validation.md")
        combined = workflow + " " + review

        self.assertRegex(combined, r"(side by side|side-by-side|in parallel)")
        self.assertRegex(combined, r"accept.{0,100}system design.{0,160}(before|first)")
        self.assertRegex(combined, r"program design.{0,240}exact accepted.{0,100}system design")
        self.assertRegex(combined, r"joint bundle.{0,100}(forbidden|not|never)|no joint bundle")
        self.assertIn("DESIGN_BLOCKED", combined)

    def test_standard_design_governance_matches_the_ratified_defaults(self):
        config = read("09-reference-config.md")
        standard = config.split("  standard:", 1)[1].split("  high_assurance:", 1)[0]

        self.assertNotRegex(config, re.compile(r"^\s+- spec\s*$", re.MULTILINE))
        self.assertNotRegex(config, re.compile(r"^\s+spec:\s+", re.MULTILINE))
        self.assertRegex(standard, r"system_design:\s+HUMAN_IF_CHANGED")
        self.assertRegex(standard, r"program_design:\s+AGENT_REVIEW")
        self.assertNotRegex(config, r"system_design:\s+AUTO")

        governance = normalized("08-state-and-governance.md")
        self.assertEqual(human_if_changed_mapping(governance), ("HUMAN", "AGENT_REVIEW"))
        self.assertEqual(
            human_if_changed_mapping("any material dimension maps to AGENT_REVIEW; no material dimensions map to HUMAN"),
            ("AGENT_REVIEW", "HUMAN"),
        )
        self.assertRegex(governance, r"baseline or classification unavailable.{0,100}fail closed to HUMAN")
        self.assertRegex(config, r"no_material_change:\s+AGENT_REVIEW")
        self.assertRegex(config, r"any_material_change:\s+HUMAN")
        self.assertRegex(config, r"baseline_or_classification_unavailable:\s+HUMAN")

    def test_downstream_controller_is_minimal_separate_and_not_a_generalized_router(self):
        state = normalized("08-state-and-governance.md")
        control = normalized("04-control-plane.md")
        artifacts = normalized("03-artifact-model.md")
        decisions = normalized("22-v0.7-decisions.md")
        combined = " ".join((state, control, artifacts, decisions))

        self.assertRegex(combined, r"separate Stage 3 and Stage 4 (?:gate/acceptance|gate and acceptance|outcomes)")
        self.assertRegex(combined, r"exact candidate/version/hash bindings")
        self.assertIn("staleness", combined)
        self.assertRegex(combined, r"does not widen (?:the )?Stage 0–2 `control.json`|does not widen this file")
        self.assertRegex(combined, r"does not introduce a generalized router|not a generalized router")

    def test_resolved_open_questions_no_longer_read_as_open(self):
        questions = normalized("10-decisions-and-open-questions.md")
        history = normalized("14-v0.2-decisions.md")

        self.assertRegex(questions, r"OQ-003.{0,100}(RESOLVED|Resolved)")
        self.assertRegex(history, r"Exact semantics of `HUMAN_IF_CHANGED`.{0,160}(resolved|D-074)")


if __name__ == "__main__":
    unittest.main()
