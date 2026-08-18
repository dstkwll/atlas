# incubator plugin

> **The four skills written for Atlas — `discovery`, `to-spec`, `spike`, `setup-atlas` — moved
> to the [`atlas`](../atlas/README.md) plugin. What remains here is forked material.**
>
> ## Status: incubation. Not canonical.
>
> This plugin contains **candidate, borrowed, transitional, and stand-in skills used to
> develop Atlas**. They are executable experiments, not architectural authority.
>
> - These are **not** canonical implementations of Atlas workflow, artifacts, or authority.
> - They **intentionally retain** Workbench, Matt Pocock, and other upstream assumptions.
> - They exist to be **used as stand-ins** while Atlas behavior is designed and calibrated.
> - **`architecture/` is authoritative** whenever there is a conflict.
> - Behavior in this plugin is **not evidence** that the Atlas architecture has accepted
>   that behavior.
> - A skill graduates into a future canonical Atlas plugin **only after explicit
>   reconciliation and acceptance**.
>
> Invocation is deliberately prefixed `incubator:` — `incubator:factory-implement`, not
> `atlas:factory-implement`. The friction is the point: every call should remind the caller
> that the skill has not earned canonical status.

There is no canonical `plugins/atlas/` yet. That is expected, not an omission.

## Architectural precedence

If a skill in this plugin conflicts with:

- anything under `architecture/`,
- the repository-root `AGENTS.md`, or
- an applicable canonical repository operating contract,

**the canonical repository contract wins.** The agent must report the conflict rather than
silently treating incubator behavior as authoritative — per `AGENTS.md`, apparent
contradictions among authoritative sources are surfaced, not reconciled in place.

Canonical architecture is never edited to make an imported skill fit.

## Provenance

