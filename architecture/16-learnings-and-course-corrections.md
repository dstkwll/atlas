# 16 — Learnings, Course Corrections, and Design Promotion Log

**Purpose:** Preserve not only what the design currently says, but **how and why it changed**. This is intended to protect the project from recency bias, repeated rediscovery, and future agents mistaking superseded ideas for current commitments.

**Snapshot date:** 2026-08-25

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

#### Full `finalize → salvage → terminate` lifecycle — **FUTURE EPHEMERAL-RUNTIME MECHANISM; EVIDENCE-BEFORE-CLEANUP REFINED BY L-025**

The full credential/revocation/destruction lifecycle remains future work for ephemeral runtimes.
L-025/D-086 promotes only the cheaper invariant now: even a durable local worktree must harvest
required evidence before destructive cleanup, because V1 may remove that worktree and otherwise erase
its only execution facts.

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
exact accepted ticket graph
      ↓
selected ready ticket
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

Keep these searchable so implementation teams know prior art exists. The V1 evidence-before-cleanup
invariant is accepted; only the full ephemeral credential-revocation/salvage/termination mechanism
remains future:

- container/VM/hosted workcells;
- formal runtime-provider contract;
- provider capability registry;
- isolated best-of-N;
- remote resumable event cursors;
- full ephemeral `finalize → salvage → terminate` lifecycle;
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
- **Autoprompt:** compact-handoff / evidence-preserving-repair / execution-framework reference donor;
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

---

## L-011 — The single-repository assumption was never stated, and was wrong for the intended user

### How it surfaced

While designing the discovery skill's artifact output, the question *where does the decision log go* had no satisfactory answer. `03-artifact-model.md` prescribed `.planning/` inside the repository being changed. The intended user's work spans many small repositories, and a single unit of work commonly touches several.

### The finding

The assumption was **one run, one repository**, and it was never written down as an assumption. It appeared instead as a fixed path in the artifact model, a repository-relative default in the reference configuration, and a `.planning/**` deny rule in two capability documents. Nothing recorded that these depended on a claim about how repositories are organized.

An assumption embedded in four incidental places, and stated in none, is invisible until something contradicts it.

### What was rejected on the way

- **Distributing a copy of each decision into every affected repository.** This reproduces the problem an external root solves — several partial records that drift, and no answer to which is authoritative.
- **A pointer file in each repository naming the planning root as a local path.** A path meaningful only on its author's machine is worse than absent: it resolves to nothing for every other reader while appearing authoritative.

Both were proposed and both failed the same test — a record is only useful to a reader who can reach what it points at.

### Accepted consequence

The planning root became configuration (D-055), a feature declares the repositories it affects (D-056), the costs of an external root are recorded rather than mitigated (D-057), and an external root is treated as a location with an access model rather than a path (D-058).

### Standing result

Where the architecture fixes a location, it should say what it assumes about the surrounding organization. A default is legitimate; an unstated structural premise is not.

---

## L-012 — A judge with an unconditional requirement manufactured the artifact it was judging

### Evidence scope

One observed run of `advance`, a non-canonical incubation skill, on a real effort. This is a
single empirical observation of one implementation, not proof about every reviewer. It is
recorded because the mechanism is general and the failure was silent.

### What happened

An effort reached specification through ordinary grilling rather than Wayfinder discovery, so
it had no discovery map. Its terminal ship-readiness judge evaluated a `discovery-unclosed`
gap whose subject identity was hardcoded to a topic-root `map.md`. The file was absent. The
judge wrote one, then continued.

A read-only judge authored the evidence it went on to judge, and reported a result as though
it had assessed the effort.

### The defect

The skill's evidence contract already knew that a grilling-originated effort has no map:
presence routing selects between the Wayfinder and grilling branches on exactly that file,
and the grilling branch states that ordinary grilling never requires Wayfinder. The knowledge
was present and the ship judge did not consult it.

The gap itself carried **no applicability test**. Every other gap in that contract names an
artifact that must exist; this one names an artifact that exists for only one of two
discovery paths, and nothing said how to establish which path an effort took. Given a
requirement it could not satisfy and no way to rule it inapplicable, creating the file was the
locally reasonable move.

### Why it generalizes

The failure was not a missing prohibition. Read-only access was already the reviewer default,
and the outcome still occurred, because the reviewer was *instructed* to require something
that should never have applied. Enforcement sits downstream of specification: a reviewer given
an unconditional requirement will find a way to complete it.

