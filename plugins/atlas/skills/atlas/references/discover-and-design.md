# Discover and design

Use the portion that resolves the present uncertainty. Stop when you can make the next responsible decision or run a bounded experiment.

## Clarify the outcome

Separate the user's problem from a proposed solution. Identify who needs what behavior, current pain, meaningful constraints, and observable success. Research available facts before asking. Challenge a costly premise if a simpler change can deliver the same outcome.

For broad work, retain a low-fidelity view of the whole journey while deepening only the relevant slice. A useful reasoning map is journeys, behaviors/state, responsibilities, vertical outcomes, options, experiments, and commitments. Enter where needed; these are not ordered stages or required documents.

Use collaborative design when taste or intent is forming, pressure-test apparent certainty, and investigate independently when the outcome is clear. Reflect a consequential interpretation before treating it as accepted. Select a diagram or comparison only when it improves the user's decision. The user should not have to choose a notation or internal method.

## Maintain a living brief or specification

For substantial or ambiguous work, default to a concise agent-readable brief before detailed implementation breakdown. Reuse an existing issue or design document when it already serves that purpose. A small clear fix can use its existing request and acceptance example; a bounded discovery probe need not wait for a finished specification. Create or expand a PRD when requested, required by the project, or useful for stakeholder agreement or handoff. Do not wait for the user to name an artifact when durable shared understanding is needed.

A PRD explains the problem, intended users and outcomes; a specification makes observable behavior and constraints precise. They may be one document. Capture the relevant scope and exclusions, journeys, acceptance examples including important failure cases, constraints, assumptions and open questions. Add technical responsibilities, interfaces and tradeoffs where they affect the decision. Use a project template if required; otherwise omit sections that do not help a reader decide or implement. Separate accepted intent, agent proposals, discovered facts and provisional design. Drafting a requirement does not accept it or authorize implementation.

Keep the whole outcome visible at low fidelity and make the next slice precise. Resolve questions that change that slice's outcome, acceptance or authority before dependent implementation; leave unrelated uncertainty open with an owner or next investigation. Derive implementation units from observable outcomes and their dependencies, not from document headings or a demand for a complete ticket tree. A useful brief can evolve through design, experiments and working software.

## Co-design through a useful visual

When co-design is requested and a polished view improves participation, generate a professional HTML view of the current journeys, architecture, alternatives, commitments and open questions. Use existing approved host capabilities and keep artifacts in the approved project environment; if HTML rendering is unavailable, provide a useful available representation and state the limitation. Do not introduce a hosting service or publish the view without authority.

The HTML is a regenerable view of the agent-readable design, not a second source of truth. Distinguish alternatives and uncertain behavior from accepted choices. Record decisions made while discussing or interacting with the view in the underlying brief, then refresh the view when it matters to the next decision. A visual selection or polished mockup alone does not establish acceptance or permission to build.

## Ground changes in the existing system

Trace the affected behavior through real code, data, configuration and integrations. Inspect relevant tests, operational assumptions, failure handling, history and compatibility obligations. Distinguish current behavior from intended contracts and local uncommitted changes. Do not inventory the entire system unless the decision needs it.

Ask what the change makes a caller, operator, data owner, or neighboring component adjust. Consider rollout, coexistence, migration, rollback and recovery where they matter. Revisit inspection if coding reveals an unexamined dependency or constraint.

When behavior or caller reliance is unclear, use [behavior tracing](understand-behavior.md). For concrete design, identify the few affected interfaces, files, data owners and dependencies needed to deliver a vertical outcome. Prefer cohesion, information hiding and narrow contracts; an abstraction needs a current consumer and a problem it prevents. Preserve existing conventions unless evidence justifies changing them.

## Make consequential design explicit

Compare the few genuine options using the same criteria: user outcome, relevant quality attributes, responsibility and data ownership, cohesion/coupling, dependency direction, failure/recovery, operability, compatibility, reversibility, and ongoing cost. Focus on the properties that affect this decision. Respect accepted interfaces and boundaries; internal details can remain provisional.

Present the recommendation, rationale and strongest counterargument. When judgment belongs to the user, state the smallest decision, concrete consequences, what can continue and what must pause. Do not manufacture options when the constraints determine the answer. Record material accepted choices locally with their rationale and source of authority.

Example: changing an internal lookup structure while preserving behavior is usually provisional refinement. Moving confidential data to a new service changes a trust boundary and requires the applicable decision and authorization.

## Learn through the smallest credible evidence

A probe answers one falsifiable question. A walking skeleton crosses the real end-to-end responsibility path with minimal scaffolding. A vertical slice delivers an observable outcome. Choose the cheapest evidence that addresses the actual uncertainty; a set of horizontal foundation tasks does not prove integration.

For a probe, state the hypothesis, success/failure signal and side-effect bounds before running. Record the result and its implication, including negative evidence. Disposable probe code becomes production code only through deliberate implementation and verification.

Useful residue is a clear outcome, accepted constraints, provisional design, evidence, unresolved judgment and next action. Update the living brief as learning changes it, and preserve consequential choices through [continuity and decisions](continuity-and-decisions.md). No universal PRD, system design, ticket graph or diagram suite is required.
