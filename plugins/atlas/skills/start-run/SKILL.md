---
name: start-run
description: Create an Atlas run by classifying a fuzzy goal and resolving workflow, governance, risk, repository baselines, and gates before Stage 1 begins.
disable-model-invocation: true
---

# Start run

Implement Stage 0 — intake and classification. Turn a fuzzy goal into an accepted, immutable run configuration, then hand control to the first selected workflow stage.

This is not machine setup. `atlas:setup-atlas` chooses the planning root once per machine; `atlas:start-run` creates one engineering run beneath that configured root.

## Steps

### 1. Resolve the machine and repository context

Read `artifacts.planning_root` from the platform-native Atlas configuration, with the legacy fallback documented by `atlas:setup-atlas`. Where no configuration exists, stop and offer `atlas:setup-atlas`; do not accept a one-run path that bypasses machine configuration.

Inspect the current Git repository when one exists. Record a stable repository identity and its current commit as the planning baseline. Ask for any other repository already known to be affected, then resolve a baseline for every repository named. Never record an affected repository without its baseline.

Where an existing `<planning-root>/<feature-slug>/run.yaml` describes this goal, resume from its `00-state.md` instead of overwriting immutable intake. Reconstruct effective intake by applying accepted `amendments/run-config-NNN.yaml` records in order, as defined by [`references/run-amendment.md`](references/run-amendment.md).

Done when the planning root, fuzzy goal, and every repository currently known to be affected have evidence-backed values.

### 2. Classify the work

Assess and record the exact `risk` keys the control plane uses: `scope`, `reversibility`, `architecture_change`, `schema_change`, `public_contract_change`, `security_sensitive`, `operational_impact`, and `testability`.

Recommend one workflow depth:

- `trivial` — direct ticket and execution; no discovery or design stages;
- `normal` — discovery, spec, program design, tickets;
- `architectural` — normal plus system design;
- `fog_of_war` — exploration before the architecture pipeline can stabilize.

Recommend one governance posture: `exploratory`, `standard`, `high_assurance`, or `autonomous`. Also recommend an execution policy, environment policy, and roster. Use current configuration where it supplies them; otherwise present an explicit recommendation rather than silently treating an illustrative example as a default.

Done when each recommendation reason records its `dimension` and `evidence` from the risk assessment that caused it.

### 3. Resolve authority before work starts

Present one intake block containing:

- fuzzy goal and affected repository baselines;
- risk assessment;
- recommended and selected workflow, execution policy, environment policy, and roster;
- ordered selected stages;
- recommended and selected governance;
- the resolved policy for every selected stage gate and every run-relevant conditionally reachable gate, using `AUTO`, `AGENT_REVIEW`, `HUMAN`, `CONDITIONAL`, or `HUMAN_IF_CHANGED`;
- for each inactive conditionally reachable route, an explicit `activation.when` predicate over persisted evidence, separate from its review-authority policy;
- for `CONDITIONAL`, record ordered `conditions` and `otherwise` authority; for `HUMAN_IF_CHANGED`, record explicit `material_dimensions` and `otherwise` authority;
- every explicit override from the recommendation as `path`, `from`, `to`, and `reason`.

A governance label alone is insufficient: snapshot the resolved gate map so later skills never reinterpret a profile from changing global configuration. Every gate records `authority`; `conditions` entries use `when` and `then`. Reject either special authority while its operands remain unresolved.

Stage 0 is recommend-only. The user accepts or overrides this complete block before it is written, as required by `architecture/02-workflow.md`. This acceptance resolves intake; it does not pre-approve any later artifact.

Done when there is one accepted, fully resolved block with no unnamed gate or policy dimension.

### 4. Place the run

Use one fixed layout for both root forms:

```text
<planning-root>/<feature-slug>/
```

The slug is short, descriptive, and stable. An external root changes only `<planning-root>`; it never introduces a project or `runs/` hierarchy.

If the directory exists for a different goal, stop and choose a different slug. Never merge two runs because their names collide.

Done when the root-relative run path is unique and agrees with `architecture/03-artifact-model.md`.

### 5. Write immutable intake and initial state

Preview both files, then write:

