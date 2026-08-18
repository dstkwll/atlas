---
name: spike
description: Answer a question by running a bounded experiment, when inspection and research cannot settle it. Use when feasibility, performance, interoperability, concurrency, or actual runtime behaviour is the open question, when comparing two approaches empirically, or when discovery routes a question here.
disable-model-invocation: true
---

# Spike

A bounded experiment whose output is **knowledge**, not production code.

Reach for a spike when the answer exists nowhere yet — not in the user's head, not in documentation, not in this codebase. It has to be created by observing behaviour.

## Steps

### 1. Decompose into spikes, ordered by risk

Break the question into two to five independent feasibility questions. Each is one spike, and each gets a Given/When/Then hypothesis:

> **Given** <preconditions and system state>
> **When** <the action or change>
> **Then** <the expected observable outcome>

Present them as a table with a risk column, then **order by risk: the spike most likely to kill the idea runs first.** There is no point proving the easy parts if the hard part fails.

Two shapes:

- **Standard** — one approach answering one question.
- **Comparison** — one question, competing approaches, sharing a number with letter suffixes (`002a`, `002b`). Build them back to back and close with a head-to-head table.

A question too broad for a single Given/When/Then is too broad to spike; one that already arrives narrow — as when `discovery` routes it here — is a single spike and skips decomposition.

Present the table and ask whether to run all of them in this order. Let the user drop, reorder, or reframe before anything is written.

### 2. Design the experiments

For each spike, two to five experiments in the shape the findings template below sets out: claim, method as working commands rather than pseudocode, side effects, and — the field that separates a spike from poking at things — **what output would validate and what would invalidate, both written before the run**.

Where a spike has real choice of approach, surface the candidates first — tool, maturity, what each costs — pick one, and say why. Where two are genuinely credible, that is a comparison spike, not a coin flip. Skip this for pure logic with no external dependency.

State the bounds before running: maximum scope, whether production code may be written (`prohibited`, `optional`, or `candidate`), and what happens to the artifacts afterward (`discard`, `preserve_evidence`, or `candidate_for_rework`).

### 3. Get approval before running anything with side effects

Present the plan: hypotheses, experiments, verdict criteria, bounds. Then stop.

`read-only` experiments — reads, greps, queries, and writes confined to the spike's own directory — run once the plan is approved.

Anything else names its side effects and gets its own confirmation immediately before it runs. Where an experiment's category is uncertain, treat it as having side effects.

**The plan is the gate.** No runtime enforces these categories; the declaration is self-policed, which is exactly why the whole plan is approved before any of it runs.

### 4. Build something the user can drive

One directory per spike, standalone, hardcoded. Preference order for the artifact:

1. A runnable command that takes input and prints observable output
2. A single HTML page demonstrating the behaviour
3. A small server with one endpoint
4. A test exercising the question with recognizable assertions

Avoid package management, build tooling, containers, and config systems unless the question is about them. It is a spike.

**Depth over speed.** One happy-path run is not a verdict. Push the edge cases, and follow anything surprising — a verdict is only worth what the investigation behind it was worth.

### 5. Record as you go

Record each experiment's method, actual output, and verdict at the moment it completes. A run summarized from memory afterward is worth less than one written down as it happened.

Per-experiment verdict: `VALIDATED`, `INVALIDATED`, or `PARTIAL`, each with concrete evidence — output excerpts, file paths, error strings, measured numbers.

An experiment that fails to run is not an `INVALIDATED` hypothesis. It is a broken experiment: fix it, or record that the method could not be executed and say what that leaves unknown.

### 6. Synthesize the verdict

The overall verdict follows the per-experiment results:

First rule that matches wins:

1. Experiments contradict each other → `MIXED`
2. Any `INVALIDATED` → `INVALIDATED`, and the failure mode is the headline
3. Any `PARTIAL` → `PARTIAL`
4. All `VALIDATED` → `VALIDATED`

Then state, in this order: what the spike now knows, what it does **not** know, and what it implies for the decision that prompted it.

An `INVALIDATED` verdict is a successful spike. It cost an experiment to learn something that would otherwise have cost an implementation.

## Findings file

One file per spike, under the run's spikes directory — `artifacts.spikes_dir` beneath the planning root, resolved as `discovery/references/run-layout.md` describes. Never hardcode a path.

See [`references/findings-file.md`](references/findings-file.md) for its shape.

## Standing rules

**Write the criteria before the run.** An experiment whose success condition is decided after seeing the output has no failure mode.

**Report the number you measured.** Not the number you expected, not a rounded impression of it. Where a measurement is noisy, say how noisy.

**Throwaway code stays throwaway.** Spike code is named so a reader can see what it is, and it does not migrate into production because it happens to work. A spike that takes two days to clean up was a bad spike. What survives is the finding; the code is evidence, retained or discarded per the declared bound.

**A spike answers its question and stops.** Adjacent things worth knowing become follow-up questions for whoever routed here, not extra experiments in this run.
