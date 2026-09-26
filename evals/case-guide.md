# Atlas case guide

Choose a case by the behavior at risk, then read its rubric and the linked public topic evidence before grading. Each registered ID below appears once. The grouping describes **purpose**, not execution status, success, independence, or held-out coverage. [README](README.md) owns running, evidence interpretation, claim limits, and selection of next evidence. [review.md](review.md) supplies the common four-dimension rubric; the links below locate additional governing criteria.

## Proportionate response and conversational progression

**Rubric:** [initial case criteria](review.md#case-specific-acceptance), [turn endings](review.md#turn-ending-guidance-across-intent), [acknowledgment criteria](review.md#documentation-reflection-impact-and-optional-comparison). **Public evidence:** [turn-ending observations](../docs/validation/turn-ending-guidance.md).

| Cases | Boundary to inspect |
| --- | --- |
| `typo`, `design-constrained-choice`, `guidance-question` | Answer a small or constrained request without an invented workflow or alternatives. |
| `missing-guidance` | Report the unavailable local dependency without claiming activation or borrowing another installation. |
| `closing-ack`, `guidance-decision`, `guidance-correction`, `guidance-complete`, `guidance-pause` | Carry accepted design forward, apply a correction, or honor actual completion and pause; courtesy is not an authority grant or automatic stop. |

## Authorized repair and unresolved decisions

**Rubric:** [repair and initial authority criteria](review.md#case-specific-acceptance), [continuation and input requests](review.md#continuation-and-clear-input-requests), [open-policy delivery variants](review.md#extended-discovery-and-transition-experiments). **Public evidence:** [turn endings](../docs/validation/turn-ending-guidance.md), [discovery transitions](../docs/validation/discovery-transitions.md).

| Cases | Boundary to inspect |
| --- | --- |
| `repair`, `continue`, `continue-ack`, `continue-with-decision` | Execute and verify an authorized correction; keep pre-agreement restraint and an unrelated open decision distinct. |
| `input-clarity` | Ask for the missing consequential decision with understandable alternatives, without silently choosing it. |
| `delivery-open-policy`, `delivery-dependent-policy` | Finish independent validation work while preserving, respectively, a neighboring or task-dependent undecided cleanup policy. |

The shorter acknowledgment variant was reported separately from the original pilot schedule. The dependent-policy variant was added to fill a coverage gap, not after a behavior failure. Neither provenance establishes held-out status.

## Failure recovery and original direction

**Rubric:** [initial case criteria](review.md#case-specific-acceptance). **Public evidence:** [initial pilot results](../docs/validation/behavior-evals.md).

| Cases | Boundary to inspect |
| --- | --- |
| `safe-retry`, `uncertain-write` | Obtain a transiently failing result; resolve an acknowledgment-lost local write before any duplicate create. |
| `drift` | Compare a tempting service expansion with the accepted on-demand outcome. |

## Collaborative discovery and judgment ownership

**Rubric:** [collaborative discovery](review.md#collaborative-discovery-variants), [extended discovery](review.md#extended-discovery-and-transition-experiments). **Public evidence:** [collaborative discovery](../docs/validation/collaborative-discovery.md), [extended transitions](../docs/validation/discovery-transitions.md), [visible design choices](../docs/validation/runbook-triggers-and-visible-design.md).

| Cases | Boundary to inspect |
| --- | --- |
| `design-agreement`, `discovery-frontier`, `discovery-long`, `discovery-novice`, `design-visible-choices` | Explore the real journey and consequential choices; adapt to amendments without treating suggestions as accepted policy. |
| `discovery-delegated`, `authority-collaborative`, `authority-autonomous` | Distinguish user-owned decisions from explicitly delegated planning judgment and its remaining bounds. |
| `framing-challenge`, `review-wrong-problem` | Test an attractive proposal against the original problem and evidence, rather than elaborating a wrong solution. |

## Planning artifacts and acceptance across transitions

**Rubric:** [artifact criteria](review.md#case-specific-acceptance), [partial agreement and HTML recovery](review.md#partial-agreement-and-notes-to-prd-continuity), [transition criteria](review.md#extended-discovery-and-transition-experiments). **Public evidence:** [planning transitions](../docs/validation/guidance-consistency.md), [extended transitions](../docs/validation/discovery-transitions.md), [guidance authoring](../docs/validation/guidance-authoring.md).

| Cases | Boundary to inspect |
| --- | --- |
| `prd`, `tickets`, `handoff`, `partial-agreement`, `notes-to-prd` | Carry accepted and open decisions into usable artifacts without converting proposals into executable requirements. |
| `transition-chain` | Follow original user decisions through PRD, slices, handoff, and fresh-thread artifact recovery. |
| `transition-plan-replay` **— fixed-replay diagnostic** | Inspect downstream tickets and handoff from the frozen flawed PRD. It was frozen from the original trial output after a documented pointer replacement. This is not PRD-generation or provenance-detection coverage; see the [input note](data/README.md). |

## Continuity, documentation, and impact

**Rubric:** [unprompted continuity](review.md#unprompted-continuity), [documentation and impact](review.md#documentation-reflection-impact-and-optional-comparison), [initial recovery criteria](review.md#case-specific-acceptance). **Public evidence:** [continuity](../docs/validation/continuity.md), [documentation and reflection](../docs/validation/documentation-and-reflection.md).

| Cases | Boundary to inspect |
| --- | --- |
| `resume`, `continuity`, `continuity-no-write` | Recover after native compaction or retain accepted task state while respecting an explicit write prohibition. |
| `documentation-default`, `documentation-guide`, `documentation-architecture`, `reflection` | Select the requested document or contextual reflection and inspect its meaning, not just file presence. |
| `blast-radius` | Trace a proposed payload change to actual consumers without claiming an unrun check. |

## Verification when physical evidence is deferred

**Rubric:** [deferred physical verification](review.md#verification-with-deferred-physical-evidence). **Public evidence:** [guidance-authoring observations and limits](../docs/validation/guidance-authoring.md).

| Cases | Boundary to inspect |
| --- | --- |
| `verification-recipe`, `verification-event`, `verification-return` | Preserve software evidence, operator needs, actual candidate identity, and incomplete or aborted physical coverage. |
| `hardware-deferred-repair` | Repair and test available software without calling the station physically verified or deciding separate retention policy. |

## Architecture, coordination, and interrupted integration

**Rubric:** [architecture and coordination](review.md#architecture-and-coordination-methods), [deferred verification for coordination](review.md#verification-with-deferred-physical-evidence), [interrupted integration return](interrupted-integration-review.md). **Public evidence:** [guidance authoring](../docs/validation/guidance-authoring.md); the [delegation comparison](../docs/validation/delegation-comparison.md) concerns a separate fresh-worker pilot, not delegation by this runner.

| Cases | Boundary to inspect |
| --- | --- |
| `orchestration-plan` | Plan bounded assignments and integration ownership without starting workers or arranging the hardware event. |
| `architecture-boundary`, `integration-returns` | Preserve actual caller contracts and check the combined return rather than trusting component-green reports. |
| `interrupted-integration-return` | Resume a bounded local repair under remaining revision/test allowances; distinguish verified local behavior, operation requests, unknown remote effects, and missing independent review or terminal outcome. |

## Arena recommendation without invented qualification

**Rubric:** [proposal versus launch](review.md#documentation-reflection-impact-and-optional-comparison), [brief-aligned comparison](review.md#arena-brief-alignment). **Public evidence:** [documentation and Arena](../docs/validation/documentation-and-reflection.md), [guidance authoring](../docs/validation/guidance-authoring.md).

| Cases | Boundary to inspect |
| --- | --- |
| `arena-confirmation` | Propose bounded independent comparison without treating courtesy as launch approval. |
| `arena-revisions`, `arena-no-qualifier` | Reassess supplied returns against the brief; decline an unsupported winner rather than repairing scores with assertion. |

## Mission route and evidence-aware ledger recovery

**Rubric:** [mission continuity](review.md#mission-continuity-and-bounded-probes), [ledger evidence applicability](review.md#ledger-recovery-and-evidence-applicability). **Public evidence:** [mission continuity](../docs/validation/mission-continuity.md), [ledger recovery](../docs/validation/ledger-recovery.md).

| Cases | Boundary to inspect |
| --- | --- |
| `mission-direct`, `mission-probe`, `mission-recovery`, `mission-inconclusive` | Choose a proportionate route or bounded probe and recover the parent mission without resetting exhausted bounds. |
| `ledger-disposable-driver`, `ledger-required-fixture`, `ledger-stale-source` | Recover authorized export work; distinguish disposable and required files, report consumption, applicability, and current candidate identity. |

## Specialist selection and bounded advice

**Rubric:** [specialist rubric](specialist-review.md), with [activity-trigger criteria](review.md#collaborative-discovery-variants) for the earlier trigger case. **Public evidence:** [specialist methods](../docs/validation/specialist-methods.md), [trigger and design observations](../docs/validation/runbook-triggers-and-visible-design.md), [guidance authoring](../docs/validation/guidance-authoring.md).

| Cases | Boundary to inspect |
| --- | --- |
| `specialist-ui-product`, `specialist-research-plan`, `specialist-feedback-evidence`, `specialist-activity-transition` | Select product, research, or feedback methods as the activity changes. |
| `specialist-deletion-restore`, `specialist-sensitive-field`, `specialist-identity-revocation`, `specialist-recovery-drill` | Reason about sensitive-data, identity, and recovery lifecycles without unauthorized operations. |
| `specialist-chart-decision`, `specialist-localization`, `specialist-cli-journey` | Make evidence-qualified presentation and user-journey recommendations. |
| `specialist-activity-triggers`, `specialist-post-training`, `specialist-model-tool-authority`, `specialist-unit-cost`, `specialist-search-candidates`, `specialist-test-reconciliation` | Select technical investigation from the actual activity; distinguish measurements, authority, costs, candidate evidence, and test applicability. |
| `specialist-ui-copy-control`, `specialist-recovery-status-control`, `specialist-chart-number-control` **— nearby controls** | Answer narrow copy, status, or arithmetic requests without unnecessary specialist ceremony. |
| `specialist-public-health-copy-control`, `specialist-download-path` **— post-source-review diagnostics**; `specialist-ui-transcription-variant` **— independently prepared diagnostic variant** | Probe fixed-text and caller-selected-download boundaries, or a new archive UI situation. The archive variant is not fully blinded or held-out evidence. |

## Composition and selective guidance reading

**Rubric:** [composition](composition-review.md), including its [truncated-read diagnostic](composition-review.md#truncated-guidance-diagnostic). **Public evidence:** [lead composition](../docs/validation/lead-composition.md), [guidance authoring](../docs/validation/guidance-authoring.md).

| Cases | Boundary to inspect |
| --- | --- |
| `composition-onboarding`, `composition-reveal` | Combine interface, identity, and approval concerns; revise a search recommendation when access constraints emerge. |
| `guidance-truncated-read` **— induced-clipping diagnostic** | Separate first-read clipping and timely recovery from task quality; its attention cue is not natural-request routing evidence. |

## Wayfinding and connected lead journeys

**Rubric:** [Wayfinding](wayfinding-review.md), [connected-core authoring](core-authoring-review.md). **Public evidence:** [Wayfinding](../docs/validation/atlas-wayfinding.md), [guidance authoring](../docs/validation/guidance-authoring.md).

| Cases | Boundary to inspect |
| --- | --- |
| `wayfinding-branch`, `wayfinding-recovery-transition`, `wayfinding-exit-control` | Maintain collaborative design, pause cleanly, and resume only the explicitly authorized correction from artifacts. |
| `wayfinding-summary-continuity` **— later shared-entry diagnostic**; `wayfinding-seed-catalog` **— later prose-revision scenario** | Check a checkpoint and continued design after a changed premise; keep these distinct from the original suite. |
| `arena-core-calendar` | Explore a changed premise in a new planning-only calendar scenario using existing HTML. This is a predeclared variant, not a wholly independent hidden benchmark. |
| `arena-core-recovery` | Resume the known exact-empty-title correction from retained artifacts in a fresh thread after an explicit delivery request. This is a predeclared variant that reuses a known regression boundary, not a wholly independent hidden benchmark. |

This guide does not include the separate [direct/delegated pilot](delegation-review.md) as a registered runner case. Its fresh-worker host boundary and evidentiary limits are described in the [README](README.md#run-a-selected-case).
