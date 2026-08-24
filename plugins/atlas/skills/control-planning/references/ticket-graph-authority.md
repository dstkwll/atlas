# Ticket graph authority evidence

`reviews/ticket-graph-v1.json` is the one exact run-relative envelope. The workflow invoker assembles its duplicate-safe UTF-8 JSON bytes from one fresh read-only Stage 5 judge. Reviewer output is evidence, never authority. The controller accepts no alias, symlink, escaping path, or alternative version.

```json
{
  "version": 1,
  "run": "feature-slug",
  "stage": "tickets",
  "policy": "AGENT_REVIEW",
  "candidate_version": 1,
  "candidate_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "source_bindings": [],
  "repository_baselines": [
    {"repository": "stable-repository-id", "baseline": "0123456789abcdef0123456789abcdef01234567"}
  ],
  "semantic_review": {
    "verdict": "PASS",
    "dimensions": [
      {"dimension": "selected_path_applicability_and_no_redesign", "result": "PASS", "evidence": "Every source and decision remains within accepted selected-path truth."},
      {"dimension": "vertical_outcomes_and_required_boundaries", "result": "PASS", "evidence": "Each non-enabling ticket is one outcome-bearing required-boundary slice."},
      {"dimension": "enabling_ticket_justification", "result": "PASS", "evidence": "Every enabling exception blocks a named imminent vertical consumer and is not safely inlinable."},
      {"dimension": "dependency_truth_and_preferred_order", "result": "PASS", "evidence": "Edges are real prerequisites; risk preference is separate canonical order."},
      {"dimension": "external_readiness_and_design_blocking", "result": "PASS", "evidence": "Every accepted external condition has an observable satisfaction rule and no missing delivery truth was invented."},
      {"dimension": "deterministic_behavior_proof", "result": "PASS", "evidence": "Every promised behavior has sufficient deterministic validator evidence; reviews only supplement it."},
      {"dimension": "execution_handoff_completeness", "result": "PASS", "evidence": "The accepted graph is complete enough for deterministic execution without replanning."}
    ],
    "gaps": []
  }
}
```

Rules:

- Top-level fields are exact. `version` and `candidate_version` are integers. Run, stage, configured policy, graph version/SHA-256, exact applicable source bindings, and repository baselines must match the current mechanically valid candidate.
- `policy` records configured `AGENT_REVIEW`, `HUMAN`, or `CONDITIONAL`. For `CONDITIONAL`, V1 evaluates ordered literal `single_repository` and `multi_repository` predicates and then `otherwise`; unknown predicates fail closed.
- The seven dimension identifiers above occur exactly once. Each row has exact `dimension`, `result`, and nonempty `evidence`. `result` is `PASS`, `BLOCKED`, or `DESIGN_BLOCKED`.
- Envelope verdict is only `PASS` or `BLOCKED`: all rows PASS gives PASS; any other row gives BLOCKED. Gaps exactly cover non-PASS dimensions.
- A local Stage 5 defect uses exact `code`, `dimension`, `problem`, and `resume_action`.
- `DESIGN_BLOCKED` additionally uses exact `upstream_source`, `upstream_issue`, and `resume_boundary`. The source and resume boundary are the same applicable source kind; Stage 5 never names an omitted source or rewrites it.
- The judge checks D-084 verticality, enabling exceptions, truthful dependencies/order, D-085 readiness and proof completeness, and no redesign. It edits no ticket, manifest, source, repository, evidence, or state and returns all gaps.

## Authority matrix

| Configured/mapped policy | Required evidence | Recorded authority |
|---|---|---|
| `AGENT_REVIEW` | exact PASS `reviews/ticket-graph-v1.json`; no human approval | `AGENT_REVIEW` |
| `HUMAN` | same exact PASS review plus explicit approval of that graph | `HUMAN` |
| `CONDITIONAL` → `AGENT_REVIEW` | exact PASS review; no human approval | `AGENT_REVIEW` |
| `CONDITIONAL` → `HUMAN` | exact PASS review plus explicit approval | `HUMAN` |

Fresh review is mandatory on every path. Human approval never bypasses review. BLOCKED or DESIGN_BLOCKED changes no state.

Under `.atlas-planning.lock`, the controller reruns mechanical validation and rereads planning, graph manifest, every indexed ticket, applicable sources, repository baselines, policy, and review immediately before replacing only `planning-control.json`. Acceptance records the exact manifest version/hash, resolved authority, date, review reference/hash, source bindings, and repository baselines; sets status `READY_FOR_EXECUTION`; and stops. It creates no execution state and launches no ticket.
