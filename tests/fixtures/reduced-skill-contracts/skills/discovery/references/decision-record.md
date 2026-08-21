# Decision record

The required shape of every entry in `10-decisions.md`. Appended the moment a question settles, never batched to the end of the run.

The log is read twice: by the discovery producer maintaining `20-prd.md`, which needs the live decisions and their provenance, and by a later reader studying how decisions get made. The second reader is why options not taken, reasoning, and confidence are required — a record of the choice alone teaches nothing about the choosing, and one too thin to reconstruct the moment is worth less than one that repeats itself.

## Shape

````markdown
### D-007 — <the question, as a question>

```yaml
id: D-007
route: grill              # grill | research | explore | spike
findings: null            # spike route only: path to the findings file it produced
status: settled           # settled | superseded
decided: <YYYY-MM-DD>
origin: user-originated   # user-originated | user-rejected | accepted-recommendation | agent-resolved
confidence: medium        # high | medium | low
unblocked: [D-011, D-012]
blocked_by: [D-003]
supersedes: null
contribution: null        # filled in at the grading pass
```

**Why this needed deciding:** <what was ambiguous, and what downstream work was waiting on it>

**Options considered:**

1. **<option>** — <the case for it, and its cost>
2. **<option>** — <the case for it, and its cost>

**Recommended:** <what the agent recommended, and why>

**Chosen:** <what was chosen>

**Reasoning:** <the decider's reasoning, in their words where they gave it. Where they accepted a
recommendation without adding reasoning, say exactly that rather than restating the recommendation
as though they had argued it.>

**Reopens if:** <the observation or change that would make this worth revisiting>
````

## Fields that carry weight

**`origin`** records where the choice came from. `user-originated` — they answered outside the options offered. `user-rejected` — they were given a recommendation and took a different option, or supplied one of their own; record what was recommended as well as what was chosen, because the rejection is the most informative thing in the record. `accepted-recommendation` — they took what was recommended. `agent-resolved` — an explore, research or spike question settled by finding or measuring the answer, never put to the user as a choice.

All four are legitimate; conflating them is not. Every grill question arrives with a recommended answer, so a log that does not distinguish them attributes the agent's judgement to the user.

**`confidence`** is the decider's, not the agent's, and it is checked at the grading pass. Low-confidence decisions that turn out load-bearing are the highest-value entries in the log.

**`unblocked`** and **`blocked_by`** are the frontier written down. They record which questions a decision opened and which it was waiting on, so the frontier can be rebuilt from the file after a session ends.

**`contribution`** stays null until the grading pass, then holds `load-bearing`, `minor`, or `irrelevant` with a sentence of justification.

## Cold-read evidence

The final cold read uses an exact table so every finding has a visible disposition:

```markdown
## Cold-read evidence

| Finding | Disposition |
|---|---|
| No unresolved contradictions found. | No action required. |
```

Use one unique row per finding. Both cells are non-empty. Replace placeholders such as `Pending.`, `TODO`, or `TBD`; they cannot support `cold_read: complete`.

## Superseding

Filling `contribution` at the grading pass is the one in-place edit a settled record receives; every other change supersedes. A reversed decision is never edited or deleted. Set its `status: superseded`, append a new record with `supersedes: D-007`, and state in the new record what changed. The reversal is the interesting part of the log.

**Both edits, or neither.** A later record that narrows, replaces or overrides an earlier one carries `supersedes:` in its own frontmatter *and* flips the earlier record's `status`. Saying it in prose alone leaves the earlier record reading `settled`, and a consumer following the fields compiles the reversed choice as live. Prose is for the human; the fields are the contract.

## Open frontier

Rewritten at every round boundary — the map a resuming session reads:

```markdown
## Open frontier

| Question | Route | Blocked by |
|---|---|---|
| Q8 — <question> | grill | — |
| Q9 — <question> | explore | — |
| Q11 — <question> | grill | Q8 |
```

Questions with no blocker are the frontier; an empty table ends the run.

## PRD alignment retrospective

Discovery ends by rebuilding one whole-table retrospective:

```markdown
## PRD alignment retrospective

| Decision | Disposition | PRD identifiers | Reason (required iff NO_NORMATIVE_EFFECT) |
|---|---|---|---|
| D-001 | NORMATIVE | R-001, C-001 | |
| D-002 | NO_NORMATIVE_EFFECT | | Internal research-method choice; no externally observable consequence. |
```

Rules:

- Exactly one row for every live `settled` decision and none for `superseded` decisions.
- `NORMATIVE` rows name one or more current PRD identifiers and leave `Reason` empty.
- `NO_NORMATIVE_EFFECT` rows name no PRD identifiers and give a non-empty reason.
- The table is rebuilt after the final decision write; do not patch yesterday's table.
