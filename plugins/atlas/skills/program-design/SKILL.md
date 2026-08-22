---
name: program-design
description: Produce the Atlas Stage 4 candidate and hand it to planning control.
disable-model-invocation: true
---

# Program design

Produce the current Stage 4 candidate.

Resolve `<atlas-plugin-root>` from this installed skill before invoking a packaged tool: it is the third parent of this file (`SKILL.md` → `program-design/` → `skills/` → plugin root). Use that absolute path; never rely on the caller's working directory.

## 1. Resume frozen authority

Read immutable `run.yaml`, authoritative Stage 0 `control.json`, and `planning-control.json` before any producer action. Require current phase `program_design`, gate `PENDING`, and exact configured authority `AGENT_REVIEW` or `HUMAN`. Reject contradictory, aliased, or incomplete state rather than repairing it or falling back. Program Design never asks a participation question; Stage 4 has no participation mode.

## 2. Inspect the actual repository and bind the source

Before drafting anything, inspect every actual target repository named in effective intake at its frozen baseline: examine the current file tree, language and tooling conventions, relevant implementations, tests, and working-tree state. Base every code-shape decision on those inspected bytes rather than candidate prose or memory.

Derive the applicable branch only from effective selected stages, never from candidate prose or artifact presence. Read exactly one applicable upstream source and do not read either omitted source:

- System Design selected: read exact accepted `30-system-design.md` and bind its integer version and SHA-256 as `kind: system_design`.
- System Design omitted and Product Closure selected: read exact accepted `20-prd.md` and bind its integer version and SHA-256 as `kind: product_closure`.
- both upstream semantic boundaries omitted: read frozen effective Stage 0 `run.yaml` and its recorded effective configuration binding as `kind: stage0`.

Reject a missing, extra, stale, or mismatched source rather than inferring a branch.

If repository inspection shows that local realization requires a new or changed upstream commitment, do not draft around it. Before writing candidate or readiness bytes, return structured read-only `DESIGN_BLOCKED` and stop. Name `upstream_source`, a nonempty `upstream_issue`, source-constrained `resume_boundary`, and the smallest `resume_action`; `upstream_source` and `resume_boundary` both equal the actual selected source-binding kind, and `resume_action` states the smallest upstream decision or change required. This producer result creates no review file, does not rewrite any upstream artifact, and does not mutate planning state.

Reviewer-discovered `DESIGN_BLOCKED` belongs only in a fresh `reviews/program-design-v1.json` assembled through the internal authority adapter; it is distinct from this producer pre-readiness stop.

## 3. Produce the Stage 4 candidate

Use [`references/program-design-file.md`](references/program-design-file.md) as the exact `40-program-design.md` shape. Preserve exactly its six frontmatter fields and ten ordered sections. Ground every placement, type, signature, call, state, migration, failure-path, test-seam, and sequencing decision in the inspected repository. In `Upstream commitment realization`, cite every upstream commitment and name its codebase-local realization.

Keep Stage 4 inside the reliance horizon: resolve code shape so Stage 5 can decompose rather than design, but do not write line-by-line pseudocode, choose ticket slices, or construct a ticket graph. The final canonical candidate has integer `version: 1`, `status: draft`, and boolean `gate_ready: true`.

## 4. Preserve producer ownership

On the normal path, write only canonical `40-program-design.md` candidate/readiness bytes. The producer must never create or modify `reviews/program-design-v1.json`, never write `planning-control.json`, never rewrite an upstream artifact, and never record semantic review or acceptance. Those belong to the later internal authority adapter and deterministic controller.

## 5. Check and continue internally

Run the read-only mechanical boundary:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage program_design
```

A structured `BLOCKED` result returns all mechanical gaps to this producer. Repair only candidate-owned bytes and rerun. On any dependency/tool error, report it exactly and stop; never emulate checking or transition logic. Mechanical `PASS` is readiness only, not semantic review or acceptance.

After mechanical `PASS`, perform the exact named internal handoff to `atlas:control-planning` without asking the user to issue a second routing command. Pass the unchanged `<run-directory>` and explicit stage `program_design`; do not invoke a reviewer or consume approval in this producer.
