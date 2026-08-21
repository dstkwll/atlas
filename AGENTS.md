# Atlas Repository Agent Operating Contract

## Authority and grounding

- `main` is Atlas's canonical artifact authority.
- Repository state is authoritative over prompt text, conversational memory, or model recollection.
- For material work, read the governing repository contracts relevant to the task. In the final report, name the files and contracts actually consulted.
- Respect accepted upstream contracts. Do not silently redesign around them.

## Contradictions and design conflicts

- If authoritative repository sources appear to contradict one another, report the conflicting files and sections. Do not silently choose, reconcile, or rewrite them unless the task explicitly authorizes that change.
- If implementation would violate an approved upstream contract, or an approved assumption is shown false, stop and report the evidence, affected contract, and smallest decision that needs reconsideration. Use `DESIGN_BLOCKED` where appropriate.

## Instruction-contract rewrites

- Treat shortening, consolidating, or moving a `SKILL.md` as a behavioral change, not prose cleanup.
- Before the rewrite, inventory every load-bearing procedure and classify it as: retained in the always-loaded skill, moved behind an explicit trigger pointer, or intentionally superseded by a named current contract. Unclassified deletion is forbidden.
- Add a separating witness for every load-bearing behavior at risk: it must fail against the actual pre-fix/reduced document and pass after restoration. Line ceilings, keyword presence, schema seams, and a green generic checker do not prove procedural preservation.
- Execute a materially rewritten skill with a fresh agent against a realistic input and record every guess or missing instruction before acceptance.

## Validation and delivery

- For repository mutations, work on a branch, inspect the final diff, open or update a draft PR, and never merge autonomously.
- For read-only work such as review, do not create a branch, commit, or PR merely to perform the review. Report findings and verification evidence without modifying the repository.
- For material work, report the validation commands and checks actually performed, their results, required behavior not directly verified, and remaining uncertainty or known limitations. When repository mutations are involved, record this evidence before opening or updating the draft PR.

## Architecture routing

- Work under or materially affecting `architecture/` must also follow `architecture/AGENTS.md`.
