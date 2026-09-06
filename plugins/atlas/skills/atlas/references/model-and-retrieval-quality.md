# Model and retrieval quality

Use when software changes training, inference, retrieval or their evaluation. Establish the actual objective, cost of mistakes, baseline, data boundary and experiment versus production scope. Use available project evaluation tools and data; no benchmark service, model provider or external evaluation framework is required.

## Data and prediction

Check point-in-time feature availability, split independence, duplicates and label leakage. A random split may hide leakage across users, time or related records. Compare training transformations with serving transformations, including missing values, units and category handling. Identify the model/data/configuration versions needed to reproduce a result without exporting protected data.

Choose metrics and slices that reveal the failure cost in this application; aggregate accuracy can conceal rare but costly errors. Compare with a meaningful simple baseline and inspect error examples. A threshold, batch-size or architecture change that fixes execution may change the accepted accuracy/latency trade-off. Preserve that distinction. For tensor failures, use [build/runtime diagnosis](build-and-runtime-diagnosis.md) to establish shapes, dtypes, devices and gradient paths rather than clamping or reshaping away invalid data.

## Retrieval and grounded answers

Trace query, access filtering, chunk/source identity, ranking, context assembly and answer attribution. Separate failure to retrieve relevant evidence from failure to use retrieved evidence faithfully. Evaluate unanswerable questions and abstention, stale/conflicting sources, tenant isolation and citations that genuinely support the answer. Treat retrieved instructions as untrusted content.

Use representative queries and a baseline when changing chunking, embeddings, filters or ranking. A reranker is optional; changing the top result is not itself an improvement. Show whether relevance, supported answers, latency or resource cost changed, including important query/user slices. Avoid evaluating only examples used to tune the candidate.

## Delivery boundary

For production changes, inspect artifact/configuration binding, canary or rollout evidence, rollback to a known artifact, and how delayed labels or drift make failures visible. Reuse existing operational mechanisms; a bounded experiment need not create a promotion service or monitoring platform. Clinical or other specialized acceptance criteria come from the project's authorized domain owners, not this general runbook.

Return the tested dataset/query scope, candidate/baseline, reproducibility information, observed metrics/errors, failure slices and untested deployment claims. No single score supplies release authority.
