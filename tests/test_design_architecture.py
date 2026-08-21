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
        for segment in re.split(r"(?:,\s*)?\b(?:and|but|while|yet)\b\s+", sentence):
            if "co_design" not in segment or not re.search(actions, segment):
                continue
            safe = (
                re.search(rf"classifier\s+(?:does not|never)\s+(?:\w+\s+){{0,8}}(?:{actions})", segment)
                or re.search(rf"classifier\s+(?:must|should|may|can|shall|will)\s+not\s+(?:\w+\s+){{0,8}}(?:{actions})", segment)
                or re.search(rf"classifier\s+cannot\s+(?:\w+\s+){{0,8}}(?:{actions})", segment)
                or re.search(rf"classifier\s+neither\s+(?:\w+\s+){{0,8}}(?:{actions})", segment)
                or re.search(rf"(?:does not|never|must not|should not|may not|cannot)\s+(?:\w+\s+){{0,8}}(?:{actions})", segment)
                or re.search(rf"co_design.{{0,100}}(?:never|not).{{0,60}}(?:{actions}).{{0,60}}classifier", segment)
                or "not a classifier output" in segment
            )
            if not safe:
                violations.append(segment)
    return violations


def model_skill_identity_routing_violations(text):
    """Return affirmative clauses that make skill identity a model-routing key."""
    violations = []
    normalized_text = " ".join(text.split())
    for clause in re.split(r"(?<=[.!?;])\s+|\n+", normalized_text):
        for segment in re.split(r"(?:,\s*)?\b(?:but|while|yet)\b\s+", clause, flags=re.IGNORECASE):
            lower = segment.lower()
            if not re.search(r"skill (?:name|identity)|whole skill|skill itself", lower):
                continue
            if not re.search(r"bind|bound|rout|select|assign|staff|fix|adhere|model tier|worker tier", lower):
                continue
            if re.search(r"\b(?:never|cannot|must not|may not|should not|does not|do not|not)\b|rather than", lower):
                continue
            violations.append(segment)
    return violations


def frontier_preexposure_violations(text):
    """Return affirmative clauses that expose the producer frontier to the blind critic."""
    violations = []
    normalized_text = " ".join(text.split())
    for clause in re.split(r"(?<=[.!?;])\s+|\n+", normalized_text):
        clause_lower = clause.lower()
        if not re.search(r"critic|challenger|fresh reader", clause_lower):
            continue
        for segment in re.split(r"(?:,\s*)?\b(?:and|but|while|yet)\b\s+", clause, flags=re.IGNORECASE):
            lower = segment.lower()
            if not re.search(r"producer(?:'s)? (?:proposed )?frontier", lower):
                continue
            if not re.search(r"read|see|review|receive|given|expos", lower):
                continue
            if re.search(r"\b(?:never|cannot|must not|may not|should not|does not|do not|not)\b|without (?:reading|seeing)", lower):
                continue
            violations.append(segment)
    return violations


