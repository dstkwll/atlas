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

On hosts supporting per-agent skill preload, selecting the profile also loads the shared Atlas core into the agent's context. Runbooks remain available for selective consultation. The profile retains instructions to read the canonical file and recover it after context loss, including on hosts that ignore preload metadata. Preload improves instruction availability; it does not guarantee adherence or restoration in every host. See [preload compatibility checks](docs/validation/copilot-core-preload.md).

The skill fallback is available from the `/` picker as `/atlas` or, when qualified, `/atlas:atlas`. Natural language also works: **Use the Atlas skill from the atlas plugin for this task: [goal].** Skill activation likewise applies to that task rather than requiring the command on each follow-up.

For collaborative design, add **Work through the design with me before implementing.** For delivery, explicitly ask for implementation and specify the desired result and constraints. Atlas chooses the relevant runbooks. When a runbook fits the activity or uncertainty, Atlas consults it and applies the relevant parts, with a brief notice naming it and its purpose. Task size is not the threshold, and consultation does not require a full process or new artifact. An Atlas load event alone does not establish runbook use; straightforward answers and mechanical edits with no meaningful uncertainty may need no additional runbook. No calibration report or workplace evidence export is needed.

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

Ask Atlas naturally: **Turn this into a PRD**, **Break this into executable vertical slices**, or **Prepare a handoff for the next agent**. It uses the same shared runbooks as the optional skills `atlas-to-documentation`, `atlas-to-tickets` and `atlas-handoff`. These requests finish at the artifact unless further work is authorized; they do not publish tracker issues or start implementation automatically.

The plugin includes the lead plus documentation, tickets, handoff, blast-radius and reflection entry points. For manual installation of the artifact entry points, copy the complete contents of `plugins/atlas/skills/` into your chosen host's skill directory, keeping all skill folders as siblings. The entry points require the shared `atlas` folder and its notices; copying a wrapper alone is incomplete. Copying only `atlas` still supports these outcomes through its shared runbooks and ordinary conversation.

In Codex, select the discovered skill or use `$atlas-to-documentation`, `$atlas-to-tickets` or `$atlas-handoff`. In other hosts, select the corresponding installed skill from the host's skill picker or ask it to read the exact installed entry path; namespacing and picker support vary. The Atlas agent profile stays the same. A skill name identifies the deliverable, not a separate lead or mandatory stage.

## Continuity and context recovery

There is no separate Atlas setup skill or automatic first-run wizard. The configuration file is optional: the lead resolves the destination when a task first needs durable records. Before the first durable write for a task, it should explain that it saves working notes for recovery, identify the approved project/configured location or repository fallback, and mention that you can choose another approved folder or vault. You can simply say “Keep this task's notes in <folder>”; no configuration knowledge is needed. Ask it to remember that location for future tasks in this project or across your projects if you want a persistent default. Atlas should clarify that scope if your request leaves it ambiguous. It should not silently turn a one-task choice into a global preference. It asks only when the destination is unclear or unsuitable. Selecting the Copilot Atlas profile is sufficient; you do not need to invoke the skill separately or request routine tracking files.

To choose a persistent personal default, you can ask Atlas to set `artifacts.planning_root` in `~/.config/atlas/config.yaml`, preserving existing settings. For example, `artifacts: { planning_root: .planning }` selects a root relative to each target repository. An approved absolute vault path can be used instead. Merely needing a record does not authorize changing global configuration, and project restrictions still override that default.

For task records and planning artifacts, Atlas first reuses the topic's approved home. Where configured, `artifacts.planning_root` in project settings or `~/.config/atlas/config.yaml` selects a repository-relative or absolute location, including a vault. Project restrictions override personal defaults; a personal vault never authorizes exporting workplace material. If no convention exists, the fallback is `.planning/<topic>/` in the target repository. Atlas reports the destination rather than silently switching it when inaccessible.

A new substantial PRD defaults to a self-contained `prd.html`: readable requirements and diagrams plus collapsed agent recovery context. It can be the source of record without a Markdown twin; existing authoritative formats remain respected. Default related files are `tickets/index.md`, numbered slice Markdown files, and `handoff.md`, all under the same topic. Vault catalog/index rules still apply without requiring duplicated PRD content. The optional Fluent 2–informed HTML starter is offline and framework-free. Material decisions and handoffs update the PRD; small tasks do not require one.

When ongoing work requires decisions, unresolved questions or next steps to survive the conversation, Atlas should establish or update the project's existing task record to retain the canonical skill location, active task and scope, and pointers to material decisions, evidence and the next action. If no existing record or brief is adequate, the default is `<planning-root>/<topic>/current.md`; a sufficient existing PRD needs no duplicate. This is a recovery path, not additional permission. It avoids a new Atlas ledger and does not require you to remind the agent on every turn. After a meaningful record or planning-document update, Atlas should briefly summarize what changed and provide a file link or usable path, grouped into its ordinary progress or final response.

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

## Documentation, impact and reflection

`atlas-to-documentation` is the canonical documentation entry point. Its hint lists `prd (default) | guide | architecture | reference — topic or source`. A bare invocation defaults to PRD when a topic is available; a requested guide, architecture document, reference or existing-document update takes precedence. The hint is descriptive text, not a promised selectable dropdown. Copilot documents [argument hints](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference); exact picker presentation and plugin prefixes depend on the host.

PRDs retain the recoverable HTML contract. Substantial architecture documents share its presentation, diagrams and recovery guidance, with architecture-specific content. Keep architecture inside the PRD when useful; do not create a mandatory companion. Guides and references use the existing format or ordinarily Markdown. All use the approved topic home.

Ask “what could this break?” or invoke `atlas-blast-radius` for focused impact analysis. Ask for a retrospective or invoke `atlas-reflect` to write contextual lessons in a separate topic reflection file. Atlas may offer reflection at a useful milestone but does not run it merely because a task ends. Reflection is explicit-only through Copilot/Claude skill metadata and Codex invocation policy; the runbook also owns the request boundary, since discovery metadata is not permission enforcement.

Arena has no skill entry point. Atlas may offer a confirmed, bounded comparison using available independent workers. It introduces no fixed model panel, cloud requirement or coordination service.
