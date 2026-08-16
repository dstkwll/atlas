# 16 — Learnings, Course Corrections, and Design Promotion Log

**Purpose:** Preserve not only what the design currently says, but **how and why it changed**. This is intended to protect the project from recency bias, repeated rediscovery, and future agents mistaking superseded ideas for current commitments.

**Snapshot date:** 2026-08-13

---

## 1. Why this log exists

As more external systems were reviewed, a predictable risk emerged:

> **The freshest repository can look like the shiniest architecture.**

A useful reference implementation should challenge the design, but it should not silently become the new center of gravity merely because it is concrete or recently discovered.

The standing rule is therefore:

> **External repositories supply evidence, implementation donors, failure history, and candidate ideas. Our documented invariants remain the baseline until an idea explicitly earns promotion.**

---

# 2. Major learning sequence

## L-001 — PlanF3: durable planning is useful; presentation is not architecture

### Initial attraction

PlanF3 made several good ideas highly visible:

- persistent planning artifacts;
- explicit relevant-file inventory;
- phase-level validation commands;
- amendments;
- fresh execution context.

### Deeper conclusion

Its central artifact combines too many responsibilities, and its apparent "closed loop" is still largely an LLM being instructed to behave like a deterministic controller.

Generated visual identity/HTML/images appear optimized for legibility/demo value rather than implementation correctness.

### Standing result

**Keep:** durable artifacts, validators, amendment provenance, file-impact awareness.

**Reject:** one giant plan/state/execution artifact; image-heavy planning; builder-authoritative status; prompt-only loop enforcement.

---

## L-002 — HumanLayer + Pocock: planning is a compilation pipeline, not one phase

### Previous state

The user's existing pipeline was a hodgepodge of grilling/brainstorming feeding specs/plans/tickets/slices.

### Clarification

HumanLayer/Dex's Product → Architecture → Program Design → Vertical Slices distinction exposed a missing abstraction boundary. Pocock supplied strong primitives for grilling, research, domain language, fog-of-war exploration, and vertical ticket formation.

### Standing result

The pre-implementation pipeline became:

```text
decision discovery
→ behavioral spec
→ system design
→ program design
→ vertical ticket compilation
```

Each artifact has one exclusive job and should reduce degrees of freedom without repeating upstream content.

---

## L-003 — `prototype` terminology was too overloaded; use `spike`

### Initial wording

The design sometimes used `prototype` for uncertainty-reduction work.

### Concern

"Prototype" can imply a user-facing artifact that inherently requires human evaluation.

### Standing result

Use **spike** for bounded work whose primary output is reduced uncertainty/evidence rather than production functionality.

A spike does **not** inherently require HITL. The consequential decision it informs may still be human-gated by policy.

---

## L-004 — SSSF: code owns the loop; agents are bounded workers

### Strong contribution

SSSF validated the inner-factory principle:

```text
reasoning/judgment → agent phase
known sequencing/state/test/git mechanics → deterministic code
```

Typed envelopes, bounded repairs, deterministic gates, and preserving builder context across correction cycles are strong implementation references.

### Correction after deeper inspection

Earlier language implied SSSF mechanically prevents all unauthorized repository writes. Its permission model is better described as **post-hoc verified**: repository mutation can be detected/rolled back/failed after the agent call.

### Standing result

SSSF remains the strongest reference for the **inner ticket-factory mechanics**, but not necessarily the codebase to fork wholesale.

And our trust principle is softened from:

> capabilities always enforce roles

into:

> **important boundaries are mechanically verified or enforced at the cheapest appropriate layer.**

---

## L-005 — Inkwell: runtime topology is separate from factory logic

### Strong contribution

Inkwell clarified three nested responsibilities:

```text
trusted host/supervisor
→ isolated execution environment
→ deterministic factory + bounded workers
```

It also demonstrated useful patterns around host-only credentials, disposable inference credentials, non-destructive harvest, direct vs mediated execution, and isolated fan-out.

### Initial overreach

The first reaction promoted a generalized provider-independent `WorkcellProvider` and several sandbox features too aggressively.

### Course correction

Those patterns are valuable **references**, but Inkwell does not prove we need remote VMs, fan-out, best-of-N, or an in-box coordinator in V1.

### Standing result

Keep the **logical supervisor/workcell/worker topology** and the principle that publishing authority is separate from implementation authority.

V1 may implement the workcell as nothing more than a local Git worktree.

---

## L-006 — Warren: operational failure history is valuable, but freshness must not redefine the system

Warren introduced the greatest recency-bias risk because it is more operationally mature and contains many elegant runtime concepts.

