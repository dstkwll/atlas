---
name: start-run
description: Create or resume an Atlas run; initialize Stage 0 or route from authoritative on-disk state.
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

- If `run.yaml` and `control.json` already describe this goal, do not reinitialize. Resume from the controller that currently owns the live cursor:
  - If authoritative `control.json.phase` is `discovery`, `control.json` remains current authority. A discovery gate in `STALE` follows [`../../references/intake-correction.md`](../../references/intake-correction.md); a gate in `REJECTED` is terminal, so report `blocked_reason` and stop. Otherwise resume Discovery.
  - If authoritative `control.json.phase` is `system_design`, `program_design`, or `tickets`, run the shared downstream handoff command before choosing a downstream owner:

    ```shell
    python3 "<atlas-plugin-root>/tools/atlas_planning.py" ensure --run "<run-directory>"
    ```

    This recovers an interrupted Product Definition Approval → planning handoff when `planning-control.json` is absent and verifies complete existing planning state when present. On success, re-read `planning-control.json`; validated `planning-control.json.phase` is the actual current planning phase. Apply the exact §3 dispatch and do not rerun Product Definition Approval or hand off from the frozen downstream phase in `control.json`.
  - Reject any other incoherent state rather than guessing a handoff.
- If `run.yaml` exists without `control.json`, treat it as interrupted initialization: show its exact accepted bytes and obtain confirmation, then rerun `resolve-run-path` for that same slug and root to prepare the current directory identity before running `initialize` against the unchanged file.
- If the existing run describes a different goal, choose a different slug. Never merge two runs because their names collide.

## 1. Resolve and accept intake

Inspect the current Git repository when present and ask for every other repository already known to be affected. Record each stable identity with its commit baseline; never admit one without the other.

Read the existing confirmed machine binding for every proposed stable repository identity before accepting intake. If one is missing or an explicitly requested replacement is needed, invoke `atlas:setup-atlas` internally for that one identity/source pair. Do not ask the user to leave `start-run`, invoke setup manually, or restart intake. After setup returns, reload machine bindings and require the exact confirmed identity/source pair before resolving the full canonical commit object ID. A declined or failed binding confirmation stops the same intake without writing `run.yaml`.

Resolve every admitted baseline to the repository's full canonical commit object ID before previewing `run.yaml`. Against the user-confirmed local Git source, run a non-mutating `git rev-parse --verify "<requested-baseline>^{commit}"` with optional locks, replacement objects, and lazy fetch disabled; require the returned lowercase hexadecimal object ID to be the repository's full 40- or 64-character canonical form. Record that returned object ID, not the input ref. New intake never stores a branch, tag, `HEAD`, or abbreviated object ID as `baseline`. If the exact commit is not locally readable, stop before writing intake; `start-run` never fetches or guesses a replacement.

Stage 0 is recommend-only. Classify the eight risk dimensions in [`references/run-file.md`](references/run-file.md), then recommend the amount of decomposition independently from authority:

- `trivial` — direct ticket/execution with no discovery or design producer;
- `normal` — Program Design before tickets, with Discovery selected only when product decisions still need resolution;
- `architectural` — System Design plus Program Design, again selecting Discovery only when product decisions still need resolution;
- `fog_of_war` — research, exploration, or spikes must stabilize the work before the design pipeline.

A workflow name does not imply an exact stage sequence or gate map. Exact selected stages and authorities remain explicit intake. Use a real configured policy when one exists; otherwise present evidence-backed alternatives and ask rather than invent policy.

Governance (`exploratory`, `standard`, `high_assurance`, or `autonomous`) describes the desired assurance posture but does not itself choose authority or supply a gate map. Use actual configured execution/environment/roster values when present; otherwise present explicit evidence-backed options rather than treating an illustrative example as a default. Record the selected ordered stages beginning with the earliest admissible producer. When discovery is selected, it must be first. If `system_design` is selected, ask once at intake: present `agent_led` and `co_design` neutrally, require the user's explicit choice, and record it in `system_design_participation`. The classifier neither recommends nor chooses this value. If `system_design` is omitted, record `system_design_participation: null`. Participation changes collaboration only, never gate authority; downstream System Design reads the frozen value and does not re-ask.

Classify every selected gate and every run-relevant conditionally reachable route. Apply the exact stage-specific legality in [`references/run-file.md`](references/run-file.md), not the general authority vocabulary: Discovery allows `AGENT_REVIEW|HUMAN`; System Design allows `HUMAN|AGENT_REVIEW|HUMAN_IF_CHANGED`; Program Design allows `HUMAN|AGENT_REVIEW`; and tickets allow `HUMAN|AGENT_REVIEW` in V1. Semantic boundaries never use raw `AUTO`. Stage 0 acceptance freezes intake but does not pre-approve new or reused PRD material.

Use [`references/run-file.md`](references/run-file.md) for the exact `run.yaml` shape. Preview the complete file and obtain human acceptance before writing it.

## 2. Initialize machine authority

Write only immutable `<run>/run.yaml`, then run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_control.py" initialize --run "<path>" --prepared-device "<device>" --prepared-inode "<inode>"
```

Initialization validates intake, writes authoritative `<run>/control.json` by atomic replacement, seals the exact-byte `run.yaml` hash, and best-effort generates `<run>/00-state.md`. See [`references/state-file.md`](references/state-file.md).

Initialization may coexist with a pre-existing `20-prd.md`, but creates no acceptance for it. It rejects pre-existing `10-decisions.md` and amendments. If initialization fails, stop. Never calculate authority fields in prose, edit `control.json` directly, or treat `00-state.md` as state authority.

Read the resulting `control.json.phase`. When it is `system_design`, `program_design`, or `tickets`, ensure the separate downstream planning snapshot at the direct handoff:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" ensure --run "<run-directory>"
```

