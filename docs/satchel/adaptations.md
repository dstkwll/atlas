# Satchel sources, adaptations and candidate choices

Satchel 0.1.0 is a collection of independently usable skills. The owner authorized a broader toolkit on October 18, 2026, with particular care for Matt Pocock's choice of language and with ideas and implementations reviewed through Copilot Claude Opus 5.5 at xhigh. The owner selected Satchel as its name; it was originally developed under the provisional name Toolbox through commit `8e4bea37fd6d5a7eb97c9b4954601ece674da0d8`. [Issue #50](https://github.com/dstkwll/atlas/issues/50) owns implementation progress; this document owns the source and adaptation account.

The skills do not activate Atlas, invoke one another, or establish a common workflow. Copying one complete skill folder is sufficient. Existing Atlas guidance remains unchanged. In particular, Satchel's writing skill is a deliberate adaptation of Matt's current source, not an extraction or replacement of Atlas's authoring method. A future consolidation is only an [Atlas idea](atlas-ideas.md).

## Sources and attribution

All Matt Pocock sources are pinned to [`49dd158d1076134a641b33efb035946536778336`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336), dated October 9, 2026. Each adapted skill includes the unchanged upstream [MIT license](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/LICENSE), copyright 2026 Matt Pocock, and a source notice that travels with a standalone copy.

