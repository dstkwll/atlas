# Boundary review envelope

A fresh semantic reviewer reads the mechanically valid candidate and returns one run-relative JSON file. It must not modify the candidate, state, or repository.

```json
{
  "version": 1,
  "run": "<feature-slug>",
  "stage": "discovery",
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
  "stage": "discovery",
  "candidate_version": 1,
  "candidate_sha256": "<sha256>",
  "verdict": "BLOCKED",
  "gaps": [
    {
      "code": "<stable-gap-code>",
      "artifact": "10-decisions.md",
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
- The controller stores the review's run-relative reference and byte hash only after acceptance. The envelope remains reviewer output, not authority by itself.
- A BLOCKED envelope guides repair and does not mutate the gate.