An unconditional requirement is a defect wherever a workflow offers more than one route to the
same stage.

### Accepted consequence

`06-review-and-validation.md` now states, in the reviewer write policy, that a reviewer
establishes an artifact's applicability before requiring it, and that a missing required
artifact is a finding rather than something to supply.

### Standing result

Where a requirement depends on which path work took, its applicability test travels with it.
A reviewer reports what is absent; it never writes what is absent.

---

## L-013 — The first executable planning gate exposed three responsibilities, not one controller

### Evidence scope

One Stage 0–2 implementation in draft PR #5, followed by adversarial tests and independent
review. The controller worked, but implementation pressure exposed architecture the prose had
left unresolved.

### What happened

The implementation correctly removed lifecycle authority from producer skills, then made one
program responsible for semantic artifact grading, approval provenance, multi-file state,
recovery, and legal transitions. Hardening that surface produced locking, transaction journals,
approved copies, receipt ledgers, and hash chains before a real Stage 0–2 run had earned them.

### Accepted consequence

Stages 0–2 separate producer completion, read-only boundary judgment, configured acceptance
authority, and deterministic transition recording. Planning state uses one machine-canonical
`control.json`; `00-state.md` is a projection. Approval provenance is version/hash metadata in
that snapshot rather than copied artifacts, and the controller grades no prose.

The judge/drive seam from incubator `advance` is accepted as a **concept donor only**. Its
Workbench routing, leash, worker, ticket, and ship machinery remain non-canonical.

### Standing result

A mechanism already implemented has not earned itself. Keep deterministic machinery only when
a concrete current failure requires it and a materially simpler design does not survive that
failure. One explicitly retained exclusion mechanism is the run lock: atomic replacement
prevents torn state but not two revision-N writers overwriting each other, and a check
immediately before replace has the same race.

---

## L-014 — Autoprompt mostly reinforced existing rules; the missing rule was stage admission

### Evidence scope

Source inspection of `Spielewoy/autoprompt-skill` at commit
`1a195165c5e54ce33fc357425a0b3af7a8dae96f`, including its canonical contracts, generated provider
packages, installer/runtime code, and a separate proposal applying its ideas to Atlas.

### What changed under source comparison

The proposal attributed several useful ideas to Autoprompt: uncertainty-aware stage routing,
boundary-local repair, useful-first decomposition, compact handoffs, and evidence reuse. Source
inspection showed an asymmetric result:

- compact pointer handoffs, retained evidence, named repair loops, framework axes, and a final goal
  check are genuine Autoprompt prior art;
- evidence-local repair and selective workflow depth were already explicit in Atlas;
- an uncertainty-axis router and earliest trustworthy semantic entry are **not** implemented by
  Autoprompt, whose invoked missions still enter its minimum roadmap/reviewer topology;
- fresh architecture review corrected an overstatement about Atlas itself: initialization may
  coexist with a prescribed candidate (`20-prd.md` in the current vocabulary) without accepting it.
  The rule must therefore govern acceptance authority, not pretend every candidate file postdates
  control.

### Accepted consequence

Atlas records Autoprompt in the borrow map and makes one missing rule explicit: a boundary omitted by
the selected workflow is `NOT_REQUIRED`, while a required pre-existing artifact may skip production
but still passes its ordinary acceptance boundary. Semantic-stage admission and later
execution-framework selection remain separate decisions.

### Standing result

External prior art can expose a missing local distinction even when the proposed attribution is
wrong. Borrow the verified mechanisms, preserve the contrast that sharpened the design, and do not
import the source's hierarchy or prompt-first control model merely to obtain those ideas.

---

## L-015 — The separate discovery-to-spec translation pass was weaker than explicit product closure

### Evidence scope

Two-model review of the living-PRD redesign, grounded in the accepted Stage 0–2 control contracts
and the observed limits of non-authoritative reviewer freshness.

### What changed

Atlas had been carrying two ideas at once: discovery should settle intent before engineering
design, and a later translation from discovery into specification might catch omissions
incidentally. Review showed that the translation pass was not a proven independent review and
that its strongest incidental value could be replaced more explicitly.

### Accepted consequence

