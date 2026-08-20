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

Read immutable `run.yaml`, accepted `amendments/run-config-NNN.yaml`, and mutable `00-state.md` first. Reconstruct effective intake in amendment order. Record `effective_config_revision` in the spec from state. Specification must be selected by the effective run and be the current phase. Read the resolved policy from effective `gates.spec`, including `authority` and all operands; if intake is missing, revisions disagree, or state has not legally advanced from discovery, stop rather than treating invocation as approval.

Read `<run>/10-decisions.md` and require `status: approved`; `approved_copy` must resolve to a run-contained file and `approved_sha256` must verify its exact bytes. Read that immutable approved copy as the authoritative contract for what was decided and why; never compile from the mutable top-level working file after its hash check.

The log keeps reversals — a record carrying `status: superseded` was overturned, and the record naming it in `supersedes:` holds the live choice. Follow every chain to its end and compile only what stands there.

Read the code where it helps establish what is currently true and what vocabulary the domain already uses — the **Current** half of every requirement comes from there. Keep what you learn about implementation under `<run>/evidence/`, where Stage 3 will want it. The run layout is fixed; only the planning root above it is configurable.

Where no decision log exists, say so and offer `atlas:discovery`; where no run exists, offer `atlas:start-run`.

### 2. Judge whether the decisions are ready

Readiness is about content, never age: a decision made months ago on a stable question is fine, one made yesterday on a question that has since shifted is not.
When a decision that would change behaviour is **missing or unsettled** before drafting — one you would have to guess at to write the requirement — route to `atlas:control-run` with a concrete reopen reason. Its deterministic `reopen --to discovery` transition marks approvals stale and returns the current phase legally. Unknowns that leave behaviour unchanged pass through to the spec's open questions, classified in step 6.

A gap that only surfaces once drafting is under way is recorded as a blocking question rather than abandoning the draft. Finish the spec, leave `gate_ready: false`, and route the persisted reason to `atlas:control-run` for the same legal reopen — the draft is what makes the gap legible.

So a spec can be complete and unapprovable at once: everything written, one question still open, `status: draft`. That is the intended end state of such a run, not a half-finished job.

A decision that was *made* but carries low confidence is neither: it stands, and it is compiled. Carry its `Confidence` onto the items that rest on it, and the decision's reopening condition into their `Reopens if` — that condition is where the risk actually lives, and the spec is where someone will look for it later.

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

Each records `derived-from: D-NNN`, naming the decisions it rests on. An item tracing to no decision is either an undocumented decision — go and record it — or this stage inventing intent, which is the failure this pointer exists to prevent.

Every normative item carries an identifier by family — `R-` requirements, `P-` prohibitions, `C-` constraints, `I-` invariants, `X-` exclusions, `Q-` open questions — assigned in order and never reused, because downstream artifacts cite them and one that changes meaning silently invalidates everything citing it.

Not every decision becomes an obligation. One settled because the outcome is impossible — a platform that cannot do the thing at all — has no observation that could falsify it, and writing it as a prohibition produces a clause that is trivially always true. That decision is an **exclusion** carrying the reason.

Done when **every decision in the log is accounted for** — as a requirement, prohibition, constraint or invariant, as an exclusion with its reason, or as an open question. A decision that changed behaviour and appears nowhere is the omission this step exists to catch.

### 4. State what must never happen

A contract of only positive obligations cannot forbid anything. Ask directly:

> What could this silently become that nobody would want?

Overproduce candidates, then keep only those specific to *this* work — routine engineering practice and standing policy belong elsewhere. Each kept prohibition becomes a **negative acceptance criterion**, as observable as any requirement.

A prohibition the log implies — "don't hold anything back" implying that no interim message may be delayed — cites the decision that implies it. One the log does not support at all is an unrecorded decision: take it back to `discovery` rather than writing it here.

### 5. Walk the edges

Now that the requirements are clear — vague requirements have no edges worth probing — test each against every category:

**boundary · adjacency · empty · encoding · ordering · precision · idempotency · concurrency**

Ask of each category what it would mean *here*, not of every requirement in turn — the unit is the distinct case, not the pair. Twelve requirements against eight categories is eight questions, not ninety-six.

Worked, for a requirement that files are copied from a card to an archive:

| Category | The question it asks here | Outcome |
|---|---|---|
| boundary | a file exactly at the size or age limit | covered by R-003 |
| adjacency | a file just inside and just outside the retention window | new requirement |
| empty | a card holding no new files | new requirement — the run must report, not fail |
| encoding | filenames with non-ASCII characters | dismissed: the archive stores bytes and never parses names |
| ordering | two cards imported out of sequence | dismissed: each import is independent |
| precision | timestamps at second versus sub-second resolution | open question |
| idempotency | the same card imported twice | covered by R-005 |
| concurrency | two cards mounted at once | new prohibition |

