# 12 — Capabilities, Credentials, and Trust

## Core principle

> **Important boundaries should be mechanically verified or enforced at the cheapest appropriate layer.**

Prompt instructions alone are not sufficient for boundaries whose violation would invalidate trust in the run. However, V1 does not require OS-level capability isolation for every role if a simpler verified boundary reliably detects, restores, and fails unauthorized mutation.

Think in increasing strength:

```text
1. prompt convention
2. post-hoc verified boundary
3. preventive capability boundary
```

Use the strongest level justified by the actual risk and implementation cost.

---

## Trust zones

### Trusted supervisor

May own:

- Git push/PR credentials;
- long-lived configuration secrets;
- gate/HITL state authority;
- publication authority;
- execution-policy authority.

### V1 workcell

The local worktree receives the source/planning baseline required for the run and the tools necessary to execute delegated work.

If/when execution moves into an isolated/ephemeral runtime, prefer scoped short-lived credentials and keep powerful durable credentials outside that environment.

### Worker ownership and contained harness helpers

The trusted supervisor resolves the ticket, exact accepted bindings, workspace, worker configuration,
budget, deterministic brief, validator/review contract, and attempt policy before invocation. The
selected worker may implement, explore within its workspace, repair, and report `DESIGN_BLOCKED`
evidence. It cannot choose or replace the ticket, alter Atlas phase/owner, reroute staffing, change
accepted dependency/design truth, weaken validation/governance, mutate Atlas planning/runtime
authority, delegate Atlas ownership, commit/push/publish, or declare acceptance.

A coding harness may use helper agents only as implementation-local mechanics inside the same
supervisor-selected worker attempt, with the same workspace, tool permissions, budget, accepted
brief, and authority envelope. Helper agents receive no Atlas identity, cannot own or accept the
ticket, cannot select a new route or worker, and cannot expand permissions. If the host cannot prove
those containment properties, helper delegation is disabled for V1. The boundary forbids delegation
of Atlas ownership, not bounded parallel reasoning inside one already-authorized attempt. Any
separately Atlas-addressable role or coordinator is a distinct trusted-supervisor dispatch under the
ordinary staffing and authority contracts, never an internal helper.

---

## Builder write boundary

Desired logical policy:

```yaml
builder:
  repo_read: true
  repo_write:
    allow:
      - src/**
      - tests/**
    deny:
      - .factory/**
      - .planning/**
      - factory/**
      - scripts/validation/**
  publish: false
  approve_gate: false
```

The `.planning/**` deny rule covers a repository-relative planning root. Where the planning root is external, it lies outside the builder's repository write scope entirely and is denied by that scope rather than by an explicit rule. A builder is never granted write access to the planning root under either arrangement: the artifacts it is judged against are not writable by it.

V1 may enforce this using **repository-state comparison and rollback/failure** rather than a perfect preventive filesystem sandbox.

The important invariant is that unauthorized mutation does not silently become accepted output.

Particularly sensitive targets include:

- factory/orchestration code deciding the current run;
- validator definitions/commands;
- governance/profile configuration;
- approved planning contracts;
- reviewer definitions;
- sealed evidence used by earlier gates.

---

## Reviewer boundary

Default logical policy:

```yaml
reviewer:
  repo_read: true
  repo_write: false
  publish: false
  approve_gate: propose_only
```

For V1, if a reviewer mutates the repository, the harness should detect the mutation, restore the repository to the pre-review state, and fail/reject the phase.

A later sandboxed runtime may make reviewer storage physically read-only if that becomes cheap and useful.

---

## Publish authority

Preferred logical boundary:

```text
WORKCELL
  produces code + evidence
  does not merge

TRUSTED SUPERVISOR
  verifies
  pushes branch
  creates draft PR

HUMAN
  reviews final PR
  merges initially
```

In a purely local V1 implementation, supervisor and workcell may be processes on the same machine. The distinction is about **authority**, not necessarily physical deployment.

## Evidence before lifecycle cleanup

The workcell/worker cannot turn cleanup into completion or erase the only evidence the supervisor
needs to decide outcome. Before removing a worktree—or later destroying a sandbox/session—the
trusted supervisor verifies that required commit/tree identity, envelopes, validator/reviewer
outcomes, blockers, logs/artifacts, runtime bindings, and supported recovery locator are durable
outside the source being removed. A failed harvest retains that source and creates a lifecycle
blocker. Policy may authorize automatic cleanup only after this evidence boundary passes.

---

## Factory self-modification

A worker must not gain acceptance by changing the mechanism evaluating the same run.

If implementation reveals that a validator, policy, workflow, or approved contract is wrong, treat that as upstream work/amendment with its own governance path rather than allowing the current builder to weaken the gate.

---

## Future stronger capability boundaries

If the workcell becomes an isolated VM/container, consider:

- read-only mounts for governance/factory/validator material;
- scoped tool capabilities;
- short-lived model credentials;
- no durable forge credentials inside the workcell;
- budget/resource caps;
- provider-native secret isolation.

These are **future hardening paths**, not reasons to delay a local verified-boundary V1. Their
promotion triggers and falsification conditions live in non-authoritative `v2-horizon.md`.
