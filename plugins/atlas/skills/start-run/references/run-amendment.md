# Run-configuration amendment

Use an amendment only for a discovery-found repository identity or baseline correction. `run.yaml` remains byte-for-byte immutable.

Store the next accepted record as `<run>/amendments/NNN-<short-name>.md`:

```markdown
---
version: 1
amendment: 1
applies_to: run.yaml
status: accepted
accepted: "<YYYY-MM-DD>"
reason: <persisted repository or baseline correction>
changes:
  repos:
    - repository: <stable repository identity>
      baseline: <commit SHA>
---

# <correction title>

<evidence for the correction>
```

Rules:

- Number files contiguously from `001`; `amendment` is the matching integer.
- Human acceptance is required before `status: accepted` is written.
- `changes` has top-level replacement semantics and may contain only a complete non-empty `repos` list.
- Repository identities are unique non-empty strings. Baselines are 7–64 hexadecimal commit SHAs.
- Workflow, gates, roster, policy, goal, placement, and identity changes require a new run.
- `apply-amendment` applies exactly one next record and writes accepted amendment count plus resulting effective configuration hash to `control.json`.
- No `previous`, `prior_effective_hash`, per-amendment ledger, receipt, or hash chain exists.
