# Copilot plugin packaging

Disposition: bounded implementation choice under the user's request to progress Copilot plugin support. The proposed `Atlas` plugin/skill name remains a naming choice for review; it does not rename or supersede the original `dstkwll/atlas` repository.

Use an Agent Plugins 1.0 root manifest and standard `skills/` folder, matching the packaging mechanism already present in original Atlas main `a57c610e133dd66ce1de75947ceced673696adb4`. Add a `.github/plugin/marketplace.json` catalog with the distinct name `atlas-successor`. Copilot CLI and VS Code document both mechanisms.

Keep one canonical skill at `plugins/atlas/skills/atlas/`. Manual skill installation copies that same folder. Do not preserve a second source copy, add symlinks, generate host variants, or import original Atlas controllers. The repository maintenance entrypoint points directly to the new source path. The manifest, marketplace and package README are packaging; the four runbooks remain optional plain Markdown.

The old user installation remains usable while the proposal is reviewed. Migration is explicit and preserves local changes, project state and other instructions. The original `atlas@dstkwll` plugin remains independent; choose the intended version per project instead of enabling competing guidance.

[Setup](../../SETUP.md) records installation and migration. [Validation](../validation/copilot-plugin.md) separates observed discovery from untested host behavior. Merge and replacing existing user installations require their applicable authority; this proposal grants neither.
