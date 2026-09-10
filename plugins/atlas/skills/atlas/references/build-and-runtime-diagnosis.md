# Build and runtime diagnosis

Use when a build, startup, test process or runtime fails. Establish the exact failing command, selected workspace/target, resolved dependencies, toolchain and relevant recent change. Use the repository's wrappers, lockfiles and configured commands. Capture the first causal error and enough surrounding output to distinguish its downstream symptoms. When the evidence is a captured profile or resource trace, use [Performance diagnosis](performance.md) for attribution and measurement limits.

Separate source/type errors, generated-artifact mismatch, dependency resolution, environment/configuration and runtime data failures. Reproduce the narrowest representative failure, then test a hypothesis that discriminates between causes. If a retry produces the same failure without new evidence, change the investigation; do not restart an unlimited loop or shrink the requested outcome.

Load only the ecosystem checks that apply:

| Context | Discriminating checks |
| --- | --- |
| JS/TS or React build | Resolved compiler/bundler, export/module mode, duplicated dependency identity, generated types, server/client imports, hydration inputs and CSS pipeline. |
| C++ | Compilation versus linking, translation-unit/source membership, symbol definitions, template visibility, linked library/ABI compatibility. |
| Go | Selected module/workspace/replacements, import cycles, method receiver/interface mismatch, multiple-result handling and map value semantics. |
| JVM/Kotlin | Wrapper and toolchain alignment, effective dependencies, annotation processors, plugin targets, framework discovery/proxies, source sets, smart casts and exhaustive cases. |
| Rust | Selected crate/features and supported toolchain, ownership/lifetime context, trait bounds, values held across suspension. |
| Swift | Actual project/scheme/destination or package target; deployment compatibility, protocol requirements, actor isolation/sendability, signing as a separate capability. |
| Python/Django | Active interpreter/environment/settings, import/startup graph, dependency compatibility, migration graph versus actual database state. |
| Dart/Flutter/mobile | Package constraints, nullability/API mismatch, generator inputs versus outputs, platform toolchain/resources/permissions and device/API level. |
| Tensor runtime | Trace shapes, dtypes, devices and gradient ownership through a small representative batch; distinguish data/collation, memory retention and runtime/driver compatibility. |

Preserve the semantics behind a compiler complaint. Making required data optional, inventing empty identifiers, casting away ownership, widening visibility, suppressing exhaustive cases or detaching work can make a build green while breaking its contract. Apply the smallest correct change, then rerun the failing command and behavior-sensitive checks. Use [runtime checks](language-runtime-checks.md) where the fix touches lifetime or concurrency.

Do not delete lockfiles, reset migration history, wipe caches, upgrade the stack or edit generated output as a default fix. First establish why the specific artifact is wrong and how its legitimate source should regenerate it. Preserve local work and secrets when inspecting configuration; print only the fields needed for diagnosis.

Return the causal explanation, change, exact checks and remaining capability/authority boundary. A build passing does not prove rendering, business behavior, training correctness or production readiness. Route schema/history inconsistencies to [data and migrations](data-and-migrations.md).
