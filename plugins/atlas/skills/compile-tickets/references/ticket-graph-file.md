# Ticket graph candidate

Stage 5 writes one canonical `50-ticket-graph.json` plus one Markdown file per ticket under `tickets/`. Ticket bytes are hashed into the manifest; the manifest SHA-256 is the complete candidate identity recorded by planning control.

## Manifest

```json
{
  "version": 1,
  "run": "feature-slug",
  "status": "draft",
  "gate_ready": true,
  "source_bindings": [
    {
      "kind": "program_design",
      "artifact": "40-program-design.md",
      "version": 1,
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "repository_baselines": [
    {
      "repository": "stable-repository-id",
      "baseline": "0123456789abcdef0123456789abcdef01234567"
    }
  ],
  "preferred_order": ["feature-01"],
  "tracer_ticket": "feature-01",
  "tickets": [
    {
      "id": "feature-01",
      "path": "tickets/feature-01.md",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ]
}
```

Rules:

- Fields are exact. `version` is integer `1`; `status` remains `draft`; `gate_ready` is boolean `true` only when the complete graph is ready for checking.
- `source_bindings` exactly equals the applicable accepted selected-path source list. It may contain `product_closure`, `system_design`, `program_design`, and the discriminated Stage 0 binding only where applicable. Omitted boundaries never appear.
- `repository_baselines` exactly equals effective frozen `run.yaml` repositories in order.
- `preferred_order` contains every ticket identity exactly once and is distinct from dependency truth.
- `tracer_ticket` is `null` when no tracer applies; otherwise it names one `vertical` ticket whose `tracer` field is `true`.
- `tickets` indexes every and only `tickets/*.md` file. Each path is exactly `tickets/<id>.md`; each SHA-256 binds exact file bytes.
- The direct trivial path has exactly one ticket, one manifest entry, and the frozen Stage 0 source binding.

## Ticket file

```markdown
---
id: feature-01
kind: vertical
status: ready
repository: stable-repository-id
blocked_by: []
tracer: true
enabling: null
references:
  - kind: program_design
    sections:
      - Call and data flow
      - Test seams and validation plan
external_prerequisites: []
validators:
  - id: public-behavior
    command: python3 -m unittest tests.test_feature.FeatureTests.test_public_behavior
    success: exit_zero
outcomes:
  - id: public-behavior
    promise: The public behavior works through every required boundary.
    acceptance:
      - The public entry point produces the expected observable result.
    validator_ids:
      - public-behavior
reviews:
  - design
---

# feature-01

## What becomes true

The public behavior works through every required boundary.

## Acceptance

- The public entry point produces the expected observable result.

## Relevant design

- `40-program-design.md#call-and-data-flow`
- `40-program-design.md#test-seams-and-validation-plan`
```

Rules:

- Fields are exact. `id` is a stable lowercase slug. `kind` is `vertical` or `enabling`; planning `status` is exactly `ready` and grants no runtime readiness authority.
- `repository` names one effective frozen target.
- Every `blocked_by` item has exactly `ticket` and nonempty `establishes`. IDs are unique, references exist, and the graph is acyclic with no self-edge.
- A `vertical` ticket has `enabling: null`. An `enabling` ticket has exactly `consumer` and `rationale`; that named vertical consumer must depend on the enabling ticket.
- `references` contains each applicable source kind exactly once. Stage 0 uses `sections: []`; each semantic source lists one or more exact existing `##` headings.
- Each external prerequisite has `id`, `condition`, and `satisfaction`. Satisfaction is either `{kind: command, command: <nonempty>, success: exit_zero}` or `{kind: human_assertion, authority: HUMAN, statement: <nonempty>, provenance: <nonempty>}`.
- Every validator has unique `id`, nonempty `command`, and `success: exit_zero`.
- Every outcome has unique `id`, nonempty `promise`, nonempty observable `acceptance`, and one or more existing `validator_ids`. Reviews never replace these validator bindings.
- `reviews` is a unique subset of `semantic`, `design`, and `quality`.
- Body headings are exactly `What becomes true`, `Acceptance`, and `Relevant design`; the body explains the contract without copying upstream design.
