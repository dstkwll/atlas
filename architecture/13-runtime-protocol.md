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

## Planning control state before execution

Stages 0–2 use `<planning-root>/<feature>/control.json` as their machine-canonical planning
state. It records only planning phase/gate outcomes and version/hash provenance. This closes
the pre-execution authority gap for a planning effort that may span repositories without
putting repository-scoped execution state in the planning root. `00-state.md` is generated
from this file and is never transition authority.

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

`control.json` does not replace this execution protocol. Once compiled work executes, each
repository-scoped factory run owns its `run.json`, events, envelopes, evidence, and logs under
that repository's `.factory/runs/` directory.

## Runtime state vs engineering truth

```text
ENGINEERING TRUTH
"what did we decide?"
→ versioned planning contracts

RUNTIME TRUTH
"what is executing right now?"
→ machine state / events / envelopes
```
