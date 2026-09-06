# Performance diagnosis

Use for reported slowness, a measured regression, resource growth or a concrete performance budget. Define the user-visible operation, representative workload/environment and metric before optimizing. Reuse available profiling and measurement tools; missing tooling limits evidence rather than requiring a new observability stack.

Establish a repeatable baseline and separate warm/cold conditions, input size, concurrency and cache state. Look at distributions or repeated samples when variance matters; one lucky run is not a reliable improvement. Use the project's latency, throughput, memory or bundle budget instead of importing universal thresholds.

Locate the bottleneck before selecting a technique: CPU/algorithmic work, blocking I/O, query count/plan, network waterfalls, rendering, allocation or retained resources. Trace cardinality and dependencies. Parallelize only independent operations within resource limits; batching can change latency, ordering and failure semantics.

Evaluate the proposed trade-off. Caching needs keys, invalidation, freshness, tenant isolation and bounded growth. Memoization can add overhead or preserve stale values. Laziness may worsen the critical interaction by deferring essential work. A faster query may increase write cost; a memory reduction may increase CPU. Preserve correctness and user-observable ordering while measuring the target.

For leaks, repeat acquire/use/release or mount/unmount cycles and inspect what remains reachable. Distinguish a bounded warm cache from unbounded retention; identify the owner that should release listeners, tasks, buffers or connections. Use the relevant [language/runtime checks](language-runtime-checks.md) when ownership is uncertain.

Compare candidate and baseline under the same meaningful conditions. Report actual before/after measurements, uncertainty, regression checks and operational cost. An estimated improvement stays an estimate. Stop when the target is met or evidence shows that the bottleneck lies outside authorized scope; return that boundary rather than redesigning the system speculatively.
