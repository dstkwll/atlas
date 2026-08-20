# atlas plugin

First-party Stage 0–2 skills implementing the Atlas architecture. `architecture/` remains authoritative; report conflicts rather than silently reconciling them. The neighboring `incubator` plugin is not part of this workflow and intentionally retains its own independent example transition material.

## Implemented flow

```text
start-run freezes run.yaml and initializes control.json
  → discovery continuously maintains 10-decisions.md and 20-prd.md
  → discovery renders 20-prd.html
  → read-only check
  → configured AGENT_REVIEW or HUMAN authority
  → controller records one transition
  → controller stops at the next selected stage
```

| Skill | Responsibility |
|---|---|
| `setup-atlas` | Configure the planning root. |
| `start-run` | Accept immutable Stage 0 `run.yaml`; initialize control. |
| `discovery` | Maintain decisions, the living PRD, and closure preparation. |
| `spike` | Produce bounded discovery evidence. |
| `control-run` | Run the read-only product-closure check, consume authority, and invoke one deterministic transition. |

Invoke explicitly as `atlas:<skill>`.

## Planning authority

Feature-root `control.json` is the only authoritative mutable Stage 0–2 state. Its mutable gate map contains the discovery product-closure boundary only when selected; otherwise `phase` starts at the first selected downstream stage with no mutable gate. Immutable `run.yaml` retains later-stage and conditional policy. After discovery acceptance, `phase` may name the next selected stage, where this controller likewise fails closed and hands off without creating later-stage gate state. `00-state.md` is a generated projection and is never read for legality. The controller preserves exact-byte `run.yaml` tamper detection, holds a run-local single-writer lock, and replaces only `control.json` atomically. Projection regeneration is best-effort after commit.

Discovery keeps provenance in `10-decisions.md` and stages each complete PRD replacement in `.20-prd.next.md`. `tools/render_prd.py write` is the only canonical write path: it renders first, then atomically replaces each of `20-prd.md` and non-authoritative `20-prd.html`. Render/staging failure preserves the prior pair; an interrupted two-file install leaves a detectable mismatch that blocks closure. Producers leave candidates at `status: draft` and record readiness only. Discovery's product-closure boundary requires `AGENT_REVIEW` or `HUMAN`; `AUTO` is unavailable because the boundary includes semantic acceptance. Agent review consumes a structured read-only envelope bound to run identity and candidate version/hash. Fresh-context reviewer independence is an invocation responsibility in V1; the controller does not authenticate reviewer identity. The controller validates mechanics and authority evidence but does not grade prose.

Current accepted provenance is the stage binding under `control.json.acceptances`, containing candidate version/hash, authority, date, and review reference/hash when applicable. Stage 0–2 creates no historical acceptance ledger, `approved/` copies, receipt files, transaction journal, replay log, amendment ledger, event stream, or hash chain.

Repository/baseline corrections use ordered `amendments/NNN-*.md`. Control stores only accepted amendment count and resulting effective configuration hash.

## Installation

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@dstkwll
```

The deterministic controller/renderer require Python 3.9+ and the pinned packages in `plugins/atlas/requirements.txt`. Installation is explicit, never automatic: `python3 -m pip install -r plugins/atlas/requirements.txt`.

## Current boundary

Stages 3–5 and execution are not implemented here. The Stage 0–2 controller stops when it reaches the next selected unsupported phase. It does not call incubator workers or create orchestration machinery.

## Licence

MIT. See [`../incubator/LICENSE`](../incubator/LICENSE) for separately forked incubator material.
