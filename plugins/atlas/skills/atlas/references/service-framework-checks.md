# Service and framework boundaries

Use the applicable section when a service change depends on framework lifecycle, ORM behavior, request binding or test wiring. First identify the actual framework/version and configured path; filenames are clues, not proof. Combine with [security](security-boundaries.md) or [data](data-and-migrations.md) only when those risks matter.

## Django and DRF

Trace lazy query evaluation, related-object access, write concurrency and transaction scope. Inspect serializers and response fields for unintended exposure; route authentication may not enforce object-level permissions. Confirm tests exercise the real middleware/permission path rather than bypassing it with force-authentication or mocks. Migration semantics depend on the engine, version and deployed data; avoid blanket claims about ORM bulk operations.

## FastAPI and Python services

Inspect dependency identity and session/resource lifetime through success and failure. A test override must target the actual dependency callable; otherwise the real service may still be used. Distinguish create, partial-update and response schemas, including unset versus null behavior. Check blocking libraries inside async handlers and the concrete token/permission validation path. Inline versus extracted code is not itself a correctness verdict.

## JVM frameworks

Determine which framework handles dependency injection, transactions and interception. Check whether the actual invocation crosses a proxy/interceptor, especially self-calls and asynchronous boundaries. Trace entity fetching/serialization, service scope, reactive event-loop blocking and concurrent writes. Event-driven handlers need explicit duplicate/out-of-order semantics. Do not require a particular layering pattern, queue or transaction annotation without showing how it protects the contract.

## .NET services

Check request versus singleton lifetimes, scope disposal, concurrent ORM-context use, tracking behavior and cancellation through persistence/outbound requests. Inspect serialization and nullable defaults at API boundaries. A synchronous wait can deadlock or exhaust threads under the actual hosting context; show the path rather than enforcing a universal ConfigureAwait rule.

## PHP and Laravel

Trace validated fields into mass assignment, route-model binding into authorization policies, model casts into response serialization and lazy relationships into query count. Inspect queue retries/idempotency and long-lived worker state. Template escaping and deserialization need the correct trust boundary; a new Actions/Services hierarchy is optional.

## Node services

Trace middleware order, input parsing, error propagation and request/task lifetime. Confirm authentication and object authorization run on the actual route. Check bounded query/result sizes and cleanup after aborted requests. Detached logging or background work may be intentional but still needs owned failure behavior.

Return the relevant framework assumption, evidence that it holds or fails, observable impact and tests actually run. Framework-specific findings need version evidence; missing access stays an uncertainty, not permission to upgrade or replace dependencies.
