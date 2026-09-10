# Atlas

Atlas is a small software-lead guide for the agent you already use. Give the main agent a goal; it chooses useful investigation, design, implementation, review and repair, carries the architectural context, and returns for decisions that belong to you.

The package contains one lead skill, three optional artifact entry points, four core activity guides and an optional specialist runbook library. It requires no added service, hook, orchestration runtime or connection to this project's Drive folder. Your existing host, tools and project rules remain in control.

## Use it in your project

Install the **Atlas** plugin from the **atlas** marketplace in Copilot:

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@atlas
```

In a fresh main-agent chat, choose the **Atlas** profile and describe your goal. Atlas stays active for that task, so continue with ordinary follow-up messages. The [setup guide](SETUP.md) covers Copilot, Codex, Claude Code, team configuration, local packages and manual skill installation. Direct skill invocation remains available where a host does not expose the profile.

The installable product is [plugins/atlas](plugins/atlas); the standalone [Atlas skill](plugins/atlas/skills/atlas) remains usable in Codex and other file-reading hosts. This repository's root files govern maintenance and are excluded from the plugin.

## How it behaves

The lead keeps accepted commitments separate from provisional choices. It can refine implementation as evidence arrives, correct ordinary defects within authority, and use independent review when the consequences warrant it. It maintains compact project-local continuity for work that needs to resume. Exploration, advice or design can be the completed result; asking for one does not implicitly authorize implementation. A small clear fix can remain a small clear fix.

For substantial design, Atlas maintains a living brief, records meaningful decisions and develops the next usable slice in detail. It can expand that brief into a PRD or specification and produce an HTML view for co-design when useful. Small clear changes can proceed directly. Atlas does not require a ticket graph, fixed sequence of specialists or review ceremony for every change. It never grants permission to publish, deploy, spend or merge.

The [specialist library](plugins/atlas/skills/atlas/references/specialist-runbooks.md) adds focused methods for technical questions such as failure handling, types, migrations, runtime bugs, accessibility and release preparation. Atlas decides whether to use a runbook itself or delegate a bounded task. No specialist sequence is mandatory.

## Finish at a useful artifact

Ask Atlas to produce a PRD, an ordered set of testable vertical slices, or a handoff for another agent. Optional `atlas-to-prd`, `atlas-to-tickets` and `atlas-handoff` skills expose those same runbooks directly. They preserve settled intent and make remaining decisions, dependencies and test prerequisites visible. Artifact creation does not authorize implementation or tracker publication. See [setup](SETUP.md#prd-ticket-and-handoff-deliverables).

## Describe the outcome you need

After activating Atlas, use ordinary requests such as:

- “Explain how this request reaches storage; I need enough context to change validation.”
- “Find out why this workaround exists and whether its constraint still applies. Investigate only.”
- “Turn our agreed design into a PRD, then prepare testable tickets. Leave implementation for the next agent.”
- “This report links to a proposed fix. Verify whether it addresses the failure before writing another patch.”
- “Make the existing project checks usable by a fresh agent, including setup, evidence and cleanup.”
- “Migrate this component while preserving its appearance and keyboard behavior.”

Atlas chooses the relevant runbooks from the request. Teaching, investigation, verification and planning can each be the completed outcome; implementation follows the authority you actually give it.

## Scope and evidence

The package is intended for ordinary software work, with risk-linked assurance. It is not a guarantee of autonomous correctness or workplace-host compatibility.

Validation results and limits accompany each pull request. Work-environment details do not need to be exported to use or improve the guide locally.

## Maintain this package

Read [AGENTS.md](AGENTS.md), [current work](project-memory/current.md), and the [delivery decision](docs/decisions/2026-09-06-portable-lead.md). The reusable product is `plugins/atlas/`; its one canonical skill lives at `plugins/atlas/skills/atlas/`. Deeper runbooks load only when relevant; the repository's coordination history is not part of the installed product.
