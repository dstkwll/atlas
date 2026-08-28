# PRD file

Maintain `<run>/20-prd.md` continuously during discovery. It is the only Product Definition Approval candidate. Stage each complete replacement in `<run>/.20-prd.next.md`; never edit the canonical file directly.

```markdown
---
run: <feature-slug>
version: 1
status: draft
gate_ready: false
intake_stale: false
cold_read: pending
effective_config_revision: 0
opened: <YYYY-MM-DD>
repos:
  - <stable repository identity from effective intake>
derived_from:
  artifact: 10-decisions.md
  version: 1
  sha256: <64 lowercase hex characters>
---

# Product requirements — <title>

## Problem

<externally observable problem>

## Goals and outcomes

<observable success outcomes>

## Non-goals

<what the product does not promise>

## Actors

<external actors>

## Scenarios

### P-001 — <name>
**Current:** <observable current behavior>
**Target:** <observable required behavior>
**Acceptance:** <observation and counterexample>
**Derived from:** D-001

## Requirements

### R-001 — <name>
**Current:** <observable current behavior>
**Target:** <observable required behavior>
**Acceptance:** <observation and counterexample>
**Derived from:** D-001

## Invariants

### I-001 — <name>
**Rule:** <continuous external obligation>
**Derived from:** D-001

## Contracts and interfaces

### C-001 — <name>
**Contract:** <product-boundary obligation>
**Derived from:** D-001

## Edge and failure cases

### X-001 — <name>
**Case:** <edge or failure case>
**Resolution:** <obligation, dismissal, or later-stage note>
**Derived from:** D-001

## Observability

<what external evidence proves the obligations>

## Acceptance outcomes

<what observable outcomes show the product contract is met>

## Open questions

None.
```

Rules:

- The section set and frontmatter schema are exact.
- The only canonical write command is `python3 tools/render_prd.py write --run <run-directory> --draft .20-prd.next.md`. It renders before replacement. A render or staging failure preserves the prior pair; an interrupted two-file install may leave a mismatch, which verification detects and Product Definition Approval blocks until the command is rerun.
- Every normative `P|R|I|C|X-NNN` item cites one or more live decisions in `Derived from:`.
- `derived_from` binds the exact current `10-decisions.md` version/hash after the retrospective is complete.
- Internal design, module structure, ticketing, file lists, and implementation sequencing are prohibited here.