The design was therefore re-evaluated against existing invariants before accepting Warren-derived changes.

### Warren ideas that survived the skepticism test

#### A. Features pay for seams — **ACCEPTED PRINCIPLE**

Do not build a provider/plugin seam speculatively. A real second implementation pays for it.

#### B. Agent output is not lifecycle authority — **ACCEPTED INVARIANT**

Warren contains a concrete hardening case where agent-authored stream content had to be prevented from masquerading as trusted system lifecycle events.

This maps directly to our typed-envelope design:

```text
agent says "pass"
        ≠
controller marks PASS
```

#### C. Freeze resolved run configuration — **ACCEPTED / V1**

Warren freezes rendered agent definitions on the run. We extend that to a full resolved run manifest containing source/planning baselines and effective policy/roster settings.

#### D. Worklist belongs to project, not agent — **ACCEPTED PRINCIPLE**

Our Markdown tickets/specs/designs are project contracts. Models, harnesses, and sessions are replaceable workers.

#### E. Review findings should become gates when possible — **ACCEPTED OPERATING PRINCIPLE**

Repeated objective review findings should migrate into deterministic validators.

### Warren ideas deliberately demoted

#### General `WorkcellProvider` contract — **DEFERRED**

The contract is an excellent future reference, but our V1 currently has one real runtime: local worktree.

Trigger for promotion: second actual runtime.

#### Provider capability flags/registry — **DEFERRED WITH THE SEAM**

Useful once providers genuinely differ.

#### Boundary falsification tests/lint gates — **REQUIRED WHEN A SEAM IS CUT**

Do not create tests for speculative abstraction boundaries; when a real seam exists, make its falsification/enforcement part of Definition of Done.

#### Full resumable provider event streaming — **DEFERRED**

V1 can use ordered local JSONL events. Remote cursor reconciliation belongs to future distributed execution.

#### `finalize → salvage → terminate` — **FUTURE EPHEMERAL-RUNTIME INVARIANT**

Critical if ephemeral workspaces can disappear; unnecessary ceremony around a durable local worktree.

#### Preview environments — **FUTURE REVIEW UX**

Potentially valuable, not core architecture.

#### `factory prime` — **FUTURE AGENT ERGONOMICS**

Self-describing machine-first CLI is attractive but should be built only if real usage demonstrates documentation drift/agent-discovery problems.

#### Forge/plugin ecosystem — **DO NOT BUILD NOW**

Avoid speculative GitHub/GitLab/Azure DevOps abstraction. Keep domain vocabulary generic enough not to poison future options, but let a second forge pay for the seam.

#### Serial multi-PR plan runs — **FUTURE DELIVERY STRATEGY**

Potentially valuable for staged migrations; not the default vertical-ticket feature model.

---


## L-007 — Ringer: measure staffing outcomes; do not turn the factory into an auto-benchmarking platform

Ringer was reviewed specifically because the design already had a `roster` dimension but had not yet specified how model/harness choices should be represented or improved over time.

### Strong contribution

Ringer separates several things that are easy to conflate:

```text
trained model
harness / agent shell
access or billing route
explicit reasoning effort
```

It also records `task_type`, per-attempt outcomes, duration/tokens, retries, and executed-check verdicts, then distinguishes **first-try pass rate** from final retry-rescued pass rate.

This sharpened our roster design substantially.

### Accepted additions

#### A. Role and worker are different — **ACCEPTED PRINCIPLE / V1**

A role such as `builder` defines authority/responsibility. A worker configuration defines the model/harness/access/reasoning implementation currently staffing that role.

#### B. Route by role × task shape — **ACCEPTED PRINCIPLE / V1**

A mechanical edit and an architectural refactor may both use the `builder` role while justifying different worker configurations.

Keep the task-shape taxonomy small until evidence proves further categories useful.

#### C. Track first-try and eventual success separately — **ACCEPTED / V1 TELEMETRY**

Final pass rate can hide expensive repair dependence. Preserve attempts so the factory can calculate first-try success, eventual success, repair count, reviewer rejection, duration, and cost/tokens when known.

#### D. Our workload generates our staffing evidence — **ACCEPTED PRINCIPLE**

External benchmarks are leads, not proof. A model that performs well on someone else's task mix remains unproven for our role/task shape until local evidence accumulates.

#### E. Validator baseline preflight — **ACCEPTED / V1**

Where a ticket declares expected baseline behavior for a validator, execute the validator before spending worker attempts. A contradictory baseline result means the check/ticket is wrong or already satisfied.

### Deliberately constrained

