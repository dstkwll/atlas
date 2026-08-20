# Findings file

One file per spike under `<run>/spikes/`. The run layout is fixed and `../../discovery/references/run-layout.md` is the authority; only the planning root above the run is configurable. Where no Stage 0 run exists, offer `start-run`.

```markdown
---
spike: <name>
hypothesis: <one line>
verdict: VALIDATED | INVALIDATED | PARTIAL | MIXED
production_code: prohibited | optional | candidate
retention: discard | preserve_evidence | candidate_for_rework
date: <YYYY-MM-DD>
---

# Spike: <the question>

## Bounds

**Dispatched by:** <the run, and the decision id that raised this question — or direct invocation within the run>

**Production code:** none | <what may survive, and where>
**Retention:** <what happens to the experiment afterwards>

Both are predeclared before anything runs.

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
**Verdict:** VALIDATED | INVALIDATED | PARTIAL | COULD-NOT-RUN
**Evidence:** <excerpt, path, number>

## Findings

**Verdict:** VALIDATED | INVALIDATED | PARTIAL | MIXED | none — <what blocked the run>

**What this establishes:** <the claim now supported, and how strongly>

**What remains unknown:** <what the spike did not settle, including anything an
experiment failed to test>

**Surprises:** <anything the investigation turned up that nobody was looking for>

**Implication:** <what the decision that prompted this should do with it>
```

A comparison spike closes with a head-to-head table across the dimensions that actually differed, and names a winner for this use case rather than in the abstract.
