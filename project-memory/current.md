# Current work

Dan authorized renaming the original repository to private `dstkwll/legacy-Atlas`, renaming this repository from `dstkwll/atlas-successor` to public `dstkwll/atlas`, reclaiming the original URL, and replacing or removing the Mac mini personal Atlas skill. Update affected local remotes and active package references while preserving repository histories and local work. Workplace installs are detached according to Dan; do not access the workplace or alter Hermes. Repository source updates follow the maintainer draft-PR process.

Repository identity before migration: original GitHub ID `1332926254`, main `a57c610e133dd66ce1de75947ceced673696adb4`; successor ID `1356247587`, main `28149a22df08760ead4cd71dc613e544dceea814`. These identities, not the reused URL, distinguish legacy history from the active product.

The activation/discovery changes have merged. The shared packaged skill remains the behavior source; native checks and limits are in `docs/validation/activation.md`. This rename changes product location and installation references, not lead behavior.

Drive root controls freshly read on 2026-09-08; AGENTS modified `2026-08-25T15:07:14.356Z`, README modified `2026-08-25T15:07:26.672Z`. Their old `dstkwll/atlas` references refer to the original repository and must be interpreted by repository identity during this migration. Do not apply the legacy architecture to the successor merely because the URL was reused.

GitHub renames and visibility change are complete and verified by repository ID and unchanged main commits. The original local checkout now points to `legacy-Atlas`; both known successor checkouts point to `atlas`. Their directories and worktrees are preserved. Installation-reference changes are being prepared on `chore/atlas-repository-name` for the normal draft-PR process.

The Mac mini personal skill at `~/.codex/skills/atlas` has been refreshed from the merged skill; all 26 files match. Its previous contents are preserved outside discovery in the workspace's `local-backups/atlas-before-rename-20260908-120939/` directory. Native local package recognition, 79 relative file links, marketplace/manifest identity agreement and whitespace checks pass.
