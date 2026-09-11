# Specialist runbooks

Use this index when a concrete technical uncertainty or risk needs more detail than the core activity guides. Select the relevant reference, not the whole library. Ordinary clear work may need none.

The runbooks can guide the main agent or a bounded worker. Choose delegation for useful isolation, parallelism or independent judgment; a named runbook is not a new role, required handoff or workflow stage. A separate context is needed only when the assignment requires independence; the producer using another checklist remains self-review.

For a delegated task, provide the exact outcome/question, relevant source and candidate, accepted constraints, whether it is read-only or allows specified edits, the selected runbook path, permitted capabilities, expected evidence and stop/return boundary. The worker may use its judgment within that assignment. Reviewers report findings; Atlas reconciles them and retains scope/authority decisions. Do not delegate missing product judgment as though it were implementation work.

Carry the [entrypoint's runbook notice rule](../SKILL.md) into the brief, including any further delegation: report actual runbook use and purpose, including self-selected additions, through available progress messages and in the return. The lead keeps these notices visible in the main conversation.

Use existing approved project/host tools. Runbooks prescribe no additional tools, models or integrations. If a capability is absent, use a valid available method and state what it proves; do not silently substitute static inspection for execution or install tooling merely because a reference mentions it. A runbook grants no additional permissions. Keep work records in the project’s [approved artifact location](artifact-location.md), which may be a configured vault, outside this reusable library.

| Technical question or trigger | Reference |
| --- | --- |
| Effects of a change beyond the immediate diff or design | [Assess blast radius](blast-radius.md) |
| Unfamiliar behavior or code/spec disagreement | [Understand existing behavior](understand-behavior.md) |
| Why a design or constraint exists, or whether its original rationale still applies | [Reconstruct design rationale](reconstruct-rationale.md) |
| Create or repair a repeatable project verification path | [Establish project verification](project-verification.md) |
| Could errors become success, retries duplicate effects or work be lost? | [Failure handling](failure-handling.md) |
| What evidence would catch a regression or substantiate this change? | [Test adequacy](test-adequacy.md) |
| Invalid states, unit/identity confusion or mutation escape paths | [Types and invariants](types-and-invariants.md) |
| Material trust, authorization or sensitive-data boundary | [Security boundaries](security-boundaries.md) |
| Persistence correctness, query behavior or deployment migration | [Data and migrations](data-and-migrations.md) |
| Measured slowness, resource growth, captured profile or performance budget | [Performance](performance.md) |
| Compiler, dependency, startup or runtime failure | [Build/runtime diagnosis](build-and-runtime-diagnosis.md) |
| Behavior-preserving simplification or proven obsolete code | [Simplify and clean](simplify-and-clean.md) |
| Versioned API uncertainty, stale docs or misleading comments | [Documentation and references](documentation-and-references.md) |
| Lifetime, cancellation, concurrency or language semantics | [Language/runtime checks](language-runtime-checks.md) |
| Request/ORM/dependency lifecycle depends on framework semantics | [Service/framework checks](service-framework-checks.md) |
| Reactive state, stale responses, rendering or mobile lifecycle | [Client state checks](client-state-checks.md) |
| Interactive outcome, accessibility or public-page discoverability | [User journeys](user-journeys.md) |
| Substantial explanatory diagram, layout or faithful redraw | [Diagram craft](diagram-craft.md) |
| Training, inference, retrieval or grounded-answer quality | [Model and retrieval quality](model-and-retrieval-quality.md) |
| Package distribution or a change in information exposure | [Release preparation](release-preparation.md) |
| Recurring agent failure or a proposed instruction change | [Guidance improvement](guidance-improvement.md) |

These are questions to investigate, not automatic findings. Use only applicable checks and return evidence that changes the next decision. A supported zero-finding review is valid. For independent assurance, apply the existing [review contract](independent-review.md); for implementation, apply [delivery and repair](deliver-and-repair.md).
