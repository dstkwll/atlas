# atlas plugin

Pipeline skills written against the Atlas architecture in this repository.

Unlike the [`incubator`](../incubator/README.md) plugin beside it, nothing here is forked. Each skill was written against a named stage of `architecture/02-workflow.md`, and `architecture/` remains authoritative whenever this plugin and it disagree — report the conflict rather than following the skill.

**This is a work in progress.** Four of the pipeline's stages have skills; the rest do not. Nothing here has been exercised on real work.

## Skills

| Skill | Stage | Produces |
|---|---|---|
| `setup-atlas` | — | `config.yaml` naming the planning root. Run once per machine, before the others. |
| `discovery` | 1 — decision discovery | `10-decisions.md`, a verbose decision log |
| `spike` | dispatched from discovery | a findings file under the run's spikes directory |
| `to-spec` | 2 — behavioural specification | `20-spec.md`, the behavioural contract |

Invocations read `atlas:<skill>` — `atlas:discovery`, `atlas:to-spec`. Codex resolves the plugin as `atlas@dstkwll`.

## What is not here

Stages 3 (system design), 4 (program design) and 5 (ticket compilation) have no skills yet. Candidates for those, and for execution and review, live in the `incubator` plugin carrying upstream assumptions — see its README for what each is and what conflicts are known.

Two consequences worth knowing before you install this:

- **The pipeline stops after Stage 2.** `incubator`'s `to-tickets` cannot consume `20-spec.md`: it reads an enumerable `## Work Items` section and stops rather than publish when one is absent. Emitting ticket-sized units from a behavioural contract would defeat the point of the stage, so the break stands until Stage 5 is written.
- **Skill names collide with the `incubator` plugin.** `setup-atlas`, and any Stage 3–5 skill added here later, will shadow or be shadowed by an incubator skill of the same name depending on the host's resolution order. Install one or the other, not both, until the incubator shrinks.

## Status of each skill

All four are **candidates**. They were written against the architecture, which is not the same as verified against it — none has been run on real work, and no host has loaded this tree.

`to-spec` has been executed once against a fabricated decision log by an agent that had not seen it, which found a contradiction three adversarial reviews had missed. That is one run against one input; the supersession path was not exercised because the fixture did not carry a superseded record.

`discovery`, `spike` and `setup-atlas` have never been run at all.

## Conventions

Every skill here is explicit-invocation-only on hosts that support it — `disable-model-invocation: true` for Claude, `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex. These skills write durable artifacts and route workflow; none should fire because a phrase resembled a trigger. Copilot and Hermes have no confirmed equivalent, so on those hosts the guarantee is unverified.

Skills that write an artifact keep the artifact's shape in `references/`, and every rule about it in `SKILL.md`. A reference here describes shape only. That split is deliberate: when both files carried rules, the same fact lived in two places and drifted every time either was edited.

## Licence

MIT. `setup-atlas` began as a stub replacing a forked skill; the other three are original. See [`../incubator/LICENSE`](../incubator/LICENSE) for the provenance of the forked material this repository also carries.
