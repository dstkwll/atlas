# Language and runtime checks

Use the sections matching changed behavior, especially when a repair touches ownership, cancellation, concurrency or representation. Establish the installed language/runtime version and project conventions. These are diagnostic questions, not demands to change language, install linters or apply every language's checklist. For web/service frameworks use [service boundaries](service-framework-checks.md); for reactive interfaces use [client state](client-state-checks.md).

## JavaScript and TypeScript

Trace promise ownership, rejected detached work, async iteration and event-loop blocking. Check whether a type assertion or non-null assertion hides unvalidated external data. Inspect closure lifetime and mutable state across awaits. Compiler strictness changes may remove protection rather than fix an error. Parallel requests still need bounded resource use and defined partial-failure behavior.

## Python and PHP

Inspect mutable defaults/shared state, broad catches and unsafe deserialization at trust boundaries. Check deterministic cleanup of files, connections and iterators when an exception or early return occurs. In Python, distinguish synchronous clients called from async code and task cancellation. In PHP, inspect coercion, serialization and long-lived worker state using the project's actual runtime assumptions. Prefer a demonstrated defect over enforcing one typing or formatting style.

## Java, Kotlin, C# and F#

Trace task/thread ownership, blocking waits, cancellation propagation and disposal. Check singleton/service lifetimes against mutable request state. On Kotlin, examine structured scopes, Flow collection/emission and exhaustiveness across sealed states. In C#, distinguish async void event handlers from unowned task failures and inspect sync-over-async and nullable escape paths. In F#, inspect discriminated-union coverage, Result/Option boundaries, computation/resource lifetime and repeated lazy enumeration. In Java, verify thread-safety and resource closure; framework transaction/proxy behavior belongs in the service reference. Do not prescribe a new layer or exception library to satisfy a checklist.

## Go

Show how each spawned goroutine exits on success, cancellation and downstream abandonment. Check channel ownership/closure, bounded queues, lock scope/order and resource cleanup deferred inside long-running loops. Preserve error identity where callers depend on it. An interface extraction or module rearrangement needs a concrete boundary benefit, not merely a compiler workaround.

## C++ and Rust

Inspect resource owner, lifetime, aliasing, iterator/reference validity and copy/move effects. For C++, trace bounds, overflow/undefined behavior, lock order and thread completion. Raw pointers or allocation are not defects without an ownership failure. For Rust, identify the invariant of each relevant unsafe boundary and whether callers satisfy it; inspect panics versus recoverable errors, blocking work or locks across async suspension, and bounded channels. Cloning or changing a removal algorithm may alter cost, identity or ordering even if the compiler accepts it.

## Swift

Inspect actor isolation and invariants across reentrant awaits, task cancellation, main-thread work and ARC cycles. Choose weak or unowned capture according to actual lifetime. A sendability annotation or nonisolated declaration needs a supported safety argument; it cannot manufacture one. Distinguish a justified programmer assertion from failure reachable through ordinary external input.

Return concrete triggering states, violated contracts, contextual guards and useful checks. Check language-version details against authoritative evidence when uncertain. Use [types and invariants](types-and-invariants.md) for representation design and [failure handling](failure-handling.md) for shared error/recovery behavior.
