# Planning control and projection

`control.json` is the only authoritative mutable Stage 0–2 state. `00-state.md` is generated for humans and is never read to decide legality.

When discovery is selected, initialization creates this shape:

```json
{
  "version": 1,
  "run": "<feature-slug>",
  "status": "PLANNING",
  "phase": "discovery",
  "revision": 1,
  "base_run_sha256": "<sha256>",
  "effective_config_hash": "<sha256>",
  "effective_config_revision": 0,
  "accepted_amendment_count": 0,
  "gates": {
    "discovery": "PENDING"
  },
  "blocked_reason": null,
  "acceptances": {
    "discovery": null
  }
}
```

`gates` contains mutable state only for the selected discovery Product Definition Approval boundary this Stage 0–2 controller implements. `run.yaml` retains all later-stage and conditional policy. After discovery acceptance, `phase` may name the next selected stage while `gates` remains unchanged; that phase is a fail-closed handoff to its owning controller.

When discovery is omitted, initialization sets `phase` to the first selected downstream stage and writes empty `gates` and `acceptances` maps. That omission has conceptual `NOT_REQUIRED` semantics and grants no approval. A pre-existing `20-prd.md` may coexist with either branch, but initialization never accepts it; selected discovery must reconcile and judge reused PRD material normally.

Each accepted candidate replaces its stage's current binding:

```json
{
  "candidate_version": 1,
  "candidate_sha256": "<sha256>",
  "authority": "HUMAN",
  "accepted": "2026-08-20",
  "review_reference": null,
  "review_sha256": null
}
```

`AGENT_REVIEW` records the review's run-relative reference and byte hash. HUMAN leaves both null. No approved copy, receipt file, or historical acceptance ledger is created.

The generated projection carries the same key facts:

```markdown
---
source: control.json
feature: <feature-slug>
status: PLANNING
phase: discovery
revision: 1
effective_config_revision: 0
effective_config_hash: <sha256>
base_run_sha256: <sha256>
gates:
  discovery: PENDING
blocked_reason: null
accepted_amendment_count: 0
acceptances:
  discovery: null
---

# Atlas state projection
```

Valid Stage 0–2 gate outcomes are `PENDING`, `AGENT_APPROVED`, `HUMAN_APPROVED`, `REJECTED`, and `STALE`. `AUTO_PASSED` is reserved for a future mechanical-only boundary; discovery cannot use it.
