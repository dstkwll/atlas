---
name: discovery
description: Resolve the open decisions a piece of work waits on, before specification. Use when starting a feature, a change, or a fuzzy idea; when the user asks to think something through, work out what to build, or decide how to approach it; or when resuming a discovery run.
disable-model-invocation: true
---

# Discovery

Work a fuzzy goal down to resolved decisions. Every decision, its options, and why it went the way it did lands on disk as it happens — the run survives the session it started in, and the log outlives the run.

This is the stage before specification. It produces **decisions and evidence**, not a specification and not code.

`to-spec` reads this log and compiles it into the behavioural contract at `20-spec.md`. It does not re-interview, and it returns here when a missing or soft decision would change behaviour.

## The frontier

The **frontier** is every open question whose prerequisites are already settled — the questions answerable *now*, without guessing at answers not yet heard.

Work in rounds: ask the whole frontier at once, numbered. The replies settle those questions, unblocking the ones that depended on them. Recompute, ask again.

Each question carries its options and a recommended answer. Where you have no recommendation worth the name, say so and ask for the instinct first — a manufactured recommendation on a question you cannot judge is worse than none, and the answer to a question asked honestly is usually the sharpest one in the round.

A question depending on another still open belongs to a later round and names what it waits on in `blocked_by`. Discovery is ready for its configured gate when the frontier is empty and the bounded cold read is resolved; the skill does not advance its own phase.

## Where the answer lives

Each open question resolves by one of four routes, chosen by where its answer already is:

| Route | The answer lives | How it resolves |
|---|---|---|
| **grill** | In the user's head | Ask them. Preference, priority, taste, risk appetite. |
| **research** | In the outside world | Dispatch a subagent. Documentation, third-party behaviour, prior art. |
| **explore** | In this codebase, already true | Dispatch a subagent to read it and report. |
| **spike** | Nowhere yet | Invoke `spike`. The answer must be created by running an experiment. |

Only **grill** questions go to the user. Finding facts is your job: dispatch rather than ask for anything you could look up.

Dispatched routes do not block the round — only the questions downstream of an investigation wait. An **explore** question answered by guessing is the most expensive failure here, because every decision downstream inherits the guess.

## Steps

### 1. Resume or open the run

Resolve a run already created by `atlas:start-run`, then reconstruct effective intake from immutable `run.yaml` plus accepted `amendments/run-config-NNN.yaml`, and read mutable `00-state.md`. Discovery must be selected by the effective run and be the current phase. If intake is absent or state does not name the latest accepted effective-config revision, stop and return to Stage 0 rather than manufacturing it here; an artifact's stale marker follows the explicit recovery rule below.

If an existing decision log has `intake_stale: true` and state now names a later `effective_config_revision`, revalidate every persisted scope finding against the effective `repos` repository-baseline pairs. Clear `intake_stale`, copy the current `effective_config_revision`, and resume only when every affected repository and baseline is represented. Otherwise leave both fields unchanged and return to Stage 0. This explicit revalidation is the only recovery path; elapsed time or the presence of an amendment is not proof.

Read `<run>/10-decisions.md` if it exists and continue from the open frontier recorded there, never re-asking a settled decision. If it names an `approved_copy`, verify `approved_sha256`; edit the working file only after deterministic `atlas:control-run` has legally reopened it as a new draft version. Otherwise create only that file inside the existing run. See [`references/run-layout.md`](references/run-layout.md) for the fixed location and initial shape.

### 2. Test whether the work is worth doing

Two challenges before any question is asked. Either can justify a recommendation to stop, and both outcomes are legitimate results — record either as the run's first decision and present the recommendation to the discovery gate named in `run.yaml`.

**The problem test.** Name the problem in the words of whoever has it. Then: what happens if nothing is built? Is there a framing under which this problem dissolves or belongs to something else?

**The announcement test.** Write three to six sentences announcing the finished thing to the people it is for. A version that cannot be written is a version worth challenging — say so plainly and give the reason.

### 3. Chart the opening frontier

Propose candidate shapes the work might take, and read the forks out of them. A question is generated by a candidate answer: without a shape in mind, the questions come out generic.

A candidate shape becomes settled only when the user decides it, through a decision record. Keep candidates at the level of approach, boundaries, and behaviour — file names, signatures, and schemas are later stages leaking upward, and proposing them makes an unsettled design feel settled.

Write the opening frontier into `10-decisions.md` before asking anything.

### 4. Run the round

Number each grill question, state it, and give a recommended answer:

```
❓ **Q3 — <short title>**: <the question, with options where they exist>

➡️ **Recommended:** <your answer, and the reason>
```

Dispatch the research, explore, and spike questions in the same round. Then wait for the user's replies.

Supply options the user had not considered, and argue against the ones they had.

