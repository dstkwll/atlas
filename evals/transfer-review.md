# Evaluate PRDs, tickets and handoffs through implementation

These development diagnostics ask whether a fresh recipient can use an artifact to perform a bounded software task. They extend the [outbox consumer checks](artifact-consumer-review.md) beyond evaluation specifications. Their fixtures and controls are exposed to maintainers, not held out.

See the [first native observations and limits](../docs/validation/artifact-transfer.md).

## Author and recipient have different inputs

`transfer-prd` and `transfer-tickets` receive accepted requirements and two current source files for a small CSV export. `transfer-handoff` receives a partially completed implementation and a narrow recovery boundary: repair numeric tie ordering only. Each uses its explicit Atlas entry and must write Markdown under `planning/deliverable/`, without implementing or editing code.

The task deliberately distinguishes accepted work from undecided future policy: exporting opaque due-date strings needs no overdue, timezone or reminder decision. The record contract includes a representative instance and legitimate extra fields; output must preserve its declared columns without exporting private source fields. The handoff must use actual code rather than a stale claim that sorting was fixed.

Inspect the producer's exact files and trace before transfer. A missing artifact, contradictory requirement, inaccurate readiness claim or unauthorized source edit remains a finding. Do not repair the artifact before handing it to the recipient. The small helper rejects unsuccessful producers and changed source files; it does not judge semantic completeness or turn a completed run into a passing authoring evaluation.

```sh
python3 evals/transfer_artifact.py /path/to/transfer-prd-1 --preview
python3 evals/transfer_artifact.py /path/to/transfer-prd-1 \
  --model gpt-5.6-sol --effort low --timeout 300 --output /tmp/prd-consumer
```

Use a model available to the authenticated native host. Preview performs no inference. Execution starts a separate unguided native thread through the existing runner. The packet contains only the exact nonempty Markdown deliverable subtree and unchanged `loans.py`/`csv_export.py`, plus the runner's local operating constraints and a common implementation request. It omits the original brief, author conversation, other planning notes, hidden checks and installed guidance. Markdown remains at its original `planning/deliverable/` paths, including nested documents, and must match the producer completion snapshot. Symlinks and non-Markdown deliverable files are refused. The transfer is a narrow local fixture adapter, not an adversarial filesystem sandbox, document sanitizer or general execution service. Review the selected producer directory before use.

`transfer-source.json` records the selected producer and hashes of every transferred file. Native metadata also retains actual staged file identities, model, condition and capture status. Preserve all attempts and bind observations to their source versions. A later correction requires a separately identified packet; do not overwrite an earlier adverse result.

## Judge what the artifact enabled

Read generated implementation code before executing it under existing local authority. In a disposable environment, import the actual `csv_export.export_csv` and apply `transfer_checks.observe`; retain every result or exception. The checker uses literal task-derived expected rows, accepts standard CSV line endings and checks input preservation. Its controls cover empty/all-returned exports, active filtering, numeric tie order, opaque and blank due dates, quoted fields and exact output columns. Checker unit tests challenge plausible incorrect outputs and mutation. These limited checks do not establish all inputs, performance, absence of external effects or useful human comprehension.

Inspect actual changes and commands separately. The consumer may edit `csv_export.py`, tests and planning; it must preserve `loans.py`, received artifacts and runner guidance. Standard pytest caches and test configuration are permitted test outputs. A handoff consumer must also respect its narrower repair scope. Passing output checks does not prove that scope or prove that all guidance was read.

Review the producer artifact against the original accepted brief after consumer execution. Separate author fidelity, recipient fidelity, independently checked task behavior and unresolved product decisions. A recipient can faithfully inherit a missing or wrong requirement. Conversely, a useful implementation can succeed from current code despite an inadequate handoff. Do not credit artifact quality solely because tests pass.

Compare condition identities and burden honestly. One producer and one consumer for each artifact type is a diagnostic application, not a ranking of artifact formats or evidence that Atlas outperforms an unguided author. Retain failures and successful baselines, and use different task families before making broader claims.

## Schema-aware outbox follow-up

`artifact-consumer-schema` adds a legitimate contract and representative record to the earlier partially clarified packet. It explicitly allows metadata keys such as `id`; extra object keys are distinct from extra outbox items. Evaluate against the original seven frozen vectors, preserving the earlier consumer code/results. This tests the missing-context hypothesis on an exposed case. It retains the earlier packet's coarse unavailable-capture behavior and is not a complete general-purpose grader.
