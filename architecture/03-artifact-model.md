# 03 — Artifact Model

## Recommended directory layout

```text
.planning/
└── <feature-slug>/
    ├── run.yaml
    ├── 00-state.md
    ├── 10-decisions.md
    ├── 20-spec.md
    ├── 30-system-design.md
    ├── 40-program-design.md
    │
    ├── evidence/
    │   ├── current-state.md
    │   └── research-*.md
    │
    ├── spikes/
    │   └── <spike-name>/
    │
    ├── tickets/
    │   ├── 01-tracer.md
    │   ├── 02-*.md
    │   └── ...
    │
    ├── reviews/
    │   ├── ticket-01-contract.json
    │   ├── ticket-01-design.json
    │   └── final-*.json
    │
    └── amendments/
        └── 001-*.md
```

`.planning/` is preferred over `docs/` because these are working engineering artifacts. Durable architectural knowledge may later graduate into `CONTEXT.md`, `docs/adr/`, or permanent documentation.

---

## `run.yaml`

Purpose:

> Immutable resolved configuration snapshot for this run.

Contains:

- selected workflow depth
- selected governance profile
- explicit overrides
- risk classification
- gate policy
- execution policy
- model roles
- artifact paths
- repository baseline

Do not rely on changing global config to reconstruct historical behavior.

---

## `00-state.md`

Purpose:

> Human-readable state mirror, with machine-parseable frontmatter.

Example:

```yaml
---
feature: async-device-jobs
status: planning
phase: program-design
baseline: 89a1c732
revision: 4

gates:
  spec: approved
  system_design: approved
  program_design: in_review
  tickets: pending

active_ticket: null
---
```

Authoritative machine state may eventually live in a structured state file/database, but a boring on-disk representation is useful for observability and recovery.

---

## `10-decisions.md`

Purpose:

> Durable record of important pre-spec decisions and their rationale.

Possible schema:

```markdown
## DEC-004 — Job execution ownership

Status: resolved
Source: grill
Decision: Worker owns device execution; scheduler only enqueues.
Why: ...
Alternatives: ...
Consequences: ...
```

This is not necessarily required for every small feature.

---

## `20-spec.md`

Owns:

> External/observable behavior.

Should answer:

- what problem exists?
- what must become true?
- what is explicitly not required?
- what invariants must hold?
- what behaviors constitute acceptance?

Must not become an implementation plan.

---

## `30-system-design.md`

Owns:

> System placement, boundaries, contracts, data ownership, and end-to-end behavior.

Should be architecture-level, not file/class-level.

---

## `40-program-design.md`

Owns:

> Internal code shape necessary to implement the approved system design.

Typical details:

```text
src/
  scheduling/
    JobScheduler.cs       MODIFY
    ScheduledJob.cs       NEW
    IJobQueue.cs          NEW

  workers/
    DeviceJobWorker.cs    NEW
```

and public/internal contracts such as important type signatures and call chains.

---

## `evidence/`

Purpose:

> Preserve factual findings that informed decisions without polluting normative design artifacts.

Examples:

- current code flow
- dependency inventory
- benchmark results
- external API constraints
- repository archaeology

Evidence is descriptive; specs/designs are normative.

---

## `spikes/`

Purpose:

> Isolated learning experiments used to reduce uncertainty.

A spike is not automatically production code and does not automatically require human review.

See `07-spikes-and-discovery.md` for detailed semantics.

---

## `tickets/*.md`

Purpose:

> Agent-grabbable vertical execution contracts.

Suggested frontmatter:

```yaml
---
id: async-jobs-02
status: ready
blocked_by:
  - async-jobs-01
risk: medium

references:
  spec: ../20-spec.md
  system_design: ../30-system-design.md
  program_design: ../40-program-design.md

validation:
  - dotnet test --filter JobCancellation
  - dotnet test

review:
  contract: required
  design: required
---
```

Human-readable body:

```markdown
# Cancellation

## What becomes true

A scheduled but not-yet-executing job can be cancelled.

## Acceptance

- Cancellation succeeds for an existing pending job.
- Cancelled jobs are never dispatched.
- Cancellation is idempotent.

## Relevant design

See `40-program-design.md#job-cancellation`.
```

Tickets should not duplicate upstream architecture/program design.

---

## `reviews/`

Prefer structured reviewer output where practical.

Example:

```json
{
  "decision": "reject",
  "findings": [
    {
      "severity": "blocking",
      "contract": "program-design §3.2",
      "problem": "Cancellation ownership moved into DeviceAdapter",
      "evidence": "..."
    }
  ]
}
```

This allows deterministic routing without requiring code to parse prose sentiment.

---

## `amendments/`

Approved upstream artifacts should not be silently edited by implementers.

A change in an approved contract should produce an explicit amendment containing:

- trigger/evidence
- affected artifact/section
- proposed change
- impact on tickets already completed
- required re-review/re-validation
- approval

The system may later fold approved amendments back into canonical documents, but provenance should remain visible.
