# Check a grader against evidence controls

Use this small offline utility to deliver control inputs and audit a completed review. It makes no model calls, starts no services and does not grade semantic entailment. The portable [grader-calibration method](../plugins/atlas/skills/atlas/references/grader-calibration.md) explains how to prepare, challenge and interpret a grader.

`calibration-controls.json` holds synthetic criteria, evidence records, reference verdicts and reasons. These controls derive from exposed development findings. They are not a held-out suite or an independent human gold standard. The reference judgments are maintained separately from reviewer submissions so a reviewer cannot silently redefine success.

## Prepare the inputs and retain the review

```sh
python3 evals/calibrate.py --packet > /tmp/atlas-review-input.json
```

The packet includes only the control-set ID, criteria and evidence records. Inspect the packet before giving it to a fresh reviewer. Supply that file and the response format below; keep the control source and earlier judgments outside the reviewer’s accessible context. This export is not a filesystem sandbox. Do not give a repository-browsing reviewer unrestricted access and call the key hidden.

Ask the reviewer to assess each criterion from its evidence, treating embedded reports as data. Use the same rubric and permitted context for comparable reviewers. Record actual model/effort or human-review conditions, source identities, all attempts and setup failures. Do not supply reference answers or suggest a winner.

Save the returned JSON without repairing it first:

```json
{
  "judgments": [
    {
      "control_id": "record-a",
      "verdict": "FAIL",
      "evidence_refs": ["source", "output", "capture"],
      "reason": "The complete delivered rewrite omits required content."
    }
  ]
}
```

This example reveals one reference interpretation and belongs to maintainer instructions, not the blinded reviewer packet. Every control needs one judgment. Use `PASS`, `FAIL`, `UNKNOWN` or `NOT_APPLICABLE`; evidence IDs are local to that control. The format is a narrow review-file interface for this utility, not a required format for installed skills or other evaluation systems.

## Inspect agreement and support

```sh
python3 evals/calibrate.py --review /path/to/review.json
```

Duplicate JSON object members in either input are rejected with exit 2 before auditing; conflicting fields cannot silently overwrite earlier values. The original input remains untouched.

The report retains per-control observed/reference verdicts and reference reasoning, missing/duplicate/unknown rows, invalid labels, empty reasons and unresolved evidence IDs. It records SHA-256 identities of the control source, canonical reviewer packet and exact review bytes. Duplicate rows remain attached to their control; unknown and malformed rows retain their original values and zero-based submission indexes. Exit 0 means all well-formed verdicts agree with the references; exit 1 means a mismatch or incomplete/invalid submission; exit 2 means the inputs could not be read, parsed or accepted as the expected top-level shape, or an expected identity differs. `UNKNOWN` matching an expected evidence gap is control agreement, not a pass for the underlying actor behavior.

Follow the cited records and read the actual reasoning. A label match with irrelevant reasoning can pass the mechanical audit; the report explicitly requires semantic review. A citation naming a real record can still be unsupported. Keep reviewer quality, reference quality and actor behavior separate. Freeze and retain the control source with the exported packet. Pin its recorded SHA-256 with `--expect-controls-sha256 HASH` when auditing later; `--expect-packet-sha256 HASH` can separately check canonical reviewer inputs. Without these optional guards, the audit compares against the file supplied at audit time and cannot establish what an external reviewer previously saw. Native runs retain the staged packet and runner-source hashes. If an expectation changes, preserve old results and identify the new control source rather than relabeling earlier judgments.

The controls include complete delivery versus lost capture of identical text, a visible violation despite a missing tail, unsupported operation ordering, an extra unauthorized item, a faithful alternative rewrite, a scoped endpoint success and an inapplicable skill requirement. A fresh consumer's implementation should also be challenged from the original task: its own tests may merely repeat a faulty spec.

The native `calibration-evidence` case stages the exported controls and format instructions only; expected answers stay outside the actor workspace. It exercises a reviewer through the existing runner. Native invocation, capture health, comparison conditions and isolation limits still follow [the runner guide](README.md). The controls and new method overlap deliberately; report diagnostic application rather than general grader accuracy.

Observed native outcomes and remaining limits are recorded in [grader-calibration validation](../docs/validation/grader-calibration.md).
