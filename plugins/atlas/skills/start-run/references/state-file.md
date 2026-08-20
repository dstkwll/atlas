# State file

`00-state.md` is the mutable human-readable mirror. The control plane, not a stage skill, owns its transitions.

```markdown
---
feature: <feature-slug>
status: PLANNING
phase: discovery
revision: 1
effective_config_revision: 0
effective_config_hash: null
base_run_sha256: null
repos:
  - <stable repository identity>
gates:
  discovery: PENDING
  spec: PENDING
  program_design: PENDING
  tickets: PENDING
  tracer: NOT_REQUIRED
  final_pr: PENDING
active_ticket: null
blocked_reason: null
pending_amendment: null
approved_artifacts: {}
accepted_amendments: {}
---

# State — <title>

## Next

<first selected stage> is next. Authority: <resolved gate authority from run.yaml>.

## Notes

- Intake accepted on <YYYY-MM-DD>.
```

## Field rules

- `feature` records the same slug as `run.yaml`.
- `status` starts as `PLANNING`.
- `phase` records the first selected post-intake stage, not `intake` after intake has been accepted.
- `revision` starts at `1` and increments on each valid control-plane transition.
- `effective_config_revision` starts at `0` and names the latest accepted run-configuration amendment.
- `effective_config_hash` is null only in the two-file preview. Before discovery starts, deterministic `tools/atlas_control.py initialize` records the canonical base-configuration SHA-256 without incrementing revision. Every later transition requires and verifies it; accepted amendments replace it with the new effective hash.
- `base_run_sha256` is null only in the two-file preview. The same initialization records SHA-256 over the exact `run.yaml` bytes. Every later transition verifies it, and amendments never replace it.
- `repos` mirrors the stable repository identities from `run.yaml`.
- `gates` records state, not authority. Selected future stages start `PENDING`; inactive conditionally reachable and unavailable routes use canonical `NOT_REQUIRED`. Their difference remains in immutable `run.yaml.activation`, not in a new gate-state label.
- `active_ticket` starts null.
- `blocked_reason` and `pending_amendment` start null and make interrupted recovery visible on disk.
- `approved_artifacts` starts empty. Deterministic control appends receipts keyed by immutable run-relative approved-copy path; each receipt records phase, SHA-256, authority, and date. Reopen never removes an earlier receipt.
- `accepted_amendments` starts empty. Deterministic control appends each accepted amendment's run-relative path and byte-level SHA-256, then verifies every recorded amendment before later transitions.

Gate authorities remain reconstructible from immutable `run.yaml` plus accepted amendments; this file records whether those gates have been satisfied. Valid states are exactly `NOT_REQUIRED`, `PENDING`, `AGENT_APPROVED`, `HUMAN_APPROVED`, `REJECTED`, and `STALE`. A successful `AUTO` gate records canonical `AGENT_APPROVED` plus the `AUTO` authority in the immutable approval receipt.
