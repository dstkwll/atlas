---
name: control-planning
description: Apply the frozen System Design authority and record one deterministic transition.
disable-model-invocation: true
---

# Control planning

Act only as the workflow-internal authority adapter for the current `system_design` boundary. This skill never routes, never synthesizes a candidate, never edits a candidate, and never grades prose. It may assemble the one evidence envelope; only the packaged controller may replace `planning-control.json`.

Resolve `<atlas-plugin-root>` from this installed skill before invoking a packaged tool: it is the third parent of this file (`SKILL.md` → `control-planning/` → `skills/` → plugin root). Use that absolute path; never rely on the caller's working directory.

The normal entry is the exact internal handoff from `atlas:system-design`; the user does not issue a second command. Receive the unchanged `<run-directory>` and explicit stage `system_design`. Do not discover a stage, choose a producer, or become a generalized router.

## 1. Establish the supported branch

Read immutable `run.yaml`, Stage 0 `control.json`, and `planning-control.json`. Require current phase `system_design`, gate `PENDING`, frozen participation `agent_led` or `co_design`, and one exact System Design policy: `HUMAN`, `AGENT_REVIEW`, or the canonical `HUMAN_IF_CHANGED` policy with the seven dimensions in [`references/system-design-authority.md`](references/system-design-authority.md).

Participation changes collaboration only. Do not re-ask it or use it to choose authority. If the frozen policy is incomplete, aliased, or contradictory, stop. No configured path falls back to another.

If files, fields, phase, policy, or frozen participation contradict one another, report the exact mismatch and stop. Never repair state, candidate bytes, board bytes, source bindings, or intake.

## 2. Check the exact candidate

Run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design
```

`check` is read-only and returns structured `PASS` or `BLOCKED` with all mechanical gaps and resume actions. For `co_design`, PASS requires current `30-system-design.html` metadata and every stable view; for `agent_led`, Slice 1 behavior remains unchanged and HTML is not required.

A `BLOCKED` result is expected control output even though the process exits nonzero: return the complete report to `atlas:system-design` and make no transition. Any other nonzero result is a dependency/tool failure; report exact stderr and stop. A PASS establishes mechanics only, not approval.

## 3. Resolve the frozen authority

Follow the exact schema, dimensions, fail-closed mapping, reviewer output, and authority matrix in [`references/system-design-authority.md`](references/system-design-authority.md). Evidence lives only at `reviews/system-design-v1.json`; the invoker assembles its exact duplicate-safe JSON bytes. The envelope carries the exact ordered current effective repository/baseline pairs after accepted Stage 0 amendments and the current candidate identity/hash. It is evidence, not authority.

- `HUMAN`: do not invoke a reviewer or create an envelope. Present the exact canonical Markdown, version/SHA-256, source binding, and boundary; obtain explicit human approval.
- `AGENT_REVIEW`: invoke one fresh read-only semantic reviewer using the seven Stage 3 dimensions. It reads mechanics, source/baselines, then the exact candidate; it edits no candidate, state, evidence, or repository and grants no authority. Assemble materiality null plus its exact semantic result.
- `HUMAN_IF_CHANGED`: first invoke a fresh read-only classifier against the exact repository/current-system baselines and candidate. The classifier edits nothing and grants no authority. Persist per-dimension evidence. Any material/unavailable result maps to `HUMAN`; seven exact `NOT_MATERIAL` rows map to `AGENT_REVIEW`. Classifier failure or schema defects are persisted with a nonempty `unavailable_reason` and route `HUMAN`; unexplained bad output stops.
- When classification maps to `AGENT_REVIEW`, invoke a distinct fresh semantic reviewer after classification and assemble its result. When it maps to `HUMAN`, set semantic review null and obtain explicit approval. Reviewer `BLOCKED` returns every gap to the producer and never mutates state.

Freshness, role identity, and read order are procedural and honestly unauthenticated by the controller. Before any human decision, present the exact canonical `30-system-design.md`, version/SHA-256, source binding, and classification evidence. Never treat conversational agreement as approval; chat choices, co-design, `gate_ready`, board, silence, classifier, or reviewer grant no human authority. If approval is declined, leave `PENDING`; no reject command exists. Do not change candidate, board, state, repository, or evidence after the final read.

## 4. Record one transition

After evidence/approval is complete, the adapter calls `advance` exactly once using the matching frozen branch:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --approval human --date "<YYYY-MM-DD>"
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --date "<YYYY-MM-DD>"
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --approval human --date "<YYYY-MM-DD>"
```

The first command is direct `HUMAN`; the second is direct/mapped `AGENT_REVIEW`; the third is mapped `HUMAN`. The controller enforces the matrix. It holds `.atlas-planning.lock`, revalidates policy/planning/Stage 0, reruns mechanics, and re-reads candidate/source/envelope at the final write boundary before atomically replacing only `planning-control.json`. Acceptance stores only the envelope reference/hash when evidence is required; HTML remains non-authoritative.

On nonzero output, report the exact error and never claim progression from an intended command. Do not retry `advance`; rerun producer/check after the mismatch is resolved.

## 5. Verify and report

On success, re-read `planning-control.json` and verify revision incremented once, the gate is `HUMAN_APPROVED` or `AGENT_APPROVED` exactly as derived, acceptance matches Markdown/source/authority/evidence bindings, and phase is the next selected boundary. Verify candidate, board, run/control, and evidence bytes were unchanged by transition.

Report the command's exact result and verified phase. Do not invoke Program Design, ticket compilation, execution, publication, or any later-stage owner in Slice 2B.

## Standing rules

- One adapter invocation records at most one transition and launches no later producer.
- Human approval applies only to the exact Markdown candidate/hash/source presented.
- Frozen participation selects collaboration mechanics, never gate authority.
- Board freshness is a mechanical precondition, never a second approval.
- Policy labels, filename, schemas, and seven dimension identifiers are literal.
- No copy, receipt, history, event, journal, rejection, reopen, staleness, or model-router operation exists.
- `planning-control.json` remains the only mutable Stage 3–5 authority; this slice changes only its System Design outcome.
- Human attention is an authority surface, not an orchestration mechanism. The user supplies judgment when policy requires it; Atlas supplies the internal handoff and must not require a second manual command.