Discovery now continuously authors both `10-decisions.md` and `20-prd.md`, and exits through one
product-closure boundary. Closure requires the complete PRD-alignment retrospective, exact
`derived_from` binding to the current decision log, a regenerated `20-prd.html` projection, and
fresh semantic acceptance. The retrospective checks are exhaustive over identifiers and
best-effort over meaning.

### Standing result

Use deterministic cross-checking where the architecture can prove it, and say plainly where it
cannot. Reviewer freshness and read order remain procedural discipline, not authenticated state.

---

## L-016 — “Involvement tiers” conflated participation with authority

### Initial proposal

The first co-design proposal coupled degrees of user involvement to automatic architecture tiers
and gate behavior. That made collaboration look like another assurance profile.

### User clarification

The failure being addressed is detachment from AI-authored architecture, not insufficient approval
ceremony. Co-design must therefore be explicitly selectable whenever System Design is selected,
while acceptance authority remains an independent governance decision.

### Standing result

System Design has a separate participation axis: `agent_led` by default or user-selected
`co_design`. The classifier neither recommends nor selects co-design; intake neutrally presents both
choices to the user. Chat becomes the interactive control surface and accepted choices are written
into canonical Markdown; neither the
conversation nor its generated visual projections gains authority. Do not reintroduce automatic
co-design tiers.

---

## L-017 — A downstream binding follows the selected path, not a preferred upstream artifact

### Contradiction found

v0.7 initially required Program Design to bind accepted System Design, or an accepted PRD when
System Design was `NOT_REQUIRED`. The existing stage-admission contract also permits Program Design
to be the earliest selected producer when both upstream semantic boundaries are `NOT_REQUIRED`.
That valid path has neither accepted artifact, so the new binding rule accidentally made an older
admission path impossible.

### Standing result

A downstream reviewer and execution compiler carry the applicability test for alternative upstream
paths. Program Design binds accepted System Design when selected, accepted product closure when that
is the selected upstream semantic boundary, or the exact accepted/frozen Stage 0 effective intake
when both are omitted. Compilation and downstream review consume only the applicable accepted
sources and never restore a requirement for an omitted PRD or System Design. `NOT_REQUIRED` still
means absence, never approval; no runtime controller is implemented by this architecture correction.

---

## L-018 — The model router already existed; Discovery's question frontier was the thin seam

### Reframe

The initial request sounded like two new subsystems: model-tier routing for skills and model sparring
for Discovery. Repository-grounded review showed the first already existed as role × task-shape roster
resolution. Binding a whole skill to one model tier would have coupled reusable procedure to worker
identity and duplicated the existing precedence chain.

The real gap was earlier: independent review challenged answers and completed artifacts, but nothing
independently challenged whether Discovery's initial question frontier was complete and correctly
routed before user deliberation began.

### Standing result

Staff model invocations through role × task shape, with exact workers in configuration and model
diversity treated as conditional staffing rather than authority. Add one bounded, blind frontier
critic before the first grill round and repeat completeness/wrong-owner review in the existing final
cold read. Do not create a second router, a council per question, or runtime machinery in this
architecture-only change.

---

## L-019 — An “approved ticket graph” without an acceptance owner is an authority gap

### Contradiction found

The architecture gave `tickets` real gate policy, told the feature runner to load an approved graph,
and required execution preflight to verify approved upstream contracts. Stage 5, however, only
produced a graph. The Stage 0–2 controller stopped before design, the v0.7 design controller stopped
at Stage 4, and repository-scoped runtime state began after approval. The consumer assumed an
acceptance no producer was authorized to record.

Two blind reviews split on the next move. One proposed fixing the Stage 3–4 authority aggregate
first; the other independently confirmed the Stage 5 gap but proposed a separate compilation
controller. The user selected the smaller staleness topology: extend the existing downstream owner
rather than create a third place whose currency could disagree with design and execution.

### Standing result

One bounded downstream planning controller owns separate System Design, Program Design, and
compiled ticket-graph outcomes through Stage 5. It binds the accepted graph to exact applicable
upstream sources and target repository baselines, and records directly caused downstream staleness
in the same logical atomic transition as an upstream change. Execution verifies this acceptance but
cannot create it. A trivial run carries the same authority in miniature: one one-node graph binds
directly to frozen Stage 0 intake/configuration plus its target repository baseline and creates no
substitute PRD or design artifact. Execution checks graph currency at ticket preflight and again
before deterministic commit, closing the in-flight staleness interval. The controller owns no Stage
6+ execution state, and architecture deliberately leaves its exact file/schema to Program Design
rather than hard-coding storage prematurely.

