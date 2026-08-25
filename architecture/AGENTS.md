# Atlas Architecture Agent Operating Contract

This contract layers architecture-specific rules on top of the repository-root `AGENTS.md`.

- Follow `architecture/00-architecture-governance.md` rather than duplicating its governance rules here.
- Distinguish `EXPLORATION`, `CANDIDATE`, and `CHANGE`. Implement only explicitly accepted `CHANGE`s.
- Ground material recommendations in the affected current canonical documents, relevant decisions, and relevant learnings.
- Evaluate proposals as deltas against the current architecture rather than redesigning from memory.
- Make surgical edits instead of wholesale regeneration.
- Edit numbered canonical architecture documents before regenerating `architecture/rolling-monolith.md`.
- Update decisions, history, and learnings when the governance protocol requires it.
- Report contradictions among canonical architecture sources instead of silently reconciling them.
- `v2-horizon.md` is not default context. Read it only when the current task names a matching named
  area or trigger, or requests a promotion review.
- Reading the horizon never authorizes implementation; promotion requires an explicit reviewed
  `CHANGE` against the then-current canonical architecture.
- After architecture changes, run `python3 tools/check_architecture.py` and report its result.
- Inherit the root contract's branch, grounding-evidence, validation-evidence, draft-PR, and merge-authority rules.
