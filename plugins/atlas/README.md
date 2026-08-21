# atlas plugin

First-party Stage 0–3 skills implementing the Atlas architecture through the agent-led + HUMAN System Design tracer. `architecture/` remains authoritative; report conflicts rather than silently reconciling them. The neighboring `incubator` plugin is not part of this workflow and intentionally retains its own independent example transition material.

## Implemented flow

```text
start-run freezes run.yaml and initializes control.json
  → discovery continuously maintains 10-decisions.md and 20-prd.md when selected
  → product closure records configured AGENT_REVIEW or HUMAN acceptance when selected
  → atlas_planning.py initializes planning-control.json at the Stage 0 handoff
  → system-design produces exact agent-led 30-system-design.md readiness
  → read-only System Design check
  → workflow-internal control-planning obtains explicit HUMAN approval
  → atlas_planning.py records one exact acceptance and advances to the next selected boundary
  → unsupported downstream stages remain fail-closed
```

| Skill | Responsibility |
|---|---|
| `setup-atlas` | Configure the planning root. |
| `start-run` | Accept immutable Stage 0 `run.yaml`; initialize control. |
| `discovery` | Maintain decisions, the living PRD, and closure preparation. |
| `spike` | Produce bounded discovery evidence. |
| `control-run` | Run the read-only product-closure check, consume authority, and invoke one deterministic transition. |
| `system-design` | Produce the exact agent-led Stage 3 candidate, record readiness, and continue the internal control handoff. |
| `control-planning` | Check the current System Design candidate, obtain explicit HUMAN approval, and invoke one deterministic planning transition. |

Invoke explicitly as `atlas:<skill>`.

## Planning authority

Feature-root `control.json` is the only authoritative mutable Stage 0–2 state. Its mutable gate map contains the discovery product-closure boundary only when selected; otherwise `phase` starts at the first selected downstream stage with no mutable gate. Immutable `run.yaml` retains later-stage and conditional policy. After discovery acceptance, `phase` may name the next selected stage, where this controller likewise fails closed and hands off without creating later-stage gate state. `00-state.md` is a generated projection and is never read for legality. The controller preserves exact-byte `run.yaml` tamper detection, holds a run-local single-writer lock, and replaces only `control.json` atomically. Projection regeneration is best-effort after commit.

Discovery keeps provenance in `10-decisions.md` and stages each complete PRD replacement in `.20-prd.next.md`. `tools/render_prd.py write` is the only canonical write path: it renders first, then atomically replaces each of `20-prd.md` and non-authoritative `20-prd.html`. Render/staging failure preserves the prior pair; an interrupted two-file install leaves a detectable mismatch that blocks closure. Producers leave candidates at `status: draft` and record readiness only. Discovery's product-closure boundary requires `AGENT_REVIEW` or `HUMAN`; `AUTO` is unavailable because the boundary includes semantic acceptance. Agent review consumes a structured read-only envelope bound to run identity and candidate version/hash. Fresh-context reviewer independence is an invocation responsibility in V1; the controller does not authenticate reviewer identity. The controller validates mechanics and authority evidence but does not grade prose.

Current accepted Stage 0–2 provenance is the stage binding under `control.json.acceptances`, containing candidate version/hash, authority, date, and review reference/hash when applicable. Stage 0–2 creates no historical acceptance ledger, `approved/` copies, receipt files, transaction journal, replay log, amendment ledger, event stream, or hash chain.

Separate feature-root `planning-control.json` is the authoritative mutable Stage 3–5 planning snapshot. Slice 1 implements only initial state plus agent-led System Design accepted by explicit HUMAN authority. `atlas_planning.py check --stage system_design` is read-only and mechanical; `advance` holds `.atlas-planning.lock`, revalidates the frozen Stage 0 anchor and candidate/source bytes, and atomically replaces only `planning-control.json`. Acceptance leaves `30-system-design.md` at `status: draft`, records exact candidate/source bindings with empty repository baselines and null review references, and never edits `run.yaml` or `control.json`.

Repository/baseline corrections use ordered `amendments/NNN-*.md`. Control stores only accepted amendment count and resulting effective configuration hash.

## Installation

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@dstkwll
```

The deterministic controller/renderer require Python 3.9+ and the pinned packages in `requirements.txt` beside this README. Installation is explicit, never automatic. Resolve the installed plugin directory and quote it so the command works from any caller directory: `python3 -m pip install -r "<atlas-plugin-root>/requirements.txt"`.

## Current boundary

Slice 1 implements one tracer only: `system_design_participation: agent_led` with `run.yaml.gates.system_design.authority: HUMAN`, using either the exact accepted Product Closure binding or the exact frozen direct Stage 0 binding. The user invokes `atlas:system-design` once; that producer's contract requires the exact internal handoff to `atlas:control-planning`, which obtains approval and calls the deterministic transition without a second user command. This repository statically verifies the handoff contract but has not yet executed skill-to-skill chaining in an installed Copilot/Codex host; that host proof belongs to Slice 5. If the host cannot perform the named handoff, the adapter becomes a shared internal procedure rather than another manual user command.

Co-design rendering, `HUMAN_IF_CHANGED`, `AGENT_REVIEW`, System Design rejection/reopen/staleness, Program Design, ticket compilation/acceptance, and execution remain intentionally unimplemented and fail closed. There is no System Design HTML renderer or packaged semantic-review contract in this slice. `atlas_planning.py` accepts only `initialize`, `check --stage system_design`, and `advance --stage system_design --approval human --date YYYY-MM-DD`; it does not route or own Stage 6+ behavior. The Stage 0–2 controller remains separate, never widens `control.json`, and never calls incubator workers or creates orchestration machinery.

## Licence

MIT. See [`../incubator/LICENSE`](../incubator/LICENSE) for separately forked incubator material.
