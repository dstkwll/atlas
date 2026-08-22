# atlas plugin

First-party Stage 0–4 skills implementing the Atlas architecture through exact System Design participation and frozen System/Program Design authority paths. `architecture/` remains authoritative; report conflicts rather than silently reconciling them. The neighboring `incubator` plugin is not part of this workflow and intentionally retains its own independent example transition material.

## Implemented flow

```text
start-run freezes run.yaml and initializes control.json
  → discovery continuously maintains 10-decisions.md and 20-prd.md when selected
  → product closure records configured AGENT_REVIEW or HUMAN acceptance when selected
  → atlas_planning.py ensure idempotently initializes or verifies planning-control.json at the Stage 0 handoff
  → system-design reads frozen agent_led/co_design participation and produces exact 30-system-design.md readiness
  → co_design writes through render_system_design.py and requires current non-authoritative 30-system-design.html
  → read-only System Design check
  → workflow-internal control-planning applies the exact System Design authority/evidence matrix
  → atlas_planning.py records one exact System Design acceptance and advances when selected
  → program-design requires readable exact frozen repository trees and one selected source; unresolved repository access returns DESIGN_BLOCKED before readiness
  → read-only Program Design mechanical check
  → workflow-internal control-planning requires fresh Program Design review and applies AGENT_REVIEW or HUMAN authority
  → atlas_planning.py records one exact Program Design acceptance and advances to tickets
  → tickets remain intentionally unsupported and fail closed
```

| Skill | Responsibility |
|---|---|
| `setup-atlas` | Configure the planning root and verify an installed host. |
| `start-run` | Accept immutable Stage 0 `run.yaml`, initialize control, or resume from authoritative state. |
| `discovery` | Maintain decisions, the living PRD, and closure preparation. |
| `spike` | Produce bounded discovery evidence. |
| `control-run` | Run the read-only product-closure check, consume authority, and invoke one deterministic transition. |
| `system-design` | Produce the exact agent-led or co-design Stage 3 candidate/board, record readiness, and continue the internal control handoff. |
| `program-design` | Produce the exact Stage 4 candidate, record readiness, and continue the internal control handoff. |
| `control-planning` | Check explicit System or Program Design, consume its frozen authority matrix, assemble exact evidence when required, and invoke one deterministic planning transition. |

Enter a normal workflow through `atlas:start-run`; implemented downstream owners route and hand off internally. A direct `atlas:<skill>` invocation is reserved for bounded entry, testing, or diagnosis.

## Planning authority

Feature-root `control.json` is the only authoritative mutable Stage 0–2 state. Its mutable gate map contains the discovery product-closure boundary only when selected; otherwise `phase` starts at the first selected downstream stage with no mutable gate. Immutable `run.yaml` retains later-stage and conditional policy. After discovery acceptance, `phase` may name the next selected stage, where this controller likewise fails closed and hands off without creating later-stage gate state. `00-state.md` is a generated projection and is never read for legality. The controller preserves exact-byte `run.yaml` tamper detection, holds a run-local single-writer lock, and replaces only `control.json` atomically. Projection regeneration is best-effort after commit.

Discovery keeps provenance in `10-decisions.md` and stages each complete PRD replacement in `.20-prd.next.md`. `tools/render_prd.py write` is the only canonical write path: it renders first, then atomically replaces each of `20-prd.md` and non-authoritative `20-prd.html`. Render/staging failure preserves the prior pair; an interrupted two-file install leaves a detectable mismatch that blocks closure. Producers leave candidates at `status: draft` and record readiness only. Discovery's product-closure boundary requires `AGENT_REVIEW` or `HUMAN`; `AUTO` is unavailable because the boundary includes semantic acceptance. Agent review consumes a structured read-only envelope bound to run identity and candidate version/hash. Fresh-context reviewer independence is an invocation responsibility in V1; the controller does not authenticate reviewer identity. The controller validates mechanics and authority evidence but does not grade prose.

Current accepted Stage 0–2 provenance is the stage binding under `control.json.acceptances`, containing candidate version/hash, authority, date, and review reference/hash when applicable. Stage 0–2 creates no historical acceptance ledger, `approved/` copies, receipt files, transaction journal, replay log, amendment ledger, event stream, or hash chain.

