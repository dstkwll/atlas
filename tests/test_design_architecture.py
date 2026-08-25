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


def separate_compilation_controller_violations(text):
    """Return affirmative clauses that give Stage 5 a separate state owner."""
    violations = []
    normalized_text = " ".join(text.split())
    for clause in re.split(r"(?<=[.!?;])\s+|\n+", normalized_text):
        lower = clause.lower()
        if not re.search(r"(?:separate|distinct|third) (?:ticket |stage 5 )?(?:compilation|handoff) controller", lower):
            continue
        if re.search(r"\b(?:no|not|never|neither|cannot|must not|may not|should not|does not|do not|reject(?:s|ed)?)\b", lower):
            continue
        violations.append(clause)
    return violations


def known_stage_five_contract_regressions(text):
    """Return exact normalized stale literals observed in prior Stage 5 prose.

    This deliberately does not classify arbitrary paraphrases or semantics.
    """
    stale_literals = (
        "tickets: auto",
        "factory run <ticket.md>",
        "factory run tickets/01.md",
        "approved markdown ticket",
        "preflight approved contract",
        "approved vertical ticket",
        "approved planning packet",
    )
    normalized_text = " ".join(text.split()).lower()
    return [literal for literal in stale_literals if literal in normalized_text]


class PairedDesignArchitectureTests(unittest.TestCase):
    def test_v014_d086_is_current_and_prior_repair_boundaries_remain(self):
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        architecture_readme = read("README.md")
        v08_decisions = read("23-v0.8-decisions.md")
        v09_decisions = normalized("24-v0.9-decisions.md")
        v10_path = ARCH / "25-v0.10-decisions.md"
        v11_path = ARCH / "26-v0.11-decisions.md"
        v12_path = ARCH / "27-v0.12-decisions.md"
        v13_path = ARCH / "28-v0.13-decisions.md"
        v14_path = ARCH / "29-v0.14-decisions.md"

        self.assertTrue(v10_path.exists(), "v0.10/D-082 decision record is absent")
        self.assertTrue(v11_path.exists(), "v0.11/D-083 decision record is absent")
        self.assertTrue(v12_path.exists(), "v0.12/D-084 decision record is absent")
        self.assertTrue(v13_path.exists(), "v0.13/D-085 decision record is absent")
        self.assertTrue(v14_path.exists(), "v0.14/D-086 decision record is absent")
        v10_decisions = normalized("25-v0.10-decisions.md")
        v11_decisions = normalized("26-v0.11-decisions.md")
        v12_decisions = normalized("27-v0.12-decisions.md")
        v13_decisions = normalized("28-v0.13-decisions.md")
        v14_decisions = normalized("29-v0.14-decisions.md")
        workflow = normalized("02-workflow.md")
        artifacts = normalized("03-artifact-model.md")
        control = normalized("04-control-plane.md")
        review = normalized("06-review-and-validation.md")
        execution = normalized("05-execution-factory.md")
        borrow_map = normalized("15-reference-implementation-borrow-map.md")
        state = normalized("08-state-and-governance.md")
        runtime = normalized("13-runtime-protocol.md")
        learnings = normalized("16-learnings-and-course-corrections.md")
        combined = " ".join((v10_decisions, workflow, artifacts, control, review, state, runtime))
        stage5 = " ".join((v12_decisions, v13_decisions, workflow, artifacts, execution, review))

        self.assertIn("architecture/29-v0.14-decisions.md", root_readme)
        self.assertIn("**v0.14**", root_readme)
        self.assertIn("**v0.14**", architecture_readme)
        self.assertIn("D-086", v14_decisions)
        self.assertIn("v0.14 north star", v14_decisions.lower())
        self.assertIn("D-085", v13_decisions)
        self.assertIn("v0.13 north star", v13_decisions.lower())
        self.assertRegex(v13_decisions, r"D-080's one accepted ticket graph execution-complete")
        self.assertRegex(stage5, r"dependency remains a real prerequisite")
        self.assertRegex(stage5, r"first (?:currently )?ready ticket in canonical graph order")
        self.assertRegex(stage5, r"continue.{0,40}resume.{0,180}(?:does not satisfy|never grants)")
        self.assertRegex(stage5, r"deterministic.{0,80}(?:execution|worker) brief")
        self.assertRegex(stage5, r"raw user prompt.{0,100}(?:not a coequal|rather than a coequal)")
        self.assertRegex(stage5, r"reject self-dependencies and cycles")
        for proof_contract in (v13_decisions, review):
            self.assertRegex(proof_contract, r"(?i)promised behavioral outcome.{0,180}deterministic validators/evidence")
            self.assertRegex(proof_contract, r"(?i)review gates.{0,180}supplement.{0,180}(?:never|may not) substitute.{0,180}deterministic proof.{0,180}outcome-bearing")
        self.assertRegex(v13_decisions, r"adds no graph, brief, external-prerequisite.{0,220}runtime-state schema")
        self.assertRegex(v13_decisions, r"without adding another graph, planner, controller, or runtime")
        self.assertRegex(borrow_map, r"SSSF also reuses named reviewer sessions.{0,180}fresh reviewer context")
        self.assertRegex(borrow_map, r"execution-time planner.{0,220}deterministically.{0,100}worker brief")
        self.assertIn("D-084", v12_decisions)
        self.assertIn("v0.12 north star", v12_decisions.lower())
        for invariant in ("Outcome-bearing", "Cross-boundary where required", "Independently verifiable", "No redesign"):
            self.assertIn(invariant, v12_decisions)
        self.assertIn("every boundary required by that behavior", stage5)
        self.assertRegex(stage5, r"Selected Program Design.{0,100}exact acceptance")
        self.assertRegex(stage5, r"otherwise.{0,100}applicable source")
        self.assertRegex(stage5, r"enabling ticket.{0,220}imminent vertical slice.{0,220}cannot safely")
        self.assertRegex(stage5, r"riskiest or most important seams")
        self.assertIn("rejects horizontal slabs", stage5)
        self.assertRegex(v12_decisions, r"`trivial` path remains one one-node graph")
        self.assertRegex(v12_decisions, r"adds no graph schema.{0,180}compiler.{0,180}execution runtime")
        self.assertIn("D-083", v11_decisions)
        self.assertIn("v0.11 north star", v11_decisions.lower())
        self.assertRegex(v11_decisions, r"ends Atlas's autonomous authority.{0,120}does not.{0,100}declare the user's goal dead")
        for direction in (
            "another materially different System Design approach",
            "upstream product commitment",
            "corrected successor run",
            "stop or defer",
        ):
            self.assertIn(direction, v11_decisions)
        self.assertIn("D-083 adds no controller transition", v11_decisions)
        self.assertIn("does not add a recovery runtime", v11_decisions)
        self.assertRegex(v11_decisions, r"next substantive implementation remains the Stage 5 Ticket Graph Compiler")
        self.assertIn("D-080", v08_decisions)
        self.assertIn("Refined by D-082", v08_decisions)
        self.assertIn("D-081", v09_decisions)
        self.assertIn("Refined by D-082", v09_decisions)
        self.assertIn("D-082", v10_decisions)
        self.assertIn("v0.10 north star", v10_decisions.lower())
        self.assertRegex(combined, r"(?i)every repair replacement.{0,180}hash-bound system design evidence envelope")
        self.assertIn("`repair_context`", combined)
        self.assertRegex(combined, r"direct `HUMAN`.{0,180}(?:evidence )?envelope")
        self.assertRegex(combined, r"semantic/materiality fields.{0,80}null")
        self.assertRegex(combined, r"grants no authority.{0,160}human approval remains the acceptance authority")
        self.assertRegex(
            combined,
            r"conditional repair evidence.{0,160}not a normal-path review requirement.{0,180}(?:does not|nor does it) widen.{0,80}acceptance schema",
        )

        self.assertIn("reviews/program-design-upstream-block-v1.json", combined)
        for verdict in (
            "CONFIRMED_UPSTREAM_CONTRADICTION",
            "NOT_CONFIRMED",
            "UNAVAILABLE",
        ):
            self.assertIn(verdict, combined)
        self.assertRegex(
            combined,
            r"exact accepted System Design.{0,260}exact frozen repository evidence.{0,260}cannot faithfully realize",
        )
        self.assertRegex(combined, r"only `CONFIRMED_UPSTREAM_CONTRADICTION`.{0,120}(?:mutate|changes)")
        self.assertRegex(
            combined,
            r"status.{0,40}`BLOCKED`.{0,140}phase.{0,40}`system_design`.{0,180}gate.{0,80}`STALE`",
        )
        self.assertRegex(combined, r"prior acceptance.{0,120}non-current")
        self.assertRegex(combined, r"Program Design.{0,100}`PENDING`.{0,100}null acceptance")
        self.assertRegex(combined, r"existing `blocked_reason`.{0,180}revision")
        self.assertRegex(
            combined,
            r"System Design N\+1.{0,260}Program Design.{0,160}status remains `BLOCKED`.{0,220}`PLANNING`",
        )
        self.assertRegex(combined, r"version `N\+1`.{0,120}different (?:content )?hash")
        self.assertRegex(combined, r"same still-current source binding")
        self.assertRegex(combined, r"fresh review.{0,160}unchanged configured authority")
        self.assertRegex(combined, r"immediate superseded acceptance.{0,160}contradiction provenance")
        self.assertIn("complete validated contradiction finding", combined)
        self.assertRegex(combined, r"contradiction (?:envelope )?reference/hash")
        self.assertRegex(
            combined,
            r"original no-clobber upstream-block envelope.{0,180}authoritative.{0,160}complete predecessor acceptance",
        )
        self.assertRegex(
            combined,
            r"complete immediate predecessor System Design acceptance.{0,600}JSON-type-sensitive equality",
        )
        self.assertRegex(
            combined,
            r"copied immediate predecessor grants no authority.{0,180}(?:never|not).{0,80}(?:competing|second).{0,40}(?:source of truth|truth)",
        )
        self.assertRegex(v10_decisions, r"candidate content itself is not copied")

        self.assertRegex(combined, r"exactly four.{0,120}producer attempts")
        self.assertRegex(combined, r"reserves.{0,100}before.{0,100}candidate (?:bytes|write)")
        self.assertRegex(combined, r"crash.{0,80}consumes")
        self.assertRegex(combined, r"reviews.{0,180}controller actions.{0,180}approvals.{0,120}do not")
        self.assertRegex(combined, r"restart.{0,100}(?:cannot|does not).{0,80}reset")
        self.assertRegex(combined, r"second contradiction.{0,100}(?:cannot|must not).{0,120}(?:nest|reset)")
        self.assertRegex(combined, r"exhaustion.{0,120}(?:loud|durable)")

        self.assertRegex(combined, r"invalidation and replacement.{0,120}not rollback")
        for excluded in (
            "Product Closure",
            "direct Stage 0",
            "accepted Program Design",
            "Stage 5",
            "D-077",
        ):
            self.assertIn(excluded, v10_decisions)
        self.assertRegex(v09_decisions, r"Refined by D-082.{0,260}new run")
        self.assertRegex(learnings, r"session-local.{0,120}four.{0,160}not durable")
        self.assertRegex(learnings, r"controller-owned.{0,120}persisted before.{0,80}writes")
        self.assertRegex(runtime, r"no Stage 6\+ execution.{0,200}execution-repair")
        self.assertRegex(runtime, r"D-082.{0,160}planning-repair episode.{0,160}pre-execution planning control")

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
        decisions_v8 = normalized("23-v0.8-decisions.md") if (ARCH / "23-v0.8-decisions.md").exists() else ""
        combined = " ".join((state, control, artifacts, decisions, decisions_v8))

        self.assertRegex(combined, r"separate Stage 3 and Stage 4 (?:gate/acceptance|gate and acceptance|outcomes)")
        self.assertRegex(combined, r"exact candidate/version/hash bindings")
        self.assertIn("staleness", combined)
        self.assertRegex(combined, r"does not widen (?:the )?Stage 0–2 `control.json`|does not widen this file")
        self.assertRegex(combined, r"does not introduce a generalized router|not a generalized router")

    def test_stage_five_prose_regressions_ignore_harmless_evidence_recording(self):
        for clause in (
            "Preflight records evidence that graph acceptance is current.",
            "Execution creates an audit event containing the accepted graph status it consumed.",
            "The runtime records the hash of the graph acceptance it verified.",
        ):
            with self.subTest(clause=clause):
                self.assertEqual([], known_stage_five_contract_regressions(clause))

    def test_downstream_planning_controller_owns_design_and_ticket_graph_acceptance(self):
        workflow = normalized("02-workflow.md").lower()
        artifacts = normalized("03-artifact-model.md").lower()
        control = normalized("04-control-plane.md").lower()
        factory = normalized("05-execution-factory.md").lower()
        state = normalized("08-state-and-governance.md").lower()
        runtime = normalized("13-runtime-protocol.md").lower()
        decisions = (
            normalized("23-v0.8-decisions.md").lower()
            if (ARCH / "23-v0.8-decisions.md").exists()
            else ""
        )
        combined = " ".join((workflow, artifacts, control, factory, state, runtime, decisions))

        self.assertRegex(decisions, r"downstream planning controller.{0,220}stage 3.{0,120}stage 4.{0,180}stage 5")
        self.assertRegex(decisions, r"one (?:logical )?(?:mutable |deterministic )?authority.{0,220}pre-execution")
        self.assertIn(
            "binds the exact graph version/hash to every source that actually governs compilation",
            decisions,
        )
        self.assertRegex(decisions, r"every branch also binds.{0,180}frozen baseline of each target repository")
        self.assertRegex(combined, r"ticket graph.{0,200}(?:version|versioned).{0,100}(?:sha-256|hash)")
        self.assertRegex(combined, r"ticket graph.{0,260}applicable accepted upstream")
        self.assertRegex(combined, r"ticket graph.{0,260}(?:repository|repo).{0,80}baseline")
        stage_five_control = control.split("stage 5 has its own boundary", 1)[1].split("---", 1)[0]
        self.assertRegex(
            stage_five_control,
            r"compiler proposes.{0,180}(?:read-only )?ticket-graph judge.{0,180}authority.{0,180}controller records",
        )

        self.assertRegex(
            combined,
            r"(?:system design|program design).{0,300}(?:change|stale).{0,260}ticket graph.{0,160}stale",
        )
        self.assertRegex(
            state,
            r"(?:same|one) logical atomic transition.{0,120}system design.{0,100}program design.{0,100}ticket graph",
        )
        self.assertRegex(factory, r"preflight.{0,300}(?:verifies|validates).{0,180}accepted ticket[- ]graph")
        self.assertRegex(factory, r"preflight.{0,300}(?:does not|cannot|must not).{0,180}(?:create|record|manufacture).{0,100}acceptance")
        commit_contract = factory.split("## commit ownership", 1)[1].split("---", 1)[0]
        self.assertRegex(commit_contract, r"immediately before.{0,100}commit.{0,180}revalidate.{0,160}(?:accepted ticket[- ]graph|graph acceptance)")
        self.assertRegex(commit_contract, r"(?:stale|mismatch).{0,160}(?:must not|no).{0,80}commit.{0,160}design_blocked")

        self.assertRegex(decisions, r"ends at stage 5|owns no stage 6\+")
        self.assertRegex(decisions, r"no (?:ticket )?execution state|owns no.{0,100}(?:execution|worktree|repair|commit)")
        self.assertRegex(decisions, r"not storage mechanics.{0,160}exact file.{0,180}(?:program design|implementation)")
        self.assertEqual([], separate_compilation_controller_violations(combined))

        for clause, forbidden in (
            ("A separate compilation controller owns the Stage 5 gate.", True),
            ("A distinct handoff controller records ticket graph acceptance.", True),
            ("A third Stage 5 compilation controller propagates staleness.", True),
            ("There is no separate compilation controller for Stage 5.", False),
            ("The architecture rejects a distinct handoff controller.", False),
            ("Stage 5 must not introduce a separate compilation controller.", False),
        ):
            with self.subTest(clause=clause):
                self.assertEqual(bool(separate_compilation_controller_violations(clause)), forbidden)

        d080_normative = decisions.split("### rejected alternatives", 1)[0]
        active_contract = " ".join((d080_normative, stage_five_control, factory, state, runtime))
        self.assertEqual([], known_stage_five_contract_regressions(active_contract))

        for stale_literal in (
            "tickets: AUTO",
            "factory run <ticket.md>",
            "factory run tickets/01.md",
            "approved Markdown ticket",
            "preflight approved contract",
            "approved vertical ticket",
            "approved planning packet",
        ):
            with self.subTest(stale_literal=stale_literal):
                self.assertTrue(known_stage_five_contract_regressions(stale_literal))

    def test_trivial_workflow_uses_one_stage_zero_bound_ticket_without_design_artifacts(self):
        start_run = (ROOT / "plugins" / "atlas" / "skills" / "start-run" / "SKILL.md").read_text(encoding="utf-8").lower()
        config = normalized("09-reference-config.md").lower()
        workflow = normalized("02-workflow.md").lower()
        artifacts = normalized("03-artifact-model.md").lower()
        runtime = normalized("11-runtime-topology.md").lower()
        factory_design = normalized("05-execution-factory.md").lower()
        questions = normalized("10-decisions-and-open-questions.md").lower()
        borrow_map = normalized("15-reference-implementation-borrow-map.md").lower()
        v02_scope = normalized("14-v0.2-decisions.md").lower()
        decisions = (
            normalized("23-v0.8-decisions.md").lower()
            if (ARCH / "23-v0.8-decisions.md").exists()
            else ""
        )

        self.assertIn("`trivial` — direct ticket/execution with no discovery or design producer", start_run)
        trivial = config.split("trivial:", 1)[1].split("normal:", 1)[0]
        self.assertRegex(trivial, r"stages:.{0,80}- tickets.{0,80}- execute")
        self.assertNotRegex(trivial, r"discovery|prd|system_design|program_design")
        self.assertNotRegex(config, r"tickets:\s+auto")

        self.assertRegex(decisions, r"trivial.{0,180}one-node ticket graph")
        self.assertRegex(decisions, r"no (?:product closure|prd).{0,120}system design.{0,120}program design.{0,260}frozen stage 0")
        for field in ("control.json.base_run_sha256", "effective_config_hash", "effective_config_revision"):
            self.assertIn(field, decisions)
        self.assertRegex(decisions, r"baseline of each target repository.{0,260}one one-node ticket graph")
        self.assertRegex(decisions, r"does not (?:require|manufacture).{0,180}(?:prd|system design|program design)")
        self.assertRegex(workflow, r"intake clarifications.{0,220}direct.{0,80}ticket")
        self.assertRegex(workflow, r"(?:unresolved product decisions|product decisions.{0,60}unresolved).{0,160}discovery")
        self.assertRegex(artifacts, r"trivial.{0,180}one-node graph.{0,260}frozen stage 0")

        tracer = workflow.split("## stage 6 — optional tracer checkpoint", 1)[1].split("## stage 7", 1)[0]
        self.assertIn("exact accepted ticket graph", tracer)
        self.assertNotIn("approved design", tracer)
        direct_runtime = runtime.split("### v1 normal path: direct execution", 1)[1].split("### future/exception", 1)[0]
        self.assertIn("exact accepted ticket-graph", direct_runtime)
        self.assertNotRegex(direct_runtime, r"approved ticket\s+↓\s+deterministic ticket factory")
        self.assertRegex(
            questions,
            r"execution-runtime implementation details.{0,220}d-086's fixed repo/run workspace",
        )
        trivial_live_contract = " ".join((decisions, workflow, config, runtime, questions, borrow_map))
        self.assertEqual([], known_stage_five_contract_regressions(trivial_live_contract))
        implementation_strategy = borrow_map.split("# recommended implementation baseline strategy", 1)[1].split("# source-handling policy", 1)[0]
        self.assertIn("exact accepted ticket-graph", implementation_strategy)
        self.assertRegex(implementation_strategy, r"graph acceptance.{0,180}applicable upstream.{0,180}(?:repository|target) baseline")
        self.assertNotIn("approved markdown ticket", implementation_strategy)
        self.assertNotRegex(implementation_strategy, r"factory run tickets/")
        self.assertIn("exact accepted ticket graph", v02_scope)
        self.assertNotIn("approved markdown ticket", v02_scope)
        ticket_factory_entry = factory_design.split("## ticket factory", 1)[1].split("---", 1)[0]
        self.assertIn("exact accepted ticket-graph", ticket_factory_entry)
        self.assertNotIn("factory run <ticket.md>", ticket_factory_entry)
        d001 = questions.split("### d-001", 1)[1].split("---", 1)[0]
        self.assertRegex(d001, r"refined by.{0,80}d-080")
        self.assertRegex(d001, r"\*\*decision:\*\*.{0,100}exact accepted ticket graph.{0,120}selected ready vertical ticket")
        self.assertNotIn("approved vertical ticket", d001)

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

    def test_v014_execution_reconciliation_is_bounded_and_horizon_is_noncanonical(self):
        decision_path = ARCH / "29-v0.14-decisions.md"
        horizon_path = ARCH / "v2-horizon.md"
        self.assertTrue(decision_path.is_file(), "v0.14/D-086 decision record is absent")
        self.assertTrue(horizon_path.is_file(), "the non-authoritative V2 horizon is absent")

        decisions = normalized("29-v0.14-decisions.md").lower()
        v02 = normalized("14-v0.2-decisions.md").lower()
        execution = normalized("05-execution-factory.md").lower()
        review = normalized("06-review-and-validation.md").lower()
        state = normalized("08-state-and-governance.md").lower()
        topology = normalized("11-runtime-topology.md").lower()
        trust = normalized("12-capabilities-and-trust.md").lower()
        runtime = normalized("13-runtime-protocol.md").lower()
        borrow_map = normalized("15-reference-implementation-borrow-map.md").lower()
        borrow_raw = read("15-reference-implementation-borrow-map.md").lower()
        warren = borrow_raw.split("# 10. jaymin west — warren", 1)[1].split("# 11.", 1)[0]
        sandcastle = borrow_raw.split("# 13. matt pocock — sandcastle", 1)[1].split("# 14. irtechie", 1)[0]
        sandcastle_proof = sandcastle.split("## proof-of-fit boundary", 1)[1].split("## likely implementation role", 1)[0]
        working_skill_repo = borrow_raw.split("# 14. irtechie — working skill repo", 1)[1].split("# cross-source", 1)[0]
        roles = normalized("17-agent-roles-rosters-and-model-policy.md").lower()
        horizon = normalized("v2-horizon.md").lower()
        monolith = normalized("rolling-monolith.md").lower()
        combined = " ".join((decisions, execution, state, topology, trust, runtime, roles))
        runtime_reviewer_example = runtime.split("## example reviewer envelope", 1)[1].split("## planning control state", 1)[0]
        review_schema = review.split("## reviewer output should be structured", 1)[1].split("## reviewer write policy", 1)[0]

        self.assertIn("d-086", decisions)
        self.assertRegex(decisions, r"no new controller.{0,120}planner.{0,120}scheduler.{0,120}provider")
        self.assertRegex(topology, r"one persistent local execution worktree.{0,180}atlas run.{0,100}repository.{0,180}accepted-commit chain")
        self.assertRegex(topology, r"logical ticket workcell.{0,80}per-ticket")
        self.assertRegex(combined, r"only one ticket.{0,80}active.{0,120}repository-scoped v1")
        self.assertRegex(runtime, r"run\.json.{0,120}machine-canonical")
        self.assertRegex(runtime, r"events\.jsonl.{0,120}(?:not|never).{0,80}(?:transition|state).{0,80}authority")
        self.assertRegex(runtime, r"condition identity.{0,200}observable satisfaction rule.{0,200}resume/recheck action")
        self.assertRegex(runtime, r"run/ticket/graph.{0,180}(?:head|tree).{0,180}validator semantics")
        self.assertRegex(runtime, r"expected accepted-chain head.{0,220}canonical candidate-tree identity")
        self.assertRegex(execution, r"canonical candidate-tree identity.{0,220}validators?.{0,220}review")
        self.assertRegex(review, r"ticket-review envelope.{0,180}same canonical candidate-tree identity")
        self.assertIn("candidate_tree_identity", runtime_reviewer_example)
        self.assertIn("candidate_tree_identity", review_schema)
        self.assertRegex(execution, r"immediately before any commit.{0,400}to-be-committed tree.{0,200}canonical candidate-tree identity")
        self.assertRegex(execution, r"candidate-tree mismatch.{0,180}stale.{0,180}rerun")
        self.assertRegex(execution, r"exact integrated commit-chain tip/tree.{0,180}promotion")
        self.assertRegex(execution, r"later (?:tree|head).{0,80}change.{0,100}stale")
        self.assertRegex(review, r"exact integrated accepted-commit-chain tip/tree.{0,220}later head/tree change.{0,100}stale")
        self.assertRegex(combined, r"evidence.{0,80}before.{0,80}(?:destructive )?cleanup")
        self.assertRegex(topology, r"before destructive cleanup.{0,160}required execution evidence.{0,120}harvest")
        self.assertRegex(trust, r"same supervisor-selected worker attempt.{0,220}same workspace.{0,180}authority envelope")
        self.assertRegex(trust, r"(?:helper|child) agents?.{0,220}(?:no atlas identity|cannot own or accept)")
        self.assertRegex(v02, r"feature worktree vs ticket worktree.{0,220}resolved/refined.{0,120}v0\.14.{0,80}d-086")
        self.assertRegex(v02, r"exact local rollback/protection mechanics remain open.{0,80}item 3")
        self.assertRegex(" ".join(warren.split()), r"v1 evidence-before-cleanup invariant.{0,120}deferred full ephemeral")
        self.assertIn("e99f832f26dc9d245c019a9ddd19fa5dee792427", sandcastle)
        self.assertRegex(" ".join(sandcastle.split()), r"license verified.{0,80}mit")
        implementation_rows = [
            line for line in sandcastle.splitlines()
            if "implementation_reference" in line or "implementation reference" in line
        ]
        self.assertEqual(5, len(implementation_rows))
        for row in implementation_rows:
            self.assertIn("adapt / spike", row)
        self.assertIn("sandcastle is not yet an atlas dependency", sandcastle)
        self.assertEqual(12, len(re.findall(r"(?m)^\d+\.", sandcastle_proof)))
        for scenario in (
            "exact-baseline worktree acquisition",
            "builder invocation from a deterministic atlas brief",
            "schema-valid result",
            "deterministic validator execution in the same environment",
            "same-builder-context repair",
            "fresh findings-only reviewer invocation",
            "reviewer mutation detection/restoration",
            "stale graph/upstream/head prevents commit",
            "atlas performs the clean-path deterministic commit",
            "outer-process restart can reacquire legal state and supported session context",
            "timeout/abort/log/evidence extraction behavior",
            "without persisting sandcastle types as engineering truth",
        ):
            self.assertIn(scenario, sandcastle_proof)
        self.assertIn("91a1b2f206dc5a6304c913df62426996b61603a1", working_skill_repo)
        self.assertRegex(" ".join(working_skill_repo.split()), r"license verified.{0,80}mit")
        self.assertRegex(combined, r"implementation completion.{0,180}(?:not|separate).{0,120}delivery completion|implementation completion.{0,220}delivery completion.{0,120}separate")
        learnings = normalized("16-learnings-and-course-corrections.md").lower()
        self.assertIn("l-025", learnings)
        self.assertRegex(learnings, r"evidence-before-cleanup.{0,180}v1.{0,220}(?:worktree|local)")
        self.assertRegex(learnings, r"v1 evidence-before-cleanup.{0,180}accepted.{0,220}full ephemeral.{0,180}future")

        self.assertIn("status: non-authoritative horizon", horizon)
        self.assertIn("not part of the numbered canonical architecture", horizon)
        self.assertNotIn("# atlas v2 horizon", monolith)
        canonical_names = {path.name for path in ARCH.glob("[0-9][0-9]-*.md")}
        self.assertNotIn("v2-horizon.md", canonical_names)

    def test_resolved_open_questions_no_longer_read_as_open(self):
        questions = normalized("10-decisions-and-open-questions.md")
        history = normalized("14-v0.2-decisions.md")

        self.assertRegex(questions, r"OQ-003.{0,100}(RESOLVED|Resolved)")
        self.assertRegex(history, r"Exact semantics of `HUMAN_IF_CHANGED`.{0,160}(resolved|D-074)")


if __name__ == "__main__":
    unittest.main()
