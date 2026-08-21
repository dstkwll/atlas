---
name: system-design
description: Produce the current Atlas System Design candidate and hand it to planning control.
disable-model-invocation: true
---

# System design

Produce only `<run>/30-system-design.md` for the current Stage 3 boundary. The producer writes readiness, never acceptance, and does not mutate `run.yaml`, `control.json`, `planning-control.json`, upstream artifacts, or review evidence.

Resolve `<atlas-plugin-root>` from this installed skill before invoking the packaged tool: it is the third parent of this file (`SKILL.md` → `system-design/` → `skills/` → the plugin root) and contains `tools/atlas_planning.py`. Use that resolved absolute path; never rely on the caller's working directory.

## 1. Resume frozen authority

Read `run.yaml`, authoritative Stage 0 `control.json`, and `planning-control.json`. Require all of the following before authoring:

- `planning-control.json.phase` is `system_design` and its gate is `PENDING`;
- the selected `system_design_participation` is `agent_led`;
- `run.yaml.gates.system_design.authority` is exactly `HUMAN`.

System Design reads the frozen value and never asks again for participation. If participation is `co_design`, stop and report that co-design is an intentionally unimplemented Slice 2 capability. If authority is `AGENT_REVIEW` or `HUMAN_IF_CHANGED`, stop and report that the authority path is an intentionally unimplemented Slice 2 capability. Do not reinterpret either case or improvise a substitute.

## 2. Bind the one applicable source

Read the selected stages and the immutable `stage0_anchor` in planning control. Choose exactly one source branch:

- selected Product Closure: bind `source_binding` to `kind: product_closure`, `artifact: 20-prd.md`, and the exact accepted version/SHA-256 in `stage0_anchor.product_closure`;
- omitted Product Closure: bind `source_binding` to `kind: stage0`, `artifact: run.yaml`, the exact `base_run_sha256` as `sha256`, and the exact `effective_config_hash` and `effective_config_revision`.

The direct branch carries no PRD field and does not create, require, or infer a PRD. If any source bytes or recorded binding disagree, stop without writing a candidate.

## 3. Produce the Stage 3 candidate

Use [`references/system-design-file.md`](references/system-design-file.md) as the exact shape. Frontmatter records `run`, integer `version: 1`, `status: draft`, boolean `gate_ready`, frozen `participation: agent_led`, intake `opened`, and the selected discriminated `source_binding`. Preserve those exact fields and no others.

Write from the reliance horizon: a choice belongs here when changing it requires a caller, peer, or operator to adjust or changes an accepted guarantee. Cover the current and proposed system; responsibilities and seams; authoritative ownership; cross-module and external contracts; schema/protocol; lifecycle/data flow; failure/recovery; compatibility; trust/security/operations; rejected alternatives; and open decisions.

Keep codebase-local realization downstream. File placement, language signatures, internal call graphs, locking mechanics, migration implementation order, and test seams belong to Program Design. Record system invariants without inventing their local realization.

While drafting, keep `status: draft` and `gate_ready: false`. Inspect the relevant current system and upstream source rather than filling placeholders from inference. Existing candidate bytes may be resumed only when their run, version, participation, and source binding match this run exactly.

## 4. Record readiness and check mechanics

Cold-read the complete candidate against the exact source and the twelve required section identities. Resolve every producer-owned gap, then set `gate_ready: true` last while keeping `status: draft`. This flag is necessary but is not acceptance.

Run the read-only check:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design
```

A structured `BLOCKED` result is an expected check outcome. Follow every reported resume action, repair only the candidate, and rerun the same check. On any tool/dependency error, report the exact error and stop; never emulate checking or transition logic in prose.

## 5. Continue the same workflow

After `PASS`, keep the exact candidate unchanged and perform an exact named internal handoff to `atlas:control-planning` without asking the user to issue a second command. Pass the same `<run-directory>` and stage `system_design`; do not ask for a new invocation, choose another controller, or consume approval in this producer.

## Completion bar

The handoff is ready only when the read-only report is `PASS`, its candidate version/hash equal the bytes still on disk, and its one source binding equals the selected-path anchor. Any other outcome remains producer work and records no authority change.

## Standing rules

- The producer never approves its own artifact or writes a gate outcome.
- `30-system-design.md` remains canonical and at `status: draft` after acceptance.
- `gate_ready: true` is readiness evidence only.
- Slice 1 has no renderer, HTML board, semantic reviewer, rejection, reopen, or staleness operation.
- Product Closure and direct Stage 0 are exclusive source branches.
- Mechanical `PASS` never claims semantic quality or approval.
- Nothing in conversation overrides frozen intake or deterministic planning state.
