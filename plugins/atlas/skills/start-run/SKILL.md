---
name: start-run
description: Create immutable Atlas Stage 0 intake and initialize its tiny planning controller.
disable-model-invocation: true
---

# Start run

Create one Stage 0 run at `<planning-root>/<feature-slug>/`. Resolve the planning root through `atlas:setup-atlas`; never invent another run hierarchy.

## 1. Resolve and accept intake

Inspect every affected repository and record its stable identity plus commit baseline. Classify the goal, risk, workflow, governance, execution/environment policy, roster, selected stages, and every selected gate. Record recommendation evidence and explicit overrides.

Discovery and specification contain semantic questions, so their authority must be `AGENT_REVIEW` or `HUMAN`. Reject `AUTO` for either boundary. Stage 0 acceptance freezes intake but does not pre-approve a candidate.

Use [`references/run-file.md`](references/run-file.md) for the exact `run.yaml` shape. Preview the complete file and obtain human acceptance before writing it.

## 2. Initialize machine authority

Write only immutable `<run>/run.yaml`, then run:

```shell
python3 tools/atlas_control.py initialize --run <run-directory>
```

Initialization validates intake, writes authoritative `<run>/control.json` by atomic replacement, seals the exact-byte `run.yaml` hash, and best-effort generates `<run>/00-state.md`. See [`references/state-file.md`](references/state-file.md).

If initialization fails, stop. Never calculate authority fields in prose, edit `control.json` directly, or treat `00-state.md` as state authority. Do not create `10-decisions.md`; discovery owns it.

## 3. Hand off

Read the first phase and authority from `control.json` and `run.yaml`. Offer the matching producer skill. Producers record completion/readiness only. `atlas:control-run` performs read-only checking, consumes configured authority, and records at most one transition.

## Intake correction

Discovery may find a wrong repository or baseline. It records `intake_stale: true`, then `atlas:control-run mark-stale` blocks the run. After explicit human acceptance, write exactly the next contiguous `amendments/NNN-*.md` using [`references/run-amendment.md`](references/run-amendment.md), then run:

```shell
python3 tools/atlas_control.py apply-amendment --run <run-directory>
```

The controller stores only accepted amendment count and resulting effective configuration hash in `control.json`. There is no amendment ledger, receipt, or hash chain. `run.yaml` remains byte-for-byte unchanged.
