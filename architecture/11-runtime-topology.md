# 11 — Runtime Topology

## Two orthogonal architectural views

The system has two independent ways of describing itself.

### Logical planes

- **Control plane** — config, workflow selection, policy, gates, lifecycle authority.
- **Reasoning plane** — discovery, design, implementation, review.
- **Deterministic plane** — git, tests, state transitions, validation, scope checks, packaging.

### Runtime tiers

- **Trusted supervisor** — owns durable authority and publication boundaries.
- **Workcell** — the execution boundary in which delegated engineering work occurs.
- **Worker phases** — bounded builder/reviewer/etc. roles invoked by the factory.

These axes are perpendicular, not competing models.

---

## Logical target topology

```text
                    USER
                     │
                     ▼
┌────────────────────────────────────┐
│         TRUSTED SUPERVISOR         │
│ intake + resolved config           │
│ workflow/governance policy         │
│ HITL gate authority                │
│ durable credentials                │
│ execution lifecycle                │
│ observability                      │
└─────────────────┬──────────────────┘
                  │
          PRE-IMPLEMENT PIPELINE
                  │
 decision discovery → spec
 → system design → program design
 → compiled vertical tickets
                  │
             APPROVED PACKET
                  │
                  ▼
┌────────────────────────────────────┐
│              WORKCELL              │
│ source baseline                    │
│ exact accepted graph packet        │
│ factory runtime                    │
│ local trace/evidence               │
│ deterministic feature/ticket DAG   │
│ builder → validate → review        │
│          ↘ repair ↗                │
│ accepted local commits             │
└─────────────────┬──────────────────┘
                  │
             RESULT / EVIDENCE
                  │
                  ▼
┌────────────────────────────────────┐
│         TRUSTED SUPERVISOR         │
│ verify                             │
│ persist provenance                 │
│ push branch                        │
│ create draft PR                    │
└─────────────────┬──────────────────┘
                  │
             HUMAN PR REVIEW
                  │
                 MERGE
```

This is a **logical topology**. It does not require multiple machines, containers, VMs, or processes.

The `APPROVED PACKET` is not an informal bundle. It is the exact accepted ticket-graph version/hash
recorded by the downstream planning controller, with its applicable accepted upstream bindings and
target repository baselines. The workcell verifies that acceptance and currency before use. It
cannot create the acceptance, silently substitute a graph, or keep executing after a bound source
is known stale.

---

## V1 workcell

For V1, the preferred workcell is deliberately boring:

```text
local Git worktree
+
small factory process
+
exact accepted graph packet
```

The worktree provides isolation from the developer's primary checkout while avoiding remote-runtime, lifecycle, credential, and recovery complexity before those problems exist.

The design should avoid unnecessarily embedding provider-specific vocabulary into domain contracts, but **V1 should not implement a generalized runtime/provider interface solely because future providers are imaginable**.

> **Features pay for seams. A real second runtime earns the provider abstraction.**

---

## Future runtime path — documented, not required

If a real need emerges for containers, local VMs, remote VMs, or hosted ephemeral sandboxes, use Warren/Inkwell as implementation references and derive the common contract from the two real implementations.

Potential future lifecycle concepts include:

```text
provision
populate
execute
observe
finalize
terminate
```

These are **design hypotheses/reference vocabulary**, not V1 interface requirements.

A future second runtime should trigger:

- explicit provider contract extraction;
- capability differences only if real differences exist;
- falsification tests proving run-domain logic does not leak provider details;
- boundary lint/enforcement where appropriate.

---

## Direct and mediated execution

### V1 normal path: direct execution

When an exact accepted ticket graph already defines the work:

```text
exact accepted ticket-graph binding
    ↓
preflight verifies graph currency, applicable upstream sources, and repository baseline
    ↓
select ready ticket from that graph
    ↓
deterministic ticket factory
    ↓
builder → validation → reviewers → accepted commit
```

A ticket file alone is not execution authority. The workcell enters only through the current graph
acceptance recorded by the downstream planning controller, including for a trivial one-node graph.
Do not pay orchestration-model cost to rediscover a known control decision.

### Future/exception path: mediated execution

A coordinator agent may become useful when choosing the next deterministic operation genuinely requires judgment, such as repeated `DESIGN_BLOCKED`, ambiguous recovery, or deciding whether to run a spike/split/escalate.

This is an **exception-handling intelligence layer**, not a V1 requirement or the center of normal execution.

---

## Isolation fan-out / best-of-N — future idea

Isolated competing workcells may eventually be valuable for:

- competing spikes;
- alternative design investigations;
- high-risk best-of-N attempts;
- roster/model comparisons.

Do **not** implement fan-out as routine V1 machinery. Revisit only after the single-workcell factory is reliable and a concrete use case justifies the additional cost, selection logic, and lifecycle complexity.
