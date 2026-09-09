# Produce a PRD

Use to turn an explored problem, conversation or existing brief into a product document another planner can use. The artifact is the outcome; it does not authorize implementation or tracker publication.

Read the relevant original request, accepted amendments and existing brief. Reuse the project's artifact location and template when useful; otherwise write a concise Markdown document in an appropriate project-local documentation location. Do not create a competing spec. Reconcile the conversation with accepted records; courtesy, agent recommendations and prototype behavior are not user decisions.

Apply [Discover and design](discover-and-design.md) to gaps that affect the requested scope. Inspect available product/repository facts; do not ask the user to supply facts you can inspect. If access is missing, distinguish a product-level PRD from repository-grounded implementation readiness. Preserve unresolved judgment rather than filling plausible defaults into accepted requirements.

Include the information a planner actually needs:
- Problem, intended users, outcomes and observable success.
- Scope and exclusions; representative journeys and important failure/recovery examples.
- Accepted commitments and their rationale when supplied; proposed choices and assumptions distinctly marked.
- Constraints, external dependencies, known current behavior and material compatibility or risk boundaries.
- Acceptance examples tied to the outcomes, with uncertainty and decisions still needed.

Add technical responsibilities or interface sketches where they encode settled decisions; a PRD need not prescribe internal helpers. Reuse existing terminology. Keep a visual linked to the underlying decisions rather than treating it as a second authority.

Read the completed document against the request and amendments: what was lost, silently narrowed or introduced? Check whether a fresh planner can distinguish settled intent from remaining design. Seek independent scrutiny when consequential ambiguity warrants it. Resolve material contradictions or mark the affected scope blocked; do not label a polished draft accepted merely because it is complete.

Return the artifact, its actual status (draft with named gaps, or ready for the specified planning purpose), and the next useful activity. Recommend [vertical-slice planning](to-tickets.md) when appropriate. Do not start it automatically when the assignment ends at the PRD.
