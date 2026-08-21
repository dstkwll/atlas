---
name: control-planning
description: Apply the current HUMAN System Design gate and record one deterministic transition.
disable-model-invocation: true
---

# Control planning

Act only as the workflow-internal authority adapter for the current `system_design` + `HUMAN` boundary. This skill never routes, never synthesizes a candidate, never edits a candidate, and never grades prose. It mutates no file itself; only the packaged controller may replace `planning-control.json`.

Resolve `<atlas-plugin-root>` from this installed skill before invoking a packaged tool: it is the third parent of this file (`SKILL.md` → `control-planning/` → `skills/` → plugin root). Use that absolute path; never rely on the caller's working directory.

The normal entry is the exact internal handoff from `atlas:system-design`; the user does not issue a second command. Receive the unchanged `<run-directory>` and explicit stage `system_design`. Do not discover a stage, choose a producer, or become a generalized router.

## 1. Establish the supported branch

Read immutable `run.yaml`, Stage 0 `control.json`, and `planning-control.json`. Require current phase `system_design`, gate `PENDING`, frozen participation `agent_led` or `co_design`, and `run.yaml.gates.system_design.authority: HUMAN`.

Participation changes collaboration only. Do not re-ask it. If authority is `AGENT_REVIEW` or `HUMAN_IF_CHANGED`, stop and report the intentionally unimplemented Slice 2B path. Do not invoke a reviewer/classifier, fall back to HUMAN, or create an envelope.

If files, fields, phase, policy, or frozen participation contradict one another, report the exact mismatch and stop. Never repair state, candidate bytes, board bytes, source bindings, or intake.

## 2. Check the exact candidate

Run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design
```

`check` is read-only and returns structured `PASS` or `BLOCKED` with all mechanical gaps and resume actions. For `co_design`, PASS requires current `30-system-design.html` metadata and every stable view; for `agent_led`, Slice 1 behavior remains unchanged and HTML is not required.

A `BLOCKED` result is expected control output even though the process exits nonzero: return the complete report to `atlas:system-design` and make no transition. Any other nonzero result is a dependency/tool failure; report exact stderr and stop. A PASS establishes mechanics only, not approval.

## 3. Obtain HUMAN authority

After `PASS`, present the exact canonical `30-system-design.md`, its version/SHA-256 from the report, its exact source binding, and the current boundary. When participation is `co_design`, also identify the current HTML as a non-authoritative projection; do not ask the human to approve an independent HTML hash.

Ask for explicit human approval of this exact Markdown candidate. Never treat conversational agreement as approval. Prior chat choices, co-design participation, `gate_ready: true`, the visual board, silence, or an agent opinion do not grant authority.

If the human does not approve, leave the gate `PENDING`, report no transition, and return to the producer. Slice 2A has no reject command. Record canonical `<YYYY-MM-DD>` only after approval. Do not change the candidate or board between presentation and transition.

## 4. Record one transition

After explicit approval, the adapter calls `advance` exactly once:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --approval human --date "<YYYY-MM-DD>"
```

The controller holds `.atlas-planning.lock`, revalidates frozen Stage 0 and planning state, reruns the mechanical check, re-reads candidate/source bytes at the write boundary, and atomically replaces only `planning-control.json`. It records HUMAN acceptance of Markdown with null review references and empty repository baselines. HTML remains non-authoritative and receives no acceptance field or hash.

On nonzero output, report the exact error and never claim progression from an intended command. Do not retry `advance`; rerun producer/check after the mismatch is resolved.

## 5. Verify and report

On success, re-read `planning-control.json` and verify revision incremented once, `gates.system_design` is `HUMAN_APPROVED`, acceptance matches the exact Markdown/source bindings, and phase is the next selected boundary. Verify `run.yaml`, `control.json`, `30-system-design.md`, and any `30-system-design.html` were unchanged by the adapter.

Report the command's exact result and verified phase. Do not invoke Program Design, ticket compilation, execution, publication, or any later-stage owner in Slice 2A.

## Standing rules

- One adapter invocation records at most one transition and launches no later producer.
- Human approval applies only to the exact Markdown candidate presented.
- Frozen participation selects collaboration mechanics, never gate authority.
- Board freshness is a mechanical precondition, never a second approval.
- Policy labels are literal; HUMAN is the only supported Slice 2A authority.
- No review/classification envelope, copy, receipt, history, event, journal, reject, reopen, or stale operation exists.
- `planning-control.json` remains the only mutable Stage 3–5 authority; this slice changes only its System Design outcome.
- Static contracts do not prove installed-host skill chaining; Slice 5 owns that proof.
