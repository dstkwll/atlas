# Atlas

Atlas is a small software-lead guide for the agent you already use. Give the main agent a goal; it chooses useful investigation, design, implementation, review and repair, carries the architectural context, and returns for decisions that belong to you.

The package contains one lead skill, four core activity guides and an optional specialist runbook library. It requires no added service, hook, orchestration runtime or connection to this project's Drive folder. Your existing host, tools and project rules remain in control.

## Use it in your project

Install the **Atlas** plugin from the **atlas-successor** marketplace in Copilot:

```shell
copilot plugin marketplace add dstkwll/atlas-successor
copilot plugin install atlas@atlas-successor
```

In a fresh main-agent chat, choose the **Atlas** profile and describe your goal. Atlas stays active for that task, so continue with ordinary follow-up messages. The [setup guide](SETUP.md) covers Copilot, Codex, Claude Code, team configuration, local packages, manual skill installation and migration from `atlas-lead` or the original Atlas plugin. Direct skill invocation remains available where a host does not expose the profile.

The installable product is [plugins/atlas](plugins/atlas); the standalone [Atlas skill](plugins/atlas/skills/atlas) remains usable in Codex and other file-reading hosts. This repository's root files govern maintenance and are excluded from the plugin.

## How it behaves

The lead keeps accepted commitments separate from provisional choices. It can refine implementation as evidence arrives, correct ordinary defects within authority, and use independent review when the consequences warrant it. It maintains compact project-local continuity for work that needs to resume. Exploration, advice or design can be the completed result; asking for one does not implicitly authorize implementation. A small clear fix can remain a small clear fix.

For substantial design, Atlas maintains a living brief, records meaningful decisions and develops the next usable slice in detail. It can expand that brief into a PRD or specification and produce an HTML view for co-design when useful. Small clear changes can proceed directly. Atlas does not require a ticket graph, fixed sequence of specialists or review ceremony for every change. It never grants permission to publish, deploy, spend or merge.

The [specialist library](plugins/atlas/skills/atlas/references/specialist-runbooks.md) adds focused methods for technical questions such as failure handling, types, migrations, runtime bugs, accessibility and release preparation. Atlas decides whether to use a runbook itself or delegate a bounded task. No specialist sequence is mandatory.

[Source provenance and adaptation](docs/research/ecc-agent-adaptation.md) records the library's origins and design choices.

## Scope and evidence

This release advances the original three-file bootstrap into a reusable delivery package. The original bootstrap is merged; existing `dstkwll/atlas` remains a separate product. The package is intended for ordinary software work, with risk-linked assurance. It is not a guarantee of autonomous correctness or workplace-host compatibility.

Validation results and limits accompany each pull request. Work-environment details do not need to be exported to use or improve the guide locally.

## Maintain this package

Read [AGENTS.md](AGENTS.md), [current work](project-memory/current.md), and the [delivery decision](docs/decisions/2026-09-06-portable-lead.md). The reusable product is `plugins/atlas/`; its one canonical skill lives at `plugins/atlas/skills/atlas/`. Deeper runbooks load only when relevant; the repository's coordination history is not part of the installed product.
