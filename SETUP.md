# Install and use Atlas

Atlas guides the main agent you already use. Choose your organization's approved agent and model. The plugin contains one skill and four optional runbooks; it adds no scripts, service, hooks, MCP servers or ECC dependency.

## Copilot plugin installation

For Copilot CLI:

```shell
copilot plugin marketplace add dstkwll/atlas-successor
copilot plugin install atlas@atlas-successor
```

Start a fresh session in the project you want to work on. VS Code can also discover plugins installed by Copilot CLI. If using only VS Code, add `dstkwll/atlas-successor` to your existing `chat.plugins.marketplaces` setting, preserving the other entries. Open Extensions, search `@agentPlugins`, and install **Atlas** from **atlas-successor**. Use Copilot Agent mode.

To share the choice with coworkers, merge these entries into the work repository's existing `.github/copilot/settings.json` through its normal review process; preserve other settings:

```json
{
  "extraKnownMarketplaces": {
    "atlas-successor": {
      "source": {
        "source": "github",
        "repo": "dstkwll/atlas-successor"
      }
    }
  },
  "enabledPlugins": {
    "atlas@atlas-successor": true
  }
}
```

VS Code presents workspace plugin recommendations; CLI supports declarative installation. Availability still depends on the host version and enterprise policy. Adding the plugin does not make it the main agent's default guidance for every task.

## Use it

In a fresh Copilot chat, select the `atlas` skill from the `/` picker and give it a goal:

```text
/atlas Help me [goal]. Inspect this project first, make ordinary in-scope
implementation decisions, and bring me material choices with your recommendation.
```

Some hosts or conflicting plugins qualify the command as `/atlas:atlas`; use the entry shown in your picker. Natural language also works: **Use the Atlas skill from the atlas-successor plugin to complete [goal].** You stay in the main session, using the usual host agent.

For collaborative design, add **Work through the design with me before implementing.** For delivery, specify the desired result and constraints. Continue the conversation normally; Atlas chooses the relevant runbooks. No calibration report or workplace evidence export is needed.

To make Atlas the project's default, append this to the existing `.github/copilot-instructions.md` (or the host's existing root `AGENTS.md`), preserving current content:

```text
For software-delivery tasks, use the installed Atlas skill from atlas-successor
as operating guidance in the main session. Load only the references relevant to
the task. Existing project/organizational rules and the user's authority apply.
If the skill is unavailable, report that instead of claiming Atlas is active.
```

## Local or restricted installation

Transfer the complete `plugins/atlas/` directory through an approved route. Keep its `plugin.json`, `skills/atlas/SKILL.md` and four references together. Do not transfer repository maintenance instructions, project memory or work data.

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

## Manual skill installation and Codex

The skill remains independently portable. Copy the complete `plugins/atlas/skills/atlas/` folder into the target project's `.agents/skills/` directory, producing `.agents/skills/atlas/SKILL.md`. Personal Codex installations can put that same folder under `~/.codex/skills/atlas/`; invoke it with `$atlas` after discovery. For personal Copilot skills, use `~/.copilot/skills/atlas/` and `/atlas`.

Choose plugin installation or manual skill installation in each host. A project/personal skill can take precedence over a plugin's skill, leaving an old copy active after a plugin update. If discovery is unavailable, ask the agent to read the exact installed `SKILL.md` path and follow its references.

## Migrating existing installations

The old `atlas-lead` installation continues to work until you replace it. Preserve local edits, install the new package, confirm Atlas appears in the host's skill picker, then remove only the old `atlas-lead` folder and update explicit invocation/default-instruction references. Keep project state and other instructions.

The original **atlas@dstkwll** is a separate, larger plugin. This package does not update or replace it. Disable the original for a project when choosing the successor so both do not offer competing Atlas guidance. Do not remove the original plugin's work records or other plugins from its marketplace.

## Update or remove

For the marketplace-installed CLI plugin:

```shell
copilot plugin marketplace update atlas-successor
copilot plugin update atlas@atlas-successor
```

In VS Code, use **Extensions: Check for Extension Updates** and review the offered update. Local copied packages are updated by replacing only their package folder after preserving local edits. Start a fresh session after updating.

To stop using the CLI plugin, run `copilot plugin uninstall atlas@atlas-successor`. In VS Code, disable or uninstall its entry in Agent Plugins. Remove any project recommendation/default paragraph that would reactivate it. Leave project instructions and work records intact.

## Compatibility evidence

Checked on 2026-09-06 against [GitHub's plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [VS Code plugin documentation](https://code.visualstudio.com/docs/agent-customization/agent-plugins), and [Copilot plugin concepts](https://docs.github.com/en/copilot/concepts/agents/about-plugins). See [the packaging validation record](docs/validation/copilot-plugin.md) for actual native checks and remaining limits. Documentation support is not proof of execution in your workplace host.
