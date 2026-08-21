# 01 — Architectural Principles

## 1. Separate design judgment from execution mechanics

The system should concentrate fuzzy reasoning and high-cost decisions before implementation, then progressively constrain execution with approved contracts and objective validators.

```text
fuzzy intent
  ↓
behavioral contract
  ↓
system contract
  ↓
program contract
  ↓
execution graph
  ↓
implementation
  ↓
objective validation + independent review
```

The goal is not to eliminate reasoning. It is to put reasoning where it has the highest leverage and to reduce unnecessary degrees of freedom during implementation.

## 2. Workflow defines capability; policy defines authority

A workflow stage answers: **what can the system do?**

A policy/gate answers: **who is allowed to accept the result and advance?**

This prevents individual skills from hard-coding assumptions about autonomy.

Examples:

- Program design can always be generated.
- One profile may auto-accept it after agent review.
- Another may require human approval.
- Another may require human approval only if architecture materially changed.

Participation is a third, independent question: **how does the user collaborate in producing the
artifact?** System Design may be `agent_led` (the default) or `co_design`, but that choice neither
changes what `30-system-design.md` means nor grants acceptance authority. The classifier neither
recommends nor selects the participation mode; intake neutrally presents both and only the user
selects it. Gate policy still independently resolves
`AGENT_REVIEW`, `HUMAN_IF_CHANGED`, or `HUMAN`.

## 3. One artifact, one abstraction level, one exclusive job

Each artifact must resolve a distinct class of uncertainty.

If two artifacts repeatedly restate one another, one of the abstraction boundaries is wrong.

The intended progression is:

1. **Decision discovery** — what is still unresolved?
2. **Product contract (living PRD)** — what must become true?
3. **System design** — where does it fit and what boundaries/contracts change?
4. **Program design** — what shape will the code take?
5. **Execution compilation** — what independent vertical slices implement the approved design?

Each stage should reduce degrees of freedom without reopening resolved upstream decisions.

Decision discovery and the product contract are authored by one producer and separated by the
product-closure boundary rather than by two stages (D-066, D-067).

The System Design / Program Design boundary is determined by **reliance horizon**, not by the
overloaded word “module.” A system-observable commitment, or a choice that requires a caller, peer,
or operator to adjust, belongs to System Design. A codebase-local realization that can change
without another party adjusting and without changing an accepted guarantee belongs to Program
Design. Composite decisions split: the invariant is upstream; its realization is downstream.

The two artifacts may be drafted side-by-side to pressure-test interfaces, but their acceptance is
sequential when both stages are selected: System Design is accepted first. Program Design remains
provisional until it is bound, rechecked, and finalized against the exact upstream source selected
by the run: accepted System Design when selected; the accepted PRD when System Design is
`NOT_REQUIRED` but product closure is selected; or the exact frozen Stage 0 effective intake when
both upstream semantic boundaries are `NOT_REQUIRED`. An omitted boundary never manufactures an
approval or a nonexistent artifact.

## 4. Downstream stages may discover problems, but cannot silently redesign upstream decisions

Downstream design and implementation agents are allowed to discover that an approved design is
invalid.

They are **not** allowed to self-authorize architectural changes. In particular, Program Design may
report feasibility findings upstream but cannot accept or silently rewrite a System Design
commitment. If Program Design requires such a change, it returns `DESIGN_BLOCKED`; any accepted
System Design change makes the Program Design candidate stale.

The same monotonic rule continues through execution compilation. The downstream planning controller
owns System Design, Program Design, and ticket-graph acceptance as separate outcomes under one
pre-execution authority. A changed accepted upstream design makes every dependent accepted ticket
graph stale in the same logical atomic transition. Execution may verify an accepted graph; it may
not create the acceptance it depends on.

If execution requires violating an approved contract, the correct state is:

```text
DESIGN_BLOCKED
    ↓
escalate
    ↓
amend upstream design
    ↓
review / approve
    ↓
resume
```

This preserves provenance and prevents architecture from drifting invisibly during implementation.

## 5. Agents reason; deterministic code governs

Use agents where judgment is required.

Use deterministic code for known mechanics:

- test/build/lint commands
- dependency graph traversal
- file-scope enforcement
- git status / diff / commit
- worktree lifecycle
- state transitions
- retry counters
- artifact existence/schema checks
- PR creation
- branch push

A model may propose a state change, but deterministic code should own authoritative state when practical.

## 6. Review and implementation are separate authorities

Reviewer responsibilities:

- inspect
- reason
- cite evidence
- accept/reject
- identify blocking vs non-blocking findings

Executor responsibilities:

- write
- repair
- validate

A reviewer should not silently fix the code it is judging.

## 7. Preserve builder context; refresh reviewer context

Within a ticket:

- Keep the same builder context across ordinary test failures and reviewer repair cycles, because implementation knowledge is useful state.
- Prefer fresh reviewer contexts on re-review, because prior conclusions create anchoring and confirmation bias.

## 8. Human involvement is an authority policy, not a workflow primitive

Do not build separate `safe`, `fast`, `refactor`, and `prototype` factories.

Build one workflow graph and configure authority/gates.

Human approval should be injected by policy at meaningful boundaries.

## 9. A draft PR is an appropriate factory output; merge initially is not

The factory should ideally produce:

> A draft PR that it believes is excellent, with evidence supporting that claim.

The initial definition of done should **not** be:

> The system merged its own code.

Human PR review remains the final authority until evidence from real use supports relaxing that rule for narrow classes of change.

## 10. Stable artifact semantics across profiles

Profiles may decide to:

- skip an artifact
- generate it
- review it
- human-approve it

But they should not change what the artifact means.

`program-design.md` must have the same semantic contract under every profile.

## 11. Risk can increase scrutiny automatically; it should not silently reduce requested scrutiny

At least initially, automatic classification should be advisory.

If later policy permits automatic routing:

- the classifier may raise minimum scrutiny when risk is detected;
- it should not silently downgrade a profile explicitly chosen by the user.

## 12. Build the smallest useful factory first

The first implementation should automate one bounded unit: a ready ticket.

Do not begin by building an enormous orchestration platform. Run real work, observe failure modes, and grow the control plane around evidence.