This idempotent command uses its own `.atlas-planning.lock`. It strictly initializes `planning-control.json` when absent; when present, it verifies the complete current planning state and succeeds without mutation. It never edits Stage 0–2 `control.json`. Invalid or mismatched existing state fails loudly and is never overwritten. If it fails, report the exact error and stop. Do not retry by editing either control file. Do not run it while `control.json.phase` is `discovery`.

## 3. Hand off

Prefer the host's safe nested skill invocation mechanism for every internal owner. If the host refuses nested invocation because the sibling is intentionally non-implicit, load the exact installed sibling `SKILL.md` as the current owner procedure using [`../../references/internal-owner-loading.md`](../../references/internal-owner-loading.md). Require either confirmed nested loading or the exact calibrated fallback before following that owner.

Read authoritative `control.json`. If its current phase is `discovery`, it owns the live cursor; invoke `atlas:discovery` internally without asking the user for a skill command. Discovery performs its own exact Product Definition Approval control handoff. After Discovery and its internal Product Definition Approval handoff return, re-read authoritative `control.json`: if Discovery still owns a pending or blocked cursor, stop without retrying; if phase advanced to `system_design`, `program_design`, or `tickets`, complete the shared `ensure` handoff from §2 and continue from validated planning state. If initial or resumed control phase already names `system_design`, `program_design`, or `tickets`, likewise complete `ensure` and re-read `planning-control.json`; validated `planning-control.json.phase` is the actual current planning phase and validated `planning-control.json.status` determines whether planning is pending or complete. Hand off to that owner, not to the frozen downstream handoff phase in `control.json`.

Receive an invocation-local continuation posture from Gazetteer when provided; otherwise use `INTERACTIVE`. Never persist this posture, infer it from frozen governance or authority, or let it alter gate legality. Mechanical producer-to-controller handoffs always complete. A HUMAN gate stops at its approval surface after the selected producer has prepared its candidate; it does not block entry into that already-selected producer. After an accepted boundary changes the meaningful phase, `INTERACTIVE` reports what completed, recommends the next meaningful phase, and returns so Gazetteer can ask “Continue?”; `AUTO_CONTINUE` announces and enters the next owner. Either posture always stops for HUMAN judgment at the authority surface, ambiguity, unchanged pending state, `BLOCKED`, `DESIGN_BLOCKED`, rejection, or an unimplemented owner. Continuation never converts continuation into approval and never satisfies a gate.

For `AUTO_CONTINUE`, use the existing bounded continuation loop, not one-shot dispatch. After an invoked producer and its internal control handoff return, run `ensure` again and re-read validated `planning-control.json`; route only from that fresh phase and status. After an accepted transition, `AUTO_CONTINUE` must enter the next selected producer even when that producer's configured gate is HUMAN; stop only after that producer has prepared its candidate and reaches the HUMAN approval surface. Never stop merely because the newly entered phase will eventually require HUMAN acceptance. The only legal downstream continuation after `system_design` is `program_design` or `tickets`; after `program_design` it is `tickets`; after pending `tickets` it is `READY_FOR_EXECUTION`. Invoke at most three downstream producers during one `start-run` invocation. Outside the exact repair flow, apply this stop rule: If the phase is unchanged while status remains `PLANNING`, the invoked stage's gate remains `PENDING`, the transition is unexpected, or an invoked owner stops `BLOCKED` or `DESIGN_BLOCKED`, stop without retrying that producer. Never derive a producer dynamically from the stage list.

A validated `BLOCKED` planning state is resumable only for these exact triples:

- `BLOCKED/system_design/SYSTEM_DESIGN_STALE` → run `python3 "<atlas-plugin-root>/tools/atlas_planning.py" reserve-repair-attempt --run "<run-directory>" --stage system_design`, require success, then enter `atlas:system-design` as an internal skill call.
- `BLOCKED/program_design/PROGRAM_DESIGN_RESUMED` → run the same command with `--stage program_design`, require success, then enter `atlas:program-design` as an internal skill call.

The reservation command durably commits and reload-verifies the next attempt before returning. Re-read `planning-control.json`, require the matching incremented `attempts_used` and `current_attempt`, and only then invoke that exact producer. Exhaustion or any reservation failure stays `BLOCKED`: report it and stop. Any other `BLOCKED` status/phase/reason combination is not routable and stops unchanged. The producer performs the existing internal `atlas:control-planning` handoff and configured authority flow; never ask the user to route a stage or issue a separate authority command.

If validated planning status is `READY_FOR_EXECUTION`, stop at the execution boundary. Require phase `tickets`, a current approved tickets gate, and exact ticket-graph acceptance; report the accepted graph version/hash and do not invoke any producer or execution owner.

For validated `PLANNING` state:

- If validated planning phase is `system_design`, invoke `atlas:system-design` internally.
- If validated planning phase is `program_design`, invoke `atlas:program-design` internally.
- If validated planning phase is `tickets`, invoke `atlas:compile-tickets` internally.

Preserve the existing Product Definition Approval, System Design, and Program Design paths. This dispatch adds only the first-party Stage 5 compiler and keeps execution fail-closed. Producers record candidate readiness only; `atlas:control-run` and `atlas:control-planning` consume configured authority and each records at most one transition. If any other phase has no first-party Atlas owner, stop and report the implementation gap; never substitute an incubator skill silently.

## Intake correction

If selected discovery proves a repository identity or baseline wrong, follow the complete shared procedure in [`../../references/intake-correction.md`](../../references/intake-correction.md). Do not improvise or mutate intake authority directly.