Separate feature-root `planning-control.json` is the authoritative mutable Stage 3–5 planning snapshot. Slice 2B preserves agent-led/co-design and direct HUMAN behavior, and adds exact System Design AGENT_REVIEW and HUMAN_IF_CHANGED evidence paths. `atlas_planning.py check --stage system_design` stays read-only and mechanical; co-design still requires a current exact deterministic board. `advance` accepts parser-optional `--approval human` and `--review reviews/system-design-v1.json`, then enforces the frozen authority matrix. The duplicate-safe exact envelope binds the exact ordered current effective repository/baseline pairs after accepted Stage 0 amendments, plus the current candidate, policy, materiality, and semantic review; it is evidence, not authority. Under the planning lock, the controller rereads planning, candidate, source, and envelope immediately before atomic replacement. Accepted evidence authorities remain loadable only while those exact current bytes and bindings remain valid. Acceptance leaves candidate/board/run/control/evidence unchanged, stores only the review ref/hash when required, and never accepts HTML independently.

Repository/baseline corrections use ordered `amendments/NNN-*.md`. Control stores only accepted amendment count and resulting effective configuration hash.

## Installation

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@dstkwll
```

The deterministic controller/renderer require Python 3.9+ and the pinned packages in `requirements.txt` beside this README. Installation is explicit, never automatic. Resolve the installed plugin directory and quote it so the command works from any caller directory: `python3 -m pip install -r "<atlas-plugin-root>/requirements.txt"`.

Operational references:

- [`skills/setup-atlas/references/installed-host-calibration.md`](skills/setup-atlas/references/installed-host-calibration.md) separates installed bytes, host recognition, discovery, procedure completion, and handoff evidence.
- [`references/program-design-blocked.md`](references/program-design-blocked.md) preserves and classifies Program Design `BLOCKED`/`DESIGN_BLOCKED` stops without inventing a reopen path.

## Current boundary

System Design retains frozen `agent_led` or `co_design` participation independently of exact `HUMAN`, `AGENT_REVIEW`, or canonical `HUMAN_IF_CHANGED` policy. Direct HUMAN uses explicit approval and no envelope. Direct AGENT_REVIEW requires a fresh seven-dimension PASS envelope. HUMAN_IF_CHANGED preserves the exact D-073 classifier/reviewer mapping. No configured path falls back, and the producer still writes only candidate/board/readiness.

When the live planning phase reaches System Design, Atlas enters that producer internally; it hands off to `atlas:control-planning` without a second user routing command. When the live planning phase reaches Program Design, Atlas enters the Program Design producer internally. A direct `atlas:program-design` invocation is a bounded entry point for testing or diagnosis, not a normal routing requirement. The producer reads exactly one D-079 source, writes only `40-program-design.md` readiness after exact baseline access is proven, runs the mechanical check, and performs the internal handoff with stage `program_design`. Program Design never asks a participation question and creates no HTML. Producer-discovered `DESIGN_BLOCKED` stops read-only before readiness; reviewer-discovered `DESIGN_BLOCKED` exists only in fresh `reviews/program-design-v1.json`. Neither mutates planning state.

Program Design accepts only from a fresh exact PASS review under configured `AGENT_REVIEW` or reviewed `HUMAN`; `AUTO` and `HUMAN_IF_CHANGED` are unavailable. The existing `planning-control.json` remains the only mutable Stage 3–5 authority. `atlas_planning.py` accepts mechanical `check` and authority-matrix `advance` commands for explicit `system_design` or `program_design`; it never routes. After accepted Program Design, tickets remain intentionally unsupported: start/resume and control stop loudly because no first-party ticket producer exists.

System/Program Design rejection, reopen, replacement acceptance, staleness propagation, ticket compilation/acceptance, and execution remain deferred. The shared `ensure --run PATH` handoff remains strict, idempotent, and non-overwriting. The Stage 0–2 controller remains separate; this slice adds no model router, controller, state file, renderer, manifest dependency, or revision snapshot.

## Licence

MIT. Separately forked incubator material retains its own licence in the [repository source](https://github.com/dstkwll/atlas/blob/main/plugins/incubator/LICENSE).
