# 08 — State, Governance, Amendments, and Recovery

## Single authoritative state owner

Agents should not independently decide that workflow phases are complete.

Prefer one deterministic state authority responsible for:

- current phase
- gate status
- active ticket
- dependency completion
- retry counters
- terminal/escalation states
- approved artifact versions

Agents produce evidence/proposals; the state machine applies valid transitions.

For pre-execution Stages 0–2, that authority is the feature-root `control.json`. The
controller changes it through one atomic file replacement and may then regenerate
`00-state.md` as a projection. Repository-scoped `.factory/runs/` state begins with execution
and remains a separate domain.

Stages 3–4 require a separate downstream design controller. It owns only the minimum gate,
acceptance, staleness, and exact candidate/version/hash bindings needed for System Design and
Program Design. It does not widen Stage 0–2 `control.json`, and v0.7 does not introduce a
generalized router. The exact storage shape is left to that controller's implementation.

---

## Suggested high-level run states

```text
INTAKE
DISCOVERY
SYSTEM_DESIGN
PROGRAM_DESIGN
TICKETING
READY_FOR_EXECUTION
EXECUTING
DESIGN_BLOCKED
FINAL_VALIDATION
PR_READY
AWAITING_HUMAN_REVIEW
COMPLETE
FAILED
```

Not every workflow depth uses every state. In v0.6, product closure is the exit boundary inside
`DISCOVERY`, not a separate durable phase/state name.

---

## Ticket states

Possible starting model:

```text
PENDING
BLOCKED
READY
ACTIVE
REPAIRING
REVIEWING
ACCEPTED
DESIGN_BLOCKED
FAILED
```

The deterministic runner owns transition legality.

---

## Gate states

```text
NOT_REQUIRED
PENDING
AUTO_PASSED
AGENT_APPROVED
HUMAN_APPROVED
REJECTED
STALE
```

A gate can become `STALE` if an upstream amendment invalidates its prior approval.

`NOT_REQUIRED` means the selected workflow does not include that boundary. It is not a successful
gate outcome and must never be used for required material reused from before the run. Reused required
material still follows the ordinary judge/authority path. In current Stages 0–2 that means
`AGENT_APPROVED` or `HUMAN_APPROVED`; a future mechanical-only boundary may use `AUTO_PASSED`. The
Stage 0–2 `control.json.gates` map continues to contain only selected mutable boundaries; omission
because a boundary was not selected has `NOT_REQUIRED` semantics without manufacturing an approval
record.

`AUTO_PASSED` means a boundary explicitly declared mechanical-only and all of its
deterministic prerequisites passed. It never means an agent reviewed the artifact. Discovery
product closure is not a mechanical-only boundary in this revision.

---

## Approved artifacts are versioned contracts

Once an artifact passes its gate, downstream work references its accepted version and content
hash from the controller that owns that boundary. Stages 0–2 use `control.json`; Stages 3–4 use
their downstream design controller.

This prevents:

> “The design changed while ticket 3 was executing and nobody knows which version the implementation targeted.”

Stages 0–2 do not create duplicate approved copies, acceptance-history ledgers, or separate
receipt files. The prescribed candidate path remains the artifact, and any change after
acceptance requires a version increment and a new gate decision. `control.json` preserves the
current acceptance binding for each stage (version, hash, authority, date, and review reference
when applicable). In v0.6 that accepted product-contract candidate is `20-prd.md`, whose
`derived_from` binding transitively names the exact decision-log version/hash it closed against.
The current Stage 0–2 controller has no post-closure reopen command. A future downstream owner may
mark that binding stale and require the next candidate version; until that owner exists, any live
source mismatch after acceptance fails closed rather than silently reopening discovery.

---

## Amendments

When execution discovers an invalid upstream assumption:

1. ticket enters `DESIGN_BLOCKED`;
2. evidence is recorded;
3. affected upstream artifact receives a proposed amendment;
4. policy determines required review/approval;
5. dependent ticket graph is recalculated;
6. already-completed work is checked for invalidation;
7. stale approvals are explicitly marked;
8. execution resumes only after valid re-approval.

The narrower Stage 0–2 case is an intake correction discovered before execution. It is an
ordered `amendments/NNN-*.md` record using machine-parseable frontmatter. Applying it updates
only `control.json`'s amendment count and effective-configuration hash. Re-reading `run.yaml`
plus the ordered amendments must reproduce that hash. No separate amendment ledger or hash
chain exists in this revision.

---

## `HUMAN_IF_CHANGED`

This gate deserves explicit support rather than being a prompt convention.

System Design semantics:

```text
bind exact repository/current-system baseline and candidate
  ↓
independent read-only classification with evidence per material dimension
  ↓
no material change
  → AGENT_REVIEW

any material change
  → human gate required

baseline or classification unavailable
  → fail closed to HUMAN
```

The stage-specific material dimensions are:

- responsibilities and system seams;
- authoritative data ownership;
- cross-module/external contracts and dependencies;
- target schema/protocol;
- end-to-end lifecycle, failure, and recovery;
- compatibility guarantees;
- trust, security, and operational commitments.

The classifier judges materiality but has no gate authority. Deterministic policy maps any material
dimension to `HUMAN` and no material dimensions to `AGENT_REVIEW`; semantic design boundaries never
use raw `AUTO`. Persist the exact baseline and candidate identities/hashes with the classification
evidence. Any change to those inputs makes the classification and prior approval stale and requires
reclassification/reapproval.

Participation remains orthogonal. Choosing `co_design` does not bypass this comparison, satisfy the
human gate, or otherwise alter authority.

---

## Run configuration is immutable provenance

At run start, resolve:

```text
global config
+ repo config
+ selected profile
+ explicit overrides
```

Then snapshot it into `run.yaml`.

Changing global settings later must not retroactively alter an active/historical run's governance semantics.

---

## Recovery and crash safety

The system should be restartable from on-disk state, with recovery machinery proportional to
the current write boundary.

For Stages 0–2 the controller has one authoritative mutable file. It writes a temporary
`control.json` beside the current one and atomically replaces it. A run-local single-writer
lock prevents two processes from committing from the same revision. Because no authoritative
transition spans several files, V1 has no transaction journal or replay protocol here.

On restart:

1. read authoritative run state;
2. inspect repository/worktree reality;
3. reconcile interrupted active operation;
4. verify accepted commits still exist;
5. determine next legal transition;
6. never rely solely on conversational/model memory.

This is one of the strongest reasons to keep artifacts/state on disk.

---

## Auditability

A future observer should be able to answer:

- What did the user ask for?
- Which workflow/profile was selected?
- Why?
- Which decisions were human-approved?
- Which design version did each ticket implement?
- Which validators ran?
- Which reviews rejected work?
- What repairs occurred?
- Did any design assumptions fail?
- Why was the PR eventually considered ready?

The architecture should make these answers emergent from stored evidence rather than reconstructed from chat history.
