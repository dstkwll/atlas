# Continuation and next-step orientation

## Intent being preserved

Atlas owns progress within the assignment and makes the path forward visible when returning to the user. These obligations were paired in [PR #10](https://github.com/dstkwll/atlas/pull/10). After guidance was still omitted following ordinary design decisions, [PR #18](https://github.com/dstkwll/atlas/pull/18) made it a standing requirement across conversational turns. The `Next:` label makes the guidance easy to find; it is not a reason to end a turn.

The intended experience is a capable conversational lead: users should neither restart authorized work after every step nor reconstruct what decision is needed from a status recap. Advisory completion remains a valid outcome. A recommendation for the broader goal does not authorize another assignment.

## Problem and correction in this PR

Recent feedback describes two failures: the lead recommends its own unblocked work and returns unnecessarily; when user judgment really is needed, the request can be vague or buried in jargon. Current main already says to continue authorized work. The feedback identifies an application problem; it does not establish that the closing label caused it.

The initial PR #38 proposal made closing guidance optional. That was a maintainer interpretation, not an accepted withdrawal of the standing requirement. This revision preserves it and clarifies the order of judgment:

1. Decide whether there is a real reason to return: completion of the assignment, a necessary decision or dependency, an explicit pause, or an applicable limit. Finish independent authorized work before returning.
2. At that return, give brief, visible orientation: what happens next, why, and who must act. If user input is needed, make it specific and answerable in plain language. The question may itself be the `Next:` paragraph.

Keep these instructions in the shared lead. The host profile points to them; no controller, new runtime, mandatory task record or second policy source is needed.

## Alternatives and tradeoffs

| Approach | Benefit | Cost or limitation |
| --- | --- | --- |
| Keep main unchanged and investigate a failing host trace | Avoids instruction growth and may locate a host/application cause | Leaves the reported return/input ambiguity unaddressed in the meantime |
| Preserve Next and clarify return conditions and responsibility | Addresses the current report while preserving consistent orientation | Adds judgment guidance, which may still be missed; short completed answers retain a small repetition cost |
| Make the closing optional | Allows more natural brevity after simple answers | Reintroduces the discretion that previously produced omitted guidance; no evidence shows removal improves continuation |

The selected correction is the middle approach. Brevity comes from a concise, contextual close and avoiding duplicate questions, rather than withdrawing orientation. Exact-output requests remain exceptions; pauses and completed work do not justify invented tasks.

## Journeys and evidence

Check ordinary design decisions followed by continued design; authorized repair followed by verification; a separate unresolved policy choice alongside independent work; a real human decision with understandable consequences; advisory completion; explicit pauses; and unavailable access or exhausted limits. Judge whether actions happen and the user can act on the question, not just whether a label appears.

The [validation record](../validation/turn-ending-guidance.md) distinguishes the superseded candidate, current samples and untested claims. Source consistency and synthetic examples do not establish reliable behavior in a workplace host or a long conversation.
