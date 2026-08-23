# Architecture

This directory is the canonical architecture working set for Atlas.

The numbered documents are authoritative. `rolling-monolith.md` is generated from those documents for portable reading/retrieval and should not be edited independently.

## Current baseline

**v0.12** defines Stage 5 ticket graphs as ordered vertical tracer slices: each non-enabling ticket
carries observable behavior across every boundary that behavior requires, is independently
verifiable, and preserves the applicable selected-path sources. Enabling tickets must justify why an imminent
vertical consumer cannot contain them, and the first frontier validates important risky seams early.
This adds no graph schema, compiler, controller transition, skill, or execution runtime. It builds on
v0.11's human replanning authority boundary.

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
