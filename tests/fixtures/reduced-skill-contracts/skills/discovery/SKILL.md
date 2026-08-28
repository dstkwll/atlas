---
name: discovery
description: Maintain the decision log and living PRD until discovery earns Product Definition Approval.
disable-model-invocation: true
---

# Discovery

Resolve a fuzzy goal into durable decisions and a living product contract. Discovery owns both `<run>/10-decisions.md` and `<run>/20-prd.md`; it never claims Product Definition Approval itself.

## 1. Resume authoritative state

Read immutable `run.yaml`, authoritative `control.json`, and accepted `amendments/NNN-*.md`. Ignore `00-state.md` for legality. Discovery must be the current phase and the PRD candidate's `effective_config_revision` must match control.

Create or resume the exact files in [`references/run-layout.md`](references/run-layout.md): append-only provenance in [`references/decision-record.md`](references/decision-record.md) and the living PRD in [`references/prd-file.md`](references/prd-file.md). Version stays the same after a `BLOCKED` review because no acceptance was recorded.

## 2. Resolve the frontier

Record the problem/announcement tests. Ask user-owned preferences; investigate facts through research, repository exploration, or a spike. Persist the entire open frontier before asking.

Append each settled decision immediately using [`references/decision-record.md`](references/decision-record.md), then apply its surviving normative consequences before moving on. Never edit canonical `20-prd.md` directly: write the complete proposed bytes to `<run>/.20-prd.next.md`, then run `python3 tools/render_prd.py write --run <run-directory> --draft .20-prd.next.md`. That single path renders before replacement and stops loudly on failure; the closure check catches any interrupted Markdown/HTML mismatch. Keep rationale, alternatives, confidence, and reversals in `10-decisions.md`; keep only the surviving normative product contract in the PRD.

If repository identity or baseline evidence contradicts intake, stop the normal path and follow [`../../references/intake-correction.md`](../../references/intake-correction.md). Never edit `run.yaml` or `control.json`.

## 3. Finish producer work

When the frontier is empty, discovery is still not done. Run this end sequence in order:

1. Grade contributions and ensure live/superseded decision fields are coherent.
2. Rebuild the whole `## PRD alignment retrospective` table in `10-decisions.md`.
3. Read the whole PRD cold and reconcile it against the live decisions.
4. Obtain one fresh cold read and record every finding plus its disposition under `10-decisions.md#Cold-read evidence`.
5. Prepare the final `.20-prd.next.md`: reconcile the body, bind `derived_from` to the exact current `10-decisions.md` version/hash, set `cold_read: complete`, and set `gate_ready: true` last while leaving `status: draft`.
6. Install the final Markdown and HTML through the canonical writer:

   ```shell
   python3 tools/render_prd.py write --run <run-directory> --draft .20-prd.next.md
   ```

These are producer completion claims, not acceptance. The candidate contains no approval fields. Run the read-only mechanical boundary check:

```shell
python3 tools/atlas_control.py check --run <run-directory>
```

A `BLOCKED` report gives exhaustive mechanical gaps and exact resume points. Repair them here. Any repair after a blocked semantic review first uses the canonical writer to install a draft with `gate_ready: false`, then reruns the whole end sequence above and asks for a fresh review. No direct PRD mutation is legal. A `PASS` means only that mechanics pass; route the unchanged candidate to `atlas:control-run` for configured `AGENT_REVIEW` or `HUMAN` semantic acceptance.

## Standing rules

- Discovery owns the decision log, the PRD, and the retrospective; design stays downstream.
- A producer never approves its own artifact or advances state.
- A read-only judge never repairs the candidate.
- Reversals remain explicit through superseding decision records.
