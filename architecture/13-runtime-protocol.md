# 13 — Runtime Protocol, State, and Evidence

## Durable contracts vs runtime protocol

Markdown remains ideal for decisions, behavioral specification, system design, program design, vertical tickets, amendments, and durable evidence summaries.

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

A generated `<planning-root>/<feature>/00-state.md` may remain useful as a projection, but it is not authoritative for attempt counts, active ownership, retry state, or exact state transitions.

## Runtime state vs engineering truth

```text
ENGINEERING TRUTH
"what did we decide?"
→ versioned planning contracts

RUNTIME TRUTH
"what is executing right now?"
→ machine state / events / envelopes
```
