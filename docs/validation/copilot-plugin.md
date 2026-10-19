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
- Git-backed marketplace installation PASSES against commit `82458ca` on `feat/copilot-plugin`. A fresh disposable `COPILOT_HOME` reported one skill installed. `plugins list --kind plugin,skill --scope user,plugin --json` reports exactly one enabled `atlas` plugin from `marketplace:atlas-successor` and one enabled plugin-scope `atlas` skill, with no errors.
- Every file in the GitHub-installed package matches the candidate's `plugins/atlas/` bytes. A repository-wide relative Markdown link check and `git diff --check` pass. Later evidence/state updates do not change the tested product bytes.

The disposable configuration directories are separate from the user's actual Copilot configuration. No workplace access, authentication, model execution, VS Code UI session or enterprise deployment was exercised. Plugin recognition/discovery does not prove that the host model follows the guidance. No behavioral test was rerun for unchanged instructions.

## Local-marketplace follow-up: October 18, 2026

Isolated offline Copilot CLI **1.0.91** checks on **macOS arm64** registered a local-directory marketplace containing Atlas **0.11.0** and the independent Toolbox **0.1.0** candidate at commit `8e4bea37fd6d5a7eb97c9b4954601ece674da0d8` from [PR #51](https://github.com/dstkwll/atlas/pull/51). Installing Toolbox left Atlas disabled. Installing Atlas alongside it exposed all eight Atlas skills and all five Toolbox skills. The host described local marketplace plugins as **live**: files remained in the source checkout rather than being copied into an installation cache.

The checks used `plugin marketplace add <local-checkout>`, `plugin install <name>@atlas`, `plugin list --json` and `skill list --json`, with separate temporary configuration and cache directories. Thirteen native commands, including independent copies of the five Toolbox skill folders, completed successfully with empty stderr. The 17 Toolbox package files were frozen and hashed; they remained unchanged during the checks. A later read of the retained fixture matched all 60 Atlas files to main commit `57225e63ee31b8e477dcdd9d6eacd89cf5a45095`; that retrospective comparison is not a continuous integrity check of the earlier run.

The earlier local-directory discovery failure remains an observation of CLI 1.0.82, not a current universal limitation. The fixtures also differed, so these observations do not isolate the CLI version as the cause of the different result. The `file://` source path was not retested. These later checks establish local registration and discovery only; they do not repeat the earlier Git-backed transfer check or establish model selection, instruction adherence, VS Code behavior or workplace compatibility. No inference or user-install changes occurred.

Verify the executable version when reproducing this result. The passing checks invoked the cached 1.0.91 runtime directly with `node <runtime>/index.js --no-auto-update`; the recorded version check used that same launch path.
