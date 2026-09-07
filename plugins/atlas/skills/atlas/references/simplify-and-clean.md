# Simplify and remove obsolete code

Use for an authorized cleanup/refactor or local complexity directly obstructing the current change. Identify the behavior and compatibility that must remain stable, affected callers and the smallest region worth improving.

Start with the reported pain or, for an authorized broader survey, use change history to locate areas repeatedly modified for the same responsibility. Investigate scattered edits, caller knowledge and difficult verification before proposing a refactor. Frequent changes alone do not prove poor design; generated churn or active feature work may explain them. Tie each candidate to a concrete change that would become easier and the cost or risk of getting there. A survey produces proposals, not permission to implement them.

Prefer clearer control flow, meaningful names and cohesive responsibilities. An extraction helps when it hides a coherent concept; it hurts when it makes readers jump between trivial fragments. Similar syntax is not proof that two domains should share an abstraction. Preserve evaluation order, exception timing, side effects, aliasing and asynchronous sequencing when simplifying expressions or replacing callbacks.

Try the deletion test as a thought experiment: if this abstraction disappeared, would needless indirection disappear, or would important knowledge and enforcement spread into callers? A short layer may protect authorization, transactions, compatibility or ownership. Judge the responsibility it hides and the knowledge callers avoid, not its line count or number of implementations. Consolidate only when it improves a demonstrated problem while preserving those guarantees. Retire old tests only after checking that their important behavior and failure coverage survive in the replacement checks.

Treat unused-code tools and text searches as candidate evidence. Check public exports, reflection, dynamic loading, configuration strings, templates, dependency injection, generated registrations, scripts and downstream consumers before removing an apparently unreferenced symbol. A library's external consumers may not appear in this repository. If that boundary cannot be inspected, retain the symbol or propose a deliberate deprecation.

Inspect dependency use beyond source imports: build tools, scripts, runtime plugins, assets and optional features. Use the project's package manager and reproducible lockfile updates when removal is authorized. Do not delete lockfiles, generated sources or migration history to make analysis quiet.

Work in understandable increments and verify the affected behavior after each meaningful transformation. Existing characterization tests or a small separating check can establish preservation; tests need not mirror the refactor. Keep a bug fix distinguishable from behavior-preserving cleanup so reviewers can assess both claims.

Return what became simpler, evidence that the removed surface has no required consumers, preservation checks, and compatibility uncertainty. Avoid arbitrary line limits, universal immutability rules, opportunistic repository-wide cleanup or commits prescribed by this runbook.
