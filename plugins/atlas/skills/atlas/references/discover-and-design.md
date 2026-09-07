# Discover and design

Use the portion that resolves the present uncertainty. Stop when you can make the next responsible decision or run a bounded experiment.

## Clarify the outcome

Separate the user's problem from a proposed solution. Identify who needs what behavior, current pain, meaningful constraints, and observable success. Research available facts before asking. Challenge a costly premise if a simpler change can deliver the same outcome.

For broad work, retain a low-fidelity view of the whole journey while deepening only the relevant slice. A useful reasoning map is journeys, behaviors/state, responsibilities, vertical outcomes, options, experiments, and commitments. Enter where needed; these are not ordered stages or required documents.

Use collaborative design when taste or intent is forming, pressure-test apparent certainty, and investigate independently when the outcome is clear. Reflect a consequential interpretation before treating it as accepted. Select a diagram or comparison only when it improves the user's decision. The user should not have to choose a notation or internal method.

## Deepen ideas through conversation

When intent is forming, work iteratively from the uncertainty most likely to change the direction. Ask a focused question or small related group, explain why it matters, and offer a grounded recommendation when useful. Follow the answer into a concrete user episode, exception or consequence; do not treat the first plausible answer as a complete requirement. Investigate inspectable facts yourself. Product intent, priorities and acceptable tradeoffs belong with the user unless already delegated.

Explore genuinely different approaches while the problem framing is open, including a simpler intervention when credible. Then pressure-test promising choices against the same real scenarios. Use counterexamples to uncover ambiguous terms and hidden policy: who may act, what happens when two people act together, what failure means, or how an action is undone, when relevant. These are prompts for investigation, not a questionnaire to exhaust or a requirement to invent alternatives.

After meaningful answers or evidence, summarize what changed, what is settled and the next consequential uncertainty. Update the living brief and decision attribution as you go. Agreement with an example or general direction does not accept every inferred rule. If the user is unavailable, continue independent investigation, sketches or bounded probes within authority; keep unresolved judgment visible rather than choosing defaults and calling discovery complete.

Before declaring a slice ready for implementation, ask whether two reasonable implementers could satisfy the written brief yet deliver materially different outcomes. Probe ambiguity that changes that slice's user behavior, acceptance, ownership, failure/recovery or authority. Resolve it from accepted context or user judgment, or exclude the dependent work and choose a useful independent slice or explicit experiment. A polished PRD, elapsed discussion or exhausted question list is not a stopping signal. Stop digging when the next task has sufficiently clear intent, important acceptance examples and a known decision boundary; leave unrelated future detail open. This does not require exhaustive design, a separate approval stage or renewed approval of settled decisions.

## Maintain a living brief or specification

For substantial or ambiguous work, default to a concise agent-readable brief before detailed implementation breakdown. Reuse an existing issue or design document when it already serves that purpose. A small clear fix can use its existing request and acceptance example; a bounded discovery probe need not wait for a finished specification. Create or expand a PRD when requested, required by the project, or useful for stakeholder agreement or handoff. Do not wait for the user to name an artifact when durable shared understanding is needed.

A PRD explains the problem, intended users and outcomes; a specification makes observable behavior and constraints precise. They may be one document. Capture the relevant scope and exclusions, journeys, acceptance examples including important failure cases, constraints, assumptions and open questions. Add technical responsibilities, interfaces and tradeoffs where they affect the decision. Use a project template if required; otherwise omit sections that do not help a reader decide or implement. Separate accepted intent, agent proposals, discovered facts and provisional design. Drafting a requirement does not accept it or authorize implementation.

Keep the whole outcome visible at low fidelity and make the next slice precise. Resolve questions that change that slice's outcome, acceptance or authority before dependent implementation; leave unrelated uncertainty open with an owner or next investigation. Derive implementation units from observable outcomes and their dependencies, not from document headings or a demand for a complete ticket tree. A useful brief can evolve through design, experiments and working software.

Before substantial implementation or handoff, read the relevant brief afresh against the material decisions it should express. Supersede obsolete requirements, expose contradictions, and keep proposed details distinct from accepted intent. Reconcile affected acceptance examples and visuals as well as prose; do not silently choose between conflicting commitments. Use a fresh independent reader when ambiguity or consequences warrant it, without making every brief pass a separate review stage.

## Explain and co-design through a useful visual

