# Turn-ending guidance

## Contract and implementation

Atlas's closing guidance applies to every conversational turn, not just acknowledgments, substantial tasks or milestones. The shared lead requires a brief final **Next:** paragraph stating the useful next action and purpose, the needed decision, a pause/resume condition, or that no further action is needed. An explicit output-only request controls presentation. Guidance does not grant permission or justify invented work.

A user decision can satisfy a condition on work already authorized. Atlas should continue that work without asking for permission again; choosing a design still does not authorize implementation. The Copilot profile loads the shared guidance before the first response, including short replies, and points back to its required turn close. It does not duplicate the closing policy.

Baseline: `b59ddbf6d07d4fd393b87d337cbabeb0b2992eac`. Candidate identities are recorded with the local evidence. Five semantic cases were added to the existing evaluator catalog: a naming decision, short architecture question, design correction, completed assignment and explicit pause. They require artifact/event review; no keyword matcher or new enforcement runtime was added.

## Persistent native conversation

Copilot CLI 1.0.82, GPT-5.6 Sol / low, native `atlas:atlas` profile, one persistent interactive process, a fresh synthetic workspace and host home. The three prompts were:

1. Compare keeping or replacing the PRD entry point; recommend one and wait for the decision before developing the chosen design. Design only.
2. “I think just replace atlas to prd with atlas to documentation being the canonical entry point”
3. “Otherwise agreed. Let's move on”

The successful skill-load result contained the candidate's closing contract. The actual final responses and artifacts showed:

| Turn | Observation |
| --- | --- |
| Recommendation | Compared the options and ended with the naming decision needed before developing the design. |
| Naming decision | Recorded replacement, developed mode routing, planning ownership and acceptance examples immediately, then identified the remaining design choices. No second permission to resume design was requested. |
| Ordinary follow-up | Recorded accepted design and closed by stating that design was complete and implementation required explicit authorization. |

All three replies provided contextual next guidance. Only the brief and current planning record changed; no implementation was performed. The terminal exited successfully after the completed third turn. This checks one ordinary conversation, not reliability across models, compaction or workplace hosts.

This interactive candidate had the final shared lead and first-response profile loading. The additional profile link to the required turn close was present in the `turn-guidance-resume` naming/pause candidate copies, not in the interactive condition. Final source review then narrowed “each response” to “each turn's final response” to avoid applying the closing rule to progress notices; that source-only precision was not rerun. The live shared lead matches the delivered source; the profile difference is retained explicitly.

## Neighboring behavior and diagnostic limits

Fresh single-turn cases with the first-response profile and explicit close produced contextual guidance after a short question, a design correction and a completed assignment. The correction was actually written; the question and completion cases created no files. The output-only sentence correction returned exactly the requested sentence, without appended guidance; no skill load was observed there, so this does not prove the loaded exception caused the correct output.

Repeated `-p` invocations using the same session ID were also exercised. These are process-resumption tests, not a persistent interactive conversation. Several resumed replies still only recorded decisions or summarized status; the final profile-reference variant also retained omissions. The different interactive result does **not** prove process restart is the cause, that earlier skill contents were lost, or that the final profile link fixes resumption. Restoration and adherence across resumed processes remain unverified/inconsistent. Do not pool these runs into a success rate or claim universal adherence.

All development conditions are retained, including failures:

| Local packet suffix | Completed turns | Purpose |
| --- | ---: | --- |
| `turn-guidance` | 12 | Baseline naming conversation and initial standing-rule candidate with neighboring cases |
| `turn-guidance-final` | 9 | Decision-condition clarification and concrete pre-send check |
| `turn-guidance-profile` | 3 | First-response loading for question, completion and exact-output cases |
| `turn-guidance-verified` | 9 | Explicit closing paragraph with the first-response profile; includes resumed-turn misses despite the packet name |
| `turn-guidance-resume` | 5 | Final profile reference in resumed naming and pause conditions; omissions remained |
| `turn-guidance-interactive` | 3 | Persistent native conversation described above |

Noninteractive turns had a 240-second per-turn limit, at most three concurrent conditions, fresh per-condition workspaces, and file/search/skill tools only. Shell, delegation, installs and external services were unavailable. The CLI reported `create` and `edit` as unrecognized allowlist entries; file writes used available `apply_patch`. This is native permission control, not hostile-code isolation. All scripted turns exited successfully, preserved candidate identities and protected project controls; process success is not a behavioral pass. Paused cases recorded the supplied decision and stopped, but some omitted the requested explicit next guidance.

## Evidence and review

The maintainer workspace retains `research/2026-09-11-<packet suffix>/` with prompts, candidate identities, source snapshots, statuses and filtered message/tool evidence with original event line numbers. Hidden reasoning is excluded from filtered packets. The interactive packet includes the driver, final artifacts and candidate identities; its raw native events remain under `/private/tmp/atlas-guidance-live/`. No workplace material or installed-copy change was involved.

Independent Sol/high review verified the conditional-authority ambiguity and the distinction between a completion recap and explicit guidance. Opus/high final source review confirmed preserved authority and one shared policy; its response-versus-turn scope finding was corrected. Candidate-copy comparisons verified shared-lead identity and which profile variant each condition used. The review also reinforced the narrower persistent-session, paused-turn and exact-output evidence claims above. The existing 15 evaluator infrastructure tests pass; these reusable cases were not run through the Codex runner. The correction establishes the requested broad response contract and has bounded native evidence, without claiming the known resumption omissions are repaired.
