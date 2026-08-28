---
name: control-run
description: Check discovery's Product Definition Approval boundary read-only, consume configured authority, and record one deterministic transition.
disable-model-invocation: true
---

# Control run

Resolve `<atlas-plugin-root>` from this installed skill before invoking the packaged controller: it is the third parent of this file (`SKILL.md` → `control-run/` → `skills/` → the plugin root) and must contain `tools/atlas_control.py`. Use that resolved absolute path; never assume the caller's working directory. This skill is an adapter; it never edits `run.yaml`, candidates, amendments, `control.json`, or `00-state.md`.

If the packaged tool or a required dependency is unavailable, or a command returns anything except its documented outcome, report the exact error and stop. A valid structured `BLOCKED` report from `check` is an expected check outcome even though the command exits 1; handle its gaps rather than treating it as tool failure. Never emulate transition logic in prose or mutate authority state as a fallback.

## 0. Recover or continue from authoritative phase

Read authoritative `control.json` before running Product Definition Approval. When its phase already names `system_design`, `program_design`, or `tickets`, run the shared downstream handoff command exactly:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" ensure --run "<run-directory>"
```

On success, re-read `planning-control.json`, hand off to its current owner, and do not rerun Product Definition Approval. This is interrupted-handoff recovery, not another Stage 0–2 transition. If the phase is `discovery`, continue below and do not run `ensure`; discovery never starts execution.

## 1. Mechanical check

Run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_control.py" check --run "<run-directory>"
```

`check` is read-only. It returns structured `PASS` or `BLOCKED` plus all mechanical gaps and exact resume points. It checks identity, version/hash, required structure, retrospective totality, bidirectional PRD citations, effective intake, HTML metadata, and stale/open markers. It is exhaustive over identifiers and best-effort over meaning. It does not grade prose or perform semantic acceptance.

A producer's `gate_ready: true` is necessary but never sufficient to advance.

## 2. Consume configured authority

After mechanical PASS, read `run.yaml.gates.discovery.authority` and execute only that branch. `check` does not choose or return the authority.

Discovery's Product Definition Approval boundary permits only:

- `HUMAN`: after mechanical PASS, present the candidate at the exact user-facing approval surface:
  - stage label: `Product Definition Approval`
  - action: `Approve the product definition`
  - helper: `Confirm the PRD and recorded decisions are complete enough to begin System Design.`
  Obtain explicit human approval only through that surface.
- `AGENT_REVIEW`: after mechanical PASS, dispatch a fresh read-only semantic reviewer with [`references/boundary-review.md`](references/boundary-review.md). Require decisions-first read order, no repair authority, and exhaustive gaps. Persist its exact envelope as `reviews/product_closure-v<version>.json`. V1 adds no reviewer identity, signature, or authentication service: freshness and read order are procedural requirements, while the controller proves only the envelope schema plus current run/version/hash binding. Never synthesize the envelope in the producer context.

`AUTO` is unavailable for this semantic boundary. Do not reinterpret it as agent approval. A future mechanical-only AUTO boundary would record `AUTO_PASSED`, never `AGENT_APPROVED`.

## 3. Record one outcome

HUMAN acceptance:

```shell
python3 "<atlas-plugin-root>/tools/atlas_control.py" advance --run "<run-directory>" --approval human
```

AGENT_REVIEW acceptance:

```shell
python3 "<atlas-plugin-root>/tools/atlas_control.py" advance --run "<run-directory>" --review "reviews/product_closure-v<version>.json"
```

A BLOCKED AGENT_REVIEW envelope is evidence for repair, not an authority transition. Leave the gate `PENDING`, follow every resume action, and run the boundary again. Only an explicit HUMAN authority may record a terminal rejection:

```shell
python3 "<atlas-plugin-root>/tools/atlas_control.py" reject --run "<run-directory>" --reason "<reason>"
```

On success, report the exact output and re-read `control.json` before claiming the resulting state. After a successful Product Definition Approval transition, if that re-read phase is `system_design`, `program_design`, or `tickets`, run the exact shared `ensure` command from §0 and re-read `planning-control.json`. Return the freshly validated phase/status to the invoking continuation owner. Do not invoke a downstream producer from `control-run`; `start-run` owns manual/auto continuation after Product Definition Approval. In direct mode, report the meaningful next phase and recommend “Use Gazetteer to continue” without requiring an internal skill command. For the expected nonzero structured `BLOCKED` check outcome, report and follow every gap. On any other nonzero exit, report the exact error and never claim progression from an intended command.

The controller validates run identity, candidate version/hash binding, authority, and transition legality. Acceptance replaces the current discovery binding in `control.json`; it does not mutate the candidate or create `approved/` copies or receipt files.

## Recovery operations

Only when repository identity or baseline evidence contradicts intake, follow [`../../references/intake-correction.md`](../../references/intake-correction.md). No other reopen or stale-acceptance path exists in V1.

## Standing rules

- `control.json` is the only authoritative mutable Stage 0–2 state.
- One invocation records at most one transition under the run-local single-writer lock.
- The authoritative write is one atomic temporary-file replacement of `control.json`.
- `00-state.md` regeneration is best-effort after commit and can never make a successful transition fail.
- There is no transaction journal, replay protocol, approved-copy store, receipt ledger, event log, or hash chain.
