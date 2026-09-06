# Discover and design

Use the portion that resolves the present uncertainty. Stop when you can make the next responsible decision or run a bounded experiment.

## Clarify the outcome

Separate the user's problem from a proposed solution. Identify who needs what behavior, current pain, meaningful constraints, and observable success. Research available facts before asking. Challenge a costly premise if a simpler change can deliver the same outcome.

For broad work, retain a low-fidelity view of the whole journey while deepening only the relevant slice. A useful reasoning map is journeys, behaviors/state, responsibilities, vertical outcomes, options, experiments, and commitments. Enter where needed; these are not ordered stages or required documents.

Use collaborative design when taste or intent is forming, pressure-test apparent certainty, and investigate independently when the outcome is clear. Reflect a consequential interpretation before treating it as accepted. Select a diagram or comparison only when it improves the user's decision. The user should not have to choose a notation or internal method.

## Ground changes in the existing system

Trace the affected behavior through real code, data, configuration and integrations. Inspect relevant tests, operational assumptions, failure handling, history and compatibility obligations. Distinguish current behavior from intended contracts and local uncommitted changes. Do not inventory the entire system unless the decision needs it.

Ask what the change makes a caller, operator, data owner, or neighboring component adjust. Consider rollout, coexistence, migration, rollback and recovery where they matter. Revisit inspection if coding reveals an unexamined dependency or constraint.

## Make consequential design explicit

Compare the few genuine options using the same criteria: user outcome, relevant quality attributes, responsibility and data ownership, cohesion/coupling, dependency direction, failure/recovery, operability, compatibility, reversibility, and ongoing cost. Focus on the properties that affect this decision. Respect accepted interfaces and boundaries; internal details can remain provisional.

Present the recommendation, rationale and strongest counterargument. When judgment belongs to the user, state the smallest decision, concrete consequences, what can continue and what must pause. Do not manufacture options when the constraints determine the answer. Record material accepted choices locally with their rationale and source of authority.

Example: changing an internal lookup structure while preserving behavior is usually provisional refinement. Moving confidential data to a new service changes a trust boundary and requires the applicable decision and authorization.

## Learn through the smallest credible evidence

A probe answers one falsifiable question. A walking skeleton crosses the real end-to-end responsibility path with minimal scaffolding. A vertical slice delivers an observable outcome. Choose the cheapest evidence that addresses the actual uncertainty; a set of horizontal foundation tasks does not prove integration.

For a probe, state the hypothesis, success/failure signal and side-effect bounds before running. Record the result and its implication, including negative evidence. Disposable probe code becomes production code only through deliberate implementation and verification.

Useful residue is a clear outcome, accepted constraints, provisional design, evidence, unresolved judgment and next action. Reuse existing issues, design notes or code when they already carry that meaning. No universal PRD, system design, ticket graph or diagram suite is required.
