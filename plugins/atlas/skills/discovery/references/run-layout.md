# Run layout

Discovery operates inside an initialized run:

```text
<planning-root>/<feature-slug>/
├── run.yaml
├── control.json
├── 00-state.md
├── 10-decisions.md
├── 20-prd.md
└── 20-prd.html
```

`control.json` is authority. `00-state.md` is only a generated projection.

`10-decisions.md` keeps provenance and the required retrospective table. Use this exact frontmatter:

```markdown
---
run: <feature-slug copied from run.yaml>
version: 1
---

# Decisions — <title>

## Problem test

Pending.

## Cold-read evidence

| Finding | Disposition |
|---|---|
| Pending. | Pending. |

## Open frontier

| Question | Route | Blocked by |
|---|---|---|
```

Create or resume the PRD immediately using [`prd-file.md`](prd-file.md), the sole owner of the complete PRD schema and canonical-write contract. This layout reference does not duplicate either.

Rules:

- `10-decisions.md` frontmatter remains exact: only `run` and `version`.
- Replace the initial cold-read placeholder with one unique row per finding and a non-empty disposition before claiming completion; use [`decision-record.md`](decision-record.md) for the exact closure contract.
- `20-prd.md` and `20-prd.html` remain adjacent run artifacts; all mutation rules live in [`prd-file.md`](prd-file.md).
