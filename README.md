# Atlas

Atlas is the canonical home for the agentic software-factory architecture being developed through iterative design, external-reference analysis, and eventually implementation.

## Start here

1. [`architecture/00-architecture-governance.md`](architecture/00-architecture-governance.md) — rules for safely evolving the architecture.
2. [`architecture/01-principles.md`](architecture/01-principles.md) through [`architecture/32-v0.17-decisions.md`](architecture/32-v0.17-decisions.md) — current modular architecture and decision history.
   Preserved history includes **v0.16** at [`architecture/31-v0.16-decisions.md`](architecture/31-v0.16-decisions.md), **v0.15** at [`architecture/30-v0.15-decisions.md`](architecture/30-v0.15-decisions.md), and **v0.14** at [`architecture/29-v0.14-decisions.md`](architecture/29-v0.14-decisions.md).
3. [`architecture/rolling-monolith.md`](architecture/rolling-monolith.md) — portable concatenation of the complete numbered canonical architecture.
4. [`architecture/v2-horizon.md`](architecture/v2-horizon.md) — non-authoritative deferred hypotheses with promotion triggers; excluded from the monolith and not a roadmap.

## Working model

- **Git is the artifact authority.**
- **Chat is the architecture/design room.**
- Material architecture changes must be grounded against the current canonical documents before they are accepted.
- Accepted changes should be applied surgically and reviewed as diffs rather than reconstructed from conversational memory.

The current architecture baseline is **v0.17**. D-090 adds an explicit intentional System Design N+1
revision while Program Design is pending and limits board authority to the pre-acceptance co-design
boundary. D-089 continues to make current System Design framing, canonical option grammar,
agent-led decision evidence, and phone/desktop projection acceptance explicit and fail-closed
without changing authority. D-087 fixes current ticket-graph candidates at exact
integer version 2 and makes Stage 5 responsible for semantic context selection; execution only
validates/materializes accepted declarations plus current runtime facts. Version 1 is retained as raw
historical evidence only and is not loadable or factory-executable. D-088 names Discovery's current
user-facing exit boundary Product Definition Approval while preserving `product_closure` machine/API
compatibility identifiers.
