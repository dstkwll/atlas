# atlas plugin

The Atlas skill set, published as a plugin so the same source tree installs on
GitHub Copilot CLI, Claude Code, and OpenAI Codex CLI. Invoked as `atlas:<skill>`
where the host namespaces plugin skills, or by bare skill name where it does not.

## Provenance

These skills derive from [Matt Pocock's agent skills](https://github.com/mattpocock/skills)
(MIT, see [`LICENSE`](./LICENSE)), vendored into the Workbench `mp` plugin at upstream
commit `84fdeffd12f2ee307994d1eb6feb48173b6e0502` and forked here.

**This is a hard fork.** Upstream sync machinery — the pristine `vendor/` tree, the
`sync.config.json` manifest, the rename overlay, and the PowerShell build — was
deliberately dropped. Skills are hand-editable source, not build output. Workbench
overlay text that previously layered on at build time is folded into the skill bodies
it belonged to. Merging future upstream changes is a manual diff against the pinned
commit above, by choice.

## Layout

```
plugins/atlas/
  skills/<name>/SKILL.md   The skills. Edit these directly.
  references/              Shared runtime contracts (advance points here)
  plugin.json              Copilot CLI manifest
  .codex-plugin/           Codex CLI manifest
  LICENSE                  Upstream MIT license
```

The marketplace index lives at the repository root in
[`.agents/plugins/marketplace.json`](../../.agents/plugins/marketplace.json) under the
marketplace name `dstkwll`, so Codex resolves this plugin as `atlas@dstkwll`.

## Skills

| Skill | Origin |
|---|---|
| `advance` | Workbench-authored |
| `codebase-design` | upstream |
| `diagnosing-bugs` | upstream |
| `domain-modeling` | upstream |
| `factory-code-review` | upstream `code-review` |
| `factory-implement` | upstream `implement` |
| `factory-research-with-sources` | upstream `research` |
| `factory-setup` | upstream `setup-matt-pocock-skills` |
| `grill-with-docs` | upstream |
| `grilling` | upstream |
| `improve-codebase-architecture` | upstream |
| `prototype` | upstream |
| `tdd` | upstream |
| `to-spec` | upstream + folded overlay |
| `to-tickets` | upstream + folded overlay |
| `wayfinder` | upstream |

Four skills carry a `factory-` prefix because their bare names are generic enough to
collide on hosts that flatten every skill into one namespace. The rest keep their
upstream names, and cross-skill references were rewritten to match.

## Known gaps

This is an initial import, not a finished set. Outstanding work:

- `advance` still resolves its driver config from `~/.copilot/config/mp-advance.json`
  and reads Obsidian vault topic folders. Both need repointing at Atlas's
  `.planning/<feature-slug>/` artifact layout.
- `factory-setup` still carries upstream's GitHub/GitLab/local tracker branching and
  the Workbench dev-workflow topic option. It should be trimmed to the Atlas layout.
- Skill-to-stage assignment against `architecture/02-workflow.md` is deliberately not
  attempted here.
- No installer. Each host reads the tree from its own configured location.
- Per-host invocation control (`disable-model-invocation` and its Codex equivalent) is
  not set, so auto-invocation behavior varies by host.
