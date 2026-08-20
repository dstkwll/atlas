# 03 — Artifact Model

## Recommended directory layout

```text
<planning-root>/
└── <feature-slug>/
    ├── run.yaml
    ├── control.json
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

**An external root resolves to an already-usable local filesystem path.** Configuration names a directory that exists and is readable when a run begins. Cloning, authentication, fetch and push lifecycle, synchronization, remote locking, conflict resolution, and repository provisioning are **outside this architecture**. Where the planning root happens to be a checkout of a shared repository, keeping that checkout current is the operator's responsibility, not the factory's. The contract here concerns artifact location and reference semantics, not remote repository management.

### `repos`

A feature that affects more than one repository declares them. Each affected repository is named in the feature's `run.yaml` and mirrored into `00-state.md` frontmatter, so the question *which planning artifacts touched this repository* is answerable by query against the planning root rather than by search across repositories.

The planning effort also preserves the relevant baseline for **each** affected repository. The architecture does not freeze a larger multi-repository schema here; the invariant is the pair itself — repository identity plus the baseline against which that repository was planned. Without one baseline per repository, later compilation cannot tell which version of each codebase the approved design describes.

`repos` and their planning baselines are **descriptive planning metadata**. They record what a body of work concerns. They grant no access, and they do not widen any agent's write scope.

### Planning scope is not execution scope

One planning effort may describe work spanning several repositories. Factory execution remains **repository-scoped**:

- Each executable ticket identifies exactly one target repository unambiguously. Compilation may partition a multi-repository planning effort into repository-scoped ticket sets; it may not leave target selection to the executor.
- An executable factory run and its immutable run manifest resolve **one repository, one worktree, and that repository's baseline**. The baseline is the corresponding repository-baseline pair preserved by planning.
- Cross-repository atomic execution, synchronized branches, coordinated integration, multi-repository rollback, and multi-pull-request transaction semantics are **not** capabilities of this architecture. A planning effort spanning several repositories is executed as several repository-scoped runs.

The planning root and the execution scope are separate concerns. Widening the first does not widen the second.

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
- affected repositories (`repos`)
- planning baseline for each affected repository

Do not rely on changing global config to reconstruct historical behavior.

---

## `control.json`

Purpose:

> Machine-canonical planning-control state for Stages 0–2.

It records only the current planning phase and revision, gate outcomes, the immutable intake
hash/effective amendment revision, and accepted candidate version/hash provenance. The
controller replaces this one JSON file atomically. It is not execution runtime state and does
not contain ticket ownership, attempts, retries, or repository-scoped factory events.

An accepted discovery or specification remains in its prescribed artifact path. Acceptance
records its current version and content hash in `control.json`; V1 does not create a second
approved copy or retain a separate acceptance history. Reopening leaves that binding visible
while stale and requires the producer to increment the candidate version; the next acceptance
replaces it.

---

## `00-state.md`

Purpose:

> Generated human-readable projection of `control.json`.

Example projection:

```yaml
---
source: control.json
feature: async-device-jobs
status: planning
phase: specification
revision: 3

gates:
  discovery: AGENT_APPROVED
  specification: PENDING

blocked_reason: null
---
```

The controller may regenerate this projection after a successful transition, but never reads
it to decide transition legality. If projection and `control.json` disagree, `control.json`
wins and the projection is stale.

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

For a Stage 1 or Stage 2 `AGENT_REVIEW` gate, the invoker persists the read-only judge's
structured output as `reviews/<stage>-v<version>.json`. It binds `run`, `stage`, candidate
`version` and SHA-256, `verdict: PASS|BLOCKED`, and an array of gaps; each gap includes a stable
code, artifact, problem, and resume stage/action. A PASS envelope has no gaps. The controller
validates and hashes this envelope but never asks it to modify the artifact or state. V1 does not
add authenticated reviewer identities or signatures: the invoker must obtain the envelope from
a fresh read-only context, while the controller enforces only schema and current run/version/hash
binding. This limitation is explicit rather than implying cryptographic independence.

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

For Stages 0–2, an accepted intake correction uses the existing ordered
`amendments/NNN-*.md` form with machine-parseable frontmatter. `control.json` records the
accepted amendment count and resulting effective-configuration hash. V1 does not add a
separate amendment ledger, per-amendment receipt file, or hash chain.
