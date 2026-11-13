# Evaluation authoring and standalone native trials

Observed November 13, 2026. These developmental checks cover the new Atlas evaluation-design method, Satchel `to-eval`, and native runner conditions. They do not establish general improvement, automatic routing, or compatibility with every host.

## Candidate and conditions

The candidate adds Atlas 0.12.0 and Satchel 0.4.0 over main `2ccb748024fd36b1fc42c9a80feb4f8df5c81bdc`. Trial metadata retains the actual uncommitted source hashes, staged files, runner identity and native responses. Public code review preserves the candidate; detailed synthetic traces remain maintainer evidence.

Four cases ran once with their explicit skill entry and once with no installed skills or skill input, using native Codex CLI 0.153.4, `gpt-5.6-sol`, low effort, and a 300-second trial limit. Both arms used the same raw tasks, fixtures and operating constraints. They had separate workspaces, Git roots, processes, configuration homes and threads. Standard host instructions remained active. This setup is not an adversarial isolation boundary.

Eight earlier requests using `gpt-6.1-sol` were rejected by the native account before actor work. Those attempts remain recorded as setup failures. The supported model was selected after querying native `model/list`; failed access is not a behavioral failure or evidence about either package.

All eight supported-model trials completed. Objective checks observed preserved guidance and source inputs, with changes restricted to permitted planning artifacts. Native tool capture parsed without errors and recorded local reads and planning edits; the reviewed events showed no tool execution prohibited by the task, outside-project reads or external operations. Hosts stopped and temporary authentication homes were removed. These facts do not grade the plans' meaning.

## Behavioral observations

| Case | Observed result | Claim boundary |
| --- | --- | --- |
| `eval-design-outbox` | Both plans distinguished final one-item state from proof of retry ordering and proposed additional operation evidence. The guided actor loaded and used the new method through the specialist index. | Baseline parity on this distinction. The unguided plan's acceptance gate could pass a requested item plus an unauthorized extra item, relegating the excess to a diagnostic. The guidance contains a closely related example; this is example application, not held-out transfer. |
| `to-eval-editor` | Both plans covered the respondent denominator, uncertainty, quotation and conditional expansion. The guided plan supplied explicit bad, correct, alternative and missing-evidence controls; it left quantitative product thresholds open. | The guided plan also contained a problematic missing-evidence example: an abrupt ending alone does not establish lost capture. Plans were not executed as benchmarks or validated by real readers. |
| `satchel-edit-scope` | Both returned faithful edits and left the source unchanged. The guided edit removed more introductory filler. | One writing sample supports a local observation, not an editing-quality rate or measured reader benefit. |
| `to-eval-direct-control` | Both answered `126`, without files or evaluation plans. | The guided skill was explicitly invoked; this tests response scope, not automatic selection. |

The author knew these cases before the runs, and the two design tasks overlap examples in the guidance. They are diagnostics. No aggregate win rate, causal improvement claim or release-reliability estimate follows from this set.

A separate fresh-context forward test used only the standalone skill and an unfamiliar purchase-order extraction brief. It produced a portable plan that separated date meaning from format, left ambiguous field policy unsettled, classified 14 previously used documents as development data, and labeled controls uncalibrated. The lead inspected that artifact. There was no unguided counterpart, actual document extraction, native packaging comparison or human study in that test.

## Grader and implementation checks

An independent context-only GPT-6 Sol / medium reviewer judged six controls without receiving their expected verdicts. It rejected an unsupported ordering claim and a denominator/causality-changing rewrite; accepted valid operation and wording alternatives; retained unknown usability for an inaccessible plan; and separated a good plan from an unauthorized execution. The lead verified all six scoped judgments. This demonstrates sensitivity on those controls, not general judge accuracy or agreement with an independent human reference set.

Opus 5.5 / high independently reviewed source. Verified findings led to explicit condition labels, unguided routing marked not applicable, rejection of a deleted explicit lead entry, visible tool-capture health, and clearer diagnostic/exposure and isolation limits. Static review is separate from native behavior.

A fresh GPT-6 Sol / high review inspected the corrected runner and the four design artifacts under anonymous condition labels. It found no concrete runner regression in the supplied source and identified the two plan-level grader defects above; the lead verified them against the artifacts. The unguided editor plan also called for calibration without supplying concrete control outputs. Both conditions therefore produced useful drafts that still needed review. The original artifacts remain unchanged; three derived regression controls were added to the reviewer guide and are explicitly distinguished from the six blinded controls. No further instruction text was added solely to chase these model misses.

The 44 evaluator unit tests passed, including five new tests for standalone staging, unguided initial/recovery inputs, preview side effects and invalid configuration. All 102 registered cases preflight in both conditions; that is not execution coverage. New-skill frontmatter, included license, local links and aligned package/marketplace versions were checked. These mechanical checks do not establish semantic quality.

## Next evidence

Review the generated graders before using their outputs for a decision. Test authentic incomplete answers separately from incomplete evidence capture, and use a fresh consumer to implement a produced spec. Add unfamiliar task families, native installed-but-not-invoked selection, representative multi-file journeys and previous-version comparisons where those claims matter. Host portability, human comprehension, broader standalone skill coverage and hardened evidence isolation remain untested here.
