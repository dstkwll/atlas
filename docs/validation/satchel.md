# Satchel validation

These findings separate source review, local package discovery and model behavior. Small fictional trials do not establish reliable enforcement or improvement over an ordinary prompt. The [full historical report](https://github.com/dstkwll/atlas/blob/e3fd4bcc80b8062b05159379e5cf98bbcebea050/docs/validation/satchel.md) preserves every attempt, source identity, correction and qualification; [PR #51](https://github.com/dstkwll/atlas/pull/51) holds implementation history. The package provenance file records source credits; adapted skill folders retain their original licenses.

## Where each skill's evidence is recorded

Sections below keep the skill names in use when each trial ran.

| Skill | Evidence |
| --- | --- |
| `catch-me-up` | The `reorient` row in the findings table. The skill had that name until 0.6.0. |
| `claim-check` | The findings table and [Uncited claims and incomplete review coverage](#uncited-claims-and-incomplete-review-coverage). |
| `define-goal` | The findings table. |
| `did-we-agree-to-this` | [Agreement checks on existing drafts](#agreement-checks-on-existing-drafts). The skill was `agreement-check` in 0.5.0. |
| `session-canvas` | [Session Canvas validation](session-canvas.md). |
| `teach-me` | The findings table. |
| `to-eval` | [Evaluation authoring](evaluation-authoring.md). |
| `to-questionnaire` | The findings table. |
| `unslop` | The findings table and [Draft editing and reader context](#draft-editing-and-reader-context). |
| `wait-what` | The findings table. |
| `why` | The findings table. |
| `writing-for-agents` | The findings table. |

## Scope of the evidence

Three studies completed 54 actor calls on authenticated Copilot Claude Opus 5.5/xhigh: 32 for the original five skills, 16 for Reorient and define-goal, and six for Why and Unslop. These counts include baselines, teaching follow-ups and diagnostic rechecks, not independent successes. Raw requests were kept separate from grading expectations. Actors had supplied text only, with no tools, files or network. Teaching follow-ups replayed the previous transcript into fresh calls; they do not prove native continuity.

Initial cases were authored before their author read the implementations; the addition-case author knew the archived predecessors. Follow-up authors knew earlier material or results, so those cases are diagnostic rather than fully held out. Independent reviews used masked treatment labels and constructed valid/invalid controls. Source use could remain inferable, and later briefs emphasized known defect classes; this was neither perfect blinding nor independent discovery of every defect. Reviewers detected the seeded errors but missed some real defects; primary inspection retained those disagreements. One initial combined source review timed out; its partial observations are not counted as a completed review. No completed result was rerun to obtain a preferred outcome. Source review is not behavioral proof.

The reusable requests and rubrics remain public:

- [Original five skills and routing controls](../../evals/satchel-cases.json), with [follow-up cases](../../evals/satchel-heldout-cases.json).
- [Catch-up and goal definition](../../evals/satchel-additions-cases.json), with the [completed-task catch-up case](../../evals/satchel-additions-followup-case.json).
- [Decision history and prose editing](../../evals/satchel-writing-history-cases.json).

## Findings that matter for use and maintenance

| Skill | Observed behavior and remaining limits |
| --- | --- |
| `wait-what` | Both matched arms corrected wrong museum advice, without establishing added value. Another response asserted an unestablished application-restoration effect. Clearer prose did not consistently preserve evidence limits. |
| `writing-for-agents` | Initial and first-repair rewrites added a stricter privacy rule inside operative instructions before asking for confirmation; the ordinary-prompt baseline also invented authority. A later diagnostic preserved the unresolved clause and put interpretations outside it, although its completion check was less complete than its body. Other cases retained separate consent/release approvals and protected originals; a release case's temporary local-only treatment did not settle the open remote-release policy. Final source clarifications were reviewed, not exercised by another actor or downstream operational assistant. |
| `to-questionnaire` | Preserved recipient knowledge versus decision authority, settled facts, conditional staffing and unknown roles. Baselines were also useful. Drafts remained lengthy for the requested short or five-minute reply; response effort was not measured. |
| `claim-check` | Preserved important denominators and bounded test conclusions. One heading called attribution contradicted while the body correctly treated causality as unresolved. Both matched arms added labeled statistical approximations; these did not establish study assumptions or generalization. A follow-up withdrew an unsourced retention recollection but turned a retention requirement into a claim about actual practice. |
| `teach-me` | Explained baker percentages and SQL joins, used prediction/feedback and honored a later request to skip exercises. Responses could become verbose, and fixed follow-ups sometimes skipped the actor's questions. A correct answer or replayed exchange did not establish lasting learning. |
| `reorient` | Initial and first-repair responses added booking assignments, advice or spending-approval gates and remained verbose; the reviewer preferred the tighter ordinary-prompt baseline. A completed-task response unnecessarily replayed its checklist. Paused work stayed paused, though vendor wording was ambiguous. Two later diagnostics preserved the real choices, including all six in one case, without the added assignment/gate. Their reviewer had earlier source context. Subsequent preservation edits received source checks, not another actor run; dependable brevity and superiority to that baseline remain unproved. |
| `define-goal` | Portable and draft-only cases produced useful objectives without claiming activation; baselines also worked. Some wording demanded absent evidence or could forbid restating existing information. A creation response falsely said an unconfirmed goal did not exist. A conflict response initially offered an unsupported separate goal-backed thread; the repair removed that offer but still imposed restrictive stopping conditions. Final clarification received source checks only. No actual goal persistence, conflict handling or tool effects were exercised. |
| `why` | Correctly distinguished an obsolete global hosting limit from the retained per-customer constraint and rejected a newer unaccepted proposal. It also promoted configured capability into observed operation and mislabeled a superseding decision. Both seed-swap arms expanded one organizer's uncertainty to “nobody”; the candidate generalized one session's turnout and absence from supplied records into absence of a recorded reason. Both were long for the request. These are partial results, not an improvement claim. |
| `unslop` | Both newsletter arms preserved numbers, periods, attribution, incomplete measurements, the untested explanation, quotation and conditional plans. The instruction rewrite preserved exact labels, separate message authorization, the narrow waiver and original-note protection. A fresh source review found no required repairs after two wording fixes. The successful ordinary-prompt baseline limits added-value claims; rewritten instructions were not subsequently executed. |

Catalog-only controls selected explanation repair and teaching appropriately and answered arithmetic and an ordinary invitation directly. They do not prove native automatic routing. Successful rechecks do not replace earlier failures. Historical source hashes and the precise bytes tested remain in the linked report; later description and attribution edits do not turn those trials into tests of the current package.

## Description and documentation cleanup

Five descriptions were shortened by 545 characters in total. Two fresh catalog-only calls on Claude Opus 5.5/xhigh selected the expected skill or no skill for all twelve requests, both before and after the edits. These editor-authored diagnostics were not held out and mostly exercised straightforward requests. They support unchanged selection on those examples, not improved routing or coverage of every boundary.

A fresh review compared the proposed cleanup with the original notices, adaptation record and validation report. It identified two lost baseline comparisons and omitted discovery changes in two credits; those details were restored and checked against the original sources. Primary inspection of the original actor prompt also placed the retention-recollection finding under claim-check. Historical package identity was independently recomputed. Scope and proportionality remain in the unchanged Atlas body. The review had no file access and did not assess the later native checks; final corrections received primary diff verification.

The temporary idea/adaptation records and the original-synthesis notice were removed. A single package-level `PROVENANCE.md` holds the source credits and modification details. All eight original licenses stay with their skill folders. The credits were briefly moved into `SKILL.md`; this added irrelevant loaded text and was corrected. Only define-goal keeps the short in-file statement “Modified for Satchel.” Skill procedures, invocation settings and supporting resources were preserved. The complete earlier report remains available through the historical link above.

## Package discovery

The intermediate 21-file cleanup candidate passed nine skill validators, eight exact upstream-license comparisons, 23 local reference/anchor checks and complete-folder copy comparisons. On macOS arm64, fourteen offline Copilot CLI 1.0.91 commands with fresh temporary configuration/cache registered a local marketplace, installed Satchel, discovered nine skills, co-installed Atlas and discovered nine plus eight skills, and discovered each of the nine Satchel folders in isolation. Listed descriptions matched their source metadata. Two builtins were counted separately. All commands exited successfully with empty stderr; source bytes were unchanged. The repository's 39 evaluator unit tests passed separately and test infrastructure rather than skill judgment.

After attribution moved to the package provenance file, the final 22-file package received nine skill validators, local-reference checks, exact credit/license preservation checks and complete-folder copy checks. Skill descriptions and procedures remained unchanged. This relocation received primary diff review; native discovery and behavioral trials were not repeated. Earlier five-, seven- and nine-skill checks, their package identities and the Toolbox-to-Satchel rename remain in the historical report.

Local registration and discovery do not establish Git-backed marketplace transfer, Codex or Claude Code invocation, useful model selection, policy enforcement or external effects. User installations and settings were untouched.

## Draft editing and reader context

Satchel 0.2.0 adds own-draft polishing, broader contrast examples, private-label clarification and a cold-read reference check to Unslop. Frequency, conditions, voice and searchable identifiers remain protected; a fresh reader is optional. A primary review refined a Claude Opus 5.5/high proposal. A separate source reviewer found no concrete defects in the resulting skill and package changes.

The [writing-quality cases](../../evals/unslop-writing-quality-cases.json) compare main `034cbe5` with the candidate skill (SHA-256 `2226e2db2545fd182249fbaa31707be6b5211189da4a62ac29d15a473c0245ed`). Six fresh, text-only Claude Opus 5.5/high calls completed: four content calls and two catalog-selection calls, paired between versions. Each content arm bundled eight unrelated tasks and ran the missing-context task separately to prevent borrowing definitions from its supplied-context counterpart. Bundled outcomes are not independent trials. An independent case author prepared eight content cases and four selection controls without reading the skill; the primary editor added the known-fact/voice-hedge case before any actor run. Grading expectations were withheld from actors. No completed call was rerun or candidate wording changed in response to these outcomes.

- Both versions preserved meaningful contrasts, exact identifiers, retry conditions and limits, genuine uncertainty, writer voice and expert terminology on the corresponding cases. Both left the already-clear newsletter unchanged and resolved supported archival references while flagging missing dates and limits. Both PR rewrites added some unnecessary editorial detail.
- In the missing-context case, both acknowledged gaps without inventing definitions. The candidate did not explicitly flag the unexplained “restart gap” itself; the baseline did. This is a retained candidate omission, not a passing claim for complete reference coverage.
- The candidate catalog selected Unslop as a final pass on a newly drafted PR description; the baseline declined because it treated the request as new drafting. Both selected explicit short-prose cleanup and declined arithmetic and code-only controls. These observations concern stated eligibility, not actual native invocation.

A fresh reviewer graded the paired outputs with version labels hidden and their order varied per case. It independently identified the same omission and brevity limitations, rejected a seeded invalid retry rewrite and accepted a valid alternative. The primary lead checked those findings against the inputs. Successful baselines and one run per prompt group limit improvement claims; these fictional cases do not establish dependable editing quality or cross-host routing.

The skill validator, JSON/version checks, preserved-license comparison, no-em-dash check and all 39 evaluator unit tests passed. Copilot CLI 1.0.91, launched with a fresh temporary configuration and local plugin path, discovered all nine Satchel skills and the exact revised Unslop description. Atlas package bytes and its version were unchanged. This discovery check did not run native model selection or the optional fresh-reader delegation path, and user installations were not updated.

## Uncited claims and incomplete review coverage

Satchel 0.2.1 makes two existing expectations explicit in claim-check: include material uncited claims within the requested scope, and identify scoped claims left unchecked with reasons. The evidence boundary, four conclusion categories and proportional reporting remain. A fresh source reviewer found no actionable defect in the two changed passages or Satchel-only version alignment.

The [four synthetic diagnostic cases](../../evals/satchel-claim-coverage-cases.json) were prepared by an independent worker without reading either skill version. The lead requested that the fourth case distinguish an interrupted in-scope review from an excluded topic before actor execution. Grading expectations were withheld from actors. Two fresh authenticated Copilot GPT-6 Sol / medium calls each received all four cases, one using main `e9a5e5a` and one using the candidate skill (SHA-256 `5ad1f1982d5dc61a3f49138d3fd987d149da5ed4d31e42ebbf6d908f4c67aaf4`). These are two bundled calls, not eight independent trials. No completed call was rerun and the skill was not tuned to the outcomes.

| Case and expected boundary | Observed in both versions |
| --- | --- |
| Launch note: verify a cited 192/200 pilot count and examine an uncited all-plans 24/7 support claim. | Supported the pilot count; contradicted the all-plans statement using the plan guide and limited the correction to the guide's effective date. |
| Inaccessible analytics: leave an asserted 3.5% churn rate unresolved rather than false. | Preserved the access limit and unresolved rate; did not claim to retrieve the report. |
| Supported return-policy answer: preserve unopened condition, 30-day delivery window and original payment method. | Accepted the answer without inventing a policy exception. Both added an unnecessary caveat about the check's limits. |
| Interrupted review: report a checked migration count and an unchecked resolution-time claim, including why work stopped. | Kept the pending claim and incomplete scope visible without continuing the audit. Both omitted the supplied production-incident interruption reason. |

The missing reason is a retained diagnostic miss, not a passing claim for complete reason reporting. Both calls used a repeated findings/evidence/uncertainty/verification format and were longer than the positive control needed. These supplied-text calls through the supervisor do not isolate native brevity or skill selection. Successful baseline behavior and one call per condition establish no causal improvement; the change clarifies the contract rather than demonstrating reliable adherence. The cases do not test real retrieval, contested evidence, long-document coverage or cross-model performance.

A fresh independent grader received the task evidence, fixed rubric and outputs with condition labels hidden and order varied by case. It confirmed no material factual distinction, identified the shared interruption-reason omission as a minor completeness miss, and treated the returns caveats as excess wording rather than invented restrictions. It rejected an invalid calibration response that called inaccessible churn evidence false and accepted a concise complete board-status alternative. The lead checked these findings against the supplied records.

The skill validator, JSON/version checks, unchanged Atlas package check and all 39 evaluator unit tests passed. The unit tests concern evaluator infrastructure, not claim-check judgment. User installations were not updated.

## Agreement checks on existing drafts

Satchel 0.5.0 adds a standalone check of a draft against the applicable decisions. Earlier ordinary reviews and a short comparison prompt had already found substantive issues in the same two historical cases. These runs tested the packaged skill through explicit native selection.

Two fresh Codex CLI 0.153.4 sessions used an initial candidate with `gpt-5.6-sol` at medium effort. The handoff review noticed a delivery safeguard but missed an obligation in the referenced protocol. The profile review distinguished approval of an earlier document from approval of the draft. We revised the skill to start from each governing source and compare like passages before attributing a change to an edit.

Three fresh sessions then used the final skill (SHA-256 `24bca493ea77a21bbe7d88df582d105669867a7824f95ab8d91c7618f6fc34a9`) with the same model and effort. Tool records show each session read the staged skill and case materials. Each returned a review with the workspace unchanged.

| Case | Observed result |
| --- | --- |
| Edited handoff, original, protocol and dispatch record | Found an evidence-retention obligation implicit in both drafts. Recognized the separate dispatch safeguard but still described its absence as a regression. Missed a narrowed prohibition in the edit. |
| Professional profile, owner conversation and decision records | Kept approval of one document separate from approval of the other. Flagged where the draft could imply broader independent adoption than the records established. Missed an unconfirmed causal link. |
| Independently written public notice with a later accepted time change | Accepted the notice as written, including the changed time and omission of internal assignments. Added an unnecessary conditional comment about printing. |

The historical cases were revisited after the first run informed the revision. These results document specific catches and misses. They do not establish consistent coverage, improvement over an ordinary prompt, automatic selection or behavior in other hosts.

## Package corrections and a structural test

Satchel 0.6.1 corrects four passages and adds package checks to the evaluator test run.

| Change | Reason |
| --- | --- |
| The `to-eval` description now opens “Design an evaluation case or plan”. | It shared its first 14 words with `atlas-to-eval`, so a host with both packages listed two nearly identical entries. |
| `session-canvas` says “the same assistant” where it said “the existing lead”. | “Lead” is Atlas's term, and the skill ships without Atlas. |
| `wait-what` asks for short sentences, consistent terms and a project glossary if one exists. | The earlier paragraph relied on ASD-STE100, “ubiquitous language” and `GLOSSARY.md`/`GLOSSARY-MAP.md` files that few projects have. |
| `did-we-agree-to-this` says to check delivery instructions where they live and not to count them as missing from the draft. | “Track separate delivery instructions in their own right” did not say what to do. The owner confirmed this reading. It matches the 0.5.0 handoff case, where the review described a separate dispatch safeguard's absence as a regression. |

`PROVENANCE.md` gains the missing `claim-check` entry, the README gains the plugin update commands, and this page gains the index above. No actor ran the four edited passages, so their effect on behavior is unobserved. A fresh Copilot GPT-6.1 Sol / high source review judged that each edited passage keeps its intended meaning. It also found that the new test accepted unclosed frontmatter, rejected a quoted name and was described as checking more than it did. The lead confirmed each point in the code, fixed the first two and narrowed the description below.

`evals/test_satchel_package.py` checks that each skill folder has closed frontmatter with a matching name and a description, a license and a README link, that `PROVENANCE.md` names each skill, that relative link targets exist, and that the manifest and marketplace versions match. The test failed on each seeded defect and passed once it was removed: version drift, a name that differs from its folder, unclosed frontmatter, a broken README link, a missing provenance name and a missing license. The checks read structure only: they do not judge skill prose, confirm that a provenance entry is complete or follow link anchors. All 83 evaluator tests passed.

Copilot CLI 1.0.114, started with a fresh temporary home and `--plugin-dir`, listed all 12 Satchel skills with the revised `to-eval` description. With Atlas's folder added, it listed those 12 beside Atlas's nine, and the two evaluation-design descriptions no longer open with the same words. This did not run model selection, a marketplace install, or Codex or Claude Code discovery. User installations were not updated.

## Host-specific detail behind references

Satchel 0.6.2 moves two passages out of their skill entries into bundled reference files.

- `define-goal`: the `get_goal`/`create_goal` protocol and the native-goal quality bar now sit in `references/native-goal-tools.md`. The entry points to it when the user asked to save a goal and the host has goal tools. The entry keeps the draft-only rule and the ban on creating a goal for an ordinary task. The workflow also no longer names Codex's `$define-goal` syntax.
- `to-eval`: the rules for partial captures, absent deliverables and paired controls now sit in `references/captured-evidence.md`. The entry keeps the core rule in one sentence and points to the reference.

The moved text is verbatim. No actor has run either skill since the move, so whether an agent reads each reference when its condition applies is unobserved. The registered `satchel-calibration-evidence` case exercises the moved `to-eval` rules and was not rerun. All 83 evaluator tests passed, including the relative-link check on both new files.
