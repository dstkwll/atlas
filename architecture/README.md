# Architecture

This directory is the canonical architecture working set for Atlas.

The numbered documents are authoritative. `rolling-monolith.md` is generated from those documents for portable reading/retrieval and should not be edited independently.

## Current baseline

**v0.11** defines the authority boundary after D-082's one bounded repair episode cannot converge.
The failed run remains durably `BLOCKED`; Atlas diagnoses preserved evidence and asks the human for a
substantive direction rather than an internal stage or command. This adds no recovery runtime,
second repair episode, reopen path, successor-run contract, or generalized router. The next
substantive implementation remains the Stage 5 Ticket Graph Compiler. It builds on v0.10's
independently confirmed four-attempt System N+1 repair and Program Design resume.

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
