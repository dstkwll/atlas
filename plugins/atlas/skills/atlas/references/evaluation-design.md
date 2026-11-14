# Design a useful evaluation

Use when turning a quality question, requirement or observed failure into an evaluation of an agent, AI feature or generated artifact. Start from the decision the evidence must support. A deterministic code regression may need only [Test adequacy](test-adequacy.md); evaluating instructions, tools or coordination also uses [Guidance improvement](guidance-improvement.md). Use the project's existing facilities. A useful evaluation does not require a particular framework, judge model, file format or service.

## Define what the result must distinguish

Identify the user outcome, candidate and relevant baseline. State what would change if the result were favorable, unfavorable or inconclusive. Keep accepted requirements separate from proposed quality preferences. Ask about a missing consequential expectation; do not invent a policy, threshold or expected answer to make the case executable. Continue independent design when a missing decision affects only one branch.

Name a plausible wrong result that a superficial check would accept, then a valid alternative the grader must accept. For an export, a file may exist but contain the wrong records; a different correct row order may be allowed. For a rewrite, a shorter answer may quietly turn permission into obligation. For an agent operation, the final state may be correct after an unauthorized intermediate action. These distinctions determine the evidence needed.

Choose a representative task from actual requirements or an authorized, minimized failure. Label synthetic examples and what they omit. A known failure makes a useful diagnostic or regression; it is not an independently held-out estimate of general quality. Add nearby ordinary requests when unwanted triggering or ceremony is a risk. Prefer a few cases that separate important behaviors over many paraphrases of the same easy task.

## Separate the task from the answer key

Give the actor the request, legitimate operating constraints, tools and source material a real caller would provide. Keep evaluator-only answers, hidden checks, scoring instructions and prior grader feedback outside every actor-visible path, including copied skills and nested fixture directories. A file named hidden is not a visibility boundary. Preview the actual staged environment rather than trusting the source layout.

For multi-turn work, specify which facts become available when, what a follow-up responds to and which state survives a restart. A fixed response to a question the actor never asked can change the task. Use a small controlled branch where needed, and distinguish a simulated user from observed human behavior. Native compaction, a fresh thread with saved files and replaying a transcript are different conditions.

Preserve the meaningful difficulty when minimizing an incident: the ambiguous acknowledgment, competing interpretation or stale source may be the cause. Remove unrelated and protected material within the approved data boundary. Keep provenance sufficient to understand the case without requiring access to private transcripts.

## Match each claim to available evidence

For each material requirement, connect the observable evidence, the check and the result that would contradict success. Use a small table if it helps; the relationships matter more than the format.

| Claim | Useful observation | What that observation alone cannot prove |
| --- | --- | --- |
| The requested artifact exists and works | File contents and an independently derived execution check | The actor used an authorized path or the artifact helps its next reader |
| The actor reconciled an uncertain write before retrying | Attributable operation events and reliable destination or terminal-operation evidence | An empty or unchanged final snapshot excludes transient effects |
| A rewrite preserved the instruction's meaning | Original and revision, important exceptions, and a representative downstream task | Matching numbers or modal words establishes equivalent obligations |
| A handoff enables the next step | A fresh intended consumer attempting the task with the permitted context | One consumer's success establishes universal clarity |

Use deterministic checks for properties that can be decided exactly. Use evidence-grounded judgment for meaning, usefulness and valid alternatives. A model judge is a measurement instrument that can be wrong; adding judges does not create independent truth. Keep objective facts distinct from the interpretation they support.

Inspect intermediate actions when sequence, authority or side effects matter. A tool-call name, announced consultation or successful process exit may not prove the relevant content was read or the intended test ran. Reused context and valid alternate tools may satisfy the requirement. Missing events, unreadable artifacts or unobserved effects leave the affected claim unknown; an observed violation is a failure even if a host blocked the effect. Not applicable is different from missing evidence.

Preserve requirement failures and unknowns beside any quality score. Define aggregation deliberately: an average can conceal an important failure, and an unknown is neither a pass nor a measured zero. Operational setup errors must remain distinct from actor behavior. No aggregate supplies release or acceptance authority.

## Challenge the grader before trusting a comparison

Try a known incorrect result, a correct result and a materially different valid alternative. Add a missing-evidence example when a claim relies on traces, external state or rendering. Check that the grader fails for the intended defect rather than a formatting preference or unrelated setup error. Retain the controls and disagreements.

For example, after a write acknowledgment is lost, an agent may list the destination and identify the item without another create. A final one-item check is useful, but cannot distinguish this from creating twice and later deleting a duplicate. Conversely, one combined command may be as valid as several commands. The grader needs the operation evidence for ordering, not a preferred command sequence.

When a semantic judge disagrees with the expected result, examine both the rubric and the reference judgment. Preserve ambiguous requirements rather than coaching the judge toward a favored answer. If the grader changes, version it and reconsider the applicability of earlier verdicts. Passing these controls establishes sensitivity on those examples, not general accuracy.

## Make the comparison interpretable

Choose the baseline that answers the question: an ordinary prompt for added value, the previous version for a regression, or an accepted simpler approach for a new system. Keep task, fixtures, authority, host, model, effort and tool access comparable except for declared differences. Record exact source identities and effective conditions where available; distinguish requested settings from observed ones.

Freeze independent cases before tuning when an improvement claim needs them. Case authors who saw the candidate or prior results may still contribute valuable diagnostics; record that exposure. Do not claim a tool can infer every prior exposure. Retain all attempts, adverse outcomes and setup failures. Decide repetition from variability and the consequence of the decision; do not rerun until the preferred condition wins. Repeated attempts on one task do not replace independent task coverage.

Assess useful outcome alongside intervention, review/repair burden, elapsed time and available resource measurements. Do not manufacture missing telemetry or infer human effort from tokens. For retrieval or predictive quality, use [Model and retrieval quality](model-and-retrieval-quality.md) for slices, leakage and data boundaries. For actual human learning or usability, use [User research](user-research.md); simulated participants cannot establish those outcomes.

## Return something another author can use

Provide the requested case, spec or plan with the raw task and setup clearly separated from grading material. Make its important requirements, evidence route, controls, comparison and prerequisites inspectable. Use the project's existing runnable format when specified and available; otherwise return a portable specification and identify the execution mapping still needed. Do not present invented framework fields or pseudocode as a validated runnable spec.

Distinguish authored, mechanically checked, grader-calibrated, executed and behaviorally reviewed results. State what was actually exercised, which cases were diagnostic or held out, the observed failures and remaining limits. An evaluation plan does not itself authorize live operations, publication, recurring execution or a new provider. Continue already-authorized execution within its bounds, or return the concrete prerequisite or decision that prevents it.
