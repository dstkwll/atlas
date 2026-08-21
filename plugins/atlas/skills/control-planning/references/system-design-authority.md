# System Design authority evidence

`reviews/system-design-v1.json` is the one exact run-relative envelope. The workflow invoker assembles and persists its exact bytes; classifier and reviewer outputs are evidence, never authority. The controller accepts no alias, versioned alternative, symlink, or escaping path.

The exact top-level shape is:

```json
{
  "version": 1,
  "run": "feature-slug",
  "stage": "system_design",
  "policy": "HUMAN_IF_CHANGED",
  "candidate_version": 1,
  "candidate_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "repository_baselines": [
    {"repository": "stable-repository-id", "baseline": "abc1234"}
  ],
  "materiality": {
    "dimensions": [
      {"dimension": "responsibilities_and_system_seams", "result": "NOT_MATERIAL", "evidence": "Specific comparison evidence."},
      {"dimension": "authoritative_data_ownership", "result": "NOT_MATERIAL", "evidence": "Specific comparison evidence."},
      {"dimension": "cross_module_external_contracts_and_dependencies", "result": "NOT_MATERIAL", "evidence": "Specific comparison evidence."},
      {"dimension": "target_schema_protocol", "result": "NOT_MATERIAL", "evidence": "Specific comparison evidence."},
      {"dimension": "end_to_end_lifecycle_failure_recovery", "result": "NOT_MATERIAL", "evidence": "Specific comparison evidence."},
      {"dimension": "compatibility_guarantees", "result": "NOT_MATERIAL", "evidence": "Specific comparison evidence."},
      {"dimension": "trust_security_operational_commitments", "result": "NOT_MATERIAL", "evidence": "Specific comparison evidence."}
    ],
    "unavailable_reason": null
  },
  "semantic_review": {
    "verdict": "PASS",
    "dimensions": [
      {"dimension": "responsibilities_and_system_seams", "result": "PASS", "evidence": "Specific review evidence."},
      {"dimension": "authoritative_data_ownership", "result": "PASS", "evidence": "Specific review evidence."},
      {"dimension": "cross_module_external_contracts_and_dependencies", "result": "PASS", "evidence": "Specific review evidence."},
      {"dimension": "target_schema_protocol", "result": "PASS", "evidence": "Specific review evidence."},
      {"dimension": "end_to_end_lifecycle_failure_recovery", "result": "PASS", "evidence": "Specific review evidence."},
      {"dimension": "compatibility_guarantees", "result": "PASS", "evidence": "Specific review evidence."},
      {"dimension": "trust_security_operational_commitments", "result": "PASS", "evidence": "Specific review evidence."}
    ],
    "gaps": []
  }
}
```

Rules:

- Top-level fields are exact. `version`, `stage`, `candidate_version`, filename, run identity, candidate SHA-256, and `repository_baselines` bind the exact frozen inputs. Baselines are the exact ordered `run.yaml.repos` repository/baseline pairs.
- `policy` is exactly `AGENT_REVIEW` or `HUMAN_IF_CHANGED`. Direct `AGENT_REVIEW` sets `materiality` to null. `HUMAN_IF_CHANGED` uses the exact materiality object above.
- A usable materiality row has exactly `dimension`, `result`, and nonempty `evidence`. `result` is `MATERIAL`, `NOT_MATERIAL`, or `UNAVAILABLE`. The seven canonical dimensions occur exactly once; aliases are invalid.
- Seven `NOT_MATERIAL` rows plus null `unavailable_reason` map deterministically to `AGENT_REVIEW`. Any `MATERIAL` or `UNAVAILABLE` row maps to `HUMAN`.
- Classifier failure, unavailable baseline, or missing/duplicate/unknown/malformed dimension output is persisted with the returned rows (possibly incomplete) and a nonempty `unavailable_reason`; that explained fail-closed shape maps to `HUMAN`. Missing or empty explanation is rejected.
- Mapped `HUMAN` requires `semantic_review: null`. Mapped/direct `AGENT_REVIEW` requires the exact semantic review object.
- A semantic row has exactly `dimension`, `result`, and nonempty `evidence`; `result` is `PASS` or `BLOCKED`. The same seven dimensions occur exactly once.
- Semantic `PASS` requires all seven rows PASS and `gaps: []`. Semantic `BLOCKED` requires one or more BLOCKED rows and one exact gap per blocked dimension; it never advances state.

Each BLOCKED gap has this exact shape:

```json
{
  "code": "stable-gap-code",
  "dimension": "responsibilities_and_system_seams",
  "problem": "Specific unresolved Stage 3 commitment.",
  "resume_action": "Repair the named commitment in 30-system-design.md."
}
```

Gap dimensions are known, unique, and cover every blocked row. Every string is nonempty.

## Authority matrix

| Frozen policy / derived authority | Required CLI evidence | Recorded authority |
|---|---|---|
| `HUMAN` | `--approval human`; no review | `HUMAN`, null review ref/hash |
| `AGENT_REVIEW` | `--review reviews/system-design-v1.json`; no human approval | `AGENT_REVIEW` |
| `HUMAN_IF_CHANGED` → `HUMAN` | both exact review and `--approval human` | `HUMAN` with review ref/hash |
| `HUMAN_IF_CHANGED` → `AGENT_REVIEW` | exact review; no human approval | `AGENT_REVIEW` |

No configured branch falls back to another. Duplicate-key-safe JSON, real-file/symlink/path confinement, exact filename, current candidate/baseline/policy binding, review hash, and semantic coherence are mechanical preconditions. Fresh context, classifier/reviewer identity, and read order are procedural requirements the controller cannot authenticate.
