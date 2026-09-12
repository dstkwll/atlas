# Establish project verification

Use when a team or later agent needs a repeatable way to verify a project outcome, or an existing verification recipe is unreliable. Reuse the project's tests, developer instructions and approved capabilities first. A reliable existing command needs no wrapper, generated skill or new harness. Keep the routine recipe to a few existing commands and the context needed to use them. Add automation only when repeated use or a concrete failure justifies maintaining it; one exercise need not become a general test driver.

Choose one representative outcome and the claims the recipe must establish. Discover the actual target, commands, fixtures and expected behavior from the project. Check that a command reaches the relevant assertion; successful startup proves only startup. Use [Test adequacy](test-adequacy.md) for proof selection and [User journeys](user-journeys.md) for interactive evidence.

Keep the recipe in the project's established test/developer documentation home, outside the installed Atlas package. If it belongs to a planning topic, use its [approved artifact location](artifact-location.md). Update the existing source rather than create a competing feature registry. Include only what another operator needs:

- Prerequisites, permitted test data and side effects, and the exact target/build identity to verify.
- How to invoke the check, launch or attach where needed, recognize readiness and confirm the target under test. A responding port or connected instrument alone does not identify the right build and configuration.
- Actions or checks that exercise the outcome, expected observations, and materially different entry paths when relevant.
- Where diagnostic evidence is retained, what it proves and which unavailable prerequisites limit it.
- How to reset and release resources created by the run, distinguishing those resources from the user's existing processes, accounts and work.

Exercise a representative path within authority before calling that part of the recipe usable. Check result capture and cleanup as well as the main action. Where safe, check an interrupted or failed step and confirm evidence remains accessible after teardown; otherwise state that recovery is untested. Inspect what any dry-run option actually suppresses before relying on it. Unexecuted portions remain drafts with named prerequisites; an exercised offline path does not validate a later hardware procedure.

## When evidence depends on equipment or an event

Choose the strongest relevant checks available now: unit tests, recorded-data checks, simulation, integration tests or physical observations. State which claims each reaches and which it cannot. A simulated or replayed input proves behavior under that input and model; name omitted physical effects when the claim depends on them. Do not assume equipment, an operator, deployment access or a rapid feedback loop is available.

Continue useful authorized software work and preparation while physical evidence is pending. Distinguish implementation prerequisites from verification prerequisites: unavailable hardware need not block an offline change with settled acceptance criteria, but unknown behavior or missing interfaces may block the dependent part. Report software progress and physical verification separately without inventing a new status system. Do not treat missing equipment as a retry problem or green unit tests as full acceptance.

For an operator-organized event, keep the preparation in the existing ticket, recipe or topic home. Include what the next operator needs: claims and expected observations; the intended software/configuration and equipment/fixture identities; known setup/access prerequisites; the applicable procedure; evidence to capture and where it belongs; and the responsible person or event window if known. Leave unknowns explicit. Organizing or running the event does not give the operator product-policy or acceptance authority; keep those decisions with their authorized owners. Reference approved operating, reset and abort procedures where required; do not invent equipment commands, substitute acceptance criteria or authorize operation, deployment or scheduling through the plan.

When results return, compare actual identities and conditions with the intended claims. Record observed or reported results, failures, partial coverage, aborted steps and unrun checks, retaining the evidence before correction. Prior or different-build results apply only where their relevance is established; do not carry a nominal result into uncovered boundary, failure or repeat behavior. A summary without raw evidence remains a report with that limit. Preserve unresolved claims and the next evidence action. Accepting reduced proof or changing acceptance criteria remains the authorized decision owner's judgment, not an inference from a successful proxy test.

## Reuse and repair the recipe

When behavior surprises you, recheck the build, instance, fixture and relevant state before changing the recipe. Separate stale instructions, a faulty test mechanism and a product defect; never redefine an expected result merely to match a regression. Preserve failure evidence before reset. Give shared mutable test resources a clear owner; source reading may proceed independently, but concurrent driving of one account or UI can invalidate observations.

When a later reader verifies a changed candidate, retain the earlier record and identify the new run separately. Recheck that the recipe still applies and execute the available relevant assertions; a changed identity alone neither proves a defect nor makes the previous pass transferable.

Return the recipe location, checks actually executed, evidence retained, cleanup result and remaining limits. Maintain commands and meaningful setup/reset knowledge when they change; do not require an exhaustive map before new investigation. Confirm the recipe's usefulness from a fresh operator's available context when feasible. Readability and one successful exercise do not prove every feature, host or failure path.
