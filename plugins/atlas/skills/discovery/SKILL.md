---
name: discovery
description: Maintain the decision log and living PRD until discovery earns product closure.
disable-model-invocation: true
---

# Discovery

Resolve a fuzzy goal into durable decisions and a living product contract. Discovery owns both `<run>/10-decisions.md` and `<run>/20-prd.md`; it never claims product closure itself.

Resolve `<atlas-plugin-root>` from this installed skill before invoking tools: it is the third parent of this file (`SKILL.md` → `discovery/` → `skills/` → the plugin root) and must contain `tools/render_prd.py` and `tools/atlas_control.py`. Use that resolved absolute path; never assume the caller's working directory.

## 1. Resume authoritative state

Read immutable `run.yaml`, authoritative `control.json`, and accepted `amendments/NNN-*.md`. Ignore `00-state.md` for legality. Discovery must be the current phase and the PRD candidate's `effective_config_revision` must match control.

Create or resume the exact files in [`references/run-layout.md`](references/run-layout.md): append-only provenance in [`references/decision-record.md`](references/decision-record.md) and the living PRD in [`references/prd-file.md`](references/prd-file.md). Version stays the same after a `BLOCKED` review because no acceptance was recorded.

## 2. Resolve the frontier

The **frontier** is every open question whose prerequisites are already settled: the questions answerable now without guessing at answers not yet found. Persist the entire frontier before asking anything.

Start a new run with two challenges:

- **The problem test.** Name the problem in the words of whoever has it. State what happens if nothing is built and whether a better framing dissolves the problem or moves it elsewhere.
- **The announcement test.** Write three to six sentences announcing the finished thing to its users. If no coherent announcement can be written, challenge the candidate rather than inventing requirements around it.

Propose candidate shapes for the work and derive the first questions from their forks. Candidate shapes stay at approach, boundary, and behavior level until a decision settles them. File names, function signatures, and schemas are later stages; introducing them here makes an unsettled design look decided.

Route each frontier question by where its answer lives:

| Route | Answer owner | Action |
|---|---|---|
| **grill** | the user | Ask about preference, priority, taste, or risk appetite. |
| **research** | the outside world | Dispatch factual research against primary sources. |
| **explore** | the existing codebase | Inspect the repository; never ask the user to supply discoverable facts. |
| **spike** | nowhere yet | Run a bounded experiment and persist its findings. |

Only **grill** questions go to the user. Work in rounds: ask every currently unblocked grill question together, with concrete options, a recommendation, and its strongest counterargument; dispatch the research, explore, and spike routes in parallel. If evidence does not support a real recommendation, say so and ask for the user's instinct first—never manufacture a recommendation. A question blocked by another stays in the recorded frontier. When answers land, append each settled decision immediately using [`references/decision-record.md`](references/decision-record.md), update what it unblocked, recompute the frontier, and start the next round.

When research, exploration, or a spike settles a decision, cite the evidence that resolved it in the decision's reasoning; a spike also names its findings file. A route label without a source is not evidence.

After each decision, apply its surviving normative consequences to the living PRD before moving on. Never edit canonical `20-prd.md` directly: write the complete proposed bytes to `<run>/.20-prd.next.md`, then run `python3 "<atlas-plugin-root>/tools/render_prd.py" write --run "<run-directory>" --draft .20-prd.next.md`. That single path renders before replacement and stops loudly on failure; the closure check catches any interrupted Markdown/HTML mismatch. Keep rationale, alternatives, confidence, and reversals in `10-decisions.md`; keep only the surviving normative product contract in the PRD.

If repository identity or baseline evidence contradicts intake, stop the normal path and follow [`../../references/intake-correction.md`](../../references/intake-correction.md). Never edit `run.yaml` or `control.json`.

## 3. Finish producer work

When the frontier is empty, discovery is still not done. Run this end sequence in order:

1. Grade contributions and ensure live/superseded decision fields are coherent.
2. Rebuild the whole `## PRD alignment retrospective` table in `10-decisions.md`.
3. Read the whole PRD cold and reconcile it against the live decisions.
4. Obtain one fresh producer cold read. Give the fresh reader only `10-decisions.md`, not a summary or conclusions, and ask whether any decision opens an unaddressed consequence or is unsupported by its own reasoning or evidence. The reader reports findings and never repairs the artifact; record every finding plus its disposition under `10-decisions.md#Cold-read evidence`.
5. Prepare the final `.20-prd.next.md`: reconcile the body, bind `derived_from` to the exact current `10-decisions.md` version/hash, set `cold_read: complete`, and set `gate_ready: true` last while leaving `status: draft`.
6. Install the final Markdown and HTML through the canonical writer:

   ```shell
   python3 "<atlas-plugin-root>/tools/render_prd.py" write --run "<run-directory>" --draft .20-prd.next.md
   ```

These are producer completion claims, not acceptance. The candidate contains no approval fields. Run the read-only mechanical boundary check:

```shell
python3 "<atlas-plugin-root>/tools/atlas_control.py" check --run "<run-directory>"
```

A `BLOCKED` report gives exhaustive mechanical gaps and exact resume points. Repair them here. Any repair after a blocked semantic review first uses the canonical writer to install a draft with `gate_ready: false`, then reruns the whole end sequence above and asks for a fresh review. No direct PRD mutation is legal. A `PASS` means only that mechanics pass; route the unchanged candidate to `atlas:control-run` for configured `AGENT_REVIEW` or `HUMAN` semantic acceptance.

## Standing rules

- **Nothing important exists only in the conversation.** At every round boundary, `10-decisions.md` contains every settled decision and the complete open frontier so a fresh session can resume without chat history.
- Discovery owns the decision log, the PRD, and the retrospective; design stays downstream.
- A producer never approves its own artifact or advances state.
- A read-only judge never repairs the candidate.
- Reversals remain explicit through superseding decision records.
