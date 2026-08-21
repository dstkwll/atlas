# 02 — End-to-End Workflow

## Overview

The architecture contains an **outer design-control loop** and an **inner execution-control loop**.

### Outer loop — design control

Question:

> Does the proposed system still represent what we actually want to build?

Authority:

> Human + reasoning agents, under configurable governance.

### Inner loop — execution control

Question:

> Does the implementation satisfy the approved contract?

Authority:

> Deterministic validators + bounded agents, with escalation when the contract itself proves invalid.

---

## Stage 0 — Intake and classification

Input:

- fuzzy goal
- existing repository context
- optional explicit workflow/profile selection
- optional System Design participation selection when `system_design` is selected:
  `agent_led` (default) or `co_design`

Output:

- recommended workflow depth
- recommended first producer stage within that workflow
- recommended governance profile
- a neutral System Design participation choice when that stage is selected
- structured risk assessment
- resolved run configuration, including the user-selected participation mode, after human
  acceptance/override

Classifier behavior for workflow depth, producer stage, governance, and risk should initially be
**recommend-only**. Participation mode is deliberately excluded from that recommendation surface.

Participation and acceptance authority are separate intake axes. The classifier neither recommends
nor selects `co_design`; intake neutrally presents `agent_led` and `co_design`, and the user may
explicitly choose either whenever System Design is selected. That choice does not alter the gate
authority resolved from governance.

Example:

```text
Goal: Add asynchronous device job scheduling

Recommended workflow: ARCHITECTURAL
Recommended governance: STANDARD

Why:
- crosses multiple modules
- introduces durable job state
- changes execution ownership
- affects failure/recovery semantics

Human gates:
- product closure
- final PR

Conditional gates:
- system design if boundaries change
- tracer slice if implementation risk becomes high

System Design participation: agent_led (user-selectable as co_design)
```

The resolved run configuration is snapshotted into the planning directory and becomes part of the run's audit trail.

Stage selection and boundary acceptance are different decisions. Stage 0 always initializes and
classifies the run, but the first **producer** action may occur later in the pipeline:

- If the selected workflow does not require an artifact boundary, that boundary is conceptually
  `NOT_REQUIRED`. Its omission is not an approval.
- If a required upstream artifact already exists, producing it again may be unnecessary, but the
  artifact must pass that stage's ordinary boundary judge and configured authority before downstream
  admission. Reuse may skip production; it never skips product closure.

The classifier therefore recommends the earliest admissible producer stage, while the control plane
proves any required upstream contracts before allowing work to begin there.

The shipped Stage 0–2 initializer enforces that distinction. When discovery is selected,
initialization creates its mutable gate and acceptance slot and starts there. When discovery is omitted,
initialization creates no discovery gate or acceptance and starts at the first selected downstream
phase for fail-closed handoff to its owner. It rejects pre-existing decision-log or amendment state
before `control.json`; a pre-existing `20-prd.md` may coexist with initialization but receives no
acceptance from that fact. Any reused candidate at a prescribed artifact path remains untrusted until
it passes the ordinary judge/authority path.

---

## Stage 1 — Decision discovery, living PRD maintenance, and product closure

Stage 2 was the former behavioral-specification stage; v0.6 folds it into Stage 1's
product-closure boundary. The “Stages 0–2” control-plane scope name remains for state-key
coherence.

Purpose:

> Determine which decisions actually need to be made before engineering design can stabilize, and
> continuously maintain the decision ledger and living product PRD as those decisions settle.

Potential resolution modes:

```text
OPEN DECISION
    │
    ├── human judgment required ───► GRILL
    ├── factual uncertainty ───────► RESEARCH
    ├── codebase uncertainty ──────► EXPLORE
    └── experiential uncertainty ──► SPIKE
```

For very large/foggy work, use a Wayfinder-style frontier of currently answerable decisions rather than pretending the entire project can be decomposed up front.

Output is **resolved decisions/evidence plus a living product PRD**, not implementation tickets.

### Exit boundary — Product closure

Question:

> Has discovery reconciled every live decision into one reviewable product contract that is ready
> to hand off to engineering design?

