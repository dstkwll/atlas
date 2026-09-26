# Atlas Wayfinding observations

The added entry makes a deliberate brainstorming and grilling mode directly selectable, backed by the existing Atlas lead and library. Source review and small native trials support the intended interaction; they do not establish general reliability or equivalence to a preferred human conversation.

## Scope and conditions

The initial schedule comprised three candidate cases in each host and one current-main design-conversation baseline in each host: eight attempts, Astra at medium effort, with a 360-second limit per case. The [cases and rubric](../../evals/wayfinding-review.md) were prepared independently before reading candidate instructions. Follow-ups are fixed, volunteered constraints and decisions; they do not simulate every branch of an unscripted conversation.

The baseline is main `b20e9a6`, package 0.9.2. Candidate trials used the first 0.10.0 draft after two source-review corrections: ordinary summaries preserve the mode, and separately authorized discovery prototypes return to the map. Candidate selects `atlas-wayfinding`; baseline selects `atlas`. This compares entry plus shared guidance, not the isolated effect of either. Both conditions use the same synthetic fixtures and task prompts within each host.

Codex used native app-server skill input on CLI 0.153.4. Copilot used its native skill expansion and session runtime through the installed SDK 1.0.13; the actual runtime reported 1.0.83. It did not use the separately installed CLI or an IDE picker. Host instructions and tools differ, so results are not pooled as interchangeable samples. Each trial used a disposable project and temporary configuration home; existing authentication was reused, without installing or updating a host. No workplace data or live external action was part of the fixtures.

Copilot's first recovery attempt completed its planning turn, then encountered a driver lifecycle API error before the fresh-session turn. A single setup replacement continued that saved workspace in a new native session with the same copied guidance; it did not replay the first turn. Both attempts remain retained. This demonstrates a split recovery execution, not an uninterrupted run of the initial driver. Two earlier zero-inference setup preflights are separate from model behavior.

## Observed behavior

| Scenario | Codex | Copilot |
| --- | --- | --- |
| Three-turn design, changed goal and partial agreement | Challenged the booking premise, revised toward welcome and useful visitor outcomes, preserved unresolved priority/retention, and followed coordinator-only closure into the shared-laptop enforcement question | Same substantive coverage, with a changing map and concrete implications; only the approved planning record changed |
| Current-main design baseline | Also gave useful alternatives, followed the corrected goal, preserved scope and exposed the enforcement question | Also succeeded substantively; it preserved open policy and treated recommendations as proposals |
| Saved-decision recovery and explicit delivery transition | First turn changed only planning. Fresh thread read the decision and source, implemented only the exact-empty-title correction, and ran a regression failing before the fix and passing afterward | After the retained driver failure, a fresh-session continuation recovered the saved decision and performed the same bounded correction with actual failing-then-passing tests |
| Requested synthesis and pause | No questions or writes; accepted direction and uncertainty preserved. The final synthesis was 139 words, but 17 words of commentary made the full visible turn 156, exceeding the 150-word cap | Pause honored without questions or writes; 135 words across the visible response |

The recovery corrections preserved nonempty strings, including whitespace, and left undecided retention behavior unchanged. Actual test calls were inspected separately from the evaluator's later constructor probe. File-scope checks and record edits support the authority observations; green endpoint checks alone would not establish them.

The candidate made the frontier, dependencies and fog more explicit in its map, while the baselines already supported useful discovery. These samples do not demonstrate improved reasoning or routing reliability. The direct entry addresses the owner's accepted preference for deliberate mode selection.

## Review refinements and later diagnostic

Independent source review and an Opus 5.5 extra-high, context-only Copilot critique informed the implementation. The final source further narrows the description to sustained interactive sessions, states summary persistence in the canonical method itself, and clarifies establishing or reusing the approved continuity artifact. Existing shared guidance already covers interrupted-worker liveness and effects; no duplicate worker-control mechanism was added. A final independent source check found no remaining contradiction in those refinements.

