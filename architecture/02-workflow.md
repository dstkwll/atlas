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
- Product Definition Approval
- final PR

Conditional gates:
- system design if boundaries change
- tracer slice if implementation risk becomes high

System Design participation: agent_led (user-selectable as co_design)
```

The resolved run configuration is snapshotted into the planning directory and becomes part of the run's audit trail.

A small number of intake clarifications may make an already-small task bounded enough for the
`trivial` path. If the accepted goal can be expressed as one independently verifiable ticket, intake
selects direct ticket execution; it does not invoke Discovery merely to produce a smaller PRD. If
real product decisions remain unresolved after intake, Discovery is selected regardless of the
expected code-change size. If system-observable or code-shape decisions remain, select the matching
design producer rather than hiding design inside a “trivial” ticket.

Stage selection and boundary acceptance are different decisions. Stage 0 always initializes and
classifies the run, but the first **producer** action may occur later in the pipeline:

- If the selected workflow does not require an artifact boundary, that boundary is conceptually
  `NOT_REQUIRED`. Its omission is not an approval.
- If a required upstream artifact already exists, producing it again may be unnecessary, but the
  artifact must pass that stage's ordinary boundary judge and configured authority before downstream
  admission. Reuse may skip production; it never skips Product Definition Approval.

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

## Stage 1 — Decision discovery, living PRD maintenance, and Product Definition Approval

Stage 2 was the former behavioral-specification stage; v0.6 folds it into Stage 1's
Product Definition Approval boundary. The “Stages 0–2” control-plane scope name remains for state-key
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

### Exit boundary — Product Definition Approval

Question:

> Has discovery reconciled every live decision into one reviewable product contract that is ready
> to hand off to engineering design?

For a HUMAN gate, present this exact user-facing copy:

- stage label: `Product Definition Approval`
- action: `Approve the product definition`
- helper: `Confirm the PRD and recorded decisions are complete enough to proceed to the next selected planning stage.`

Discovery owns both `10-decisions.md` and `20-prd.md` continuously; v0.6 removes the separate
specification translation producer. Product Definition Approval is discovery's single exit boundary,
not a new authoring stage or durable phase name.

Approval requires:

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

For each material choice, present a decision packet rather than prose alone: a concise comparison
matrix using the same criteria for every option, plus the minimum useful visual that exposes the
decision-relevant structure. Select the fitting view from topology/component, sequence or data flow,
schema/protocol, state/lifecycle, and failure/recovery; pair it with a plain-language explanation of
the trade-offs, operational consequences, and failure modes it changes. If no visual adds
decision-relevant clarity, state why no visual adds clarity rather than creating decoration.
Decision-time visuals are ephemeral,
non-authoritative aids until the settled choice is written into canonical Markdown.

Begin every material decision packet, and every preview of the exact decision or next question, in
simplified technical English. State the exact decision or next question, why it matters now, the fixed
constraints, what is not yet decided, the same evaluation criteria and trade-off axes, what each option
optimizes, and whether the options are genuine choices or rejected controls retained for evidence.
When constraints determine the answer, synthesize the resulting consequence; do not manufacture a
preference picker. Prefer one combined context-plus-diagram phone-first packet over separate context
and topology visuals.

In `agent_led`, whenever the analysis presents materially different alternatives, persist equivalent
decision evidence in canonical `30-system-design.md`. Keep that evidence within the existing twelve
required sections: summarize the selected route in the Decision map and retain the alternatives and
reasoning in the owning section. This rule does not require `30-system-design.html`; HTML is not
created solely for this evidence rule.

Current decision groups use unique owning H3 identities and unique standalone `Option <number> — ...`
labels; comparison matrices support rather than replace those labels. A settled route uses
`(selected)`. The Decision map uses `Decision`, `Selected route`, free-form
`Relationship / disposition`, and `Implementation consequence`. Renderer readiness comes only from
the parsed frontmatter Boolean. Legacy markers render only for exact previously accepted candidate
bytes.

Co-design also requires `30-system-design.html`, a deterministic, self-contained visual board bound
to the exact Markdown source path/hash and renderer version. It contains precise architecture views,
not decorative generative imagery: current/proposed topology, seam/ownership map,
interface/contract view, end-to-end sequence or data flow, applicable schema/protocol deltas,
failure/recovery paths, open decisions, and rejected alternatives. An inapplicable view states why.
Feedback returns through chat using the stable labels. Generated chat images or snapshots are
ephemeral projections; HTML bytes never acquire independent acceptance authority.

Stage 3 stops before codebase-local realization inside the accepted seams.

At its boundary, System Design reads the effective selected stages and chooses exactly one
admission/provenance binding:

- Product Definition Approval selected → exact accepted `20-prd.md` version/hash;
- Product Definition Approval `NOT_REQUIRED` → exact accepted/frozen Stage 0 intake and effective configuration,
  bound by `control.json.base_run_sha256`, `effective_config_hash`, and
  `effective_config_revision`.

An omitted Product Definition Approval creates no PRD or approval. A change to whichever bound source makes
accepted System Design stale; Program Design that depends on it becomes stale transitively in the
same logical downstream transition.

While Program Design is still `PENDING` with null acceptance, an explicit user-authorized
`begin-system-design-revision` transition may intentionally replace accepted System Design without
claiming an upstream contradiction. The controller retains acceptance N as non-current provenance,
marks System Design `STALE`, returns to Stage 3, and increments revision once. Version N+1 must have
a different hash, the same source binding, current D-089 format, fresh checks, and the unchanged
review/authority policy. Reacceptance returns to pending Program Design. This adds no general
rollback, history ledger, or Stage 0/Product Definition Approval reopen path.

For co-design, the board must be usable and exact at Stage 3's pre-acceptance review boundary. After canonical
Markdown is accepted, board loss or render drift is a presentation defect and cannot block Stage 4.

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
- System Design `NOT_REQUIRED` with selected Product Definition Approval → exact accepted `20-prd.md` candidate;
- both upstream semantic boundaries `NOT_REQUIRED` → exact accepted/frozen Stage 0 intake and
  effective run configuration that authorized direct Program Design admission.

The last branch binds `control.json.base_run_sha256`, `effective_config_hash`, and
`effective_config_revision`; it does not manufacture an upstream artifact or approval. Any accepted
Stage 3 change makes Stage 4 stale. If Stage 4 discovers that a system commitment must change, it
returns `DESIGN_BLOCKED` upstream rather than escalating merely to a human inside Stage 4.

Program Design always has semantic questions and therefore never uses raw `AUTO`. Its recommended
standard authority is `AGENT_REVIEW`; `HUMAN` remains available under governance or high assurance.
An independent fresh review remains mandatory.

### Bounded selected-System-Design repair

D-082 adds one exception to forward-only Stage 4 progression. While Program Design is `PENDING`, has
null acceptance, and is bound to currently accepted System Design, exact frozen repository evidence
may prove that the accepted commitment cannot be faithfully realized without changing it. Producer
prose or `DESIGN_BLOCKED` alone cannot route the run. `control-planning` must obtain the independent
`reviews/program-design-upstream-block-v1.json` judgment; only
`CONFIRMED_UPSTREAM_CONTRADICTION` authorizes the existing downstream controller to mutate state.

That mutation is one atomic invalidation-and-replacement transition, not rollback or reopen: status
becomes `BLOCKED`, phase returns to `system_design`, the System Design gate becomes `STALE`, its old
acceptance remains auditable but non-current, Program Design remains `PENDING` with null acceptance,
the bounded episode is recorded in the existing `blocked_reason`, and revision increments once.

The System Design producer may then create exactly version `N+1` with a different hash and the same
still-current source binding. It receives fresh checks, fresh review/classification when configured,
and the unchanged configured authority. Reacceptance advances to Program Design inside the same
episode, but status
remains `BLOCKED`; only fresh Program Design acceptance against N+1 clears the episode and restores
`PLANNING`. Across replacement System Design and resumed Program Design, exactly four
controller-authorized producer attempts are available. The controller reserves and persists each
attempt before candidate bytes change, so a crash consumes it; reviews, controller actions, and
approvals do not. Restarts cannot reset the budget, a second contradiction cannot nest or reset it,
and exhaustion is loud and durable.

This path does not apply to Product Definition Approval, direct Stage 0, accepted Program Design, or Stage 5 and
tickets. Their current fail-closed boundaries remain unchanged.

### Human replanning escalation after non-convergence

If D-082 exhausts its budget or resumed Program Design still cannot converge, autonomous replanning
ends and the run remains durably `BLOCKED` with its evidence preserved. Atlas first diagnoses the
shared failure assumptions, nearest accepted truth plausibly responsible, credible untried
architecture families, and consequences of changing product or run assumptions. Diagnosis is
recommendation evidence, not authority.

The human then chooses the substance: try another materially different architecture, reconsider an
upstream product commitment, reframe the work as a corrected successor run, or stop/defer. Atlas does
not ask the user to select an internal stage or command. D-083 defines this authority boundary only;
it adds no second repair episode, reopen path, successor-run contract, state transition, or recovery
runtime. Stage 5 remains the next substantive implementation.

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

Its ticket graph is an execution ordering for early seam validation, not a decomposition of work
volume by architectural layer. Every non-enabling ticket must establish observable behavior, cross
every boundary required by that behavior (not every possible layer), be independently verifiable,
and stay within the applicable accepted selected-path sources; selected Program Design remains the
exact decomposition contract. The first frontier takes the thinnest real path through the riskiest
or most important seams rather than the easiest fraction of the work.

A standalone enabling ticket must name and block an imminent vertical slice and explain why it cannot
safely live there. Unconsumed foundation epics and layer slabs are not vertical slices.

The same accepted graph must also be execution-complete. A dependency remains a real prerequisite
and states what the downstream ticket relies on it establishing. Separately, canonical graph order
preserves the risk-informed preference among tickets that are already ready. V1 selects the first
ready ticket in that order; no agent chooses between ready tickets.

Readiness is closed over every accepted execution-preventing condition, including a non-ticket
external prerequisite such as merge, CI, or exact artifact publication. Topology or an accepted
upstream commit alone cannot prove that external fact. Stage 5 preserves the observable satisfaction
condition and accepted proof path but does not invent a missing delivery contract. `continue` or
`resume` later wakes deterministic revalidation; it never grants the awaited truth.

Inputs are the applicable accepted sources for the actual selected path:

- exact accepted product PRD when Product Definition Approval is selected;
- exact accepted System Design when System Design is selected;
- exact accepted Program Design when Program Design is selected;
- accepted/frozen Stage 0 intake and effective run configuration for a direct admission path across
  omitted upstream semantic boundaries.

An omitted boundary contributes neither an artifact nor an approval. Compilation preserves the
accepted bindings carried by the selected path rather than requiring every possible upstream file.
When Product Definition Approval, System Design, and Program Design are all omitted, the `trivial` path compiles
one one-node ticket graph directly from the accepted/frozen Stage 0 intake, effective configuration,
and target repository baseline. It creates no substitute PRD or design artifact.

Outputs:

- one execution-complete ticket graph whose manifest version is exact integer `2`;
- truthful blocking relationships plus canonical preferred order;
- observable external-prerequisite satisfaction conditions where applicable;
- explicit proof paths linking promised outcomes to validators/review gates;
- the real tracer ticket where useful; and
- exact per-ticket `context.sources` declarations selected by the compiler, with purpose and exact
  upstream H2 sections for every applicable semantic source.

Stage 5 is the final pre-execution planning boundary. The compiler proposes the complete ticket
graph; it does not accept its own output. A read-only ticket-graph judge evaluates verticality,
dependency completeness, validation contracts, repository targeting, and semantic context
completeness. The current manifest version is exact integer `2`; version 1 is raw historical evidence
only and is not loadable or factory-executable. There is no converter, projection, or fallback.
The configured `tickets` authority decides whether the downstream planning controller may record
acceptance. That controller records the exact graph version/SHA-256, every applicable accepted
upstream binding, and each target repository baseline.

The downstream planning controller is one logical authority for Stages 3–5, while preserving each
stage's distinct outcome. A System Design or Program Design change marks every dependent accepted
ticket graph stale in the same logical atomic transition as the upstream state change. Its exact
file, schema, lock, and implementation decomposition remain Program Design choices. There is no
separate compilation controller.

Each ticket replaces top-level `references` with exact `context: {sources: [...]}`. Every applicable
selected-path source kind appears exactly once with exact `kind`, `sections`, and nonempty `purpose`.
Stage 0 sections are empty; semantic-source sections are nonempty, unique, and resolve to existing H2
headings. Ticket body H2s are exactly `What becomes true`, `Acceptance`, and `Execution context`.

compile-tickets owns semantic context selection. Execution receives only the exact accepted
ticket-graph binding; it may verify that acceptance and currency but may not create or record them.
The supervisor deterministically validates and materializes accepted declarations plus current
runtime facts into a deterministic non-authoritative worker brief. It must not select sources, add sections, write
purposes, summarize missing context, or fill context gaps. Missing declared material is a
packaging/preflight blocker; missing accepted judgment is `DESIGN_BLOCKED`. Repository facts within
inspection authority remain discoverable. The supervisor does not invoke a planner or treat the raw
user prompt as a coequal contract.

---

## Stage 6 — Optional tracer checkpoint

For high-risk or foundational changes, run one minimal end-to-end tracer slice before authorizing the remainder of the graph.

Possible policy:

```text
exact accepted ticket graph
   ↓