Discovery owns both `10-decisions.md` and `20-prd.md` continuously; v0.6 removes the separate
specification translation producer. Product closure is discovery's single exit boundary, not a new
authoring stage or durable phase name.

Closure requires:

- a complete `10-decisions.md` with the required PRD-alignment retrospective;
- a current `20-prd.md` whose `derived_from` binds the exact decision-log version and hash it was
  reconciled against;
- a current `20-prd.html` projection regenerated from that Markdown;
- deterministic reconciliation checks plus configured semantic acceptance.

The accepted PRD defines the **product contract** and remains understandable and approvable without
requiring implementation knowledge.

---

## Stage 3 — System design

Question:

> Where does this change fit in the existing system?

Stage 3 owns **system-observable commitments** and choices requiring coordinated change across a
seam:

- current system
- proposed system
- responsibilities and system seams
- authoritative data owner
- cross-module and external contracts
- target schema/protocol
- end-to-end lifecycle, data flow, failure, and recovery
- compatibility commitments
- trust, security, and operational commitments
- rejected alternatives

The ownership test is reliance, not whether someone calls the thing a “module”: if changing a choice
requires any caller, peer, or operator to adjust, or changes an accepted guarantee, it belongs here.
Composite decisions split: Stage 3 owns the invariant while Stage 4 owns its realization.

### Participation modes

`agent_led` is the default. `co_design` is user-selected at intake, never silently selected by the
classifier, and is available whenever System Design is selected. It changes the collaboration UX,
not artifact semantics or acceptance authority.

In co-design, chat is the primary interactive control surface. Work one system seam or decision at
a time. For each, ask one plain question; present two or three concrete alternatives; give a
recommendation and its strongest counterargument; and assign a stable label. The user may redirect
or zoom in. Accepted conversational choices are written into canonical `30-system-design.md`;
conversation alone never has artifact or acceptance authority.

Co-design also requires `30-system-design.html`, a deterministic, self-contained visual board bound
to the exact Markdown source path/hash and renderer version. It contains precise architecture views,
not decorative generative imagery: current/proposed topology, seam/ownership map,
interface/contract view, end-to-end sequence or data flow, applicable schema/protocol deltas,
failure/recovery paths, open decisions, and rejected alternatives. An inapplicable view states why.
Feedback returns through chat using the stable labels. Generated chat images or snapshots are
ephemeral projections; HTML bytes never acquire independent acceptance authority.

Stage 3 stops before codebase-local realization inside the accepted seams.

---

## Stage 4 — Program design

Question:

> What shape should the implementation take inside the codebase?

Stage 4 owns **codebase-local realization** without changing system-observable commitments. When
System Design is selected, this means realization inside its exact accepted seams. On a direct
Program Design path, the accepted/frozen Stage 0 intake and effective run configuration supply the
applicable upstream constraints:

- file/package/module placement
- new vs modified files
- important types and language-level signatures
- internal interfaces
- internal state mutation and ownership mechanics
- call stacks / interaction chains
- locking, concurrency, and lifetime mechanics
- test seams
- migration implementation order and local expand/contract mechanics

No production method bodies.

Program design resolves the architecture-ish decisions that otherwise emerge invisibly during implementation.

The decision test is: if the choice can change without any caller, peer, or operator adjusting and
without changing an accepted guarantee, it belongs in Stage 4; otherwise it belongs in Stage 3.

### Paired drafting, sequential acceptance

`30-system-design.md` and `40-program-design.md` may be drafted side-by-side so codebase feasibility
can pressure-test interfaces. The Program Design draft is provisional: it may report feasibility
findings upstream, but it cannot accept or silently rewrite Stage 3.

There are two distinct judges and outcomes, never one bundle verdict. The process must accept
System Design first when that stage is selected. Program Design then binds, rechecks, and finalizes
against the source required by the actual selected path:

- selected System Design → exact accepted `30-system-design.md` candidate;
- System Design `NOT_REQUIRED` with selected product closure → exact accepted `20-prd.md` candidate;
- both upstream semantic boundaries `NOT_REQUIRED` → exact accepted/frozen Stage 0 intake and
  effective run configuration that authorized direct Program Design admission.

