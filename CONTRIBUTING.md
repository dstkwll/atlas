# Contributing to Atlas

Start with [AGENTS.md](AGENTS.md) and [the architect charter](docs/architect-charter.md). They govern work on Atlas itself. The installable product is `plugins/atlas/`; maintaining this repository does not impose GitHub tracking or private coordination on projects using the plugin.

## One home for each kind of information

| Information | Home |
| --- | --- |
| Product intent, architect responsibility and accepted architecture | Charter and relevant `docs/decisions/` records |
| Consequential accepted documentation policy and rationale | [Documentation boundaries](docs/decisions/2026-09-26-documentation-boundaries.md) |
| A substantive task's outcome, acceptance, decisions, blockers and continuation | Its [GitHub issue](https://github.com/dstkwll/atlas/issues) |
| Implementation, review, checks and completed-change history | Linked pull requests and Git |
| Public behavioral findings and material limits | Topic summaries in `docs/validation/`, including [guidance-authoring observations](docs/validation/guidance-authoring.md) |
| Optional overview of work | A [GitHub Project](https://github.com/dstkwll/atlas/projects) containing those same issues and PRs |
| Detailed trial traces and personal donor research | Maintainer evidence outside the installed package; public maintenance does not depend on private notes |

Use an issue when meaningful decisions or unfinished work must survive sessions. A small self-contained fix can use its PR directly. Search existing work before creating another record. Creating or updating GitHub records requires the assignment's applicable authority; routine local continuity does not itself authorize publication. Keep protected information in its approved environment.

## Start and resume

Read the current assigned issue and relevant comments, linked PRs and accepted decisions, then compare their status with the actual checkout and live GitHub evidence. Identify the intended outcome, granted scope, unresolved judgment and next useful action. Do not choose another backlog item merely because the last task is complete. A board status or issue assignment is not permission to implement, dispatch workers, change priorities or merge.

If GitHub or required guidance cannot be read, report exactly what is unavailable. Continue work independent of it, using a clearly provisional local note only when needed and permitted. On reconnection, reconcile against current remote state before updating the existing record; do not create a competing committed ledger or claim an unsaved update succeeded.

## Keep the issue useful

A compact issue body should make the outcome, relevant constraints and acceptance behavior clear. Add the current scope of work, consequential accepted decisions, open judgment and links to implementation or evidence where they matter. Ordinary prose is enough; no required template or field schema.

Update at meaningful events: accepted decisions, a material blocker, handoff, or completion. Keep the body useful for current resumption; retain superseded material choices and their reasons in a short comment or linked decision. Distinguish what the user chose, what the agent proposed and what it decided within delegated authority. A handoff identifies the actual candidate, what was checked, what remains unknown and the next safe action. No per-turn diary is needed.

Link partial PRs without closing the larger issue. Use a closing keyword only when the PR actually completes the issue's acceptance. A merged PR proves integration of that change, not every broader claim. When closing without delivery, state the disposition and use the appropriate closure reason.

## Keep the overview inexpensive

Use one Project as a view over real issues and PRs when useful. Prefer native metadata and built-in workflows over duplicate summaries, mandatory estimates, scheduled ledger updates or custom synchronization. Keep issue state authoritative over its board display; a Done column can include work closed without delivery. Do not use board changes to authorize execution or automatic issue closure.

Historical backfill should link relevant completed PRs and preserve useful decisions or unresolved evidence. Label retrospective summaries as such. Do not invent old tickets, dates, approvals or priorities, or make every recorded limitation a new commitment.

## Review and complete

Follow the branch, draft-PR, versioning and authorization rules in AGENTS.md. Review the actual diff against the intended behavior, check whether accepted direction requires a charter or decision update, and preserve evidence with its limitations. Run the relevant [evaluations](evals/README.md) for behavioral changes; source loading and infrastructure checks are not adherence proof.

When creating or revising skills and runbooks, use [Writing agent guidance](docs/writing-agent-guidance.md) to make the method's decisions, examples, completion conditions and references clear. Preserve accepted behavior when editing the prose; assess the complete loaded path rather than only the entry file.

If startup guidance changes, check a fresh session can find and apply it. Copilot's standard repository entry is [.github/copilot-instructions.md](.github/copilot-instructions.md); it points to the same maintenance contract. Start the host in the repository and verify its discovered instructions. A conversation created outside this checkout needs an explicit repository pointer in that host's saved project instructions. The [startup validation](docs/validation/maintainer-startup.md) records observed coverage and remaining limits.

For a saved architect project outside the checkout, use a pointer such as:

> Act as Atlas's architecture and critical-review partner unless the assignment requests implementation. Locate current `dstkwll/atlas`, read its AGENTS.md and startup references, refresh main, and inspect the assigned issue and linked PRs before substantive work. Apply additional coordination requirements configured for this environment. Recover scope and evidence from those sources; do not depend on a previous chat or infer authority from tracker status. Report unavailable sources and continue unaffected work.

Save the pointer in the host's actual project configuration and verify a fresh conversation follows it. A copy in a draft, local note or synced project mirror does not change that configuration. Keep temporary branch/task status on the issue, not in the saved pointer.
