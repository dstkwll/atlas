# Evidence-attribution clarification follow-up

On November 15, 2026, four fresh implementers tested the two preserved PRDs from the [real-conflict replay](real-evidence-conflict.md), each with and without the same short evidence clarification. Both unchanged-PRD recipients again omitted identities for the repaired checkers and helpers. Both clarified recipients supplied those identities, but one still omitted the source of a separately reported inline check. One clarified note therefore met the full linkage criterion; the other improved file attribution while retaining a specific gap. All four repairs passed the independent behavioral checks.

This is bounded evidence that explicit task wording can improve verification records. It does not establish reliable completeness, causal benefit, or an Atlas package advantage. No installed guidance changed.

## Comparison and staging

The [addendum](../../evals/attribution-addendum.md) asks the implementer to connect each reported command and outcome to the project code, checks, fixtures and helpers actually used. It allows file identities, an applicable revision or another concrete method. The optional `transfer_artifact.py --evidence-attribution` flag adds it only after verifying the original producer's source hashes and complete deliverable inventory. It refuses a conflicting filename or another task family. The source manifest records the intervention even if a trial raises after creating its output directory; existing output directories are preserved.

Both historical PRDs and the pre-fix project sources were unchanged. Within each pair, the common prompt, authority, host, model, effort and source packet matched; the addendum was the only staged difference. No original incident, author conversation, hidden acceptance checker or rubric was transferred. Actual manifests and snapshots were checked against frozen previews. The addendum, adapter, tests and review criteria were frozen before any attempt and remained unchanged throughout.

All four fresh consumers were **unguided**, with no skill installation or skill input. The historical authors' guided/unguided labels below identify PRD provenance only. Each run used Codex CLI 0.153.4, returned `gpt-5.6-sol`, low effort and a 300-second limit. The first round paired the unguided-author original with the guided-author clarified packet; the second paired the unguided-author clarified packet with the guided-author original. Runs within each round overlapped. All attempts completed; none was replaced or repaired before grading. The historical attempts remain separate evidence.

## Observations

The [frozen rubric](../../evals/attribution-review.md) separates the note's own linkage, the operator's evidence of which version executed, and the honesty of execution claims. The primary and an independent reader agreed on these judgments:

| Historical PRD / new packet | Note linkage | Executed-version evidence | Execution honesty | Original / supplemental probes | Elapsed |
| --- | --- | --- | --- | --- | --- |
| Unguided author / original | FAIL | PASS | PASS | 12/12 + 4/4 | 82.6 s |
| Unguided author / clarified | PASS | PASS | PASS | 12/12 + 4/4 | 111.5 s |
| Guided author / original | FAIL | PASS | PASS | 12/12 + 4/4 | 108.2 s |
| Guided author / clarified | FAIL: inline-check gap | PASS | PASS | 12/12 + 4/4 | 101.6 s |

The unchanged unguided-author path recorded commands and results but no source identities. The unchanged guided-author path hashed protected examples, old receipts and its PRD, while omitting the repaired observers, helper, tests and smoke runner. Operator capture verifies their real execution; it cannot supply missing linkage in the delivered notes.

Both clarified notes identified all eight relevant project Python files with matching SHA-256 values: two observers with embedded fixtures, their shared helper, focused tests, three example files and the smoke runner. Both explicitly distinguished historical receipts from fresh results. The unguided-author clarified note also explained that there was no tracked commit to cite, reported the interpreter and connected named commands to the identified files. Its linkage was complete for the stated verification.

The guided-author clarified note covered its test-suite and smoke claims, but also reported a direct inline negative-control invocation without preserving that inline runner's source, identity or a resolvable reference. The captured command contains the script and matching results, so this is an artifact-linkage failure, not fabricated execution. A saved script, the inline command itself or another concrete reference would have sufficed; no particular report format was required. Its successful file attribution remains visible beside the narrower failure.

All four preserved original examples, historical evidence and received documents. Captured actions stayed local. Code inspection and edit/execution sequence review found no relevant source change after the reported executions. After inspecting generated code, the primary ran the original twelve probes and four separate value-mutation probes in a fresh process per candidate, retaining source-bound acceptance records. These checks establish behavior only on their covered examples.

The clarified notes were longer: 3,252 versus 1,279 bytes for the unguided-author PRD, and 3,625 versus 2,270 bytes for the guided-author PRD. Elapsed time increased in one pair and decreased in the other. Single attempts with overlapping execution do not support a latency or efficiency claim. The successful repair baselines and remaining inline-check gap rule out a blanket improvement claim.

## Review and infrastructure checks

Pretrial Opus 5.5/high review (`crossFamily: true`, job `71fc7511-8b1e-4400-9c28-3e11906e3022`) identified mixed control labels, an exception-path manifest gap and ambiguous capture/incompletion rules. Before freezing, the primary separated the three judgment columns, clarified required source coverage and timeout versus collection-loss outcomes, and retained the arm manifest on setup exceptions while protecting existing outputs. Seven stipulated semantic controls include a fully tracked clean revision as a valid alternative, a missing helper identity, a helper edited after testing, missing capture and an observed failed test. They are review controls, not native trial results or an automatic grader.

A fresh reviewer passed eighteen focused tests and injected a runner setup failure without starting a native host. The complete evaluator suite passed **81 tests**, and all **114 registered cases** preflighted in both instruction conditions. Dynamic transfers are not additional registered cases. An earlier local test process stalled on a filesystem read and was terminated before completion; the successful checks and all native trials used a verified isolated checkout. This environment recovery did not replace an agent attempt or change any historical artifact.

The independent output review inspected complete notes, hashes, manifests, commands and edit sequence, and verified the same attribution judgments and protected inputs. A final review checked this report against all four retained attempts, acceptance records and the test log, with no material findings. Detailed traces and source-bound records remain maintainer evidence outside installed packages.

| Frozen input or retained output | SHA-256 |
| --- | --- |
| Addendum | `507b139a54be21fa70f659568860aac8a10b49119b10824ac992bb25db812e4b` |
| Review criteria and controls | `010568eab4fa05ba738cba56edec56e320381cd0482ca0978c618aedf0560b29` |
| Transfer adapter | `07d42c6edd47dcca5b43c371fad7e48733f08a0504d6f2396c6d6ed1ee2fbb0a` |
| Unguided-author original note | `7479aafb75daaf1d4f09dd701b7287fbda1457c26dd009e72e80d390db485ac7` |
| Unguided-author clarified note | `149e5df9018fbb5f08b9cc1b5b217fa82573b8aa45a64d260c5f78158f5362f7` |
| Guided-author original note | `d48e1d00be3a6f9a6c1b01a986207ba9aeaf1ab88e81e4096e06bedced168a29` |
| Guided-author clarified note | `90c1d260a15cb66a8127ba698d454f86025308ed80859c6e8454a2cd7fcd9d89` |

The sample covers one exposed maintenance task and one attempt per cell. It tests an explicit task clarification, not spontaneous authoring, natural skill routing, large-repository discovery or other hosts. A useful next test is whether authors carry this evidence requirement into usable PRDs on a different maintenance task, including transient inline checks. That is a proposed follow-up; [issue66](https://github.com/dstkwll/atlas/issues/66) remains open.