preflight verifies graph acceptance, applicable upstream bindings, and repository baseline
   ↓
selected tracer ticket factory
   ↓
automated validation/review
   ↓
HUMAN CHECKPOINT
   ↓
remaining accepted graph
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

The feature runner owns global dependency traversal across the accepted planning graph and dispatches
work into the repository-scoped run/workspace named by each ticket. Repository-scoped runs execute
that work; they do not select or admit it.

Pseudo-flow:

```text
load exact accepted ticket-graph version/hash and verify its accepted upstream/baseline bindings
load authoritative per-ticket state from every repository record plus current external evidence
reconstruct prerequisite satisfaction and the only legal next action after restart
while nonterminal tickets remain:
    if no ticket is active:
        derive readiness across the entire accepted planning graph
        admit at most one active ticket across the entire accepted planning graph
        select the first currently ready ticket in global canonical order
        dispatch it only to the repository-scoped run/workspace named by that ticket

    run TicketFactory(active_ticket)

    if ACCEPTED:
        persist accepted or terminal completion plus its associated accepted commit/tree and evidence binding
        continue

    if DESIGN_BLOCKED:
        persist terminal evidence
        stop and escalate upstream

    if FAILED:
        persist terminal evidence
        stop and report
```

A repository-scoped run cannot select, admit, or execute a ticket targeting another repository.
Parallel admission remains deferred in V1; any future parallel policy must be promoted explicitly.

