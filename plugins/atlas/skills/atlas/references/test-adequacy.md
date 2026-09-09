# Test design and adequacy

Use to choose proof for a meaningful change or evaluate whether submitted tests substantiate it. Begin with accepted behavior, the candidate/baseline and the reachable failure classes. Use the project's existing test stack; this runbook does not require a coverage service or a new test framework.

Map important claims to observable assertions. Ask whether the test would fail if the original defect returned, the key branch were reversed, a side effect were omitted, or an unintended duplicate occurred. A no-throw assertion or mocked implementation may run code without checking its contract. When useful, demonstrate a separating failure on the baseline or a temporary altered copy, never by silently modifying the reviewed candidate.

Choose test boundaries according to the uncertainty. Small deterministic rules often suit unit tests; serialization, transactions, middleware and adapters may need integration tests; a critical user journey may need end-to-end execution. Avoid both universal test-layer requirements and treating a mocked unit test as integration proof. Assert at the boundary the user or dependent component relies on.

Select cases from actual behavior: absent versus empty data, boundary values, malformed external input, permission differences, cancellation, duplicate delivery, concurrency or partial writes. Do not require every edge-case category for every change. Check that fixtures distinguish the competing outcomes rather than producing the same answer for good and bad implementations.

Keep tests independent of order, wall-clock luck, shared accounts and uncontrolled network state. Control time/randomness where appropriate; wait for relevant observable conditions. Mocks should preserve the contract under test and must not replace the very enforcement being claimed. An integration gap stays visible when the real dependency is unavailable.

For an ambiguous bug or recurring failed repair, derive expected behavior and a discriminating counterexample from the issue, accepted amendments and real system before adopting the producer's test or repair story. Proving failure before the correction is valuable. Test-first development is an available method, not a mandate for trivial edits or exploratory work. Line coverage, passing counts and numeric scores supplement evidence; they do not decide adequacy. Classify missing checks by the consequence they leave unverified.

Return which claims are proven, which are only inspected, important missing coverage, and actual commands/results. Investigate flaky failures rather than skipping them to produce a green result; any accepted quarantine needs visible lost coverage and its owner. Read [user journeys](user-journeys.md) for interactive behavior.

## Test-first work when it helps

For behavior changes and bug fixes with observable expected outcomes, prefer a small red-green-refactor loop when it supplies useful feedback; honor an explicit project or user TDD requirement. Establish the relevant test boundary, fixtures and runnable environment first. Use existing interfaces and accepted behavior; ask only when defining the boundary would require new judgment, not for approval of every test.

Write one meaningful failing behavior check, confirm it fails for the intended missing behavior, implement enough to pass, then refactor while preserving the checks. Repeat in integrated increments rather than writing an entire speculative test suite before learning from implementation. A setup error, missing import unrelated to the target behavior, or unreachable assertion does not establish red. A test added after implementation may be valuable, but do not report an unobserved red phase.

Derive expected values from accepted examples or an independent oracle. Prefer stable observable interfaces over private-method assertions and mocks of the behavior being claimed. Use integration checks when the contract crosses a real dependency; do not mistake mock agreement for provider compatibility. Keep trivial prose edits, exploratory probes and poorly specified behavior from acquiring ceremonial tests; state an appropriate alternative or resolve the expected behavior first. Planning test steps does not authorize writing production code or claim that those tests passed.