These skills derive from [Matt Pocock's agent skills](https://github.com/mattpocock/skills)
(MIT, see [`LICENSE`](./LICENSE)), vendored into the Workbench `mp` plugin at upstream
commit `84fdeffd12f2ee307994d1eb6feb48173b6e0502` and forked here.

`spike` additionally adapts structure — risk-ordered decomposition, comparison spikes with a
head-to-head close, the interactable-artifact preference, and next-spike selection — from
Hermes Agent's bundled `spike` skill, itself adapted from the GSD project's `/gsd-spike`
workflow (MIT © 2025 Lex Christopherson, [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)).
No text was copied; the borrowing is at the level of workflow shape.

**This is a hard fork.** Upstream sync machinery — the pristine `vendor/` tree, the
`sync.config.json` manifest, the rename overlay, and the PowerShell build — was
deliberately dropped. Skills are hand-editable source, not build output. Workbench overlay
text that previously layered on at build time is folded into the skill bodies it belonged
to. **Merging future upstream changes is a manual diff against the pinned commit above**,
by choice.

## Layout

```
plugins/incubator/
  skills/<name>/SKILL.md   The skills. Edit these directly.
  references/              Shared runtime contracts (advance points here)
  plugin.json              Copilot CLI manifest
  .codex-plugin/           Codex CLI manifest
  LICENSE                  Upstream MIT license
```

The marketplace index lives at the repository root in
[`.agents/plugins/marketplace.json`](../../.agents/plugins/marketplace.json) under the
marketplace name `dstkwll`, so Codex resolves this plugin as `incubator@dstkwll`.

## Candidate status

Lightweight statuses, not a lifecycle: `candidate` (may contribute to a canonical skill),
`stand-in` (usable now, will be replaced), `reference` (read for ideas, not for behavior),
`needs-reconciliation` (known conflict with canonical architecture).

| Skill | Origin | Current role | Status | Known Atlas conflict |
|---|---|---|---|---|
| `factory-implement` | upstream `implement` | Temporary implementation worker | **stand-in / candidate** | Its review-and-commit behavior has **not** been reconciled with the canonical executor → deterministic validators → contract reviewer → design/quality reviewer → controller-acceptance flow. It is **not** the canonical ticket factory or definition-of-done loop. |
| `factory-code-review` | upstream `code-review` | Two-axis review of a diff | **candidate / reference** | Its Standards and Spec axes may contribute to Atlas review roles, but they are **not** equivalent to canonical contract-review plus design/quality-review semantics. |
| `to-tickets` | upstream | Ticket authoring | **needs reconciliation — currently incompatible with `to-spec`** | Retains issue-tracker and `.scratch/` assumptions. Not adapted to the canonical planning artifact model or to execution-compilation semantics. **It reads a `## Work Items` section and identifiers of the form `R1`, and stops rather than publish when they are absent; the rewritten `to-spec` emits `## Requirements` and `R-001`.** The pipeline cannot advance from spec to tickets until Stage 5 is written. Emitting Work Items from Stage 2 would reintroduce ticket-sized units into the behavioural contract, so the break is left visible rather than papered over. |
| `advance` | Workbench-authored | Phase-boundary judge and driver | **candidate / reference — not control-plane authority** | Contains useful candidate ideas on evidence, criterion mapping, readiness, bounded workers, and orchestration UX. Its lifecycle, authority model, leash and ship semantics, and review semantics are **not** canonical Atlas behavior. One observed defect is fixed in its evidence contract: see "Observed defects" below. |
| `codebase-design` | upstream | Design reasoning | candidate | Not audited. |
| `diagnosing-bugs` | upstream | Debugging loop | candidate | Not audited. |
| `domain-modeling` | upstream | Domain modeling | candidate | Not audited. |
| `factory-research-with-sources` | upstream `research` | Research resolution | candidate | Not audited. |
| `grill-with-docs` | upstream | Grilling against documents | candidate | Not audited. |
| `grilling` | upstream | Frontier-ordered interview | candidate | Not audited. |
| `improve-codebase-architecture` | upstream | Architecture improvement | reference | Not audited. |
| `prototype` | upstream | Throwaway artifact to react to | candidate | Overlaps `spike` in name only: `prototype` builds an artifact to react to and its verdict is a taste judgment; `spike` runs experiments against a hypothesis with verdict criteria declared beforehand. Otherwise not audited. |
| `tdd` | upstream | Red-green-refactor loop | candidate | Not audited. |
| `wayfinder` | upstream | Multi-session decision map | candidate | Not audited. |

"Not audited" means exactly that: no claim is made either way about conflict with canonical
architecture. Exhaustively auditing every skill is out of scope for this import.

## Invocation control

Skills that can materially mutate, route workflow, implement code, publish, or decide
readiness are marked explicit-invocation-only where the host supports it — Claude Code's
`disable-model-invocation: true` in frontmatter, and Codex's
`policy.allow_implicit_invocation: false` in `agents/openai.yaml`.

Currently explicit-only: `advance`, `factory-implement`, `factory-code-review`,
`to-tickets`, `grill-with-docs`,
`improve-codebase-architecture`, `wayfinder`.

**Unverified by host.** Copilot CLI and Hermes have no confirmed equivalent of these keys.
Whether either silently ignores them, and therefore whether an explicit-only skill can be
auto-invoked there, has not been tested. No cross-host normalization layer was built.

## Observed defects

Recorded because they were seen in a real run, not inferred from reading.

**`advance` ship judge fabricated a Wayfinder map (fixed).** On an effort that reached
specification through ordinary grilling rather than Wayfinder, the terminal ship-readiness
judge required a topic-root `map.md` — the hardcoded subject identity of its
`discovery-unclosed` gap — found none, and wrote one. A read-only judge manufactured the
evidence it was judging.

The contract already knew grilling efforts have no map: presence routing branches on
`map.md`, and the `grilling-to-spec` branch states that ordinary grilling never requires
Wayfinder. The ship judge simply did not consult that, and `discovery-unclosed` carried no
applicability test. `references/lifecycle-evidence.md` now scopes the gap to efforts where
`map.md` is present, and states that a judge never creates an artifact it requires.

The general lesson is recorded in Atlas's canonical architecture, since it applies to every
reviewer the architecture specifies, not only to this skill.

## Known gaps

- `advance` still resolves its driver config from `~/.copilot/config/mp-advance.json` and
  reads Obsidian vault topic folders rather than an Atlas planning root.
- Ticket-state vocabulary is upstream's (`needs-triage`, `ready-for-agent`,
  `ready-for-human`, `wontfix`), not Atlas's run and ticket states. Deliberately not
  reconciled here: `advance` reads that vocabulary and `to-tickets` writes it, so changing one
  without the other breaks the loop. The rewritten `to-spec` no longer participates.
- Skill-to-stage assignment against `architecture/02-workflow.md` is not attempted.
- No installer. Each host reads the tree from its own configured location.
- No host has loaded this tree. Manifest shapes match the documented formats; that is a
  static check, not a runtime one.
