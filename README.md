# Atlas Successor

Atlas is a small software-lead guide for the agent you already use. Give the main agent a goal; it chooses useful investigation, design, implementation, review and repair, carries the architectural context, and returns for decisions that belong to you.

The package contains one lead skill and four short, optional runbooks. It requires no ECC installation, added service, hook, orchestration runtime or connection to this project's Drive folder. Your existing host, tools and project rules remain in control.

## Use it in your project

1. Copy the complete [atlas-lead folder](.agents/skills/atlas-lead) into your project's `.agents/skills/` directory. Preserve existing files and instructions.
2. Start a fresh main-agent session in the target project.
3. Ask: **Use atlas-lead to complete [your goal]. Follow this project's rules, make ordinary implementation decisions, and bring me material choices with a recommendation.**

[Setup and troubleshooting](SETUP.md) covers Copilot in VS Code and the CLI, optional default activation, restricted environments and direct-file use if discovery is unavailable. Install only the skill folder; this repository's root files govern development of Atlas itself.

## How it behaves

The lead keeps accepted commitments separate from provisional choices. It can refine implementation as evidence arrives, correct ordinary defects within authority, and use independent review when the consequences warrant it. It maintains compact project-local continuity for work that needs to resume. A small clear fix can remain a small clear fix.

You can work collaboratively on design or delegate a bounded result. Atlas does not require a PRD, ticket graph, fixed sequence of specialists, or review ceremony for every change. It never grants permission to publish, deploy, spend or merge.

## Scope and evidence

This release advances the original three-file bootstrap into a reusable delivery package. The original bootstrap is merged; existing `dstkwll/atlas` remains a separate product. The package is intended for ordinary software work, with risk-linked assurance. It is not a guarantee of autonomous correctness or workplace-host compatibility.

[Validation evidence](docs/validation/portable-lead.md) distinguishes what was actually exercised from static checks and behavior still unverified. Work-environment details do not need to be exported to use or improve the guide locally.

## Maintain this package

Read [AGENTS.md](AGENTS.md), [current work](project-memory/current.md), and the [delivery decision](docs/decisions/2026-09-06-portable-lead.md). The reusable product is `.agents/skills/atlas-lead/`. Deeper runbooks load only when relevant; the repository's coordination history is not part of the installed product.
