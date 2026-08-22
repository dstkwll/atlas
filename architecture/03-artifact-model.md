# 03 — Artifact Model

## Recommended directory layout

```text
<planning-root>/
└── <feature-slug>/
    ├── run.yaml
    ├── control.json
    ├── 00-state.md
    ├── 10-decisions.md
    ├── 20-prd.md
    ├── 20-prd.html
    ├── 30-system-design.md
    ├── 30-system-design.html        # required only for co_design
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

Before a stage may inspect repository bytes, D-081 resolves each stable identity through the
machine-local `repositories.bindings` configuration. The binding is not copied into any run artifact.
It names one already-usable local Git repository/object source, from which Atlas verifies and reads
the exact full baseline commit tree directly. Current `HEAD`, index, and working-tree bytes are only
drift context and never baseline authority. Missing local access is `BLOCKED`; a contradiction found
after exact inspection is `DESIGN_BLOCKED` only when accepted upstream truth must change.

### Planning scope is not execution scope

One planning effort may describe work spanning several repositories. Factory execution remains **repository-scoped**:

- Each executable ticket identifies exactly one target repository unambiguously. Compilation may partition a multi-repository planning effort into repository-scoped ticket sets; it may not leave target selection to the executor.
- An executable factory run and its immutable run manifest resolve **one repository, one worktree, and that repository's baseline**. The baseline is the corresponding repository-baseline pair preserved by planning.
- Cross-repository atomic execution, synchronized branches, coordinated integration, multi-repository rollback, and multi-pull-request transaction semantics are **not** capabilities of this architecture. A planning effort spanning several repositories is executed as several repository-scoped runs.

The planning root and the execution scope are separate concerns. Widening the first does not widen the second.

### Consequences of an external root

These are costs, not defects, and are accepted deliberately:

- **Contract and code no longer share a commit.** With a repository-relative root, the approved contract and the change implementing it appear in one history; with an external root they do not. Correlation is by explicit reference, not by construction.
- **Review loses ambient context.** A reviewer reading a pull request cannot see the contract unless the planning root is resolvable in their environment. Contract review therefore depends on configuration being correct wherever review runs.
- **Atomicity is lost.** Repository-relative planning gives history, blame, and atomic contract-plus-code commits for free. An external root gives none of these unless it is itself version-controlled.

Where a repository benefits from a permanent local record — a public repository, or one whose readers cannot reach the planning root — a decision may **graduate** into that repository as an ADR under `artifacts.adr_path`. Graduation is a deliberate act producing a durable record, not an automatic mirror of planning state.

---

## `run.yaml`

Purpose:

> Immutable resolved configuration snapshot for this run.

Contains:

- selected workflow depth
- resolved ordered stages, including the earliest producer stage
- selected System Design participation (`agent_led` by default, or user-selected `co_design`)
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

Machine-local `repositories.bindings` is the deliberate exception to resolved-config snapshotting:
its paths are excluded from `run.yaml` and `effective_config_hash`, then resolved fresh on each
repository-inspection/check/acceptance attempt. The portable identity plus full baseline commit is
the stable truth; the current binding is only an environment route to those exact bytes.

---

## `control.json`

Purpose:

> Machine-canonical planning-control state for Stages 0–2.

It records only the current planning phase and revision, gate outcomes, the immutable intake
hash/effective amendment revision, and accepted candidate version/hash provenance. The
controller replaces this one JSON file atomically. It is not execution runtime state and does
not contain ticket ownership, attempts, retries, or repository-scoped factory events. Its mutable
`gates` map contains the discovery boundary only when selected. Immutable `run.yaml` retains
later-stage and conditional policy. When discovery is omitted, `phase` begins at the first selected
downstream stage with no mutable gate; after product closure acceptance, `phase` may likewise name
the next selected stage without creating mutable state for that stage.

An accepted discovery/product-closure candidate remains in its prescribed artifact path.
Acceptance records its current version and content hash in `control.json`; V1 does not create a
second approved copy or retain a separate acceptance history. The Stage 0–2 controller provides no
post-closure reopen. D-082 does not alter that rule: its one replacement path is owned by the
downstream planning controller and reaches only selected System Design from pending Program Design.
Any live Stage 0–2 mismatch after acceptance still fails closed (see 08 — State and Governance).

Stages 3–5 do not widen this file. One downstream planning controller is the logical mutable authority
for their separate System Design, Program Design, and ticket-graph outcomes, exact
candidate/version/hash bindings, and monotonic staleness. A changed accepted upstream design marks
all directly dependent downstream acceptances stale in the same logical atomic transition. The
controller ends at Stage 5 and owns no repository-scoped execution state. Its exact file, storage
representation, schema fields, lock, and module/CLI decomposition remain implementation choices;
v0.8 adds no separate compilation controller or generalized router.

D-082 constrains that existing downstream state without prescribing a new schema. During its one
selected-System-Design repair episode, the existing `blocked_reason` slot carries the active bounded
episode and attempt usage. The independently judged contradiction is stored at
`reviews/program-design-upstream-block-v1.json`; it is not a Program Design candidate review and
requires no ready candidate. No history array, event log, approved-copy store, or additional
top-level control field is introduced.

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
phase: discovery
revision: 3

gates:
  discovery: PENDING

blocked_reason: null
---
```

