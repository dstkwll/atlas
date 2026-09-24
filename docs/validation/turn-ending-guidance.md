# Turn-ending guidance checks

Atlas should continue unblocked authorized work and return for a real reason. Requests for user input should state the question, why it matters and enough context to answer in plain language. Completed answers need no fixed next-step paragraph. A resolved decision releases work already authorized; it does not grant broader permission. Explicit output-only requests control the response format.

The [evaluation cases](../../evals/cases.json) and [review criteria](../../evals/review.md#turn-ending-guidance-across-intent) cover decisions, corrections, short questions, completion and pauses. Judge the meaning of the response and actual actions, not merely a closing label.

## Historical observations and limits

These observations predate the continuation correction. They tested closing guidance and do not establish that the new behavior is reliable.

- A native Copilot conversation continued authorized design after a decision and supplied contextual next guidance across ordinary follow-ups.
- Short-question, correction and completion checks also produced useful closing guidance. Output-only requests returned the requested output, though that alone does not prove the skill's exception was applied.
- Some process-resumption checks omitted next guidance. Reliable restoration and adherence across restarted sessions are not established.
- The shared lead has interactive evidence; complete interactive validation of the current profile is still outstanding.

These observations support bounded behavior claims, not a guarantee across hosts, models or context recovery. Detailed trial records remain with maintainer evidence.


## Continuation correction, 2026-09-24

User feedback supersedes the mandatory closing paragraph: recommending available, authorized work is not a sufficient reason to end a turn. The correction preserves advice-only scope, explicit pauses, approval requirements and resource limits, and asks for necessary input in plain language with a specific question, reason and practical context.

Three matched native scenarios ran once per condition on Codex Desktop 0.153.4 with `gpt-5.6-sol`, low effort and a 120-second per-trial limit. Baseline was main `1c0e2d6`; candidate was the same source with this PR's continuation section. Raw traces, snapshots and setup failures remain in local maintainer evidence.

| Scenario | Baseline observation | Candidate observation |
| --- | --- | --- |
| Approved repair | Waited before approval, then edited and ran boundary assertions in the second turn | Same; recovered from a missing `python` command with `python3` and completed verification before returning |
| Completed assignment | Acknowledgment plus mandatory next-action paragraph | Brief acknowledgment with no follow-up work or closing ritual |
| Product decision | Plain options and recommendation, ending with a Next paragraph | Direct question, two practical alternatives and a short recommendation; no policy decision or implementation |

Both conditions completed all three scenarios. Action traces and resulting artifacts support the repair observation; the read-only cases produced no file changes. Baseline also succeeded at continuation and clear language, so this small comparison does not establish improved persistence or general clarity. The question prompt explicitly requested plain language; spontaneous clarity, longer tasks, explicit limits, access failures, pauses and other hosts were not exercised in this comparison.

Three earlier candidate attempts were rejected before model execution because `gpt-6-sol` was unavailable to the CLI account. One baseline setup attempt failed because an archive lacked Git metadata. These are retained setup failures, not behavior failures or passing trials.

An independent Copilot source review using Claude Sonnet 5/high found no blocking instruction defects. The lead verified its caution about preserving decisions/check results and restored those words in the final reporting sentence; the behavioral samples preceded this small reporting clarification. Its stale-link check also found the Copilot profile still pointing to the removed mandatory-close section; that pointer now names continuation and clear input requests. Native profile behavior was not rerun. The reviewer did not inspect runtime evidence. Its coverage questions remain explicit limits above. The evaluator's 39 correctness tests and diff checks passed; those checks do not establish behavioral reliability.