#### Automatic promotion/demotion — **REJECTED FOR V1**

Telemetry may produce evidence-backed roster recommendations. It does not modify roster defaults by itself.

Human review remains the promotion mechanism initially.

#### Ringer's exact promotion thresholds — **NOT ADOPTED**

The specific sample-count/first-try thresholds are lightweight heuristics suitable to Ringer's product, not universal statistical truth for this factory.

#### Model-specific steering lifecycle — **DEFERRED**

Ringer demonstrates a thoughtful candidate/confirmed/refuted/stale steering model. Preserve it in the borrow map as prior art, but implement nothing beyond optional notes until repeated local evidence shows generic role packages are insufficient.

#### Catalog exploration / autonomous bakeoffs — **DEFERRED**

Interesting optimization layer; not required for reliable software delivery.

#### Swarm-first cheap-worker philosophy — **REJECTED AS AN INVARIANT**

The standing rule is instead:

> Use the least expensive worker configuration that accumulated evidence shows is adequate for the role/task shape/risk, without weakening deterministic validation, review, or governance.

### License/provenance note

Ringer's observed license at this snapshot is PolyForm Shield 1.0.0 rather than MIT. Treat it primarily as a concept/reference source and re-check any pinned revision before source-code reuse.

### Standing result

v0.3 adds `17-agent-roles-rosters-and-model-policy.md` and `18-v0.3-decisions.md`.

The Ringer review changes **how we staff and learn from workers**, not the core planning pipeline, ticket factory, supervisor boundary, or governance model.

---

# 3. The promotion framework for external ideas

Every external idea should have two independent classifications.

## Architectural disposition

```text
REUSE
ADAPT
CONCEPT
REFERENCE
REJECT
```

## Maturity in our design

```text
OBSERVED
    Interesting external idea.

CANDIDATE
    Appears applicable to a problem we actually have.

ACCEPTED_PRINCIPLE
    Belongs in the architecture independent of a specific mechanism.

IMPLEMENTATION_REFERENCE
    Revisit when implementing the affected subsystem.

DEFERRED
    Valuable only after a named triggering condition occurs.

ADOPTED
    Actually implemented locally.

REJECTED
    Considered and intentionally not pursued.
```

This prevents `ADAPT` from being misread as "build this immediately."

---

# 4. Promotion test

Before a new idea becomes core architecture, answer:

1. **What existing problem in our design does this solve?**
2. **Does the problem exist now, or are we imagining a future problem?**
3. **Can we preserve the principle without implementing the mechanism yet?**
4. **Does it simplify an existing component or add a new noun/subsystem?**
5. **Is it grounded in working implementation or only design prose?**
6. **If implementation-grounded, what pressure/failure caused it to exist?**
7. **Does it conflict with a previously accepted invariant?**
8. **Can it wait until a concrete trigger makes the need obvious?**

The burden of proof is higher for a new subsystem than for a cheap invariant.

---

# 5. Current minimalism rule

The intended V1 is **not** a general software-factory platform.

It is:

```text
planning contracts
      ↓
approved ticket
      ↓
local worktree
      ↓
small deterministic ticket factory
      ↓
validated + independently reviewed commit
      ↓
feature integration
      ↓
draft PR
      ↓
human
```

V1 should include only the supporting machinery needed to make that reliable:

- control/governance policy;
- frozen run manifest;
- typed envelopes;
- controller-owned state transitions;
- simple state/evidence/event persistence;
- deterministic validators;
- mechanical verification of important write boundaries;
- bounded repairs;
- independent reviewers;
- `DESIGN_BLOCKED` escalation;
- stable role packages + small task-shape taxonomy;
- frozen worker/model/harness provenance;
- per-attempt outcome telemetry for later human roster review;
- validator baseline preflight where declared.

Everything else must earn its way in.

---

# 6. Future ideas to retain in comments/docs without implementing now

Keep these searchable so implementation teams know prior art exists:

- container/VM/hosted workcells;
- formal runtime-provider contract;
- provider capability registry;
- isolated best-of-N;
- remote resumable event cursors;
- salvage-before-destroy;
- live preview review surfaces;
- machine-self-describing `factory prime` command;
- staged multi-PR delivery;
- forge/provider abstraction;
- stronger preventive OS/filesystem capability enforcement.

For each, the reference implementation borrow map should name which upstream files to revisit if/when the trigger occurs.

---

# 7. Current meta-learning

The strongest architecture is not the union of every good idea found in every repository.

It is the **smallest coherent set of mechanisms that preserves our core invariants and solves problems we actually have**, while retaining enough provenance to cheaply recover proven patterns when new requirements appear.

