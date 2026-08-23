---
name: control-planning
description: Apply frozen System or Program Design authority and record one deterministic transition.
disable-model-invocation: true
---

# Control planning

Act only as the workflow-internal authority adapter. It supports exactly the explicit stages `system_design` and `program_design`; it never discovers, infers, or reroutes a stage. This skill never routes, never synthesizes a candidate, never edits a candidate, and never grades prose. It may assemble one evidence envelope; only the packaged controller may replace `planning-control.json`.

Resolve `<atlas-plugin-root>` from this installed skill before invoking a packaged tool: it is the third parent of this file (`SKILL.md` → `control-planning/` → `skills/` → plugin root). Use that absolute path; never rely on the caller's working directory.

The normal entry is the exact internal handoff from `atlas:system-design` or `atlas:program-design`; the user does not issue a second command. Receive the unchanged `<run-directory>` and explicit stage `system_design` or `program_design`. Reject every other value. Do not discover a stage, choose a producer, or become a generalized router.

## 1. Establish the supported branch

Read immutable `run.yaml`, Stage 0 `control.json`, and `planning-control.json`. Accept normal status `PLANNING` when the explicit stage equals current phase with gate `PENDING`. Also accept one reserved `BLOCKED` repair tuple: `system_design` / gate `STALE` / `SYSTEM_DESIGN_STALE` / matching System attempt, or `program_design` / gate `PENDING` / `PROGRAM_DESIGN_RESUMED` / matching Program attempt. Every other blocked tuple or missing reservation stops unchanged.

For `system_design`, require frozen participation `agent_led` or `co_design` and one exact System Design policy: `HUMAN`, `AGENT_REVIEW`, or canonical `HUMAN_IF_CHANGED` with the seven dimensions in [`references/system-design-authority.md`](references/system-design-authority.md). Participation changes collaboration only. Do not re-ask it or use it to choose authority.

For `program_design`, require the configured `AGENT_REVIEW` or `HUMAN` authority exactly as defined in [`references/program-design-authority.md`](references/program-design-authority.md). Program Design has no participation, `AUTO`, or `HUMAN_IF_CHANGED` branch. If any frozen policy is incomplete, aliased, or contradictory, stop; no configured path falls back to another.

If files, fields, phase, policy, or frozen participation contradict one another, report the exact mismatch and stop. Never repair state, candidate bytes, board bytes, source bindings, or intake.

## 2. Check the exact candidate

Run exactly one mechanical check selected by the explicit stage; never run both commands.

For explicit stage `system_design`, run only:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design
```

For explicit stage `program_design`, run only:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage program_design
```

`check` is read-only and returns structured `PASS` or `BLOCKED` with all mechanical gaps and resume actions. For `co_design`, PASS requires current `30-system-design.html` metadata and every stable view; for `agent_led`, Slice 1 behavior remains unchanged and HTML is not required.

A `BLOCKED` result is expected control output even though the process exits nonzero: return the complete report to the named producer and make no transition. For Program Design, producer-discovered `DESIGN_BLOCKED` never enters this adapter; reviewer-discovered `DESIGN_BLOCKED` belongs only in fresh `reviews/program-design-v1.json` and also makes no transition or planning-state mutation. Any other nonzero result is a dependency/tool failure; report exact stderr and stop. A PASS establishes mechanics only, not approval.

