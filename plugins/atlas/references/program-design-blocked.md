# Program Design blocked response

Use this runbook for an **ordinary repository dependency `BLOCKED`**, a producer pre-readiness **true upstream `DESIGN_BLOCKED`**, or `DESIGN_BLOCKED` **reviewer evidence**. It classifies and preserves a non-mutating stop; it does not turn a local dependency into an authority question.

## 1. Identify the branch

- **Repository dependency:** missing binding/source, noncanonical or unavailable baseline/object, unreadable tree/blob, or required submodule/LFS content is mechanical `BLOCKED`. No candidate readiness or review evidence is created.
- **Producer pre-readiness:** an exact baseline was readable, but exact code contradicts accepted upstream truth and realization requires that truth to change. Capture structured `upstream_source`, `upstream_issue`, `resume_boundary`, and `resume_action` in the operator report only.
- **Reviewer evidence:** keep the exact fresh `reviews/program-design-v1.json`; its one `DESIGN_BLOCKED` gap is evidence, not authority. Do not call `advance`.
- **Local code-shape defect:** this is `BLOCKED`, not `DESIGN_BLOCKED`; return it to the Program Design producer for candidate-only repair.

## 2. Prove the stop is non-mutating

Re-read authoritative state and verify `planning-control.json` remains `PENDING` at phase `program_design` with the same revision. `PENDING` means no acceptance was written; it does not encode either failure classification. Verify `run.yaml`, `control.json`, selected upstream source, and any pre-existing candidate/review bytes are unchanged. A producer pre-readiness stop leaves no new `40-program-design.md` or review file.

If the **frozen repository baseline cannot be located and read**, return ordinary mechanical `BLOCKED` before candidate readiness. Current `HEAD`, index, and working-tree bytes may describe drift but cannot replace the exact baseline.

Resume a missing local dependency through `setup-atlas` or an offline repository repair, then rerun `atlas_repository.py verify`; this requires no authority decision or reopen. Atlas itself performs no clone, fetch, authentication, checkout, worktree, submodule/LFS hydration, or repository mutation.

An abbreviated baseline may be corrected only through the accepted repository-intake correction while Discovery owns the cursor. If Discovery no longer owns the cursor, an abbreviated baseline requires a corrected new run; downstream code never silently expands it.

## 3. Name the smallest authority decision for true DESIGN_BLOCKED

Only after exact baseline inspection proves an accepted upstream contradiction, report the exact selected `upstream_source`, conflicting or missing commitment, source-constrained `resume_boundary`, and smallest accepted-truth change needed. Never route to an omitted stage. `resume_boundary` classifies the selected source that would have to become current again; it is not permission to edit that artifact and does not decide where a future repository binding lives.

Current V1 has **no supported reopen or replacement-acceptance path** for accepted System Design or Program Design. This runbook does not authorize editing upstream artifacts, either control file, or review evidence. The shared intake-correction procedure applies only while Discovery owns the cursor and proves repository identity/baseline intake wrong; it is not a downstream reopen mechanism. Do not prescribe a `run.yaml` field, Stage 0 amendment/effective-configuration field, absolute artifact path, registry schema, clone/fetch behavior, or new controller.

## 4. Completion report

Return:

1. origin: repository preflight, producer, or reviewer;
2. exact immutable source and current hashes;
3. local `BLOCKED` versus upstream `DESIGN_BLOCKED` classification;
4. complete repository gaps/resume actions when mechanical `BLOCKED`;
5. proven non-mutation results; and
6. for true `DESIGN_BLOCKED` only, the smallest unresolved authority decision.
