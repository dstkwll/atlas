# Evidence-attribution clarification diagnostic

This follow-up asks whether a short task-level clarification closes the missing source linkage observed in the [real-conflict replay](../docs/validation/real-evidence-conflict.md). It does not change Atlas or Satchel guidance. Retain the two actual historical PRDs, their original attempts and acceptance receipts. Each supplies a fresh matched pair: the unchanged artifact and the same artifact plus [this addendum](attribution-addendum.md). All four recipients are unguided. The historical authors' guidance conditions identify artifact provenance; they are not the new intervention.

Use `transfer_artifact.py PRODUCER --preview` for the original packet and add `--evidence-attribution` for the clarified packet. The flag is restricted to `conflict-prd`; it adds `planning/deliverable/evidence-attribution.md` only after verifying the original inventory and hashes, and never overwrites an original document. Review the exact staged bytes before execution. The common consumer prompt, original code/evidence and PRD remain identical within each pair. The new manifest records the addendum's identity and whether the intervention was selected. Original reports, incident, author conversation and primary acceptance checks remain excluded.

Bound the initial comparison to four native attempts: one unchanged and one clarified recipient per historical PRD, on the same available model, effort and 300-second limit. Retain all failures, no replacements. Record requested and returned settings. Verify every staged manifest against the frozen preview hashes, including the addendum, before grading; read the source bytes as well as the hash-only preview. Freeze staging, addendum, rubric and control judgments before execution. Alternate the order across pairs to reduce a simple order confound, and report actual scheduling. One attempt per cell, on one exposed task, cannot establish causality or general reliability. The same added requirement changes task specificity; this is not a comparison of skill packages.

## Review distinct claims

Inspect the full record and captured actions; a hash-looking string or a successful process exit is insufficient. Give criterion-level PASS, FAIL or UNKNOWN with evidence pointers, and keep the original behavior checks separate.

| Claim | Evidence needed |
| --- | --- |
| A reader can identify the tested project sources | Reported identities resolve to the relevant observer, implementation, fixture/check runner and helper bytes; inline test code can be identified by the recorded command itself. No helper is required if the repair has none. |
| Those sources apply to the reported results | Captured execution and edit/hash sequence connect each result to those bytes. A later relevant edit without a rerun invalidates a claim about the final version; a clearly labelled historical result can still be true. |
| Execution claims are honest | The named command reaches the claimed check and its actual result agrees with the note. Expectations, failed attempts and historical results are distinguished. |
| Repair and boundaries survive | Inspect actual code, run the original twelve plus four supplemental behavior probes separately, and verify original evidence, examples and received documents remain intact. |

Assess actor-authored source linkage separately from operator evidence: the harness's own snapshots can verify what ran but cannot fill a missing link in the delivered note. A completely captured note omitting required sources fails note linkage. A trusted complete final inventory showing no required note, or a faithfully captured unfinished note that omits the linkage, also fails that delivered-artifact criterion, including after a timeout. Collection loss that prevents inspection leaves only the affected criteria UNKNOWN. Missing command capture leaves execution applicability and honesty UNKNOWN; it does not erase a verified omission in the note. A captured contradiction remains FAIL despite an unrelated missing tail. Do not require a specific filename, hash algorithm, JSON schema or a hash of the note containing itself. Git revision evidence is valid only when it covers the relevant working tree, including new or modified helpers, fixtures and checks. Relevant sources include each observer/check executed, the saved example implementations it exercises, embedded fixtures or separate fixture files, the runner (such as smoke.py or the exact inline command), and any helper actually used. Original receipts need identity when a new claim relies on their contents; merely retaining them is checked separately. Runtime/environment details matter when needed for the claim; this bounded task does not require a lockfile or the identity of every standard-library file.

## Semantic controls

These are stipulated small review controls, not native trial outcomes or an automatic grader. Judge the source-attribution and execution columns separately before reviewing actual outputs.

| Control packet | Note linkage | Version actually executed (operator evidence) | Execution honesty | Reason |
| --- | --- | --- | --- | --- |
| Note gives commands and correct counts but omits repaired checker/helper identities; capture establishes exact code and real execution | FAIL | PASS | PASS | Operator evidence cannot fill missing linkage in the note. |
| Note lists matching checks/implementation/fixture/helper hashes and commands; capture confirms those bytes and matching results | PASS | PASS | PASS | Artifact and execution evidence agree. |
| Note identifies a clean fully tracked revision covering all relevant sources; capture verifies that tree and results | PASS | PASS | PASS | Valid alternative to per-file hashes. |
| Note gives HEAD while a relevant helper is untracked; capture identifies the helper bytes used and confirms the stated result | FAIL | PASS | PASS | The note lacks identity for a relevant dependency, even though the operator can recover it. |
| Note gives matching final-file identities and claims final-code results; capture shows a helper changed after the only test run | PASS | FAIL | FAIL | Final identities are inspectable, but the claim that those bytes were tested is contradicted. |
| Complete note and matching final hashes supply source linkage, but command capture is unavailable | PASS | UNKNOWN | UNKNOWN | Delivered linkage exists; its execution applicability cannot be verified. |
| Note identifies the executed sources and claims a named test passed; capture identifies those bytes and shows that test failed; later capture is missing | PASS | PASS | FAIL | An observed contradiction is retained despite unrelated missing evidence. |


Track unnecessary scope changes, report size, elapsed time and actual method use alongside outcomes. If both originals now succeed, retain that variability rather than crediting the addendum with the historical difference. If the addendum helps, recommend another task or a narrowly justified guidance change; do not infer a mandatory reporting system from one diagnostic.
