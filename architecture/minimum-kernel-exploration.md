# Minimum-kernel exploration

**Status:** `EXPLORATION` — non-authoritative.

**Date opened:** 2026-09-01.

**Canonical baseline:** `cd9d5dc488d88c9b5d03b96da2e515a9caf14c28`.

This document records a design pivot for investigation. It does not amend the numbered architecture, revoke an accepted decision, authorize implementation, or make this proposed shape canonical.

## Why Atlas is regrouping

Atlas has demonstrated real value in planning runs:

- exact accepted artifacts and source bindings made approvals auditable;
- frozen repository baselines exposed a material mismatch between an accepted design and production code;
- `DESIGN_BLOCKED` prevented downstream work from silently redesigning the accepted system;
- fresh semantic review found missing production paths, unreachable behavior, incomplete failure data, and validators that would not prove runtime behavior;
- a structured ticket graph ultimately bound executable validation assets, binary provenance, evidence destinations, and behavior-level proof;
- visual decision support improved human review.

Atlas has also accumulated machinery whose cost appears disproportionate to the authority it protects:

- Markdown headings, markers, tables, and section order treated as machine protocols;
- non-authoritative HTML projections participating in workflow legality;
- controller state duplicated in candidate frontmatter;
- structured execution declarations mirrored into ticket prose and then reconciled;
- exact section-selection protocols created so workers do not read complete accepted documents;
- specialized repair state, evidence, attempt, and revision machinery;
- tests that preserve presentation grammar or mirrored architecture wording rather than behavior.

PR #31 made the mismatch visible. A narrow projection-compatibility problem expanded into an intentional-revision transition, repair/revision discrimination, compatibility handling, revision arithmetic, and broad architecture updates. PR #31 was closed unmerged; its evidence remains available.

The working hypothesis is:

> Models understand planning documents. Deterministic code understands identity, authority, legal state, repository facts, execution graphs, commands, and proof.

## Proposed minimum kernel

The following capabilities are presumed valuable enough to retain during exploration, but their current implementation is not presumed optimal.

1. **Exact identity and provenance**
   - accepted artifact hash;
   - exact source binding;
   - repository baseline and candidate-tree identity;
   - review/evidence identity.
2. **Explicit authority**
   - human and configured reviewer authority remain distinct from producer claims;
   - a producer cannot accept its own work;
   - participation mode does not create authority.
3. **Legal state transitions**
   - deterministic code validates and records transitions;
   - state writes are atomic and have unambiguous outcomes;
   - downstream work cannot silently change accepted upstream truth.
4. **Semantic judgment**
   - capable models and humans interpret immutable accepted planning material;
   - whether a worker receives complete documents or selected material remains an open design choice;
   - fresh semantic review judges completeness, feasibility, consistency, and no-redesign;
   - deterministic code does not grade prose.
5. **Executable truth**
   - structured execution data carries facts an executor must consume;
   - whether that data is one graph artifact or a smaller set of bound artifacts remains open;
   - dependencies, repository targets, runtime prerequisites, validators, evidence outputs, and proof bindings remain machine-readable when they affect execution;
   - exact-tree validation and deterministic commit remain downstream goals.
6. **Visible blocking**
   - conflicts between accepted planning and verified code produce `DESIGN_BLOCKED` rather than improvisation;
   - missing execution material blocks explicitly rather than being invented by a worker.
7. **Useful presentation without authority**
   - visual boards may remain valuable decision aids;
   - a projection never becomes a second source of truth merely because it is rendered or verified.

## Machinery under reconsideration

The exploration must determine whether to delete, collapse, or retain a smaller form of:

- deterministic Discovery, PRD, System Design, and Program Design prose grammar;
- mandatory HTML projection currency after canonical Markdown acceptance;
- candidate `status`, `gate_ready`, copied dates, and other self-attestation fields;
- ticket Markdown that mirrors structured graph data;
- exact-H2 execution-context declarations;
- separate Stage 0–2 and Stage 3–5 planning controllers;
- D-082's four-attempt repair episode, reservation protocol, retained context, and revision arithmetic;
- exact semantic-review envelope dimensions that no controller decision consumes separately;
- architecture tests whose observable behavior is prose repetition rather than contradiction detection.

No item in this list is deleted by this document.

## Evidence boundary

The exploration must not make the opposite mistake and remove structure that real execution consumes. A non-authoritative retrospective from one private multi-repository planning run reports that the run reached exact status `READY_FOR_EXECUTION` only after its accepted ticket graph included:

- real runtime validators rather than source-text checks;
- exact old/candidate binary provenance;
- deterministic materialization of session-scoped validation assets;
- persistent evidence destinations;
- exact fixture overlays and hashes;
- behavior markers proving positive and negative paths.

The private control file, accepted graph, and review receipt are intentionally not copied into this public repository. Treat the retrospective as provisional evidence until a reviewer with access verifies those exact artifacts. Even if verified, the result supports structured execution data, not automatically a new subsystem or first-class schema branch for every observed fact. A mechanism earns promotion only when an execution owner consumes it and a simpler representation cannot preserve the proof.

## Required walk-throughs

Before proposing canonical architecture changes, test the proposed minimum kernel on three existing cases:

1. **Upstream contradiction:** an accepted design conflicts with exact frozen production code. Determine the minimum safe path from contradiction evidence to a corrected, reaccepted design.
2. **Execution-proof compilation:** a ticket graph initially names incomplete validation assets, then becomes execution-ready through real validators, provenance, and durable evidence. Determine which facts genuinely require a machine schema.
3. **Ordinary planning:** a low-complexity change with no cross-repository or repair complexity. Confirm that the minimum path stays small rather than imposing the most complex workflow on every run.

For each case, record:

- the smallest trusted outcome;
- which actor supplies judgment;
- which deterministic facts must be checked;
- what may remain prose;
- machinery required only by the current representation;
- the first failure the smaller shape cannot handle.

## Promotion rules

A proposal from this exploration may become a canonical change only when it:

1. names the current problem and empirical evidence;
2. states the accepted invariant it preserves or intentionally amends;
3. removes or collapses more seams than it adds;
4. identifies the real consumer of every deterministic field and validation rule;
5. includes a separating behavior witness where code already exists;
6. states what remains unresolved;
7. receives explicit acceptance before numbered architecture or implementation changes.

## Immediate bounded work

Two narrow corrections are intentionally separate from the broader exploration:

- PR #32 fixed a repeated Windows false-failure after a successful atomic planning-state write and is merged.
- A future small change may remove post-acceptance HTML projection currency from authoritative planning-state loading while preserving the board as pre-acceptance co-design support. That change requires its own exact review and must not reintroduce PR #31's larger revision machinery.

## Open decisions

The walk-throughs must answer, one decision at a time:

1. Does accepted-design correction need an automatic repair episode, a general explicit amendment, or only `DESIGN_BLOCKED` plus a user-authorized new version?
2. Which planning-document checks protect authority, and which only protect presentation shape?
3. Should workers receive complete accepted documents or preselected sections?
4. Should executable truth be one graph artifact, a manifest plus ticket files, or another minimal representation?
5. Do two planning controllers protect a real authority boundary?
6. Which visual projections remain worth maintaining when none can block accepted truth?

Until those decisions are accepted, current `main` remains authoritative.