The last branch binds `control.json.base_run_sha256`, `effective_config_hash`, and
`effective_config_revision`; it does not manufacture an upstream artifact or approval. Any accepted
Stage 3 change makes Stage 4 stale. If Stage 4 discovers that a system commitment must change, it
returns `DESIGN_BLOCKED` upstream rather than escalating merely to a human inside Stage 4.

Program Design always has semantic questions and therefore never uses raw `AUTO`. Its recommended
standard authority is `AGENT_REVIEW`; `HUMAN` remains available under governance or high assurance.
An independent fresh review remains mandatory.

A design review should explicitly challenge:

- shallow wrappers
- unjustified interfaces
- seams invented only for unit testing
- poor locality
- vocabulary drift
- state ownership ambiguity
- unnecessary new abstractions
- failure semantics

---

## Stage 5 — Execution compilation

Question:

> How can the approved design be built as independent, verifiable vertical slices?

This stage should be treated as a **compiler**, not another open-ended design step.

Inputs are the applicable accepted sources for the actual selected path:

- exact accepted product PRD when product closure is selected;
- exact accepted System Design when System Design is selected;
- exact accepted Program Design when Program Design is selected;
- accepted/frozen Stage 0 intake and effective run configuration for a direct admission path across
  omitted upstream semantic boundaries.

An omitted boundary contributes neither an artifact nor an approval. Compilation preserves the
accepted bindings carried by the selected path rather than requiring every possible upstream file.

Outputs:

- ticket graph
- blocking relationships
- tracer slice where useful
- deterministic validation contracts
- explicit references to upstream sections

Tickets should reference upstream source-of-truth sections rather than copying them.

---

## Stage 6 — Optional tracer checkpoint

For high-risk or foundational changes, run one minimal end-to-end tracer slice before authorizing the remainder of the graph.

Possible policy:

```text
approved design
   ↓
tracer ticket factory
   ↓
automated validation/review
   ↓
HUMAN CHECKPOINT
   ↓
remaining tickets
```

This captures Dex's incremental steering principle without forcing human review of every ticket.

---

## Stage 7 — Ticket factory

Each ready ticket enters a bounded autonomous execution loop:

```text
preflight
→ executor
→ deterministic validators
→ contract reviewer
→ design/quality reviewer
→ bounded repair if rejected
→ accepted commit
```

Possible terminal states:

- `ACCEPTED`
- `FAILED`
- `DESIGN_BLOCKED`

`DESIGN_BLOCKED` is semantically distinct from a failed implementation attempt.

---

## Stage 8 — Feature runner

The feature runner owns dependency traversal.

Pseudo-flow:

```text
load approved ticket graph
while unblocked tickets exist:
    select next ticket
    run TicketFactory(ticket)

    if ACCEPTED:
        mark complete
        continue

    if DESIGN_BLOCKED:
        stop and escalate upstream

    if FAILED:
        stop and report
```

Parallel execution may be introduced later when tickets are truly independent and policy allows it.

---

## Stage 9 — Whole-feature validation and review

After all tickets are complete, review against the applicable accepted upstream sources: the product
contract when selected, System Design when selected, Program Design when selected, and the frozen
Stage 0 binding on a direct path. Then run:

- full build/test/lint suite
- integration/system tests
- architecture/scope checks
- whole-branch applicable-contract compliance review
- whole-branch architecture/program-design drift review
- maintainability/standards review
- conditional ops/security/migration/UI review

This catches interactions that cannot be judged at individual ticket scope.

---

## Stage 10 — Package and create draft PR

The system should deterministically assemble evidence from the run:

- source planning bundle
- approved design versions
- completed tickets
- commits per ticket
- validation results
- automated reviewer outcomes
- repairs performed
- design amendments
- unresolved warnings

Then:

- push branch
- create draft PR
- attach or summarize evidence

This is a mechanical packaging step and belongs inside the factory.

---

## Stage 11 — Human PR review

Initial final authority:

> Human.

The factory should make the human review unusually high leverage by presenting a polished implementation plus provenance and validation evidence.

Merge remains a human action initially.