---

## L-020 — Host calibration is evidence; user routing is a design defect

### Evidence scope

A bounded installed-host calibration on Copilot CLI 1.0.80 exercised the current System Design path
from one explicit user invocation. The producer handed off internally to `control-planning`, fresh
reviewer subprocesses returned two substantive `BLOCKED` results before a third seven-dimension
`PASS`, and the deterministic controller recorded `AGENT_APPROVED` at `program_design`. Installed
plugin bytes matched merged source before the run.

This demonstrates feasibility for that host, version, and path. It is not a continuing compatibility
guarantee. Codex chaining and D-077 roster resolution/provenance were not proved; the host selected
the observed reviewer workers without a shipped Atlas role × task-shape resolution record.

### Course correction

The first write-back put the dated Copilot result into executable skill prose and added a regression
test protecting the sentence that chaining was “proven.” That confused an observation with a product
contract: the test could stay green after a future host release broke the behavior.

### Accepted consequence

Preserve host calibrations here as dated evidence. Keep executable contracts host-independent and
test the required behavior where an executable compatibility harness exists, not the wording of a
past experiment.

### Standing result

Human attention is reserved for judgment and authority, not workflow routing. Internal stages,
skills, controllers, and host adapters must preserve one user-level invocation across internal
handoffs. Atlas may interrupt only when the required answer genuinely belongs to the user or when
policy requires explicit human authority. The user supplies judgment; Atlas supplies orchestration.
If a host cannot perform a named skill-to-skill handoff, the implementation must provide another
internal mechanism rather than shift orchestration to the user.

---

## L-021 — Repository identity is not repository access, and environment failure is not design failure

### Contradiction found

The first real Program Design implementation repeated the frozen repository identity and baseline in
its evidence while inspecting a nearby checkout. Canonical architecture already said those fields
were descriptive and granted no access. The implementation therefore had no lawful identity-to-byte
resolution mechanism, and current `HEAD`/worktree could silently stand in for the frozen baseline.

### Course correction

The first stop correctly treated the missing resolver contract as an architecture contradiction, but
then over-generalized: it described a future machine that lacked a configured source or commit as
`DESIGN_BLOCKED`. External review separated the two propositions. Absence of a system-wide resolver
contract is a design gap; absence of a local dependency after that contract exists is ordinary
`BLOCKED`.

### Standing result

Portable runs record stable identity plus baseline. A confirmed machine-local binding resolves that
identity to one already-usable Git object source, and Program Design reads the exact full commit tree
without touching the current checkout. Missing mapping/object/content is `BLOCKED`; only a
code-grounded need to change accepted upstream truth is `DESIGN_BLOCKED`. Never dress setup failure
as an architectural finding, and never dress an architectural contradiction as setup work.

The machine binding is intentionally absent from portable resolved configuration and its hash. It is
re-read per attempt because two machines may reach the same immutable Git commit through different
paths. Conversely, an abbreviated baseline is not an environment problem that a binding can repair;
new intake records the full ID, and an already-downstream V1 run with bad intake starts again rather
than gaining an invented reopen path.

---

## L-022 — A session-local repair cap is not a durable bound

### Initial attraction

The initially attractive session-local four-step cap was not durable. It looked bounded in
conversation, but a restarted skill, process, or session could begin the count again. The same
apparent safety limit therefore authorized unbounded producer work over time.

### Course correction

The exact four-attempt budget belongs to D-080's deterministic downstream planning controller, not
to an agent session. The controller must reserve and persist each attempt before producer-owned
candidate writes; a crash consumes the reservation. Review, controller transitions, and authority
acts do not spend it, and restart cannot reset it.

### Standing result

Exact repair budgets must be controller-owned and persisted before writes. A second contradiction
cannot nest or reset the active episode, and exhaustion must remain loud and durable. The same
persistence discipline applies to the repair's why: every replacement evidence envelope carries the
complete validated contradiction finding plus its one immediate superseded acceptance and original
contradiction reference/hash, without turning that provenance into recursive history.

---

## L-023 — Loud repair failure ends autonomous authority, not necessarily the goal

### Initial attraction

