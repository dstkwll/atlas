# 06 — Review and Validation Architecture

## Validation hierarchy

Not all verification is the same.

### Layer 1 — deterministic validators

Best evidence where available:

- compilation/build
- unit tests
- integration tests
- static analysis
- linters
- architecture checks
- schema checks
- generated artifact checks
- browser assertions
- diff/scope checks

These should run before LLM review so reviewers spend reasoning tokens on ambiguity rather than failures a command can prove.

### Layer 2 — independent semantic review

Required for things deterministic checks cannot fully judge:

- contract/product-contract compliance
- architecture drift
- maintainability
- unnecessary complexity
- missing edge cases
- inappropriate abstractions
- misleading tests

### Layer 3 — human authority

Used where policy requires human judgment or acceptance.

---

## Per-ticket review axes

Recommended default: two independent axes.

### Contract reviewer

Question:

> Did this ticket produce exactly the behavior required by the approved contracts?

Checks:

- ticket acceptance
- relevant product-contract sections
- relevant system/program-design sections
- missing behavior
- scope creep
- false-positive tests

### Design/quality reviewer

Question:

> Is this a good implementation for this codebase while respecting approved design?

Checks:

- architecture/program-design drift
- module boundaries
- state ownership
- unnecessary abstractions
- codebase conventions
- maintainability
- locality
- test seam quality
- readability

These axes should remain independent enough that one does not mask the other.

---

## Conditional reviewers

Do not create a reviewer for every conceivable concern.

Enable specialist reviewers based on structured change/risk signals.

Examples:

### Operations reviewer

Trigger when significant I/O or runtime dependency behavior changes.

Inspect:

- timeouts
- retries
- resource cleanup
- queue/database/network/file failure behavior
- backpressure
- unbounded growth
- degraded dependencies
- cancellation

### Security reviewer

Trigger for:

- auth/authz
- secrets
- trust boundaries
- untrusted input
- cryptography
- permission changes
- externally exposed endpoints

### Migration reviewer

Trigger for:

- schema migrations
- compatibility windows
- expand/contract changes
- backfills
- rollback considerations

### UI/browser verifier

Trigger for user-facing UI behavior that can benefit from browser-level verification.

---

## Reviewer output should be structured

Preferred conceptual schema:

```json
{
  "decision": "accept | reject",
  "findings": [
    {
      "severity": "blocking | warning",
      "category": "contract | design | quality | ops | security",
      "source": "40-program-design.md#job-cancellation",
      "problem": "...",
      "evidence": "...",
      "suggested_direction": "..."
    }
  ]
}
```

Deterministic orchestration should consume this structured output.

---

## Reviewer write policy

Default:

> Read-only repository access.

If a reviewer mutates code, the harness should detect and reject/restore the mutation.

Reviewer and executor roles should not blur.

### A reviewer never creates the artifact it requires

Read-only access is the enforcement. This is the design rule upstream of it: a reviewer that requires an artifact must first establish that the artifact is **applicable to the work under review**, and a missing required artifact is reported as a finding rather than supplied.

A reviewer given an unconditional requirement — an artifact named as required with no test for whether this piece of work should have one — has two ways to complete its task when the artifact is absent, and only one of them is correct. Creating it is the failure mode, and it is a plausible-looking one: the reviewer appears to have resolved a gap, while the evidence it goes on to judge is evidence it authored.

Two consequences for specifying any reviewer:

- **Requirements that depend on which path the work took carry their applicability test with them.** Where a workflow offers alternative routes to the same stage, an artifact produced by only one route is conditional on evidence that the route was taken, and its absence on the other route is not a gap.
- **A required artifact that is absent is a finding.** The reviewer reports it and stops. It never writes a routing artifact, an evidence file, a ticket, or a product contract in order to satisfy its own condition.

Observed in a real run of a non-canonical skill; recorded as L-012. The mechanism generalizes to any reviewer this architecture specifies.

---

## Discovery product-closure boundary

The discovery exit boundary is product closure. Its judge is read-only and returns `PASS` or
`BLOCKED`. A blocked result reports all material gaps found in that pass; each gap names the
affected artifact and the exact stage and action that can resume it. `BLOCKED` returns to the
producer without changing authoritative state. A producer-authored completion flag is evidence
that the attempt ended, never proof that product closure passed.

**Mechanical checks:** candidate identity and version match the planning run; required decision
identifiers and record fields are present and unique; declared repository scope matches the
effective intake; the open-frontier structure contains no unresolved entry; cold-read evidence
is recorded and dispositioned; intake is not stale; the required PRD-alignment retrospective
contains exactly one row for every live decision; every `NORMATIVE` decision maps to current PRD
identifiers; every `NO_NORMATIVE_EFFECT` decision has a reason and maps to none; every normative
PRD item cites one or more live decisions; the mappings agree in both directions; `20-prd.md`
`derived_from` binds the exact current `10-decisions.md` version/hash; and `20-prd.html` declares
the current Markdown source/hash. These checks are exhaustive over identifiers and best-effort
over meaning.

**Semantic questions, in order:**

1. Does the decision record state and support the real problem?
2. Are important consequences, contradictions, or scope questions still unresolved?
3. Are decisions supported well enough to justify the product contract?
4. Did every cold-read finding receive a real disposition?
5. Does each PRD obligation describe externally observable behavior?
6. Are acceptance outcomes genuinely observable?
7. Does any live decision carry a normative consequence the PRD omits or understates?
8. Does the PRD assert an obligation that its cited decisions do not actually support?
9. Is any `NO_NORMATIVE_EFFECT` reason false or evasive?

Failure resumes at discovery in `10-decisions.md` and `20-prd.md`. Because the semantic questions
are part of this boundary, acceptance authority is `AGENT_REVIEW` or `HUMAN` in this revision.
Reviewer freshness and read order remain procedural requirements: the controller can enforce
schema, binding, and artifact identity, but it cannot authenticate who read first or how fresh a
review context really was.

---

## Whole-feature review

Ticket-level correctness is insufficient.

After all tickets:

1. full product-contract compliance
2. architecture drift across combined change
3. program-design drift
4. cross-ticket interactions
5. dead/duplicate transition code
6. standards/maintainability
7. specialty review triggers
8. final diff scope

---

## Human review policy

Human review can occur at different points based on governance profile.

Potential gates:

- product-closure approval
- system design approval
- program design approval
- ticket graph approval
- tracer slice approval
- every N tickets
- design amendment approval
- final PR approval

The long-term goal is not “remove humans.”

The goal is:

> Spend human judgment only where it meaningfully changes outcomes.
