# Program Design file

```markdown
---
run: <feature-slug>
version: 1
status: draft
gate_ready: true
opened: <YYYY-MM-DD>
source_binding:
  kind: system_design
  artifact: 30-system-design.md
  version: 1
  sha256: <64-lowercase-hex>
---

# Program design — <title>

## Repository grounding

<inspected repositories, baselines, paths, conventions, and feasibility evidence>

## Upstream commitment realization

<each upstream commitment, its exact source citation, and its local realization>

## File-tree diff

<exact files and packages added, changed, moved, or removed, with responsibilities>

## Types and boundary signatures

<important types, language-level signatures, ownership, and invariants>

## Call and data flow

<local call graph, state/data movement, and error propagation>

## State, locking, concurrency, and lifetime

<internal mutation, locks, concurrency rules, cleanup, and object/process lifetime>

## Migration and local failure-path implementation

<codebase-local migration mechanics, ordering, rollback points, and failure handling>

## Test seams and validation plan

<public seams, separating witnesses, validators, and exact commands>

## Least-confident decisions

<decision, evidence, uncertainty, and bounded consequence>

## Implementation constraints and sequencing

<implementation-order constraints without ticket decomposition>
```

Accepted Product Closure source shape:

```yaml
source_binding:
  kind: product_closure
  artifact: 20-prd.md
  version: 1
  sha256: <64-lowercase-hex>
```

Frozen effective Stage 0 source shape:

```yaml
source_binding:
  kind: stage0
  artifact: run.yaml
  sha256: <64-lowercase-hex>
  effective_config_hash: <64-lowercase-hex>
  effective_config_revision: 0
```
