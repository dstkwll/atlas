# Product interface review

Use when designing or substantially revising a screen, reviewing interface quality, or investigating a product that feels confusing, generic or difficult to use. A requested mechanical edit with settled appearance needs only its relevant regression checks. This method can inform early design as well as an implemented interface; identify which evidence is available rather than requiring a finished build.

## Ground the critique in the user's work

Establish who uses the interface, what they are trying to finish, the domain object or status they must understand, and the next meaningful action. Recover accepted brand, platform, content and interaction constraints. Infer only what the evidence supports; expose an assumption if it would change the design. A product does not need a new visual identity or novel interaction to be useful.

Inspect representative content and consequential states. Does visual priority follow the user's decision, or merely the component library's defaults? Can users distinguish urgent work from supporting information, understand the consequence of an action, and recover from an error? Check whether empty, loading, partial, disabled and narrow-screen views preserve the task. Do not mistake a screenshot's attractive composition for a functioning journey.

Use available implemented screens, sketches, wireframes or code according to the assignment. Cite the actual view, state and condition behind a finding, and distinguish observed rendering from a source-level hypothesis. If the render or device is unavailable, continue useful critique while keeping appearance, interaction and usability claims appropriately unverified. Read [User journeys](user-journeys.md) for behavioral, responsive and accessibility verification.

## Develop and compare useful changes

Explain what the current design makes the user notice or do, the resulting friction, and the smallest change that addresses it. Preserve choices that already serve the task. A sparse screen, dense table or familiar pattern can be correct; neither novelty nor a preferred aesthetic supplies acceptance criteria.

When the evidence leaves a consequential choice open, use [Discover and design](discover-and-design.md) to compare viable directions against the same representative work. For example, a queue, table and spatial view differ in scanning, prioritization and relationship discovery; compare those consequences rather than presenting cosmetic variants as alternative strategies. Include the recommendation, practical tradeoffs and when another option would be preferable. Honor delegated judgment and settled constraints without adding an approval stage.

Comparable products or visual references can clarify a specific uncertainty. Explain the transferable pattern and why it fits; do not require a reference quota, copy another product's identity, or install a catalogue. A known design system may already supply sufficient guidance.

## Return an actionable review

Tie consequential findings to the user's job, evidence and a verification condition. Separate observed defects, supported design concerns and optional preferences; accept zero findings when supported. Distinguish a proposed improvement from a measured benefit. A reviewer score or verdict cannot authorize implementation or release.

Return enough context to act: what should remain, the prioritized changes or design options, why they matter, and which states or user tasks would verify them. In the final response, distinguish source inspection, rendered views and exercised interactions; name important unchecked states and unavailable checks, including checks announced but not completed. Use the existing brief when decisions need to survive. If the unresolved claim is about what actual users understand or need, consult [User research](user-research.md); an expert or simulated-persona walkthrough generates hypotheses, not participant evidence.
