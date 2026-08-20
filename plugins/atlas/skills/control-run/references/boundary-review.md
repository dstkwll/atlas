# Boundary review envelope

A fresh semantic reviewer reads the mechanically valid product-closure candidate and returns one JSON envelope. The invoker persists its exact bytes as `reviews/product_closure-v<version>.json` before invoking `advance`. The reviewer must read `10-decisions.md` before `20-prd.md`, must not modify the candidate, state, or repository, and must not repair any gap it finds.

Apply every question below before choosing `PASS` or `BLOCKED`, and report every material gap in the same pass. The deterministic controller proves only the envelope plus live version/hash binding; freshness and read order are procedural requirements, not authenticated facts. The retrospective is exhaustive over identifiers and best-effort over meaning.

## Product-closure semantic questions

1. Does the decision record state and support the real problem?
2. Are important consequences, contradictions, or scope questions still unresolved?
3. Are decisions supported well enough to justify the product contract?
4. Did every cold-read finding receive a real disposition?
5. Does each PRD obligation describe externally observable behavior?
6. Are acceptance outcomes genuinely observable?
7. Does any live decision carry a normative consequence the PRD omits or understates?
8. Does the PRD assert an obligation that its cited decisions do not actually support?
9. Is any `NO_NORMATIVE_EFFECT` reason false or evasive?

These are the packaged questions defined canonically in `architecture/06-review-and-validation.md`. The envelope stays unchanged except `stage` names the human-facing boundary:

```json
{
  "version": 1,
  "run": "<feature-slug>",
  "stage": "product_closure",
  "candidate_version": 1,
  "candidate_sha256": "<sha256>",
  "verdict": "PASS",
  "gaps": []
}
```

A blocked result reports every material gap found in that pass:

```json
{
  "version": 1,
  "run": "<feature-slug>",
  "stage": "product_closure",
  "candidate_version": 1,
  "candidate_sha256": "<sha256>",
  "verdict": "BLOCKED",
  "gaps": [
    {
      "code": "<stable-gap-code>",
      "artifact": "20-prd.md",
      "problem": "<specific unresolved semantic gap>",
      "resume_stage": "discovery",
      "resume_action": "<exact action that can resolve it>"
    }
  ]
}
```

Rules:

- Fields are exact. `verdict` is `PASS` or `BLOCKED`.
- `run`, `stage`, `candidate_version`, and `candidate_sha256` bind the review to the exact run boundary checked.
- PASS has no gaps. BLOCKED has at least one gap and reports all material gaps found, not only the first.
- Each gap has a stable code and names the affected artifact and exact resume stage/action.
- The controller accepts only `reviews/product_closure-v<version>.json`, then stores that run-relative reference and byte hash after acceptance. Accepted AGENT_REVIEW state remains valid only while those exact review bytes remain present. The envelope remains reviewer output, not authority by itself.
- A BLOCKED envelope guides repair and does not mutate the gate.
