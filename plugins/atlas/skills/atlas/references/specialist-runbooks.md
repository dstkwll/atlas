# Specialist runbooks

Use this index when a matching activity, changed boundary, observed failure or concrete uncertainty calls for a focused method beyond the core activity guides. Cleanup, distribution, documentation impact and recurring guidance failures can qualify without an already-diagnosed technical defect. Select the relevant reference, not the whole library. Ordinary clear work may need none.

Several references may inform one decision. Connect their relevant findings against the task's goal and accepted constraints; return a coherent result rather than a collection of checklists. Revisit selection when new evidence changes the question. The [lead](../SKILL.md#choose-and-combine-useful-methods) owns composition and scope.

The runbooks can guide the main agent or a bounded worker. Choose delegation for useful isolation, parallelism or independent judgment; a named runbook is not a new role, required handoff or workflow stage. A separate context is needed only when the assignment requires independence; the producer using another checklist remains self-review.

For a delegated task, provide the exact outcome/question, relevant source and candidate, accepted constraints, whether it is read-only or allows specified edits, the selected runbook path, permitted capabilities, expected evidence and stop/return boundary. The worker may use its judgment within that assignment. Reviewers report findings; Atlas reconciles them and retains scope/authority decisions. Do not delegate missing product judgment as though it were implementation work.

Carry the [entrypoint's runbook notice rule](../SKILL.md) into the brief, including any further delegation: report actual runbook use and purpose, including self-selected additions, through available progress messages and in the return. The lead keeps these notices visible in the main conversation.

Use existing approved project/host tools. Runbooks prescribe no additional tools, models or integrations. If a capability is absent, use a valid available method and state what it proves; do not silently substitute static inspection for execution or install tooling merely because a reference mentions it. A runbook grants no additional permissions. Keep work records in the project’s [approved artifact location](artifact-location.md), which may be a configured vault, outside this reusable library.

| Activity, question or trigger | Reference |
| --- | --- |
| Consequential structure or interface choices within accepted behavior | [Architecture design](architecture-design.md) |
| Interdependent contributions, shared resources or integration uncertainty | [Coordinate work](coordinate-work.md) |
| Effects of a change beyond the immediate diff or design | [Assess blast radius](blast-radius.md) |
| Unfamiliar behavior or code/spec disagreement | [Understand existing behavior](understand-behavior.md) |
| Why a design or constraint exists, or whether its original rationale still applies | [Reconstruct design rationale](reconstruct-rationale.md) |
| Create or repair project verification, including E2E suite setup and parallel-test failures | [Establish project verification](project-verification.md) |
| Could errors become success, retries duplicate effects or work be lost? | [Failure handling](failure-handling.md) |
| Choose regression evidence, test-first work (TDD), or checks for a change | [Test adequacy](test-adequacy.md) |
| Changed data models, states, units, APIs or mutation ownership; invalid states or mutation escape paths | [Types and invariants](types-and-invariants.md) |
| Security review; changed or uncertain identity, permissions, credentials, personal-data lifecycle or model/tool authority; untrusted input/reachability affecting a security property | [Security boundaries](security-boundaries.md) |
| Persistence, query or migration correctness; backup/restore, deletion/retention or recovery claims | [Data and migrations](data-and-migrations.md) |
| Slowness, measured regression, resource growth, profile, performance budget or cost per useful operation | [Performance](performance.md) |
| Compiler, dependency, startup or runtime failure | [Build/runtime diagnosis](build-and-runtime-diagnosis.md) |
| Authorized cleanup/refactor or local complexity obstructing the change; behavior-preserving simplification | [Simplify and clean](simplify-and-clean.md) |
| Versioned API uncertainty, technical choices needing external evidence, stale guidance or misleading comments, or changes affecting what users and maintainers need to know | [Documentation and references](documentation-and-references.md) |
| Lifetime, cancellation, concurrency or language semantics | [Language/runtime checks](language-runtime-checks.md) |
| Request/ORM/dependency lifecycle depends on framework semantics | [Service/framework checks](service-framework-checks.md) |
| Reactive state, stale responses, rendering or mobile lifecycle | [Client state checks](client-state-checks.md) |
| Interactive outcome, accessibility, localization, CLI/script behavior or public-page discoverability | [User journeys](user-journeys.md) |
| New/revised screen, interface critique or confusing/generic product experience | [Product interface review](product-design-review.md) |
| User study, feedback synthesis or a decision dependent on actual user evidence | [User research](user-research.md) |
| Chart, dashboard or quantitative graphic whose encoding affects interpretation | [Quantitative visualization](data-visualization.md) |
| Substantial explanatory diagram, layout or faithful redraw | [Diagram craft](diagram-craft.md) |
| Training, inference, retrieval or grounded-answer quality | [Model and retrieval quality](model-and-retrieval-quality.md) |
| Fine-tuning, preference/reward learning, training-signal diagnosis or checkpoint integrity | [Model post-training](model-post-training.md) |
| Package distribution or a change in information exposure | [Release preparation](release-preparation.md) |
| Evaluate agent instructions/tools/coordination, or diagnose recurring guidance failures | [Guidance improvement](guidance-improvement.md) |

These are questions to investigate, not automatic findings. Use only applicable checks and return evidence that changes the next decision. A supported zero-finding review is valid. For independent assurance, apply the existing [review contract](independent-review.md); for implementation, apply [delivery and repair](deliver-and-repair.md).
