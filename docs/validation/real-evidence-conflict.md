# Real multi-file evidence conflict

On November 15, 2026, four declared native attempts tested whether a PRD author could discover a sibling defect from conflicting repository evidence and transfer an actionable repair to a fresh implementer. Both the unguided and Atlas-guided paths repaired both observer families and passed all twelve independent probes. Both left the same evidence gap: their new verification notes did not identify the changed checkers and helper whose behavior they reported. This is parity on one bounded repair, with incomplete source attribution for the refreshed results; it demonstrates no Atlas advantage or general reliability.

## Real defect, curated replay

The case replays the actual type-mutation false positive found during [PR70 review](https://github.com/dstkwll/atlas/pull/70#discussion_r4577537654). Python equality treated equal-valued integer/float and integer/boolean values as preserved input. The defect affected both the support-summary and CSV observers, including exception paths. It was fixed before PR70 merged at `1904914fd4cd88c0740cd1e3c7456bf1ad257aac`.

The [fixture](../../evals/conflict-fixtures.json) retains exact pre-fix observer and validation-report bytes from `9c9210b9913d4e4e30343751d17e804bbaa889bc`, original positive receipts, and actual saved native implementations. Those implementations solve earlier synthetic application tasks; the evaluator defect and maintenance evidence are real. This is not a production incident.

The README, incident description and smoke adapter were written for the replay and are labelled as such in its source manifest. The incident describes only the summary counterexample. Authors must inspect the sibling CSV source and reconcile the green receipts with the weaker historical checker. Discovery is narrow: there are two observer modules and the smoke adapter invokes both. The case does not measure search through a large unfamiliar repository.

## Conditions and observed outcomes

All four attempts used native Codex CLI 0.153.4, returned model `gpt-5.6-sol`, low effort and a 300-second timeout. Raw author inputs matched exactly, apart from guided skill staging. The guided author used `atlas-to-documentation` and read the lead, documentation, PRD, artifact-location, documentation-reference and existing-behavior guidance. Each fresh implementer was unguided and received only its actual PRD, unchanged observer/example code, original receipts and smoke adapter. Original incident, reports, manifest and author conversation were excluded. No document was repaired before transfer; no attempt was replaced.

| Observation | Unguided author path | Atlas-guided author path |
| --- | --- | --- |
| Author completed, planning only | 98.9 seconds | 143.2 seconds |
| Both observer defects discovered and reproduced | Yes | Yes |
| Fresh implementer completed | 90.4 seconds | 96.8 seconds |
| Independent behavioral probes | 12/12 passed | 12/12 passed |
| Implementer's own tests, observed in capture | 6 passed | 10 passed |
| Retained examples through the smoke adapter with repaired observers | 5 summary + 5 CSV passed | 5 summary + 5 CSV passed |
| Original evidence, examples and received PRD preserved | Yes | Yes |
| New results identify changed checker and helper versions | No | No |

Both authors initially hit an import-path error in a local diagnostic and then successfully reproduced the mutation using the examples directory on `PYTHONPATH`. Captures retain those failures. Both correctly distinguished an insensitive checker from incorrect application implementations; neither treated the counterexample as proof that every old result was false.

The primary inspected generated code and commands before executing the [independent probes](../../evals/conflict_checks.py) in separate processes. The probes cover both observers, retained implementations, valid output-key-order or CSV-line-ending alternatives, numeric type mutation, mutation followed by exception, and nested scalar type changes. The frozen checker, fixture, rubric and transfer machinery were unchanged after author execution began. All captures parsed without errors; host completion and temporary-home cleanup were recorded. Commands reviewed were local to the supplied projects, with no observed external service or publication action.

## Artifact quality and evidence limits

A condition-blind reader inspected both actual PRDs against the source packet, without access to runtime outcomes. Both covered the affected files, normal and exception paths, retained behavior, history preservation and local re-execution. Primary review agreed that both were actionable for the core repair.

Both omitted explicit attribution of fresh results to the repaired sources and any new helper. The unguided-path implementer recorded commands and passing results. The guided-path implementer additionally hashed the unchanged examples, historical receipts and received PRD, and correctly noted that an empty Git diff in an untracked snapshot does not prove preservation. Neither identified its changed observer/helper bytes. Captured execution and the primary's separately retained source hashes support the observed repairs, but do not retroactively supply that missing linkage in the recipient-authored verification notes. This is a source-attribution gap, not a requirement for a particular filename, JSON schema or hashing algorithm, and not evidence of fabricated execution.

The guided PRD also imposed package-style import compatibility and excluded JSON serialization as the comparison contract. Top-level imports were demonstrated by the packet; an existing package-import consumer was not established. Raw JSON can lose Python type distinctions, but alternatives should be judged against the actual distinctions required. Both PRDs chose dictionary-order and identity/alias boundaries; the unguided PRD anticipated tuples beyond current fixture data. These are scope/constraint caveats beside the successful repair. The guided PRD was longer (15,076 versus 10,721 bytes), with no demonstrated downstream benefit here.

## Calibration, review and reproducibility

Before any native author, Opus 5.5/high source review (`crossFamily: true`, job `ad2b6a1b-f44f-46f5-83d8-4b84b11ccb79`) identified setup and grading issues. Corrections made Markdown and scratch locations explicit, allowed new evidence and verification files while protecting originals, removed an incident hint prescribing refreshed hash records, corrected provenance labels and checked hashes, and made nested probes compatible with a default-bound case list. A fresh Codex review independently passed twenty focused tests and found no remaining repair defects.

Controls expose the original mutation defect in both families, retain CSV failure after a summary-only repair, reject an always-false preservation check and a normal-path-only repair, and accept a JSON-based alternative on the covered fixture domain. That alternative control does not establish support for every Python key or object type. The probes cover acyclic built-in values; they do not establish identity, alias, cyclic-data or arbitrary-object preservation.

At the original trial checkpoint, all 75 evaluator unit tests passed; all 114 registered cases preflighted in both conditions. These infrastructure checks are separate from the four native attempts and their manual judgments. A final independent review checked this report against all four retained trials and found no material overclaims; a wording correction clarified that the smoke adapter itself was unchanged. The [procedure](../../evals/conflict-review.md) preserves the four-attempt bound and separates objective protection checks, semantic PRD review, runtime repair and evidence applicability. Detailed traces, original outputs, source inventories and independent acceptance records remain maintainer evidence outside the installed packages.

| Frozen artifact | SHA-256 |
| --- | --- |
| Replay fixture | `af8b90c4e3ec0d25bf631a750024ef38a0c31b88827c6e50eaeccd85d4658328` |
| Independent probes | `9bda174e0ee0dc73ecde9b1cfcd0018875c6bdaa7456f1f3399f5c510fb5a5fb` |
| Review rubric | `e6e85bd8bd6d63bbded7dab439e2285c1fc23c2f67c3714c64011a6245bfcf8d` |
| Unguided author's actual PRD | `858fef0b9e791b4bd1e719aa8aed556ee28c47e4053ed4a5c02c9e69ee4537a0` |
| Guided author's actual PRD | `a0ac73b2da457b45ea84537004946171f34ff46a77a9f4a890a80b84c03136f0` |

## Supplemental checks after PR review

[PR71 review](https://github.com/dstkwll/atlas/pull/71#discussion_r4577703407) found a gap in the frozen twelve probes: a comparator that checks recursive types, keys and list lengths but ignores scalar values passes all twelve. The primary reproduced this false positive. Such a repair would lose the original observers' ability to detect a same-type value mutation, such as incrementing an identifier.

Four separate [supplemental probes](../../evals/conflict_value_checks.py) now increment integer identifiers after saving the valid output, on both normal and exception paths in both observers. Empty inputs remain preserved; populated inputs must be reported as mutated. A regression control demonstrates that the type-only comparator passes the original twelve but fails all four supplemental probes. Both the original historical observers and current repaired observers pass these value checks, establishing the retained behavior that the incomplete comparator loses.

The primary rechecked the exact two saved recipient implementations in separate processes after verifying their code hashes against the original acceptance records. Both passed **4/4 supplemental probes**. No additional native author or consumer ran, and neither implementation was edited. Original acceptance records and all frozen evaluator identities remain unchanged; new source-bound supplemental receipts are retained separately. These post-review observations are not part of the original twelve-probe result. The supplemental checker SHA-256 is `897e4f58a9856c171417c6bbc90a05d61e3a388be98fb53926e12f90368591c7`. The expanded evaluator suite passes **77 tests**. Opus 5.5/high independently reviewed the supplemental source and found no material defect; its wording feedback narrowed the stated coverage to top-level integer identifiers. Same-type string or nested-value changes remain outside these four probes.

The case is developer-exposed and uses one author/recipient pair per condition. Host/model variation, larger repository discovery, ticket/handoff variants and general reliability remain untested. The later [evidence-attribution follow-up](evidence-attribution.md) preserved the original artifacts and results and tested an explicit clarification; it improved file attribution while leaving an inline-check gap in one clarified note. This observation alone does not justify new mandatory runbook steps or infrastructure. [Issue66](https://github.com/dstkwll/atlas/issues/66) remains open.
