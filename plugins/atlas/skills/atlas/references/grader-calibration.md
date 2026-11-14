# Calibrate an evaluation's judgment

Use when deciding whether a human rubric, model judge or program can distinguish the outcomes an evaluation relies on, or when verdicts conflict with observable evidence. [Evaluation design](evaluation-design.md) establishes the task and intended claim; this method tests the measurement. Use existing project tools and the smallest set of controls that exposes the relevant distinctions.

## Establish the reference judgment

Start with a material requirement and the actual evidence it needs. State the criterion narrowly enough to judge: final state, operation ordering, semantic preservation and authorization are different claims even when they concern one task. Retain unresolved product expectations instead of turning a reviewer's preference into policy.

Prepare a known defect, a correct result and a materially different valid alternative. Add an evidence-gap control where the observation can be missing. Change one consequential fact between paired controls when that exposes the cause of a verdict. Freeze expected judgments and reasons before the reviewer sees the cases. Distinguish independently reviewed references from author-proposed expectations; disagreement may reveal a faulty reference.

For example, the same unfinished text means different things when the recorder captured the complete delivered answer and when it independently reports losing the remainder. The first can establish an omission; the second leaves dependent claims unknown. For a required JSON export, complete captured invalid bytes establish a format failure; a collector-lost suffix leaves validity unknown unless the faithful prefix already establishes a syntax violation that no suffix can repair. A trusted complete inventory of the required location at the judged time can establish that a required file is absent. Pair these controls, and reconcile the main rubric with its examples before a consumer implements either rule. An intact unsupported claim still fails even when later capture is missing. A confident actor explanation is not independent evidence that capture failed.

Check the whole requirement. Exactly one requested record can coexist with an unauthorized extra record. Counting the target alone may pass a narrower fact while failing the task. Keep those failures visible in the acceptance decision. Conversely, missing operation history does not prevent judging a complete final-state criterion that does not require that history.

## Run the reviewer without the answer key

Give the reviewer the criterion and permitted evidence, with stable references it can cite. Keep expected verdicts, reference reasons, condition identities when blinding matters, and earlier feedback outside its inputs. Audit nested copied resources. Preserve enough context to avoid manufacturing ambiguity, while avoiding annotations that reveal the desired label.

Request a scoped judgment, supporting evidence and reasoning. Use the project's existing result format. Missing evidence is unknown; a criterion that does not apply is different. If evidence is partial, grade what it actually establishes rather than assigning one blanket unknown or pass to the whole artifact. Do not demand a preferred phrase or tool sequence when different approaches satisfy the requirement.

Inspect both label and reasoning. A valid evidence identifier proves only that the reference exists. The cited content must support the conclusion, apply to the tested candidate, and establish the claimed effect. Matching the expected label with an invented rationale is not a calibrated judgment. Preserve contradictory evidence and unresolved disagreement.

## Diagnose disagreement and limit the conclusion

Separate input/setup failure, unavailable evidence, ambiguous requirements, flawed reference expectations and reviewer error. Reproduce a program's false acceptance or rejection with the smallest relevant input. For an artifact-derived grader, let a fresh consumer implement the spec, then challenge it with controls derived independently from the original task. Tests that merely reproduce the spec can inherit its mistake.

Repair the layer responsible for the defect. A missing observation may need better capture; an ambiguous rubric needs a clearer criterion; a wrong reference needs corrected adjudication. Do not add agent instructions automatically when the measurement is wrong. Record changes to controls, reference judgments and reviewer guidance so earlier results remain attributable to their actual versions.

After a material change, rerun affected controls and a valid alternative. Predeclare additional variation or repetition when it matters to the decision; avoid coaching on a fixed answer key until it passes. Exposed controls remain useful regression checks, but further agreement on them is not held-out evidence. Use different case families or independent reference reviewers before making broader accuracy claims.

Return criterion-level matches, disagreements, missing/invalid judgments, evidence references and adjudication status. Retain every attempted review and available cost/burden measurements. State which controls were prepared, applied, checked or independently adjudicated. Control agreement is evidence about the reviewer on those cases; it does not establish actor quality, general judge accuracy or release authority. A calibration plan does not authorize model calls, publication or recurring execution beyond the existing assignment.
