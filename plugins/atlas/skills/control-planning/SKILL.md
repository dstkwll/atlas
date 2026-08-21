---
name: control-planning
description: Apply the current HUMAN System Design gate and record one deterministic transition.
disable-model-invocation: true
---

# Control planning

Act only as the workflow-internal authority adapter for Slice 1's current `system_design` + `HUMAN` boundary. This skill never routes, never synthesizes a candidate, never edits a candidate, and never grades prose. It mutates no file itself; only the packaged controller may replace `planning-control.json`.

Resolve `<atlas-plugin-root>` from this installed skill before invoking the packaged tool: it is the third parent of this file (`SKILL.md` → `control-planning/` → `skills/` → the plugin root) and contains `tools/atlas_planning.py`. Use that resolved absolute path; never rely on the caller's working directory.

The normal entry is the exact internal handoff from `atlas:system-design`; the user does not issue a second command. Receive the unchanged `<run-directory>` and explicit stage `system_design`. Do not discover a stage, choose a producer, or act as a generalized router.

## 1. Establish the supported branch

Read immutable `run.yaml`, Stage 0 `control.json`, and `planning-control.json`. Require current phase `system_design`, gate `PENDING`, frozen participation `agent_led`, and `run.yaml.gates.system_design.authority: HUMAN`.

If participation is `co_design`, stop and report the intentionally unimplemented Slice 2 capability. If authority is `AGENT_REVIEW` or `HUMAN_IF_CHANGED`, stop and report the intentionally unimplemented Slice 2 authority path. Do not invoke a reviewer, classify materiality, fall back to HUMAN, or reinterpret policy.

If files, fields, phase, or policy are missing or contradictory, report the exact mismatch and stop. Never repair control state, candidate bytes, source bindings, or intake.

## 2. Check the exact candidate

Run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design
```

`check` is read-only and returns structured `PASS` or `BLOCKED` with all mechanical gaps and resume actions. A `BLOCKED` result is expected control output even though the process exits nonzero: return the complete report to `atlas:system-design` for candidate repair and make no transition. Any other nonzero result is a tool/dependency failure; report its exact stderr and stop.

A `PASS` establishes mechanics only. It does not approve meaning, convert readiness into acceptance, or authorize this adapter to alter candidate prose.

## 3. Obtain HUMAN authority

After `PASS`, present the exact `30-system-design.md` candidate, its version/SHA-256 from the report, its exact source binding, and the current boundary. Ask for explicit human approval of this exact candidate. Approval from prior conversation, co-design participation, `gate_ready: true`, silence, or an agent opinion is not explicit human approval.

If the human does not approve, leave the gate `PENDING`, report that no transition occurred, and return to the producer. Slice 1 has no reject command or terminal-rejection path.

Record the canonical current date as `<YYYY-MM-DD>` only after approval. Do not change the candidate between presentation and transition.

## 4. Record one transition

After explicit approval, the adapter calls `advance` exactly once:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --approval human --date "<YYYY-MM-DD>"
```

The controller holds `.atlas-planning.lock`, revalidates frozen Stage 0 and planning state, mechanically checks the candidate, re-reads candidate/source bytes, and atomically replaces only `planning-control.json`. It records HUMAN acceptance with null review references and empty repository baselines, then advances to the next selected downstream boundary.

On a nonzero result, report the exact error and never claim progression from an intended command. Do not retry `advance`; rerun the producer/check workflow after the reported mismatch is resolved.

## 5. Verify and report

On success, re-read `planning-control.json` and verify revision incremented once, `gates.system_design` is `HUMAN_APPROVED`, its acceptance matches the exact candidate/source bindings, and phase is the next selected boundary. Also verify `run.yaml`, `control.json`, and `30-system-design.md` were not changed by the adapter.

Report the command's exact result and verified phase. Do not invoke Program Design, ticket compilation, execution, publication, or any later-stage owner in Slice 1.

## Standing rules

- One adapter invocation records at most one transition.
- The adapter launches no later producer and selects no next workflow action.
- Human approval applies only to the exact candidate just presented.
- Policy labels are consumed literally and are never mapped to a fallback authority.
- HUMAN is the only supported Slice 1 authority.
- No reviewer envelope or packaged review reference exists in this slice.
- No copies, receipts, history, events, journal, reject, reopen, stale, or renderer behavior exists.
- `planning-control.json` is the only mutable Stage 3–5 authority, and this slice changes only its System Design outcome.
