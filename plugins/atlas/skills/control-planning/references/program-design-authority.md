# Program Design authority evidence

`reviews/program-design-v1.json` is the one exact run-relative envelope. The workflow invoker assembles and persists its exact UTF-8 JSON bytes; reviewer output is evidence, never authority. The controller accepts no alias, alternative version, symlink, or escaping path.

The exact top-level shape is:

```json
{
  "version": 1,
  "run": "feature-slug",
  "stage": "program_design",
  "policy": "AGENT_REVIEW",
  "candidate_version": 1,
  "candidate_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "repository_baselines": [
    {"repository": "stable-repository-id", "baseline": "0123456789abcdef0123456789abcdef01234567"}
  ],
  "semantic_review": {
    "verdict": "PASS",
    "dimensions": [
      {"dimension": "upstream_commitment_realization", "result": "PASS", "evidence": "Specific path and commitment evidence."},
      {"dimension": "repository_grounding_and_feasibility", "result": "PASS", "evidence": "Specific repository evidence."},
      {"dimension": "files_packages_types_and_responsibilities", "result": "PASS", "evidence": "Specific code-shape evidence."},
      {"dimension": "signatures_call_and_data_flow", "result": "PASS", "evidence": "Specific interface and flow evidence."},
      {"dimension": "state_locking_concurrency_and_lifetime", "result": "PASS", "evidence": "Specific state and lifetime evidence."},
      {"dimension": "migration_and_local_failure_path_implementation", "result": "PASS", "evidence": "Specific local migration and failure-path evidence."},
      {"dimension": "testability_and_compilation_readiness", "result": "PASS", "evidence": "Specific Stage 5 readiness evidence."}
    ],
    "gaps": []
  }
}
```

Rules:

- Top-level fields are exact. `version` and `candidate_version` are exact integers. `run`, `stage`, configured `policy`, candidate SHA-256, and `repository_baselines` bind the exact current inputs. Baselines are exact portable effective repository/full-canonical-OID pairs in their effective order after accepted Stage 0 amendments. They never contain a machine-local source path.
- `policy` is exactly `AGENT_REVIEW` or `HUMAN`. Program Design has no `materiality`, `AUTO`, or `HUMAN_IF_CHANGED` branch.
- A semantic row has exactly `dimension`, `result`, and nonempty `evidence`. `result` is `PASS`, `BLOCKED`, or `DESIGN_BLOCKED`. The seven Stage 4 dimensions above occur exactly once; aliases are invalid.
- Verdict is derived mechanically: any `DESIGN_BLOCKED` row yields `DESIGN_BLOCKED`; otherwise any `BLOCKED` row yields `BLOCKED`; otherwise the verdict is `PASS`.
- `gaps` contains exactly one gap for every non-PASS dimension and no gap for a PASS dimension.
- A Stage 4-local implementation defect is `BLOCKED`. An accepted upstream guarantee or missing upstream truth that cannot be realized is `DESIGN_BLOCKED` under `upstream_commitment_realization`. An unresolved local code-shape choice is `BLOCKED`; a resolved choice with bounded residual uncertainty may appear in `Least-confident decisions`. `testability_and_compilation_readiness` requires that Stage 5 receives no design question it must answer. The controller validates the declared result and evidence schema; it does not classify reviewer prose.
- Missing local bindings, objects, submodule content, or Git LFS content are mechanical `BLOCKED`, not `DESIGN_BLOCKED`. Resolve those dependencies outside review and rerun repository verification before assembling evidence.

Each `BLOCKED` gap has exactly:

```json
{
  "code": "stable-gap-code",
  "dimension": "files_packages_types_and_responsibilities",
  "problem": "Specific unresolved Stage 4 code-shape defect.",
  "resume_action": "Repair the named defect in 40-program-design.md."
}
```

Each `DESIGN_BLOCKED` gap has exactly:

```json
{
  "code": "stable-upstream-gap-code",
  "dimension": "upstream_commitment_realization",
  "problem": "Why accepted upstream truth cannot be realized.",
  "upstream_source": "system_design",
  "upstream_issue": "The exact conflicting commitment or missing decision/guarantee.",
  "resume_boundary": "system_design",
  "resume_action": "The smallest upstream decision or change required."
}
```

Every required string is nonempty. `upstream_source` and `resume_boundary` both equal the candidate's actual source-binding kind: `system_design`, `product_closure`, or `stage0`. Evidence never names an omitted boundary.

## Authority matrix

| Configured policy | Required CLI evidence | Recorded authority |
|---|---|---|
| `AGENT_REVIEW` | `--review reviews/program-design-v1.json`; no human approval | `AGENT_REVIEW` |
| `HUMAN` | the same exact PASS review and `--approval human` | `HUMAN` |

Both authorities require a fresh exact PASS review. Human approval never bypasses review, and neither `BLOCKED` nor `DESIGN_BLOCKED` advances state. A successful acceptance always records the candidate version/hash, derived authority, date, review reference/hash, and exactly one source binding. Acceptance records those exact portable pairs from `repository_baselines`, never a machine-local source path, in existing `planning-control.json`.

Duplicate-key-safe JSON, valid UTF-8, managed real-file/path confinement, exact filename, current candidate/source/repository/policy binding, review hash, and semantic coherence are mechanical preconditions. Under `.atlas-planning.lock`, the controller rereads candidate, source, review, and planning inputs immediately before atomic replacement. Acceptance increments the planning revision once and advances only to a selected `tickets` boundary; it launches no ticket work.
