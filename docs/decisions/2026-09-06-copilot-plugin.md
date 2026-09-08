# Copilot plugin packaging

Atlas uses an Agent Plugins 1.0 root manifest and standard `skills/` folder. The `.github/plugin/marketplace.json` catalog is named `atlas`, and its Atlas plugin is installed as `atlas@atlas` from `dstkwll/atlas`.

Keep one canonical skill at `plugins/atlas/skills/atlas/`. Manual skill installation copies that same folder. Do not preserve a second source copy, add symlinks, or generate host variants. The repository maintenance entrypoint points directly to this source path.

The portable skill owns lead behavior. Copilot exposes it through a native profile that loads the shared skill into the main conversation. Skill invocation remains available independently. The package adds no runtime, hooks, service or mandatory agent hierarchy.

[Setup](../../SETUP.md) records supported installation and usage. [Packaging validation](../validation/copilot-plugin.md) and [activation validation](../validation/activation.md) distinguish native observations from unverified host behavior. Packaging supplies no authority for unrelated merges or workplace mutations.
