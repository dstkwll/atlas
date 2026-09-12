# Deliver and repair

Use when implementing a bounded outcome, investigating a defect, coordinating a worker, or recovering valid progress.

## Deliver observable increments

Choose the smallest integrated behavior with meaningful checks at the level currently feasible. Include the code, data, configuration and interface work that behavior actually needs. Inline enabling work unless an imminent consumer justifies separating it. Match the target project's style, dependencies and checks; do not add preferred tools or unrelated cleanup. When proof depends on unavailable equipment or an operator event, use [Project verification](project-verification.md#when-evidence-depends-on-equipment-or-an-event) to preserve the remaining physical claims while continuing useful authorized work.

Plan the next usable vertical slice in detail and keep later work coarse. Tie it to the intended outcome and acceptance examples in the brief or existing request; demonstrate the result and use evidence or user feedback to choose what comes next. Update the brief and remaining work when learning changes provisional design. Changes to accepted intent still need the applicable judgment. A spec supports this feedback loop; it does not freeze requirements or oblige completion of an obsolete task list. Use the team's cadence where one exists, without imposing sprints, story points or a new backlog system.

For a report from a thread or tracker, inspect existing evidence, ownership and relevant fix artifacts before starting another patch. Distinguish observed defects from requested behavior and unresolved expectations. Compare possible duplicates by trigger, signature, affected version and current status; a long-closed issue may be a recurrence. Use causal evidence and established ownership rather than routing solely by the screen showing the symptom. Clarification, a related-issue recommendation or [verification of an existing fix](test-adequacy.md#verify-an-existing-fix) may be the useful outcome. Do not turn weak similarity into a duplicate verdict or a stale PR into a permanent veto on authorized repair. Assignment, tracker changes and notifications still require applicable authority.

For a bug, reproduce the incorrect behavior and identify the causal path before broad changes. Add a separating regression check when it protects meaningful behavior: it should expose the defect before the repair and pass afterward. For a trivial reversible text change, direct inspection or an existing check may suffice.

Tests should exercise observable behavior and relevant failure modes, not merely mirror the implementation. Reuse the project's checks. Investigate a failing check before blaming the environment; distinguish existing failures from regressions with evidence. Never weaken an assertion or skip a required check just to obtain green output. Report unavailable dependencies as a bounded evidence gap.

When implementation exposes a poor provisional choice, refine it and continue. If the change would alter accepted behavior, ownership, trust, risk, or a relied-on guarantee, preserve the discovery and return the smallest material decision.

For a failing build/startup use [build diagnosis](build-and-runtime-diagnosis.md); for hidden or partial failure use [failure handling](failure-handling.md). Choose [test evidence](test-adequacy.md) from the claimed behavior. These references can inform direct work or a bounded worker; they do not create extra stages.

## Use workers selectively

Choose coordination from the actual dependencies. A single lead can deliver a clear slice directly. Independent work can overlap when its shared contract, separate write surfaces, return evidence and integration responsibility are clear. Work awaiting equipment or a decision can be preserved with its exact dependency while unaffected work proceeds. Use [tickets](to-tickets.md) when these assignments need durable handoff; do not turn every decision or prerequisite into a separate worker or mandatory stage.

A coordination plan is not a launch instruction. Execute only within existing authority and practical resource bounds; accepting a planning-only breakdown does not authorize workers or implementation. When splitting work is useful, the lead remains responsible for reconciling results and checking the integrated outcome rather than accumulating independent success reports.

Give a worker enough context to act without inventing accepted judgment. State outcome, authoritative sources, allowed files/systems, authority, prohibited side effects, evidence and stopping/return conditions. Narrow the brief and permissions for a less capable worker. Avoid concurrent writers on the same work surface unless isolation and integration are clear.

Before multiplying uncertain repeated work across workers, consider one representative slice to check the brief, verification method and integration arrangement. Use what it reveals to correct later briefs within accepted scope; a successful pilot does not prove every slice or extend the total budget. Skip a separate pilot when the work or method is already clear.

Name the isolation the assignment actually needs and what the host supplies. Fresh context supports independent judgment; a separate worktree or write surface prevents concurrent file collisions; host permissions or a security sandbox constrain access. One does not imply the others merely because a tool calls a session or workspace isolated.

Select the relevant source sections and explain why each constrains this task; a pile of links is not a usable brief. Distinguish binding decisions from background evidence and identify what the worker may decide. Leave implementation reasoning to the worker within that boundary. Use the reconciled living brief when design spans multiple decisions.

Before delegating substantial implementation, apply the [discovery readiness check](discover-and-design.md#deepen-ideas-through-conversation) to the assigned slice. Carry the intended behavior, important success/failure examples, settled responsibilities, known unknowns and the worker's allowed choices into its brief. Do not bury unresolved product or architecture judgment inside an implementation task as "use sensible defaults." Match task size and specificity to the worker's demonstrated capability and available context; a model label alone is not evidence that it can resolve ambiguity safely.

Tell workers to return a newly uncovered consequential choice to the lead with the competing interpretations, affected behavior and any safe work that can continue. Pause only the dependent portion. The lead resolves the question from accepted sources or its existing delegation, and asks the user only for missing judgment it cannot supply. Record the resolution before dependent work resumes. Routine in-scope implementation choices remain the worker's to make; uncertainty does not require escalating every variable name or helper extraction. Verify the returned behavior against the accepted intent, including assumptions the worker introduced, rather than accepting a green test suite that encodes a new policy.

If the handoff relies on a particular validation command, check when possible that it runs in the intended environment and reaches the relevant assertion or known control case. A successful startup or smoke check establishes that the check can run, not that the proposed behavior is correct. Report missing access, setup failures and assertions not reached as evidence gaps; do not promise proof from an unusable check or weaken acceptance to fit it.

Worker completion is a claim. Inspect the actual result and evidence, reconcile overlapping changes, and verify the integrated candidate. Reviewers report findings; they must not repair the work they judge. A worker's proposed scope expansion remains a proposal.

If a worker is interrupted or its return is unusable, first distinguish a report-only failure from an incorrect implementation, an environment/dependency failure, and execution whose effects are unknown. Establish liveness and effect uncertainty before retrying or cleaning up. Preserve recoverable changes, failure output and proof, and carry already-tried remedies into the correction; a malformed report must not replay a successful mutation, and a failed dependency must not trigger an identical blind retry. Remove an ephemeral workspace only after confirming that needed work and evidence have been retained.

## Correct without turning every defect into a user decision

Confirm review findings against actual behavior. Repair defects that invalidate the accepted outcome while staying within the existing architecture, authority, risk and strategy. Defer adjacent improvements with enough context to recover them. Disagree with an unsupported finding using evidence rather than treating review as a vote.

After meaningful repair, repeat affected objective checks and obtain fresh independent review when required. That review covers the repair and shared regression/failure surface, not only disappearance of the previous finding. Bind findings and proof to the candidate actually inspected; changed bytes can invalidate earlier evidence.

Before a potentially lengthy correction episode, use the task's existing practical time/attempt bound or choose a proportionate local bound within granted authority and make it visible. Continue while findings narrow. Stop earlier for contradictory evidence, repeated defect classes without progress, material strategy/scope changes, or an exhausted bound. A normal second defect is not itself a human decision. A fresh session does not replenish the remaining budget.

Do not invent a fixed retry allowance for ordinary execution. Fixing a malformed tool argument, a wrong path or a missing period does not automatically consume a substantive review-repair cycle. A limit on tool calls still governs tool calls; a limit on substantive repair cycles governs those cycles. Respect explicit user, project and host limits regardless of how an attempt is labeled. Do not locally extend explicit user, project or host limits. A self-selected planning bound may be revised visibly within delegated authority only when new evidence changes the estimate, not merely because the bound was exhausted. Preserve cumulative effort; repeated extensions without narrowing findings require stopping or a new decision, not another reset.

## Repair the mechanism when needed

Before replacing a failed mechanism or expanding a probe, compare the proposed next action with the original user outcome and accepted constraints. If work is becoming mainly about supporting machinery, read and apply [Discover and design](discover-and-design.md) to reconsider the simplest viable approach before expanding it. Refine provisional choices within existing authority; return material changes in scope, architecture, guarantees or risk for judgment. A transient retry or trivial command correction does not by itself require rediscovery. Do not treat setup failure alone as evidence against the accepted design.

Distinguish broken work from a broken command, playbook, path, tool or host capability. Preserve user work and accepted commitments. Use a safe equivalent or repair an agent-owned mechanism within authority, prove it reaches the intended behavior, then resume. Do not bypass organizational policy, tool permissions or required controls.

For routine recovery, establish what failed and whether effects are known, correct the cause or allow a plausible transient condition to clear, then verify the actual result. Use proportionate backoff or an authorized equivalent for an unavailable dependency. A second failure alone is not a stop condition, and retrying need not require new information when a known transient condition reasonably warrants another attempt. Stop repeating an approach when there is no credible path to progress or the cumulative effort is disproportionate; changing tools, workers or error labels does not make an endless recovery sequence acceptable. Keep recovery inside applicable total time, attempt and resource limits.

An authorized publication that omitted punctuation may need a small in-place correction, not a new publication or a request for renewed permission. Establish the existing result from reliable current evidence, inspecting it when unknown or stale, and correct it only if the granted authority covers that edit. A timeout with an unknown write outcome requires reconciliation before retrying, as described in Failure handling. The apparent triviality of the intended change does not make duplicate external effects safe.

If no safe path remains, report the blocked claim, exact condition and evidence, attempted approaches, why repetition is unhelpful, and next safe action. Do not label setup failure as architectural contradiction unless evidence actually challenges an accepted design.
