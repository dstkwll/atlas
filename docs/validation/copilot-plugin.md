# Copilot plugin packaging validation

Date: 2026-09-06. Baseline: `b8280e8a1772a35a27abe20ceb1a40c61edbb92c` (merged PR #4). Candidate: `feat/copilot-plugin`.

This change packages the existing guidance and proposes the name `atlas`. It does not claim new delivery behavior. Historical behavioral evidence remains in [portable-lead.md](portable-lead.md).

## Checks performed

- The skill-creator format validator passes for `plugins/atlas/skills/atlas`.
- Comparison against the baseline proves the four references are byte-identical and `SKILL.md` changes only `name: atlas-lead` to `name: atlas` and the title `Atlas lead` to `Atlas`.
- All skill-relative references resolve. The marketplace's source resolves to the plugin, and its name/version match the manifest.
- Copilot CLI 1.0.82 recognizes the package with `--plugin-dir ... plugin list`.
- In a disposable `COPILOT_HOME`, native direct local installation reports one skill installed. `plugins list --kind plugin,skill --json` reports enabled plugin `atlas` version `0.1.0` and enabled plugin-scope skill `atlas`, with no errors. Direct installs emit a deprecation warning, so the documented ongoing path uses a marketplace.
- A separate disposable local-directory marketplace reports successful install but the subsequent skill listing omits `atlas`. This is a host-path limitation, not a passing skill-discovery result. A `file://` marketplace source is rejected as a local path in this CLI version. Do not recommend either as a verified workaround.
- Git-backed marketplace installation PASSES against commit `82458ca` on `feat/copilot-plugin`. In a fresh disposable `COPILOT_HOME`, `copilot plugin marketplace add 'dstkwll/atlas-successor#feat/copilot-plugin'` followed by `copilot plugin install atlas@atlas-successor` reports one skill installed. `plugins list --kind plugin,skill --scope user,plugin --json` reports exactly one enabled `atlas` plugin from `marketplace:atlas-successor` and one enabled plugin-scope `atlas` skill, with no errors.
- Every file in the GitHub-installed package matches the candidate's `plugins/atlas/` bytes. A repository-wide relative Markdown link check and `git diff --check` pass. Later evidence/state updates do not change the tested product bytes.

The disposable configuration directories are separate from the user's actual Copilot configuration. No workplace access, authentication, model execution, VS Code UI session or enterprise deployment was exercised. Plugin recognition/discovery does not prove that the host model follows the guidance. No behavioral test was rerun for unchanged instructions.
