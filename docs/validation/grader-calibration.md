# Grader calibration and the Atlas evaluation entry

November 14, 2026. This slice adds a portable calibration method, an offline review audit and `atlas-to-eval`, a thin companion to standalone Satchel `to-eval`. It continues [evaluation authoring](evaluation-authoring.md) and [initiative #66](https://github.com/dstkwll/atlas/issues/66). Satchel's source and version are unchanged.

## What was exercised

Five native Codex 0.153.4 trials used `gpt-5.6-sol`, low effort, one attempt per condition, with a 300-second limit per attempt. Four were selected before execution: the eight-control review with Atlas and without guidance, the new entry's outbox-design task, and the entry with its shared Atlas dependency removed. One explicit calibration-method probe followed an observed routing miss; it supplements rather than replaces that result. All five completed, their tool capture parsed without errors, and the temporary hosts and credential homes were cleaned up.

The package bytes captured for every trial match this candidate. Raw metadata retains candidate, staged-guidance and runner hashes; final offline audits were rerun with pinned control and reviewer-packet identities after audit repairs. The control source SHA-256 is `ec92163e62ffb68f90d589889b4f610082ce3bd135c76d4efd73c199ed2a0132`. These are exposed synthetic development controls, not a held-out benchmark or independently established human gold standard.

| Trial | Observed result | Limit |
| --- | --- | --- |
| Eight controls, Atlas guided | All eight reference labels matched; primary inspection found reasons supported by supplied evidence. Only planning output changed. | Selected the general independent-review method, without reading grader-calibration. This is a method-selection miss, not evidence of applying the new method. |
| Same controls, unguided | All eight labels matched with supported reasons; only planning output changed. | Baseline parity prevents claiming an improvement from Atlas. |
| Explicit grader-calibration probe | Read the new method and produced eight matching, supported judgments. | Direct prompting establishes application under that condition, not natural routing or general accuracy. |
| atlas-to-eval, outbox design | Read the entry, shared lead and evaluation-design method; saved a plan without executing or editing the tool. Included total-count and extra-item failures and the endpoint/operation-order distinction. | The generated plan still has inconsistent malformed-evidence handling, described below. |
| atlas-to-eval, missing shared lead | Observed the absent dependency, reported that the entry could not run faithfully, and left project state unchanged. | One synthetic missing-dependency trial; no broader host compatibility claim. |

The control judgments separate a complete but unfinished delivered answer (`FAIL`) from the same prefix with independently declared capture loss (`UNKNOWN`). They retain a visible unsupported claim despite lost tail bytes, reject an unauthorized extra item, distinguish final state from operation-order proof, accept a faithful paraphrase and mark an absent unguided skill requirement inapplicable. Recorder status is supplied synthetic evidence here; no actual recorder-loss fault was injected.

## Remaining artifact defect

The outbox plan first says a malformed or missing required file fails unless setup evidence explains its absence. Its later grader-control section groups unavailable and malformed state together as unknown/setup error. A consumer could inherit either rule. This is a real inconsistency retained for further spec-consumer work; the useful entry behavior does not make its entire generated plan reliable. The plan was not executed and its proposed 30-attempt pilot was not run.

## Audit assurance and limits

The offline [calibration utility](../../evals/calibration.md) exports only reviewer-visible fields, detects missing/duplicate/unknown judgments and unresolved evidence references, retains submitted rows, and compares labels with declared expectations. Optional identity guards reject changed control sources or reviewer-visible packets. They do not prove what an external reviewer saw unless the caller preserves and supplies the expected identities.

All 55 evaluator unit tests pass, including ten calibration tests covering withholding reference fields, fixture contents, malformed submissions, conflicting rows, identity drift and exit statuses. All 105 registered cases preflight in both conditions. These are mechanical checks. A deliberately irrelevant rationale with a real citation and matching label still passes the label audit; the report explicitly requires semantic review.

Opus 5.5/high independently reviewed the source and found the eight reference judgments defensible. Primary verification led to retaining duplicate/unknown row contents, adding optional identity guards and clarifying input-shape errors. Suggested leakage and fixture-key blockers were not present in the actual staged fixture or registry; those were checked directly. A fresh Codex reviewer inspected the repairs and integration, found no concrete defects, and independently passed the nine focused tests. That reviewer did not inspect native trial artifacts; native semantic judgments above are primary review. The controls remain authored development expectations, with model review, rather than human-adjudicated reference truth.

Natural calibration routing, broader case families, repeated observations, other hosts and fresh downstream consumers remain open. No broad accuracy, reliability or superiority claim follows from these trials. No global installation or release was performed.

Before merge, GitHub review exposed duplicate JSON object members being silently overwritten by decoding. A regression test reproduced false agreement for duplicate verdict fields and duplicate judgments lists, plus an ambiguous control source. The decoder now rejects duplicate members in both inputs with exit 2; all ten calibration tests and the full 55-test suite pass. Native actor inputs and package guidance were unchanged by this audit-only correction.
