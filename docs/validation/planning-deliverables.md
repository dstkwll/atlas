# Planning deliverable checks

Checked 2026-09-09. The package adds three optional artifact entry points and three shared runbooks; Atlas remains the lead. These checks concern instructional behavior and package discovery, not implementation of an execution system.

## Actual exercises

A separate agent received the candidate skills and a synthetic accepted request to cancel unstarted queued jobs, owner-only, with atomic start/cancel exclusion and existing status polling. It was given queue API/state facts and an unavailable test DB, but no intended ticket structure or expected output. It produced a PRD, a ticket plan and a recipient handoff in an isolated temporary workspace.

Primary inspection of those artifacts found one cohesive vertical slice covering the stated scope, ownership enforcement, competing transitions, persisted polling and regression evidence. It did not split persistence, implementation and tests into independently complete claims. It marked response semantics and compatibility as decisions to resolve from the target or user, distinguished supplied facts from inspected code, and retained missing DB access as a prerequisite. The supplied test command was not run and no red phase or race guarantee was claimed proven. It did not implement, publish tracker issues or send the handoff. A single synthetic example is not a general quality or completeness rate.

An independent Copilot reviewer, gpt-5.6-sol/high, received the three runbooks, ticket wrapper and affected lead/test/setup changes. It returned no blocking findings. Primary inspection verified its packaging caveats against the other two wrappers, shared relative paths and included notices. This was text review, not a live host behavioral test.

## Packaging checks

- Skill Creator format validation passed for the main skill and all three wrappers.
- All 81 plugin-relative file links resolved; manifest versions agreed; whitespace checks passed.
- Copilot CLI 1.0.82 installed the local package in an isolated COPILOT_HOME and reported four skills installed. Native listing showed atlas, atlas-to-prd, atlas-to-tickets and atlas-handoff enabled, with no errors.
- A preliminary plugin-dir listing did not enumerate candidate skills in the existing user environment; it was not counted as discovery proof. The isolated installed-package listing is the positive evidence. Direct installation warns of deprecation; documented ongoing installation remains marketplace-based.
- The wrappers require the sibling atlas directory and report unavailable shared guidance. The documented manual full-package copy retains all siblings and notices; the main skill alone retains natural-language access to all three runbooks.
- A separate structural check copied only the three wrappers to an isolated directory. Each shared-source path was absent and each wrapper explicitly required reporting that dependency rather than claiming execution. No remembered-source fallback was used; this did not exercise a host model's response to missing files.

## Limits and retained evidence

No workplace host, VS Code picker, live tracker publishing, cross-host transfer, unavailable-source model session or actual TDD implementation was exercised. Native CLI discovery does not prove the model loads and follows every skill. The forward exercise used candidate source files in an independent agent context, not the installed Copilot runtime. No personal installed copy was updated. Broader multi-ticket projects and recipient reliability remain unmeasured.

Synthetic PRD, ticket, handoff and independent-review artifacts are retained in the sibling workspace directory research/2026-09-09-planning-deliverables. Donor dispositions remain in the existing source-adaptation record; reusable skills contain no donor runtime dependency.
