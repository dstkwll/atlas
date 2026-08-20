---
name: control-run
description: Apply a supported Atlas gate through deterministic code and advance mutable run state without changing immutable intake.
disable-model-invocation: true
---

# Control run

Wrap the repository's deterministic `tools/atlas_control.py` state authority. This skill gathers an authority signal and reports results; it never edits candidate frontmatter, `run.yaml`, amendments, or `00-state.md` itself.

Invoke explicitly as `atlas:control-run`.

## Steps

### 1. Locate the deterministic authority

Resolve the Atlas repository that supplied this plugin and require:

```text
tools/atlas_control.py
```

Run it with Python 3.9 or newer in an environment containing PyYAML. If the program or dependency is unavailable, stop loudly. Do not reproduce its transition logic in prose or mutate state as a fallback.

### 2. Inspect without deciding

Resolve the exact run directory and read its candidate and state only to present the request. Do not repair the candidate under review.

The program independently reconstructs effective intake from immutable `run.yaml` plus accepted `amendments/run-config-NNN.yaml`, verifies the append-only amendment ledger and effective-state hash, verifies current phase, source status, run identity, phase-specific candidate schema and required body structure, predecessor approvals and receipts, revision, and approval date, checks `gate_ready`, rejects stale intake, resolves the current policy, writes an immutable approved copy, appends its SHA-256 receipt to authoritative state, and applies at most one supported transition. Before approving specification, it also requires every `D-NNN` reference to exist in the immutable approved discovery copy.

For a pristine Stage 0 run, `atlas:start-run` invokes `initialize --run <run-directory>` before discovery. That deterministic command validates the exact documented `run.yaml` and pristine `00-state.md` schemas, then seals both the canonical effective-configuration hash and exact-byte `run.yaml` SHA-256 into revision-1 state. It refuses to bless schema-incomplete intake or a run after discovery or amendments have begun.

### 3. Supply only the configured authority signal

Read the configured authority for the current phase so the user can see what will happen:

- `AUTO` — invoke the program without an approval argument.
- `HUMAN` — show the artifact path and readiness evidence, ask for explicit approval, then pass `--approval human` only after the user approves.
- `AGENT_REVIEW`, `CONDITIONAL`, and `HUMAN_IF_CHANGED` — stop with an implementation gap. Their complete policy remains snapshotted, but this candidate deterministic authority does not execute them yet. Never emulate them with prompt judgement or silently downgrade them to `HUMAN`.

A human's request to run an experiment is side-effect consent, not gate approval. Invoking this skill is not itself approval of a `HUMAN` gate.

### 4. Invoke one transition

For `AUTO`:

```shell
python3 tools/atlas_control.py advance --run <run-directory>
```

For an explicitly approved `HUMAN` gate:

```shell
python3 tools/atlas_control.py advance --run <run-directory> --approval human
```

The program is the only writer. On success, report its exact output and the resulting artifact and state paths. On nonzero exit, report stderr and leave the run for diagnosis; never claim progression from an intended command.

If the configured authority explicitly rejects the candidate, persist that outcome rather than leaving an ambiguous pending gate:

```shell
python3 tools/atlas_control.py reject --run <run-directory> --reason <persisted-reason>
```

The program sets the current gate to canonical `REJECTED`, records `status: BLOCKED` and `blocked_reason`, increments state revision, and leaves the candidate unapproved.

### 5. Apply accepted Stage 0 amendments

When discovery persists `intake_stale: true`, first record the authoritative blocked state through:

```shell
python3 tools/atlas_control.py mark-stale --run <run-directory> --reason <persisted-scope-finding>
```

The program requires an initial pending discovery gate or a legally reopened stale discovery gate and a schema-valid stale, non-ready decision candidate, then records canonical `STALE`, `BLOCKED`, the reason, and the exact next amendment name.

`atlas:start-run` may write that one accepted amendment after human intake acceptance. Apply its state effect only through:

```shell
python3 tools/atlas_control.py apply-amendment --run <run-directory>
```

The program validates contiguous numbering, previous links, canonical hashes, the V1 `repos`-only replacement boundary, and exactly one pending effective-config revision before updating state. Stage 0 does not edit `00-state.md` directly.

### 6. Reopen specification into discovery

When `atlas:to-spec` persists a behaviour-changing unresolved decision, invoke the one legal backward transition:

```shell
python3 tools/atlas_control.py reopen --run <run-directory> --to discovery --reason <persisted-reason>
```

The program verifies every receipt in the append-only approved-artifact ledger, marks discovery and specification gates `STALE`, preserves the approved copy and its receipt, creates a new versioned working decision draft, marks the spec stale when a spec file already exists, and returns the state phase to discovery. Neither this skill nor an artifact producer performs those edits.

## Standing rules

**Deterministic code owns state.** This skill is an adapter, never a second authority.

**One transition per invocation.** The controller holds a run-local nonblocking single-writer lock across recovery, validation, and commit. A concurrent invocation exits nonzero without computing or committing from a stale revision. Re-read state before another call.

**Crash recovery is deterministic and separate from the requested command.** Multi-file transitions install an fsynced run-local journal before replacing files. The next invocation finishes and verifies those recorded writes, removes the journal, then exits nonzero with an explicit statement that no newly requested operation ran. Re-read state before deciding whether any command still applies; never interpret recovery as success for the command that happened to trigger it.

**Reviewer never writes.** Unsupported review authorities fail closed until deterministic receipt validation exists.

**Inactive-route activation is not implemented.** Preserve `activation.when` and leave canonical `NOT_REQUIRED` unchanged until deterministic activation support exists.

**No downgrade path.** Missing code, missing PyYAML, malformed policy, stale intake, unsupported authority, or write failure is visible and blocking.
