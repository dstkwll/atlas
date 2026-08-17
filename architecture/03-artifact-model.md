# 03 — Artifact Model

## Recommended directory layout

```text
<planning-root>/
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

## Planning root

`<planning-root>` is resolved from configuration (`artifacts.planning_root`), not fixed by this document. It takes one of two forms:

- **Repository-relative** — the default, `.planning/` inside the repository being changed. `.planning/` is preferred over `docs/` because these are working engineering artifacts. Durable architectural knowledge may later graduate into `CONTEXT.md`, `docs/adr/`, or permanent documentation.
- **External** — an absolute path or a separate planning repository, shared by many code repositories.

The external form exists because a change is not always confined to one repository. Where an organization has many small repositories rather than a monorepo, a single unit of work commonly spans several, and no one of them is an honest home for the artifacts describing it. Forcing such work into one repository's `.planning/` requires nominating an arbitrary owning repository, which misrepresents the change.

An external planning root is a location with an access model, not merely a path. A root reachable only by its author cannot be referenced by collaborators; a shared planning repository can. Configuration therefore records the root, and no artifact records an absolute path that resolves differently for different readers.

### `repos`

A feature that affects more than one repository declares them. Each affected repository is named in the feature's `run.yaml` and mirrored into `00-state.md` frontmatter, so the question *which planning artifacts touched this repository* is answerable by query against the planning root rather than by search across repositories.

### Consequences of an external root

These are costs, not defects, and are accepted deliberately:

- **Specification and code no longer share a commit.** With a repository-relative root, the approved contract and the change implementing it appear in one history; with an external root they do not. Correlation is by explicit reference, not by construction.
- **Review loses ambient context.** A reviewer reading a pull request cannot see the contract unless the planning root is resolvable in their environment. Contract review therefore depends on configuration being correct wherever review runs.
- **Atomicity is lost.** Repository-relative planning gives history, blame, and atomic spec-plus-code commits for free. An external root gives none of these unless it is itself version-controlled.

Where a repository benefits from a permanent local record — a public repository, or one whose readers cannot reach the planning root — a decision may **graduate** into that repository as an ADR under `artifacts.adr_path`. Graduation is a deliberate act producing a durable record, not an automatic mirror of planning state.

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
- resolved planning root
- repository baseline
- affected repositories (`repos`)

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

repos:
  - device-service
  - job-scheduler

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
