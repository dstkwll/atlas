# Deliver and repair

Use when implementing a bounded outcome, investigating a defect, coordinating a worker, or recovering valid progress.

## Deliver observable increments

Choose the smallest integrated behavior that can be verified. Include the code, data, configuration and interface work that behavior actually needs. Inline enabling work unless an imminent consumer justifies separating it. Match the target project's style, dependencies and checks; do not add preferred tools or unrelated cleanup.

Plan the next usable vertical slice in detail and keep later work coarse. Tie it to the intended outcome and acceptance examples in the brief or existing request; demonstrate the result and use evidence or user feedback to choose what comes next. Update the brief and remaining work when learning changes provisional design. Changes to accepted intent still need the applicable judgment. A spec supports this feedback loop; it does not freeze requirements or oblige completion of an obsolete task list. Use the team's cadence where one exists, without imposing sprints, story points or a new backlog system.

For a bug, reproduce the incorrect behavior and identify the causal path before broad changes. Add a separating regression check when it protects meaningful behavior: it should expose the defect before the repair and pass afterward. For a trivial reversible text change, direct inspection or an existing check may suffice.

Tests should exercise observable behavior and relevant failure modes, not merely mirror the implementation. Reuse the project's checks. Investigate a failing check before blaming the environment; distinguish existing failures from regressions with evidence. Never weaken an assertion or skip a required check just to obtain green output. Report unavailable dependencies as a bounded evidence gap.

When implementation exposes a poor provisional choice, refine it and continue. If the change would alter accepted behavior, ownership, trust, risk, or a relied-on guarantee, preserve the discovery and return the smallest material decision.

For a failing build/startup use [build diagnosis](build-and-runtime-diagnosis.md); for hidden or partial failure use [failure handling](failure-handling.md). Choose [test evidence](test-adequacy.md) from the claimed behavior. These references can inform direct work or a bounded worker; they do not create extra stages.

## Use workers selectively

Give a worker enough context to act without inventing accepted judgment. State outcome, authoritative sources, allowed files/systems, authority, prohibited side effects, evidence and stopping/return conditions. Narrow the brief and permissions for a less capable worker. Avoid concurrent writers on the same work surface unless isolation and integration are clear.

Worker completion is a claim. Inspect the actual result and evidence, reconcile overlapping changes, and verify the integrated candidate. Reviewers report findings; they must not repair the work they judge. A worker's proposed scope expansion remains a proposal.

## Correct without turning every defect into a user decision

Confirm review findings against actual behavior. Repair defects that invalidate the accepted outcome while staying within the existing architecture, authority, risk and strategy. Defer adjacent improvements with enough context to recover them. Disagree with an unsupported finding using evidence rather than treating review as a vote.

After meaningful repair, repeat affected objective checks and obtain fresh independent review when required. That review covers the repair and shared regression/failure surface, not only disappearance of the previous finding. Bind findings and proof to the candidate actually inspected; changed bytes can invalidate earlier evidence.

Before a potentially lengthy correction episode, use the task's existing practical time/attempt bound or choose a proportionate local bound within granted authority and make it visible. Continue while findings narrow. Stop earlier for contradictory evidence, repeated defect classes without progress, material strategy/scope changes, or an exhausted bound. A normal second defect is not itself a human decision. A fresh session does not replenish the remaining budget.

## Repair the mechanism when needed

Distinguish broken work from a broken command, playbook, path, tool or host capability. Preserve user work and accepted commitments. Use a safe equivalent or repair an agent-owned mechanism within authority, prove it reaches the intended behavior, then resume. Do not bypass organizational policy, tool permissions or required controls.

If no safe path remains, report the blocked claim, exact condition and evidence, attempted approaches, why repetition is unhelpful, and next safe action. Do not label setup failure as architectural contradiction unless evidence actually challenges an accepted design.
