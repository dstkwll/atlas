# Continuity creation and visible updates

Checked with Copilot CLI 1.0.82, GPT-5.6 Sol / low, against main `6db28eb` and the candidate. This is a bounded diagnostic series, not a reliability estimate. No installed plugin was changed.

## What changed

The lead's continuity obligation now appears at task establishment, with a concrete trigger in discovery before moving from an accepted design decision to the next consequential question. Routine recovery records do not need a separate artifact request; trivial tasks and explicit no-write instructions remain exceptions. Existing records are reused, otherwise the topic's approved planning home owns current.md. Configuration is optional. First use explains storage and gives a usable file path; material successful updates include a concise linked notice. Choosing a task destination does not silently change global settings. The Copilot profile still loads one shared lead source.

## Native profile exercise

Use the exact three prompts in `evals/cases.json`'s `continuity` case, without asking to save files or explicitly invoking a skill. Start with an empty synthetic project and a local candidate plugin. Select `atlas:atlas` once and send the subsequent messages to the same session. Inspect tool calls, returned results, the actual files and their updates at each turn. The explicit skill input of `evals/run.py` tests a different activation path; it was not used for these Copilot trials.

The tested invocation used `--plugin-dir <local-candidate> --agent atlas:atlas --session-id <uuid> --model gpt-5.6-sol --effort low --output-format json -p <turn>`. Each condition had a separate COPILOT_HOME and workspace, existing authentication supplied only through the child environment, no plugin installation, no remote export, disabled built-in MCPs, and `--available-tools view,glob,grep,create,edit,apply_patch,skill --allow-tool write`. External actions, source implementation, delegation and changes to the candidate/instructions were prohibited. Each invocation had a 180-second timeout. This is an ordinary native permission boundary, not hostile-code isolation. Record the installed host version, exact candidate bytes, prompts and settings when reproducing; tool names and support can change.

Keep observations from repository files and the host's session artifact directory separate. Copilot used its own persistent session-files area in the repository-free fixture; checking only the project tree would incorrectly report no record. A second fixture supplied a Git repository, `atlas.config.yaml` with `artifacts: { planning_root: notes }`, and an existing `notes/request-inbox/current.md` with a prior no-new-external-service constraint. The project instructions explicitly identified that config and existing record.

## Observations

| Condition | Observed result |
| --- | --- |
| Initial restricted-tool exercises | The allowlist omitted Copilot's apply_patch tool. No writes were possible. These four conditions are setup-limited, not evidence that Atlas failed persistence. The candidate reported inability to save. |
| Baseline with writes available | No record in the first two design/decision turns. Wrote a handoff at pause. |
| First wording candidate with writes available | Still waited until pause; saved a current.md in host session files. Clarifying triggers at the bottom of the lead was insufficient in this trial. |
| Candidate with obligation moved near task establishment and discovery link | Read continuity and created a record at the accepted-decision turn, then updated it at pause. Explained storage and alternative location, but omitted a usable path from its response. |
| Explicit configured project home | Updated the existing notes/request-inbox/current.md, retained the earlier constraint and unresolved manager policy, and created no competing record. |
| Explicit first-write path wording | Created at the accepted-decision turn and announced the actual path. Pause response still lacked a linked update notice, before that rule was added. |
| Final material-update notice wording | Created at the accepted-decision turn, announced the actual destination and alternative-folder option, then linked the successful write with what changed. At pause, updated the record and linked the checkpoint with the next decision and no-implementation boundary. |
| Trivial answer and explicit no-write controls | No planning notes were created in the project or session-files areas. Both were repeated on the final candidate. |

All attempts were retained: four setup-limited conditions, four writable baseline/initial-candidate conditions, three placement conditions, one configured-home condition, one path-notice condition, and three final-notice conditions. Each design condition used three ordinary turns; each trivial/no-write condition used one. Revisions were diagnostic responses to observed gaps, not repeated sampling until a fixed candidate passed. They therefore cannot establish a causal effect size or general success rate.

The final record preserves manual exclusive claiming, one winner with owner feedback, owner release, unresolved manager reassignment and discovery-only authority. There is a remaining content-quality concern: it labels return-to-unclaimed as user-accepted while also leaving release destination open. The user explicitly accepted release, not every resulting state rule. Timely storage and visible updates do not establish perfect decision attribution or an implementation-ready design; that artifact needs review before use.

## Review and limits

Independent source review checked trigger ambiguity, existing-record reuse, lightweight and no-write exceptions, and persistent-setting authority. The modifier was clarified, the artifact tree now includes conditional current.md, and context loss remains explicit in the route. A subsequent Sol review identified ambiguity between project-wide and cross-project persistent defaults; that scope is now explicitly clarified before settings changes. That final scope-only clarification was source-reviewed, not exercised in a configuration-writing trial. The reviewer received the diff and configured artifact, not the raw native traces, and correctly withheld independent behavioral approval. The primary inspected the actual tool calls/results and artifact contents. A possible delayed claim/release feedback ambiguity in the synthetic brief was treated as artifact quality feedback, not a defect requiring extra Atlas policy. Review event history had an eviction gap; the terminal result was available in full.

Raw native streams and diagnostic drivers remain local; filtered tool/message evidence and actual artifact contents are retained in the workspace's research/2026-09-10-continuity directory, excluding reasoning messages. Candidate file identities distinguish the revisions. No workplace material was used. No native compaction, fresh-session recovery, VS Code UI, global vault write or missing/unwritable configuration trial was performed here. The configured-home check preceded the final notice-only wording; it proves that tested location behavior, not every possible configuration. Fifteen evaluator correctness tests remain separate from these qualitative behavioral observations.
