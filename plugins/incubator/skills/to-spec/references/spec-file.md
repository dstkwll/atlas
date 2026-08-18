# Spec file

The shape of `20-spec.md`. Written to be read by someone who will not build the thing.

## Location

`<run>/20-spec.md`, under the planning root — resolved as `../../discovery/references/run-layout.md` describes. Never hardcode a path.

## Template

```markdown
---
run: <slug>
status: draft | approved | superseded
revision: 1
approved: <YYYY-MM-DD or null>
derived-from: 10-decisions.md
---

# Spec — <title>

## Problem

What is wrong today, from the perspective of whoever suffers it. No solution.

## Requirements

### R-001 — <short name>
**Current:** <what is true today>
**Target:** <what must become true>
**Acceptance:** <the observation that settles it; and what would falsify it>
**Derived from:** D-003, D-007
**Revision:** 1

### R-002 — <short name>
...

## Prohibitions

Negative acceptance criteria — what must never happen. Same form, same falsifiability.

### P-001 — <short name>
**Must never:** <the outcome nobody wants>
**Acceptance:** <the observation that would show it happening>
**Derived from:** D-011

## Constraints

Externally observable limits and user-mandated conditions: budgets, deadlines, compatibility
obligations, regulatory requirements, things that may not change. Technologies, schemas and
internal structure are Stage 3–4 material and do not belong here.

## Invariants

What must hold true throughout, not merely at the end.

## Out of scope

| Excluded | Why |
|---|---|

Reasons are required. Unexplained exclusions return later looking like oversights.

## Edge coverage

| Edge | Category | Resolution |
|---|---|---|
| <the case> | boundary/adjacency/empty/encoding/ordering/precision/idempotency/concurrency | covered by R-00N · dismissed: <reason> · open: Q-00N |

Categories with no applicable edge are omitted rather than listed as none.

## Open questions

| ID | Question | Kind | Routed to |
|---|---|---|---|
| Q-001 | <question> | blocking · deferred | discovery · system design · program design |

**Blocking** means the answer changes what must become true; the spec is not done while one
stands. **Deferred** means the answer belongs to a later stage.

## Stories

Optional, non-normative. Written where they help a reader understand who wants what. They
carry no obligations — the requirements above do.
```

## Identifier rules

`R-`, `P-` and `Q-` identifiers are assigned once, in order, and never reused. A retired
requirement's identifier stays retired; a superseded one keeps its identifier and increments
its revision.

Downstream artifacts cite these identifiers, so an identifier that changes meaning silently
invalidates everything citing it.

## Revising an approved spec

Bump the revision on the changed requirement, not the document. Record what was invalidated:
the designs and tickets that cite that identifier, and nothing else.

A spec whose `status` is `superseded` names its successor in the frontmatter.
