---
name: to-spec
description: Write the behavioural contract — what must become true, and what must never happen — from a discovery run's decisions. Use after decisions are settled and before any design work, or when the user asks for a spec, requirements, or acceptance criteria.
disable-model-invocation: true
---

# To spec

Compile a decision log into a **behavioural contract**: what must become true, what must never happen, and how anyone would know.

This is the last artifact written in the language of the problem. Everything after it — system design, program design, tickets — speaks the language of the solution. It is also where commitment begins: before this, changing course is free.

Someone who will never build the thing must be able to read it and approve it.

## What may not appear

Class names. File layouts. Method signatures. Internal interfaces. Module structure. Test fixtures, harnesses, commands, or the name of the thing under test.

The test is not whether a detail is *true* — it is whether a reader must know the implementation to judge the requirement. "Responds within 200ms at p95" is behaviour. "The `FeedCache` returns within 200ms" is structure.

## Steps

### 1. Read the decisions

Read `<run>/10-decisions.md`. It is authoritative for what was decided and why — this stage does not re-litigate settled choices, and does not re-interview.

Read the code where it helps establish what is currently true and what vocabulary the domain already uses. Implementation findings from that reading inform the requirements but never enter the contract; where they matter to later stages, write them to `<run>/evidence/` instead.

Where no decision log exists, say so and offer `discovery` rather than inventing decisions.

### 2. Judge whether the decisions are ready

Readiness is about content, never age. A decision made months ago on a stable question is fine; one made yesterday on a question that has since shifted is not.

Return to `discovery` when a **missing or soft decision would change behaviour** — a requirement that cannot be written without guessing what was wanted. Do not guess and flag it; an outcome-changing gap goes back upstream.

Unknowns that do not change behaviour may pass. They belong in the spec's open questions, classified in step 5.

### 3. Write requirements as deltas

Each requirement carries a stable identifier and three parts:

| Part | Content |
|---|---|
| **Current** | What is true today |
| **Target** | What must become true |
| **Acceptance** | The observation that would settle whether it did |

Acceptance names an **observable predicate and its counterexample** — what would have to be seen for this to be satisfied, and what would falsify it. Not a fixture, not a command, not a test name.

> ✗ The system should be fast
> ✓ A feed request returns within 200ms at p95 under normal load; slower than that falsifies it

Size each requirement as **one independently judgeable obligation or invariant**. Ticket compilation happens later and maps requirements to tickets many-to-many, so a requirement is not a unit of work — it is a unit of judgement.

Every requirement records `derived-from: D-NNN`, naming the decisions it rests on. A requirement tracing to no decision is either an undocumented decision — go and record it — or this stage inventing intent, which is the failure this pointer exists to prevent.

Identifiers are assigned once and never reused. A retired requirement's identifier stays retired.

### 4. State what must never happen

A contract of only positive obligations cannot forbid anything. Ask directly:

> What could this silently become that nobody would want?

Overproduce candidates, then keep only the ones specific to *this* work — routine engineering practice and standing policy belong elsewhere. Each kept prohibition becomes a **negative acceptance criterion**, phrased as observably as any other requirement.

Then walk the edges of the requirements now that they are clear — vague requirements have no edges worth probing:

**boundary · adjacency · empty · encoding · ordering · precision · idempotency · concurrency**

Each edge resolves one of three ways: covered by an existing or new requirement, **dismissed with a stated reason**, or recorded as an open question. A dismissal with no reason is not a dismissal.

### 5. Classify what remains open

Every unresolved question is one of two kinds, and saying which is the whole point:

- **Blocking** — the answer changes what must become true. It returns to `discovery`; the spec is not done.
- **Deferred** — the answer belongs to system or program design. It is recorded and passed downstream.

An unclassified open question is an invitation for a later stage to invent behaviour.

### 6. Check the contract against itself

Before offering it for approval, read the draft as a reader who was not in the conversation:

1. Does any requirement require implementation knowledge to judge? That is the leak this stage exists to prevent, and it is easiest to see in the acceptance clauses.
2. Does every requirement trace to a decision?
3. Does every decision that changes behaviour appear as a requirement, an exclusion, or an open question?
4. Do any two requirements contradict?
5. Is every acceptance clause falsifiable — could an observation show it *unmet*?

Then dispatch a subagent that has not seen the conversation to read `20-spec.md` cold and answer the same five questions. It proposes corrections; it does not invent requirements and does not approve.

### 7. Get approval

Present the spec and the open questions. Approval is the user's, on the file as written — not on a summary of it, and not on a score.

A blocking open question means the answer is no. Approving with soft decisions still in play is allowed only where the risk is visible in the document and the user accepts it explicitly.

## The artifact

`<run>/20-spec.md`, resolved under the planning root — see [`../discovery/references/run-layout.md`](../discovery/references/run-layout.md). See [`references/spec-file.md`](references/spec-file.md) for its shape.

## Amending an approved spec

An approved spec is superseded, never quietly edited. Amend by revising the requirement in place with a new revision marker, and **invalidate what traced to it** — the designs and tickets carrying that identifier, not the whole spec.

Scoping invalidation by identifier is what stable identifiers buy. Amending is then cheap enough to actually do, which is the only reason a spec stays true.

## Standing rules

**Decisions are upstream, design is downstream.** This stage compiles; it does not decide and it does not design. A question that wants a decision goes back; one that wants a design goes forward.

**Stories are context, not contract.** Where user stories help a reader understand who wants what, write them — but requirements, constraints, invariants, prohibitions and exclusions carry the obligations. Stories are never the normative text.

**Exclusions carry reasons.** Work deliberately out of scope is recorded with why, or it returns later looking like an oversight.