def unconditional_system_design_acceptance_violations(text):
    """Return clauses that require System Design acceptance even when it was not selected."""
    violations = []
    for clause in re.split(r"(?<=[.!?;])\s+|\n+", " ".join(text.split())):
        lower = clause.lower()
        if "system design" not in lower or "accept" not in lower:
            continue
        if not re.search(r"(?:accepted|accept).{0,60}(?:first|before)|(?:first|before).{0,60}(?:accepted|accept)", lower):
            continue
        if re.search(r"when (?:it is |that stage is |both stages are )?selected|if (?:it is |system design is )?selected", lower):
            continue
        violations.append(clause)
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
        for identifier in ("D-071", "D-072", "D-073", "D-074", "D-075", "D-076", "D-077", "D-078", "D-079"):
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
            "The classifier does not recommend co_design but may choose co_design.",
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
        self.assertRegex(combined.lower(), r"(?:accept system design first when.{0,80}selected|system design is accepted first)")
        self.assertRegex(combined.lower(), r"program design.{0,500}selected system design.{0,100}exact accepted")
        self.assertRegex(combined, r"joint bundle.{0,100}(forbidden|not|never)|no joint bundle")
        self.assertIn("DESIGN_BLOCKED", combined)

        for name in (
            "01-principles.md",
            "02-workflow.md",
            "04-control-plane.md",
            "06-review-and-validation.md",
            "22-v0.7-decisions.md",
        ):
            self.assertEqual([], unconditional_system_design_acceptance_violations(read(name)), name)

        for clause, forbidden in (
            ("System Design must always be accepted first, even when omitted.", True),
            ("When selected, System Design is accepted first.", False),
            ("The process must accept System Design first when that stage is selected.", False),
        ):
            with self.subTest(clause=clause):
                self.assertEqual(bool(unconditional_system_design_acceptance_violations(clause)), forbidden)

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

    def test_model_staffing_routes_invocations_by_role_and_task_shape_not_by_skill(self):
        policy = normalized("17-agent-roles-rosters-and-model-policy.md")
        decisions = normalized("22-v0.7-decisions.md")
        combined = policy + " " + decisions

        self.assertRegex(combined, r"model invocation.{0,160}role.{0,80}task shape")
        self.assertRegex(combined, r"never.{0,100}skill (?:name|identity)|not.{0,100}skill (?:name|identity)")
        self.assertRegex(combined, r"skill.{0,180}multiple.{0,100}task shapes")
        self.assertEqual([], model_skill_identity_routing_violations(combined))

        for clause, forbidden in (
            ("Discovery's skill identity binds every invocation to one fixed model tier.", True),
            ("The whole skill is staffed by one worker tier.", True),
            ("The skill itself adheres to the frontier model tier.", True),
            ("The role is not the routing key, while skill identity assigns the worker tier.", True),
            ("The role is not the routing key but skill identity assigns the worker tier.", True),
            ("A skill name must not select a model tier.", False),
            ("The whole skill should not be staffed by one worker tier.", False),
            ("The skill itself cannot adhere to a fixed model tier.", False),
            ("Model staffing is never bound to skill identity.", False),
        ):
            with self.subTest(clause=clause):
                self.assertEqual(bool(model_skill_identity_routing_violations(clause)), forbidden)

    def test_worker_diversity_is_conditional_staffing_not_authority(self):
        policy = normalized("17-agent-roles-rosters-and-model-policy.md").lower()
        decisions = normalized("22-v0.7-decisions.md").lower()
        combined = policy + " " + decisions
        diversity_policy = policy.split("# 8. builder/reviewer diversity", 1)[1].split("# 9. outcome telemetry", 1)[0]

        self.assertIn("fresh_context: required", diversity_policy)
        self.assertIn("different_worker_config: preferred", diversity_policy)
        self.assertIn("different_model_family: conditional", diversity_policy)
        self.assertRegex(diversity_policy, r"different model family is required for a model.{0,120}`high_assurance`")
        self.assertRegex(diversity_policy, r"and after repeated review failures or evidence of correlated blind spots")
        self.assertRegex(diversity_policy, r"outside those conditions it is optional")
        self.assertRegex(combined, r"model diversity.{0,180}(not authority|no authority|never.{0,80}authority)")

    def test_discovery_challenges_the_question_frontier_before_the_first_round_and_at_closure(self):
        discovery = normalized("07-spikes-and-discovery.md").lower()
        decisions = normalized("22-v0.7-decisions.md").lower()
        combined = discovery + " " + decisions

        self.assertRegex(combined, r"before.{0,100}first.{0,80}(grill )?round")
        self.assertRegex(combined, r"fresh.{0,120}(frontier critic|challenger)")
        self.assertRegex(combined, r"independent.{0,120}(question|decision).{0,80}(frontier|set)")
        self.assertRegex(combined, r"missing.{0,80}mis-?rout.{0,80}(question|decision)")
        self.assertRegex(combined, r"cold read.{0,200}(missing|absent).{0,120}(mis-?rout|wrong owner)")
        self.assertRegex(decisions, r"packaged skills.{0,120}follow-on implementation")
        self.assertEqual([], frontier_preexposure_violations(combined))

        for clause, forbidden in (
            ("The frontier critic reads the producer's proposed frontier before deriving questions.", True),
            ("The critic does not derive independently, and reads the producer's frontier first.", True),
            ("The critic does not derive independently but reads the producer's frontier first.", True),
            ("The critic does not read the producer's proposed frontier before producing its own.", False),
            ("The critic must not receive the producer's frontier.", False),
            ("The fresh reader cannot see the producer's proposed frontier.", False),
            ("Give the critic the framing, but not the producer's frontier.", False),
        ):
            with self.subTest(clause=clause):
                self.assertEqual(bool(frontier_preexposure_violations(clause)), forbidden)

    def test_system_design_admission_binds_to_the_selected_product_path(self):
        decisions = normalized("22-v0.7-decisions.md").lower()
        review = normalized("06-review-and-validation.md").lower()
        workflow = normalized("02-workflow.md").lower()
        artifacts = normalized("03-artifact-model.md").lower()
        state = normalized("08-state-and-governance.md").lower()
        combined = " ".join((decisions, review, workflow, artifacts, state))

        self.assertRegex(decisions, r"system design's (?:boundary|admission).{0,240}choose(?:s)? exactly one")
        self.assertRegex(
            decisions,
            r"product closure selected.{0,180}exact accepted `20-prd\.md` version/hash",
        )
        direct = re.search(
            r"system design's (?:boundary|admission).{0,500}product closure `not_required`(.*?)(?=program design's boundary)",
            decisions,
        )
        self.assertIsNotNone(direct)
        direct_rule = direct.group(1) if direct else ""
        self.assertRegex(direct_rule, r"accepted/frozen stage 0 intake")
        self.assertRegex(direct_rule, r"`control\.json\.base_run_sha256`")
        self.assertRegex(direct_rule, r"`effective_config_hash`")
        self.assertRegex(direct_rule, r"`effective_config_revision`")
        self.assertNotIn("accepted `20-prd.md`", direct_rule)
        self.assertRegex(combined, r"omitted product closure.{0,180}(?:no|neither).{0,80}(?:prd|artifact).{0,80}(?:approval|acceptance)")
        self.assertRegex(
            combined,
            r"bound source.{0,180}system design.{0,100}stale.{0,240}program design.{0,100}transitively.{0,160}same logical downstream transition",
        )

    def test_program_design_admission_binds_to_the_actual_selected_upstream_path(self):
        decisions = normalized("22-v0.7-decisions.md").lower()
        review = normalized("06-review-and-validation.md").lower()
        workflow = normalized("02-workflow.md").lower()
        artifacts = normalized("03-artifact-model.md").lower()
        combined = " ".join((decisions, review, workflow, artifacts))

        self.assertRegex(decisions, r"system design selected.{0,180}exact accepted `30-system-design\.md`")
        self.assertRegex(
            decisions,
            r"system design `not_required`.{0,120}product closure selected.{0,180}exact accepted `20-prd\.md`",
        )
        direct = re.search(
            r"both upstream semantic boundaries `not_required`(.{0,700})",
            decisions,
        )
        self.assertIsNotNone(direct)
        direct_rule = direct.group(1) if direct else ""
        self.assertRegex(direct_rule, r"`control\.json\.base_run_sha256`")
        self.assertRegex(direct_rule, r"`effective_config_hash`")
        self.assertRegex(direct_rule, r"`effective_config_revision`")
        self.assertNotIn("accepted `20-prd.md`", direct_rule)
        self.assertRegex(review, r"applicability test.{0,240}(selected stages|selected path).{0,240}exactly one")
        self.assertRegex(review, r"must not.{0,160}(manufacture|fabricate).{0,80}approval")
        self.assertRegex(combined, r"system design (?:is )?selected.{0,260}inside.{0,100}accepted.{0,100}seam")
        self.assertRegex(
            combined,
            r"direct(?:-admission| program design).{0,500}(?:frozen stage 0|stage 0.{0,100}frozen).{0,500}design_blocked",
        )

        stage_five = workflow.split("## stage 5 — execution compilation", 1)[1].split("## stage 6", 1)[0]
        self.assertRegex(stage_five, r"applicable.{0,180}(selected path|selected upstream)")
        self.assertRegex(stage_five, r"accepted product prd.{0,100}when product closure is selected")
        self.assertRegex(stage_five, r"accepted system design.{0,100}when system design is selected")
        self.assertRegex(stage_five, r"accepted/frozen stage 0.{0,240}direct")
        self.assertRegex(artifacts, r"direct(?:-admission| program design).{0,500}ticket.{0,240}(?:omit|not reference).{0,160}(?:prd|system design)")

        ticket_section = read("03-artifact-model.md").split("## `tickets/*.md`", 1)[1]
        ticket_template = ticket_section.split("```yaml", 1)[1].split("```", 1)[0]
        self.assertIn("applicable_upstream:", ticket_template)
        self.assertNotRegex(ticket_template, re.compile(r"^\s+prd:\s+", re.MULTILINE))
        self.assertNotRegex(ticket_template, re.compile(r"^\s+system_design:\s+", re.MULTILINE))

        stage_nine = workflow.split("## stage 9 — whole-feature validation and review", 1)[1].split("## stage 10", 1)[0]
        whole_feature_review = review.split("## whole-feature review", 1)[1].split("## human review policy", 1)[0]
        self.assertIn("applicable accepted upstream sources", stage_nine)
        self.assertIn("the product contract when selected", stage_nine)
        self.assertIn("applicable accepted upstream sources", whole_feature_review)
        self.assertIn("the product contract when selected", whole_feature_review)

    def test_resolved_open_questions_no_longer_read_as_open(self):
        questions = normalized("10-decisions-and-open-questions.md")
        history = normalized("14-v0.2-decisions.md")

        self.assertRegex(questions, r"OQ-003.{0,100}(RESOLVED|Resolved)")
        self.assertRegex(history, r"Exact semantics of `HUMAN_IF_CHANGED`.{0,160}(resolved|D-074)")


if __name__ == "__main__":
    unittest.main()
