# 13 — Runtime Protocol, State, and Evidence

## Durable contracts vs runtime protocol

Markdown remains ideal for decisions, the living product PRD, system design, program design,
vertical tickets, amendments, and durable evidence summaries.

Phase-to-phase communication should use typed, schema-validated envelopes.

## Example builder envelope

```json
{
  "ticket": "async-jobs-03",
  "phase": "builder",
  "result": "completed",
  "changed_files": [
    "src/JobScheduler.cs",
    "tests/JobSchedulerTests.cs"
  ],
  "contract_deviations": [],
  "blockers": [],
  "evidence": ["evidence/build-03.json"]
}
```

## Example reviewer envelope

```json
{
  "ticket": "async-jobs-03",
  "phase": "contract_review",
  "candidate_tree_identity": "<canonical identity>",
  "verdict": "reject",
  "findings": [
    {
      "severity": "blocking",
      "contract_ref": "tickets/03.md#acceptance-2",
      "problem": "Cancelled jobs may still dispatch",
      "evidence": "..."
    }
  ]
}
```

Deterministic code consumes these envelopes and decides which state transition is legal.

## Planning control state before execution

Stages 0–2 use `<planning-root>/<feature>/control.json` as their machine-canonical planning
state. It records only planning phase/gate outcomes and version/hash provenance. In v0.6 the
accepted product-contract candidate is `20-prd.md`, and its `derived_from` field binds the exact
`10-decisions.md` version/hash product closure reconciled. This closes the initial planning
authority gap for an effort that may span repositories without putting repository-scoped execution
state in the planning root. `00-state.md` is generated from this file and is never transition
authority.

After that handoff, one downstream planning controller owns the selected Stage 3–5 candidate
bindings, separate gate outcomes, dependency/staleness chain, and final accepted ticket-graph
binding. Its accepted graph names every applicable accepted upstream source and the frozen baseline
for each target repository. The controller records upstream changes and all directly caused
downstream invalidations as one logical atomic transition. Architecture does not fix its exact file,
storage representation, schema, or module/CLI decomposition.

The downstream planning controller ends at Stage 5. It hands execution an exact accepted
ticket-graph version/hash; it owns no Stage 6+ execution worktree, active-ticket, execution-attempt,
retry, execution-repair, validation, commit, branch, or event state. D-082's bounded Stage 3→4
planning-repair episode and producer-attempt budget remain pre-execution planning control, not
execution state. No separate compilation controller exists.

## Machine-canonical runtime state

Suggested runtime layout:

```text
.factory/
  runs/
    <run-id>/
      run.json
      events.jsonl
      envelopes/
      evidence/
      logs/
```

`run.json` (or its Program Design equivalent) is the machine-canonical repository-scoped execution
record. `events.jsonl` may preserve ordered observation/telemetry, but it is not transition or state
authority. Authority-bearing updates use a closed schema and atomic replacement, or another minimal
mechanism with equivalent no-intermediate-contradiction semantics. This rule does not freeze an exact
file/schema/module design.

The conceptual V1 minimum is only what restart and revalidation require:

```text
run identity
accepted graph version/hash
repository identity + frozen baseline
expected accepted-chain head
canonical candidate-tree identity for the active attempt
active ticket or none
authoritative state for every ticket assigned to that repository
accepted or terminal completion + associated accepted commit/tree and evidence binding
bounded attempt counters
wait/block reason
resolved worker identity
builder session handle when the substrate exposes one
evidence/envelope references
```

Across all repository-scoped records bound to one accepted graph, at most one ticket is active. The
trusted supervisor selects the first currently ready ticket in global canonical order and records it
as active only in the repository-scoped run named by that ticket. A repository-scoped record cannot
select, admit, or execute a foreign-repository ticket. Parallel admission remains deferred.

On restart, the trusted supervisor combines the accepted graph, authoritative state for every ticket
assigned to each repository, and current external-condition evidence to reconstruct prerequisite
satisfaction and determine the only legal next action after restart. Events and the last accepted
commit/tree are not substitutes for authoritative ticket completion; Git reality is reconciled as
currency/evidence rather than promoted into workflow authority.

Do not add a queue, lease scheduler, event-sourced workflow database, generalized WIP system, or
disposable-environment fields before a runtime exists that consumes them.

A generated `<planning-root>/<feature>/00-state.md` may remain useful as a projection, but it is not
authoritative for attempt counts, active ownership, retry state, or exact state transitions.

`control.json` does not replace this execution protocol. Once compiled work executes, each
repository-scoped factory run owns its runtime record, events, envelopes, evidence, and logs under
that repository's `.factory/runs/` directory.

## Evidence-bearing waits and blockers

A blocker is a claim about the world. `continue` or `resume` wakes revalidation; it never satisfies
the claim. A durable wait/block record carries or references:

```text
condition identity
observable satisfaction rule
last check + observed result
relevant artifact/external reference
checked-at time where meaningful
resume/recheck action
```

The owner stores enough evidence to rerun the cheapest accepted check. V1 adds no sensor registry,
background polling, webhook, daemon, or event bus.

## Deterministic proof receipts

A proof receipt must be sufficiently bound to answer:

```text
which run/ticket/graph and expected accepted-chain HEAD were checked?
which canonical candidate-tree identity supplied the exact bytes under validation?
what validator semantics ran?
what baseline expectation applied when declared?
what happened and what evidence was produced?
```

Before ticket gates begin, deterministic code derives one canonical candidate-tree identity from the
exact bytes proposed for commit, including every admitted tracked and untracked path. Program Design
may choose the Git/index mechanism; architecture fixes only the identity/equality obligation. Every
validator and ticket reviewer binds that same identity. Any candidate-byte change stales those gates
and requires a new identity plus rerun.

Preserve an exact command or stable validator-definition identity, verdict/result, and
output/artifact references. Preserve environment and worker identity only where proof meaning depends
on them. V1 reruns checks; it does not add proof reuse, invalidation hashing, proof caching, or an
environment-equivalence subsystem.

## Evidence harvest and completion layers

Before destructive cleanup removes the only remaining source of execution facts, durably harvest the
required commit/tree identity, worker/reviewer envelopes, validator outcomes, blockers and
`DESIGN_BLOCKED` evidence, required logs/artifacts, runtime-produced bindings, and supported recovery
locator. If harvest fails, retain the source and record a lifecycle blocker.

Local implementation completion, PR/CI/package/deployment readiness, and downstream repository
readiness are separate facts. A local accepted commit cannot manufacture an external fact or satisfy
a downstream readiness condition.

## Runtime state vs engineering truth

```text
ENGINEERING TRUTH
"what did we decide?"
→ versioned planning contracts

RUNTIME TRUTH
"what is executing right now?"
→ machine state / events / envelopes
```
