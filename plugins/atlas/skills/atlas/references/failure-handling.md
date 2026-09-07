# Failure handling and recovery

Use when a change can hide failure, duplicate effects, lose work, or leave partially updated state. Inspect the requested path, its callers, error contract and real side-effect boundaries. Review is read-only; a repair assignment permits changes only within its scope.

Trace a representative failure from origin to the observer who must respond. A thrown exception may be correctly handled upstream; a catch, default or detached task is a question to investigate, not automatically a defect. Determine whether the caller can distinguish success, absence, partial success, cancellation and unavailable service.

Examine fallback semantics. An empty collection after a failed fetch can falsely assert that nothing exists; cached data can conceal staleness or cross a tenant boundary. Identify what makes degradation acceptable and how its status reaches the caller or operator. Preserve error cause and useful context without leaking secrets or private payloads.

For retries, identify the actual effect boundary and how duplicate delivery is detected. A timeout after a remote write may leave the result unknown. Retry only where the operation or its protocol makes that safe, with bounded attempts/deadline and an observable exhausted outcome. Do not erase cancellation by catching it as an ordinary retryable failure. Detached work still needs an owner for errors, lifetime and shutdown.

For multi-step mutations, inspect atomicity, rollback and compensation across the real resources. A database rollback does not undo an email or remote charge. Check failures between steps, duplicate requests, concurrent workers and process interruption. Use the existing mechanism that owns consistency; adding generic retry or orchestration infrastructure is not the default repair.

Use a focused reproducer or fault injection in an authorized disposable environment when possible. Show the triggering failure, incorrect observable result, why existing guards miss it, and the expected result after repair. Preserve the failing evidence; do not make the test pass by hiding the failure. If reproduction is unavailable, separate a supported code-path finding from unverified runtime effects.

Return actionable findings or a verified repair with affected behavior and remaining uncertainty. A legitimate, explicit degraded result may be correct. Read [data and migrations](data-and-migrations.md) when transaction or rollout semantics drive the failure.
