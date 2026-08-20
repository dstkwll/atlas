# 04 — Control Plane, Policy Dimensions, and Gates

## Why the control plane exists

The control plane prevents autonomy policy from leaking into individual agents/skills.

Without it, one skill might ask for human approval, another might auto-advance, and another might open a PR based on whatever instructions happened to be in its prompt.

The control plane centralizes:

- workflow depth;
- stage admission;
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
Goal → Discovery → Spec → Program Design → Tickets → Factory
```

```text
ARCHITECTURAL
Goal → Discovery → Spec → System Design → Program Design → Tickets → Factory
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

Stage 1 discovery and Stage 2 behavioral specification both require semantic acceptance in
this revision, so their configured authority is `AGENT_REVIEW` or `HUMAN`, not `AUTO`.

### `AGENT_REVIEW`

A separate reviewer must approve before progression; no human approval required.

### `HUMAN`

Human approval required regardless of whether agent reviews pass.

### `CONDITIONAL`

Policy evaluates structured conditions to determine whether escalation is required.

### `HUMAN_IF_CHANGED`

Human approval required only if the stage introduces a material change relative to an approved baseline or specified semantic dimensions.

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

### Stage 0–2 boundary seam

For discovery and behavioral specification, keep four responsibilities distinct:

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

An explicit user-selected assurance level should not be silently downgraded. Future policy may automatically raise minimum scrutiny for known high-risk conditions after the system earns that trust.

---

## Stable artifact semantics

Policy can decide whether an artifact is skipped/generated/reviewed/approved.

Policy should **not redefine the artifact's semantic meaning**.

For example, `program-design.md` means the same kind of thing under `exploratory` and `high_assurance`; only whether it is required/reviewed/human-approved changes.

This stability allows agents and deterministic tools to consume artifacts reliably across the system.
