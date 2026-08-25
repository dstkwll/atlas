# 17 — Agent Roles, Rosters, Model Policy, and Outcome Telemetry

**Added in:** v0.3  
**Purpose:** Define how reasoning roles are packaged, how concrete model/harness workers staff those roles, how task shape influences routing, and how the factory collects enough evidence to improve staffing decisions without automatically changing policy.

---

## 1. Core separation

Do not overload one configuration object with responsibility, permissions, model identity, retries, and cost posture.

Keep these concepts distinct:

```text
ROLE PACKAGE
"What is this worker responsible for and allowed to do?"

TASK SHAPE
"What kind of cognitive work is this invocation performing?"

WORKER CONFIGURATION
"Which model + harness + access route + reasoning setting is actually invoked?"

ROSTER
"Which worker configuration normally staffs each role/task-shape combination?"

EXECUTION POLICY
"How many attempts, reviewers, checkpoints, budgets, etc.?"

PRESET
"Which named combination of workflow/governance/execution/environment/roster should this effort use?"
```

This preserves one stable engineering workflow while allowing model staffing to evolve independently.

---

# 2. Role packages

A **role package** defines behavior and authority independent of whichever model currently staffs it.

Example roles:

- `discovery_researcher`
- `discovery_frontier_critic`
- `spike_worker`
- `system_design_critic`
- `program_design_critic`
- `builder`
- `contract_reviewer`
- `design_reviewer`
- conditional specialist reviewers such as `ops_reviewer`, `security_reviewer`, or `migration_reviewer`

A role package may define:

```yaml
roles:
  builder:
    prompt: roles/builder.md
    skills:
      - tdd
      - repo-conventions
    tools:
      - shell
      - editor
    writes:
      allow:
        - src/**
        - tests/**
      deny:
        - .planning/**
        - .factory/**
        - factory/**
        - scripts/validation/**

  contract_reviewer:
    prompt: roles/contract-reviewer.md
    skills:
      - contract-compliance
    tools:
      - shell_readonly
    writes: []
```

A role package should not contain model-specific prompting quirks unless a real need later earns that mechanism.

Every Atlas-dispatched model invocation is staffed by its **role and task shape**, never by a skill
name or skill identity. A skill may orchestrate multiple Atlas-dispatched model invocations with
cheap factual lookup, frontier synthesis, and an independent semantic review—and the roster may staff
each differently without coupling the reusable procedure to one worker tier. An in-skill action only
affects staffing when it is exposed as a stable task shape; arbitrary action-level routing would
explode the taxonomy and is not part of V1.

Authority-contained helper agents used internally by one harness do not become Atlas role packages,
worker attempts, or roster routes. They remain inside the already-resolved worker attempt and must
satisfy the containment contract in `12-capabilities-and-trust.md`.

---

# 3. Task shapes

A role alone is too coarse for model selection.

The same `builder` role may perform very different kinds of work:

```text
mechanical_edit
bounded_bug_fix
feature_implementation
architectural_refactor
test_hardening
migration
```

Likewise a researcher might perform:

```text
factual_lookup
codebase_investigation
architecture_investigation
benchmark_spike
```

Task shape describes **the cognitive/workload character of this invocation**, not its authority.

## Starting taxonomy

Keep V1 controlled and small. Suggested initial values:

```text
mechanical_edit
bounded_bug_fix
feature_implementation
architectural_refactor
test_hardening
code_review
factual_research
architecture_investigation
spike
migration
```

Do not create dozens of categories before real telemetry proves they matter.

If a task is hard to classify, use the closest stable category and preserve optional tags for later analysis rather than proliferating the primary taxonomy.

---

# 4. Worker configuration identity

Model identity must not be conflated with the harness invoking it.

A worker configuration should be able to answer:

- what trained model was used?
- which harness/agent shell invoked it?
- through which access/billing route?
- what explicit reasoning effort/configuration was requested?
- what local worker configuration version was resolved?

Example:

```yaml
workers:
  frontier_coder:
    model: <model-id>
    harness: codex
    access: chatgpt_oauth
    reasoning: high

  economical_coder:
    model: <model-id>
    harness: opencode
    access: openrouter_api
    reasoning: medium

  frontier_reasoner:
    model: <model-id>
    harness: claude_code
    access: subscription
    reasoning: high
```

Exact provider/model names are configuration, not architecture.

## Identity provenance

The run record should preserve both:

- the **expected/resolved** identity from configuration;
- the **observed/reported** identity when the harness exposes it.

If those disagree, the run should record the mismatch rather than silently crediting results to the expected model.

