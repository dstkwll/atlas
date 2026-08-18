---
name: spike
description: Answer a question by running a bounded experiment, when inspection and research cannot settle it. Use when feasibility, performance, interoperability, concurrency, or actual runtime behaviour is the open question, or when discovery routes a question here.
disable-model-invocation: true
---

# Spike

A bounded experiment whose output is **knowledge**, not production code.

Reach for a spike when the answer exists nowhere yet — not in the user's head, not in documentation, not in this codebase. It has to be created by observing behaviour.

The discipline that makes a spike worth running: **what would count as a negative result is written down before anything runs.** An experiment that cannot come back negative has measured nothing.

## Steps

### 1. State the hypothesis

One claim, in Given/When/Then form:

> **Given** <preconditions and system state>
> **When** <the action or change>
> **Then** <the expected observable outcome>

A question too broad for a single Given/When/Then is too broad to spike — narrow it. A question that splits into two unrelated claims is two spikes.

Where the spike was routed here by `discovery`, the hypothesis restates that question. Where it was invoked directly, agree the hypothesis with the user before continuing.

### 2. Design the experiments

Two to five experiments that together test the hypothesis. Each carries four things, and the third is what makes this a spike rather than a session of poking at things:

| Field | Content |
|---|---|
| **Claim** | The sub-claim this experiment tests |
| **Method** | Working commands or code, not pseudocode |
| **Verdict criteria** | What output would **validate**, and what output would **invalidate**. Both, stated concretely, before running |
| **Side effects** | `read-only`, or the specific mutations it performs |

Where experiments are sequenced — a later one depending on an earlier verdict — say so explicitly.

State the bounds before running: the maximum scope, whether production code may be written (`prohibited`, `optional`, or `candidate`), and what happens to the artifacts afterward (`discard`, `preserve_evidence`, or `candidate_for_rework`).

### 3. Get approval before running anything with side effects

Present the plan: hypothesis, experiments, verdict criteria, bounds. Then stop.

`read-only` experiments — reads, greps, queries, and writes confined to the spike's own directory — run once the plan is approved.

Anything else names its side effects and gets its own confirmation immediately before it runs. Where an experiment's category is uncertain, treat it as having side effects.

**The plan is the gate.** No runtime enforces these categories; the declaration is self-policed, which is exactly why the plan is approved as a whole before any of it runs.

### 4. Run and record as you go

Record each experiment's method, actual output, and verdict in the findings file at the moment it completes. A run whose output is summarized from memory afterward is worth less than one written down as it happened.

Per-experiment verdict: `VALIDATED`, `INVALIDATED`, or `PARTIAL`, each with the concrete evidence — output excerpts, file paths, error strings, measured numbers.

An experiment that fails to run is not an `INVALIDATED` hypothesis. It is a broken experiment: fix it, or record that the method could not be executed and say what that leaves unknown.

### 5. Synthesize the verdict

The overall verdict follows the per-experiment results:

| Per-experiment verdicts | Overall |
|---|---|
| All `VALIDATED` | `VALIDATED` |
| Any `INVALIDATED` | `INVALIDATED` — the failure mode is the headline |
| `VALIDATED` and `PARTIAL` mixed | `PARTIAL` |
| Experiments contradict each other | `MIXED` |

Then state, in this order: what the spike now knows, what it does **not** know, and what it implies for the decision that prompted it.

An `INVALIDATED` verdict is a successful spike. It cost an experiment to learn something that would otherwise have cost an implementation.

## Findings file

One file per spike, at `<run>/spikes/<name>/findings.md`. Where the spike runs outside a discovery run, ask where it belongs rather than choosing a path.

```markdown
---
spike: <name>
hypothesis: <one line>
verdict: VALIDATED | INVALIDATED | PARTIAL | MIXED
production_code: prohibited | optional | candidate
retention: discard | preserve_evidence | candidate_for_rework
date: 2026-08-16
---

# Spike: <the question>

## Hypothesis
**Given** <preconditions>, **When** <action>, **Then** <expected outcome>.

## Experiments

### 1 — <name>
**Claim:** <sub-claim>
**Side effects:** read-only | <named mutations>
**Verdict criteria:** validates if <concrete>; invalidates if <concrete>
**Method:**
```
<commands or code, as run>
```
**Output:** <what actually came back>
**Verdict:** VALIDATED | INVALIDATED | PARTIAL
**Evidence:** <excerpt, path, number>

## Findings

**Verdict:** <overall>

**What this establishes:** <the claim now supported, and how strongly>

**What remains unknown:** <what the spike did not settle, including anything an
experiment failed to test>

**Implication:** <what the decision that prompted this should do with it>
```

## Standing rules

**Write the criteria before the run.** An experiment whose success condition is decided after seeing the output has no failure mode.

**Report the number you measured.** Not the number you expected, not a rounded impression of it. Where a measurement is noisy, say how noisy.

**Throwaway code stays throwaway.** Spike code is named so a reader can see what it is, and it does not migrate into production because it happens to work. What survives a spike is the finding; the code is evidence, retained or discarded per the declared bound.

**A spike answers its question and stops.** Adjacent things worth knowing become follow-up questions for whoever routed here, not extra experiments in this run.
