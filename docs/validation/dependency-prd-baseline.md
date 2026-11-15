# Dependency-aware PRD transfer and an unguided baseline

On November 14, 2026 (local time), four native trials compared Atlas-guided and unguided PRD authors on a synthetic support-digest task, then gave each actual document to a fresh unguided implementer. Both recipients implemented the ready summary correctly on the independent examples and preserved blocked delivery. This case showed no downstream advantage for Atlas. Both documents retained small fidelity caveats.

This follows [artifact transfer](artifact-transfer.md) and continues [issue #66](https://github.com/dstkwll/atlas/issues/66). The [case and review procedure](../../evals/dependency-review.md) are maintainer diagnostics. No installed guidance or package version changed.

## What the case distinguishes

Counting open tickets by exact team name is fully specified and ready. Sending a digest depends on an Operations lead decision about authorized recipients, followed by the Identity team's matching resolver contract. A draft suggests selecting the first owner and skipping teams with no owner, but neither policy is approved. A useful PRD must enable the independent summary and preserve those missing contributions without adopting the proposal.

The fixture is deliberately explicit and synthetic. It tests preservation and transfer of known uncertainty, not discovery of a hidden dependency or negotiation with real stakeholders. It contains no real directory or delivery service.

## Conditions and integrity

The declared four attempts all completed, with no replacements or artifact repairs. Both authors used Codex CLI 0.153.4, returned model `gpt-5.6-sol`, low effort and a 300-second limit. The case prompt, source stubs, brief, routing draft and local operating instructions matched across actual staged snapshots. The guided author additionally received Atlas's installed skills and explicit `atlas-to-documentation` activation. Captured commands read that entry, the lead, documentation/PRD references, existing-behavior guidance and discovery/design guidance. The unguided author had no installed skills.

Both recipients were fresh unguided native threads with the same model, effort, timeout and common implementation request. They received only the author's actual Markdown deliverable and unchanged `queue_summary.py`/`delivery.py`, plus local operating instructions. The original brief, routing draft, author conversation and independent checks were absent. The common request authorized work the artifact declared ready; it did not identify which feature was blocked.

The primary reverified every transferred file against producer completion and recipient initial snapshots. Captured recipient commands stayed in their own projects; none read omitted source documents or another workspace. This is an observed instruction boundary, not an adversarial read sandbox. All four captures reported no parse errors, and all native hosts stopped with temporary homes removed. Trial metadata retains source and staged-input hashes. The source baseline was merged #69 at `1f5fe68f9102491922044e42218a4396ed6b9d00` plus this PR's evaluation changes.

## Observed outcomes

| Observation | Unguided author and its recipient | Atlas-guided author and its recipient |
| --- | --- | --- |
| Ready-summary requirements | Preserved input, filtering, grouping, ordering, privacy and mutation rules | Same core requirements preserved |
| Unresolved delivery | Named Operations decision, then Identity contract; rejected first-owner/skip-unowned proposal | Same dependency and proposal boundaries preserved |
| Author source changes | Planning document only | Planning document only |
| Independent recipient checks | Five of five examples correct; inputs preserved | Five of five examples correct; inputs preserved |
| Blocked source and received document | Unchanged | Unchanged |
| Recipient's own tests | Six persistent tests passed | Six persistent tests passed |
| PRD size | 10,355 bytes; 1,522 whitespace-delimited words | 13,126 bytes; 1,902 whitespace-delimited words |
| Native elapsed time, author / recipient | 91.0 / 61.3 seconds | 96.2 / 54.2 seconds |

The implementations use the same basic counting-and-sorting algorithm; the guided-artifact recipient also added a docstring. The primary inspected production code and tests before running the independent checker in a separate Python process for each recipient. The five task-derived examples cover empty input, falsey closed values, exact case-sensitive order, grouping/filtering, whitespace-sensitive identities, private extras and input preservation. The file-boundary check and source/command review separately supported preservation of delivery and artifact scope. No routing implementation or external-service call appeared in the captured actions.

Timings are harness observations, not performance estimates: the author runs overlapped, as did parts of the recipient runs. Word count measures document size, not clarity, human effort or quality. This one pair does not estimate variance or establish a causal effect, superiority, equivalence across tasks or general reliability.

## Artifact fidelity beyond passing code

A fresh Codex reviewer received exact-byte copies labelled A/B without condition labels or trial access. Its content review found parity on ready-contract completeness, independent readiness, missing decisions and accountable contributions, preservation of the unapproved proposal, stated baseline and self-contained usefulness. The primary verified these findings against the actual documents and brief. Content judgments do not substitute for action evidence.

The same review identified caveats that remain in the evidence:

- **Guided PRD:** a blanket caching exclusion is broader than the brief's purity constraint. It also makes future failure/recovery requirements mandatory planning inputs beyond the stated recipient-policy and resolver dependency. Neither addition blocked the observed summary, but successful code does not make those additions accepted requirements.
- **Unguided PRD:** “Authorized next action” and “In scope now” describe implementation without explicitly restating that the current assignment is planning and implementation comes later. In a handoff these can describe the subsequent assignment; the primary records authority ambiguity, not an observed unauthorized action. The author only wrote planning output, and the fresh recipient received separate implementation authorization.
- The unguided document's complexity estimate is additional implementation guidance, explicitly separated from the contract. Both documents elaborate future delivery readiness; neither supplies an invented recipient-selection policy.

No trial document was rewritten to remove a caveat, and no additional native run was selected to obtain a preferred result.

## Evaluator review and checks

Before any native author ran, Opus 5.5/high source review found that case-insensitive sorting and busiest-team-first sorting both passed the initial examples. The primary reproduced both false positives, added a separating exact-order example and added both negative controls. A fresh Codex reviewer independently confirmed that the new example catches both defects and that the earlier vectors do not. The task requirement did not change, and the final checker, fixture, rubric and helper identities were frozen before author execution.

The Opus job was `0daf9a8e-9653-47b1-8095-c05e91dcc622`, with cross-family routing and no write grant. Its first dispatch failed before inference because a requested read path did not exist; the corrected dispatch was the only review inference job. Optional review suggestions clarified recipient settings and preserved the distinction between author-caused and recipient-caused failure. No broad sandbox or infrastructure was added.

Final local checks: **68 evaluator tests passed**; **113 registered cases** preflighted in both conditions. The fresh reviewer independently passed 13 focused dependency/CSV transfer tests and verified that the prior CSV consumer descriptor is unchanged. The two dynamic recipients are not registered cases. Primary pre-author semantic controls distinguished proper dependency gating, blocking all work, promoting the routing proposal and missing action capture; these are criterion-specific checks, not calibration of a general-purpose semantic judge.

## Exact output identities

| Output | SHA-256 |
| --- | --- |
| Unguided PRD | `3edfd7a8727d837721963c91ba2b1a03d83df55118a010bb6d9ef7f9a0c44c16` |
| Guided PRD | `03a91bfa09296b0273d03f9cfe2d8d157189558015d47445c80b310e158abd69` |
| Unguided-artifact recipient implementation | `48ae20b1e7212f12525ee89cc40dfa0bdc50c7d29e4f055806f4953186d80a06` |
| Guided-artifact recipient implementation | `6a689fe69f692bd0351bceddd5a87316a2b6439f9eb664e76220a733cf36fc5b` |
| Independent summary checker | `16c05d8cf753a4567435b151245166fb7efc87b66bd12d241b8630d970288465` |

The useful result is a reusable comparison that retains successful baseline behavior and document caveats. It does not justify adding a runbook or tightening Atlas from this single case. A later evaluation could use a real multi-file task where the dependency must be discovered from conflicting evidence, or a controlled follow-up that resolves it; either needs separately declared inputs and bounds. The broader initiative remains open.
