# 04 — Control Plane, Policy Dimensions, and Gates

## Why the control plane exists

The control plane prevents autonomy policy from leaking into individual agents/skills.

Without it, one skill might ask for human approval, another might auto-advance, and another might open a PR based on whatever instructions happened to be in its prompt.

The control plane centralizes:

- workflow depth;
- stage admission;
- System Design participation;
- governance / gate authority;
- execution policy;
- environment policy;
- model/harness roster;
- risk/classifier recommendations;
- reviewer requirements;
- retry limits;
- artifact locations;
- state-transition authority.

---

## Configuration dimensions

Keep these dimensions independent even if a named preset resolves several at once.

### `system_design_participation`

Question:

> How does the user collaborate while the System Design candidate is produced?

Values are `agent_led` (default) and `co_design`. This dimension exists only when System Design is
selected, and intake prompts the user with both choices. The classifier does not recommend or select
the participation mode; `co_design` exists only through the user's explicit intake choice.
Participation does not alter artifact semantics, review independence, or the authority resolved from
governance.

### `workflow`

Question:

> How much reasoning/artifact decomposition does this work warrant?

Possible starting values:

- `trivial`
- `normal`
- `architectural`
- `fog_of_war`

Example shapes:

```text
TRIVIAL
Goal → Ticket → Implement → Validate → PR
```

```text
NORMAL
Goal → Discovery + Product Closure → Program Design → Tickets → Factory
```

```text
ARCHITECTURAL
Goal → Discovery + Product Closure → System Design → Program Design → Tickets → Factory
```

```text
FOG_OF_WAR
Goal → Wayfinder / Research / Spikes → stabilize decisions → architecture pipeline
```

### `governance`

Question:

> Who has authority to advance through the selected workflow?

Possible starting postures:

- `exploratory`
- `standard`
- `high_assurance`
- `autonomous`

A security-sensitive small change might be `normal + high_assurance`.
A large personal experiment might be `architectural + autonomous`.

### `execution_policy`

Question:

> How aggressively does the execution factory operate?

Controls things such as:

- repair limits;
- concurrency/parallelism;
- mandatory vs conditional reviewers;
- tracer checkpoints;
- commit strategy;
- timeout/budget behavior.

### `environment_policy`

Question:

> Where/how does execution run and what isolation/retention rules apply?

**V1 default:** `local_worktree`.

Future values can be added only when a concrete runtime earns them.

### `roster`

Question:

> Which model/harness staffs each reasoning role?

Keep this separate from assurance. “High assurance” should not intrinsically mean one specific vendor/model.

### `preset`

A convenience name resolving the above dimensions, for example:

```yaml
preset: important_refactor
```

might resolve to:

```yaml
workflow: architectural
governance: standard
execution_policy: conservative
environment_policy: local_worktree
roster: frontier
```

Do not create combinatorial named profiles for every possible combination.

---

## Stage selection and boundary admission

The selected workflow determines which semantic artifact boundaries are required. It does not grant
approval to artifacts merely because a later starting point is convenient.

Two cases are intentionally distinct:

1. **Boundary not selected:** the artifact is not required by this workflow. Its gate is conceptually
   `NOT_REQUIRED`; no approval is implied or fabricated.
2. **Required artifact already exists:** its production step may be reused, but the artifact must pass
   the same boundary contract and configured authority as a newly produced candidate. Only the
   resulting accepted version/hash binding permits downstream admission.

This keeps “skip work we do not need” separate from “trust work that already exists.” It also keeps
semantic routing orthogonal to later execution-framework selection: Stage 0 chooses which approved
contracts the run needs; Stages 5–7 may later choose how implementation work executes. A library of
execution playbooks is deferred until those stages have a concrete consumer.

---

## Configuration hierarchy

Recommended precedence:

```text
global defaults
    <
repository configuration
    <
selected preset / explicit dimension choices
    <
explicit run overrides
```

Possible files:

```text
~/.factory/config.yaml
<repo>/.factory/config.yaml
<planning-root>/<feature>/run.yaml
<repo>/.factory/runs/<run-id>/run-manifest.json
```

`run.yaml` can preserve the human-visible intake/policy decision for the engineering effort.

`run-manifest.json` is the machine-canonical fully resolved execution snapshot for an actual factory run, including source/planning hashes and exact roster/config versions.

---

## Gate vocabulary

### `AUTO`

Output can advance immediately once deterministic prerequisites are satisfied **only when the
boundary contract declares no semantic acceptance question**. A successful automatic gate is
recorded as `AUTO_PASSED`, never `AGENT_APPROVED`.

Discovery's product-closure boundary requires semantic acceptance in this revision, so its
configured authority is `AGENT_REVIEW` or `HUMAN`, not `AUTO`.

### `AGENT_REVIEW`

A separate reviewer must approve before progression; no human approval required.

### `HUMAN`

Human approval required regardless of whether agent reviews pass.

### `CONDITIONAL`

Policy evaluates structured conditions to determine whether escalation is required.

### `HUMAN_IF_CHANGED`

Human approval is required only if the stage introduces a material change relative to an exact
repository/current-system baseline on one or more stage-specific material dimensions. System Design
uses responsibilities/system seams, authoritative data ownership, cross-module/external contracts,
target schema/protocol, end-to-end lifecycle/failure/recovery, compatibility guarantees, and
trust/security/operational commitments.

