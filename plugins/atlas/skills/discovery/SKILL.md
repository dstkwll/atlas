---
name: discovery
description: Produce the Stage 1 decision candidate without claiming boundary acceptance.
disable-model-invocation: true
---

# Discovery

Resolve a fuzzy goal into durable decisions and evidence at `<run>/10-decisions.md`. Produce neither a specification nor workflow approval.

## 1. Resume authoritative state

Read immutable `run.yaml`, authoritative `control.json`, and accepted `amendments/NNN-*.md`. Ignore `00-state.md` for legality. Discovery must be the current phase and the candidate's `effective_config_revision` must match control.

Create or resume the exact candidate shape in [`references/run-layout.md`](references/run-layout.md). After a deterministic reopen, the producer—not the controller—writes the next candidate version. The expected version is one greater than the latest accepted discovery record in `control.json`.

## 2. Resolve the frontier

Record the problem/announcement tests. Ask user-owned preferences; investigate facts through research, repository exploration, or a spike. Persist the entire open frontier before asking, and append each settled decision immediately using [`references/decision-record.md`](references/decision-record.md).

A repository or baseline correction sets `intake_stale: true` and `gate_ready: false`, then routes to:

```shell
python3 tools/atlas_control.py mark-stale --run <run-directory> --reason <persisted-finding>
```

Never edit `run.yaml` or `control.json`.

## 3. Finish producer work

When the frontier is empty, grade contributions and obtain one fresh cold read. Record its findings and each disposition under `## Cold-read evidence`; a scalar completion claim is insufficient. Resolve or disposition every finding. Then set `cold_read: complete` and `gate_ready: true` while leaving `status: draft`.

These are producer completion claims, not acceptance. The candidate contains no approval fields. Run the read-only mechanical boundary check:

```shell
python3 tools/atlas_control.py check --run <run-directory>
```

A `BLOCKED` report gives exhaustive mechanical gaps and exact resume points. Repair them here. A `PASS` means only that mechanics pass; route the unchanged candidate to `atlas:control-run` for configured `AGENT_REVIEW` or `HUMAN` semantic acceptance.

## Standing rules

- Decisions and evidence are the output; specification and design are downstream.
- A producer never approves its own artifact or advances state.
- A read-only judge never repairs the candidate.
- Reversals remain explicit through superseding decision records.
