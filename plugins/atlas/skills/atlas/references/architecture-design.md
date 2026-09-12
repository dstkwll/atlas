# Architecture design

Use when accepted behavior still permits materially different responsibilities, interfaces, ownership or dependencies, or repeated implementation friction challenges the structure. A clear local realization can stay in ordinary delivery. Unsettled product intent belongs in [Discover and design](discover-and-design.md).

Develop a coherent design from the actual project. Enter at the unresolved decision, reuse settled work and revisit assumptions when evidence changes. The activities below are reasoning aids, not a sequence to exhaust, a quota of alternatives or a requirement to create another document.

## Establish the decision and affected path

Recover the accepted outcome, constraints and current assignment. Separate inspected behavior, accepted architecture, provisional choices and missing judgment. State the decision that matters now and what it could change. Use [behavior tracing](understand-behavior.md) or [design rationale](reconstruct-rationale.md) when facts or the reason for a constraint are unclear.

Follow the relevant inputs, decisions, state and outputs through the real system and proposed change. Identify who owns each rule, what callers or operators must coordinate, and where errors become observable. Inspect enough surrounding code, configuration and operational context to understand the whole affected path. Do not judge a component only by its internal elegance.

An interface includes what its caller must know: invariants, ordering, errors, configuration, ownership and relied-on performance guarantees. A usage sketch, type/ownership map, call flow or concise prose can expose these obligations. Use the actual task and names; distinguish current from proposed behavior. Add detail where it prevents expensive divergence, while leaving local implementation choices open.

## Develop and compare credible options

Consider keeping or simplifying the existing structure alongside other viable approaches when there is a real choice. For each, make the consequential responsibility and data ownership, dependencies, failure/recovery and verification boundaries clear. Prefer cohesion, information hiding and narrow contracts; an abstraction needs a current consumer and a problem it prevents. Preserve conventions unless evidence justifies changing them.

Compare options against the same task-specific criteria. Relevant questions include the user outcome, caller burden, duplicated knowledge, shared mutable state, temporal coupling, compatibility, operability, reversibility, access for verification and ongoing maintenance. Use small sketches of the same caller task when that exposes a consequential interface difference. Fewer methods or a shorter call sequence is not automatically better if it hides necessary control or loses guarantees. Do not manufacture alternatives when the constraints determine the answer.

Use [Types and invariants](types-and-invariants.md) when rule enforcement or ownership is uncertain, [Blast radius](blast-radius.md) when effects reach beyond the immediate change, and other specialists for their specific uncertainties. These do not require a panel of agents.

## Resolve the uncertainty that changes the choice

Choose evidence that can discriminate between viable designs: source inspection, a contract check, an authorized bounded probe or independent comparison. Name the uncertainty, what observation would change the recommendation, and the practical effort and side-effect bounds before a probe. An executable prototype is useful only when it answers the question; unavailable hardware or a failed setup does not establish architectural failure or success.

When independent competing proposals would materially help, offer [Arena](arena.md) with its existing confirmation and bounds before launching. For equipment-dependent claims, [Project verification](project-verification.md) separates available evidence from what remains to be established. Do not make an unavailable proof a blanket stop on unrelated authorized design work.

## Reconcile one design and its decision boundary

Synthesize compatible choices into one proposal. Trace the affected path again: do responsibilities, state ownership, caller obligations and failure behavior fit together? Do not combine attractive pieces whose assumptions conflict. State the recommendation, rationale, meaningful tradeoffs and strongest counterargument together with the supporting evidence and limits.

Distinguish accepted decisions, proposals, discovered facts and provisional implementation choices. Return consequential judgment to its owner when it is not already delegated, making the practical consequences and dependent work clear. Continue unaffected authorized preparation. Record material choices with their rationale and source of authority through [Continuity and decisions](continuity-and-decisions.md).

Before handoff, check whether a reasonable implementer can preserve the intended outcome without inventing architecture. Identify the rule-owning boundaries, observable acceptance and failure behavior, allowed implementation latitude, unresolved decisions and evidence that would require reconsideration. Do not prescribe helpers or future extensibility without a present consequence. A complete design does not authorize implementation.

Update the existing brief, PRD or architecture record with the useful result. An architecture section in the PRD may suffice. Use [documentation](to-documentation.md), [HTML document](html-document.md) and [diagram](diagram-craft.md) guidance when the presentation warrants them; retain one source of record without a mandatory extra file or Markdown twin. Close with the next useful activity under the current assignment.
