# Artifact failure, evidence loss and fresh consumers

November 14, 2026. This follows the [calibration slice](grader-calibration.md) merged in #67 and continues [initiative #66](https://github.com/dstkwll/atlas/issues/66). It clarifies existing Atlas and standalone Satchel evaluation guidance and adds exposed diagnostics. It does not add a runtime or install either package globally.

A complete artifact that violates a required format is an observed failure. A collector that lost bytes may leave a dependent claim unknown, while an intact violation in a faithful prefix can still establish failure. A trusted inventory establishes absence only for the required location at the judged time. These distinctions now appear in evaluation design, grader calibration and standalone `to-eval`.

## What the consumer actually did

The preceding native outbox plan contained conflicting rules: its main rubric failed malformed required JSON, while a later grader control grouped malformed and unavailable evidence as unknown/setup error. Two fresh, unguided native Codex sessions received minimized plan excerpts and the same small final-state checker interface. One excerpt retained the conflict; the other partially clarified the evidence rules. Seven task-derived vectors were frozen and withheld before either consumer ran.

The primary inspected the exact generated code, then executed the frozen vectors against each unmodified implementation. Both consumers' own smoke checks had passed. Independent execution showed:

| Input / expected verdict | Original-plan consumer | Partially clarified-plan consumer |
| --- | --- | --- |
| Complete malformed JSON / FAIL | UNKNOWN, explicitly citing the conflicting rules | FAIL |
| Same prefix after unavailable full capture / UNKNOWN | UNKNOWN | UNKNOWN |
| Exact valid item with its normal id field / PASS | PASS | UNKNOWN |
| Complete wrong root shape / FAIL | FAIL | FAIL |
| Trusted inventory proves required file absent / FAIL | FAIL | FAIL |
| Target plus unauthorized extra item / FAIL | FAIL | FAIL |
| Equivalent valid key order and whitespace / PASS | PASS | UNKNOWN |

The first consumer exposed the specification conflict rather than silently choosing a policy. That is faithful consumption, but it cannot supply the authoritative task's FAIL judgment for malformed output. The second consumer implemented that boundary correctly but treated additional object keys as unresolved because the partial clarification introduced “item shape” without defining allowed fields. Its notes and code identify that ambiguity. The minimized packet also omitted the original tool's concrete output schema; the `id` field came from task-derived expectations outside the consumer's context. This is an artifact/context sufficiency problem, not evidence that the consumer should guess a schema.

The partial clarification therefore did not produce a fully usable checker. The two additional UNKNOWN results remain visible beside the repaired boundary. These single consumers do not establish a causal effect or general reliability. The conditions differ in their conflict, added provenance/checklist wording and setup-error phrasing; the experiment does not isolate each difference. Neither the old source artifact nor either generated consumer was rewritten to make the checks pass.

The retained [consumer fixtures and review guide](../../evals/artifact-consumer-review.md) are diagnostic material, not a finished grader to adopt. In particular, the partial clarification also treats unavailable capture too broadly: it does not cover a faithfully captured prefix that already proves a violation. That later source-review finding is preserved separately from the seven frozen vectors.

## Control and source review

The initial twelve-control `evidence-boundaries-v2` set retained all original eight controls unchanged and added complete malformed output, lost collection, wrong root shape and verified absence. Native Atlas and standalone Satchel reviewers each matched all twelve reference labels. Primary semantic review found the format/capture judgments supported, but later independent review identified ambiguity in the absence criterion: “By completion, the agent created…” could describe history, whereas a final inventory only establishes final presence. Its matching labels therefore were not sufficient reference validation.

Opus 5.5/high independently reviewed the source, minimized plans and controls. It identified that criterion ambiguity, the too-broad missing-suffix rule, missing inventory scope qualifiers and the item-shape confound. The primary verified those findings. Final `evidence-boundaries-v3` asks directly whether the file exists at completion and adds a thirteenth control whose faithful JSON prefix is already irreparably invalid. The final portable guidance retains observed violations despite missing later bytes and scopes inventories to trusted location/time evidence. Earlier v2 artifacts and audits remain bound to their original source; they are not relabeled as v3 coverage.

## Conditions and limits

The initial four trials used native Codex 0.153.4, `gpt-5.6-sol`, low effort, one attempt per case and a 300-second limit. Both consumer cases were unguided. The Atlas reviewer selected the existing general independent-review method; it did not read the revised evaluation/calibration references. The Satchel reviewer read its explicitly selected `to-eval` skill, with no Atlas or sibling skill installed. All four completed with parsed tool capture, preserved source/guidance and changes restricted to planning. Reviewed commands showed no outside-project or external operations.

A fifth, separately declared Satchel trial completed after review corrections, read the final standalone skill and matched all thirteen v3 references. Primary inspection found the reasons supported by the supplied records, including the final-presence criterion and irreparably invalid prefix. It preserved inputs and guidance, changed only planning output, and its tool capture parsed without errors. The v3 control-source SHA-256 is `d7db333b860e7625c0c24af34e98200f8187ccfe23a2fbecc1f3dbe89599d5b9`. Source hashes, staged packets, all attempts, original artifacts, audit reports and consumer-code identities are retained in maintainer evidence. There is no untouched baseline for the guidance clarification, no realistic collector fault injection and no human reference study. Native use of the final Atlas wording remains unverified; source review and a Satchel observation cannot establish that behavior.

A fresh Codex reviewer independently inspected the final source, controls, fixture staging and version alignment, found no blockers, and passed all 55 tests. That review did not inspect the private native traces; the native behavioral interpretation remains primary review.

All 55 evaluator unit tests pass, including duplicate-key input rejection retained from the #67 merge correction. All 108 registered cases preflight in guided and unguided conditions. Mechanical coverage, control agreement, source use and useful downstream behavior remain separate claims.

Next evidence should carry a representative valid schema instance into a fresh consumer, keep invalid and valid-alternative cases independent of its own tests, and extend beyond outbox graders to PRDs, tickets and handoffs. Avoid repairing only the failing example until a favored artifact passes.