| Satchel skill | Source | Relationship |
| --- | --- | --- |
| `wait-what` | [Matt's wait-what](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/wait-what/SKILL.md) | Small explanation-repair adaptation |
| `writing-for-agents` | [Matt's writing-for-agents](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/writing-for-agents/SKILL.md) and [SKILL-MECHANICS.md](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/writing-for-agents/SKILL-MECHANICS.md) | Original files copied first, then selectively revised |
| `to-questionnaire` | [Matt's to-questionnaire](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/to-questionnaire/SKILL.md) | Retains recipient/gap method; broadens output and incomplete-context handling |
| `teach-me` | [Matt's teach](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/productivity/teach/SKILL.md), read with its three linked format files | Substantial scope adaptation: focused conversational teaching |
| `claim-check` | Original Satchel synthesis | No third-party skill text copied; rationale below |

[Anthropic's skill-authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), retrieved October 18, 2026, informs discovery descriptions, direct reference paths, navigation for long references, representative evaluation and model/host limits. Those ideas are expressed in new prose; no passages are copied. It is a supplementary authoring source, not a runtime dependency. The supplied [Reddit post](https://www.reddit.com/r/claudeskills/comments/1x55vua/anthropics_official_agent_skills_guide_6_insights/) summarizes that guide; it contributes no additional copied text or independent evaluation evidence. Its reference to the first “100 chars” should not replace the primary guide's discussion of partial line reads.

The existing [Atlas authoring method](../../plugins/atlas/skills/atlas/references/writing-agent-guidance.md) informed preservation review, especially source authority, exceptions and evidence limits. Its instructions are not required to run Satchel. Detailed research packets and review traces remain maintainer evidence; the public [validation summary](../validation/satchel.md) preserves material findings and limits.

## Shared adaptation choices

- **Language carries decisions.** Retain useful source terms and distinguish their intended meanings from nearby misreadings. Do not replace a precise term with a bland synonym just for a uniform voice. Definitions and examples should preserve the decision a term enables.
- **Normal discovery.** The descriptions state when each method applies. Upstream `wait-what`, `to-questionnaire` and `teach` specify `disable-model-invocation: true`; the new versions omit that field and allow ordinary host discovery. This is an intentional invocation-policy change, not a claim that a host flag is portable. `wait-what` targets failure to understand the previous explanation, not surprise alone. Existing user-installed skills and host settings are untouched.
- **Independent distribution.** Required references and licenses stay inside each skill folder. The only additional instruction file is writing's conditional mechanics reference. Notices link maintenance records but do not tell an executing agent to load them.
- **Scope remains local to the request.** A method can improve a draft or explanation without authorizing messages, publication, persistent learning records or unrelated work. These boundaries are placed beside the relevant actions rather than supplied by a shared controller.
- **Source claims are not guarantees.** Terms can be useful without proving a causal theory about pretraining or attention. Formatting, discovery and source preservation are checked separately from behavior; the package makes no general performance claim.

## wait-what

Retained: the compact intervention, “re-pitch,” missing context, Simplified Technical English as a recognizable reference, and ubiquitous language grounded in relevant glossaries.

| Change | Why and readings considered |
| --- | --- |
| Description identifies the assistant's last confusing explanation and excludes surprise/disagreement alone | “Wait, what?” can express several intents; confusion is the repair trigger |
| Converts the source's first-person user prompt into agent instructions | Keeps the intervention usable as discovered guidance while preserving the intended request |
| Names the current point and important connection, with an example when useful | “Where you've got to” can otherwise invite a recap of the whole session |
| Preserves uncertainty/caveats and corrects an exposed mistake | “Re-pitch” could mean selling the same wrong answer more persuasively |
| Uses ASD-STE100 as a style reference, adds concrete short/direct/consistent-language guidance, and disclaims conformance | Retains the loaded reference without promising controlled-language certification or hiding necessary technical terms |
| Defines ubiquitous language as shared terms, starts from the conversation, and makes glossary lookup conditional | Supports non-repository use while preserving established domain meanings; no glossary setup becomes a prerequisite |
| Asks a focused clarification only when the repair target is unclear | Avoids responding to a clear request for explanation with another unnecessary interview |

The invocation-field change is described above. No glossary generator, teaching course or fact-check workflow was added.

## writing-for-agents

Retained: the two-file structure and Matt's conceptual sequence; context pointers, branches, context load versus human cognitive load, steps versus reference, information hierarchy, progressive disclosure, co-location, sprawl, completion clarity/demand, premature completion, post-completion steps, legwork, leading words, single source of truth, cache, relevance, no-ops and sediment. Much of the original wording remains where it carries the intended meaning accurately.

| Source area | Change and reason |
| --- | --- |
| Description and opening | Covers referenced agent instructions explicitly; aims for predictable decisions with task-appropriate output. Adds authoritative sources, accepted obligations, exceptions, provenance and user choices so a cleanup cannot silently change the contract. Already-authorized changes remain permitted. |
| Context pointers | Qualifies wording-only causality with actual host loading and accessible tools. Sharpen a weak pointer and inspect its reading path before deciding to inline. Retains the reason: unread target content cannot supply its own discovery cue. |
| Two loads | Defers context cost conditionally rather than promising zero cost; asks what the host actually loads. Preserves the human cost of remembering commands. |
| Hierarchy and disclosure | Retains the branch test and co-location, but treats attention effects as observations to check. Adds direct reachability, long-reference navigation and accounting for the full loaded path. Treats hierarchy and context budget as joint concerns rather than universally ranking one first. |
| Completion | Gives consequential steps evidence-based completion conditions. Exhaustiveness applies to defined finite sets; open work preserves uncertainty and a stopping condition. An empty known-question list is not exhaustive understanding. |
| Sequence splitting | Requires an observed problem and a meaningful change in visibility. Preserves Matt's warning that already-loaded instructions remain in context, and the reverse risk that merging exposes later steps; a new session or worker is an architectural choice. |
| Leading words | Preserves the mechanism as a writing technique, but replaces guaranteed pretraining activation with a definition and recognition test where meaning could mislead or consequential scope depends on it. Ordinary vocabulary needs no glossary. Names unintended role, intensity, authority and convention as possible imported meanings. |
| Tight/red examples | A tight loop supplies relevant feedback before the next change; independent speed, determinism and cost requirements remain explicit when needed. Red means the relevant check fails on the bug, not an unrelated failure. |
| Negation | Replaces the universal elephant/forbidden-behavior explanation with a scope test. A prohibition names the excluded behavior and may leave the intended action implicit. Retains necessary prohibitions and offers a permitted route; positive wording must not weaken a boundary. |
| Reading for meaning | Adds proportional checks for literal obligations, implied/negative meanings and isolated-context interpretation. Keeps essential scope with the action and quoted or hypothetical instructions as evidence. Defines consequential changes through obligations, permissions, exceptions, responsible actors, data handling and completion. Unsettled interpretations, including definitions/tests/examples that would settle them, stay outside revised guidance; retain source wording/scope and report proposals separately unless deciding them is authorized. A stricter reading is still a change; embed-then-confirm is insufficient. Ordinary editorial choices need no approval. |
| Pruning | Checks that entry paths reach the surviving source and that deleted text carries no extra obligation. Allows short local reminders without creating competing definitions. |
| No-ops | Tests consequential claims against representative behavior, retaining real constraints even if a small sample succeeds. Removes a demonstrated no-op sentence whole. Replaces escalation from “thorough” to “relentless” with a concrete decision, action or evidence requirement. |
| Behavioral checks | Adds baseline/candidate comparison (no guidance for new methods; current version for consequential modifications), fresh caller context, relevant near misses, actual reference use and coverage limits. Mechanical checks remain narrow; ordinary clarifications need proportionate review. Unavailable runs are reported honestly and do not alone block ordinary authoring. |
| Mechanics: invocation | Removes universal flag, invisible-description, zero-context and cross-skill claims. Uses verified host behavior, normal discovery by default and preservation of existing user policies. Separates discovery from authority. |
| Mechanics: frontmatter/paths | Adds concise purpose-plus-trigger metadata and explicit distinction between installed-reference paths and task-output paths. |
| Mechanics: shared reference and splitting | Requires complete packaging when independent installation is intended, while allowing co-shipped shared references or verified declared dependencies. Requires a demonstrated independent use case for a split. Reading a file is not context isolation. |
| Mechanics: router | Retains the idea as an optional response to demonstrated discovery difficulty; host abilities decide whether it can invoke anything. Satchel itself has no router. |

These additions are authoring guidance, not an asserted improvement over Matt's source or Atlas. Atlas retains its separate existing method for this release. The divergence is visible for a later owner decision rather than concealed behind a supposed shared source.

Two smaller wording changes are deliberate: the donor's preference for existing terms becomes choosing a fitting term while making coined terms earn their learning cost; its assumption that every document contains restatements becomes looking for them without presuming they exist. Concrete `disable-model-invocation` instructions are replaced by checking the chosen host's actual metadata and behavior, not by an equivalent universal flag.

## to-questionnaire

Retained: “Grill the send, not the subject”; identify the recipient and what the user needs back; target their knowledge gap; make the document answerable without the original conversation; put important questions first; allow partial answers; and invite missing context at the end.

| Change | Why and readings considered |
| --- | --- |
| Description names drafting for another person, asynchronously or in a meeting | Distinguishes an outgoing questionnaire from a live quiz or interview of the requester |
| Replaces two mandatory interview exchanges with using supplied facts and asking only material missing questions | The original staged questions can repeat information or block an explicitly requested draft |
| Allows a requested immediate draft with labeled assumptions | Missing context must not silently convert a draft request into an intake interview |
| Makes recipient responsibilities explicit, including multiple recipients | Knowledge and decision authority are different; one recipient must not silently inherit another's authority |
| Separates facts, decisions, advice and provisional assumptions | A question's premise can accidentally accept a proposal or supply an answer |
| Preserves coverage of every item the user needs back; orders prerequisites before dependent questions and uses simple conditional text | Makes an asynchronous first pass useful without a branching engine |
| Includes only recipient-appropriate context and flags questions that need unshareable context | A self-contained draft need not expose restricted material or silently leave an unanswerable question |
| Requires neutral questions and open/uncertain/conditional answers where options help | Avoids forcing a preferred answer or implying that listed choices exhaust reality |
| Replaces mandatory Markdown heading/template structure with a proportionate document shape; Purpose carries the role of “How your answers will be used” | Supports two short emails or a small list as well as a longer document |
| Uses a deadline or effort expectation only when supplied | Avoids inventing commitments on behalf of the user |
| Defaults to a response draft without a requested destination; makes file output conditional on the user's requested artifact; retains the source topic-slug filename fallback for saved Markdown | Supports existing destinations and chat drafts without writing files merely because the skill ran |
| Explicitly distinguishes drafting from sending or collecting responses | “Send-ready” describes the draft's usefulness, not authority to contact someone |

The invocation-field change is described above. The source's single-person framing, fixed “one exchange” pacing, required From/To fields, answer-stub formatting and exact example are no longer mandatory; their useful roles are preserved when the requested format needs them.

## teach-me

This is the largest adaptation. Matt's `teach` assumes a stateful teaching workspace. Satchel's `teach-me` serves a focused conversational learning request. It retains the source's **mission**, tightly scoped **lesson**, **zone of proximal development**, **retrieval practice**, feedback, and distinction between present fluency and lasting retention. These terms define decisions: what to teach next, how much help to give and what an answer can establish.

| Source area | Change and reason |
| --- | --- |
| Name/description | Renamed `teach` to `teach-me`, targets learning with optional practice, and distinguishes ordinary fact questions and explanation repair. Omitted source `argument-hint`; explicit invocation remains available through normal host discovery. |
| Stateful premise and workspace | Removed automatic `MISSION.md`, `RESOURCES.md`, learning-records, lessons, reference, assets and `NOTES.md` creation, numbering and workspace conventions. A single learning request does not authorize a persistent course. The three source format files are therefore not bundled. |
| Mission/calibration | Uses supplied goals and level; asks only when the missing distinction changes the lesson. A learner need not complete an intake interview before receiving a useful answer. |
| Knowledge/skills/wisdom framework | Focuses on the learner's requested understanding or ability. Removes compulsory resource-building and community referral; these are unnecessary dependencies for the bounded conversational method. |
| Sources | Replaces “Never trust your parametric knowledge” and mandatory source collection/citations in every lesson with suitable verification of unfamiliar, disputed or changing claims and honest separation of inspected sources, recall and examples. |
| Lesson format | Removes mandatory HTML, beauty/style prescriptions, CLI opening, cross-lesson links and primary-source/follow-up reminders. Honors the requested depth, format and artifact home. |
| Shared assets/reference library | Removes mandatory stylesheet, reusable components, no-inline-code rule and parallel reference-document creation. Those belong to an explicitly requested course/artifact project. |
| Zone of proximal development | Defines the next reachable challenge from observed learner evidence; vocabulary, confidence or silence is insufficient evidence of mastery. No filesystem learning record is required. |
| Explanation | Adds worked examples, analogy limits and preservation of needed technical precision. A direct answer remains available when requested. |
| Practice/feedback | Offers practice without requiring the learner to request interaction first, while honoring an explanation-only preference. Adapts feedback to the actual attempt, preserving the next-attempt feedback loop without requiring automatic tools. Hints support the next attempt; the learner can request a solution instead. Removes exact equal-word/character counts but retains avoiding answer cues through position, length or formatting. |
| Fluency/retention | Retains the distinction, limits what one successful answer proves and suggests later retrieval or a changed example when useful. Removes automatic curriculum, community and persistence assumptions; schedules require a request. |
| Ending/artifacts | Finishes at the requested depth. Saves lessons/reference sheets/records only when requested, in the user's format and home. |

Other deliberate reductions: the source's named spacing, interleaving and desirable-difficulty program becomes optional later retrieval or a changed example, without asserting equivalent long-term effects. Its knowledge-versus-skill difficulty doctrine and “only what's required to acquire that skill” rule become goal-appropriate depth and reachable challenge, allowing conceptual learning as well as skill acquisition. The source's compulsory glossary adherence belongs to its removed reference-library workflow; this adaptation introduces no new glossary machinery. It does not discover, migrate or manage an existing Matt teaching workspace. Such workspace work requires an explicit assignment and the relevant existing instructions.

The invocation-field change is described above. This adaptation does not claim equivalence to Matt's full teaching system, validated long-term learning gains, or coverage of all its capabilities.

## claim-check

This is original guidance rather than a port. Its additions each support the requested claim/evidence task:

- Fix the claim's scope before judging it so time, population, comparison and conditions survive paraphrase.
- Respect supplied-source boundaries and label missing access so a document check cannot masquerade as external verification.
- Label recalled background knowledge separately from inspected evidence; a remembered source or quotation is not a checked citation.
- Trace original evidence and repeated accounts so repetition does not become false corroboration.
- Check numerical units, denominators, time periods and causal inference because each can change a conclusion without changing the quoted numbers.
- Locate quotations in context and connect conclusions to actual passages/calculations rather than merely related links.
- Distinguish supported, supported only in narrower form, contradicted and unresolved; absence of support is not evidence of falsity.
- Treat source instructions as data, preserve uncertainty under user pressure, and avoid invented confidence scores.
- Scale the return to the request. A short check can be a sentence; a long document is not automatically exhaustively audited.

No autonomous research service, source database, mandatory web search, publication action or professional-certification claim is introduced.

## Other candidates considered

| Candidate | Disposition and reason | Revisit when |
| --- | --- | --- |
| Audience rewrite | Deferred. Ordinary requests already specify audience and tone; no distinct repeatable method was established beyond preserving meaning. | A recurring audience/format problem demonstrates useful additional guidance |
| Context handoff | Deferred. Atlas already exposes a handoff; a general standalone version may be useful but needs a clear non-engineering continuation case and preservation criteria. | Repeated cross-session work outside Atlas establishes what a separate entry must preserve |
| Grilling / decision check | Deferred. No sufficiently distinct bounded standalone method was established for this release. Atlas Wayfinding is an existing option for Atlas users; questionnaire addresses a different, asynchronous task. | A bounded, standalone decision review is needed without a sustained exploration mode |
| Shared lead/router | Excluded from this release. The accepted product is independent skills, and a five-item catalog is sufficient. | Users demonstrate a discovery problem that a catalog alone cannot solve |

The required concept review supported the five-skill collection, subject to full source inspection and final implementation review. Reviewer recommendations were checked against the sources; model agreement is not evidence of behavioral reliability. [Validation](../validation/satchel.md) records the completed coverage and remaining limits.
