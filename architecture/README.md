# Architecture

This directory is the canonical architecture working set for Atlas.

The numbered documents are authoritative. `rolling-monolith.md` is generated from those documents for portable reading/retrieval and should not be edited independently.

## Current baseline

**v0.13** makes D-080's one accepted ticket graph execution-complete. Dependencies preserve real
prerequisite meaning while canonical order carries D-084's risk preference among ready tickets;
external readiness needs observable evidence, and `resume` only wakes revalidation. The trusted
supervisor deterministically derives a non-authoritative worker brief from accepted bindings and
current validated evidence, without an execution-time planner. D-085 adds no graph/brief/runtime
schema, second acceptance layer, monitoring machinery, or execution implementation.

## Change discipline

For material changes:

1. Read the relevant canonical documents.
2. Treat the proposal as a delta.
3. Evaluate it as `EXPLORATION`, `CANDIDATE`, or `CHANGE`.
4. If accepted, update the modular documents surgically.
5. Record decisions/course corrections where appropriate.
6. Regenerate the rolling monolith and run a consistency audit.

## Validate the rolling monolith

Run `python3 tools/check_architecture.py` from the repository root. The validator
checks that `rolling-monolith.md` exactly matches the numbered canonical
architecture documents in filename order, including whitespace and newlines.
