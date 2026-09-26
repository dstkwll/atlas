# Guidance consistency and planning transitions

## Scope and method

Three reference clarifications align specialist record placement, investigation continuity and transient retries with existing shared contracts. Two additional cases probe existing behavior rather than introducing more product rules: partial agreement through ticket creation, and working notes through an HTML PRD and later amendment.

Baseline main: `47e32b57be11304de7b21745d0059783dc162760`. Candidate product differs in the three reference paragraphs and manifest version. Native trials use a copied candidate with per-file SHA-256 identities retained locally. No planning/PRD instructions changed for these experiments. These are descriptive probes, not a baseline comparison or a reliability estimate.

Host: Copilot CLI 1.0.82, native `atlas:atlas` profile, gpt-5.6-sol with low effort. Each case has a fresh synthetic Git workspace and Copilot home, a configured `notes` planning root, an existing request-inbox note, and three ordinary conversation turns sharing a session. The operator does not explicitly invoke a skill. The model may invoke one itself. Only file read/search/write and skill tools are exposed; no shell, implementation, installs, external services or delegation. This is ordinary native permission control, not hostile-code isolation.

The reusable Codex cases use `planning/inbox` to match that runner’s existing scope checks. They have not been run through Codex in this change. Native Copilot fixtures use project configuration and are separate conditions. Manual semantic criteria are in `evals/review.md`; artifact existence and infrastructure tests alone cannot pass these cases.

## Observations

Both native cases completed all three turns once, with no timeout or replacement run. Candidate plugin files remained byte-for-byte unchanged; retained workspace changes stayed under the configured topic home. Primary review inspected successful reads, messages, per-turn snapshots and final artifacts.

| Dimension | Partial agreement → tickets | Notes → HTML PRD → amendment → pause |
| --- | --- | --- |
| Activation | Atlas skill loaded from the native profile | Shared Atlas read successfully after the profile selected the PRD skill |
| Routing | Discovery and continuity consulted before notes; ticket runbook consulted before tickets; notices supplied | PRD, artifact location, HTML and discovery references consulted; handoff reference consulted at pause; notices supplied |
| Application | Owner self-release accepted; proposed reason, destination and manager policy stayed out of executable requirements. Two ordered ticket drafts include test prerequisites and a conditional block if release forces unresolved policy. | Accepted behavior and open manager policy survived. Amendment reached readable and recovery sections. Final HTML explicitly owns the planning account and contains its recovery context. Attribution lagged until the explicit pause prompt; see qualifications below. |
| Authority | Planning only; no implementation/publication. Drafts require repository inspection before execution. | Planning only; no implementation/publication. Fresh reader recovered that boundary. |

The ticket drafts state that target-repository inspection is still needed before execution. One out-of-bounds file-view request failed and was recovered; no condition was discarded.

A fresh Copilot reader (gpt-5.6-luna, medium) received only the final HTML, without the source note, prompts or expected answers. It recovered manual claiming, conflict behavior, owner release to the unclaimed queue, no new service, unresolved manager policy, planning-only authority, user amendment attribution and the next design activity. The primary compared that reconstruction to the original fixture and user amendments. This establishes one bounded recovery example, not fresh-session activation or autonomous execution readiness.

### Qualifications retained

- After the amendment, HTML content was current but attribution still said no decision-maker was recorded. The explicit pause/recovery request repaired this in the final HTML. The experiment therefore does not establish timely attribution on every material update.
- The adjacent note remained consistent, but had no pointer to the newly authoritative HTML. Final HTML names itself the source of record; entry through the old note remains less clear than the continuity guidance intends. No contradictory current requirements were observed.
- No rendering tools were exposed. The agent made no claim of visual testing, but did not explicitly disclose the missing rendering check required by the HTML runbook. Visual quality, narrow-width behavior and print recovery are unverified.
- The HTML treats “more than two claimants” as proposed in its acceptance table while describing the general single-winner rule elsewhere. The fresh reader recovered this qualification; it illustrates remaining editorial consistency limits, not a new user decision.

The final planning deliverables met the targeted acceptance-boundary and recovery goals, with the above application gaps. No additional product wording was added for them: existing continuity/HTML guidance already covers attribution, linking and honest verification reporting. Keep these as regression examples and require broader evidence before changing the routing or adding another instruction.

An initial Sonnet/high source review was inconclusive because the brief omitted linked contracts. A supervised Sol/high review received those contracts and found no material inconsistency in the three edits. The primary verified that approved locations do not grant export permission, routine discovery continuity is already canonical, and transient recovery remains bounded with uncertain-write reconciliation.

## Evidence and limits

Local raw events, snapshots and filtered tool/message evidence with original event line numbers, per-turn artifacts and source identities are retained in local maintainer evidence. Evidence excludes hidden reasoning from the retained review packet. The trial driver is retained with that evidence. Raw host events remain local; no workplace data is involved.

Fifteen evaluator infrastructure tests pass; all 117 product-relative Markdown links resolve and manifests/cases parse. These checks do not prove activation, judgment, visual quality or cross-host compatibility. The three consistency corrections have source-level validation; the planning experiments do not exercise their routing and are not evidence of a causal improvement from those corrections.
