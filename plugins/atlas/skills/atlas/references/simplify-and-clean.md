# Simplify and remove obsolete code

Use for an authorized cleanup/refactor or local complexity directly obstructing the current change. Identify the behavior and compatibility that must remain stable, affected callers and the smallest region worth improving.

Prefer clearer control flow, meaningful names and cohesive responsibilities. An extraction helps when it hides a coherent concept; it hurts when it makes readers jump between trivial fragments. Similar syntax is not proof that two domains should share an abstraction. Preserve evaluation order, exception timing, side effects, aliasing and asynchronous sequencing when simplifying expressions or replacing callbacks.

Treat unused-code tools and text searches as candidate evidence. Check public exports, reflection, dynamic loading, configuration strings, templates, dependency injection, generated registrations, scripts and downstream consumers before removing an apparently unreferenced symbol. A library's external consumers may not appear in this repository. If that boundary cannot be inspected, retain the symbol or propose a deliberate deprecation.

Inspect dependency use beyond source imports: build tools, scripts, runtime plugins, assets and optional features. Use the project's package manager and reproducible lockfile updates when removal is authorized. Do not delete lockfiles, generated sources or migration history to make analysis quiet.

Work in understandable increments and verify the affected behavior after each meaningful transformation. Existing characterization tests or a small separating check can establish preservation; tests need not mirror the refactor. Keep a bug fix distinguishable from behavior-preserving cleanup so reviewers can assess both claims.

Return what became simpler, evidence that the removed surface has no required consumers, preservation checks, and compatibility uncertainty. Avoid arbitrary line limits, universal immutability rules, opportunistic repository-wide cleanup or commits prescribed by this runbook.
