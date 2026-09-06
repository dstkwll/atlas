# Use Atlas in an existing project

Atlas is Markdown guidance for your normal main agent. Use your organization's approved agent and model. It needs no extra account, ECC, script, service or network connection of its own. The host may still need its usual network access.

## Copilot in VS Code or Copilot CLI

1. Get the complete `atlas-lead` folder from this repository's `.agents/skills/` directory or the supplied bundle. Copy the folder into the target project's `.agents/skills/` directory, producing `.agents/skills/atlas-lead/SKILL.md` and its `references/` folder. Do not copy only `SKILL.md`, replace existing instructions, or copy Atlas's root `AGENTS.md` or project memory.
2. Use the project root as your workspace/current directory. Start a fresh main-agent session. A reasoning-capable model is appropriate for the lead; use the choices approved in your environment.
3. Ask: **Use atlas-lead to complete [specific goal]. Inspect this project first, make ordinary in-scope decisions, and return for material choices with your recommendation.** Copilot also supports `/atlas-lead` when the skill is discovered.

The same folder can be placed in `.github/skills/atlas-lead/` instead if that is your team's convention. Choose one location to avoid duplicate discovery. Existing project instructions and tool permissions still apply.

This is enough to begin normal work. The first task is not a request for a calibration report, raw transcript, or workplace evidence export.

## Make it the project default, if wanted

Add the following small paragraph to the project's existing `.github/copilot-instructions.md` (or root `AGENTS.md` for a host that reads it). Create a new instruction file only if the project has none. Keep all existing content and resolve actual conflicts under project policy.

```text
For software-delivery tasks, read .agents/skills/atlas-lead/SKILL.md and use it as operating guidance in the main session. Load only the references relevant to the current task. Existing project/organizational rules and the user's authority still apply.
```

If you installed under `.github/skills/`, use that path in the paragraph. This enables the lead role in the main session; it does not create a child agent. Native skill discovery alone makes the skill available, but does not guarantee it is selected for every request.

## If the skill is not discovered

Ask the main agent to read the exact installed file path and follow its links for this task. For example: **Read .agents/skills/atlas-lead/SKILL.md and use it to lead this change: [goal].** This uses the same guidance without relying on a slash-command picker.

Check that the workspace is the intended project, the folder name is `atlas-lead`, `SKILL.md` is present with its frontmatter, and all references were copied. In VS Code, `/skills` opens skill configuration; in Copilot CLI, `/instructions` shows discovered instruction files when checking the optional default paragraph. Keep enterprise restrictions in place. If the host cannot read the files, report the missing capability; do not change security settings or install another agent to work around policy.

## Other hosts and restricted environments

A file-reading agent can use the same explicit-path request. For native discovery in another host, place the complete folder in that host's documented skill location. Do not assume identical host features or install multiple copies to try to force discovery.

For work, transfer only the reusable skill folder and this setup guide through an approved route. Keep project decisions, code, state, test output and credentials in the approved environment. No Atlas Drive access or feedback connection is required. Reuse the project's existing state convention; let the lead create a small local note only when continuation needs one and its location is permitted.

## Update or remove

Review an update as a change to agent behavior. Replace only the installed `atlas-lead` folder after preserving any local edits. Keep project memory outside it. To stop using Atlas, remove the optional default paragraph and the installed skill folder; leave project instructions and work records intact. No global cleanup is needed.

## Compatibility evidence

Setup paths and invocation were checked against official documentation on 2026-09-06: [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [Copilot CLI skills reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#skills-reference), and [Copilot CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions). Host behavior can vary with version and enterprise policy. See [validation](docs/validation/portable-lead.md) for actual execution evidence and limits.
