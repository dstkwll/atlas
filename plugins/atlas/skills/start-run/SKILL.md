---
name: start-run
description: Create immutable Atlas Stage 0 intake and initialize its tiny planning controller.
disable-model-invocation: true
---

# Start run

Create one Stage 0 run at `<planning-root>/<feature-slug>/`. Resolve the planning root through `atlas:setup-atlas`; never invent another run hierarchy.

## 1. Resolve and accept intake

Inspect every affected repository and record its stable identity plus commit baseline. Classify the goal, risk, workflow, governance, execution/environment policy, roster, the selected ordered stages, every selected gate, and every run-relevant conditionally reachable route. Discovery's product-closure authority must be `AGENT_REVIEW` or `HUMAN`.

Discovery exits through a semantic product-closure boundary, so its authority must be `AGENT_REVIEW` or `HUMAN`. Reject `AUTO`. Stage 0 acceptance freezes intake but does not pre-approve the living PRD candidate.

Use [`references/run-file.md`](references/run-file.md) for the exact `run.yaml` shape. Preview the complete file and obtain human acceptance before writing it.

## 2. Initialize machine authority

Write only immutable `<run>/run.yaml`, then run:

```shell
python3 tools/atlas_control.py initialize --run <run-directory>
```

Initialization validates intake, writes authoritative `<run>/control.json` by atomic replacement, seals the exact-byte `run.yaml` hash, and best-effort generates `<run>/00-state.md`. See [`references/state-file.md`](references/state-file.md).

If initialization fails, stop. Never calculate authority fields in prose, edit `control.json` directly, or treat `00-state.md` as state authority. Do not create `10-decisions.md`; discovery owns it.

## 3. Hand off

Read the first phase and authority from `control.json` and `run.yaml`. Offer `atlas:discovery`. Producers record completion/readiness only. `atlas:control-run` performs read-only checking, consumes configured authority, and records at most one transition.

## Intake correction

If discovery proves a repository identity or baseline wrong, follow the complete shared procedure in [`../../references/intake-correction.md`](../../references/intake-correction.md). Do not improvise or mutate intake authority directly.
