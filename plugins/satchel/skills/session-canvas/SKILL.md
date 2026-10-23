---
name: session-canvas
description: Discover, build and maintain a visual map of the current session with the user. Use for an evolving view of direction, understanding or work remaining; a one-off diagram needs no ongoing canvas.
---

# Session canvas

Help the user see where this session stands and where it may go. First discover what would help them orient, then build and maintain that view. Work in the existing conversation with its tools, permissions and assignment. The canvas represents work; it does not authorize tasks, bookings, publication or other actions depicted in it. No other skill is required.

## Discover before rendering

Read relevant session context first: the user's purpose, accepted decisions, constraints, work and evidence already available, unresolved questions, and the current direction. Reuse settled answers. Keep tentative ideas distinct from commitments. When context is sparse, help develop a useful working direction without requiring the user to arrive with a fully specified goal.

Offer a brief interpretation and a recommendation with meaningful alternatives. Ask about gaps that would change what the canvas helps the user see or decide. Follow answers into consequences; challenge a framing when it would hide an important dependency or uncertainty. Investigate accessible facts yourself. Avoid a fixed questionnaire, repeated approval questions, or making the user choose technical formats they have no reason to care about.

Useful questions depend on what remains unclear:

- **Purpose:** “Would it help most to compare possible directions, track the route to done, understand how things connect, or combine those?” Recommend from the session rather than always asking this list.
- **Detail:** “What should be visible at a glance, and what can wait until you inspect it?” Consider blockers and decisions the user needs to notice.
- **Interaction:** Offer steering through chat and, where the host supports it, direct interaction. Distinguish inspection from edits to shared content. Clarify what consequential edits mean before implementing them.
- **Upkeep:** Recommend a brief check after each completed user exchange; offer updates at meaningful milestones or on request when those better suit the user. Explain the actual host limits before promising automatic signals.

Resolve enough about the canvas's purpose, useful content, interaction and upkeep to choose a representation. The underlying project may still have alternatives, assumptions and unknowns; those can be the content. A brainstorming map need not invent tasks or a route to done.

Before the first render, give a short **text-only brief** covering the understanding above, the proposed view and any consequential limitations. Invite confirmation or correction and wait for the answer. Do not render a candidate design during discovery: it can anchor both participants prematurely. Existing explicit confirmation of that brief counts; do not ask again. Carry corrections into the brief without restarting settled discovery.

## Build the agreed view

Choose and combine only useful visual patterns after discovery. Read the relevant backing guidance before constructing that part of the view:

| User need | Guidance |
| --- | --- |
| Explore choices, assumptions and unanswered questions | [Exploration](references/exploration.md) |
| See work, dependencies, parallel opportunities and the route to done | [Progress](references/progress.md) |
| Understand relationships or reasons that affect the next decision | [Understanding](references/understanding.md) |

These are methods to combine, not required sections or a menu that limits the result. A combined view should distinguish an open choice from committed work. For example, comparing two venues while someone checks access rules does not make both venues planned bookings.

Use the actual host surface. In the **Copilot desktop app**, read [Copilot canvas](references/copilot.md) for its native builder and validation path. In **Codex or a host using saved artifacts**, read [Saved artifact](references/saved-artifact.md). Verify capabilities before selecting an interaction that relies on them. If the preferred surface is unavailable, explain the limitation and use an already acceptable alternative; obtain the user's choice when the fallback materially changes the agreed experience.

Save output in the session workspace or the user's chosen artifact home, never inside the installed skill. Keep one identifiable canvas for this conversation. Choose a readable overview, text labels as well as color, and inspectable supporting detail where useful. Verify the actual rendered result and an update when the host permits it. Saving valid source or receiving a successful tool response alone does not establish visible rendering.

## Maintain orientation through this session

Follow the agreed cadence. By default, the existing lead briefly compares the canvas with the conversation and work performed before completing each user exchange. This means the user message and the work/response it prompted, not every tool call or internal model turn. Use this same check when the user asks to refresh. Do not create a separate recurring reviewer, scheduler or stop hook to force extra turns.

Check whether direction, decisions, evidence, task status, dependencies, open questions or next steps changed. Update what changed and preserve the useful layout. When the purpose, major route or useful level of detail changes, reconsider the representation and retain a concise reason. Routine in-scope updates need no renewed brief approval; return consequential changes to the user's accepted intent to them. If the agent has wandered from the agreed goal, show the discrepancy and correct the work or seek the needed decision. Do not rewrite the goal to legitimize the detour.

Keep a visible **last-assessed point**, naming the conversation exchange or event and the scope checked. A no-change assessment counts; a file-write timestamp does not. The marker reports the last check, not guaranteed ongoing freshness. If a check or update was skipped or failed, retain the previous marker and explain the gap when known.

Distinguish **new activity not yet assessed** from **an assessed mismatch**, which needs a reason. An optional passive activity signal may be added only when its real event delivery, cutoff and reconnect behavior have been verified in this host. It performs bookkeeping, not semantic judgment or model work. Missing history means freshness is unknown. Without that verified signal, use the last-assessed marker alone; do not display a live “current” badge.

Scope upkeep to this conversation. On same-session recovery, read the saved canvas and relevant conversation/evidence, check that they belong together, and assess the gap before advancing the marker. Preserve files when the session ends. Automatic discovery, transfer and synchronization into another conversation are outside this method's promise.

Finish a render or update with a concise orientation: what changed, any important uncertainty or failed verification, and the next useful move. Continue the underlying authorized work where appropriate. Once created, the canvas stays an aid to that work; the user should not have to manage this skill's internal routing.
