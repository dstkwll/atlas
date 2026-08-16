# Atlas Repository Agent Operating Contract

## Authority and grounding

- `main` is Atlas's canonical artifact authority.
- Repository state is authoritative over prompt text, conversational memory, or model recollection.
- For material work, read the governing repository contracts relevant to the task. In the final report, name the files and contracts actually consulted.
- Respect accepted upstream contracts. Do not silently redesign around them.

## Contradictions and design conflicts

- If authoritative repository sources appear to contradict one another, report the conflicting files and sections. Do not silently choose, reconcile, or rewrite them unless the task explicitly authorizes that change.
- If implementation would violate an approved upstream contract, or an approved assumption is shown false, stop and report the evidence, affected contract, and smallest decision that needs reconsideration. Use `DESIGN_BLOCKED` where appropriate.

## Validation and delivery

- Work on a branch, inspect the final diff, open a draft PR, and never merge autonomously.
- Before opening or updating a draft PR, record the validation commands and checks actually performed, their results, required behavior not directly verified, and remaining uncertainty or known limitations.

## Architecture routing

- Work under or materially affecting `architecture/` must also follow `architecture/AGENTS.md`.