- `<run>/run.yaml` in the shape defined by [`references/run-file.md`](references/run-file.md);
- `<run>/00-state.md` in the shape defined by [`references/state-file.md`](references/state-file.md).

`run.yaml` is immutable provenance. `00-state.md` is the mutable human-readable mirror. The first post-intake stage begins with its gate state `PENDING`. A conditionally reachable route begins in the canonical `NOT_REQUIRED` state while inactive; its snapshotted `activation.when` predicate preserves the distinction from a permanently unavailable route.

In `run.yaml`, write `version: 1`; record `opened` from the acceptance date; record `planning_root` with configuration source, resolved mode, and portable path form; record `run_path` as the feature slug; and write `execution_policy`, `environment_policy`, `roster`, and `repos` exactly as accepted. Every `repos` entry carries its repository-baseline pair. Never copy an external absolute root into the artifact.

In `00-state.md`, record `feature` from the run slug, `status: PLANNING`, `phase` from the first selected stage, `revision: 1`, `effective_config_revision: 0`, `effective_config_hash: null`, `base_run_sha256: null`, the mirrored `repos`, `blocked_reason: null`, `pending_amendment: null`, `approved_artifacts: {}`, `accepted_amendments: {}`, and `active_ticket: null`. The two hashes are controller-owned seals; the two empty maps are controller-owned append-only receipt ledgers. The `gates` map uses only canonical states: selected stages are `PENDING`; inactive or unreachable routes are `NOT_REQUIRED`. Reachability remains reconstructible from `run.yaml.activation`, not from a new state label.

Do not create `10-decisions.md`. Discovery owns that artifact after it verifies the run snapshot.

Immediately seal the accepted base intake through the packaged deterministic controller:

```shell
python3 tools/atlas_control.py initialize --run <run-directory>
```

The command computes both the canonical effective-configuration hash and SHA-256 over the exact `run.yaml` bytes, writes them to `00-state.md.effective_config_hash` and `base_run_sha256` without incrementing revision, and refuses to run after discovery or amendments begin. If it fails, stop; do not hand off an unsealed run or calculate either authority hash in prose.

Done when both files exist, every accepted intake value is represented, deterministic initialization succeeds, and reading only those files reconstructs the next stage and its authority.

### 6. Hand off without claiming later authority

Name the next selected stage and its gate authority. If it is `discovery`, offer `atlas:discovery` against this run. After a stage reports readiness, route to `atlas:control-run`; it is the sole first-party procedure that applies gate outcomes and advances `00-state.md`. If the selected first stage has no first-party Atlas skill yet, stop and report that implementation gap rather than substituting an incubator skill silently.

Skills produce candidate artifacts and readiness evidence. `atlas:control-run` applies gate outcomes and state transitions; Atlas start-run does not approve later stages.

## Scope changes after intake

Discovery may reveal another affected repository or invalidate a preserved baseline. That makes effective intake stale. Discovery records `intake_stale: true` and the finding in `10-decisions.md`, then deterministic `atlas:control-run mark-stale` blocks `00-state.md` and names the next pending amendment before returning here. `run.yaml` remains unchanged.

Preview a complete replacement `repos` block. V1 amendments may change only repository-baseline pairs; start a different run when workflow, gates, roster, policy, goal, or placement must change. After human acceptance, write the next contiguous `amendments/run-config-NNN.yaml` in the exact shape defined by [`references/run-amendment.md`](references/run-amendment.md). The record must set `applies_to: run.yaml`, name `previous`, record the `prior_effective_hash`, and state a concrete `reason`. Then invoke `atlas:control-run` to apply the accepted amendment through deterministic `tools/atlas_control.py apply-amendment`; Stage 0 never edits `00-state.md` directly. The base `run.yaml` remains byte-for-byte unchanged. Discovery revalidates and clears its own `intake_stale` marker before it can become gate-ready.

## Standing rules

**Fixed layout, configurable root.** Only the configured planning root moves; the feature layout beneath it does not.

**Repository plus baseline.** Neither half is sufficient planning provenance.

**Policy owns authority.** A skill may judge artifact readiness; only the resolved gate map determines who may advance it.
