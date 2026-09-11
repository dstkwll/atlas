# Documentation, reflection and impact checks

The [evaluation cases](../../evals/cases.json) and [review criteria](../../evals/review.md#documentation-reflection-impact-and-optional-comparison) cover documentation selection, reflection persistence, impact assessment and confirmation before independent comparison. Checks used native Copilot sessions; equivalent behavior in other hosts is not established.

| Capability | Observed behavior | Remaining limits |
| --- | --- | --- |
| Documentation | Selected PRD, guide and architecture outputs from intent and created the requested artifacts. | Source accuracy and disclosure of unperformed checks had gaps. Rendering and independent HTML recovery were not verified. |
| Reflection | Saved a separate contextual record and linked it from task state. | Ambiguous source links caused a missed source; a clear relative link worked. This does not establish general retrieval reliability. |
| Blast radius | Identified a downstream compatibility failure without changing implementation. | Evidence came from source inspection, not runtime execution. |
| Arena | Proposed bounded independent work without launching it. | Working delegation was unavailable; launch restraint and limit enforcement with usable workers remain unverified. |

## Packaging and verification limits

The documentation command was discoverable. Argument-hint presentation and cross-host invocation controls remain unverified. Structural checks resolve product links and parse metadata; they do not establish host compatibility or agent judgment.

The evaluator's unit tests check evaluation infrastructure, not skill adherence. Handling unavailable HTML recovery validation has source review but no behavioral verification. See [turn-ending guidance checks](turn-ending-guidance.md) for conversational continuation.

Detailed trial records remain with maintainer evidence. Public usage instructions are in [Setup](../../SETUP.md).
