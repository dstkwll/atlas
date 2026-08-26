---
name: system-design
description: Produce the current Atlas System Design candidate and hand it to planning control.
disable-model-invocation: true
---

# System design

Produce the current Stage 3 candidate. The producer writes readiness, never acceptance, and does not mutate `run.yaml`, `control.json`, `planning-control.json`, upstream artifacts, or review evidence. `30-system-design.md` is always canonical; co-design additionally requires the non-authoritative `30-system-design.html` board.

Resolve `<atlas-plugin-root>` from this installed skill before invoking a packaged tool: it is the third parent of this file (`SKILL.md` → `system-design/` → `skills/` → plugin root). Use that absolute path; never rely on the caller's working directory.

## 1. Resume frozen authority

Read `run.yaml`, authoritative Stage 0 `control.json`, and `planning-control.json`. Accept exactly one branch:

- normal: status `PLANNING`, phase `system_design`, gate `PENDING`;
- D-082 repair: exact reserved tuple `BLOCKED` / `system_design` / `SYSTEM_DESIGN_STALE`, gate `STALE`, with `current_attempt.stage: system_design`.

Both branches require frozen participation `agent_led` or `co_design` and an exact supported policy: `HUMAN`, `AGENT_REVIEW`, or canonical `HUMAN_IF_CHANGED`. Any other blocked tuple or missing reservation stops unchanged.

System Design reads the frozen value and never asks again for participation. It also reads policy literally; participation stays orthogonal. The producer does not classify materiality, invoke the acceptance reviewer, assemble evidence, obtain approval, or reinterpret/fall back from policy; those belong to the internal control handoff.

## 2. Bind the one applicable source

Read selected stages and immutable `stage0_anchor`; choose exactly one `source_binding`. On the D-082 repair branch, copy the same exact source binding from `blocked_reason.superseded_system_design`; never reselect or change it. On the normal branch:

- selected Product Definition Approval: record `kind: product_closure`, `artifact: 20-prd.md`, and its exact accepted integer `version` and `sha256`;
- omitted Product Definition Approval: record `kind: stage0`, `artifact: run.yaml`, exact base `sha256`, `effective_config_hash`, and integer `effective_config_revision`.

The direct branch has no PRD field. If source bytes or the recorded binding disagree, stop without writing a candidate.

## 3. Produce the Stage 3 candidate

Use [`references/system-design-file.md`](references/system-design-file.md) as the exact shape. Frontmatter records `run`, integer `version`, `status: draft`, boolean `gate_ready`, frozen `participation`, intake `opened`, and the selected discriminated `source_binding`; preserve exactly those fields. Normal version is `1`; on the D-082 repair branch, version is the superseded acceptance version plus one. While drafting keep `gate_ready: false`.

Write from the reliance horizon: changing a Stage 3 choice requires a caller, peer, or operator to adjust or changes an accepted guarantee. **Features pay for seams:** introduce or retain a system seam only when a named accepted behavior, authority boundary, or independently changing responsibility requires it. Delete speculative seams; anticipated reuse, aesthetic symmetry, and hypothetical flexibility do not pay for one. Cover all twelve required sections. Keep file placement, language signatures, internal calls, locking mechanics, migration order, and test seams in Program Design.

### `agent_led`

Inspect the current system and applicable source, draft all sections, cold-read the candidate, and repair producer-owned gaps. Write canonical `30-system-design.md` as in Slice 1. Do not require or create HTML.

### `co_design`

Chat is the interactive control surface. Work on one system seam or decision at a time. Ask one plain question; present two or three concrete alternatives; give a recommendation and its strongest counterargument; assign the matching stable label from [`references/system-design-board.md`](references/system-design-board.md). The user may redirect or zoom in. Write each settled choice into Markdown; conversation alone is neither artifact nor approval.

Never edit canonical `30-system-design.md` directly in co-design. Stage the complete replacement at `<run>/.30-system-design.next.md`, then run:

```shell
python3 "<atlas-plugin-root>/tools/render_system_design.py" write --run "<run-directory>" --draft .30-system-design.next.md
```

`write` renders first, then installs canonical Markdown and the mandatory deterministic HTML projection. For explicit regeneration or diagnosis use only:

```shell
python3 "<atlas-plugin-root>/tools/render_system_design.py" render --run "<run-directory>"
python3 "<atlas-plugin-root>/tools/render_system_design.py" verify --run "<run-directory>"
```

Before presenting the board as a decision surface, apply the mobile projection contract in [`references/system-design-board.md`](references/system-design-board.md): exercise the real current board at phone and desktop widths, prove no page-level horizontal overflow, and visually inspect the header, one non-trivial table, and one diagram. A mechanically verified but unreadable board is not complete decision evidence. When browser rendering is unavailable, state that limitation and use a verified phone-first decision image for chat rather than claiming the HTML is mobile-ready.

The board must remain self-contained, metadata-bound, non-authoritative, and complete across every stable view. Put an explicit inapplicability reason in the matching Markdown section when a view does not apply. Do not generate decorative images or accept HTML bytes independently.

## 4. Record readiness and check mechanics

Cold-read the complete candidate against its exact source. For co-design, verify the current board. Then set `gate_ready: true` last while keeping `status: draft`, using the same co-design reserved-draft write path when applicable. Run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage system_design
```

A structured `BLOCKED` result is expected control output. Follow every resume action, repair only producer-owned candidate/projection files, and rerun. On a dependency/tool error, report it exactly and stop; never emulate checking or transition logic.

## 5. Continue the same workflow

After `PASS`, keep the exact Markdown and, for co-design, current HTML unchanged. Perform an exact named internal handoff to `atlas:control-planning` without asking the user to issue a second command. Load that exact owner under [`../../references/internal-owner-loading.md`](../../references/internal-owner-loading.md). Pass the same `<run-directory>` and stage `system_design`; do not consume approval in this producer.

## Standing rules

- The producer never approves its artifact or writes a gate outcome.
- `30-system-design.md` remains `status: draft` after acceptance; `gate_ready: true` is readiness only.
- Product Definition Approval and direct Stage 0 are exclusive source branches.
- Mechanical `PASS` never claims semantic quality or approval.
- Slice 2B leaves all classification, semantic review, evidence assembly, and authority consumption in the internal control handoff; it adds no rejection, reopen, or staleness operation.
- Nothing in conversation overrides frozen intake or deterministic planning state.
