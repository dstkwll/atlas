# Ledger recovery evaluator coverage

This maintainer-only extension adds three frozen recovery scenarios and independent export observations. It does not change Atlas 0.7.4 guidance or introduce a runtime. The accepted outcome requires preserving input bytes, including when the export destination aliases the source.

## Sensitivity evidence

On September 20, 2026, the new probes were replayed against four retained synthetic native implementations produced under unchanged guidance. Source hashes were checked against their original after-snapshots before attributing replay results. Every implementation passed the independent preview and separate-destination export samples. Three failed source preservation for same-path, symbolic-link and hard-link destinations; the fourth preserved input for all three. The old generic observation check supplied host/guidance facts without checking export behavior. This demonstrates added detection of an observed defect, not improved model behavior.

Committed sensitivity tests reproduce destructive writing, a path-only guard that misses links, damage followed by an exception, a missing/always-refusing export, changed negative totals and incorrect rows. Safe refusal, safe no-op on aliases, and exports returning either data or nothing are accepted where the contract permits them. Frozen report hashes and actual good-pass/bad-fail execution establish the stale-source fixture's premise. The tests require no account, model or private trial files.

The protected-source observation compares snapshots, including the original verifier. A stronger verifier can make that fact false without violating the brief: review the diff for weakening. It is not a policy verdict. Likewise, an alias-preservation fact alone does not establish a working export; the separate export sample remains necessary.

## Maintained runner exercise

Three fresh runs used the normal `evals/run.py` entry point, unchanged Atlas 0.7.4, Codex CLI 0.153.4, and requested/returned `gpt-5.6-sol` with low effort, one turn per case and a 300-second host bound. All completed; host shutdown and temporary authenticated-home removal were confirmed. All passed preview, separate export and exact required-fixture observations, with no checker-induced workspace changes.

| Case | Same path | Symbolic link | Hard link |
| --- | --- | --- | --- |
| Disposable driver | Input destroyed | Input destroyed | Input destroyed |
| Required fixture | Input destroyed | Input destroyed | Input destroyed |
| Stale source | Input preserved | Input preserved | Input destroyed |

The required-fixture run restored the archived bytes and checked the manifest. The stale-source run repaired negative totals and added a realpath guard; its own symbolic-link check passed, but the independent hard-link probe exposed the remaining defect. These failures are retained as useful evaluator observations, not successful whole-task outcomes. All three strengthened the verifier, making the unchanged-source observation false; inspection found the original required sample still covered.

The stale-source report appeared in actual tool output before a later `.git` lookup failed, so consumption was reached in this sample. Current source hashes were also emitted. Neither fact alone establishes that the agent explicitly compared the report's source identity or retained its applicability judgment in the completion record. The rubric preserves those separate review questions.

Local automated verification: 35 evaluator tests passed (25 existing plus 10 ledger sensitivity tests), with no inference in the unit suite. Native outcomes above validate the extension's execution path and defect sensitivity; they do not measure an Atlas improvement.

## Limits

These are synthetic project-record recoveries with one sample per native condition, not genuine compaction or long-session trials. There is no no-Atlas control, guidance intervention, efficacy estimate or general correctness claim. Report consumption, applicability and source identity remain separate manual judgments with action/output witnesses; a failed chained command must remain a miss. The workspaces have no seeded Git repository. Raw host traces remain local; public maintenance and CI do not depend on them.
