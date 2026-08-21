---
name: start-run
description: Create immutable Atlas Stage 0 intake and initialize its tiny planning controller.
disable-model-invocation: true
---

# Start run

Create one Stage 0 run at `<planning-root>/<feature-slug>/`. Resolve the planning root through `atlas:setup-atlas`; never invent another run hierarchy.

Resolve `<atlas-plugin-root>` from this installed skill before invoking tools: it is the third parent of this file (`SKILL.md` → `start-run/` → `skills/` → the plugin root) and must contain `tools/atlas_control.py`. Use that resolved absolute path; never assume the caller's working directory.

## 0. Refuse run collisions before writing

Choose a short, descriptive, stable slug made only of lowercase letters, digits, and single hyphens. Absolute paths, separators, `.`, and `..` are invalid. Resolve the planning root selected by `atlas:setup-atlas` to an existing absolute directory, then run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_control.py" resolve-run-path --planning-root "<absolute-planning-root>" --slug "<feature-slug>"
```

The command returns JSON containing `path`, `device`, and `inode`. Keep all three values together. Use `path` exactly as the target and later as `initialize --run`; pass the unchanged device/inode values to initialization. Never reconstruct the path or recompute its identity. The command atomically creates a missing target directory, and rejects unsafe slugs, symlinked roots or targets, non-directory collisions, and any target that escapes the root. Inspect that target before producing intake and before writing `run.yaml`. Never overwrite an existing `run.yaml`; require the target path to be unique.

- If `run.yaml` and `control.json` already describe this goal, do not reinitialize; resume the existing run according to authoritative state. A `PLANNING` run resumes at current `control.json.phase`. A discovery gate in `STALE` follows [`../../references/intake-correction.md`](../../references/intake-correction.md); a gate in `REJECTED` is terminal, so report `blocked_reason` and stop. Reject any other incoherent state rather than guessing a handoff.
- If `run.yaml` exists without `control.json`, treat it as interrupted initialization: show its exact accepted bytes and obtain confirmation, then rerun `resolve-run-path` for that same slug and root to prepare the current directory identity before running `initialize` against the unchanged file.
- If the existing run describes a different goal, choose a different slug. Never merge two runs because their names collide.

## 1. Resolve and accept intake

Inspect the current Git repository when present and ask for every other repository already known to be affected. Record each stable identity with its commit baseline; never admit one without the other.

Stage 0 is recommend-only. Classify the eight risk dimensions in [`references/run-file.md`](references/run-file.md), then recommend the amount of decomposition independently from authority:

- `trivial` — direct ticket/execution with no discovery or design producer;
- `normal` — Program Design before tickets, with Discovery selected only when product decisions still need resolution;
- `architectural` — System Design plus Program Design, again selecting Discovery only when product decisions still need resolution;
- `fog_of_war` — research, exploration, or spikes must stabilize the work before the design pipeline.

A workflow name does not imply an exact stage sequence or gate map. Exact selected stages and authorities remain explicit intake. Use a real configured policy when one exists; otherwise present evidence-backed alternatives and ask rather than invent policy.

Governance (`exploratory`, `standard`, `high_assurance`, or `autonomous`) describes the desired assurance posture but does not itself choose authority or supply a gate map. Use actual configured execution/environment/roster values when present; otherwise present explicit evidence-backed options rather than treating an illustrative example as a default. Record the selected ordered stages beginning with the earliest admissible producer. When discovery is selected, it must be first. If `system_design` is selected, ask once at intake: present `agent_led` and `co_design` neutrally, require the user's explicit choice, and record it in `system_design_participation`. The classifier neither recommends nor chooses this value. If `system_design` is omitted, record `system_design_participation: null`. Participation changes collaboration only, never gate authority; downstream System Design reads the frozen value and does not re-ask.

Classify every selected gate and every run-relevant conditionally reachable route. Apply the exact stage-specific legality in [`references/run-file.md`](references/run-file.md), not the general authority vocabulary: Discovery allows `AGENT_REVIEW|HUMAN`; System Design allows `HUMAN|AGENT_REVIEW|HUMAN_IF_CHANGED`; Program Design allows `HUMAN|AGENT_REVIEW`; and tickets allow `HUMAN|AGENT_REVIEW|CONDITIONAL` in V1. Semantic boundaries never use raw `AUTO`. Stage 0 acceptance freezes intake but does not pre-approve new or reused PRD material.

Use [`references/run-file.md`](references/run-file.md) for the exact `run.yaml` shape. Preview the complete file and obtain human acceptance before writing it.

## 2. Initialize machine authority

Write only immutable `<run>/run.yaml`, then run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_control.py" initialize --run "<path>" --prepared-device "<device>" --prepared-inode "<inode>"
```

Initialization validates intake, writes authoritative `<run>/control.json` by atomic replacement, seals the exact-byte `run.yaml` hash, and best-effort generates `<run>/00-state.md`. See [`references/state-file.md`](references/state-file.md).

Initialization may coexist with a pre-existing `20-prd.md`, but creates no acceptance for it. It rejects pre-existing `10-decisions.md` and amendments. If initialization fails, stop. Never calculate authority fields in prose, edit `control.json` directly, or treat `00-state.md` as state authority.

Read the resulting `control.json.phase`. When it is `system_design`, `program_design`, or `tickets`, initialize the separate downstream planning snapshot exactly once:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" initialize --run "<path>"
```

This command uses its own `.atlas-planning.lock` and creates only `planning-control.json`; it never edits Stage 0–2 `control.json`. If it fails, report the exact error and stop. Do not retry by editing either control file. Do not run it while `control.json.phase` is `discovery`.

## 3. Hand off

Read the current phase and authority from `control.json` and `run.yaml`. If current `control.json.phase` is `discovery`, offer `atlas:discovery`. Otherwise, hand off to the owner of the actual current phase; this controller fails closed there and creates no synthetic discovery gate. Producers record completion/readiness only. `atlas:control-run` performs read-only checking, consumes configured authority, and records at most one transition.

If the current phase has no first-party Atlas owner, stop and report that implementation gap; never substitute an incubator skill silently.

## Intake correction

If selected discovery proves a repository identity or baseline wrong, follow the complete shared procedure in [`../../references/intake-correction.md`](../../references/intake-correction.md). Do not improvise or mutate intake authority directly.
