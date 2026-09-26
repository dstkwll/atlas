# Documentation boundaries for durable Atlas evidence

Accepted 2026-09-26. This decision concerns where maintainers preserve reasoning and evidence. It does not amend Atlas product architecture, installed guidance, or the authority to publish or merge work.

## Reader problem and decision

A maintainer needs to find the current accepted reason for a consequential choice without reconstructing a sequence of drafts and reviews. The same maintainer must be able to assess a public behavioral claim—including adverse results and untested conditions—without access to private research. Keeping every trial report in the current documentation tree obscures those purposes. Moving all evidence to private notes would prevent public maintainers from assessing the claims.

Use a purpose-based split:

- **ADRs** record consequential accepted decisions and the reasons and tradeoffs that remain relevant to future choices. This accepted documentation policy warrants an ADR; ordinary reports and implementation choices do not automatically require one. Promote consequential *accepted rationale*, not an observation or a promising trial result, into policy.
- **Canonical runbooks and operational guidance** own reusable methods. For skill and runbook craft, use the existing [Writing agent guidance](../writing-agent-guidance.md) method rather than creating a second authoring standard.
- **Concise public, topic-focused validation summaries** state the tested scope, observed behavior, material adverse findings and limits, with source-preservation judgments where relevant. A public maintainer must be able to interpret their claims without private notes.
- **The substantive issue, PRs and Git history** retain author selection, review sequence, per-file disposition, implementation checks, handoffs and other one-off work history. Keep full historical reports recoverable through linked PR and Git records when consolidating or removing them from the current documentation tree.
- **Private maintainer evidence** can retain detailed traces and diagnostics; it is not a prerequisite for public maintenance or product use. A personal wiki may distill transferable lessons but is not repository authority.

## Alternatives and tradeoff

| Approach | Benefit | Cost |
| --- | --- | --- |
| Keep detailed execution reports as current documentation | Maximum detail immediately at hand | Makes the current finding difficult to locate and mixes durable limits with draft and review chronology |
| Move all evaluation material into private maintainer notes | Keeps the public tree small | Makes public maintenance depend on private access and leaves behavioral claims difficult to assess |
| Separate accepted rationale, reusable method, scoped public findings and work history | Gives each reader an appropriate home while retaining inspectable evidence | Requires checking that material findings survive consolidation and that the full originals remain recoverable |

The third approach is accepted. Apply this boundary to existing documentation as well as new work, including reports already merged. Preserve material evidence and limitations before shortening the current tree; do not infer policy from successful or unsuccessful observations alone. Keep substantive progress and remaining decisions in the assigned issue or PR rather than maintaining a second status ledger. This split requires no registry, schema, pipeline, word quota or public dependency on private notes. Existing runtime tests, cases, rubrics, product safety rules and authority boundaries remain in force.
