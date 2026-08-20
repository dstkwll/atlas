# Run layout

Discovery operates inside an initialized run:

```text
<planning-root>/<feature-slug>/
├── run.yaml
├── control.json
├── 00-state.md
└── 10-decisions.md
```

`control.json` is authority. `00-state.md` is only a generated projection.

Use this exact `10-decisions.md` frontmatter for every discovery candidate, including a reopened next version:

```markdown
---
run: <feature-slug copied from run.yaml>
version: 1
status: draft
gate_ready: false
intake_stale: false
cold_read: pending
effective_config_revision: 0
opened: "<YYYY-MM-DD copied from run.yaml>"
repos:
  - <stable repository identity from effective intake>
---

# Decisions — <title>

## Problem test

Pending.

## Cold-read evidence

Pending. Record the baseline findings and the disposition of each finding.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|
```

Field rules:

- The schema is exact; no approval, approved-copy, receipt, or supersedes fields exist.
- `version` starts at `1`. After reopen, write one greater than the latest accepted discovery version in `control.json`.
- `status` remains `draft`; the producer changes only completion/readiness fields.
- `effective_config_revision`, `opened`, and `repos` mirror effective intake/control.
- `intake_stale: true` requires `gate_ready: false` and Stage 0 amendment recovery.
- `cold_read: complete` and `gate_ready: true` mean producer work ended, not that the boundary was accepted.
