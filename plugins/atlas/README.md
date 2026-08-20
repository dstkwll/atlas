# atlas plugin

First-party Stage 0–2 skills implementing the Atlas architecture. `architecture/` remains authoritative; report conflicts rather than silently reconciling them. The neighboring `incubator` plugin is not part of this workflow.

## Implemented flow

```text
start-run freezes run.yaml and initializes control.json
  → discovery produces 10-decisions.md
  → read-only check
  → configured AGENT_REVIEW or HUMAN authority
  → controller records one transition
  → to-spec produces 20-spec.md
  → read-only check
  → configured AGENT_REVIEW or HUMAN authority
  → controller records one transition and stops at the next selected stage
```

| Skill | Responsibility |
|---|---|
| `setup-atlas` | Configure the planning root. |
| `start-run` | Accept immutable Stage 0 `run.yaml`; initialize control. |
| `discovery` | Produce the Stage 1 decision candidate. |
| `spike` | Produce bounded discovery evidence. |
| `to-spec` | Produce the Stage 2 behavioral candidate. |
| `control-run` | Run read-only checks, consume authority, and invoke one deterministic transition. |

Invoke explicitly as `atlas:<skill>`.

## Planning authority

Feature-root `control.json` is the only authoritative mutable Stage 0–2 state. Its mutable gate map contains only selected discovery and specification boundaries; immutable `run.yaml` retains later-stage and conditional policy. After specification acceptance, `phase` may name the next selected stage, where this controller fails closed and hands off without creating later-stage gate state. `00-state.md` is a generated projection and is never read for legality. The controller preserves exact-byte `run.yaml` tamper detection, holds a run-local single-writer lock, and replaces only `control.json` atomically. Projection regeneration is best-effort after commit.

Producers leave candidates at `status: draft` and record readiness only. Discovery and specification require `AGENT_REVIEW` or `HUMAN`; `AUTO` is unavailable because both boundaries include semantic acceptance. Agent review consumes a structured read-only envelope bound to run identity and candidate version/hash. Fresh-context reviewer independence is an invocation responsibility in V1; the controller does not authenticate reviewer identity. The controller validates mechanics and authority evidence but does not grade prose.

Current accepted provenance is the stage binding under `control.json.acceptances`, containing candidate version/hash, authority, date, and review reference/hash when applicable. Stage 0–2 creates no historical acceptance ledger, `approved/` copies, receipt files, transaction journal, replay log, amendment ledger, event stream, or hash chain.

Repository/baseline corrections use ordered `amendments/NNN-*.md`. Control stores only accepted amendment count and resulting effective configuration hash.

## Installation

```shell
copilot plugin marketplace add dstkwll/atlas
copilot plugin install atlas@dstkwll
```

The deterministic controller requires Python 3.9+ and PyYAML.

## Current boundary

Stages 3–5 and execution are not implemented here. The Stage 0–2 controller stops when it reaches the next selected unsupported phase. It does not call incubator workers or create orchestration machinery.

## Licence

MIT. See [`../incubator/LICENSE`](../incubator/LICENSE) for separately forked incubator material.
