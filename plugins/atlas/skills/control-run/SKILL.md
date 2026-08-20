---
name: control-run
description: Check a Stage 1–2 boundary read-only, consume configured authority, and record one deterministic transition.
disable-model-invocation: true
---

# Control run

Use packaged `tools/atlas_control.py`. This skill is an adapter; it never edits `run.yaml`, candidates, amendments, `control.json`, or `00-state.md`.

## 1. Mechanical check

Run:

```shell
python3 tools/atlas_control.py check --run <run-directory>
```

`check` is read-only. It returns structured `PASS` or `BLOCKED` plus all mechanical gaps and exact resume points. It checks identity, version/hash, required structure, effective intake, accepted predecessor binding, and stale/open markers. It does not grade prose or perform semantic acceptance.

A producer's `gate_ready: true` is necessary but never sufficient to advance.

## 2. Consume configured authority

Discovery and specification permit only:

- `HUMAN`: after mechanical PASS, present the candidate and obtain explicit human approval.
- `AGENT_REVIEW`: after mechanical PASS, dispatch a fresh read-only semantic reviewer with [`references/boundary-review.md`](references/boundary-review.md). Require it to apply every semantic question listed there for the current stage, judge all questions before choosing PASS or BLOCKED, and report every material gap without repair. Persist its exact envelope. V1 adds no reviewer identity, signature, or authentication service: fresh-context independence is the invoker's responsibility, while the controller proves only schema and current run/version/hash binding. Never synthesize the envelope in the producer context.

`AUTO` is unavailable for these semantic boundaries. Do not reinterpret it as agent approval. A future mechanical-only AUTO boundary would record `AUTO_PASSED`, never `AGENT_APPROVED`.

## 3. Record one outcome

HUMAN acceptance:

```shell
python3 tools/atlas_control.py advance --run <run-directory> --approval human
```

AGENT_REVIEW acceptance:

```shell
python3 tools/atlas_control.py advance --run <run-directory> --review reviews/<review>.json
```

A BLOCKED AGENT_REVIEW envelope is evidence for repair, not an authority transition. Leave the gate `PENDING`, follow every resume action, and run the boundary again. Only an explicit HUMAN authority may record a terminal rejection with `reject --reason <reason>`.

The controller validates run identity, candidate version/hash binding, authority, and transition legality. Acceptance replaces the current stage binding in `control.json`; it does not mutate the candidate or create `approved/` copies or receipt files.

## Recovery operations

```shell
python3 tools/atlas_control.py mark-stale --run <run-directory> --reason <finding>
python3 tools/atlas_control.py apply-amendment --run <run-directory>
python3 tools/atlas_control.py reopen --run <run-directory> --to discovery --reason <reason>
```

Reopen changes only authority state. It retains the current acceptance binding until the discovery producer writes and passes the next candidate version; the next acceptance replaces that binding.

## Standing rules

- `control.json` is the only authoritative mutable Stage 0–2 state.
- One invocation records at most one transition under the run-local single-writer lock.
- The authoritative write is one atomic temporary-file replacement of `control.json`.
- `00-state.md` regeneration is best-effort after commit and can never make a successful transition fail.
- There is no transaction journal, replay protocol, approved-copy store, receipt ledger, event log, or hash chain.
