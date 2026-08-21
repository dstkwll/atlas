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

Discovery question formation has its own bounded producer-side challenge before the first grill
round. A fresh, read-only frontier critic independently derives candidate questions and routes from
the effective intake and initial framing, then the producer dispositions differences against its
persisted frontier. This improves the inputs to deliberation; it is not an acceptance review and has
no gate authority. The final producer cold read repeats the missing-decision and wrong-owner-route
check against the complete decision record and PRD before `gate_ready` becomes true.

The discovery exit boundary is product closure. Its judge is read-only and returns `PASS` or
`BLOCKED`. A blocked result reports all material gaps found in that pass; each gap names the
affected artifact and the exact stage and action that can resume it. `BLOCKED` returns to the
producer without changing authoritative state. A producer-authored completion flag is evidence
that the attempt ended, never proof that product closure passed.

**Mechanical checks:** candidate identity and version match the planning run; required decision
identifiers and record fields are present and unique; every decision has a closed contribution
grade; declared repository scope matches the effective intake; the exact open-frontier table contains
no unresolved entry; the exact cold-read table gives each unique finding a non-placeholder
disposition; intake is not stale; the required PRD-alignment retrospective
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

## System Design boundary

System Design review judges the exact `30-system-design.md` candidate independently of its
participation mode. Co-design does not make conversational agreement an approval and does not
change the gate authority.

Deterministic checks establish candidate identity/version/hash and required source bindings. When
participation is `co_design`, they also require `30-system-design.html`, verify that it is
self-contained and binds the exact Markdown source path/hash plus renderer version, and require each
prescribed architecture view or an explicit reason it is inapplicable. The HTML and ephemeral chat
images remain projections and never receive an independent acceptance outcome.

The required source binding follows an applicability test over the effective selected stages and
chooses exactly one branch:

1. Product Closure selected → exact accepted `20-prd.md` version/hash.
2. Product Closure `NOT_REQUIRED` → exact accepted/frozen Stage 0 intake and effective
   configuration, bound by `control.json.base_run_sha256`, `effective_config_hash`, and
   `effective_config_revision`.

The reviewer must not require or fabricate a PRD or approval for omitted Product Closure. A change
to whichever bound source makes accepted System Design stale; dependent Program Design becomes
stale transitively in the same logical downstream transition.

Semantic review checks the Stage 3 reliance horizon: responsibilities and system seams,
authoritative data ownership, cross-module/external contracts, target schema/protocol, end-to-end
lifecycle/failure/recovery, compatibility, and trust/security/operations. The judge reports its own
Stage 3 result; no later Program Design verdict can accept or amend it.

Under standard governance, `HUMAN_IF_CHANGED` compares the candidate against the exact
repository/current-system baseline. An independent read-only classifier provides per-dimension
evidence; deterministic policy sends any material dimension to `HUMAN` and otherwise requires
`AGENT_REVIEW`. The baseline, candidate bindings, and evidence persist. Missing or unprovable
baseline/classification fails closed to `HUMAN`; changed inputs make the classification and approval
stale. Autonomous governance uses `AGENT_REVIEW`; high assurance uses `HUMAN`. System Design never
uses raw `AUTO` for its semantic boundary.

---

## Program Design boundary

Program Design has its own independent fresh review because codebase-local realization still asks
semantic questions. It never uses raw `AUTO`. The recommended standard authority is
`AGENT_REVIEW`; policy may select `HUMAN`, including for high assurance.

Paired drafting may produce both design candidates side-by-side, but the Program Design result is
provisional until selected upstream acceptance completes. Its boundary carries an applicability test:
read the effective selected stages, treat selected `discovery` as selection of its product-closure
boundary, choose exactly one of the following branches, and verify the candidate against that exact
source:

1. System Design selected → exact accepted `30-system-design.md` version/hash.
2. System Design `NOT_REQUIRED`; product closure selected → exact accepted `20-prd.md` version/hash.
3. Both upstream semantic boundaries `NOT_REQUIRED` → exact accepted/frozen Stage 0 intake and
   effective configuration, bound by `control.json.base_run_sha256`, `effective_config_hash`, and
   `effective_config_revision`.

The reviewer must not manufacture or fabricate approval for an omitted boundary, require a
nonexistent artifact, or accept more than one branch. Any accepted System Design change makes the
Program Design candidate and prior result stale.

The Stage 4 judge evaluates files/packages/types, language signatures, internal state mutation and
call graph, locking/concurrency/lifetime mechanics, migration implementation order, and test seams.
If acceptance would require a caller, peer, or operator to adjust or would change an accepted
guarantee, the finding belongs upstream: return `DESIGN_BLOCKED` rather than seek a human exception
inside Stage 4. Stage 3 and Stage 4 always produce distinct outcomes; there is no joint bundle
verdict.

---

## Whole-feature review

Ticket-level correctness is insufficient.

After all tickets, review against the applicable accepted upstream sources: the product contract when
selected, System Design when selected, Program Design when selected, and the frozen Stage 0 binding
on a direct path.

1. full applicable-contract compliance
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
