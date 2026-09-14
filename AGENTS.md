# Maintaining Atlas

Before substantive work, read [the architect charter](docs/architect-charter.md), [the contributor workflow](CONTRIBUTING.md), and [README.md](README.md). Inspect the actual remote, branch, HEAD and worktree, refresh main when available, and read the assigned GitHub issue, linked PRs and relevant accepted decisions. Preserve unrelated changes. After context loss, recover these sources before dependent work; a previous chat or status note is not current evidence.

Use [the Atlas lead contract](plugins/atlas/skills/atlas/SKILL.md) as the main-session operating guidance. Read deeper references only for the present task. The portable skill owns lead behavior; this file owns maintenance rules specific to this repository.

## Authority and scope

Current `dstkwll/atlas` main and accepted decisions describe the product. Explicit current user decisions can authorize a change to that baseline; distinguish accepted amendments from proposals, observed behavior and historical permissions. Surface contradictions instead of silently choosing a new direction.

The assignment determines the role: architects preserve coherence and pressure-test direction; implementers deliver the authorized change. Read the charter in either role. Ownership means carrying that assignment through, not choosing unrelated backlog work or gaining publication, merge or spending authority. An issue, assignment, board column or earlier closed task grants no permission by itself.

Repository guidance must suffice for public maintenance. Apply additional personal or organizational coordination rules only where configured; report unavailable required sources and continue unaffected work. Private research is not a prerequisite for contributors or plugin users.

## Change and validation

Work on a branch, review the final diff, preserve evidence, and return a draft PR. Merge requires explicit user authorization. Ordinary in-scope implementation and corrections need no second approval. Record material authority changes before relying on them.

For each PR changing the installable `plugins/atlas/` package, advance its version from current main before publication. Use a patch increment for corrections and a minor increment for added capabilities; identify compatibility breaks explicitly. Keep `plugins/atlas/plugin.json`, the Atlas plugin entry in `.github/plugin/marketplace.json`, and this single-plugin marketplace's metadata version aligned. Recheck against current main when another package change merges first. Maintainer-only documentation and evaluation changes outside the package need no bump. A merged commit does not automatically increment manifest versions or publish a GitHub Release; release publication still requires its applicable authority.

Treat instructional changes as behavior changes. Identify important behavior being retained, moved behind a trigger, or explicitly superseded. Check realistic outcomes with fresh independent review where authority or complex guidance makes producer bias material. Format checks do not prove judgment. Keep runtime tests for actual behavior; do not create validators of exact prose or headings.

Keep product guidance self-contained and portable. Do not add external agent-framework dependencies, universal stages, workflow controllers, queues, schedulers, retry engines, schemas, compatibility systems or bulk architecture copies without an explicit accepted decision and demonstrated need. Native skill placement is packaging, not a runtime adapter.

Keep donor comparisons and adaptation research in the maintainer's research notes. Retain current design rationale needed for safe maintenance in the repository and applicable third-party attribution and license notices in distributions. Product use and maintenance must not depend on private notes. Keep detailed trial histories and tooling diagnostics in local maintainer evidence; public validation summaries retain coverage, concise observations and material limitations.

Keep the assigned issue or PR current at material decisions, blockers, handoffs and completion, following CONTRIBUTING.md. Before publication, check whether accepted intent changed and update the charter or relevant decision in the same PR; otherwise preserve intent and correct implementation drift. Installed copies must not include this repository's maintenance instructions, active work state or historical publication authority.