The reference repositories are therefore treated as:

- **Pocock / HumanLayer:** planning and abstraction donors;
- **Superpowers:** execution/review discipline donor;
- **SSSF:** inner factory mechanics donor;
- **Inkwell:** supervisor/workcell/trust-topology donor;
- **Masterplan:** durable-state/resume donor;
- **Warren:** production-runtime failure-history and future control-plane donor;
- **Ringer:** model-identity / roster-telemetry / validator-preflight reference donor;
- **Groundwork / PlanF3 / Maciej gist:** selective idea/checklist donors.

No single repository is the architecture.

---

## L-008 — The architecture itself needs governance once chat becomes a hidden dependency risk

### Trigger

After v0.3, the architecture had become coherent enough that losing or subtly drifting it became a more serious risk than generating additional ideas. Long conversational context introduces failure modes such as compression, recency bias, partial recollection, and quiet rewriting of earlier decisions.

### Key distinction

The conversation is useful as a **reasoning environment**, but must not be the architecture's memory system.

### Standing result

v0.4 introduces `00-architecture-governance.md` as a process constitution for future architecture work.

Material changes now follow:

```text
EXPLORATION
  ↓
CANDIDATE
  ↓
read canonical affected docs
  ↓
pressure-test against invariants/history
  ↓
ACCEPT / DEFER / REJECT
  ↓
if accepted: surgical document delta + decision record + consistency audit
```

The current architecture must be reconstructable without chat history.

### Migration-health model

Architecture checkpoints now explicitly classify the working environment as:

```text
CHAT_NATIVE
GIT_READY
GIT_REQUIRED
```

At v0.4 the project is **CHAT_NATIVE, approaching GIT_READY**. The transition should be driven by implementation/diff/concurrency needs rather than arbitrary conversation length.

This historical status is superseded by L-009.

### Course-correction rule

Future snapshots should never be regenerated wholesale from remembered conversation. They are created from the current canonical snapshot plus accepted deltas.

This turns context compression from a potential architecture-loss event into a recoverable inconvenience: future agents are expected to re-read the canonical packet.

---

## L-009 — Git is now the artifact authority; agent instructions are shared repository state

### Transition

Atlas has completed the Git-authority transition anticipated by v0.4. The GitHub repository is now the canonical artifact authority, and `main` is the current canonical architecture state. Chat remains the primary architecture/design reasoning room.

### Operating consequence

Repository mutations are performed through coding agents such as Codex or a manual Git workflow, reviewed as branch diffs through draft pull requests, and merged only under human control.

The root `AGENTS.md` is the shared repository-wide operating contract for architecture and coding agents. Architecture-specific evolution rules layer on top through `architecture/AGENTS.md`. Tool-specific files should point to the root contract rather than creating competing instruction sets.

### Standing result

Future agents must ground material work in repository state, implement only explicitly accepted architecture changes, edit modular documents surgically before regenerating the rolling monolith, and stop when a request conflicts with current architecture or invariants.

---

## L-010 — Calibration Run 001 validated constraint layering and exposed contract-observability gaps

### Evidence scope

Calibration Run 001 was one manual execution-factory simulation. Its results are empirical evidence for refining the process, not proof that every future workflow must have the same shape.

### Observations

- The planning pipeline successfully constrained the implementer; the executor described the work as almost entirely implementation of an already-designed solution.
- Behavioral, system-design, program-design, and execution-ticket constraints each materially reduced uncertainty.
- Concrete acceptance tests and delivery checks were valuable, while repeated restatements of closed constraints added less value than one authoritative constraint section.
- The rolling-monolith separator and absence of a prefix or suffix leaked into implementation because the derived-artifact format lacked an explicit authoritative definition.
- Some externally observable process behavior was not tested at the actual public boundary, showing that acceptance contracts should be mapped to the appropriate validation boundary.
- Execution-environment preflight caused more friction than product or design ambiguity.
- The root agent contract mixed repository-wide execution rules with architecture-document evolution rules.

### Accepted consequence

The root contract now contains shared repository rules, while `architecture/AGENTS.md` contains architecture-specific evolution rules. Agents must name grounding sources, report what validation did and did not establish, and surface contradictions among authoritative sources rather than silently reconciling them.

This refinement preserves the canonical-source rule and architecture governance. It does not establish an "execution first at all costs" mandate. Architecture work may still resolve contradictions, preserve rationale, clarify authority boundaries, record failure modes, and reduce future ambiguity; the existing features-pay-for-seams and current-problem tests remain the controls against speculative architecture.
