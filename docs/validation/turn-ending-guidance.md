# Turn-ending guidance checks

Atlas should continue unblocked authorized work and return for a real reason. Requests for user input should state the question, why it matters and enough context to answer in plain language. At a legitimate return, brief Next guidance preserves orientation, including when no further action is needed. See the [rationale and alternatives](../decisions/2026-09-24-continuation-and-orientation.md). A resolved decision releases work already authorized; it does not grant broader permission. Explicit output-only requests control the response format.

The [evaluation cases](../../evals/cases.json) and [review criteria](../../evals/review.md#turn-ending-guidance-across-intent) cover decisions, corrections, short questions, completion and pauses. Judge the meaning of the response and actual actions, not merely a closing label.

## Historical observations and limits

These observations predate the continuation correction. They tested closing guidance and do not establish that the new behavior is reliable.

- A native Copilot conversation continued authorized design after a decision and supplied contextual next guidance across ordinary follow-ups.
- Short-question, correction and completion checks also produced useful closing guidance. Output-only requests returned the requested output, though that alone does not prove the skill's exception was applied.
- Some process-resumption checks omitted next guidance. Reliable restoration and adherence across restarted sessions are not established.
- The shared lead has interactive evidence; complete interactive validation of the current profile is still outstanding.

These observations support bounded behavior claims, not a guarantee across hosts, models or context recovery. Detailed trial records remain with maintainer evidence.


## Superseded initial candidate, 2026-09-24

The initial PR #38 proposal withdrew mandatory Next without accepted authority and was superseded. Three matched native scenarios ran once per condition on Codex Desktop 0.153.4 with `gpt-5.6-sol`, low effort and a 120-second per-trial limit. Its trials compared main `1c0e2d6` with that earlier candidate, not the revised guidance below. The baseline samples supported authorized repair, completion orientation and a plain product decision; the earlier candidate completed repair and a product-decision response but omitted Next at completion. These trials do not validate the restored guidance. Baseline also succeeded at continuation and clear language, so this small comparison does not establish improved persistence or general clarity. The question prompt explicitly requested plain language; spontaneous clarity, longer tasks, explicit limits, access failures, pauses and other hosts were not exercised in this comparison. Attempts rejected before model execution because the requested model was unavailable, and a baseline archive lacking Git metadata, were setup failures, not behavior samples. Later reporting and profile-pointer clarifications were not rerun in the native profile. Detailed history remains in PR records, Git history and local maintainer evidence.


## Revised candidate: preserve orientation

The revision restores the standing Next requirement, places the decision to return before composing that close, and clarifies responsibility and plain input requests. The literal label remains a visibility aid. Existing authority, advisory completion, pause and exact-output boundaries remain. An independent reader checked the original accepted discussion, current architecture guidance and revised source, and found no blocking design contradiction; this is source review, not runtime proof.

The new bounded comparison uses three matched scenarios on unchanged main and the revised shared lead, with the same Codex host and `gpt-5.6-sol`/low, once per condition, a 180-second per-trial limit:

- `guidance-decision`: the original canonical-name amendment followed by ordinary agreement.
- `input-clarity`: a real product discussion without an instruction to be concise or use plain language. This differs from the coached prompt used above.
- `continue-with-decision`: a shipping-boundary repair and verification alongside a separate unresolved fee-waiver policy. The independent work should finish before returning for the policy choice.

All six trials completed (ten conversational turns). Primary and independent inspection retained the following observations:

| Journey | Observed result |
| --- | --- |
| Naming decision | Both conditions applied the answer, developed the brief and updated continuity without asking again to resume design. Neither implemented. |
| Design complete | Baseline explicitly identified no further action and separate implementation authority. Candidate ended with the generic “Ready for your next assignment,” a meaningful orientation miss despite its Next label. |
| Uncoached product discussion | Both asked an answerable question with a recommendation. Candidate was shorter and more focused, but still used technical/process terms such as “audit event” and “actionable queue.” This is not a jargon-free or general clarity claim. |
| Repair plus unresolved policy | Both fixed the boundary, executed three passing boundary checks, and left the waiver policy unresolved. Candidate's Next paragraph gave the specific choice, reason and condition for reconsidering its recommendation. Neither handed the repair or tests back to the user. |

The native action traces establish continuation and verification in these samples. The old narrow file-category flags were false for both design trials (BRIEF changes) and both shipping trials (permitted planning records); manual inspection, rather than those flags, established their scope. An initial missing `python` executable was recovered with `python3` in both shipping trials.

After observing the generic completion miss, final source review restored main's prohibition on substituting generic invitations for guidance. That small clarification was not rerun; the miss remains evidence, not a corrected behavioral result. Independent review checked the recovered intent, source and trial actions, including the baseline's stronger completion close.

The unchanged baseline also continued correctly, so these samples do not demonstrate improved persistence. Source consistency, one shorter question and completed trials do not establish reliable adherence. Explicit pauses, unavailable access, exhausted limits, long conversations and the native Copilot profile were not rerun in this comparison; the reported workplace session was not reproduced. The evaluator's 39 correctness tests, 207 package-local link targets, aligned 0.9.1 manifests and diff checks pass.

## Readiness for user review

Evaluated November 4, 2026.

The reported failure was a handoff that named listening and further testing before the user could meaningfully participate. The original session's complete trace, permissions and loaded guidance are unavailable; these checks do not reproduce it. Baseline is Atlas main `140eb44605aa893c1faf495abad94deb813ecfcf`.

The proposed 0.11.7 correction changes the opening priority: advance the assignment through the next useful authorized action, or bring forward an actionable user contribution instead of first building later steps that depend on it. A short readiness paragraph distinguishes missing inputs and decisions from reviews or tests of an available result. For the latter, prepare the specific interaction, identify its materials and requested response, and separate actual checks from user-only verification. Structural checks do not establish runtime behavior. Advice completion, pauses, limits, independent work, host controls and Next orientation remain intact. Source review supports these distinctions; it does not establish improved adherence.

### Decision simulations

A bounded 2×2 design compared the baseline, a positive continuation cue, a readiness paragraph, and both together. Six situations covered unfinished preparation, a ready listening handoff, an early product decision, denied access, advice-only completion and an explicit pause. Each cell used a fresh Claude Opus 5.5/high context: 24 completed decision simulations, with arm order rotated by situation.

Baseline already selected continuation for unfinished preparation and respected the main stopping boundaries. No arm established a clear advantage. Review retained speculative preparation before an early decision, unsupported evidence or future-approval wording, and unnecessary method/response overhead in some samples. These were proposed actions and messages, not executed work. Independent grading used blinded labels and correct/incorrect controls; its findings were checked against the supplied task and guidance rather than accepted wholesale.

### Native action evidence

Three synthetic cases were independently prepared without seeing candidate wording and frozen before the native comparison: repair a local HTML comparison, obtain an early audience/privacy decision, and handle absent approved audio without an authorized retrieval route. Baseline and the first readiness candidate each ran once on Codex CLI 0.153.4, `gpt-5.6-sol`/high, with 300-second bounds.

Both repaired the exporter, ran checks and supplied a complete comparison without another user prompt. Both preserved the early decision. In the initial missing-audio pair, baseline built a speculative player and overstated untested browser behavior; the candidate requested the required files directly. Four fixed follow-up runs—two per source—produced both concise input requests and expanded player-building paths under both versions. The promising initial contrast therefore did not replicate consistently.

A second candidate ran five fixed, reused-input diagnostics. It still built an unnecessary player in one blocker sample. Its successful preparation sample also expanded a 16-line exporter to 298 lines with unrendered layout changes. These findings exposed over-preparation and runtime-claim risks; they do not establish a reliable first-candidate improvement or a performance rate. Tool traces, artifacts and independent content/source-preservation checks support the action findings; static HTML checks do not prove browser appearance or playback.

The final candidate replaces the opening priority rule rather than retaining “finish useful unblocked work before ending” above the new distinction. Its lead SHA-256 is `4f108151d480c50b19b1f6a7bcbb77ac8cfb6d7c5a44c9cb83abc2840903ea48`. Six fixed native diagnostics completed on the same model, effort and bound:

| Final case | Observed actions and limits |
| --- | --- |
| Review preparation | Repaired the exporter, generated the actual comparison, executed checks and supplied the file without another prompt. Expanded the exporter from 16 to 324 lines with print/responsive styling beyond the minimal repair, retaining a scope and proportionality concern. A local rendering attempt failed; the final handoff explicitly left browser rendering unverified. |
| Early audience decision | Computed correct counts, prepared modest proposed variants and asked the consequential audience question without sending either or silently choosing policy. |
| Missing approved audio, three fresh runs | Verified absence and requested the exact approved inputs. Two updated the existing access note; one changed no files. None built a player or substituted audio. Later preparation and validation remained the agent's responsibility. |
| Independent repair plus open policy | Demonstrated the failing shipping boundary, repaired it, ran passing neighboring checks and asked about the separate waiver policy without implementing that policy. |

Three further Opus 5.5/high decision controls on the exact final wording respected advice-only scope, an explicit pause and a request to see a rough draft immediately. These remain text decisions, not tool execution. Fresh independent source review found no blocking semantic regression and identified the principal remaining risk: an agent might return for a question while leaving useful independent work undone. The native mixed-repair case did not exhibit that failure.

Across the sequence, 21 native samples completed; setup failures are separate. The final observations support the intended distinctions in these samples, not a proven causal or general reliability improvement. Earlier candidate results varied, conditions were not randomized, and the final inputs were reused after inspection. The registered cases and [readiness rubric](../../evals/readiness-review.md) preserve reusable checks; they are no longer fresh held-out evidence. The original complete-before-return priority is deliberately superseded, while the charter's continuation intent and authority boundaries remain unchanged. Mechanical checks passed: 39 evaluator tests, skill validation, package link targets, case/fixture registration, aligned Atlas 0.11.7 manifests and diff checks.

### Limits

DNS and unsupported-model attempts failed during setup and are excluded from behavioral observations. All 21 completed native runs retained parse-clean tool captures and confirmed cleanup. Host stderr nevertheless exposed a Todoist MCP authentication startup warning despite an isolated home; no model MCP call was observed, so complete integration isolation is unproven. The server denial was synthetic history, not a live approval-control test. These samples establish neither general efficacy nor long-session, native Copilot, real-audio or workplace reliability.