The log's frontmatter records its `run`, quoted canonical `opened` date, `repos`, and `effective_config_revision` values from effective intake and state. It owns the boolean `intake_stale` and `gate_ready` fields plus `cold_read`; these are readiness evidence, not workflow state. The initial and reopened frontmatter schemas are exact and reject extra fields. A reopened draft additionally retains the controller-written `supersedes` path naming the active immutable approved discovery copy. See [`references/run-layout.md`](references/run-layout.md) for both exact shapes and the fixed run location.

### 5. Record every decision as it is made

Append a decision record the moment a question settles — before the next round, not at the end of the run. Each carries an `id` assigned in order and never reused, since later artifacts cite it; the `route` that settled it; `status: settled`; and the `decided` date. See [`references/decision-record.md`](references/decision-record.md) for the required shape.

A record holds why the question needed deciding, the options with the case for each, what you recommended, what was chosen, the decider's reasoning, and what would reopen it. Preserve the user's own words when they decided; cite the evidence when research, exploration, or a spike resolved it. The options not taken and the reopening condition are the two a later reader needs most and the two easiest to skip.

`origin` is a required field, and it distinguishes four cases: the user originated the answer, rejected your recommendation for a different one, accepted it, or the question never reached them because you resolved it by reading or by measuring. A spike-routed record names the `findings` file it produced, so the pair is navigable from either end. A log that blurs these teaches a reader your judgement wearing the user's name — and a rejected recommendation, recorded alongside what was rejected, is the most informative record in the log.

Inside a draft, reversing a settled decision writes a new record carrying `supersedes:` and flips the old one to `status: superseded`. Both edits, or a consumer following the fields compiles the reversed choice as live. If discovery was already approved, first invoke `atlas:control-run` to apply the legal `spec -> discovery` reopen; its deterministic program preserves the approved copy and creates a versioned working draft before this skill edits it.

Update the open frontier in the same edit: settled questions leave it, and its `unblocked` field records the ones that join. Where a decision reveals a repository or baseline absent from effective intake, record the scope finding, set `intake_stale: true` and `gate_ready: false`, and leave immutable intake unchanged; then route to `atlas:control-run mark-stale` with the persisted reason. Its deterministic transition blocks the run and names the next amendment; return to Stage 0 before progression.

### 6. Repeat until the frontier is empty

Recompute the frontier after each round and return to step 4.

### 7. Grade the decisions

Walk the log once the frontier is empty. Grade each record's actual contribution to the resolved design — load-bearing, minor, or irrelevant in hindsight — and append it to the record.

Compare each grade against the confidence the record carries: a low-confidence decision that turned out load-bearing is the most useful entry in the log, and so is a confident one that turned out not to matter.

Finish the readiness evidence by naming the least confident decisions that survived, so the configured discovery gate knows where the design is softest.

### 8. Have the log read cold

The frontier was computed by the agent that ran the conversation, so an empty frontier is a checker's verdict on its own work. Dispatch a subagent that has not seen the conversation to read `10-decisions.md` and answer two questions:

1. Does any decision open a consequence that no question addressed?
2. Is any decision unsupported by its own stated reasoning?

Brief it on the artifact, not the conclusions — it reads the log, never a summary of how the run went.

**One pass, and it proposes rather than reopens.** Route each finding by where its answer lives: factual gaps return to research, exploration, or spike; preference and trade-off gaps return to grill. Record the resulting decision. Findings that survive their route return to the frontier for one further round, which is not itself re-reviewed.

When that round is complete, set `cold_read: complete` and `gate_ready: true` while leaving `status: draft`. Keep candidate `version` as a positive integer starting at 1; a deterministic reopen increments it for the next working draft. Report the file and name the effective policy at `gates.discovery`, including its `authority` and operands. Route to `atlas:control-run`; it evaluates that policy, applies the gate outcome, marks approval, and advances the phase. This skill never marks itself approved or advances to specification.

`approved`, `approved_authority`, `approved_copy`, and `approved_sha256` must remain null while discovery authors the candidate. Only deterministic `tools/atlas_control.py` writes those approval-receipt fields.

## Standing rules

**Nothing important exists only in the conversation.** A fresh session with no memory of it must resume from `10-decisions.md` alone. Check that at every round boundary, and immediately if context runs low.

**Decisions are the output.** Not a specification, not a requirements document, not code. Writing a specification here duplicates the stage that owns it and invites the two to drift.

**Backtrack in the open.** When a later answer invalidates a settled decision, say so, supersede that record with a new one naming what changed, and return the reopened question to the frontier. Superseded records stay — the reversal is the interesting part.

**Policy owns progression.** Read gate authority from immutable intake. Human conversation may supply grill decisions, but that does not silently turn every stage boundary into a human gate.