The controller may regenerate this projection after a successful transition, but never reads
it to decide transition legality. If projection and `control.json` disagree, `control.json`
wins and the projection is stale.

---

## `10-decisions.md`

Purpose:

> Durable record of important discovery decisions, their rationale, and the reconciliation
> provenance that binds them to the living PRD.

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

`10-decisions.md` also owns a required `## PRD alignment retrospective` table. That table is the
mechanical reconciliation surface for product closure: it is exhaustive over identifiers and
best-effort over meaning, and the semantic reviewer judges whether its mappings and
`NO_NORMATIVE_EFFECT` reasons are honest.

---

## `20-prd.md`

Owns:

> The living product contract discovery continuously maintains for product closure.

Should answer:

- what problem exists?
- what must become true?
- what is explicitly not required?
- what invariants must hold?
- what behaviors constitute acceptance?

Its frontmatter includes `derived_from`, binding the exact `10-decisions.md` version and SHA-256
the PRD was reconciled against. It must not become an implementation plan.

---

## `20-prd.html`

Owns:

> A mandatory generated projection of `20-prd.md` for cold-read review.

It is regenerated whenever the PRD changes and must declare the exact current Markdown source path,
source SHA-256, and renderer version before product closure can pass. The controller verifies this
metadata binding without re-rendering, so “current” does not claim byte-for-byte body recomputation
during verification. It is never authoritative and never contributes its own acceptance hash.

---

## `30-system-design.md`

Owns:

> System-observable commitments: responsibilities, seams, authoritative data ownership,
> cross-module/external contracts, target schema/protocol, end-to-end lifecycle and
> failure/recovery, compatibility, trust, security, and operations.

The decision boundary is the reliance horizon. A choice belongs here when changing it requires a
caller, peer, or operator to adjust, or changes an accepted guarantee. It should remain
architecture-level rather than file/class-level. Composite decisions record the invariant here and
leave its local realization to Program Design.

Its admission/provenance applicability test reads the effective selected stages and chooses exactly
one binding:

- exact accepted `20-prd.md` version/hash when Product Closure is selected;
- exact accepted/frozen Stage 0 intake and effective configuration when Product Closure is
  `NOT_REQUIRED`, using `control.json.base_run_sha256`, `effective_config_hash`, and
  `effective_config_revision`.

The omitted-Product-Closure branch creates no PRD or approval. A change to the bound source makes
accepted System Design stale and transitively stales any dependent Program Design in the same
logical downstream transition.

In the D-082 repair state only, the stale accepted candidate remains at this canonical path as
non-current provenance until version `N+1` replaces it. N+1 must have a different content hash and
the same still-current source binding, and must pass fresh mechanical checks, fresh semantic
review/classification when configured, and the unchanged configured authority. Every repair
replacement also has a hash-bound System Design evidence envelope whose `repair_context` carries the
complete validated contradiction finding, immediate superseded acceptance, and original
contradiction reference/hash.
For direct `HUMAN`, its semantic/materiality fields are null; it grants no authority, and human
approval remains the acceptance authority. This conditional repair evidence is not a normal-path
review requirement and does not widen the acceptance schema. It records one immediate predecessor,
not a recursive chain or history.

---

## `30-system-design.html`

Owns:

> A mandatory generated visual board when System Design participation is `co_design`.

`30-system-design.md` remains canonical. The HTML is deterministic, self-contained, and
non-authoritative; it embeds the exact Markdown source path, source SHA-256, and renderer version.
It provides precise current/proposed topology, seam/ownership, interface/contract, end-to-end
sequence or data-flow, applicable schema/protocol delta, failure/recovery, open-decision, and
rejected alternatives views. A view that does not apply states why rather than disappearing or being
replaced with decorative imagery.

Stable labels connect board views to chat feedback. Generated chat images and snapshots are
ephemeral projections. Neither they nor the HTML bytes receive an independent acceptance hash or
authority.

---

## `40-program-design.md`

