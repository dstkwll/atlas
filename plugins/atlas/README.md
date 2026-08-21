# atlas plugin

First-party Stage 0–3 skills implementing the Atlas architecture through the agent-led/co-design + HUMAN System Design tracer. `architecture/` remains authoritative; report conflicts rather than silently reconciling them. The neighboring `incubator` plugin is not part of this workflow and intentionally retains its own independent example transition material.

## Implemented flow

```text
start-run freezes run.yaml and initializes control.json
  → discovery continuously maintains 10-decisions.md and 20-prd.md when selected
  → product closure records configured AGENT_REVIEW or HUMAN acceptance when selected
  → atlas_planning.py initializes planning-control.json at the Stage 0 handoff
  → system-design reads frozen agent_led/co_design participation and produces exact 30-system-design.md readiness
  → co_design writes through render_system_design.py and requires current non-authoritative 30-system-design.html
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
| `system-design` | Produce the exact agent-led or co-design Stage 3 candidate/board, record readiness, and continue the internal control handoff. |
| `control-planning` | Check the current System Design candidate, obtain explicit HUMAN approval, and invoke one deterministic planning transition. |

Invoke explicitly as `atlas:<skill>`.

## Planning authority

Feature-root `control.json` is the only authoritative mutable Stage 0–2 state. Its mutable gate map contains the discovery product-closure boundary only when selected; otherwise `phase` starts at the first selected downstream stage with no mutable gate. Immutable `run.yaml` retains later-stage and conditional policy. After discovery acceptance, `phase` may name the next selected stage, where this controller likewise fails closed and hands off without creating later-stage gate state. `00-state.md` is a generated projection and is never read for legality. The controller preserves exact-byte `run.yaml` tamper detection, holds a run-local single-writer lock, and replaces only `control.json` atomically. Projection regeneration is best-effort after commit.

Discovery keeps provenance in `10-decisions.md` and stages each complete PRD replacement in `.20-prd.next.md`. `tools/render_prd.py write` is the only canonical write path: it renders first, then atomically replaces each of `20-prd.md` and non-authoritative `20-prd.html`. Render/staging failure preserves the prior pair; an interrupted two-file install leaves a detectable mismatch that blocks closure. Producers leave candidates at `status: draft` and record readiness only. Discovery's product-closure boundary requires `AGENT_REVIEW` or `HUMAN`; `AUTO` is unavailable because the boundary includes semantic acceptance. Agent review consumes a structured read-only envelope bound to run identity and candidate version/hash. Fresh-context reviewer independence is an invocation responsibility in V1; the controller does not authenticate reviewer identity. The controller validates mechanics and authority evidence but does not grade prose.

Current accepted Stage 0–2 provenance is the stage binding under `control.json.acceptances`, containing candidate version/hash, authority, date, and review reference/hash when applicable. Stage 0–2 creates no historical acceptance ledger, `approved/` copies, receipt files, transaction journal, replay log, amendment ledger, event stream, or hash chain.

Separate feature-root `planning-control.json` is the authoritative mutable Stage 3–5 planning snapshot. Slice 2A preserves Slice 1's agent-led + HUMAN path and adds co-design + HUMAN. `atlas_planning.py check --stage system_design` is read-only and mechanical; for `co_design` it additionally verifies current `30-system-design.html` source/hash/version metadata and all stable board views, and accepted co-design state fails closed if that mandatory projection later becomes missing or stale. `advance` holds `.atlas-planning.lock`, revalidates the frozen Stage 0 anchor and candidate/source bytes, reruns the same check at the write boundary, and atomically replaces only `planning-control.json`. Acceptance leaves canonical `30-system-design.md` at `status: draft`, records its exact candidate/source bindings with empty repository baselines and null review references, never hashes or accepts the non-authoritative HTML independently, and never edits `run.yaml` or `control.json`.

Repository/baseline corrections use ordered `amendments/NNN-*.md`. Control stores only accepted amendment count and resulting effective configuration hash.

## Installation

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@dstkwll
```

The deterministic controller/renderer require Python 3.9+ and the pinned packages in `requirements.txt` beside this README. Installation is explicit, never automatic. Resolve the installed plugin directory and quote it so the command works from any caller directory: `python3 -m pip install -r "<atlas-plugin-root>/requirements.txt"`.

## Current boundary

Slice 2A supports `system_design_participation: agent_led` or `co_design` only with `run.yaml.gates.system_design.authority: HUMAN`, using either the exact accepted Product Closure binding or exact frozen direct Stage 0 binding. Agent-led behavior remains the Slice 1 path. Co-design works one labelled seam/decision at a time and uses `render_system_design.py write --draft .30-system-design.next.md` as the canonical paired Markdown/HTML write path; pre-install failures preserve the prior pair and an interrupted install leaves a mismatch that blocks checking. The HTML is deterministic, self-contained, metadata-bound, and non-authoritative.

The user invokes `atlas:system-design` once; that producer contract requires the exact internal handoff to `atlas:control-planning`, which obtains explicit approval of the exact Markdown/hash/source and calls the deterministic transition without a second user command. This repository statically verifies the handoff contract but has not executed installed-host skill-to-skill chaining in Copilot/Codex; Slice 5 owns that proof. If the host cannot perform the named handoff, the adapter becomes a shared internal procedure rather than another manual user command.

`HUMAN_IF_CHANGED`, `AGENT_REVIEW`, review/classification envelopes, System Design rejection/reopen/staleness, Program Design, ticket compilation/acceptance, and execution remain intentionally unimplemented and fail closed for Slice 2B or later. `atlas_planning.py` still accepts only `initialize`, `check --stage system_design`, and `advance --stage system_design --approval human --date YYYY-MM-DD`; it does not route or own Stage 6+ behavior. The Stage 0–2 controller remains separate, never widens `control.json`, and never calls incubator workers or creates orchestration machinery.

## Licence

MIT. See [`../incubator/LICENSE`](../incubator/LICENSE) for separately forked incubator material.
