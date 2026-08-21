# Run file

`run.yaml` is the immutable Stage 0 snapshot. Later skills read it; none edits it.

```yaml
version: 1
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
stages: [discovery, program_design, tickets, execute, final_review, pr]
governance: standard
gates:
  discovery:
    authority: HUMAN
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
    baseline: <commit SHA>
overrides:
  - path: <selected field path>
    from: <recommended value>
    to: <accepted value>
    reason: <why the recommendation was overridden>
```

## Field rules

- `version` is `1` for this candidate schema.
- `run` and `run_path` both carry the accepted feature slug; the path is relative to the configured planning root.
- `opened` records the intake acceptance date.
- `goal` records the accepted fuzzy goal.
- `planning_root` records the configuration `source`, the resolved `mode`, and a portable `path` form. Repository-relative roots record the configured relative value (`.planning` by default); external roots record `.` because the file already lives beneath that root. It never copies a machine-specific absolute path.
- `recommendation` records workflow, governance, execution policy, environment policy, roster, the complete recommended gate map, and structured evidence before overrides.
- `workflow` records the accepted workflow depth; `stages` records its resolved ordered stages beginning with the selected earliest producer. Discovery is present only when selected and is first when present.
- `governance` records the accepted posture; `gates` records the fully resolved policy for every selected stage and every run-relevant conditionally reachable route. Every entry has `authority`. Valid authorities are `AUTO`, `AGENT_REVIEW`, `HUMAN`, `CONDITIONAL`, and `HUMAN_IF_CHANGED`. When discovery is selected, its product-closure boundary specifically requires `AGENT_REVIEW` or `HUMAN`; `AUTO` is unavailable because that boundary includes semantic acceptance. When discovery is omitted, omit its gate policy too. The explicit map wins over later changes to global profiles.
- A conditionally reachable route omitted from `stages` records `activation.when` separately from gate review policy. This remains immutable policy in `run.yaml`; it does not create mutable gate state in the Stage 0–2 `control.json`, which owns the discovery boundary only when selected. If discovery is omitted, the controller creates no mutable gates and starts at the actual first selected phase. The later-stage controller that owns the route may materialize `NOT_REQUIRED` and reachable states when that capability is implemented.
- A `CONDITIONAL` entry also records ordered `conditions`, the authority produced by each match, and `otherwise` authority. A `HUMAN_IF_CHANGED` entry records explicit `material_dimensions` and the `otherwise` authority used when none changed. Never write either authority without those operands: a label that requires later profile interpretation is not a resolved snapshot.

Use these exact shapes when either special authority is selected:

```yaml
gates:
  tickets:
    authority: CONDITIONAL
    conditions:
      - when: <structured predicate over run or artifact state>
        then: HUMAN
    otherwise: AGENT_REVIEW
  program_design:
    authority: HUMAN_IF_CHANGED
    material_dimensions:
      - <named semantic dimension>
    otherwise: AGENT_REVIEW
```

`when` is data for deterministic policy evaluation, not an instruction to an artifact-producing skill. `then` and `otherwise` each use the same gate-authority vocabulary.
- `execution_policy`, `environment_policy`, and `roster` record the accepted resolved choices.
- `risk` records all eight classified dimensions used to justify the recommendation.
- `repos` records one `repository` plus `baseline` pair for every repository known to be affected at intake.
- `overrides` records each accepted value that differs from the recommendation as `path`, `from`, `to`, and `reason`. It is `[]` when the recommendation was accepted unchanged.

Internal artifact links are root-relative or run-relative. `run.yaml` never copies an external absolute planning-root path into the artifact.
