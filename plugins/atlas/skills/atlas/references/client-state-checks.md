# Client state and lifecycle

Use for reactive UI changes where state identity, asynchronous updates, rendering or lifecycle can invalidate behavior. Inspect the actual framework/version, user journey and project state-management approach. Apply only the relevant section; no separate reviewer per framework is required.

## React and TypeScript UI

Check stable hook order, dependencies and stale closures. Trace effects through setup/cleanup and changing inputs, including responses arriving out of order. Confirm list identity preserves the intended item state when entries reorder. Inspect server/client boundaries for forbidden imports, leaked data, per-request isolation and hydration determinism. Do not add memoization or copy props into state without evidence it solves the actual problem.

## Vue and Nuxt

Distinguish reactive sources from snapshots, watcher inputs from captured values, and readonly props from writable state. Check watcher/subscription cleanup, computed dependencies and stable list identity. Trace SSR state and public configuration per request. Version-specific reactivity behavior needs verification before declaring destructuring or an update pattern incorrect.

## Flutter and Dart

Inspect widget identity, state ownership and the project's chosen state manager. Check mounted/context validity across async gaps, controller/subscription disposal, and navigation lifecycle. Rebuild cost should be measured; a long build method alone is not a bug. Preserve text scaling, semantics, localization and constrained-screen behavior.

## Native/declarative mobile

For Compose/Kotlin, check lifecycle-aware collection, state stability, effect keys and coroutine scopes. For Swift UI, check observed state ownership and actor/main-thread boundaries. For HarmonyOS/ArkUI, establish API/device level, observation semantics and navigation/resource compatibility from current project evidence. Do not migrate the app to another state model simply because the donor prefers it.

Exercise transitions users actually encounter: repeated submission, navigation away during a request, rapid input changes, retry after failure and returning to an existing screen. Static source review can identify hazards but does not prove interactive behavior. Use [user journeys](user-journeys.md) for live validation and [performance](performance.md) for measured rendering problems. Return the state sequence and concrete result supporting each finding.
