---
name: to-spec
description: Write the behavioural contract — what must become true, and what must never happen — from a discovery run's decisions. Use after decisions are settled and before any design work, or when the user asks for a spec, requirements, or acceptance criteria.
disable-model-invocation: true
---

# To spec

Compile a decision log into a **behavioural contract**: what must become true, what must never happen, and how anyone would know.

This is the last artifact written in the language of the problem. Everything after it — system design, program design, tickets — speaks the language of the solution. It is also where commitment begins: before this, changing course is free.

## The outside view

Write every line from the **outside view**: what someone observes of the system without knowing how it is built. A requirement holds the outside view when a reader who has never seen the codebase can judge whether it is met.

> The outside view: "a feed request returns within 200ms at p95"
> The inside view: "the `FeedCache` returns within 200ms"

Both may be true. Only the first can be judged by the person approving it, and only the first survives the implementation being replaced.

When a detail feels necessary, it is usually a Stage 3 or Stage 4 decision arriving early — record it in `<run>/evidence/` and let the design stages own it.

## Steps

### 1. Read the decisions

Read `<run>/10-decisions.md`. It is authoritative for what was decided and why: treat every settled choice as given, and carry its reasoning forward rather than re-deriving it.

Read the code where it helps establish what is currently true and what vocabulary the domain already uses — the **Current** half of every requirement comes from there. Keep what you learn about implementation in `<run>/evidence/`, where Stage 3 will want it.

Where no decision log exists, say so and offer `discovery`.

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

Done when **every decision in the log is accounted for** — as a requirement, as an exclusion with its reason, or as an open question. A decision that changed behaviour and appears nowhere is the omission this step exists to catch.

### 4. State what must never happen

A contract of only positive obligations cannot forbid anything. Ask directly:

> What could this silently become that nobody would want?

Overproduce candidates, then keep only the ones specific to *this* work — routine engineering practice and standing policy belong elsewhere. Each kept prohibition becomes a **negative acceptance criterion**, phrased as observably as any other requirement.

Then walk the edges of the requirements now that they are clear — vague requirements have no edges worth probing:

**boundary · adjacency · empty · encoding · ordering · precision · idempotency · concurrency**

Each edge resolves one of three ways: covered by an existing or new requirement, **dismissed with a stated reason**, or recorded as an open question. A dismissal states why the case cannot arise.

Done when every category has been considered against every requirement, and each raised edge carries one of the three resolutions.

### 5. Classify what remains open

Every unresolved question is one of two kinds, and saying which is the whole point:

- **Blocking** — the answer changes what must become true. It returns to `discovery`; the spec is not done.
- **Deferred** — the answer belongs to system or program design. It is recorded and passed downstream.

An unclassified open question is an invitation for a later stage to invent behaviour.

### 6. Check the contract against itself

Before offering it for approval, read the draft as a reader who was not in the conversation:

1. Does every requirement hold the outside view? Acceptance clauses leak first.
2. Does every requirement trace to a decision?
3. Does every decision that changes behaviour appear as a requirement, an exclusion, or an open question?
4. Do any two requirements contradict?
5. For each acceptance clause, name the observation that would show it unmet. A clause with no such observation is an aspiration.

Then dispatch a subagent that has not seen the conversation to read `20-spec.md` and answer the same five questions — it holds the outside view by construction. It proposes corrections; the requirements stay yours and the approval stays the user's.

### 7. Get approval

Approval is the user's, on the file as written rather than on a summary of it. A blocking open question means the answer is no.

Where a soft decision survives into an approved spec, the risk is visible in the document and the user accepts it explicitly.

## The artifact

`<run>/20-spec.md`, resolved under the planning root — see [`../discovery/references/run-layout.md`](../discovery/references/run-layout.md). See [`references/spec-file.md`](references/spec-file.md) for its shape.

## Amending an approved spec

Revise the changed requirement and bump its revision, then **invalidate by identifier** — the designs and tickets citing it, and nothing else. Scoping invalidation this way is what stable identifiers buy, and it keeps amending cheap enough to actually do, which is the only reason a spec stays true. See [`references/spec-file.md`](references/spec-file.md).

## Standing rules

**Decisions are upstream, design is downstream.** This stage compiles; it does not decide and it does not design. A question that wants a decision goes back; one that wants a design goes forward.

**Stories are context, not contract.** Where user stories help a reader understand who wants what, write them — but requirements, constraints, invariants, prohibitions and exclusions carry the obligations. Stories are never the normative text.

**Exclusions carry reasons.** Work deliberately out of scope is recorded with why, or it returns later looking like an oversight.
