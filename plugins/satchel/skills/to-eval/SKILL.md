---
name: to-eval
description: Turn a requirement, quality question or observed failure into an evaluation case or plan with meaningful evidence and graders. Use for eval design, not ordinary answering or an implied request to run a benchmark.
---

# To eval

Turn the user's concern into an evaluation that can distinguish useful work from a plausible failure. It may test an agent, AI feature, generated artifact or workflow. Work with the supplied requirements and available evidence; no framework, sibling skill or model provider is required. An ordinary question needs its answer, not an unsolicited eval.

## Find the distinction that matters

Identify the outcome and the decision the evaluation supports. Preserve the user's accepted scope and quality requirements. If a missing expectation would change what counts as success, ask for that distinction or leave the affected criterion explicitly unresolved while preparing the rest. Do not invent a product policy or numeric threshold to complete a rubric.

Name one plausible wrong result that an easy check would accept, and one valid alternative that should pass. A file can exist with the wrong contents; a fluent rewrite can strengthen an uncertain claim; a final correct state can follow an unauthorized action. These examples should expose the relevant distinction rather than prescribe one output style.

Use representative requests or authorized failure evidence. Label synthetic cases and the difficulty they preserve. A case built after seeing a failure is useful diagnostic or regression evidence, not a held-out demonstration of general improvement. Include a nearby ordinary request when misrouting is a plausible failure.

## Build the actor's task and the evaluator's evidence

Give the actor a natural request, realistic source material and legitimate operating constraints. Keep expected answers, hidden tests, grader instructions and earlier grader feedback separate from everything the actor receives. Check copied folders and references as well as top-level files; naming a file hidden does not hide it.

For a conversation, specify when information is revealed and what the next turn responds to. Do not force a reply that ignores the actor's actual question. Distinguish a continued session, transcript replay and recovery from saved artifacts. Simulated users may exercise interaction but do not establish real user satisfaction or learning.

Connect each material requirement to an observable result and an appropriate check:

- Use deterministic checks for exact properties such as required records, numerical results or a known effect.
- Use evidence-grounded judgment for meaning, usefulness and alternative correct approaches. A rubric should state the consequential distinction, not reward headings or the author's preferred wording.
- Inspect attributable events and resulting state when order, permissions or side effects matter. A command's presence does not establish successful execution, and final state alone may miss an intermediate violation.
- Keep missing or inaccessible evidence **unknown**, separate from an observed failure and from a criterion that does not apply. A critical failure must stay visible beside any quality score.

For example, after a create request loses its acknowledgment, exactly one intended item in storage is useful evidence. It does not establish that the actor reconciled the result before retrying. That claim also needs reliable operation evidence. One combined command and several commands may both implement a valid sequence.

If the intended observation is unavailable, say what remains untested and what would supply it. Do not substitute a keyword check for semantic understanding or a model report for an unobserved tool effect. For an artifact used by another person or agent, consider testing the next consumer's task as well as reading the artifact.

## Test the test and define the comparison

Provide a known-bad output or trace, a correct example and a materially different valid alternative. Include a missing-evidence control when relevant. Explain the expected judgment and why each control distinguishes the intended property. These expectations stay with the evaluator. When a grader is available, check that it recognizes the controls; otherwise label them prepared, not calibrated.

For a comparison, choose an ordinary-prompt, previous-version or other meaningful baseline. Identify what may differ and keep the other important conditions comparable, including host, model, effort, tools and fixtures. Preserve source identities, all attempts and setup failures. Choose repetition based on variability and the decision; avoid fixed trial counts presented as statistical assurance or rerunning until a favored answer passes. Prepare independent held-out cases before tuning when that claim matters.

Measure the user's outcome alongside unnecessary intervention, review burden, time or resource use when available. Do not invent measurements or average away important failures. Baseline ties and inconclusive findings are valid results.

## Deliver the evaluation at the requested level

Return the task/setup, grading criteria and evidence, controls, comparison conditions and any unresolved prerequisites in a form the next author or operator can use. Adapt the shape to the request; a short case needs no elaborate report. Use the project's existing eval format when available. If a specific framework is requested, verify its current field contract before presenting a runnable file; otherwise provide a portable spec and mark unmapped execution details.

Separate what you authored from what was checked, calibrated, executed or reviewed. State whether missing access, tool traces, rendering or human observations limit the conclusion. Design alone does not start trials, create a persistent goal, contact people, publish artifacts or schedule future work. Separately authorized execution keeps its existing scope. Save only where the user or project expects the artifact, never in the installed skill folder.
