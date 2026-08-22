# Architecture

This directory is the canonical architecture working set for Atlas.

The numbered documents are authoritative. `rolling-monolith.md` is generated from those documents for portable reading/retrieval and should not be edited independently.

## Current baseline

**v0.10** gives D-080's downstream planning controller one bounded repair path when pending Program
Design proves an exact-code contradiction with its selected accepted System Design. Independent
confirmation starts a durable four-attempt invalidation-and-replacement episode; System Design N+1
and resumed Program Design receive fresh acceptance without rollback, user routing, or a generalized
staleness mechanism. It builds on v0.9's exact portable repository grounding.

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
