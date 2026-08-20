---
name: control-run
description: Check discovery's product-closure boundary read-only, consume configured authority, and record one deterministic transition.
disable-model-invocation: true
---

# Control run

Use packaged `tools/atlas_control.py`. This skill is an adapter; it never edits `run.yaml`, candidates, amendments, `control.json`, or `00-state.md`.

## 1. Mechanical check

Run:

```shell
python3 tools/atlas_control.py check --run <run-directory>
```

`check` is read-only. It returns structured `PASS` or `BLOCKED` plus all mechanical gaps and exact resume points. It checks identity, version/hash, required structure, retrospective totality, bidirectional PRD citations, effective intake, HTML metadata, and stale/open markers. It is exhaustive over identifiers and best-effort over meaning. It does not grade prose or perform semantic acceptance.

A producer's `gate_ready: true` is necessary but never sufficient to advance.

## 2. Consume configured authority

Discovery's product-closure boundary permits only:

- `HUMAN`: after mechanical PASS, present the candidate and obtain explicit human approval.
- `AGENT_REVIEW`: after mechanical PASS, dispatch a fresh read-only semantic reviewer with [`references/boundary-review.md`](references/boundary-review.md). Require decisions-first read order, no repair authority, and exhaustive gaps. Persist its exact envelope as `reviews/product_closure-v<version>.json`. V1 adds no reviewer identity, signature, or authentication service: freshness and read order are procedural requirements, while the controller proves only the envelope schema plus current run/version/hash binding. Never synthesize the envelope in the producer context.

`AUTO` is unavailable for this semantic boundary. Do not reinterpret it as agent approval. A future mechanical-only AUTO boundary would record `AUTO_PASSED`, never `AGENT_APPROVED`.

## 3. Record one outcome

HUMAN acceptance:

```shell
python3 tools/atlas_control.py advance --run <run-directory> --approval human
```

AGENT_REVIEW acceptance:

```shell
python3 tools/atlas_control.py advance --run <run-directory> --review reviews/product_closure-v<version>.json
```

A BLOCKED AGENT_REVIEW envelope is evidence for repair, not an authority transition. Leave the gate `PENDING`, follow every resume action, and run the boundary again. Only an explicit HUMAN authority may record a terminal rejection with `reject --reason <reason>`.

The controller validates run identity, candidate version/hash binding, authority, and transition legality. Acceptance replaces the current discovery binding in `control.json`; it does not mutate the candidate or create `approved/` copies or receipt files.

## Recovery operations

Only when repository identity or baseline evidence contradicts intake, follow [`../../references/intake-correction.md`](../../references/intake-correction.md). No other reopen or stale-acceptance path exists in V1.

## Standing rules

- `control.json` is the only authoritative mutable Stage 0–2 state.
- One invocation records at most one transition under the run-local single-writer lock.
- The authoritative write is one atomic temporary-file replacement of `control.json`.
- `00-state.md` regeneration is best-effort after commit and can never make a successful transition fail.
- There is no transaction journal, replay protocol, approved-copy store, receipt ledger, event log, or hash chain.