A durable exhausted D-082 episode can look terminal: the controller cannot legally advance, so
"fail loudly" is easy to read as "the work is dead." The opposite shortcut is also tempting—offer
the user a menu of internal stages and let them operate the compiler.

### Course correction

The durable `BLOCKED` state is a statement about Atlas's current authority, not a product judgment.
Atlas should diagnose the preserved evidence first: shared failure assumptions, nearest accepted
truth plausibly responsible, materially different architecture families, and consequences of
changing product or run assumptions. The diagnosis recommends; it does not authorize.

### Standing result

After one bounded automatic repair cannot converge, the human chooses a substantive direction:
another materially different architecture, upstream product reconsideration, corrected successor
run, or stop/defer. Atlas owns internal orchestration, but no recovery mechanism is implied until a
real failed case earns it. Preserve the principle now and return implementation energy to the normal
Stage 5 Ticket Graph Compiler path.

---

## L-024 — A vertical label does not make horizontal work vertical

### Course correction

An earlier decomposition called layer slabs "vertical slices" while sequencing schema, services,
interfaces, and integration separately. That delays the only proof that matters: whether the accepted
boundaries compose into real behavior.

### Standing result

Stage 5 follows behavior paths across every boundary they require, not a checklist of every layer.
The first frontier targets important risky seams, and each non-enabling ticket is outcome-bearing and
independently verifiable. Standalone enabling work must name its imminent vertical consumer and prove
it cannot safely be inlined; imagined future reuse does not earn a foundation seam.

---

## L-025 — Mature donor machinery predicts failures; it does not pre-authorize its solutions

### Evidence reviewed

Sandcastle, Working Skill Repo, SSSF, and Inkwell independently cover runtime problems Atlas is about
to encounter: workspace/session lifecycle, supervisor ownership, proof and blocker evidence, repair,
cleanup, isolation, and long-running recovery. The risk was importing each donor's mature control
machinery merely because it already exists.

### Reconciliation

Most donor findings confirmed accepted Atlas architecture. The few V1 gaps were obligations an
implementer would otherwise have to guess: one coherent repo/run accepted-chain workspace with
per-ticket logical workcells; one active ticket across the accepted planning graph and one small
closed runtime authority per target repository; sufficiently bound wait/proof evidence; contained
helper-agent behavior without delegation of Atlas ownership; exact integrated-tree promotion;
evidence harvest before destructive cleanup; and explicit implementation-versus-delivery separation.

The evidence-before-cleanup invariant moved from future-only wording into V1 because Atlas already
creates and may remove local worktrees. Only the invariant moved; disposable-environment machinery
did not. Conversely, Working Skill Repo's goal/proof governors, resource scheduler, project graph,
and oscillation system, plus Inkwell's VMs/credentials and Sandcastle's planners/merge agents, remain
deferred or rejected.

### Standing result

Use SSSF as the ticket-workcell protocol donor, Working Skill Repo as the supervisor-behavior donor,
Sandcastle only as a bounded execution-substrate proof-of-fit candidate, and Inkwell as the future
strong-isolation topology donor. A dependency can run machinery; it never receives Atlas authority.
Preserve future hypotheses with explicit triggers in unnumbered `v2-horizon.md` rather than turning
them into V1 requirements or a roadmap.

---

## L-026 — A pointer-only ticket defers semantic selection into execution

### Contradiction found

D-085 required one execution-complete graph and rejected a runtime planner, while the current ticket
shape carried only source kinds and section names under `references`. That left the concrete reason a
source constrained a ticket implicit and made it easy for a later supervisor to select, summarize,
or fill semantic context while assembling a worker brief.

### Reconciliation

D-087 fixes the current ticket-graph manifest at exact integer version 2 and replaces top-level
`references` with exact `context.sources`. Stage 5 selects every applicable accepted source kind,
its exact semantic H2s, and a nonempty purpose. The judge evaluates semantic completeness; the
supervisor only validates/materializes the accepted declaration plus current runtime facts.

### Standing result

Version 1 is raw historical evidence only and is not loadable or factory-executable; no compatibility projection or
fallback exists. Missing declared material is a packaging/preflight blocker. Missing accepted
judgment is `DESIGN_BLOCKED`. Repository facts within granted inspection authority remain
discoverable without becoming undeclared planning truth. No execution runtime or planning-run
migration is introduced by this correction.
