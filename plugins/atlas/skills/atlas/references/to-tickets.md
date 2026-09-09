# Plan executable vertical slices

Use to turn accepted scope into a coherent sequence of work that a specified implementer can execute and test. Produce local ticket drafts using existing project conventions unless tracker publication is explicitly authorized. Readiness is an evidence-backed planning judgment, not permission to execute.

Resolve the existing topic home through [Artifact location](artifact-location.md). By default create `tickets/index.md` for scope, dependency order and readiness, plus one numbered Markdown file per meaningful slice. Reuse established project/tracker organization; do not move artifacts into the code repository when an approved vault is configured.

## Ground intent and the recipient

Read the source brief, accepted amendments and relevant repository instructions and behavior. Reconcile dropped, conflicting or invented requirements before decomposing. A formal PRD is not mandatory if the request already supplies sufficient intent. Use [Discover and design](discover-and-design.md) for consequential gaps; prepare unaffected work while unresolved choices block dependent slices.

Identify the intended recipient and available environment from context. A fresh or less capable agent needs more explicit boundaries, examples and source context; never delegate missing product judgment as implementation latitude. If the repository or required environment cannot be inspected, label the plan provisional and name the remaining verification. Do not invent paths, commands or contracts.

## Establish enough design

Trace the relevant end-to-end behavior and identify which responsibility owns each important rule. Preserve accepted architecture and the project's vocabulary. Compare small caller examples for genuinely different interface choices when the choice changes behavior, testability or coupling. Include ordering, errors and invariants a consumer relies on, not only type signatures.

Prefer cohesive behavior behind a useful interface. Add a boundary, adapter or preliminary refactor only for the current change's demonstrated need. Keep enabling work inside its consuming slice unless it earns separate delivery. Where independently developed consumers and providers need a shared contract, identify the existing authoritative type/schema and how both verify it; do not introduce contract-generation infrastructure by default.

Record settled interface/ownership decisions and what the implementer may refine. A relevant type, state or call-flow sketch can remove ambiguity; do not prescribe every helper or assume fewer methods prove a better design.

## Slice and sequence

Each normal slice delivers a narrow, integrated observable outcome through the layers it actually needs, including verification. Do not require a UI for an API-only change or split database, service and tests into unrelated completion claims. Size for a credible implementation and review effort with the intended recipient, not an invented universal ticket count or context-window promise.

Order slices by real prerequisites and useful feedback. Name the output each dependency supplies. Distinguish semantic independence from concurrent-write safety; independent tickets can still collide in shared files. Mark integration ownership when work is split.

Mechanical wide migrations can use expand, migrate in bounded batches, then contract, preserving compatibility and verifying each landing point. If only a final integration can be green, state that explicitly with the agreed integration arrangement; intermediate work is not independently releasable. An uncertainty that prevents design may need a bounded spike with a question, evidence and exit decision rather than a fictional implementation ticket.

Map the whole requested scope. Make currently knowable slices executable; keep later detail conditional when it depends on learning. If a complete breakdown is requested, cover the full scope and expose unresolved details rather than silently omitting later work or claiming certainty.

## Make each ticket usable

Use the project's ticket shape; absent one, use the separate files and index above. Supply:
- Outcome and scope exclusions; source requirements or acceptance examples it serves.
- Current behavior and relevant source locations, distinguished from proposed file changes. Tell the recipient to recheck stale paths/baselines before relying on them.
- Prerequisites and dependency outputs; readiness and any exact blocker.
- Accepted responsibilities, contracts and risk boundaries; allowed implementation choices and return conditions.
- Ordered implementation guidance sufficient to navigate the slice, including integration and meaningful failure behavior, without freezing routine realization.
- Observable acceptance examples and how they will be tested; fixtures, test environment and important failure witnesses.
- Expected return evidence, relevant review and delivery/rollback considerations where consequence warrants them.

Avoid dumping the conversation or an entire source tree. Explain why each linked source matters. Tests must derive expected outcomes from accepted behavior, not encode a worker's new policy.

## TDD prerequisites and execution guidance

Use [Test adequacy](test-adequacy.md#test-first-work-when-it-helps) for behavior changes or bug fixes where test-first work gives useful feedback, and whenever the assignment or project requires TDD. Identify the test boundary, accepted expected outcome, fixtures/dependencies and a runner that reaches a relevant assertion. A missing dependency or startup failure is not the red phase.

During planning, specify the intended failing behavior and verification approach; do not claim tests ran or modify implementation merely to call a ticket ready. Check existing test viability when safe and authorized. If setup is needed, make it an explicit prerequisite or an initial bounded step with a stop condition. Distinguish ready now, ready after named prerequisites, and blocked by unresolved judgment or unavailable proof. No blockers in the ticket graph is insufficient evidence of readiness.

## Check the plan as a whole

Trace every accepted outcome to a slice and credible acceptance evidence. Check missing integration, duplicate work, circular or unnecessary dependencies, unreachable test prerequisites and contradictory commitments. Read a representative ticket as a fresh recipient: can it be acted on without inventing product or architecture decisions? Use independent review when scope, ambiguity or worker handoff makes it valuable. Missing independent review stays an evidence limit, not an invented pass.

Return the ordered plan, the actual executable frontier, conditional/blocked work and the recommended next action. Explain what “ready” is based on and what has not been tested. Creating ticket drafts neither authorizes execution nor makes tracker publication implicit. When publication is authorized, verify destinations, existing issues and dependency links and report partial creation honestly; do not close parent issues or apply acceptance labels without authority.
