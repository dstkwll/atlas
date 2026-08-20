---
name: to-spec
description: Produce the Stage 2 behavioral contract from accepted discovery without claiming acceptance.
disable-model-invocation: true
---

# To spec

Compile accepted discovery into `<run>/20-spec.md`: externally observable behavior, not implementation design or tickets.

## 1. Bind the accepted source

Read immutable `run.yaml` and authoritative `control.json`; ignore `00-state.md` for legality. Specification must be the current phase. Read `control.json.acceptances.discovery` and verify that current `10-decisions.md` bytes still match its candidate hash.

Write the exact candidate frontmatter from [`references/spec-file.md`](references/spec-file.md). `derived_from` records accepted discovery stage, candidate version, and candidate SHA-256. Compile only the decisions represented by that accepted provenance.

If a behavior-changing decision is missing, route an explicit reopen through:

```shell
python3 tools/atlas_control.py reopen --run <run-directory> --to discovery --reason <persisted-reason>
```

## 2. Write the outside-view contract

Give every obligation a stable identifier and observable acceptance outcome. Account for each live decision as a requirement, prohibition, constraint, invariant, reasoned exclusion, or classified open question. Walk boundary, adjacency, empty, encoding, ordering, precision, idempotency, and concurrency edges.

Do not add files, classes, methods, implementation shape, work items, or tickets. Design stages own those.

## 3. Finish producer work

Obtain a fresh cold read. Resolve defects and blocking questions. Leave `status: draft`; set `gate_ready: true` only when producer work is complete.

Run the read-only mechanical judge:

```shell
python3 tools/atlas_control.py check --run <run-directory>
```

Repair a `BLOCKED` report at its named resume point. A mechanical `PASS` is not semantic acceptance. Route the unchanged candidate to `atlas:control-run`, which consumes configured `AGENT_REVIEW` or `HUMAN` authority and records at most one transition.

## Standing rules

- The candidate contains no approval, approved-copy, receipt, supersedes, or amendment fields.
- The producer never approves its own spec or edits `control.json`.
- Decisions are upstream; design and tickets are downstream.
- Current acceptance provenance lives only in the stage bindings under `control.json.acceptances`.
