# 07 — Decision Discovery, Research, Exploration, and Spikes

## Terminology decision: prefer `spike` for learning experiments

The word `prototype` is overloaded. It can imply:

- an exploratory throwaway experiment,
- a user-facing mockup that needs review,
- a candidate implementation likely to survive into production,
- or a proof-of-concept artifact.

For this architecture, **`spike` is the clearer default term for uncertainty-reduction work**.

A spike means:

> A bounded experiment whose primary output is knowledge/evidence, not production code.

A spike does **not** inherently require human review.

Whether a spike requires a human gate is a policy decision based on what decision it informs and how consequential that decision is.

---

## Decision discovery is a routing problem

Given an unresolved question, choose the cheapest valid resolution mechanism.

```text
OPEN QUESTION
    │
    ├── requires preference/tradeoff judgment ─► GRILL / HUMAN
    │
    ├── answer exists externally ──────────────► RESEARCH
    │
    ├── answer exists in repository ──────────► EXPLORE
    │
    └── answer requires observing behavior ───► SPIKE
```

This avoids asking humans factual questions agents can answer and avoids “researching” questions that require an empirical experiment.

---

## Challenge the frontier, not only its answers

Before the first grill round, the producer persists its complete initial frontier and one fresh
frontier critic independently derives a candidate question set and route for each question from the
effective intake, problem test, announcement test, and available evidence. The critic does not read
the producer's proposed frontier before producing its own. The producer compares the two sets and
records every missing or misrouted question plus its disposition before asking the user anything.
The critic is read-only: it proposes questions and routes, never answers them, repairs the artifacts,
or accepts the stage.

This is one bounded challenge per Discovery run, not a council for every question. At closure, the
existing fresh cold read independently checks again for any absent decision or wrong owner route
revealed by the now-complete decision record and PRD. The later product-closure reviewer remains a
separate acceptance role; neither challenge has gate authority.

---

## Grill

Use for decisions involving:

- product intent
- desired tradeoffs
- preference between valid alternatives
- unacceptable outcomes
- risk tolerance
- scope boundaries

The grill should act like a dependency-aware decision tree rather than a generic interview.

Ask only currently answerable questions whose upstream dependencies are resolved.

---

## Research

Use for external factual uncertainty.

Examples:

- framework/API behavior
- standards
- library constraints
- protocol semantics

Research produces evidence and citations, not authoritative product decisions.

---

## Repository exploration

Use for codebase uncertainty.

Examples:

- current ownership boundaries
- existing abstractions
- test seams
- hidden coupling
- actual call flow

Where useful, preserve findings under `evidence/` so later agents do not repeatedly rediscover the same facts.

---

## Spike

Use when an important unknown cannot be resolved confidently by inspection or research.

Examples:

- performance characteristic
- library interoperability
- concurrency semantics
- feasibility of a new API
- actual device/runtime behavior
- migration edge case

A good spike has:

```yaml
question: Can X satisfy Y under Z?
max_scope: bounded
success_evidence: explicit
production_code: prohibited | optional | candidate
retention: discard | preserve_evidence | candidate_for_rework
```

Its output should include:

- question
- method
- observations
- result
- confidence
- implications for upstream decisions

---

## Does a spike require human review?

Not inherently.

Examples:

### Auto-acceptable spike

Question:

> Does library A expose cancellation through API B?

Agent runs a tiny experiment and records definitive evidence.

No human review is necessarily useful.

### Human-gated consequence

Question:

> Which of two architectures should we adopt given the latency/cost tradeoff demonstrated by the spike?

The spike itself can complete automatically.

The **decision informed by the spike** may require human approval.

This reinforces the distinction:

> Evidence production and decision authority are separate concerns.

---

## Fog-of-war / Wayfinder mode

For genuinely large work, do not require full ticket decomposition before enough architectural decisions are known.

Maintain a frontier of currently resolvable questions.

Conceptually:

```text
known territory
   ↓
current decision frontier
   ↓
resolve one or several decisions
   ↓
new territory becomes visible
```

Only transition into engineering design and ticket compilation once enough uncertainty has collapsed.

This prevents premature decomposition and false precision.

---

## Discovery outputs and skill-writing discipline

Discovery continuously maintains the durable decision ledger and the living PRD; v0.6 removes the
separate translation producer that used to turn discovery into a later specification artifact.

The main discovery skill should keep the universal ordered path inline and disclose
branch-specific procedures or reference material only through precise trigger pointers. Apply the
Writing for Agents pruning rules aggressively: `discovery/SKILL.md` may be up to 400 lines as a
hard ceiling, not a target; remove duplication, no-op instructions, and facts the environment
already owns; never fill available space merely because it is available.
