# Current work

## Outcome and authority

On 2026-09-06 the user requested researching Copilot plugins and progressing implementation for the successor, noting that original Atlas already supported plugins. They dislike `atlas-lead` and are considering `atlas`. This authorizes a bounded packaging change and draft PR under the repository maintenance contract; it does not authorize merge or replacing existing installations. `Atlas` is the proposed draft name, pending the user's naming response.

The preceding portable package is complete: PR #4 merged at `b8280e8a1772a35a27abe20ceb1a40c61edbb92c`. The user subsequently explicitly authorized local installation, and its five files were installed at `~/.codex/skills/atlas-lead` and verified against that commit. The old prohibition on global installation in the preceding task no longer describes that completed authorized action. Leave this working installation intact during the plugin proposal.

## Repository and progress

- Repository: `https://github.com/dstkwll/atlas-successor`.
- Current inspected main/base: `b8280e8a1772a35a27abe20ceb1a40c61edbb92c`.
- Working branch: `feat/copilot-plugin`; published [draft PR #5](https://github.com/dstkwll/atlas-successor/pull/5).
- Scope: native Copilot plugin and separate `atlas-successor` marketplace, one canonical skill directory, install/update/migration documentation, native package checks. The skill's operating behavior remains unchanged.
- Product candidate: `plugins/atlas/`, with one `atlas` skill and four runbooks. The proposed skill rename changes only its frontmatter name and title.
- Native proof: GitHub marketplace install from candidate `82458ca` succeeded, discovering one enabled Atlas plugin and one enabled Atlas skill with no errors. All installed product files match the candidate. Local-directory marketplace discovery has a documented host limitation; Git-backed installation is verified. VS Code UI and authenticated model behavior remain untested.
- Next action: obtain the user's naming/merge decision on draft PR #5. No merge authority for this change. Do not rerun initial behavioral experiments for unchanged guidance.

## Commitments and evidence

The user supplies judgment; the main agent supplies orchestration. Optional runbooks remain guidance. No ECC dependency, workflow controller, hooks, services, fixed agent roster, or new privileges. Keep repository maintenance rules and state outside the installed plugin. Preserve original Atlas as a separate product.

Original Atlas main `a57c610e133dd66ce1de75947ceced673696adb4` already uses a root Agent Plugins 1.0 manifest and `.github/plugin/marketplace.json`, under marketplace `dstkwll`. Its packaging is a donor; its orchestration is not adopted. The successor's distinct marketplace avoids claiming to update `atlas@dstkwll`.

Drive controls freshly read on 2026-09-06: `AGENTS.md` modified `2026-08-25T15:07:14.356Z`; `README.md` modified `2026-08-25T15:07:26.672Z`. Official GitHub and VS Code plugin documentation was inspected the same day. Prior behavioral evidence remains in [portable package validation](../docs/validation/portable-lead.md); new packaging evidence belongs in [plugin validation](../docs/validation/copilot-plugin.md).

Compare this replaceable snapshot with current Git and PR evidence on resume.