Three of those existed already, three became new items, one was dismissed with its reason, one stayed open. That distribution is normal.

Each edge resolves one of three ways: covered by an existing or new requirement or prohibition, **dismissed with a stated reason**, or recorded as an open question. A dismissal states why the case cannot arise.

Done when every category has been considered and each raised edge carries a resolution. A category that raises nothing carries a row saying so — considered-and-empty and never-considered must not look alike.

### 6. Classify what remains open

Every unresolved question is one of two kinds, and saying which is the whole point:

- **Blocking** — the answer changes what must become true. It returns to `discovery`; the spec is not done.
- **Deferred** — the answer belongs to system or program design. It is recorded and passed downstream.

An unclassified open question is an invitation for a later stage to invent behaviour.

### 7. Check the contract against itself

Before declaring it ready for its configured gate, read the draft as a reader who was not in the conversation:

1. Does every normative item hold the outside view? Acceptance clauses leak first.
2. Does every normative item trace to a decision that stands?
3. Does every decision that changes behaviour appear somewhere — obligation, exclusion, or open question?
4. Do any two normative items contradict?
5. For each acceptance clause, name the observation that would show it unmet. A clause with no such observation is an aspiration.

Then dispatch a subagent that has not seen the conversation to read `20-spec.md` and answer the same five questions — it holds the outside view by construction. It proposes corrections; the producing skill decides whether they are defects, while the configured gate owns progression.

### 8. Report gate readiness

Leave the artifact at `status: draft` and present the file itself, not a summary, with its readiness evidence and the resolved policy from effective `gates.spec`. Set `gate_ready: true` only when no blocking open question or contract defect remains; otherwise leave it false and return to discovery.

Route a gate-ready draft to `atlas:control-run`. That control-plane skill applies the policy, marks approval, and advances mutable state; this skill does not.

Where any item rests on a low-confidence decision, its `Confidence` field says so for the configured authority to judge explicitly. A decision made on thin ground can still pass a gate; one never made was returned upstream in step 2.

The control plane invokes the resolved authority — AUTO, AGENT_REVIEW, HUMAN, CONDITIONAL, or HUMAN_IF_CHANGED — and applies the gate state and phase transition. This skill never marks its own output approved.

## The artifact

`<run>/20-spec.md`, resolved under the planning root — see [`../discovery/references/run-layout.md`](../discovery/references/run-layout.md). See [`references/spec-file.md`](references/spec-file.md) for its shape.

## Amending an approved spec

A valid control-plane gate outcome sets `status: approved` and writes the `approved` date. Until then it stays `draft`.

While authoring, `approved`, `approved_authority`, `approved_copy`, and `approved_sha256` must remain null. Only deterministic `tools/atlas_control.py` writes those approval-receipt fields; this skill reads and verifies the discovery receipt but never manufactures one for the specification.

A withdrawn item keeps its identifier and leaves a **tombstone** in place — a heading-backed item keeps its heading with the body replaced by `Withdrawn in version N — <why>`, a row-backed item keeps its row with the remaining cells replaced by the same sentence. That is what makes reuse visibly wrong.

An approved spec is immutable in the controller-written `approved/spec-r<state-revision>.md` copy whose SHA-256 is recorded in the top-level receipt. In the currently implemented candidate contract, `version` must be `1`, `supersedes` must be null, and `amendment` must be null. A future specification-amendment transition is not implemented in this plugin; when added, it must preserve that approved copy and define deterministic predecessor/amendment provenance under the flow owned by `architecture/08-state-and-governance.md`. Until then, this skill and controller reject non-null values rather than inventing that future schema.

What this stage contributes is **the affected section stated as identifiers** — `R-004, P-002` rather than "the caching requirements" — so that flow has a precise input when it recalculates what is stale.

## Standing rules

**Decisions are upstream, design is downstream.** This stage compiles; it does not decide and it does not design. A question that wants a decision goes back; one that wants a design goes forward.

**Stories are context, not contract.** Write them where they help a reader understand who wants what; the normative families carry the obligations.

**Exclusions carry reasons.** Work deliberately out of scope is recorded with why, or it returns later looking like an oversight.

**Policy owns progression.** Read gate authority from immutable intake; never infer it from the fact that a human invoked this skill or discussed the draft.
