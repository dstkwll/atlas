# Architecture

This directory is the canonical architecture working set for Atlas.

The numbered documents are authoritative. `rolling-monolith.md` is generated from those documents for portable reading/retrieval and should not be edited independently.

## Current baseline

**v0.14** makes the Stage 5 → execution boundary implementable without adding execution machinery. One
planning effort may span multiple target repositories under one accepted cross-repository ticket
graph; execution instantiates one independent repository-scoped workspace, runtime record, and
accepted chain per target repository. Logical workcells remain per-ticket; one small closed runtime
authority admits one active ticket per repository-scoped run; waits and proof receipts bind observable
evidence; helper agents cannot acquire Atlas ownership; repository-slice promotion is separate from
ticket acceptance; and required evidence is harvested before destructive cleanup. Sandcastle remains
a proof-of-fit substrate candidate, not a dependency or authority. The unnumbered `v2-horizon.md`
preserves deferred triggers and is excluded from canonical generation.

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
