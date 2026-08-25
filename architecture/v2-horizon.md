# Atlas V2 Horizon

> **STATUS: NON-AUTHORITATIVE HORIZON**
> This file records deferred Atlas hypotheses worth preserving. It is not part of the numbered canonical architecture, not a V1 requirement, not a roadmap, and not a commitment to implement. Every item requires an explicit reviewed promotion decision against then-current canonical architecture. Canonical generation/validation must not treat this file as an input to `rolling-monolith.md`.

## Governing rule

Features pay for seams. An option may be promoted only when its named trigger is observed and the smallest proposed seam is still justified. Donor availability, novelty, and imagined future flexibility are not triggers.

Each promotion review must record:

```text
observed problem
measured/credible trigger
current canonical constraint
donor/provenance
minimum proposed seam
authority that remains outside
falsification/removal condition
```

## H-01 — Proof reuse and invalidation

**Hypothesis:** Bound deterministic proof receipts can safely avoid repeated expensive checks when exact proof inputs and environment equivalence remain valid.

**Trigger:** Deterministic validation cost materially dominates execution and real runs repeatedly reproduce identical proof inputs.

**Minimum seam:** A narrow proof-reuse decision over exact check semantics, graph/ticket binding, repository tree, relevant inputs/configuration, and declared environment facts.

**Authority outside:** Accepted graph truth, validator meaning, ticket acceptance, and promotion remain Atlas controller/supervisor authority. Cached evidence never self-authorizes reuse.

**Falsify/remove when:** Equivalence is unreliable, invalidation complexity approaches rerun cost, or stale-proof incidents occur.

**Donors:** Working Skill Repo; donor synthesis C-06.

## H-02 — Stable response-required presentation contract

**Hypothesis:** Multiple hosts/UIs may need a stable derived indication that the user must respond now, may intervene, or need not act.

**Trigger:** Real host integrations repeatedly mis-present existing HUMAN, external-wait, BLOCKED, and completion states.

**Minimum seam:** A read-only presentation projection derived from authoritative state; no new lifecycle state or gate.

**Authority outside:** Existing owner/controller state remains the sole workflow truth.

**Falsify/remove when:** Gazetteer prose and owner-specific states remain sufficient.

**Donor:** Working Skill Repo; donor synthesis C-08.

## H-03 — Parallel scheduling and resource claims

**Hypothesis:** Independent ready tickets can execute concurrently when temporary resource/file/conflict claims are kept separate from engineering dependencies.

**Trigger:** Sequential execution is trustworthy and measured throughput is a meaningful bottleneck across a sustained sample.

**Minimum seam:** Ready-set scheduler plus temporary claims; no mutation of Stage 5 prerequisite edges or accepted preferred order.

**Authority outside:** Stage 5 dependency truth, ticket readiness, acceptance, integrated-tree proof, and publication remain supervisor authority.

**Falsify/remove when:** Conflict/merge/revalidation cost erases throughput gains or semantic reconciliation becomes normal.

**Donors:** Working Skill Repo; cautious contrast with Sandcastle parallel/merge examples; donor synthesis C-11/C-24.

## H-04 — Non-authoritative project orientation map

**Hypothesis:** A provenance-bearing repository map can reduce repeated source-orientation cost without becoming engineering truth.

**Trigger:** Multiple runs show materially expensive repeated orientation and stale-map fallback can be made reliable.

**Minimum seam:** Read-only navigation cache with source pointers, confidence/freshness, and mandatory fallback to source inspection.

**Authority outside:** Accepted artifacts and repository source remain authoritative; Gazetteer cannot use the map to invent workflow truth.

**Falsify/remove when:** Maintenance/staleness cost exceeds saved investigation or agents begin treating the map as truth.

**Donor:** Working Skill Repo `kb-map`; donor synthesis C-17.

## H-05 — Durable cross-run goal governor

**Hypothesis:** Long-lived objectives may need coordination and proof across multiple bounded Atlas feature runs and external waits.

**Trigger:** Atlas first reliably executes one accepted graph, survives an external wait, completes a PR lifecycle, and then real objectives repeatedly outlive individual runs.

**Minimum seam:** One objective record that references bounded runs and objective-level evidence; it does not absorb their internal controllers.

**Authority outside:** Each run’s planning/execution truth remains with its existing owners; goal state cannot manufacture run acceptance.

**Falsify/remove when:** Objectives are adequately handled as independent runs plus human coordination, or governor state duplicates run authority.

**Donor:** Working Skill Repo; donor synthesis C-18.

## H-06 — Oscillation and no-progress detection

**Hypothesis:** Some execution traces may thrash despite bounded local repair attempts.

**Trigger:** Repeated real traces show recurring cycles or stalled progress not safely handled by attempt bounds and terminal states.

**Minimum seam:** Read-only trace detector that surfaces a typed blocker/recommendation; no autonomous redesign.

**Authority outside:** Supervisor/controller determines the legal stop/escalation; detector findings are evidence only.

