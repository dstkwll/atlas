# System Design file

```markdown
---
run: <feature-slug>
version: 1
status: draft
gate_ready: false
participation: agent_led
opened: <YYYY-MM-DD>
source_binding:
  kind: product_closure
  artifact: 20-prd.md
  version: 1
  sha256: <64-lowercase-hex>
---

# System design — <title>

## Current system

<current topology, responsibilities, guarantees, and constraints>

## Proposed system

### Decision map

| Decision | Selected route | Adoption or disposition | Implementation consequence |
|---|---|---|---|
| <decision name> | <Option N — selected route (selected)> | <retained/adapted/wrapped/replaced/deferred> | <what callers, peers, operators, or later design now do> |

<proposed topology and system-observable commitments>

## Responsibilities and seams

<responsibility allocation and coordinated-change seams>

## Authoritative data ownership

<authoritative owners and consistency boundaries>

## Contracts and interfaces

<cross-module and external contracts>

## Schema and protocol

<schema or protocol commitments, or an applicability statement>

## Lifecycle and data flow

<end-to-end lifecycle, sequence, and data movement>

## Failure and recovery

<failure modes, recovery paths, and degraded behavior>

## Compatibility

<compatibility guarantees and transition window>

## Trust, security, and operations

<trust boundaries, security commitments, and operational guarantees>

## Rejected alternatives

<alternative, reason, and consequence>

## Open decisions

<remaining non-blocking decisions, or None.>
```

Direct Stage 0 source shape:

```yaml
source_binding:
  kind: stage0
  artifact: run.yaml
  sha256: <64-lowercase-hex>
  effective_config_hash: <64-lowercase-hex>
  effective_config_revision: 0
```
