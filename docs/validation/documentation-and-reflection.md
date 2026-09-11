# Documentation, reflection and impact checks

## Scope and source

The candidate replaces the PRD skill entry point with documentation, adds naturally routed impact analysis and intentional reflection, introduces Arena only as a confirmed runbook, and shares HTML presentation/recovery between PRDs and architecture documents. There is no PRD alias or swarm runtime.

Baseline main: `a2cec960c2dbaa36428fdad1ec00c4450f3cdb47`. Initial native cases used the working candidate with per-file identities retained in each metadata file. A follow-up candidate clarified the lead’s distinction between closing acknowledgment and agreement advancing unfinished work. A later source-only refinement explicitly permits delivering HTML with unavailable independent recovery validation disclosed. No other product behavior changed after those trials. These are descriptive probes, not a reliability estimate or a controlled improvement claim.

## Native conditions and observations

Copilot CLI 1.0.82, gpt-5.6-sol / low, local candidate plugin and native `atlas:atlas` profile. Seven initial cases completed nine turns. Three labelled follow-up cases completed four turns. Each condition used a fresh synthetic Git workspace and Copilot home; subsequent turns reused the native session ID. At most three conditions ran concurrently, with a 300-second limit per turn and no automatic rerun. Available tools were file reading/search/writing and skill loading; no shell, installs, external services or delegation. This is ordinary native permission control, not hostile-code isolation.

| Case | Observed result | Limits |
| --- | --- | --- |
| Documentation default | Explicit new skill request selected PRD; wrote `planning/inbox/prd.html` and made the current note a pointer. Preserved open manager policy and planning-only authority. | Source inspection only; the artifact inaccurately describes a missing owner key as unclaimed, whereas the supplied consumer requires the key and accepts a null value. No general documentation-accuracy pass. |
| Guide | Natural guide request consulted documentation guidance and wrote `guide.md` with prerequisites, command and expected output; no PRD. | Example command was not executed; the response did not clearly disclose that missing verification. |
| Architecture, initial | Wrote `architecture.html`, separating accepted commitments, proposed design and unverified implementation. Current note identifies the technical account; recovery context retains authority and next action. | No rendering or fresh-reader recovery test. The response omitted an explicit rendering limitation. Source presence is not visual or recovery proof. |
| Reflection | Explicit request produced a separate contextual file and linked it from current state; no shared-policy edits or implementation. | Initial note’s bare `BRIEF.md` pointer was interpreted relative to its topic folder, causing an unsupported missing-source conclusion despite the root brief being present. |
| Reflection, corrected-pointer diagnostic | With an explicit `../../BRIEF.md` link, inspected the brief and produced contextual lessons, evidence limits and proposed/accepted distinctions without the missing-source claim. | Fixture repair, not evidence of improved product instructions. |
| Arena proposal, then “Thanks” | Proposed two candidates with one attempt each and a total time bound; no launch; disclosed the project’s no-delegation restriction. | Usable delegation was not exposed, so actual launch/timeout enforcement and consent restraint with working delegation remain unverified. |
| Blast radius | Identified the consumer’s `KeyError` if `owner` is removed and described the lost display behavior; source unchanged. | No runtime test possible with these exposed tools; conclusion is source-level evidence. |
| Agreement continuation, initial and follow-up (two turns each) | First turn recommended keeping architecture in the PRD. Both second turns merely acknowledged “Agreed, thanks!” rather than advancing design or recommending the next activity. | **Continuation failed in both conditions.** The narrow closing-language clarification did not demonstrate a fix. Retain this regression case; do not claim reliable follow-through. |
| Trivial control, follow-up | Returned only “The reports are ready.” | One example; no general over-activation claim. |

All thirteen native turns completed. Candidate plugin hashes remained unchanged. Per-turn artifacts and events are retained, including failures; no failed condition was replaced or pooled into a success rate. Protected fixture/source files remained unchanged in the completed file snapshots. Tool effects and rendering claims were reviewed separately from mere artifact existence.

## Packaging and UI

The full package has six sibling skill folders: lead, documentation, tickets, handoff, blast-radius and reflection. Documentation includes the PRD-first freeform argument hint. Reflection uses Copilot/Claude `disable-model-invocation` and a separate Codex `agents/openai.yaml` with implicit invocation disabled; its runbook independently requires an intentional request. No Arena skill or old PRD entry point exists.

A native CLI picker probe recognized `/atlas:atlas-to-documentation` and completed the command name. The argument hint was not observed in that terminal surface, so its picker display remains unverified; a selectable enum is not claimed. An initial probe failed to attach stdin correctly. In the corrected terminal probe, an attempted command-menu navigation unexpectedly submitted the selected skill; it was interrupted, a shell-read request was rejected, and the terminal exited reporting zero file changes. This was a separate UI diagnostic on the CLI’s default Sonnet model, not one of the behavioral conditions above. Do not count it as successful end-to-end skill execution or zero-inference UI testing.

The bundled local skill validator accepts blast-radius but rejects `argument-hint` and `disable-model-invocation` as unknown keys. A future validator improvement should distinguish shared structure from host metadata and unsupported features from invalid content; that work is deferred. Those documented host fields are retained; YAML parsing, matching names and native Copilot loading were checked separately. This does not establish identical host support, VS Code picker behavior or Codex implicit-invocation behavior.

## Independent review and disposition

Sol/high reviewed the new shared contracts. One finding was accepted: explicitly disclose missing fresh-reader recovery validation rather than implying unauthorized delegation is necessary. Two findings were rejected after verification: a generic documentation request need not universally become a PRD (the accepted default is bare explicit invocation), and Codex invocation policy belongs in its separate `agents/openai.yaml`, not SKILL frontmatter. The review packet had concatenated file text without sufficient labels, contributing to the latter misunderstanding.

The final supervised source review used Opus/high and found no material defect in its supplied packet. Verified editorial findings clarified the follow-up case labels, retained disclosure omissions in this disposition, and kept the reconstruction comparison adjacent to the available-reader path. Its suggested extra pause wording was unnecessary because explicit pauses already take precedence; no behavior claim rests on that suggestion.

The feature scope is implemented with the limitations above. Guide example-verification disclosure and architecture rendering-disclosure omissions also remain open, as does the PRD source-accuracy miss. The recovery-validation refinement was source-reviewed, not behaviorally retested. The acknowledgment failure remains open; avoid additional universal instructions or a claim that this change solved it. The source clarification makes the intended boundary explicit, but its observed behavior remains unsuccessful in the tested condition.

## Evidence

Raw local streams: `/private/tmp/atlas-capability-evidence/` and `/private/tmp/atlas-capability-followup/`. Filtered messages/tool records with original event line numbers, per-turn files, candidate identities and driver scripts: maintainer workspace `research/2026-09-11-capabilities/`. Hidden reasoning is excluded from the filtered packet. The UI diagnostic used `/private/tmp/atlas-picker-probe/`; no workplace material or installed-copy update was involved.

Reusable cases and manual semantic criteria are in `evals/cases.json` and `evals/review.md`. They have not been run through the Codex runner in this change. Fifteen evaluator infrastructure tests pass, 144 relative product links resolve, YAML and JSON parse, and diff checks pass. These checks do not prove agent judgment or deployment compatibility.
