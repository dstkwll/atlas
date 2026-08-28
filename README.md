# Atlas

Atlas is the canonical home for the agentic software-factory architecture being developed through iterative design, external-reference analysis, and eventually implementation.

## Start here

1. [`architecture/00-architecture-governance.md`](architecture/00-architecture-governance.md) — rules for safely evolving the architecture.
2. [`architecture/01-principles.md`](architecture/01-principles.md) through [`architecture/30-v0.15-decisions.md`](architecture/30-v0.15-decisions.md) — current modular architecture and decision history.
   The preserved **v0.14** history remains at [`architecture/29-v0.14-decisions.md`](architecture/29-v0.14-decisions.md).
3. [`architecture/rolling-monolith.md`](architecture/rolling-monolith.md) — portable concatenation of the complete numbered canonical architecture.
4. [`architecture/v2-horizon.md`](architecture/v2-horizon.md) — non-authoritative deferred hypotheses with promotion triggers; excluded from the monolith and not a roadmap.

## Working model

- **Git is the artifact authority.**
- **Chat is the architecture/design room.**
- Material architecture changes must be grounded against the current canonical documents before they are accepted.
- Accepted changes should be applied surgically and reviewed as diffs rather than reconstructed from conversational memory.

The current architecture baseline is **v0.15**. D-087 fixes current ticket-graph candidates at exact
integer version 2 and makes Stage 5 responsible for semantic context selection; execution only
validates/materializes accepted declarations plus current runtime facts. Version 1 remains historical
planning and is not factory-executable.
