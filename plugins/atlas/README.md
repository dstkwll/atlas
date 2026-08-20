# atlas plugin

Pipeline skills written against the Atlas architecture in this repository.

Unlike the [`incubator`](../incubator/README.md) plugin beside it, nothing here is forked. Each skill was written against a named stage of `architecture/02-workflow.md`, and `architecture/` remains authoritative whenever this plugin and it disagree — report the conflict rather than following the skill.

**This is a work in progress.** The first two pipeline stages have skills, alongside machine setup and the spike route. Stages 3–5 do not.

## Skills

| Skill | Stage | Produces |
|---|---|---|
| `setup-atlas` | — | `config.yaml` naming the planning root. Run once per machine, before the others. |
| `discovery` | 1 — decision discovery | `10-decisions.md`, a verbose decision log |
| `spike` | dispatched from discovery | a findings file under the run's spikes directory |
| `to-spec` | 2 — behavioural specification | `20-spec.md`, the behavioural contract |

Invocations read `atlas:<skill>` — `atlas:discovery`, `atlas:to-spec`. Codex resolves the plugin as `atlas@dstkwll`.

## Install with Copilot CLI

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@dstkwll
```

Install `atlas` without `incubator` while their skill names overlap.

## What is not here

Stages 3 (system design), 4 (program design) and 5 (ticket compilation) have no skills yet. Candidates for those, and for execution and review, live in the `incubator` plugin carrying upstream assumptions — see its README for what each is and what conflicts are known.

Two consequences worth knowing before you install this:

- **The pipeline stops after Stage 2.** `incubator`'s `to-tickets` cannot consume `20-spec.md`: it reads an enumerable `## Work Items` section and stops rather than publish when one is absent. Emitting ticket-sized units from a behavioural contract would defeat the point of the stage, so the break stands until Stage 5 is written.
- **Skill names collide with the `incubator` plugin.** `setup-atlas`, and any Stage 3–5 skill added here later, will shadow or be shadowed by an incubator skill of the same name depending on the host's resolution order. Install one or the other, not both, until the incubator shrinks.

## Status of each skill

All four are **candidates**. They were written against the architecture, which is not the same as proving the complete pipeline.

`discovery` has been executed once on a real photo-archive decision topic. It completed two rounds and produced a decision log that a fresh `to-spec` executor consumed. That Stage 2 run wrote a blocked behavioural specification and stopped correctly because two blocking questions remained. These runs exercised discovery → specification, not the rest of the pipeline.

`to-spec` was also executed against a fabricated fixture, which found a joint-followability contradiction that three adversarial reviews had missed. The fixture did not exercise supersession; the later photo-archive run did.

`spike` and `setup-atlas` have not been executed end to end. Copilot CLI 1.0.80 registered the repository's marketplace in an isolated home, installed `atlas@dstkwll`, reported all four skills, and successfully dispatched interactive `/atlas:setup-atlas`; that proves marketplace installation, plugin discovery, and the explicit invocation path, not the skill's write behavior or cross-host invocation policy.

## Conventions

Every skill here is explicit-invocation-only on hosts that support it — `disable-model-invocation: true` for Claude, `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex. These skills write durable artifacts and route workflow; none should fire because a phrase resembled a trigger. Copilot and Hermes have no confirmed equivalent, so on those hosts the guarantee is unverified.

Skills that write an artifact keep the artifact's shape in `references/`, and every rule about it in `SKILL.md`. A reference here describes shape only. That split is deliberate: when both files carried rules, the same fact lived in two places and drifted every time either was edited.

## Licence

MIT. `setup-atlas` began as a stub replacing a forked skill; the other three are original. See [`../incubator/LICENSE`](../incubator/LICENSE) for the provenance of the forked material this repository also carries.
