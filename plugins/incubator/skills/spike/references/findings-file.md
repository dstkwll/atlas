# Findings file

One file per spike, under `artifacts.spikes_dir` beneath the planning root — `spikes/` where that key is unset. The planning root resolves as `../../discovery/references/run-layout.md` describes. Never hardcode a path; where no run exists, ask.

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

**Surprises:** <anything the investigation turned up that nobody was looking for>

**Implication:** <what the decision that prompted this should do with it>
```

A comparison spike closes with a head-to-head table across the dimensions that actually differed, and names a winner for this use case rather than in the abstract.
