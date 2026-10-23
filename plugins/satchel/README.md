# Satchel

A collection of standalone skills for everyday work with an agent. Each skill works on its own, including without Atlas.

| Skill | Use it to |
| --- | --- |
| [wait-what](skills/wait-what/SKILL.md) | Re-explain something confusing with the context needed to understand it. |
| [writing-for-agents](skills/writing-for-agents/SKILL.md) | Write or revise instructions for agents, including skills. |
| [unslop](skills/unslop/SKILL.md) | Edit wordy or formulaic prose while preserving its meaning and voice. |
| [why](skills/why/SKILL.md) | Reconstruct why a decision was made from the available records. |
| [to-questionnaire](skills/to-questionnaire/SKILL.md) | Turn unresolved questions into a questionnaire someone can answer. |
| [claim-check](skills/claim-check/SKILL.md) | Assess claims against available evidence and identify uncertainty. |
| [teach-me](skills/teach-me/SKILL.md) | Learn a topic through explanation, examples and practice. |
| [reorient](skills/reorient/SKILL.md) | Catch up on current work and decisions that need you. |
| [define-goal](skills/define-goal/SKILL.md) | Turn an intention into a bounded, verifiable objective. |
| [session-canvas](skills/session-canvas/SKILL.md) | Discover and maintain a visual map of the current session. |

Choose the skill that fits the current request. The host keeps control of tools, permissions and project instructions. Invoking a skill does not authorize publishing, sending messages or changing unrelated files.

`reorient` catches you up on task progress; `wait-what` repairs a confusing explanation. `why` reconstructs a decision's history; `claim-check` assesses whether evidence supports a claim. `unslop` edits prose; `writing-for-agents` helps author agent instructions. Each can be used without the others.

`define-goal` can prepare a copyable objective on hosts without native goal tools. Defining an objective does not itself start the underlying work.

`session-canvas` works with you to decide what orientation would help, confirms a short text brief, then builds the view. It can combine exploration, progress and explanation, using Copilot's native canvas builder or a saved artifact in another host such as Codex. The same agent checks alignment after each user exchange by default; you can choose another cadence. A visible last-assessed point records the check. Automatic activity signals need host verification, and transfer between conversations is outside the first version. See the [design decision](https://github.com/dstkwll/atlas/blob/main/docs/decisions/2026-10-22-session-canvas.md) and [validation limits](https://github.com/dstkwll/atlas/blob/main/docs/validation/session-canvas.md).

## Install

For a draft checkout, load the local package for a Copilot CLI session:

```shell
copilot --plugin-dir /absolute/path/to/atlas/plugins/satchel
```

Once Satchel is merged into the marketplace's default branch, add the marketplace if needed, then install it:

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install satchel@atlas
```

Start a fresh session and select the skill through the host's skill picker, or ask the agent to use the named skill. Picker names and plugin prefixes vary by host. Satchel has no agent profile to select.

To install just one skill, copy its **complete folder** from `skills/`, including references and licenses, into your host's skill directory:

| Host | Project directory | Personal directory |
| --- | --- | --- |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Copilot | `.github/skills/` | `~/.copilot/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |

For example, copying `skills/wait-what/` into `.agents/skills/` produces `.agents/skills/wait-what/SKILL.md`. No sibling skill folder is required. In Codex, invoke `$wait-what`; in hosts with slash commands, select the discovered skill. If discovery is unavailable, ask the agent to read the exact installed `SKILL.md` path.

Choose plugin installation or manual copying for a skill in each host. Keeping both can expose duplicate entries or leave an older copy active after an update.

## Sources and evidence

The package records source credits and modification details in [PROVENANCE.md](PROVENANCE.md), separate from the task instructions. The adapted skills draw from Matt Pocock, Lauren Tan and OpenAI, with additional writing ideas from Sushruth; `claim-check` and `session-canvas` are original syntheses. Reorient began as the project owner’s original synthesis, with Ketchup guidance incorporated in the Satchel revision. Each skill with an upstream contribution retains its applicable license. Keep that license when copying a standalone skill.

All ten skills allow normal model discovery. Each has a distinct task and contains its own required instructions; Satchel adds no lead, required sequence, service, hooks, scripts or MCP servers. Session Canvas may create a session-scoped extension through Copilot's existing builder when that is the chosen surface. The authoring skill retains Matt's conceptual vocabulary and two-file structure. The teaching skill serves conversational learning rather than maintaining a course workspace. Atlas retains its separate software-lead and authoring methods.

The public [validation summary](https://github.com/dstkwll/atlas/blob/main/docs/validation/satchel.md) records observed behavior and limits; draft reviewers can read that path in their checkout or PR. Using a skill requires only its installed folder. Research history and deferred ideas belong in the project's issues and PRs.
