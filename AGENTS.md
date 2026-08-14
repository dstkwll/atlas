# Atlas Agent Operating Contract

- `main` is the canonical artifact authority for Atlas.
- Before material architecture work, read `architecture/00-architecture-governance.md`, the affected canonical documents, and relevant decisions and learnings.
- Treat repository state as authoritative over prompt text or conversational memory.
- Implement only an explicitly accepted architecture `CHANGE`; do not independently promote `EXPLORATION` or `CANDIDATE` ideas.
- Make surgical edits to the current architecture instead of regenerating it from memory.
- If a request conflicts with current architecture or invariants, stop and report the conflict rather than silently resolving it.
- Edit modular architecture documents first, then regenerate `architecture/rolling-monolith.md`.
- Update decision and history records when required by the governance document.
- Work on a branch, inspect the final diff, open a draft PR, and never merge autonomously.
