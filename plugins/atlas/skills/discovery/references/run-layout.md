# Run layout

Discovery operates inside a run already created by `atlas:start-run`. It does not choose a planning root or create a run directory.

## Resolve the existing run

Read `artifacts.planning_root` from the platform-native Atlas configuration, with the legacy fallback documented by `setup-atlas`. Resolve the selected run as:

```text
<planning-root>/<feature-slug>/
```

This layout is identical for repository-relative and external planning roots. An external root changes only `<planning-root>`; it does not add project or `runs/` directories.

The run must already contain:

```text
<run>/
├── run.yaml
└── 00-state.md
```

`run.yaml` is immutable Stage 0 provenance. Reconstruct effective intake by applying accepted `amendments/run-config-NNN.yaml` in numeric order, then read its goal, repositories and baselines, selected stages, and resolved gate policies. `00-state.md` must identify discovery as the current phase and the same effective-config revision. If either file is absent, mismatched, or discovery is not selected/current, stop and offer `atlas:start-run`; do not manufacture intake from inside discovery.

## Discovery artifacts

Discovery creates or resumes:

```text
<run>/
├── 10-decisions.md
├── evidence/
└── spikes/
```

`evidence/` and `spikes/` are fixed run-relative locations from `architecture/03-artifact-model.md`. They are not configurable directories.

Start a new `10-decisions.md` with:

```markdown
---
run: <feature-slug copied from run.yaml>
version: 1
status: draft
gate_ready: false
intake_stale: false
cold_read: pending
approved: null
approved_authority: null
approved_copy: null
approved_sha256: null
effective_config_revision: <copied from 00-state.md>
opened: "<YYYY-MM-DD copied from run.yaml>"
repos:
  - <stable repository identity copied from run.yaml>
---

# Decisions — <title>

## Problem test

Pending.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|
```

The rest grows during the run. `version` is a positive integer starting at 1 and incrementing for every reopened working draft. Decision entries follow [`decision-record.md`](decision-record.md). `approved`, `approved_authority`, `approved_copy`, and `approved_sha256` are written only by deterministic `tools/atlas_control.py` after the configured gate passes. The copy under `<run>/approved/` is the immutable contract; its receipt also remains in `00-state.md.approved_artifacts` after a legal reopen creates a new top-level working draft.

## Reopened discovery candidate

The deterministic `spec -> discovery` reopen writes this exact frontmatter shape before discovery edits the body:

```markdown
---
run: <feature-slug copied from run.yaml>
version: <approved predecessor version plus one>
status: draft
gate_ready: false
intake_stale: false
cold_read: complete
approved: null
approved_authority: null
approved_copy: null
approved_sha256: null
effective_config_revision: <copied from 00-state.md>
opened: "<YYYY-MM-DD copied from run.yaml>"
repos:
  - <stable repository identity copied from effective intake>
supersedes: <run-relative active approved/discovery-rN.md path>
---
```

The reopened schema is the initial schema plus `supersedes`. That value must name the active immutable discovery copy in the append-only state receipt ledger; discovery cannot replace it. Both receipt fields stay present and null in the working draft so the controller can reapprove the exact schema and append a new receipt without deleting the predecessor.

## Scope changes

The repository-plus-baseline pairs in `run.yaml` are the intake snapshot. When discovery finds another affected repository or invalidates a baseline:

1. record the finding as a decision;
2. set this artifact's `intake_stale: true` and `gate_ready: false`;
3. leave immutable `run.yaml` unchanged and invoke deterministic `tools/atlas_control.py mark-stale`, which blocks mutable state and names the pending amendment;
4. return to `atlas:start-run`, which writes that accepted run-configuration amendment; deterministic `tools/atlas_control.py apply-amendment` updates the state mirror before discovery revalidates and clears its own stale marker.

Discovery may describe the new scope, but it does not silently widen immutable intake.
