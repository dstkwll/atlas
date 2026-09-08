# Copilot plugin packaging

Historical naming decision. The later [repository naming decision](2026-09-08-repository-naming.md) replaces the repository and marketplace names; the original repository described below is now `dstkwll/legacy-Atlas`.

Disposition: bounded implementation choice under the user's request to progress Copilot plugin support. The user accepted **Atlas** as the primary plugin/skill name on 2026-09-06 and explicitly authorized merging PR #5. This does not rename or supersede the original `dstkwll/atlas` repository.

Use an Agent Plugins 1.0 root manifest and standard `skills/` folder, matching the packaging mechanism already present in original Atlas main `a57c610e133dd66ce1de75947ceced673696adb4`. Add a `.github/plugin/marketplace.json` catalog with the distinct name `atlas-successor`. Copilot CLI and VS Code document both mechanisms.

Keep one canonical skill at `plugins/atlas/skills/atlas/`. Manual skill installation copies that same folder. Do not preserve a second source copy, add symlinks, generate host variants, or import original Atlas controllers. The repository maintenance entrypoint points directly to the new source path. The manifest, marketplace and package README are packaging; the four runbooks remain optional plain Markdown.

The old user installation remains usable while the proposal is reviewed. Migration is explicit and preserves local changes, project state and other instructions. The original `atlas@dstkwll` plugin remains independent; choose the intended version per project instead of enabling competing guidance.

[Setup](../../SETUP.md) records installation and migration. [Validation](../validation/copilot-plugin.md) separates observed discovery from untested host behavior. The user's subsequent instruction to merge and keep Atlas as primary authorizes this merge and completing the local rename, preserving local edits. It grants no authority for unrelated merges or workplace mutations.
