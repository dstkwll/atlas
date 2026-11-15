# Schema-aware consumers and planning-artifact transfer

On November 14, 2026, seven bounded native Codex trials exercised a schema-aware outbox checker and fresh consumers of a PRD, tickets and a recovery handoff. This continues [artifact evidence boundaries](artifact-evidence-boundaries.md) and [issue #66](https://github.com/dstkwll/atlas/issues/66). It adds maintainer diagnostics; installable guidance is unchanged.

## Conditions and evidence

All seven declared attempts completed on Codex CLI 0.153.4 with returned model `gpt-5.6-sol`, requested low effort and a 300-second limit per trial. There were no replacement native attempts. Sources were based on `337b93ce39dad4db5d52f144c5d2cbc25e72987d` plus the evaluation changes in this PR. The three producers explicitly used their respective Atlas entries. The schema consumer and three implementation recipients were unguided, with no installed skills. Captured producer commands read the entry, lead and relevant documentation, tickets or handoff references.

Recipients received each producer's actual `planning/deliverable/` subtree and unchanged current Python sources. They did not receive the original brief, producer conversation, other planning notes or acceptance checker. The existing runner supplied local operating constraints and a common implementation authorization. The helper preserves artifact paths and records transferred hashes; the final helper also rejects edits, added files and partial deletions against the completion snapshot. PRD and ticket transfers preceded the partial-deletion guard; their actual complete inventories and hashes were subsequently verified against the final guard. No artifact was repaired before transfer.

Every trial retained metadata, source identities, before/after snapshots, events, captured tool records and completion/cleanup facts. Capture reported no parse errors; each native host stopped and its temporary home was removed. The primary inspected generated source and commands, then executed each implementation in a separate Python process using the task-derived checker. Detailed traces remain maintainer evidence. Mechanical results remain separate from the semantic findings below.

## Schema-aware outbox result

The new packet supplies the missing record contract: metadata keys such as `id` are legitimate and do not count as additional items. The consumer agreed with all **seven original vectors**, including complete malformed JSON, unavailable capture, exact output, wrong top-level shape, verified absence, an extra item and equivalent serialization. The earlier partially clarified consumer agreed with five of those seven; it returned UNKNOWN for both valid objects containing `id`.

This supports the missing-context explanation on this exposed case. It is not a controlled causal comparison: both packet and prompt changed, and a different fresh consumer produced the implementation. The earlier code and adverse results remain unchanged. These seven vectors do not independently cover every declared schema rule, such as an object without `id` or a wrong title.

The packet intentionally retains its earlier coarse rule that unavailable capture yields UNKNOWN. It therefore does not implement the newer distinction where a faithfully captured prefix can already establish a violation. The consumer also records unresolved duplicate-member semantics. Neither the seven agreements nor its own ten smoke checks establish a complete general-purpose grader.

## What each planning artifact enabled

The shared task is a pure active-loan CSV export: preserve the existing active predicate, export only three declared columns, keep dates opaque, sort by exact tool string then numeric loan ID, quote CSV correctly and preserve inputs. Overdue, timezone, reminder and invalid-input policies remain outside scope. The recovery case starts with working export code missing only the secondary sort key.

| Artifact | Producer observation | Fresh recipient observation |
| --- | --- | --- |
| PRD | Preserved required export behavior and deferred policy; source files unchanged. Added input-order preservation for records tied on both sort keys, beyond what the brief clearly settled. | Implemented the export; four inline self-authored tests passed. All five independent task-derived examples passed, with inputs preserved. No persistent test file was delivered. |
| Tickets and readiness index | One integrated slice was ready without future policy decisions. Baseline compilation and the reported `NotImplementedError` were supported by captured execution. No implementation was performed by the author. | Observed the stub failure before implementation, then passed five persistent tests and full available discovery. All five independent examples passed, with inputs preserved. |
| Recovery handoff | Rechecked actual tool-only sorting, rejected the stale fixed-status claim and carried the narrow remaining repair. Accurately stated that authoring had not run tests. | Changed only the sort key to `(tool, loan_id)`, ran focused local checks, and passed all five independent examples. No persistent test file was delivered. |

All three recipients preserved `loans.py`, the received documents and runner guidance. Inspection found standard-library, in-memory implementations with no added filesystem/network behavior. The handoff's one-line source diff also satisfied its narrower scope. These observations are distinct from the objective file-boundary check, which alone cannot establish narrow repair behavior.

The PRD's extra exact-tie rule remains an author-fidelity caveat even though its recipient implemented it. The independent checker does not turn that extra rule into accepted task policy. Successful implementations do not prove flawless authoring, artifact-format superiority, human comprehension, natural method selection or general reliability. The recovery recipient also had substantial working code as evidence.

## Checker review and retained limitations

The task-derived checks use literal expected rows for empty input, all-returned input, filtering/numeric ordering/blank dates, exact primary string ordering, and quoted fields with private extras. Each checks input preservation. Opus 5.5/high source review found that the initial vectors accidentally accepted an ID-only sort. The primary reproduced that false positive and added a separating primary-order/case-sensitivity example plus negative controls. This amendment occurred after producers started, before any recipient run or output grading; source requirements did not change. It is not a fully preregistered evaluation.

Review also improved artifact-path preservation, completion-hash checking, timeout/exit handling and permitted test-cache scope. A fresh Codex reviewer found that deleting one document after completion could transfer an incomplete packet; the final inventory comparison and multi-document regression resolve that defect. The reviewer independently verified the repair and seven focused tests. Opus supplied source review, not execution evidence; its job was `62a91051-8d7c-46ea-91e1-6599eae24d0d` with cross-family routing.

Final local verification: **62 evaluator unit tests passed**, and **112 registered cases** preflighted in both guided and unguided conditions. The three dynamic recipients are not additional registered cases. These checks validate bounded evaluator behavior, not agent reliability. The transfer helper is a local fixture adapter with manual review, not an adversarial sandbox or automatic semantic grader.

## Retained output identities

SHA-256 identifies the exact generated outputs used for these observations. Trial metadata retains the full staged input and guidance identities.

| Output | SHA-256 |
| --- | --- |
| PRD | `b9353ab591f36c163f24a71e6a59ab8f9795891bb49633ecfb1029eb5fcd05ea` |
| Ticket | `473952ba567b7248935e67e3977fabeb8f135bd5ef4fc878d36502f6f06eb85a` |
| Ticket index | `263c10609d0a54d1c88701a25249a5875ad5dd9c12ce27d321d498a1f2531738` |
| Handoff | `971f781639828c3107266b0693118c05974029d0b06cf07fe36492ac28e56d21` |
| PRD recipient implementation | `617122c86dde0081212149f19969478ec27102f81fef8dcac6915e280dc1bae2` |
| Ticket recipient implementation | `0dc5a4f2bbc7312974384b4d462a8874467d051bf9b21309dc467d8510de568d` |
| Handoff recipient implementation | `7b715df5d8ed34f2a82fd2753c7d9b3bd6455c041adba8c7e66883906757a8c3` |
| Independent CSV checker | `29708911bd14c7a4e497128ad0876956b975ef43d48c796c2b16c8c83b84fb8f` |

The next useful evidence is a different task family with a real unresolved dependency or authority conflict, plus an unguided author baseline. The current result does not justify changing portable runbooks or adding a new runtime. The broader initiative remains open.
