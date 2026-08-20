# Spec file

Write `<run>/20-spec.md` with this exact frontmatter:

```markdown
---
run: <feature-slug>
version: 1
status: draft
gate_ready: false
effective_config_revision: 0
derived_from:
  stage: discovery
  candidate_version: 1
  candidate_sha256: <accepted discovery SHA-256 from control.json>
---

# Spec — <title>

## Problem

<observable problem>

## Requirements

### R-001 — <name>
**Current:** <observable current behavior>
**Target:** <observable required behavior>
**Acceptance:** <observation and counterexample>
**Derived from:** D-001

## Prohibitions

<negative obligations or reasoned none>

## Constraints

<externally observable limits or reasoned none>

## Invariants

<continuous obligations or reasoned none>

## Out of scope

| ID | Excluded | Why | Derived from |
|---|---|---|---|
| X-001 | <excluded behavior> | <reason> | D-001 |

## Edge coverage

| Edge | Category | Resolution |
|---|---|---|
| <case> | boundary | <obligation, dismissal, or question> |

## Open questions

<classified deferred questions, or `None.`>
```

Rules:

- The schema is exact. Candidate version starts at `1`; a future spec reopen may require a later version.
- `status` remains `draft`; `gate_ready` records producer completion only.
- `effective_config_revision` matches authoritative control.
- `derived_from` exactly binds the latest accepted discovery version/hash.
- Approval metadata is written only to `control.json`; no approved copy or receipt exists.