This is primarily for trustworthy telemetry, not runtime gate authority.

---

# 5. Rosters

A **roster** maps roles and optionally task shapes to worker configurations.

Example:

```yaml
rosters:
  default:
    defaults:
      discovery_researcher: frontier_reasoner
      discovery_frontier_critic: frontier_reasoner
      spike_worker: frontier_coder
      builder: standard_coder
      contract_reviewer: frontier_reasoner
      design_reviewer: frontier_reasoner

    assignments:
      builder:
        mechanical_edit: economical_coder
        bounded_bug_fix: standard_coder
        feature_implementation: standard_coder
        architectural_refactor: frontier_coder

      discovery_researcher:
        factual_research: economical_reasoner
        architecture_investigation: frontier_reasoner
```

A named roster represents a staffing posture, not an assurance level.

High assurance may require additional reviews or HITL gates without changing the model roster at all.

---

# 6. Routing precedence

Recommended resolution order:

```text
explicit invocation override
        ↓
explicit run/ticket worker override
        ↓
roster role + task-shape assignment
        ↓
roster role default
        ↓
global worker fallback
```

Presets may select a roster, but they should not erase the independent meaning of the roster dimension.

All resolved choices are frozen into the run manifest.

---

# 7. V1 selection policy

V1 model selection is configuration-driven.

The system may **recommend** a worker/roster based on known task shape, risk, or accumulated telemetry, but it does not autonomously promote a model into a new default lane.

The same conservative policy used for workflow/governance classification applies here:

> **Evidence may recommend a roster change. Humans approve roster changes initially.**

No automatic model promotion is required for the factory to function.

---

# 8. Builder/reviewer diversity

Independence begins with fresh context and independent evaluation; model diversity is a staffing
constraint, not authority.

V1 policy:

```yaml
review_independence:
  fresh_context: required
  different_worker_config: preferred
  different_model_family: conditional
```

A different worker configuration is preferred where available, but ordinary review remains valid
when a fresh reviewer uses the same strong model. A different model family is required for a model
critic or reviewer under `high_assurance`, and after repeated review failures or evidence of
correlated blind spots. Outside those conditions it is optional: do not multiply model calls or
force vendor diversity for its own sake.

The family requirement changes staffing only. Model diversity grants no authority, never resolves a
gate, and never substitutes for configured human acceptance. If the required family separation
cannot be established, record that the diverse model pass is unavailable rather than claiming it
occurred; governance decides the legal next step.

---

# 9. Outcome telemetry

Every agent invocation should produce enough structured metadata to evaluate the staffing policy later.

Minimum useful record:

```yaml
run_id: ...
ticket_id: ...
role: builder
task_shape: bounded_bug_fix

worker:
  config_id: standard_coder
  model_expected: ...
  model_observed: ...
  harness: ...
  access: ...
  reasoning: high

attempt:
  number: 1
  outcome: failed_validation

performance:
  duration_ms: ...
  input_tokens: ...
  output_tokens: ...
  estimated_cost: ...

validation:
  deterministic_pass: false
  contract_review: not_run
  design_review: not_run

failure_class:
  - test_failure
```

Do not make token/cost availability mandatory when a harness cannot report it. Preserve `unknown` rather than guessing.

---

# 10. Metrics that matter

For each meaningful `role × task_shape × worker configuration` slice, calculate when enough samples exist:

- tasks completed;
- attempts;
- **first-try pass rate**;
- eventual pass rate;
- average/median repair attempts;
- deterministic-validation failure rate;
- contract-review rejection rate;
- design-review rejection rate;
- `DESIGN_BLOCKED` rate;
- median duration to accepted outcome;
- median tokens/cost where available;
- last-seen timestamp;
- model/harness identity drift warnings.

## Why first-try pass rate matters

Final pass rate alone can hide expensive repair dependence.

Example:

```text
Worker A
first-try: 94%
final:     98%

Worker B
first-try: 63%
final:     98%
```

Both eventually succeed at the same rate, but Worker B may consume substantially more repair time/tokens and may impose more reviewer churn.

The first-try/final gap is therefore a useful measure of **repair-lane dependency**.

---

# 11. Human-reviewed roster recommendations

Telemetry should generate reviewable recommendations rather than edit config.

Example:

```text
ROSTER REVIEW

builder × mechanical_edit

Current: standard_coder
  42 tasks
  98% first-try
  100% final
  $0.39 median accepted cost

Candidate: economical_coder
  37 tasks
  95% first-try
  100% final
  $0.07 median accepted cost

Recommendation:
Consider promoting economical_coder for builder × mechanical_edit.

No configuration changed.
```