For explicit stage `program_design`, after candidate mechanics pass and before invoking a reviewer or writing evidence, run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_repository.py" verify --run "<run-directory>"
python3 "<atlas-plugin-root>/tools/atlas_repository.py" list --run "<run-directory>" --repository "<stable-repository-id>"
python3 "<atlas-plugin-root>/tools/atlas_repository.py" search --run "<run-directory>" --repository "<stable-repository-id>" --needle "<literal>"
python3 "<atlas-plugin-root>/tools/atlas_repository.py" read --run "<run-directory>" --repository "<stable-repository-id>" --path "<baseline-path>"
```

Run `verify` first. On failure, return its complete mechanical repository `BLOCKED` report before invoking a reviewer or writing evidence; do not run `list`, `search`, or `read`. On PASS, proceed to exact baseline inspection. The fresh reviewer reads the exact baseline only through the adapter commands above, repeating `list`, `search`, and `read` as needed. Current `HEAD`, index, and working-tree bytes are never substitute review inputs.

Adapter `config_path`, bound `source`, Git-directory, and absolute diagnostic paths are ephemeral operational evidence. Never copy them into `reviews/program-design-v1.json`. Reviewer evidence names only stable repository identity, full baseline OID, baseline-relative repository paths, and relevant code evidence.

## 3. Resolve the frozen authority

Follow the exact schema, dimensions, fail-closed mapping, reviewer output, and authority matrix in [`references/system-design-authority.md`](references/system-design-authority.md). Evidence lives only at `reviews/system-design-v1.json`; the invoker assembles its exact duplicate-safe JSON bytes. The envelope carries the exact ordered current effective repository/baseline pairs after accepted Stage 0 amendments and the current candidate identity/hash. It is evidence, not authority.

- `HUMAN`: do not invoke a reviewer or create an envelope. Present the exact canonical Markdown, version/SHA-256, source binding, and boundary; obtain explicit human approval.
- `AGENT_REVIEW`: invoke one fresh read-only semantic reviewer using the seven Stage 3 dimensions. It reads mechanics, source/baselines, then the exact candidate; it edits no candidate, state, evidence, or repository and grants no authority. Assemble materiality null plus its exact semantic result.
- `HUMAN_IF_CHANGED`: first invoke a fresh read-only classifier against the exact repository/current-system baselines and candidate. The classifier edits nothing and grants no authority. Persist per-dimension evidence. Any material/unavailable result maps to `HUMAN`; seven exact `NOT_MATERIAL` rows map to `AGENT_REVIEW`. Classifier failure or schema defects are persisted with a nonempty `unavailable_reason` and route `HUMAN`; unexplained bad output stops.
- When classification maps to `AGENT_REVIEW`, invoke a distinct fresh semantic reviewer after classification and assemble its result. When it maps to `HUMAN`, set semantic review null and obtain explicit approval. Reviewer `BLOCKED` returns every gap to the producer and never mutates state.

For the D-082 System replacement only, every policy uses a fresh review envelope with the controller-required `repair_context`: episode start revision, complete superseded System acceptance, contradiction review reference/hash and finding, attempts used, and expected acceptance revision. Direct `HUMAN` repair sets materiality and semantic review null, then requires both that fresh review envelope and explicit human approval; normal direct `HUMAN` remains review-free. Agent-review and mapped branches retain their normal judgments plus the same `repair_context`.

Freshness, role identity, and read order are procedural and honestly unauthenticated by the controller. Before any human System Design decision, present the exact canonical `30-system-design.md`, version/SHA-256, source binding, and classification evidence. Never treat conversational agreement as approval; chat choices, co-design, `gate_ready`, board, silence, classifier, or reviewer grant no human authority. If approval is declined, leave `PENDING`; no reject command exists. Do not change candidate, board, state, repository, or evidence after the final read.

## Program Design branch

Follow the exact reviewer output, `DESIGN_BLOCKED` semantics, and authority matrix in [`references/program-design-authority.md`](references/program-design-authority.md); do not duplicate or reinterpret its full schema here. Evidence lives only at `reviews/program-design-v1.json`, and the invoker assembles its exact duplicate-safe JSON bytes. Invoke one distinct fresh read-only semantic reviewer after mechanical PASS. Both configured `AGENT_REVIEW` and `HUMAN` require a fresh exact PASS review bound to the current candidate, repository baselines, and exactly one applicable source. `BLOCKED` returns local gaps to the producer. `DESIGN_BLOCKED` follows [`../../references/program-design-blocked.md`](../../references/program-design-blocked.md) and returns the exact upstream issue without state mutation; HUMAN has no exception. Only after PASS may HUMAN obtain explicit human approval for that exact reviewed candidate. The reviewer and human edit no candidate, source, repository, evidence, or state.

## 4. Record one transition

After evidence/approval is complete, the adapter calls `advance` exactly once using the matching frozen branch:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --approval human --date "<YYYY-MM-DD>"
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --date "<YYYY-MM-DD>"
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage system_design --review reviews/system-design-v1.json --approval human --date "<YYYY-MM-DD>"
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage program_design --review reviews/program-design-v1.json --date "<YYYY-MM-DD>"
python3 "<atlas-plugin-root>/tools/atlas_planning.py" advance --run "<run-directory>" --stage program_design --review reviews/program-design-v1.json --approval human --date "<YYYY-MM-DD>"
```

The first three commands are the exact System Design matrix: direct `HUMAN`, direct/mapped `AGENT_REVIEW`, and mapped `HUMAN`. The final two are Program Design `AGENT_REVIEW` and reviewed `HUMAN`. Select exactly one command from the explicit stage and configured branch; the adapter calls `advance` exactly once. The controller enforces each matrix. It holds `.atlas-planning.lock`, revalidates policy/planning/Stage 0, reruns mechanics, and re-reads candidate/source/envelope at the final write boundary before atomically replacing only `planning-control.json`. Acceptance stores only the envelope reference/hash when evidence is required; System Design HTML remains non-authoritative.

On nonzero output, report the exact error and never claim progression from an intended command. Do not retry `advance`; rerun producer/check after the mismatch is resolved.

## 5. Verify and report

On success, re-read `planning-control.json` and verify revision incremented once, the gate is `HUMAN_APPROVED` or `AGENT_APPROVED` exactly as derived, acceptance matches Markdown/source/authority/evidence bindings, and phase is the next selected boundary. Verify candidate, board, run/control, and evidence bytes were unchanged by transition.

Report the command's exact result and verified phase. After accepted Program Design, verify phase `tickets` and stop loudly: no first-party ticket producer exists. Do not invoke ticket compilation, execution, publication, or any later-stage owner.

## Standing rules

- One adapter invocation records at most one transition and launches no later producer.
- Human approval applies only to the exact Markdown candidate/hash/source presented.
- Frozen participation selects collaboration mechanics, never gate authority.
- Board freshness is a mechanical precondition, never a second approval.
- Policy labels, filename, schemas, and seven dimension identifiers are literal.
- No copy, receipt, history, event, journal, rejection, reopen, staleness, or model-router operation exists.
- System Design retains its Slice 2B classifier/reviewer and direct-HUMAN behavior unchanged.
- `planning-control.json` remains the only mutable Stage 3–5 authority; this adapter changes only the one explicit System Design or Program Design outcome.
- Human attention is an authority surface, not an orchestration mechanism. The user supplies judgment when policy requires it; Atlas supplies the internal handoff and must not require a second manual command.
