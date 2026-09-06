# Types, invariants and boundaries

Use when data models, states, units, APIs or mutation ownership change, or when invalid combinations are easy to represent. Start with the domain rules and consumers, then inspect representations and all construction/mutation paths.

For each important invariant, ask where it is established, who can invalidate it, and what protects it afterward. Include public setters, mutable aliases, deserialization, ORM hydration, migrations and foreign interfaces. A private constructor or branded type is insufficient if a cast or alternate writer bypasses it. Static types do not validate untrusted runtime data.

Check whether optional fields, booleans and status strings permit contradictory combinations. A discriminated union or constrained constructor can make valid states explicit when that reduces real branching or bugs. Do not introduce a type hierarchy merely to score better on a rubric. Preserve the repository's idioms and public compatibility.

Distinguish identities, units, currency, timestamps/time zones, missing values and unknown results where mixing them changes behavior. Examine overflow, precision, rounding and normalization at conversion boundaries. Ensure equality and hashing remain consistent with the chosen meaning and mutable state.

Check whether the model owns the rule or scatters it among callers. Cohesion improves when related invariants and their valid operations share an owner; coupling grows when clients must understand representation details to use an API safely. Prefer the smallest representation or boundary validation that prevents the demonstrated invalid state. Immutability is useful where it protects reasoning; blanket copying is not a correctness proof.

Show a concrete invalid construction or transition and its observable effect, or explain why all reachable paths are protected. Use compiler checks for static guarantees and runtime tests for external input and dynamic escape paths. Report compatibility/migration effects of a proposed change. No universal score, mandatory redesign, or new state-transition engine is required.
