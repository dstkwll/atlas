# Produce a PRD

Use to turn an explored problem, conversation or existing brief into a product document another planner can use. The artifact is the outcome; it does not authorize implementation or tracker publication.

Read the relevant original request, accepted amendments and existing brief. Resolve the topic home through [Artifact location](artifact-location.md), including an applicable configured vault. For a new substantial PRD, default to one self-contained `prd.html` following [Recoverable HTML PRD](html-prd.md). Honor an explicit format request or established authoritative source; do not silently replace a governed Markdown document or create a competing spec. Reconcile the conversation with accepted records; courtesy, agent recommendations and prototype behavior are not user decisions.

Apply [Discover and design](discover-and-design.md) to gaps that affect the requested scope. Inspect available product/repository facts; do not ask the user to supply facts you can inspect. If access is missing, distinguish a product-level PRD from repository-grounded implementation readiness. Preserve unresolved judgment rather than filling plausible defaults into accepted requirements.

Include the information a planner actually needs:
- Problem, intended users, outcomes and observable success.
- Scope and exclusions; representative journeys and important failure/recovery examples.
- Accepted commitments and their rationale when supplied; proposed choices and assumptions distinctly marked.
- Constraints, external dependencies, known current behavior and material compatibility or risk boundaries.
- Acceptance examples tied to the outcomes, with uncertainty and decisions still needed.

Add technical responsibilities or interface sketches where they encode settled decisions; a PRD need not prescribe internal helpers. Reuse existing terminology. Keep a visual linked to the underlying decisions rather than treating it as a second authority.

Once this topic has a PRD, keep it current at material design decisions, accepted amendments and handoffs. A small unrelated task does not require a PRD. HTML may hold both the readable plan and agent recovery context without a separate Markdown twin; preserve one coherent account of commitments.

Read the completed document against the request and amendments: what was lost, silently narrowed or introduced? Check whether a fresh planner can distinguish settled intent from remaining design. Seek independent scrutiny when consequential ambiguity warrants it. Resolve material contradictions or mark the affected scope blocked; do not label a polished draft accepted merely because it is complete.

Return the artifact, its actual status (draft with named gaps, or ready for the specified planning purpose), and the next useful activity. Recommend [vertical-slice planning](to-tickets.md) when appropriate. Do not start it automatically when the assignment ends at the PRD.