Owns:

> Codebase-local realization inside the exact accepted System Design seams when that stage is selected,
> or inside the accepted/frozen applicable upstream source on a direct path.

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

and language-level signatures, internal state mutation, call chains, locking/concurrency/lifetime
mechanics, migration implementation order, and test seams.

It is provisional while paired drafting pressure-tests System Design. Before acceptance, its
applicability test reads the run's actual selected stages and chooses exactly one upstream binding:

- exact accepted `30-system-design.md` version/hash when System Design is selected;
- exact accepted `20-prd.md` version/hash when System Design is `NOT_REQUIRED` and product closure
  is selected;
- exact accepted/frozen Stage 0 intake and effective configuration when both upstream semantic
  boundaries are `NOT_REQUIRED`, using `control.json.base_run_sha256`, `effective_config_hash`, and
  `effective_config_revision`.

The direct-admission branch does not manufacture an approval or require a nonexistent PRD. Tickets
compiled from direct Program Design cite the accepted Program Design and its frozen Stage 0 binding;
they omit references to nonexistent PRD or System Design artifacts. Program Design has a distinct
judge and outcome; there is no joint design-bundle verdict. An accepted System Design change makes it
stale. A finding that requires changing a system commitment returns `DESIGN_BLOCKED` upstream rather
than being approved inside Stage 4.

For the one D-082 path, that return begins before candidate readiness: pending Program Design has
null acceptance, and `reviews/program-design-upstream-block-v1.json` independently confirms whether
the exact accepted System Design and exact frozen repository evidence prove that Program Design
cannot faithfully realize the commitment without changing it. Producer text alone cannot invalidate
the upstream acceptance. After System Design N+1 is accepted, this same Program Design candidate may
remain version 1, but its bytes and fresh review must bind N+1 before acceptance.

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

Evidence is descriptive; the PRD and designs are normative.

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
  applicable_upstream:
    - <path-to-applicable-accepted-source>

validation:
  - dotnet test --filter JobCancellation
  - dotnet test

review:
  contract: required
  design: required
---
```

The compiler replaces the placeholder with one entry for each applicable accepted source on the
selected path. It never emits the placeholder itself. Product Closure, System Design, and Program
Design entries appear only when those boundaries are selected. A direct Program Design path lists
the accepted Program Design and its frozen Stage 0 binding, not nonexistent upstream artifacts. A
`trivial` path with no semantic producer has one ticket and therefore one one-node graph; its sole
planning source is the frozen Stage 0 intake/effective configuration, plus the target repository
baseline. It neither requires nor manufactures a PRD, System Design, or Program Design artifact.

The complete set of ticket files plus dependency relationships forms the **ticket-graph candidate**.
Before execution, the downstream planning controller records an acceptance binding over the exact
graph version and SHA-256, its applicable accepted upstream sources, and the frozen baseline of each
target repository. This is an acceptance of the complete graph, not permission for each ticket to
self-approve. Any bound upstream acceptance or baseline change makes the graph stale. The artifact
model fixes those semantic bindings but does not yet fix whether a future implementation represents
the graph with an index, manifest, canonical serialization, or another deterministic form.

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

The D-082 upstream-block envelope is deliberately separate from those candidate-bound reviews. It
has exactly three verdicts: `CONFIRMED_UPSTREAM_CONTRADICTION`, `NOT_CONFIRMED`, and `UNAVAILABLE`.
Only `CONFIRMED_UPSTREAM_CONTRADICTION` may authorize a state change. Its bound evidence includes the
current planning identity/revision, accepted System Design identity and source binding, ordered
effective repository baselines, the code-cited contradiction, and the smallest required upstream
change. The envelope is evidence for one active episode, not an acceptance or history ledger.

For the discovery product-closure `AGENT_REVIEW` gate, the invoker persists the read-only judge's
structured output as `reviews/product_closure-v<version>.json`. It binds `run`; a `stage` field
whose value is the boundary label `product_closure` and which the controller accepts only when it
equals the report's `boundary`; candidate `version` and SHA-256, `verdict: PASS|BLOCKED`, and an
array of gaps; each gap includes a stable
code, artifact, problem, and resume stage/action. A PASS envelope has no gaps. The controller
validates and hashes this envelope but never asks it to modify the artifact or state. V1 does not
add authenticated reviewer identities or signatures: the invoker must obtain the envelope from
a fresh read-only context, while the controller enforces only schema and current run/version/hash
binding. After acceptance, those exact review bytes remain required at the canonical run-relative
path and their hash is rechecked with the accepted PRD/decision provenance. This limitation is
explicit rather than implying cryptographic independence.

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
