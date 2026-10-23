# Session Canvas validation

October 22, 2026. This covers the first Satchel `session-canvas` candidate on main `e9a5e5a`, with Satchel advanced from 0.2.0 to 0.3.0. Atlas's package is unchanged. The [accepted decision](../decisions/2026-10-22-session-canvas.md) defines the intended behavior; the [reusable cases and review criteria](../../evals/session-canvas-review.md) retain the fictional inputs.

## Behavioral observations

Fresh Codex subagent contexts exercised the instructions, with actual file access for the candidate and no desktop renderer. The inherited model and effort were not independently captured. The primary editor wrote the cases and inspected the responses and saved HTML; these are small diagnostic checks, not held-out effectiveness evidence. The baseline and candidate used the same initial user facts, but had different permitted file access and guidance. Only their first conversational response was compared.

- **Initial discovery:** the ordinary-prompt baseline immediately produced a useful text canvas, preserving open choices and booking limits. The candidate read the skill, reused those facts, recommended a combined view with a simpler alternative, and waited at a text brief. It did not create a file before confirmation. This demonstrates a difference on one prompt, not that the baseline failed its own instructions or that the skill reliably improves outcomes.
- **Confirmed construction:** after confirmation, the candidate read the exploration, progress, understanding and saved-artifact references and wrote one HTML file. Source inspection found the open venue choice, active access investigation, unstarted outreach, booking boundary, inspectable reasons and an explicit assessment point/scope. HTML source checks passed; visual readability and interaction were not observed.
- **Changed route:** a later user report ruled out the library for a Saturday event and selected the workshop. The same file retained the Saturday outcome and overview structure, changed the venue and investigation status, preserved the supplied reason, and kept outreach unstarted and booking withheld. It labeled completion as reported and left workshop availability unknown.
- **No-change exchange:** the candidate compared the next user message with the canvas and changed only the two assessment paragraphs. The substantive facts and layout remained unchanged. The marker named the new exchange and distinguished considering invitees from starting outreach.
- **Scope controls:** a separate fresh context handled two prompts together. It proposed focused exploration for an early idea and asked about the user's motivation before drawing. It answered a one-off browser/proxy/server explanation with a small diagram without imposing ongoing-canvas discovery. The shared context and explicit description mean this is not independent native automatic-routing evidence.

All candidate artifacts retained the missing-preview qualification. No booking, outreach or other external task was performed. These observations do not establish reliable upkeep across long sessions, after compaction, or after a missed check. Direct canvas editing, same-session reopening, automatic activity detection, racing updates and cross-session transfer were not exercised.

## Independent source review

Authenticated Copilot GPT-6 Sol / high completed a fresh context-only review of the skill and all five references. It reported no evidence-backed defect and explicitly withheld runtime conclusions. The primary lead checked its authority, assessment and rendering-evidence observations against the source. There were no review-driven behavioral edits. All emitted events were retrieved without a reported gap; this is a source-review receipt, not a behavioral success rate.

The reviewed six-file skill tree has SHA-256 `da535d105034bae3314a77af84a4d0da88ee570f2bf38944935a6664d7820020`, computed over sorted relative paths, each followed by a NUL, file bytes and another NUL. No fixed renderer, event listener, runtime or template is shipped.

## Host evidence and limits

Read-only inspection of installed GitHub Copilot app 1.1.15 found its embedded `create-canvas` guidance and shipped SDK contracts. They describe session-scoped scaffolding, extension guide/reload/inspection tools, native open/actions, saved content identity and a loopback renderer. The primary lead independently read the relevant embedded sections and the [official canvas-extension guide](https://docs.github.com/en/copilot/how-tos/github-copilot-app/working-with-canvas-extensions). This supports the runbook's source basis; it does not establish that the tools are exposed or work in a live desktop session.

The attempted desktop inspection stopped because the Mac was locked and computer use could not unlock it. No fresh Copilot conversation or extension was created. Initial rendering, update visibility, panel reopening and the optional passive activity signal therefore remain unverified. The baseline feature is the visible last-assessed point; no live freshness indicator is promised or implemented.

The Codex-side trial established instruction following and saved-file changes in a subagent workspace. It did not exercise the Codex app preview, automatic refresh or native skill picker. Neither host has a completed end-to-end desktop walkthrough in this evidence.

## Mechanical checks

The skill format validator and five within-folder relative references passed. The repository's 39 evaluator unit tests passed; they protect evaluation infrastructure rather than this skill's judgment. Package/version and diff checks are recorded with the PR. Mechanical validity does not establish discovery, useful application or desktop compatibility.

An offline Copilot CLI check used a copied standalone folder in a temporary project's `.github/skills/session-canvas`, with fresh configuration/cache and blocked network/user-state access. It discovered the exact name and description as an enabled project skill. No credentials, inference, installation or global configuration changes were used. The normal launcher reported 1.0.91; isolation with updates disabled selected bundled CLI 1.0.83, which is the version actually tested.

The same 1.0.83 CLI accepted `--plugin-dir <candidate-satchel> skill list --json` but listed only its two built-ins, omitting every Satchel skill. That command did not confirm plugin discovery; its cause remains uninvestigated. These CLI observations neither confirm nor refute desktop canvas rendering.