An independent read-only classifier compares the exact candidate with that baseline and emits
evidence per dimension. Deterministic policy maps any material dimension to `HUMAN`; no material
dimension maps to `AGENT_REVIEW`. Candidate/baseline identities and hashes plus classification
evidence are persisted. If the baseline or classification cannot be established, the gate fails
closed to `HUMAN`. A baseline or candidate change makes the result stale and requires
reclassification/reapproval. Semantic design boundaries never use raw `AUTO`.

---

## Reviews and gates are different concepts

A review asks:

> Is this good/correct?

A gate asks:

> Who has authority to allow progression?

Example:

```yaml
program_design:
  reviews:
    - program_design_critic
    - testability_critic
  gate:
    authority: HUMAN
```

The human becomes the decision authority rather than the primary bug finder.

### Boundary labels are not state keys

`control.json.phase`, the `gates` map, the `acceptances` map, and every gap's resume stage remain
keyed by the controlled producer name `discovery`. `product_closure` is the semantic label for
discovery's exit boundary: it names the review envelope and human-facing vocabulary, and it never
becomes a phase value, gate key, or acceptance key. This keeps stage-index coherence unchanged
while making the boundary explicit (D-067).

### Stage 0–2 boundary seam

For discovery and its product-closure boundary, keep four responsibilities distinct:

```text
producer completes a candidate
  → read-only boundary judge returns PASS/BLOCKED with all gaps and resume points
  → PASS goes to the configured authority; BLOCKED returns to the producer without mutation
  → deterministic controller records one legal acceptance or explicit HUMAN rejection
```

The producer's completion claim is input, not acceptance. The judge reads only evidence for
that boundary and never edits the candidate or planning state. Objective structure and
cross-reference checks may be deterministic; semantic completeness is judged by a fresh
reviewer under `AGENT_REVIEW`, or by the human under `HUMAN`. The controller validates the
candidate identity/hash, the applicable judge or human authority, and transition legality; it
does not grade prose.

### Stages 3–5 downstream planning seam

Stages 3 through 5 use the same separation of producer, independent read-only judge, configured
authority, and deterministic transition recording, but their state does not belong in the Stage
0–2 `control.json`. One downstream planning controller is the logical mutable authority for their
separate exact candidate/version/hash bindings, distinct outcomes, dependency chain, and staleness
propagation. It records every downstream invalidation directly caused by an upstream state change in
the same logical atomic transition. Its exact storage/schema remains an implementation choice; it
ends at Stage 5 and owns no execution state. v0.8 adds neither a separate compilation controller nor
a generalized router.

Paired drafting does not merge gates. When selected, System Design is accepted first. Program Design
is then bound, rechecked, and finalized against the selected path's applicable source: the accepted
System Design when selected; the accepted PRD when System Design is `NOT_REQUIRED` but product
closure is selected; or the accepted/frozen Stage 0 intake and effective-configuration hashes when
both upstream semantic boundaries are `NOT_REQUIRED`. The downstream judge reads the effective
selected stages, chooses exactly one branch, and never treats `NOT_REQUIRED` as approval. Program
Design requires independent semantic review and never raw `AUTO`; the recommended standard
authority is `AGENT_REVIEW`, with `HUMAN` available under governance/high assurance. A Stage 4
finding that would change a Stage 3 commitment returns `DESIGN_BLOCKED` upstream.

Stage 5 has its own boundary inside that same controller:

```text
execution compiler proposes complete ticket graph
  → independent read-only ticket-graph judge returns PASS/BLOCKED with all gaps
  → PASS goes to the configured tickets authority; BLOCKED returns to compilation
  → downstream planning controller records exact graph/version/hash acceptance
  → execution preflight verifies the accepted binding and currency
```

The Stage 5 judge examines verticality, dependency completeness, validation contracts, repository
targeting, and exact applicable-upstream references. The controller binds the accepted graph to
each applicable accepted upstream source and each target repository baseline. It does not grade the
graph's prose. Execution preflight may reject a missing or stale acceptance, but it cannot create,
record, or manufacture one.

---

## Classifier behavior

Initial behavior:

> **Recommend; do not silently route.**

Classifier should produce structured evidence:

```yaml
risk:
  scope: high
  reversibility: medium
  architecture_change: true
  schema_change: false
  public_contract_change: true
  security_sensitive: false
  operational_impact: medium
  testability: high
```

Then the user accepts or overrides the recommendation.

When System Design is selected, intake separately prompts for `agent_led` or `co_design`; this is an
explicit collaboration preference, not a classifier output. The classifier does not determine or
recommend participation, and the choice does not change gate authority.

An explicit user-selected assurance level should not be silently downgraded. Future policy may automatically raise minimum scrutiny for known high-risk conditions after the system earns that trust.

---

## Stable artifact semantics

Policy can decide whether an artifact is skipped/generated/reviewed/approved.

Policy should **not redefine the artifact's semantic meaning**.

For example, `program-design.md` means the same kind of thing under `exploratory` and `high_assurance`; only whether it is required/reviewed/human-approved changes.

This stability allows agents and deterministic tools to consume artifacts reliably across the system.
