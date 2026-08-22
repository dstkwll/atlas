# 09 — Reference Configuration

Most of this document is intentionally illustrative rather than a frozen schema. It tests how **workflow, governance, execution, environment, and roster** remain separate dimensions, with optional presets for convenience.

Two interfaces are stable in V1 because planning skills now consume them:

```yaml
artifacts:
  planning_root: .planning

repositories:
  bindings:
    "stable-repository-id": /absolute/path/to/local-git-source
```

`artifacts.planning_root` is a supported configuration key. Its value remains configurable per machine:

- a repository-relative path, resolved from the repository root;
- or an absolute path / already-usable local checkout of a planning repository.

The default is `.planning`. Changing the key or its resolution semantics requires an explicit version or migration rather than an illustrative edit.

`repositories.bindings` is the second supported machine-local interface. It maps each stable
repository identity to exactly one absolute path naming an already-usable local Git repository or
object source. The path never enters portable artifacts. A binding is established once with explicit
confirmation and then reused; remote URLs may suggest a candidate but never silently create or
change a binding. Resolution is read-only and does not clone, fetch, authenticate, checkout,
materialize a worktree, initialize submodules, or hydrate Git LFS content.

Bindings are environment routing, not resolved run policy. `run.yaml` and `effective_config_hash`
exclude `repositories.bindings`; each repository-inspection/check/acceptance attempt reads the
current confirmed machine binding and still requires the exact full portable baseline commit/tree.

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
      - tickets
      - execute
      - final_review
      - pr

  normal:
    stages:
      - discovery
      - program_design
      - tickets
      - execute
      - final_review
      - pr

  architectural:
    stages:
      - discovery
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
      - system_design
      - program_design
      - tickets
      - execute
      - final_review
      - pr

design:
  system_design:
    participation: agent_led        # intake prompts agent_led | co_design; this is the default
    prompt_at_intake: true
    classifier_controls_participation: false
    co_design_board: 30-system-design.html

governance:
  exploratory:
    gates:
      discovery: AGENT_REVIEW
      system_design: AGENT_REVIEW
      program_design: AGENT_REVIEW
      tickets: AGENT_REVIEW
      tracer: AUTO
      final_pr: HUMAN

  standard:
    gates:
      discovery: HUMAN
      system_design: HUMAN_IF_CHANGED
      program_design: AGENT_REVIEW
      tickets: AGENT_REVIEW
      tracer: CONDITIONAL
      final_pr: HUMAN

  high_assurance:
    gates:
      discovery: HUMAN
      system_design: HUMAN
      program_design: HUMAN
      tickets: HUMAN
      tracer: HUMAN
      final_pr: HUMAN

  autonomous:
    gates:
      discovery: AGENT_REVIEW
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
    baseline: exact_repository_current_system
    classifier: independent_read_only
    no_material_change: AGENT_REVIEW
    any_material_change: HUMAN
    baseline_or_classification_unavailable: HUMAN
    persist_bindings_and_evidence: true
    stale_on_baseline_or_candidate_change: true
    material_dimensions:
      - responsibility_or_system_seam
      - authoritative_data_owner
      - cross_module_or_external_contract
      - target_schema_or_protocol
      - end_to_end_lifecycle_failure_recovery
      - compatibility_guarantee
      - trust_security_or_operational_commitment

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