---

## Stage 9 — Whole-feature validation and review

After all tickets in one repository slice are accepted, bind validation and review to that slice's
exact integrated accepted-commit-chain tip/tree. Review against the applicable accepted upstream
sources: the product contract when selected, System Design when selected, Program Design when
selected, and the frozen Stage 0 binding on a direct path. Then run:

- full build/test/lint suite for that repository slice
- integration/system tests
- architecture/scope checks
- repository-slice applicable-contract compliance review
- repository-slice architecture/program-design drift review
- maintainability/standards review
- conditional ops/security/migration/UI review

This catches interactions that cannot be judged at individual ticket scope. Passing Stage 9 proves
only that repository slice. No repository slice declares the planning effort globally ready; the
trusted supervisor evaluates global readiness from every required repository slice and
external/dependency condition in the accepted graph.

---

## Stage 10 — Package and create draft PR

For each repository slice that passes Stage 9, the system deterministically assembles evidence from
that repository-scoped run:

- source planning bundle
- approved design versions
- completed tickets for the slice
- commits per ticket
- validation results bound to the exact integrated tip/tree
- automated reviewer outcomes
- repairs performed
- design amendments
- unresolved warnings

Then:

- push that repository's branch
- create one draft PR for that repository slice
- attach or summarize evidence

This is a mechanical repository-slice packaging step and belongs inside the factory. There is no
single cross-repository branch or PR, and packaging a slice does not establish global readiness.

---

## Stage 11 — Human PR review

Initial final authority for each repository-scoped draft PR:

> Human.

The factory should make each human review unusually high leverage by presenting a polished repository
slice plus provenance and validation evidence. Merge remains a human action initially.
