# Satchel

A collection of standalone skills for everyday work with an agent. Each skill works on its own, including without Atlas.

| Skill | Use it to |
| --- | --- |
| [wait-what](skills/wait-what/SKILL.md) | Re-explain something confusing with the context needed to understand it. |
| [writing-for-agents](skills/writing-for-agents/SKILL.md) | Write or revise instructions for agents, including skills. |
| [to-questionnaire](skills/to-questionnaire/SKILL.md) | Turn unresolved questions into a questionnaire someone can answer. |
| [claim-check](skills/claim-check/SKILL.md) | Assess claims against available evidence and identify uncertainty. |
| [teach-me](skills/teach-me/SKILL.md) | Learn a topic through explanation, examples and practice. |
| [reorient](skills/reorient/SKILL.md) | Catch up on current work and decisions that need you. |
| [define-goal](skills/define-goal/SKILL.md) | Turn an intention into a bounded, verifiable objective. |

Choose the skill that fits the current request. The host keeps control of tools, permissions and project instructions. Invoking a skill does not authorize publishing, sending messages or changing unrelated files.

`reorient` catches you up on task progress; `wait-what` repairs a confusing explanation. `define-goal` can prepare a copyable objective on hosts without native goal tools. Defining an objective does not itself start the underlying work.

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

To install just one skill, copy its **complete folder** from `skills/`, including references and license notices, into your host's skill directory:

| Host | Project directory | Personal directory |
| --- | --- | --- |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Copilot | `.github/skills/` | `~/.copilot/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |

For example, copying `skills/wait-what/` into `.agents/skills/` produces `.agents/skills/wait-what/SKILL.md`. No sibling skill folder is required. In Codex, invoke `$wait-what`; in hosts with slash commands, select the discovered skill. If discovery is unavailable, ask the agent to read the exact installed `SKILL.md` path.

Choose plugin installation or manual copying for a skill in each host. Keeping both can expose duplicate entries or leave an older copy active after an update.

## Sources and evidence

The package includes source attribution and applicable licenses with each adapted skill. The public [adaptation record](https://github.com/dstkwll/atlas/blob/main/docs/satchel/adaptations.md) explains what changed and why. The [validation summary](https://github.com/dstkwll/atlas/blob/main/docs/validation/satchel.md) distinguishes observed behavior from untested conditions. [Atlas ideas](https://github.com/dstkwll/atlas/blob/main/docs/satchel/atlas-ideas.md) records proposals for later discussion.

The published links above resolve after merge; draft reviewers can read the same paths in their checkout or PR. These records support maintenance; using the skills requires only their installed folders. The package adds no service, hooks, scripts or MCP servers.
