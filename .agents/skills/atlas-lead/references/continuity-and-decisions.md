# Continuity and decisions

Use for multi-session work, material decisions, authority changes, pauses, handoffs, or resumption. A small task completed directly needs no new memory file.

## Keep one useful front door

Prefer the target project's existing work-state convention. If none exists and continuity is needed, use a small task-specific Markdown note in a local project-approved location, such as `project-memory/current.md` for a single active task. Do not overwrite another task's note or store state in the reusable skill. Keep protected state within its approved environment; a public source repository is not automatically an approved location for work evidence.

The record should let a fresh lead recover the goal/done claim, accepted versus provisional choices, current authority, relevant repository/worktree identity, meaningful evidence or blocker, and next safe action. Use ordinary prose, links and headings; exact grammar is not correctness. Reference existing repository decisions and evidence instead of duplicating them. Commit a state file only when project policy permits its content and location.

## Write at meaningful boundaries

Persist authority changes before any downstream action relies on them, including a changed assignment or permission envelope. Also checkpoint before a likely interruption, after a material discovery or decision, and on completion/pause. Preserve remaining correction authority if resumption depends on it.

Keep the current view compact. Preserve a material superseded commitment and its rationale in an existing decision record or a short decision note when later work relies on it; do not erase it or accumulate a transcript. For a consequential user choice, record context, genuine options, recommendation/reasoning, the user's selected or introduced direction, and any rationale they actually supplied. Do not infer a general preference or taste profile.

## Resume from evidence

Inspect current project instructions, repository identity, branch/HEAD, worktree and applicable live PR/check state before relying on a note. Treat old status statements as observations to verify. Distinguish stale status from conflicting authority: a merge can obsolete a next-action note but does not grant permission for the next feature.

If the task is already complete, report that fact or continue only another currently authorized task. If authority is missing or contradictory, reconstruct it from authorized sources or ask the smallest necessary question; do not make the user retell facts already inspectable. If a material external state cannot be checked, name that limitation and continue only work independent of it.

Verify that cited proof still applies after edits. Record an exact commit/tree or other candidate identity when later review or delivery relies on exact bytes, including relevant dirty-worktree changes. Avoid a self-referential demand that a file contain the hash of the commit that includes that file: record the checked candidate, then explain any subsequent checkpoint-only change and verify it separately.

Use normal Git conflict handling and host filesystem facilities. Do not silently overwrite another writer's authority record. A repeat objective corruption or evidence mismatch may justify a narrow mechanism; ordinary continuity does not require a database or controller.

## Pause or finish

Preserve the actual result, decisions/deltas, checks and evidence, accepted risks, deferred candidates only when useful, and the next safe action. Make an unverified claim or blocker explicit. On completion, remove stale active-work instructions from the current view and retain durable decision/evidence pointers. Routine history belongs in Git and existing records, not in the next agent's starting context.
