# Produce useful documentation

Use when the requested outcome is a document or a meaningful documentation update. Identify the reader, the task the document must support, and the available source. Reuse an existing adequate document and honor its format. Resolve the topic home through [Artifact location](artifact-location.md); no new home merely because the entry point changed.

## Select the document from intent

An explicit `atlas-to-documentation` invocation with no document type defaults to PRD. An explicit type, an existing document being updated, or a clear natural-language request takes precedence: “write a setup guide” is a guide, even if the caller omitted the word `guide` as a formal argument. If there is no identifiable topic or source, ask that missing question; the PRD default does not invent a product. Argument hints are descriptive text, not an enforced enum or promised dropdown. Understand equivalent plain-language requests.

| Requested outcome | Method |
| --- | --- |
| PRD: intended product behavior, scope and acceptance | Apply [Produce a PRD](to-prd.md), retaining its specialized content and recovery contract. |
| Guide: enable someone to complete a task | Establish prerequisites, permitted actions, expected results and relevant failure/recovery steps. For onboarding, use a small working example; for an operational procedure, prioritize executable steps and verification. |
| Architecture: understand an existing or proposed system | Follow the architecture guidance below and [Understand existing behavior](understand-behavior.md) or [Discover and design](discover-and-design.md) as appropriate. |
| Reference: look up interfaces, settings or limits | Organize by the thing being described, using exact names, inputs, outputs, defaults, errors and relevant constraints supported by evidence. |

## Write for the reader's next action

Use [Documentation and reference evidence](documentation-and-references.md) for source/version checks and tested examples. Lead with the useful outcome, use consistent domain terms, explain non-obvious prerequisites and keep conditions beside the actions they govern. Prefer concrete examples to abstract assurances. Separate instructions, explanation and lookup material where it helps navigation; do not force a useful PRD or architecture document into a single rigid category.

An existing repository format or explicit request wins. Otherwise use Markdown for ordinary guides/references and self-contained HTML for a substantial architecture document. Apply [Recoverable HTML documents](html-document.md) when using HTML, including its visual verification and recovery limits. A short answer may suffice without creating a large artifact; an explicitly requested file must still be delivered or its blocker stated.

## Architecture content

Establish whether the request concerns observed architecture, a proposed design or a comparison. Inspect available system evidence before describing current behavior; never turn a design sketch into an as-built claim. Preserve accepted design separately from implementation facts when they disagree.

Explain the system's purpose and boundary, responsibilities, critical interfaces, data ownership, relevant runtime paths, failure/recovery, trust boundaries, constraints and consequential tradeoffs. Record the decisions and rationale actually supplied, proposals and unresolved questions, source relevance and what was not verified. Include only detail that changes understanding or a decision. Do not invent components, extensibility or an implementation plan to fill a template.

Use [Diagram craft](diagram-craft.md) for substantial views. Select a context/responsibility view, sequence, state or deployment view according to the question; no required diagram suite. Label current, proposed and accepted meaning consistently in text and visuals. Preserve relevant failure branches and provide a textual equivalent.

Keep architecture inside the PRD when that serves the reader. Create a separate `architecture.html` when the depth, audience or existing-system question warrants it, not as a mandatory PRD companion. State what each document owns: the PRD owns product commitments; a separate architecture document owns its technical account. Include the constraints needed to understand the architecture independently and identify their source, without creating another editable copy of the full requirements. Synchronize affected claims when accepted decisions change. A self-contained architecture document recovers its own meaning; do not claim it reconstructs missing product requirements, code or proof.

## Deliver

Reconcile the result against the request and evidence. Validate relevant links, safe examples and rendered HTML where available; distinguish source inspection from executed or visual checks. Mark gaps and actual planning status. Identify the file and material changes using the existing continuity notice. Document creation does not authorize implementation, publication, deployment or an additional artifact workflow.