The human can then update a version-controlled roster deliberately.

---

# 12. Review cadence

Do not inspect the scoreboard after every few invocations.

Prefer a combination of evidence volume and elapsed time, for example:

```text
roster review is due when

≥ N new comparable executions exist since last review

OR

review interval elapsed and meaningful new evidence exists
```

`N` is deliberately not frozen in architecture. A starting operational value such as 20–30 comparable executions can be tested later.

The same review may surface regressions:

```text
Worker X first-try success on architectural_refactor
fell materially across the most recent evidence window.
```

Again: surface evidence; do not silently reroute production work.

---

# 13. Model/harness changes and evidence freshness

Historical results are not timeless truth.

A model version, harness behavior, reasoning default, tool policy, or access route can change.

Therefore:

- preserve exact identity/version information where available;
- mark identity uncertainty rather than backfilling assumptions;
- support recency windows in future reports;
- avoid treating stale historical evidence as permanently authoritative.

Do not build a complex decay algorithm in V1. Preserve the data needed to reason about freshness later.

---

# 14. Model-specific steering — documented future capability

Some models/harnesses may eventually show persistent, repeatable quirks that benefit from worker-specific steering.

Possible future lifecycle:

```text
observation
  ↓
candidate steering rule
  ↓
validated / confirmed
  ↓
active
  ↓
model/harness change
  ↓
stale / reverify

or

refuted
```

Possible distinction:

```text
DRIVER GUIDANCE
Advice to the controller/orchestrator about how to present work to a worker.

WORKER GUIDANCE
Instruction injected into the worker itself.
```

**V1 decision:** do not build steering machinery.

At most, preserve optional human notes per worker configuration. Promote this subsystem only after repeated evidence demonstrates that generic role packages are insufficient.

---

# 15. Validator preflight

Before spending a worker attempt, the factory should be able to prove that ticket validation commands are sane against the baseline when their expected baseline behavior is knowable.

Example:

```text
NEW behavior validator
baseline result expected: FAIL

UNCHANGED regression validator
baseline result expected: PASS
```

If the baseline result contradicts the declared expectation, the ticket/validator should be corrected before implementation begins.

This prevents agent repair loops from burning attempts against an impossible or already-satisfied contract.

Suggested ticket metadata:

```yaml
validation:
  - command: dotnet test --filter NewCancellationBehavior
    baseline_expectation: fail

  - command: dotnet test --filter ExistingSchedulerRegression
    baseline_expectation: pass
```

Not every validator requires a baseline expectation. Use it where the semantics are meaningful and deterministic.

---

# 16. Relationship to execution truth

Worker telemetry is evidence, not lifecycle authority.

```text
worker reports success
        ↓
telemetry records worker outcome
        ↓
deterministic validators/review gates execute
        ↓
controller decides legal state transition
```

A high-performing model does not get permission to skip validators or reviews.

Model policy optimizes staffing **inside** the existing governance and execution contracts; it does not supersede them.

---

# 17. V1 scope

Implement only what the initial factory needs:

1. stable role package identifiers;
2. small task-shape taxonomy;
3. concrete worker configurations separating model/harness/reasoning/access identity;
4. roster role/task-shape mappings;
5. frozen resolved worker config in `run-manifest.json`;
6. per-attempt outcome telemetry;
7. metrics/reporting sufficient for manual roster review;
8. validator baseline preflight where declared by tickets.

Explicitly defer:

- automatic roster promotion;
- catalog-driven model discovery;
- autonomous model bakeoffs;
- sophisticated evidence decay;
- model-specific steering lifecycle;
- universal cross-model reviewer diversity outside the named conditional triggers;
- a dedicated model-benchmarking platform.

---

# 18. Reference implementation provenance

The strongest current reference for this subsystem is **Ringer**:

- repository: `https://github.com/NateBJones-Projects/ringer`
- useful concepts: task-type performance slices, first-try vs eventual pass rate, model/harness/access/reasoning identity separation, raw attempt logs, evidence-based routing recommendations, baseline validator preflight, and optional model-specific steering.

Borrow the **measurement and separation principles**, not Ringer's exact promotion thresholds or its swarm-first product architecture.

See `15-reference-implementation-borrow-map.md` for implementation-time file pointers and disposition.

---

# North-star rule

> **Use the least expensive worker configuration that accumulated evidence shows is adequate for a particular role and task shape—but keep the deterministic contract, review policy, and human governance unchanged, and require a human to approve staffing-policy changes until the system earns greater autonomy.**
