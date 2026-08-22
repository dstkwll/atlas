# Program Design blocked response

Use this runbook for either a **producer pre-readiness** `DESIGN_BLOCKED` result or `DESIGN_BLOCKED` **reviewer evidence**. It classifies and preserves a stop; it does not reopen an accepted boundary or invent repository access.

## 1. Identify the branch

- **Producer pre-readiness:** no candidate readiness or review evidence is created. Capture the structured `upstream_source`, `upstream_issue`, `resume_boundary`, and `resume_action` in the operator report only.
- **Reviewer evidence:** keep the exact fresh `reviews/program-design-v1.json`; its one `DESIGN_BLOCKED` gap is evidence, not authority. Do not call `advance`.
- **Local code-shape defect:** this is `BLOCKED`, not `DESIGN_BLOCKED`; return it to the Program Design producer for candidate-only repair.

## 2. Prove the stop is non-mutating

Re-read authoritative state and verify `planning-control.json` remains `PENDING` at phase `program_design` with the same revision. Verify `run.yaml`, `control.json`, selected upstream source, and any pre-existing candidate/review bytes are unchanged. A producer pre-readiness stop leaves no new `40-program-design.md` or review file.

If the **frozen repository baseline cannot be located and read**, classify that as an upstream architecture/access gap. Current descriptive repository/baseline metadata grants no access and is not proof of the inspected bytes. Stop before candidate readiness; current HEAD or working-tree bytes may describe drift but cannot silently replace frozen-baseline design truth.

## 3. Name the smallest authority decision

Report the exact selected `upstream_source`, the conflicting or missing commitment, the source-constrained `resume_boundary`, and the smallest decision needed. Never route to an omitted stage. `resume_boundary` classifies the selected source that would have to become current again; it is not permission to edit that artifact and does not decide where a future repository binding lives.

When the missing capability is the unratified repository-binding/baseline-reader mechanism itself, `resume_action` asks only for ratification of that machine-local binding and exact-tree read contract. Do not prescribe a `run.yaml` field, Stage 0 amendment/effective-configuration field, absolute artifact path, registry schema, clone/fetch behavior, or new controller.

Current V1 has **no supported reopen or replacement-acceptance path** for accepted System Design or Program Design. `planning-control.json` remains `PENDING`; this runbook does not authorize editing upstream artifacts, either control file, or review evidence. The shared intake-correction procedure applies only when discovery owns the cursor and proves repository identity/baseline intake wrong; it is not a downstream reopen mechanism.

## 4. Completion report

Return:

1. origin: producer or reviewer;
2. exact immutable source and current hashes;
3. local `BLOCKED` versus upstream `DESIGN_BLOCKED` classification;
4. proven non-mutation results;
5. smallest unresolved authority decision; and
6. explicit statement that resume is unsupported until the named upstream mechanism or decision is ratified.