One additional three-turn `wayfinding-summary-continuity` diagnostic per host used the final skill sources. Each selected ordinary `atlas`, requested Wayfinding by name, asked for a short checkpoint, then supplied a priority decision. Both kept the mode active, saved the new decision, superseded the contrary recommendation, followed the skills-availability consequence and left retention and visitor-experience uncertainty open. Only the existing planning record changed. The checkpoints stayed within 120 words: 111 in Codex and 107 in Copilot.

Both hosts also consulted the Wayfinding wrapper during that named request. These diagnostics therefore demonstrate named activation and continuity through a summary; they do not isolate the shared method from the wrapper. They were added after review, are not held-out cases, and do not retroactively make the initial schedule a test of every final instruction. Final description selectivity, creation of a record in a fresh project, and transitions while workers are in flight retain source-only coverage here.

## Checks and limits

The evaluator's 39 correctness tests passed. The new skill passed frontmatter validation; case identifiers, fixtures, entry paths, relative links, aligned 0.10.0 versions and the final diff were checked. These are packaging and evaluator checks, not conversational grades. Recorded cleanup confirms trial hosts stopped and temporary homes were removed; those observations are not a security-isolation guarantee.

Detailed attempts, source hashes, tool traces, per-turn change observations and independent reviews remain local maintainer evidence. Codex snapshots contain hashes; actual writes and saved decisions were inspected through tool records and retained artifacts. The reusable synthetic cases and review criteria are public; trial histories and host diagnostics are not installed with the product.

Not established: donor parity; generic implicit selection; long-session compaction; every exit or prototype transition; an unscripted human session reaching readiness; Copilot IDE or workplace-host behavior; other model families; or automatic installation and update behavior. No merge, release or installation of the candidate was part of this validation.

## Portable authoring and prose revision

The owner subsequently authorized shipping the writing craft as a portable Atlas method. The lead and specialist index route agent-facing authoring requests to one `writing-agent-guidance.md` reference; the maintainer document points to the same source. Guidance improvement remains the conditional diagnosis/evaluation method. This adds no public skill, external donor dependency or library-wide audit.

A fresh isolated agent exercise reported selecting the new reference and produced a release-note drafting skill from synthetic notes. Inspection confirmed the resulting artifact preserved shipped-versus-uncertain status, owner wording and decisions, proportional investigation, draft-only authority and file-reading portability, with a useful mixed-list example. This exercises authoring in a delegated context, not native Codex/Copilot automatic routing or execution of the generated skill.

A separate four-turn seed-catalog conversation was prepared before inspecting the prose revision and run once against the pre-edit and revised Wayfinding guidance in each native Codex and Copilot host, using Astra at medium effort. All four sessions revised dependencies after a changed premise, accepted a partial decision without resolving unrelated uncertainty, honored a short checkpoint without leaving Wayfinding, and resumed collaborative design without implementation. Edits stayed in the existing planning record. The successful pre-edit samples limit any improvement claim; these are small scripted checks on one model, not evidence of broad reliability. The tested candidate predates the final source-review clarification about evidence-established facts and meaningful findings; those later words have source-review coverage, not a fresh native trial. The new authoring route is not directly exercised by this scenario.


An Opus 5.5 extra-high source critique identified the narrower answer-only update trigger and a possible human-runbook audience ambiguity. The final source responds to answers or findings, separates established facts from accepted choices, and makes authoring triggers explicitly agent-facing. It also avoids duplicating the evaluation method and clarifies factual dependencies and host loading. The supplied critique packet was partly clipped; that review is not evidence for omitted passages. A separate full-source review of the final candidate found no concrete defect. The authoring exercise also predates these final wording clarifications.

The 39 evaluator correctness tests pass with the new reusable seed-catalog case registered. Skill format, relative links, unchanged mode transitions, distribution attribution and aligned package versions were checked. The broader library audit remains outside this revision.
