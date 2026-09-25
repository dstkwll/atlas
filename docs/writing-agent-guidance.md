# Writing skills and runbooks

Use this reference when creating or revising Atlas guidance. Write for a capable agent making decisions in a real task. A useful instruction changes what it notices, chooses, does or checks. Its length follows from that job; there is no target word count or required document template.

## Give the method a clear job

Lead with the outcome and the situation that calls for this method. Make the first useful action easy to find. A skill description or a link from the lead is part of the instruction: it must say when to reach the material, not merely name an attractive capability. Distinct triggers should correspond to distinct cases, rather than a list of synonyms.

Choose a familiar concept when it gives the agent something precise to reason with. Define its recognition test beside it, then use the name consistently. A **blocked question** can already be stated, but needs another answer; **fog** is territory whose questions are not yet clear. Those definitions guide classification. A label such as “thoughtful discovery” supplies much less direction.

The term earns its place through that decision, not through a claim that a particular word reliably activates a model. Use ordinary language where no special concept is needed.

## Put decisions and their consequences together

Organize a procedure around the choices and feedback that change its next action. Keep a decision's trigger, action, relevant exception and reason together. Use a sequence when order matters; a reference of peer rules does not need to become a staged workflow.

For an interactive method, make the transfer of control clear: what the agent investigates, what the user decides, what waits for an answer, and how that answer changes the next question. For autonomous work, identify the evidence that changes the next action. Give a short reason when it helps the agent handle an unfamiliar case.

For example, “Explore the important dependencies” leaves several plausible behaviors. A more useful instruction is: “Ask questions whose prerequisites are settled. When an answer makes another question meaningful, bring it forward. Investigate accessible facts yourself. While a fact or decision is pending, continue questions that do not depend on it.” This describes a reusable operation without fixing a question count or inventing a controller.

Scope initiative to the assignment. A method may recommend an action without authorizing it. Put a consequential boundary beside the action it governs, using the existing authority contract rather than inventing another approval flow.

## Make success recognizable

Name the result that matters and the evidence that distinguishes it from merely completing an activity. A test that passes has not necessarily shown sensitivity to the bug. A saved design has not necessarily resolved its consequential choices. A short handoff has not necessarily preserved what the next agent needs.

Set the bar relative to the task. For a bounded code change, explicit affected cases may all need checking. For open-ended discovery, record what is settled, what could change the route, and why remaining questions can wait. Exhaustive language needs a defined set; an empty list of known questions is not proof that nothing remains undiscovered.

If a later action repeatedly tempts the agent to declare an earlier one complete, first clarify the earlier completion condition. Moving later instructions behind an ordinary file link does not remove them from a context that already loaded them. A separate agent or session is a different architectural choice, not a prose cleanup.

## Use examples to resolve ambiguity

Add a compact example where two reasonable readings would lead to different behavior. Show the consequential distinction, with enough context to understand it. An example should help the agent recognize a class of case; its incidental names, layout or tool choices do not become requirements.

| Vague direction | More operational direction |
| --- | --- |
| Produce meaningful alternatives | Compare choices that change the user's workflow; changing only labels or colors does not establish a different approach |
| Keep the map current | When the owner removes booking priority, save that decision and revisit any scheduling promise that depended on it |
| Verify the fix | Show that the regression detects the original failure, then passes with the correction; use an independent expected result |

Prefer a clear action over a collection of prohibitions. Retain explicit prohibitions where authority, data preservation or another real invariant requires them, and state the permitted route when useful. Negative wording is not inherently defective, and replacing it with upbeat but ambiguous language is not an improvement.

## Put guidance where it is used

Keep common operating instructions on the common path. Put substantial conditional detail behind a pointer naming the condition and target. Keep a concept's definition, rules and caveats together. A simple method may fit in one file; splitting is useful when it separates real branches or reusable responsibilities.

Review the full loaded path: entry point, shared lead, method and required references. A tiny wrapper can depend on substantial guidance. Moving the same required material to another file changes packaging, not the total information the agent needs.

Consider the human's burden too. Moving guidance out of the default context can make someone remember another command. A directly selectable skill earns that burden when it offers a useful deliberate choice; an internal method can stay reachable through the lead. Saving model context and making the interface easier to use are related but different goals.

Give each rule one authoritative home. Brief reminders can connect a local action to that rule without creating a second definition. Before deleting apparent duplication, check that the relevant entry paths actually reach the surviving source and that the wording carries no additional obligation. Avoid both competing copies and essential instructions hidden behind weak pointers.

Use the host's actual loading mechanism. An explicit file path can be appropriate where another harness has a native skill tool. Invocation flags, tool names, hidden descriptions and context isolation are host capabilities to verify, not portable properties of prose. A referenced skill or runbook is not automatically a separate worker.

## Save state for its next reader

Describe what an ongoing task must preserve, what changes it and how it is recovered. Reuse the project's approved artifact where it serves that purpose. Save current intent, decisions and their reasons, relevant uncertainty and evidence pointers; link existing detail instead of accumulating a transcript or a parallel ledger.

Choose the artifact for the decision it supports. A visual comparison helps someone choose a design; a compact record helps another session recover it. Neither a required diagram nor a mandatory file layout follows merely from wanting useful continuity.

## Revise against behavior

Before pruning, identify the behavior each important passage protects. Distinguish a repeated explanation, a useful local reminder, a non-obvious rationale and a rule already enforced by a verified tool. Preserve exceptions and operating constraints that still matter. Information easily recovered from current configuration may need only a pointer; undocumented reasons and expensive lookups can deserve prose.

Use source review to find unclear choices, scattered definitions and unnecessary instructions. Treat claims that a sentence is a no-op, a stronger adjective helps, or a rewrite improves all models as hypotheses until behavior supports them. Favor current, relevant, maintained examples; adoption counts help choose examples but do not establish causation. Wrappers, renamed skills and their underlying methods are not independent votes.

For a material behavior change, use [guidance improvement](../plugins/atlas/skills/atlas/references/guidance-improvement.md): retain the baseline and important obligations, check realistic outcomes and a nearby valid case, and inspect actual use and effects. Scale the check to the change; an ordinary explanatory edit need not launch model trials. A source-only writing review should say what it found without claiming measured improvement.

This reference complements the architect charter and contributor workflow. It is a writing lens, not a new execution sequence, scoring system or permission boundary.

## Source basis

Informed by Matt Pocock's MIT-licensed [writing-for-agents](https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/productivity/writing-for-agents/SKILL.md) and concrete examples in [grilling](https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/productivity/grilling/SKILL.md), [prototype](https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/engineering/prototype/SKILL.md), [TDD](https://github.com/mattpocock/skills/blob/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/engineering/tdd/SKILL.md) and related methods. Applicable [third-party notices](../plugins/atlas/skills/atlas/THIRD_PARTY_NOTICES.md) are retained. These sources inform the craft; Atlas's accepted behavior and host constraints determine its application.
