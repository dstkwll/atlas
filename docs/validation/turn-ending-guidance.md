# Turn-ending guidance checks

Atlas should close each conversational turn with a useful next action, needed decision, pause condition or completed disposition. A resolved decision releases work already authorized; it does not grant broader permission. Explicit output-only requests control the response format.

The [evaluation cases](../../evals/cases.json) and [review criteria](../../evals/review.md#turn-ending-guidance-across-intent) cover decisions, corrections, short questions, completion and pauses. Judge the meaning of the response and actual actions, not merely a closing label.

## Observations and limits

- A native Copilot conversation continued authorized design after a decision and supplied contextual next guidance across ordinary follow-ups.
- Short-question, correction and completion checks also produced useful closing guidance. Output-only requests returned the requested output, though that alone does not prove the skill's exception was applied.
- Some process-resumption checks omitted next guidance. Reliable restoration and adherence across restarted sessions are not established.
- The shared lead has interactive evidence; complete interactive validation of the current profile is still outstanding.

These observations support bounded behavior claims, not a guarantee across hosts, models or context recovery. Detailed trial records remain with maintainer evidence.
