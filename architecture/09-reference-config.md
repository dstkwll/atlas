# 09 — Reference Configuration

Most of this document is intentionally illustrative rather than a frozen schema. It tests how **workflow, governance, execution, environment, and roster** remain separate dimensions, with optional presets for convenience.

One interface is stable in V1 because the planning skills already consume it:

```yaml
artifacts:
  planning_root: .planning
```

`artifacts.planning_root` is a supported configuration key. Its value remains configurable per machine:

- a repository-relative path, resolved from the repository root;
- or an absolute path / already-usable local checkout of a planning repository.

The default is `.planning`. Changing the key or its resolution semantics requires an explicit version or migration rather than an illustrative edit.

The layout beneath a run is fixed by `03-artifact-model.md`. In particular, evidence lives at `<run>/evidence/` and spikes at `<run>/spikes/`; they are not separate configuration knobs in V1. Other keys below remain illustrative until a real consumer earns and stabilizes them.

```yaml
version: 0.2

artifacts:
  planning_root: .planning        # stable V1 interface; value remains configurable
  permanent_docs: docs
  adr_path: docs/adr

factory:
  state_root: .factory/runs
  worktree_root: .factory/worktrees

validation:
  repo_default:
    - dotnet build
    - dotnet test

workflows:
  trivial:
    stages:
      - ticket
      - execute
      - final_review
      - pr

  normal:
    stages:
      - discovery
      - spec
      - program_design
      - tickets
      - execute
      - final_review
      - pr

  architectural:
    stages:
      - discovery
      - spec
      - system_design
      - program_design
      - tickets
      - execute
      - final_review
      - pr

  fog_of_war:
    stages:
      - wayfinder
      - discovery
      - spec
      - system_design
      - program_design
      - tickets
      - execute
      - final_review
      - pr

governance:
  exploratory:
    gates:
      spec: AUTO
      system_design: AUTO
      program_design: AGENT_REVIEW
      tickets: AUTO
      tracer: AUTO
      final_pr: HUMAN

  standard:
    gates:
      spec: HUMAN
      system_design: HUMAN_IF_CHANGED
      program_design: HUMAN
      tickets: AGENT_REVIEW
      tracer: CONDITIONAL
      final_pr: HUMAN

  high_assurance:
    gates:
      spec: HUMAN
      system_design: HUMAN
      program_design: HUMAN
      tickets: HUMAN
      tracer: HUMAN
      final_pr: HUMAN

  autonomous:
    gates:
      spec: AGENT_REVIEW
      system_design: AGENT_REVIEW
      program_design: AGENT_REVIEW
      tickets: AGENT_REVIEW
      tracer: AUTO
      final_pr: HUMAN

execution_policies:
  fast:
    max_repair_attempts: 2
    max_parallel_tickets: 1
    reviews:
      contract: required
      design: conditional
      ops: conditional
      security: conditional

  conservative:
    max_repair_attempts: 3
    max_parallel_tickets: 1
    reviews:
      contract: required
      design: required
      ops: conditional
      security: conditional
      migration: conditional

  # Future policy after sequential V1 proves reliable.
  parallel:
    maturity: deferred
    max_parallel_tickets: 2

environment_policies:
  local_worktree:
    maturity: v1
    type: local_worktree
    retain_on_failure: true

  # Documentation-only examples. Do not implement until a real need pays
  # for the second runtime and therefore the provider seam.
  isolated_container:
    maturity: deferred

  remote_vm:
    maturity: deferred

rosters:
  default:
    discovery:
      class: reasoning
    design:
      class: reasoning
    builder:
      class: coding
    contract_reviewer:
      class: reasoning
    design_reviewer:
      class: reasoning

presets:
  everyday_change:
    workflow: normal
    governance: standard
    execution_policy: conservative
    environment_policy: local_worktree
    roster: default

  important_refactor:
    workflow: architectural
    governance: high_assurance
    execution_policy: conservative
    environment_policy: local_worktree
    roster: default

routing:
  classifier_mode: recommend_only

  # These are recommendation/minimum-policy ideas, not silent V1 routing.
  recommendation_rules:
    - when:
        security_sensitive: true
      recommend_governance: high_assurance

    - when:
        architecture_change: true
        scope: high
      recommend_governance: high_assurance

human_if_changed:
  system_design:
    material_dimensions:
      - component_boundary
      - data_ownership
      - external_dependency
      - public_contract
      - schema
      - protocol
      - failure_semantics
      - cross_layer_dependency

specialty_review_triggers:
  ops:
    when_any:
      - network_io_changed
      - database_io_changed
      - file_io_changed
      - queue_behavior_changed
      - subprocess_behavior_changed

  security:
    when_any:
      - authentication_changed
      - authorization_changed
      - trust_boundary_changed
      - untrusted_input_changed
      - secret_handling_changed

pr:
  create: draft
  push_branch: true
  merge: human_only
```

## Configuration design notes

### Keep each dimension small

Start with a few meaningful workflow/governance/execution choices. Do not create a combinatorial catalog of named presets.

### Explicit overrides are useful, but visible

Example:

```text
factory start "goal" \
  --workflow architectural \
  --governance standard \
  --execution conservative \
  --override gate.program_design=AGENT_REVIEW
```

The resolved choice and override should be captured in the feature's `run.yaml` and the actual execution's immutable `run-manifest.json`.

### Policy should be inspectable before execution

A future command such as:

```text
factory explain-policy
```

could render:

- recommended/selected workflow;
- governance gates;
- execution policy;
- environment choice;
- roster;
- conditional/specialty reviewers;
- explicit overrides.

This is useful, but the CLI command itself is **not** a V1 requirement unless real usage demonstrates the need.
