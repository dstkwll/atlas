# Establish project verification

Use when a team or later agent needs a repeatable way to verify a project outcome, or an existing verification recipe is unreliable. Reuse the project's tests, developer instructions and approved capabilities first. A reliable existing command needs no wrapper, generated skill or new harness. Keep the routine recipe to a few existing commands and the context needed to use them. Add automation only when repeated use or a concrete failure justifies maintaining it; one exercise need not become a general test driver.

Choose one representative outcome and the claims the recipe must establish. Discover the actual target, commands, fixtures and expected behavior from the project. Check that a command reaches the relevant assertion; successful startup proves only startup. Use [Test adequacy](test-adequacy.md) for proof selection and [User journeys](user-journeys.md) for interactive evidence.

Keep the recipe in the project's established test/developer documentation home, outside the installed Atlas package. If it belongs to a planning topic, use its [approved artifact location](artifact-location.md). Update the existing source rather than create a competing feature registry. Include only what another operator needs:

- Prerequisites, permitted test data and side effects, and the exact target/build identity to verify.
- How to launch or attach, recognize readiness and confirm which instance is under test. A responding port alone does not identify the right build.
- Actions or checks that exercise the outcome, expected observations, and materially different entry paths when relevant.
- Where diagnostic evidence is retained, what it proves and which unavailable prerequisites limit it.
- How to reset and release resources created by the run, distinguishing those resources from the user's existing processes, accounts and work.

Exercise a representative path within authority before calling the recipe usable. Check result capture and cleanup as well as the main action. Where safe, check an interrupted or failed step and confirm evidence remains accessible after teardown; otherwise state that recovery is untested. Inspect what any dry-run option actually suppresses before relying on it. An unexecuted recipe remains a draft with named prerequisites, not verified guidance.

When behavior surprises you, recheck the build, instance, fixture and relevant state before changing the recipe. Separate stale instructions, a faulty test mechanism and a product defect; never redefine an expected result merely to match a regression. Preserve failure evidence before reset. Give shared mutable test resources a clear owner; source reading may proceed independently, but concurrent driving of one account or UI can invalidate observations.

Return the recipe location, checks actually executed, evidence retained, cleanup result and remaining limits. Maintain commands and meaningful setup/reset knowledge when they change; do not require an exhaustive map before new investigation. Confirm the recipe's usefulness from a fresh operator's available context when feasible. Readability and one successful exercise do not prove every feature, host or failure path.
