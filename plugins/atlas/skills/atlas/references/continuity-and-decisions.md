# Continuity and decisions

Use for multi-session work, material decisions, authority changes, pauses, handoffs, or resumption. A small task completed directly needs no new memory file.

## Keep one useful front door

Prefer the target project's existing work-state convention. If none exists and continuity is needed, use a small task-specific Markdown note in a local project-approved location, such as `project-memory/current.md` for a single active task. Do not overwrite another task's note or store state in the reusable skill. Keep protected state within its approved environment; a public source repository is not automatically an approved location for work evidence.

An existing topic PRD can own planning continuity, including a self-contained HTML document with embedded recovery context. Use [Artifact location](artifact-location.md) to honor the configured planning root or approved vault. Do not require a separate Markdown state record when the existing artifact already supplies what recovery needs. Keep that PRD current at material decisions and handoffs; do not create one for every small task.

The record should let a fresh lead recover the canonical Atlas skill's installed or source location, the active task and bounded scope, the goal/done claim, accepted versus provisional choices, current authority, relevant repository/worktree identity, meaningful evidence or blocker, and next safe action. Link to the decisions and evidence needed at the resume point instead of duplicating them. These locations and pointers make recovery possible; they are not new permission and do not prove that a host will restore guidance automatically. Use ordinary prose, links and headings; exact grammar is not correctness. Commit a state file only when project policy permits its content and location.

## Write at meaningful boundaries

Persist authority changes before any downstream action relies on them, including a changed assignment or permission envelope. Also checkpoint before a likely interruption, after a material discovery or decision, and on completion/pause. Preserve remaining correction authority if resumption depends on it.

Keep the current view compact. Preserve a material superseded commitment and its rationale in an existing decision record or a short decision note when later work relies on it; do not erase it or accumulate a transcript. For a consequential user choice, record context, genuine options, recommendation/reasoning, the user's selected or introduced direction, and any rationale they actually supplied. Do not infer a general preference or taste profile.

Distinguish an option the user chose from those offered, an alternative they introduced, an agent proposal still awaiting judgment, and a choice the agent made under delegated authority. Record who decided and the scope of acceptance; an unanswered recommendation is not consent. Preserve the relevant prompt or option wording when needed to interpret the choice. Do not invent missing options or rationale, or attribute an agent's assumption to the user.

When a material decision depends on a concrete assumption, add a brief reconsideration trigger if it will help later judgment: for example, revisit synchronous processing if measured latency exceeds the agreed response budget. Use actual assumptions and agreed limits, not invented thresholds or a required field on every decision. When the trigger occurs, record the evidence and bring back the affected judgment; it does not itself authorize changing an accepted commitment. Provisional implementation choices remain refinable within delegated authority.

During substantial design, keep the current brief/specification up to date and append short material decision entries in that document or an existing decision log. A progress checkpoint records the meaningful result, what changed, evidence or unresolved questions, and the next action; do not log every tool call. The current-state note links to this design and history rather than duplicating them. Update the affected documents when accepted scope or behavior changes, preserving important superseded decisions and their rationale.

For periodic direction checks, use the accepted outcome, design constraints and material decisions in this existing record or its linked brief/PRD as the reference point. Record only a meaningful drift finding, changed provisional approach, unresolved decision or accepted amendment and its next action. Keep the reference current without rewriting accepted commitments to match whatever execution happened to produce. Do not create a separate direction log or preserve a turn count; after recovery, reestablish alignment before dependent work.

## Resume from evidence

After compaction, session restoration or another material context loss, reload the canonical Atlas skill from its recorded location, only the references relevant to the next action, and the existing task record when available before doing work that depends on them. If the canonical guidance cannot be recovered, identify the missing source rather than claiming Atlas remains active. Do not reread every reference on every turn.

Inspect current project instructions, repository identity, branch/HEAD, worktree and applicable live PR/check state before relying on a note. Treat old status statements as observations to verify. Distinguish stale status from conflicting authority: a merge can obsolete a next-action note but does not grant permission for the next feature. A task record and source pointer preserve recoverable context; the host still controls whether conversation guidance survives compaction or resume.

If the task is already complete, report that fact or continue only another currently authorized task. If authority is missing or contradictory, reconstruct it from authorized sources or ask the smallest necessary question; do not make the user retell facts already inspectable. If a material external state cannot be checked, name that limitation and continue only work independent of it.

After an interrupted worker or uncertain tool result, preserve the existing authority and correction bound. Before retry or cleanup, recover available work and evidence and establish whether execution is still live or may already have produced effects; use [Deliver and repair](deliver-and-repair.md#use-workers-selectively) for the failure classification. A new session, worktree or report does not by itself prove cancellation, isolation or a clean restart.

Verify that cited proof still applies after edits. Record an exact commit/tree or other candidate identity when later review or delivery relies on exact bytes, including relevant dirty-worktree changes. Avoid a self-referential demand that a file contain the hash of the commit that includes that file: record the checked candidate, then explain any subsequent checkpoint-only change and verify it separately.

Use normal Git conflict handling and host filesystem facilities. Do not silently overwrite another writer's authority record. A repeat objective corruption or evidence mismatch may justify a narrow mechanism; ordinary continuity does not require a database or controller.

## Pause or finish

Preserve the actual result, decisions/deltas, checks and evidence, accepted risks, deferred candidates only when useful, and the next safe action. Make an unverified claim or blocker explicit. On completion, remove stale active-work instructions from the current view and retain durable decision/evidence pointers. Routine history belongs in Git and existing records, not in the next agent's starting context.

Repeated corrections or stalled attempts can justify [guidance improvement](guidance-improvement.md). Diagnose the cause before turning a local failure into enduring policy. Preserve the requested outcome and remaining correction boundary; another session or worker does not reset them.
