# Run file

`run.yaml` is the immutable Stage 0 snapshot. Later skills read it; none edits it.

```yaml
version: 2
run: <feature-slug>
opened: <YYYY-MM-DD>
goal: <the accepted fuzzy goal, verbatim enough to recognize>
planning_root:
  source: artifacts.planning_root
  mode: repository-relative      # repository-relative | external
  path: "<configured relative path>" # configured value for repository-relative; . for external
run_path: <feature-slug>
recommendation:
  workflow: normal
  governance: standard
  execution_policy: conservative
  environment_policy: local_worktree
  roster: default
  gates: <complete recommended gate map using the same shape as gates below>
  reasons:
    - dimension: workflow
      evidence: <risk evidence supporting the recommendation>
workflow: normal
stages: [discovery, system_design, program_design, tickets, execute, final_review, pr]
system_design_participation: agent_led  # agent_led | co_design when system_design is selected; otherwise null
governance: standard
gates:
  discovery:
    authority: HUMAN
  system_design:
    authority: HUMAN_IF_CHANGED
    material_dimensions:
      - responsibilities_and_system_seams
      - authoritative_data_ownership
      - cross_module_external_contracts_and_dependencies
      - target_schema_protocol
      - end_to_end_lifecycle_failure_recovery
      - compatibility_guarantees
      - trust_security_operational_commitments
    otherwise: AGENT_REVIEW
  program_design:
    authority: HUMAN
  tickets:
    authority: AGENT_REVIEW
  tracer:
    activation:
      when: <persisted failure evidence that makes the tracer route reachable>
    authority: CONDITIONAL
    conditions:
      - when: <persisted condition that escalates tracer review>
        then: HUMAN
    otherwise: AGENT_REVIEW
  final_pr:
    authority: HUMAN
execution_policy: conservative
environment_policy: local_worktree
roster: default
risk:
  scope: medium
  reversibility: medium
  architecture_change: false
  schema_change: false
  public_contract_change: false
  security_sensitive: false
  operational_impact: low
  testability: high
repos:
  - repository: <stable repository identity>
    baseline: <full canonical commit object ID>
overrides:
  - path: <selected field path>
    from: <recommended value>
    to: <accepted value>
    reason: <why the recommendation was overridden>
```

## Field rules

- `version` is `2` for new runs. Version-1 runs remain valid for their existing Stage 0–2 behavior, but cannot initialize selected downstream System Design because they lack explicit participation provenance.
- `run` and `run_path` both carry the accepted feature slug; the path is relative to the configured planning root. The slug uses only lowercase letters, digits, and single hyphens (`[a-z0-9]+(?:-[a-z0-9]+)*`); the controller rejects path separators, absolute paths, dot segments, leading/trailing hyphens, and repeated hyphens.
- `opened` records the intake acceptance date.
- `goal` records the accepted fuzzy goal.
- `planning_root` records the configuration `source`, the resolved `mode`, and a portable `path` form. Repository-relative roots record the configured relative value (`.planning` by default); external roots record `.` because the file already lives beneath that root. It never copies a machine-specific absolute path.
- `recommendation` records workflow, governance, execution policy, environment policy, roster, the complete recommended gate map, and structured evidence before overrides.
- `workflow` records the accepted workflow depth; `stages` records its resolved ordered stages beginning with the selected earliest producer. Discovery is present only when selected and is first when present.
- `system_design_participation` is exactly the user's explicit `agent_led` or `co_design` choice when `system_design` is selected and is `null` otherwise. Stage 0 presents both choices neutrally exactly once; the classifier neither recommends nor chooses the value. Participation affects collaboration only, never acceptance authority. Downstream System Design reads the frozen value and never asks again. Program Design and tickets have no participation mode.
- `governance` records the accepted posture; `gates` records the fully resolved policy for every selected stage and every run-relevant conditionally reachable route. Every entry has `authority`. General vocabulary is `AUTO`, `AGENT_REVIEW`, `HUMAN`, `CONDITIONAL`, and `HUMAN_IF_CHANGED`, but each boundary narrows it. Discovery allows only `AGENT_REVIEW` or `HUMAN`. System Design allows `HUMAN`, `AGENT_REVIEW`, or `HUMAN_IF_CHANGED`, never `AUTO`; `HUMAN_IF_CHANGED` requires `otherwise: AGENT_REVIEW` and exactly these seven `material_dimensions` in this order: `responsibilities_and_system_seams`, `authoritative_data_ownership`, `cross_module_external_contracts_and_dependencies`, `target_schema_protocol`, `end_to_end_lifecycle_failure_recovery`, `compatibility_guarantees`, `trust_security_operational_commitments`. Program Design allows only `HUMAN` or `AGENT_REVIEW`. Tickets allows only `HUMAN` or `AGENT_REVIEW` in V1; it has no `AUTO` or `CONDITIONAL` branch. When a stage is omitted, omit its gate policy too. The explicit map wins over later changes to global profiles.
- A conditionally reachable route omitted from `stages` records `activation.when` separately from gate review policy. This remains immutable policy in `run.yaml`; it does not create mutable gate state in the Stage 0–2 `control.json`, which owns the discovery boundary only when selected. If discovery is omitted, the controller creates no mutable gates and starts at the actual first selected phase. The later-stage controller that owns the route may materialize `NOT_REQUIRED` and reachable states when that capability is implemented.
- A `CONDITIONAL` entry also records ordered `conditions`, the authority produced by each match, and `otherwise` authority. A `HUMAN_IF_CHANGED` entry records the exact ordered seven System Design identifiers above and the `otherwise` authority used when none changed. Never write either authority without those operands: a label that requires later profile interpretation is not a resolved snapshot.

Use this exact shape when `HUMAN_IF_CHANGED` is selected:

```yaml
gates:
  system_design:
    authority: HUMAN_IF_CHANGED
    material_dimensions:
      - responsibilities_and_system_seams
      - authoritative_data_ownership
      - cross_module_external_contracts_and_dependencies
      - target_schema_protocol
      - end_to_end_lifecycle_failure_recovery
      - compatibility_guarantees
      - trust_security_operational_commitments
    otherwise: AGENT_REVIEW
```

`when` is data for deterministic policy evaluation, not an instruction to an artifact-producing skill. `then` and `otherwise` each use the same gate-authority vocabulary.
- `execution_policy`, `environment_policy`, and `roster` record the accepted resolved choices.
- `risk` records all eight classified dimensions used to justify the recommendation.
- `repos` records one `repository` plus `baseline` pair for every repository known to be affected at intake. `baseline` is the full canonical lowercase hexadecimal object ID of a commit, resolved and proved locally before acceptance; it is never a branch, tag, `HEAD`, or abbreviated object ID.
- `overrides` records each accepted value that differs from the recommendation as `path`, `from`, `to`, and `reason`. It is `[]` when the recommendation was accepted unchanged.

Internal artifact links are root-relative or run-relative. `run.yaml` never copies an external absolute planning-root path into the artifact.
