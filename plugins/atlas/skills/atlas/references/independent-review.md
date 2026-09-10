# Independent review

Use when consequence, ambiguity, interacting behavior or producer bias warrants independent judgment, or when the user/project requires it. Small direct changes do not automatically need another agent.

## Set the claim and boundary

Give a fresh reviewer the outcome under review, applicable commitments, exact candidate/baseline, relevant evidence, and read-only scope. Supply raw sources instead of only the producer's narrative. Use a separate context or authorized human reviewer; changing the producer's persona is self-review. Match the number and lenses of reviewers to actual risks and explicit project requirements.

The reviewer establishes which requirements apply before treating an absent artifact as a defect. Missing required evidence is a finding, never something the reviewer should manufacture. Review must not modify the candidate or grant product, risk, publication or merge authority.

For an ambiguous bug or repeated failed repair, derive the required behavior and at least one discriminating example from the original issue, accepted amendments and inspected system before reading the producer's causal story in depth. Then test that story and candidate against the evidence. Do not require one privileged deepest function or invent an oracle for unstated user judgment; expose unresolved intent instead.

## Examine behavior and consequences

Trace relevant success and failure paths. Check accepted contracts, neighboring behavior, input and trust boundaries, state/data ownership, concurrency, recovery, migration, and operational effects only where applicable. In stateful or evidence-composing code, actively challenge combinations of states that could produce an incorrect success claim or bypass a boundary. Happy-path tests and isolated field checks may miss those combinations.

Identify the consequential assumptions that make the change safe and seek evidence capable of overturning them. Focus on unresolved assumptions that could change the verdict, rather than producing an exhaustive speculative risk list. Match each claim to its evidence: live interaction, unit tests and source inspection can establish different properties, so one does not automatically replace the others.

Use the project's existing deterministic checks for objective properties. Inspect whether the tests reach the claimed behavior and whether evidence belongs to the candidate being delivered. Missing execution access limits the verdict; it does not justify fabricated results.

Return prioritized findings with exact locations, triggering conditions, affected behavior/contract, evidence, uncertainty, and verification not performed. Separate blockers from suggestions. Avoid style preferences, speculative future problems and required documentation whose only consumer is the review itself.

For a specific risk, select a lens from the [specialist index](specialist-runbooks.md). Before reporting a defect, identify the triggering input/state and bad outcome, inspect callers and framework guards, and explain why existing protection is insufficient. Pattern matches and stylistic thresholds are not findings. A zero-finding result is valid; disclose important uncertainty rather than inventing severity or approval.

When evaluating an agent report, compare its claims with the original assignment, accepted amendments and actual artifacts; neither a confident narrative nor a numeric quality score proves completion.

## Integrate findings

The lead verifies findings, removes duplicates, challenges unsupported claims, and owns the final synthesis. Independent reviewers are evidence sources, not a majority vote. Green checks cannot settle a semantic contradiction; a forceful reviewer assertion does not make a defect real.

Ordinary in-scope defects remain the lead's responsibility to repair. Material commitment or authority changes return to the appropriate owner. After meaningful correction, use fresh review of the repair and affected/shared failure surface; retain evidence of what was checked and which candidate it binds.

If the required reviewer is unavailable, complete safe preparation and objective checks, preserve the exact candidate and open review requirement, and return that specific blocker. Do not replace independence with the producer's own approval. This does not stop an otherwise authorized trivial task whose assurance never required independent review.

Communicate the supported outcome, blocking findings, non-blocking concerns, checks/results, required behavior not directly verified and remaining uncertainty. Scale report length to the claim. Do not attach a universal verdict schema or fixed review dimensions unless an actual consumer requires them.
