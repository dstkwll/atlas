# atlas plugin

Pipeline skills written against the Atlas architecture in this repository.

Unlike the [`incubator`](../incubator/README.md) plugin beside it, this is Atlas-owned source rather than a vendored skill set. Its borrowed workflow shapes are credited under Licence. Each pipeline skill is written against a named stage of `architecture/02-workflow.md`, and `architecture/` remains authoritative whenever this plugin and it disagree — report the conflict rather than following the skill.

**This is a work in progress.** Intake, control-plane transitions, and the first two artifact stages have skills, alongside machine setup and the spike route. Stages 3–5 do not.

## Skills

| Skill | Stage | Produces |
|---|---|---|
| `setup-atlas` | — | `config.yaml` naming the planning root. Run once per machine, before the others. |
| `start-run` | 0 — intake and classification | immutable `run.yaml` plus initial `00-state.md` |
| `control-run` | control-plane adapter | invokes deterministic `tools/atlas_control.py` for one supported gate outcome and state transition |
| `discovery` | 1 — decision discovery | `10-decisions.md`, a verbose decision log |
| `spike` | dispatched from discovery | a findings file under the run's spikes directory |
| `to-spec` | 2 — behavioural specification | `20-spec.md`, the behavioural contract |

Invocations read `atlas:<skill>` — `atlas:discovery`, `atlas:control-run`, `atlas:to-spec`. Codex resolves the plugin as `atlas@dstkwll`. In Copilot CLI, invoke the slash command explicitly: a natural-language prompt naming `setup-atlas` loaded the plugin but selected the wrong built-in skill, while `/atlas:setup-atlas` dispatched correctly.

## Install with Copilot CLI

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@dstkwll
```

The deterministic controller requires Python 3.9 or newer and PyYAML. `setup-atlas` verifies both and offers an install command only with explicit approval.

## What is not here

Stages 3 (system design), 4 (program design) and 5 (ticket compilation) have no skills yet. Candidates for those, and for execution and review, live in the `incubator` plugin carrying upstream assumptions — see its README for what each is and what conflicts are known.

One consequence worth knowing before you install this:

- **The pipeline stops after Stage 2.** `incubator`'s `to-tickets` cannot consume `20-spec.md`: it reads an enumerable `## Work Items` section and stops rather than publish when one is absent. Emitting ticket-sized units from a behavioural contract would defeat the point of the stage, so the break stands until Stage 5 is written.

## Status of each skill

All six are **candidates**. They were written against the architecture, which is not the same as proving the complete pipeline.

`discovery` has been executed once on a real photo-archive decision topic. It completed two rounds and produced a decision log that a fresh `to-spec` executor consumed. That Stage 2 run wrote a blocked behavioural specification and stopped correctly because two blocking questions remained. These runs exercised discovery → specification, not the rest of the pipeline.

`to-spec` was also executed against a fabricated fixture, which found a joint-followability contradiction that three adversarial reviews had missed. The fixture did not exercise supersession; the later photo-archive run did.

A manual Copilot CLI smoke test exercised the six-skill branch in isolated homes and a disposable fixture repository; the generated fixture is not committed evidence. `start-run` read a repository-relative planning root, preserved the fixture's exact Git baseline, snapshotted selected and inactive-route gate policies, and wrote `run.yaml` plus `00-state.md` at `.planning/<feature-slug>/`. Explicit `/atlas:discovery` produced a cold-read, gate-ready `10-decisions.md`; an explicit human approval advanced it to specification; and `/atlas:to-spec` produced a gate-ready draft `20-spec.md`. After the prompt-owned controller was replaced, a fresh plugin install included `tools/atlas_control.py`; current `/atlas:control-run` invoked that installed program, applied the configured `HUMAN` specification gate, wrote the immutable approved copy and approval receipt, and advanced revision 2 to revision 3 at program design. No alternate run directory was created. Reproducible transition evidence lives in `tests/test_atlas_control.py` and `tests/test_atlas_control_hardening.py`; `spike` and `setup-atlas` have not been executed end to end.

The deterministic program seals base intake before discovery and has separating tests for base-policy tampering, `HUMAN`, `AUTO`, accepted-amendment, rejection, and `spec -> discovery` reopen transitions, including byte-for-byte preservation of `run.yaml`, tamper-evident amendment and approved-artifact receipts, pre-draft reopen, path containment, source-state/schema validation, and recovery from an interrupted multi-file transition. `AGENT_REVIEW`, `CONDITIONAL`, `HUMAN_IF_CHANGED`, and inactive-route activation remain fully snapshotted but fail closed as explicit implementation gaps rather than being emulated by a prompt.

Copilot CLI 1.0.80 registered the repository's marketplace, installed `atlas@dstkwll`, and reported all six skills. Interactive slash invocation dispatched the intended skills. Non-interactive `-p` did not dispatch the slash command and instead treated it as ordinary prompt text, so that route is not claimed as supported.

## Conventions

Every skill here is explicit-invocation-only on hosts that support it — `disable-model-invocation: true` for Claude, `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex. These skills write durable artifacts and route workflow; none should fire because a phrase resembled a trigger. Copilot and Hermes have no confirmed equivalent, so on those hosts the guarantee is unverified.

Skills that write an artifact keep the artifact's shape in `references/`, and every rule about it in `SKILL.md`. A reference here describes shape only. That split is deliberate: when both files carried rules, the same fact lived in two places and drifted every time either was edited.

## Licence

MIT. `discovery`, `to-spec`, `start-run`, and `control-run` are original. `setup-atlas` began as an Atlas-owned replacement scaffold for an imported setup skill. `spike` substantially rewrites and adapts credited workflow language and shape — risk-ordered decomposition, comparison spikes, interactable artifacts, and next-spike selection — from Hermes Agent's bundled `spike` skill, itself adapted from the GSD `/gsd-spike` workflow (MIT © 2025 Lex Christopherson, [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)). See [`../incubator/LICENSE`](../incubator/LICENSE) for the separately forked material this repository carries.
