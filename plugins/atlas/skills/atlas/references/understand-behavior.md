# Understand existing behavior

Use for an unfamiliar change path, legacy behavior, or a missing/contradictory contract. Start with the requested outcome, affected entry points, available source revision, and any accepted specifications. Analysis is read-only unless documentation or repair is separately in scope.

Trace one representative operation from its trigger through validation, decisions, storage, external effects and response. Include error branches, asynchronous handoffs, retries and cancellation where they change the result. Follow configuration, dependency injection and generated bindings when a source-level call alone cannot establish what runs. Expand around unresolved behavior rather than inventorying every file.

For each important observation, identify the triggering input/state, observable result, enforcement point, caller reliance and tests or runtime evidence. Distinguish what a test asserts from what it merely executes. An intended invariant needs evidence at every mutation boundary, including hydration, migrations and background jobs; one validating constructor may not own them all.

Compare code, tests, documentation and accepted commitments. Record contradictions explicitly. Observed behavior is not newly accepted intent: a swallowed error or missing authorization check does not become a requirement because current code exhibits it. Characterization tests can preserve a known baseline while a defect remains separately identified. Do not impose a specification format or silently replace existing decisions with mined assertions.

When the missing fact is why a guard, interface or workaround was introduced, use [Reconstruct design rationale](reconstruct-rationale.md). Keep historical explanation separate from present-day authority.

Identify coupling that matters to the proposed change: callers that depend on ordering or exceptions, shared state owners, transaction boundaries, public compatibility, and external systems whose behavior is only assumed. Trace an event through both publisher and consumer when accessible; otherwise identify the missing segment rather than inventing an end-to-end guarantee.

Return the smallest useful behavior map, precise evidence locations, uncertainties and implications for the next change. Use [visual explanation guidance](discover-and-design.md#explain-and-co-design-through-a-useful-visual) when a call tree, flow or change comparison makes that map clearer. Stop when the risky assumptions are resolved or a specific inaccessible boundary limits the claim. Use [documentation and references](documentation-and-references.md) if versioned API behavior is the missing fact. Do not require a codemap or formal spec when a short explanation suffices.
