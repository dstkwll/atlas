# atlas plugin

First-party Stage 0–3 skills implementing the Atlas architecture through exact System Design participation and HUMAN/AGENT_REVIEW/HUMAN_IF_CHANGED authority paths. `architecture/` remains authoritative; report conflicts rather than silently reconciling them. The neighboring `incubator` plugin is not part of this workflow and intentionally retains its own independent example transition material.

## Implemented flow

```text
start-run freezes run.yaml and initializes control.json
  → discovery continuously maintains 10-decisions.md and 20-prd.md when selected
  → product closure records configured AGENT_REVIEW or HUMAN acceptance when selected
  → atlas_planning.py initializes planning-control.json at the Stage 0 handoff
  → system-design reads frozen agent_led/co_design participation and produces exact 30-system-design.md readiness
  → co_design writes through render_system_design.py and requires current non-authoritative 30-system-design.html
  → read-only System Design check
  → workflow-internal control-planning applies HUMAN or assembles exact classifier/reviewer evidence
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
| `control-planning` | Check System Design, consume the frozen authority matrix, assemble exact evidence when required, and invoke one deterministic planning transition. |

Invoke explicitly as `atlas:<skill>`.

## Planning authority

Feature-root `control.json` is the only authoritative mutable Stage 0–2 state. Its mutable gate map contains the discovery product-closure boundary only when selected; otherwise `phase` starts at the first selected downstream stage with no mutable gate. Immutable `run.yaml` retains later-stage and conditional policy. After discovery acceptance, `phase` may name the next selected stage, where this controller likewise fails closed and hands off without creating later-stage gate state. `00-state.md` is a generated projection and is never read for legality. The controller preserves exact-byte `run.yaml` tamper detection, holds a run-local single-writer lock, and replaces only `control.json` atomically. Projection regeneration is best-effort after commit.

Discovery keeps provenance in `10-decisions.md` and stages each complete PRD replacement in `.20-prd.next.md`. `tools/render_prd.py write` is the only canonical write path: it renders first, then atomically replaces each of `20-prd.md` and non-authoritative `20-prd.html`. Render/staging failure preserves the prior pair; an interrupted two-file install leaves a detectable mismatch that blocks closure. Producers leave candidates at `status: draft` and record readiness only. Discovery's product-closure boundary requires `AGENT_REVIEW` or `HUMAN`; `AUTO` is unavailable because the boundary includes semantic acceptance. Agent review consumes a structured read-only envelope bound to run identity and candidate version/hash. Fresh-context reviewer independence is an invocation responsibility in V1; the controller does not authenticate reviewer identity. The controller validates mechanics and authority evidence but does not grade prose.

Current accepted Stage 0–2 provenance is the stage binding under `control.json.acceptances`, containing candidate version/hash, authority, date, and review reference/hash when applicable. Stage 0–2 creates no historical acceptance ledger, `approved/` copies, receipt files, transaction journal, replay log, amendment ledger, event stream, or hash chain.

Separate feature-root `planning-control.json` is the authoritative mutable Stage 3–5 planning snapshot. Slice 2B preserves agent-led/co-design and direct HUMAN behavior, and adds exact System Design AGENT_REVIEW and HUMAN_IF_CHANGED evidence paths. `atlas_planning.py check --stage system_design` stays read-only and mechanical; co-design still requires a current exact deterministic board. `advance` accepts parser-optional `--approval human` and `--review reviews/system-design-v1.json`, then enforces the frozen authority matrix. The duplicate-safe exact envelope binds immutable `run.yaml.repos`, current candidate, policy, materiality, and semantic review; it is evidence, not authority. Under the planning lock, the controller rereads planning, candidate, source, and envelope immediately before atomic replacement. Accepted evidence authorities remain loadable only while those exact current bytes and bindings remain valid. Acceptance leaves candidate/board/run/control/evidence unchanged, stores only the review ref/hash when required, and never accepts HTML independently.

Repository/baseline corrections use ordered `amendments/NNN-*.md`. Control stores only accepted amendment count and resulting effective configuration hash.

## Installation

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@dstkwll
```

The deterministic controller/renderer require Python 3.9+ and the pinned packages in `requirements.txt` beside this README. Installation is explicit, never automatic. Resolve the installed plugin directory and quote it so the command works from any caller directory: `python3 -m pip install -r "<atlas-plugin-root>/requirements.txt"`.

## Current boundary

Slice 2B supports frozen `agent_led` or `co_design` participation independently of exact `HUMAN`, `AGENT_REVIEW`, or canonical `HUMAN_IF_CHANGED` policy. Direct HUMAN uses explicit approval and no envelope. Direct AGENT_REVIEW requires a fresh seven-dimension PASS envelope. HUMAN_IF_CHANGED uses the same exact D-073 dimensions: material/unavailable/explained classifier failure maps to HUMAN with review evidence plus explicit approval, while seven NOT_MATERIAL rows map to a distinct fresh semantic reviewer and AGENT_REVIEW. No configured path falls back. The producer still writes only candidate/board/readiness and hands internally to control.

The user invokes `atlas:system-design` once; that producer contract requires the exact internal handoff to `atlas:control-planning`, which consumes the exact configured authority/evidence for the Markdown/hash/source and calls the deterministic transition without a second user command. This repository statically verifies the handoff contract but has not executed installed-host skill-to-skill chaining in Copilot/Codex; Slice 5 owns that proof. If the host cannot perform the named handoff, the adapter becomes a shared internal procedure rather than another manual user command.

System Design rejection/reopen/staleness, Program Design, ticket compilation/acceptance, and execution remain intentionally unimplemented and fail closed for later slices. `atlas_planning.py` still accepts only `initialize`, `check --stage system_design`, and `advance --stage system_design [--approval human] [--review reviews/system-design-v1.json] --date YYYY-MM-DD`; it does not route or own Stage 6+ behavior. The Stage 0–2 controller remains separate, never widens `control.json`, and no model router, controller, state file, renderer, manifest dependency, or revision snapshot was added. Static contracts still do not prove installed-host chaining; Slice 5 owns that proof.

## Licence

MIT. See [`../incubator/LICENSE`](../incubator/LICENSE) for separately forked incubator material.
