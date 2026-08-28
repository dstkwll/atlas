# Architecture

This directory is the canonical architecture working set for Atlas.

The numbered documents are authoritative. `rolling-monolith.md` is generated from those documents for portable reading/retrieval and should not be edited independently.

## Current baseline

**v0.16** records D-089: System Design uses explicit simplified-English framing, canonical standalone
option labels and Decision-map identity, equivalent agent-led evidence, and verified phone/desktop
projection without changing planning authority or adding an artifact.

**v0.15** makes D-085's semantic handoff executable without adding execution machinery. The current
ticket-graph manifest version is exact integer `2`; version 1 is retained as raw historical evidence
only and is not loadable or factory-executable. Each ticket declares exact `context.sources` with a nonempty purpose, while Stage
5 owns semantic context selection and the later supervisor only validates/materializes the accepted
declaration plus current runtime facts. Missing declared material is a packaging/preflight blocker;
missing accepted judgment is `DESIGN_BLOCKED`.

### Current terminology and compatibility

D-088 governs the terminology boundary. `Product Definition Approval` is the current user-facing stage label. Historical decision and provenance records retain the former user-facing label `Product Closure` unchanged. This is not an identifier migration: the serialized boundary remains `product_closure`; review files remain `reviews/product_closure-v<version>.json`; source bindings remain `kind: product_closure`; and review envelopes remain `stage: product_closure`.

**v0.14**'s execution topology remains unchanged: one planning effort may span multiple target
repositories under one accepted cross-repository ticket graph; execution instantiates one independent
repository-scoped workspace, runtime record, and accepted chain per target repository. Logical
workcells remain per-ticket; one small closed runtime authority admits at most one active ticket
across the entire accepted planning graph. Waits and proof receipts bind observable evidence; helper
agents cannot acquire Atlas ownership; repository-slice promotion is separate from ticket acceptance;
and required evidence is harvested before destructive cleanup. v0.15 adds no execution runtime or
planning-run mutation. Sandcastle remains a proof-of-fit substrate candidate, not a dependency or
authority. The unnumbered `v2-horizon.md` preserves deferred triggers and is excluded from canonical
generation.

## Deferred horizon routing

`v2-horizon.md` is not default context. Read it only when the current task names a matching named area
or trigger, or requests a promotion review. Reading the horizon never authorizes implementation;
promotion requires an explicit reviewed `CHANGE` against the then-current canonical architecture.

Matching areas include proof reuse, response-required presentation, parallel scheduling or resource
claims, repository-orientation memory, cross-run goals, oscillation or no-progress detection, strong
isolation or a second runtime, disposable-environment state, best-of-N, environment-local
coordination, and reviewer-topology simplification. A named area routes the agent to the horizon's
trigger test; it does not establish that the trigger has occurred.

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
