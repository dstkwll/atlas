# Install and use Atlas

Atlas guides the main agent you already use. Choose your organization's approved agent and model. The plugin contains one lead skill, optional artifact entry points, core activity guides and specialist runbooks; it adds no scripts, services, hooks or MCP servers.

## Copilot plugin installation

For Copilot CLI:

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@atlas
```

Start a fresh session in the project you want to work on. VS Code can also discover plugins installed by Copilot CLI. If using only VS Code, add `dstkwll/atlas` to your existing `chat.plugins.marketplaces` setting, preserving the other entries. Open Extensions, search `@agentPlugins`, and install **Atlas** from **atlas**. Use Copilot Agent mode.

To share the choice with coworkers, merge these entries into the work repository's existing `.github/copilot/settings.json` through its normal review process; preserve other settings:

```json
{
  "extraKnownMarketplaces": {
    "atlas": {
      "source": {
        "source": "github",
        "repo": "dstkwll/atlas"
      }
    }
  },
  "enabledPlugins": {
    "atlas@atlas": true
  }
}
```

VS Code presents workspace plugin recommendations; CLI supports declarative installation. Availability still depends on the host version and enterprise policy. Adding the plugin does not make it the main agent's default guidance for every task.

## Activate it for a task

In a fresh Copilot Agent-mode chat, choose the **Atlas** profile from the agent picker and give it a goal:

```text
Help me [goal]. Inspect this project first, make ordinary in-scope
implementation decisions, and bring me material choices with your recommendation.
```

In Copilot CLI, enter `/agent` and select `atlas:atlas`, or start a session with `copilot --agent atlas:atlas`. The plugin-qualified name is required by the checked CLI. Profile discovery depends on the installed plugin and host version; if the profile is not offered, use the skill fallback below. [GitHub's custom-agent documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli#using-a-custom-agent) describes `/agent` and `--agent` selection.

The profile directs the main session to load Atlas. It specifies no model or tool override; the host controls tool availability, permissions and project instructions. Activate it once for the task, then use normal follow-up messages until the goal is complete or you replace its scope. State the assignment you want: exploration, explanation, critique, advice and design are valid completed outcomes and do not implicitly authorize implementation.

The skill fallback is available from the `/` picker as `/atlas` or, when qualified, `/atlas:atlas`. Natural language also works: **Use the Atlas skill from the atlas plugin for this task: [goal].** Skill activation likewise applies to that task rather than requiring the command on each follow-up.

For collaborative design, add **Work through the design with me before implementing.** For delivery, explicitly ask for implementation and specify the desired result and constraints. Atlas chooses the relevant runbooks. No calibration report or workplace evidence export is needed.

To make Atlas the project's default, append this to the existing `.github/copilot-instructions.md` (or the host's existing root `AGENTS.md`), preserving current content:

```text
For software exploration, design and delivery tasks, read and apply the installed Atlas skill from the
atlas plugin in the main session. Its canonical entry is the plugin's
skills/atlas/SKILL.md; load only references relevant to the task. Existing
project/organizational rules and the user's authority apply. If that guidance
is unavailable, report it instead of claiming Atlas is active.
```

For a manual project installation, use the exact entry path `.agents/skills/atlas/SKILL.md` in that paragraph instead of the plugin path. This optional default makes the recovery source explicit; it does not activate Atlas on hosts that ignore the project instructions or expand what Atlas may do.

## Local or restricted installation

Transfer the complete `plugins/atlas/` directory through an approved route. Keep its `plugin.json`, `com.github.copilot/` profile directory, complete `skills/` directory and third-party notices together. Do not transfer repository maintenance instructions, project memory or work data.

For VS Code, add its absolute directory to the existing `chat.pluginLocations` map with value `true`. Example on Windows (use your actual path):

```json
{
  "chat.pluginLocations": {
    "C:/Tools/atlas": true
  }
}
```

For a Copilot CLI session using the local package:

```shell
copilot --plugin-dir /absolute/path/to/atlas
```

This mounts the plugin for that session. The native CLI also currently supports `copilot plugins install /absolute/path/to/atlas`, but warns that direct installs are deprecated; prefer the marketplace for ongoing installation. Local directory marketplaces have a discovery limitation in the tested CLI; see [validation](docs/validation/copilot-plugin.md).

## Manual skill installation, Codex and Claude Code

The skill remains independently portable. Copy the complete `plugins/atlas/skills/atlas/` folder into the target project's `.agents/skills/` directory, producing `.agents/skills/atlas/SKILL.md`. Personal Codex installations can put that same folder under `~/.agents/skills/atlas/` (the checked local Codex also discovers the older `~/.codex/skills/atlas/` location); invoke it with `$atlas` after discovery, or select it through Codex's `/skills` interface when available. For personal Copilot skills, use `~/.copilot/skills/atlas/` and `/atlas`.

For Claude Code, copy the complete folder to `~/.claude/skills/atlas/` for personal use or `.claude/skills/atlas/` for one project, then invoke `/atlas` in the main session. This package does not provide a Claude agent profile. Claude documents that invoked skills persist on later turns and are reattached through automatic compaction within a shared content budget; see [Skill content lifecycle](https://code.claude.com/docs/en/skills#skill-content-lifecycle). Do not use `claude --agent atlas`: Claude agent profiles replace the default system prompt and this package intentionally defers such a profile, as described in [Claude's agent documentation](https://code.claude.com/docs/en/sub-agents).

Choose plugin installation or manual skill installation in each host. Duplicate installations can expose competing Atlas entries or leave an old copy active after a plugin update; check the source the host actually loads. If discovery is unavailable, ask the agent to read the exact installed `SKILL.md` path and follow its references.

For an optional Codex project default, add the default-guidance paragraph above to the existing root `AGENTS.md`, using `.agents/skills/atlas/SKILL.md` as its source. Codex reads project instructions when starting work; this supplies an entry path independent of an earlier skill invocation. Preserve the project's other instructions. See [Codex project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## PRD, ticket and handoff deliverables

Ask Atlas naturally: **Turn this into a PRD**, **Break this into executable vertical slices**, or **Prepare a handoff for the next agent**. It uses the same shared runbooks as the optional skills `atlas-to-prd`, `atlas-to-tickets` and `atlas-handoff`. These requests finish at the artifact unless further work is authorized; they do not publish tracker issues or start implementation automatically.

The plugin includes all four skill folders. For manual installation of the artifact entry points, copy the complete contents of `plugins/atlas/skills/` into your chosen host's skill directory, keeping `atlas`, `atlas-to-prd`, `atlas-to-tickets` and `atlas-handoff` as siblings. The three entry points require the shared `atlas` folder and its notices; copying a wrapper alone is incomplete. Copying only `atlas` still supports all three outcomes through ordinary conversation.

In Codex, select the discovered skill or use `$atlas-to-prd`, `$atlas-to-tickets` or `$atlas-handoff`. In other hosts, select the corresponding installed skill from the host's skill picker or ask it to read the exact installed entry path; namespacing and picker support vary. The Atlas agent profile stays the same. A skill name identifies the deliverable, not a separate lead or mandatory stage.

## Continuity and context recovery

For work that needs continuity, let Atlas use the project's existing task record to retain the canonical skill location, active task and scope, and pointers to material decisions, evidence and the next action. This is a recovery path, not additional permission. It avoids a new Atlas ledger and does not require you to remind the agent on every turn.

Hosts differ in how they restore instructions after compaction or resume. Recoverable files let the agent reload Atlas and task state; they do not guarantee automatic restoration across every host. If the host loses both the activation instruction and the source pointer, the skill cannot arrange its own reload. A host-loaded profile or optional project instruction supplies a separate entry path; loading instructions still does not guarantee model adherence. Optional project instructions can point to the installed skill as the task entry path, but a project file cannot guarantee identical behavior on a host that does not load it. After a context loss, Atlas should reload its canonical skill, relevant references and the existing task record before dependent work, and report when any of those sources cannot be recovered. [Copilot CLI context management](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management) and [Claude skill lifecycle](https://code.claude.com/docs/en/skills#skill-content-lifecycle) describe their respective host behavior; neither is a cross-host Atlas guarantee.

Remote or mobile clients connected to a configured coding host may expose the host's active session, but this package has not verified a mobile Atlas picker. Confirm activation in the connected host rather than assuming the local desktop picker is available.

## Update or remove

For the marketplace-installed CLI plugin:

```shell
copilot plugin marketplace update atlas
copilot plugin update atlas@atlas
```

In VS Code, use **Extensions: Check for Extension Updates** and review the offered update. Local copied packages are updated by replacing only their package folder after preserving local edits. Start a fresh session after updating.

To stop using the CLI plugin, run `copilot plugin uninstall atlas@atlas`. In VS Code, disable or uninstall its entry in Agent Plugins. Remove any project recommendation/default paragraph that would reactivate it. Leave project instructions and work records intact.

## Compatibility evidence

Plugin packaging was checked on 2026-09-06 against [GitHub's plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [VS Code plugin documentation](https://code.visualstudio.com/docs/agent-customization/agent-plugins), and [Copilot plugin concepts](https://docs.github.com/en/copilot/concepts/agents/about-plugins). See [the packaging validation record](docs/validation/copilot-plugin.md) for actual native checks and remaining limits. The [activation and continuity record](docs/validation/activation.md) covers the subsequent native profile, follow-up and compaction checks. Documentation support is not proof of execution in your workplace host.
