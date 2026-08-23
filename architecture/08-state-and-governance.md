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

Stages 3–5 use one downstream planning controller as their logical mutable authority. It owns only
the gate, acceptance, staleness, dependency, and exact candidate/version/hash bindings needed for
System Design, Program Design, and the compiled ticket graph. Each boundary keeps a separate outcome;
one controller never means one joint verdict. The Stage 0–2 `control.json` remains frozen after
handoff and is the exact upstream admission anchor, not the live downstream phase owner.

A changed accepted upstream artifact and every directly dependent downstream invalidation are one
logical atomic transition: System Design may stale Program Design and the ticket graph; Program
Design may stale the ticket graph. The controller ends at Stage 5, owns no repository-scoped
execution state, and is not a generalized router. Its exact file, storage representation, schema,
lock, and module/CLI decomposition remain Program Design and implementation choices.

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
hash from the controller that owns that boundary. Stages 0–2 use `control.json`; Stages 3–5 use
one downstream planning controller with separate acceptance outcomes. Stage 5's accepted ticket
graph additionally binds all applicable accepted upstream sources and the frozen baseline of each
target repository. `READY_FOR_EXECUTION` means that exact graph acceptance exists and is current;
it is produced by the downstream planning controller, never inferred by the execution runtime.

This prevents:

> “The design changed while ticket 3 was executing and nobody knows which version the implementation targeted.”

Stages 0–2 do not create duplicate approved copies, acceptance-history ledgers, or separate
receipt files. The prescribed candidate path remains the artifact, and any change after
acceptance requires a version increment and a new gate decision. `control.json` preserves the
current acceptance binding for each stage (version, hash, authority, date, and review reference
when applicable). In v0.6 that accepted product-contract candidate is `20-prd.md`, whose
`derived_from` binding transitively names the exact decision-log version/hash it closed against.
The current Stage 0–2 controller has no post-closure reopen command. D-082 reaches neither Product
Closure nor direct Stage 0; any live Stage 0–2 source mismatch after acceptance fails closed rather
than silently reopening discovery.

System Design acceptance chooses exactly one admission/provenance binding from the selected path:
the exact accepted `20-prd.md` version/hash when Product Closure is selected, or the exact
accepted/frozen Stage 0 intake and effective configuration when Product Closure is `NOT_REQUIRED`,
bound by `control.json.base_run_sha256`, `effective_config_hash`, and
`effective_config_revision`. Omitted Product Closure creates no PRD or approval. A change to
whichever source is bound to accepted System Design makes that acceptance stale; dependent Program
Design becomes stale transitively in the same logical downstream transition.

---

## Bounded Program Design upstream-repair episode

D-082 permits exactly one pending Program Design → selected accepted System Design repair/reaccept
→ pending Program Design path under the D-080 controller. This is invalidation and replacement, not
rollback or reopen. Product Closure, direct Stage 0, accepted Program Design, Stage 5/tickets, and
execution-originated repair remain outside this path.

Only a current `reviews/program-design-upstream-block-v1.json` verdict of
`CONFIRMED_UPSTREAM_CONTRADICTION` can open the episode. The atomic return sets status `BLOCKED`,
phase `system_design`, and the System Design gate `STALE`; retains the prior acceptance as
non-current and non-consumable provenance; leaves Program Design `PENDING` with null acceptance;
records the bounded episode in the existing `blocked_reason`; and increments revision once. Any
invalid or non-confirming input changes nothing.

Replacement requires version `N+1`, a different hash, the same still-current source binding, fresh
mechanical checks and fresh semantic review/classification when configured, and the unchanged
authority. Its atomic acceptance
replaces the current System Design binding, restores that gate's derived approved state, sets phase
to `program_design`, advances the existing `blocked_reason` episode, and increments revision once.
The overall status remains `BLOCKED` through System Design N+1 acceptance and resumed Program Design.
Only fresh Program Design acceptance against N+1 clears the episode and restores `PLANNING`.

The active episode permits exactly four controller-authorized producer attempts in total across the
two producers. Before candidate bytes change, the controller reserves and persists an attempt; an
interrupted or crashed attempt is therefore consumed. Reviews, controller actions, and approvals do
not consume attempts. A restart cannot reset the budget, a second contradiction cannot nest or
reset the episode, and exhaustion is loud and durable with current evidence preserved. The active
episode lives only in the existing `blocked_reason`. Every repair replacement has a hash-bound
System Design evidence envelope whose `repair_context` carries the complete validated contradiction
finding, immediate superseded acceptance, and original contradiction reference/hash. Direct
`HUMAN` repair uses the same conditional evidence envelope with semantic/materiality fields null;
it grants no authority, and human approval remains the acceptance authority. This is not a
normal-path review requirement and does not widen the acceptance schema. It records one immediate
predecessor only, not a recursive chain. No history array, event log, rollback ledger, or new
top-level state field is implied. The original no-clobber upstream-block envelope is authoritative
for that complete predecessor acceptance. The live acceptance must exactly match it before
staleness, and every retained or copied predecessor must remain JSON-type-exactly equal through
reload, reservation, review, and N+1 acceptance. The later `repair_context` copy cannot grant
authority or become a second truth.

---

## Amendments

The following is the broader future execution-originated amendment flow; D-082 does not implement
or authorize it. When execution discovers an invalid upstream assumption:

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

The downstream planning controller must preserve the same semantic property: one authoritative
transition either records an upstream change plus all directly caused Stage 4/5 staleness or records
none of them. Architecture fixes that logical atomicity, not the storage mechanism. Program Design
may choose one snapshot, a transactional store, or another minimal representation, but it may not
expose an intermediate state in which an upstream acceptance changed while its dependent ticket
graph still appears current. No acceptance-history ledger or event-sourced replay system is earned
by this rule alone.

For a D-082 episode, crash safety also requires each of the four controller-owned producer attempts
to be reserved durably before producer-owned candidate bytes change. Recovery reads that persisted
reservation as consumed; restarting a skill, process, or session never recreates the budget.

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