**Falsify/remove when:** Simple bounds eliminate the issue or detector noise causes unnecessary stops.

**Donor:** Working Skill Repo; donor synthesis C-19.

## H-07 — Strong isolation and credential boundaries

**Hypothesis:** Some tasks require disposable containers/VMs/remote sandboxes with structurally withheld supervisor capabilities.

**Trigger:** Local worktrees are insufficient for observed trust, reproducibility, dependency, or credential risks, or a real second runtime is required.

**Minimum seam:** Runtime adapter for the required provider plus bounded worker credentials, external lifecycle ownership, restart reacquisition, and evidence harvest before destruction.

**Authority outside:** Trusted supervisor retains planning/graph readiness, HITL, credential minting, peer environment lifecycle, evidence sealing, commit/publication, and unrelated repository access.

**Falsify/remove when:** Isolation does not materially reduce the observed risk or adapter/credential complexity exceeds benefit.

**Donors:** Inkwell; Sandcastle runtime providers as candidate substrate; donor synthesis C-25/C-26.

## H-08 — Closed disposable-environment record

**Hypothesis:** A small closed-schema environment record can support restart, harvest, and cleanup without a workflow database.

**Trigger:** H-07 produces a real disposable runtime with lifecycle state not represented by the local V1 run record.

**Minimum seam:** Environment locator, Atlas run/ticket binding, repo identity, expected head, session handle, credential-lease identity without secret material, harvest state, and cleanup state.

**Authority outside:** The record reports lifecycle facts; it does not own ticket readiness or acceptance.

**Falsify/remove when:** Existing runtime state suffices or fields proliferate into a second workflow controller.

**Donor:** Inkwell; donor synthesis C-29.

## H-09 — Best-of-N bounded implementations

**Hypothesis:** Competing isolated implementations of the same accepted ticket may improve outcomes for narrow risky, objective, performance, or calibration tasks.

**Trigger:** Single-attempt execution is trustworthy and a concrete work class shows measured benefit from competition.

**Minimum seam:** Fixed accepted ticket/brief, isolated candidates, deterministic elimination/objective measurement, fresh semantic comparison, and HUMAN judgment only for genuine remaining taste.

**Authority outside:** Candidates cannot redesign upstream truth; selection and acceptance remain Atlas/human authority.

**Falsify/remove when:** Cost or selection ambiguity outweighs quality gains.

**Donor:** Inkwell; donor synthesis C-30.

## H-10 — Optional environment-local coordinator

**Hypothesis:** A future runtime may need bounded environment-local steering that deterministic kickoff cannot express.

**Trigger:** Real tickets repeatedly require legitimate in-environment coordination after accepted design, and the need cannot be removed through better deterministic brief/workcell design.

**Minimum seam:** Optional coordinator inside one environment and authority envelope; never the normal path.

**Authority outside:** Ticket selection, graph readiness, accepted truth, staffing policy, retries, commit, and publication remain outside with the trusted supervisor.

**Falsify/remove when:** Deterministic kickoff remains sufficient or coordinator decisions drift into planning/acceptance.

**Donor:** Inkwell’s contrast between deterministic and agent-mediated kickoff; donor synthesis C-27.

## H-11 — Review-topology simplification checkpoint

**Type:** Empirical decision checkpoint, not a promised feature.

**Trigger:** A meaningful sample shows one semantic reviewer axis has low unique blocking yield, high overlap/noise, or poor cost-to-repair value.

**Decision:** Simplify, combine, or retarget reviewers only while preserving fresh independent semantic judgment required by accepted policy.

**Authority outside:** Deterministic validation and governance requirements remain unchanged.

**Donors:** Working Skill Repo; donor synthesis C-09/C-10.

## Explicitly not horizon commitments

The following remain rejected or already canonical rather than deferred V2 promises:

- Sandcastle/SSSF runtime planner;
- donor skill taxonomy as product UX;
- normal merge-agent reconciliation;
- worker-owned commit or acceptance;
- artifact-presence routing;
- automatic model promotion;
- generalized provider abstraction before a second real runtime;
- background event infrastructure without a real requirement.

## Provenance

- Full donor synthesis: https://drive.google.com/file/d/1DG4eFaR4o0S64a4bWbq5Ge7vMFTcK3de/view
- Sandcastle architecture analysis: https://docs.google.com/document/d/1w8BL5PuGLDnaGVpvK7IkFfQwbnNxGLRGyLLU9-_ACv8/edit
- Sandcastle: https://github.com/mattpocock/sandcastle/commit/e99f832f26dc9d245c019a9ddd19fa5dee792427
- Working Skill Repo: https://github.com/Irtechie/working-skill-repo/commit/91a1b2f206dc5a6304c913df62426996b61603a1
- SSSF: https://github.com/disler/super-simple-software-factory/commit/de31374882e7a4e3e5b7bb9bd09e69dc2f779356
- Inkwell: https://github.com/disler/inkwell-agent-sandboxes-and-software-factory/commit/92f1701810993b8303562265ba04c727468fe070
