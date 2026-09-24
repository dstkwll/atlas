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

The initial PR #38 candidate removed the mandatory closing paragraph. Historical reconstruction showed that this was an unsupported interpretation of the feedback: consistent orientation and authorized continuation were both intended. The candidate is superseded, not evidence of an accepted intent change. Its trials remain below for provenance.

Three matched native scenarios ran once per condition on Codex Desktop 0.153.4 with `gpt-5.6-sol`, low effort and a 120-second per-trial limit. Baseline was main `1c0e2d6`; candidate was the same source with this PR's continuation section. Raw traces, snapshots and setup failures remain in local maintainer evidence.

| Scenario | Baseline observation | Candidate observation |
| --- | --- | --- |
| Approved repair | Waited before approval, then edited and ran boundary assertions in the second turn | Same; recovered from a missing `python` command with `python3` and completed verification before returning |
| Completed assignment | Acknowledgment plus mandatory next-action paragraph | Brief acknowledgment with no follow-up work or closing ritual |
| Product decision | Plain options and recommendation, ending with a Next paragraph | Direct question, two practical alternatives and a short recommendation; no policy decision or implementation |

Both conditions completed all three scenarios. Action traces and resulting artifacts support the repair observation; the read-only cases produced no file changes. Baseline also succeeded at continuation and clear language, so this small comparison does not establish improved persistence or general clarity. The question prompt explicitly requested plain language; spontaneous clarity, longer tasks, explicit limits, access failures, pauses and other hosts were not exercised in this comparison.

Three earlier candidate attempts were rejected before model execution because `gpt-6-sol` was unavailable to the CLI account. One baseline setup attempt failed because an archive lacked Git metadata. These are retained setup failures, not behavior failures or passing trials.

An independent Copilot source review using Claude Sonnet 5/high found no blocking instruction defects. The lead verified its caution about preserving decisions/check results and restored those words in that candidate’s reporting sentence; the behavioral samples preceded this small reporting clarification. Its stale-link check also found the Copilot profile still pointing to the removed mandatory-close section; that pointer now names continuation and clear input requests. Native profile behavior was not rerun. The reviewer did not inspect runtime evidence. Its coverage questions remain explicit limits above. The evaluator's 39 correctness tests and diff checks passed; those checks do not establish behavioral reliability.


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