Choose the representation from what the reader needs to understand. Pseudocode can explain a rule, a call tree execution order, a component or shallow file tree ownership, and a sequence or flow diagram interactions across boundaries. A small before/after view can isolate a change; include enough surrounding context to preserve meaning and order. Use actual names and distinguish inspected behavior from proposed behavior. A short inline explanation may be sufficient; richer UI or dense comparisons can benefit from HTML. These are choices, not a required visual suite.

When co-design is requested and a polished view improves participation, generate a professional HTML view of the current journeys, architecture, alternatives, commitments and open questions. Use existing approved host capabilities and keep artifacts in the approved project environment; if HTML rendering is unavailable, provide a useful available representation and state the limitation. Do not introduce a hosting service or publish the view without authority.

The HTML is a regenerable view of the agent-readable design, not a second source of truth. Distinguish alternatives and uncertain behavior from accepted choices. Record decisions made while discussing or interacting with the view in the underlying brief, then refresh the view when it matters to the next decision. A visual selection or polished mockup alone does not establish acceptance or permission to build.

Keep the decision, relevant context, comparison and smallest useful visual together so the user can judge without hunting across the artifact. Check rendered readability on the intended device or a representative viewport, including a phone when relevant: labels, accepted/proposed status and consequences must remain legible. State what could not be checked; visual polish alone is not evidence of usability.

Use [Diagram craft](diagram-craft.md) when a substantial diagram needs deliberate layout, source-preserving simplification or an exportable artifact. It is optional; a clear inline explanation or diagram needs no extra artifact.

## Ground changes in the existing system

Trace the affected behavior through real code, data, configuration and integrations. Inspect relevant tests, operational assumptions, failure handling, history and compatibility obligations. Distinguish current behavior from intended contracts and local uncommitted changes. Do not inventory the entire system unless the decision needs it.

Ask what the change makes a caller, operator, data owner, or neighboring component adjust. Consider rollout, coexistence, migration, rollback and recovery where they matter. Revisit inspection if coding reveals an unexamined dependency or constraint.

When behavior or caller reliance is unclear, use [behavior tracing](understand-behavior.md). For concrete design, identify the few affected interfaces, files, data owners and dependencies needed to deliver a vertical outcome. Prefer cohesion, information hiding and narrow contracts; an abstraction needs a current consumer and a problem it prevents. Preserve existing conventions unless evidence justifies changing them.

## Make consequential design explicit

Compare the few genuine options using the same criteria: user outcome, relevant quality attributes, responsibility and data ownership, cohesion/coupling, dependency direction, failure/recovery, operability, compatibility, reversibility, and ongoing cost. Focus on the properties that affect this decision. Respect accepted interfaces and boundaries; internal details can remain provisional.

For a consequential interface choice, compare small usage sketches of the same representative caller task under genuine alternatives, including the existing design when viable. An interface includes everything the caller must know: invariants, ordering, errors, configuration, ownership and relevant performance guarantees. Show what each option hides, what the caller still coordinates, and where verification belongs. Fewer methods or a shorter call sequence is not automatically better if it hides necessary control or loses guarantees. Explore alternatives directly or through bounded workers when useful; no fixed number of designs or agents is required.

Present the exact decision and why it matters now, fixed constraints, remaining uncertainty, recommendation, rationale and strongest counterargument together with the comparison. When judgment belongs to the user, state the practical consequences, what can continue and what must pause. Use plain language and only the visual that helps this choice; no fixed presentation format is required. Do not manufacture options when the constraints determine the answer. Record material accepted choices locally with their rationale and source of authority.

Example: changing an internal lookup structure while preserving behavior is usually provisional refinement. Moving confidential data to a new service changes a trust boundary and requires the applicable decision and authorization.

## Learn through the smallest credible evidence

A probe answers one falsifiable question. A walking skeleton crosses the real end-to-end responsibility path with minimal scaffolding. A vertical slice delivers an observable outcome. Choose the cheapest evidence that addresses the actual uncertainty; a set of horizontal foundation tasks does not prove integration.

Test the assumption most likely to invalidate the approach before polishing less consequential details. For a probe, state the hypothesis, what observed outcomes would support or contradict it, and the time/work and side-effect bounds before running. Record the result and its implication, including negative or inconclusive evidence. A setup failure or a run that never reaches the relevant behavior leaves the hypothesis unverified; it does not refute it. Disposable probe code becomes production code only through deliberate implementation and verification.

Useful residue is a clear outcome, accepted constraints, provisional design, evidence, unresolved judgment and next action. Update the living brief as learning changes it, and preserve consequential choices through [continuity and decisions](continuity-and-decisions.md). No universal PRD, system design, ticket graph or diagram suite is required.
