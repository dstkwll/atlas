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

Output:

- recommended workflow depth
- recommended first producer stage within that workflow
- recommended governance profile
- structured risk assessment
- resolved run configuration after human acceptance/override

Classifier behavior should initially be **recommend-only**.

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
- program design
- final PR

Conditional gates:
- system design if boundaries change
- tracer slice if implementation risk becomes high
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

This does not change the shipped Stage 0–2 initializer. It rejects pre-existing discovery and
amendment state before `control.json`; a pre-existing `20-prd.md` may coexist with initialization,
but receives no acceptance from that fact. Any reused candidate at a prescribed artifact path remains
untrusted until it passes the ordinary judge/authority path.

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

Suggested content:

- current system
- proposed system
- affected components/modules
- system boundaries
- external contracts
- data ownership
- API/protocol contracts
- persistence/schema changes
- end-to-end flows
- failure/recovery behavior
- compatibility constraints
- security/operational concerns
- rejected alternatives

This is the architectural layer.

It should stop before detailed internal code shape.

---

## Stage 4 — Program design

Question:

> What shape should the implementation take inside the codebase?

Suggested content:

- file/module placement
- new vs modified files
- important types
- interfaces/contracts
- public method/function signatures
- ownership/state boundaries
- call stacks / interaction chains
- concurrency/lifetime assumptions
- test seams
- migration/expand-contract mechanics where relevant

No production method bodies.

Program design resolves the architecture-ish decisions that otherwise emerge invisibly during implementation.

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

Inputs:

- accepted product PRD
- approved system design when present
- approved program design when present

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

After all tickets are complete:

- full build/test/lint suite
- integration/system tests
- architecture/scope checks
- whole-branch product-contract compliance review
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
