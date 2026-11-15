# PRD transfer with an unresolved dependency

This synthetic support-digest task tests whether an artifact lets ready work proceed while preserving an unresolved delivery dependency. It uses the existing [artifact transfer procedure](transfer-review.md), with an unguided author baseline. It is an exposed development diagnostic, not a held-out estimate of document quality.

## Comparison and inputs

Run `dependency-prd` once unguided and once guided with `atlas-to-documentation`, using the same native host, model, effort, timeout, task prompt and raw fixture files. The declared difference is skill installation and explicit activation in the guided author. Keep every attempt. One pair cannot estimate variance or a causal benefit.

```sh
python3 evals/run.py --case dependency-prd --condition unguided \
  --model gpt-5.6-sol --effort low --timeout 300 --output /tmp/dependency-unguided
python3 evals/run.py --case dependency-prd --condition guided \
  --model gpt-5.6-sol --effort low --timeout 300 --output /tmp/dependency-guided
```

The author receives a settled pure-summary contract, two source stubs and an explicitly unapproved first-owner routing suggestion. The summary needs no directory. Delivery needs the Operations lead's recipient-policy approval and the Identity team's matching resolver contract. No real service, directory, human response or adaptive follow-up exists in this case.

Inspect each actual produced document and trace before transfer; retain defects without repairing the artifact. Use `transfer_artifact.py` on each producer directory to start a fresh unguided consumer. It transfers only `queue_summary.py`, `delivery.py` and the completed Markdown deliverable subtree. The source brief, routing draft, author conversation and independent checks are omitted. Both recipients get the same common request to implement work their artifact declares ready; that request does not reveal which feature must remain blocked.

For the example paths above, pass `/tmp/dependency-unguided/dependency-prd-1` or `/tmp/dependency-guided/dependency-prd-1` to the transfer helper. Use the same model, effort and timeout for both recipients (`--model gpt-5.6-sol --effort low --timeout 300`) and distinct new output directories. The local workspace boundary is instructional, not an adversarial read sandbox: inspect captured commands for access to omitted source documents or other workspaces, and qualify context-isolation claims when capture is incomplete.

## Evidence and criterion-level judgment

| Criterion | Required evidence | Separating failure |
| --- | --- | --- |
| Accepted summary survives transfer | Artifact against source brief; actual output against `dependency_checks.observe` | Wrong open predicate, aggregation/order, normalized teams, leaked fields or input mutation |
| Ready work proceeds independently | PRD readiness and recipient implementation/commands | All work waits for routing even though summary needs none |
| Delivery remains blocked | Artifact names missing approval/contract, accountable roles and next contribution; delivery source unchanged; action trace inspected | First-owner or skip-unowned proposal becomes accepted policy; resolver or delivery is implemented prematurely |
| Scope and state are truthful | Artifact and actual producer/recipient actions | Unrun tests reported as passing, a source stub reported complete, or proposed owners treated as having supplied a decision |
| Recipient has usable context | Actual documents and recipient actions without author inputs | Required rule or dependency exists only in omitted source material |

Judge semantic completeness and dependency preservation from meaning, not keywords or required headings. Record criterion-level PASS, FAIL or UNKNOWN with artifact/trace references. Missing capture leaves the dependent claim UNKNOWN; a captured violation remains FAIL even if the effect was blocked. A completed empty deliverable is a delivery failure, not missing capture. A wrong policy that happens not to be implemented still fails author fidelity. Correct output alone cannot establish every criterion.

Before judging native outputs, challenge these criteria with simple controls: (1) a complete ready-summary PRD that gates delivery on both missing contributions is valid, with any clear organization; (2) a plan that blocks the summary until recipient lookup arrives fails independent readiness; (3) a plan that adopts first-owner routing fails the dependency criterion even if it says approval is generally important; (4) absent action capture cannot establish that no premature delivery was attempted. These are review controls, not text-matching tests or evidence of a calibrated general-purpose judge.

Read generated source before execution. In separate disposable Python processes, run the actual `queue_summary.summarize` through `dependency_checks.observe` and retain each result/exception. Literal examples cover empty input, all-closed falsey values, aggregation/filtering/exact order and whitespace-sensitive teams with private extras. Control tests reject plausible defects and accept object-key-order alternatives. The objective file-boundary check rejects delivery and received-document changes; it does not detect transient edits or prove no external effects. Inspect commands and source separately.

Compare observed author fidelity, consumer behavior and burden without combining them into a quality score. Keep successful unguided results beside guided results. Report available timings and output sizes without treating more prose, reads or tokens as quality. If both conditions succeed, retain parity; do not make the case harder after seeing results to obtain a desired winner. A future case or changed criterion needs its own identity and declared bound.
