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

Both may be true; only the first can be judged by the person approving it, and only the first survives the implementation being replaced.

Five things belong to the design stages and reach the spec only as evidence: class names, file layouts, method signatures, internal interfaces, and implementation structure. Where one feels necessary, it is a Stage 3 or Stage 4 decision arriving early — record it under the run's evidence directory and let those stages own it.

## Steps

### 1. Read the decisions

Read `<run>/10-decisions.md`. It is authoritative for what was decided and why: treat every settled choice as given, and carry its reasoning forward rather than re-deriving it.

The log keeps reversals — a record carrying `status: superseded` was overturned, and the record naming it in `supersedes:` holds the live choice. Follow every chain to its end and compile only what stands there.

Read the code where it helps establish what is currently true and what vocabulary the domain already uses — the **Current** half of every requirement comes from there. Keep what you learn about implementation under `artifacts.evidence_dir` — `evidence/` where that key is unset — beside the run, where Stage 3 will want it.

Where no decision log exists, say so and offer `discovery`.

### 2. Judge whether the decisions are ready

Readiness is about content, never age: a decision made months ago on a stable question is fine, one made yesterday on a question that has since shifted is not.

Return to `discovery` when a decision that would change behaviour is **missing or unsettled** — one you would have to guess at to write the requirement. Unknowns that leave behaviour unchanged pass through to the spec's open questions, classified in step 5.

A decision that was *made* but carries low confidence is neither: it stands, and it is compiled. Carry its confidence onto the items that rest on it, so what the approval is resting on stays visible.

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

Size each requirement as **one independently judgeable obligation**. Ticket compilation maps requirements to tickets many-to-many later, so a requirement is a unit of judgement rather than a unit of work.

Every requirement records `derived-from: D-NNN`, naming the decisions it rests on. A requirement tracing to no decision is either an undocumented decision — go and record it — or this stage inventing intent, which is the failure this pointer exists to prevent.

Every normative item carries an identifier by family — `R-` requirements, `P-` prohibitions, `C-` constraints, `I-` invariants, `X-` exclusions, `Q-` open questions. Identifiers are assigned once and never reused; a withdrawn item leaves a tombstone rather than freeing its identifier.

Done when **every decision in the log is accounted for** — as a requirement, prohibition, constraint or invariant, as an exclusion with its reason, or as an open question. A decision that changed behaviour and appears nowhere is the omission this step exists to catch.

### 4. State what must never happen

A contract of only positive obligations cannot forbid anything. Ask directly:

> What could this silently become that nobody would want?

Overproduce candidates, then keep only those specific to *this* work — routine engineering practice and standing policy belong elsewhere. Each kept prohibition becomes a **negative acceptance criterion**, as observable as any requirement, and reaches the document through the log like everything else.

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

1. Does every normative item hold the outside view? Acceptance clauses leak first.
2. Does every normative item trace to a decision that stands?
3. Does every decision that changes behaviour appear somewhere — obligation, exclusion, or open question?
4. Do any two normative items contradict?
5. For each acceptance clause, name the observation that would show it unmet. A clause with no such observation is an aspiration.

Then dispatch a subagent that has not seen the conversation to read `20-spec.md` and answer the same five questions — it holds the outside view by construction. It proposes corrections; the requirements stay yours and the approval stays the user's.

### 7. Get approval

Approval is the user's, on the file as written rather than on a summary of it. A blocking open question means the answer is no.

Where an item rests on a low-confidence decision, its `Confidence` field says so and the user accepts that explicitly. A decision made on thin ground is approvable; one never made was returned upstream in step 2.

## The artifact

`<run>/20-spec.md`, resolved under the planning root — see [`../discovery/references/run-layout.md`](../discovery/references/run-layout.md). See [`references/spec-file.md`](references/spec-file.md) for its shape.

## Amending an approved spec

An approved spec is an immutable contract: downstream work cites a version, so the approved bytes stay as approved. Amendment adds a new version rather than editing the old one, and `architecture/08-state-and-governance.md` owns the flow — proposed amendment, review policy, recalculated ticket graph, completed work checked for invalidation, stale approvals marked, execution resumed only after re-approval.

The amendment is its own record under `amendments/`, carrying what `architecture/03-artifact-model.md` requires of one. What this stage contributes to it is **the affected section stated as identifiers** — `R-004, P-002` rather than "the caching requirements" — so the flow has a precise input when it recalculates the dependent ticket graph. That precision is what stable identifiers buy, and it keeps amending cheap enough to actually do, which is the only reason a spec stays true.

See [`references/spec-file.md`](references/spec-file.md) for how a version records its amendment.

## The Stage 5 seam

`to-tickets` in this plugin cannot consume this spec: it reads an enumerable `## Work Items` section and stops rather than publish when one is absent. Emitting ticket-sized work items from here would put them back into a behavioural contract, so the break stands until Stage 5 is written. Say so rather than reshaping the spec to fit the legacy consumer.

## Standing rules

**Decisions are upstream, design is downstream.** This stage compiles; it does not decide and it does not design. A question that wants a decision goes back; one that wants a design goes forward.

**Stories are context, not contract.** Where user stories help a reader understand who wants what, write them — but requirements, constraints, invariants, prohibitions and exclusions carry the obligations. Stories are never the normative text.

**Exclusions carry reasons.** Work deliberately out of scope is recorded with why, or it returns later looking like an oversight.
