# Release preparation and exposure review

Use when distributing a package, publishing a release, exposing previously private material or changing a release boundary. Establish exactly what is intended to leave the environment, its recipients, source revision and granted authority. Preparation and independent exposure review are separate assignments; neither implies permission to publish.

Inspect the actual deliverable, not only the source tree: packaged files, generated outputs, binaries, source maps, configuration examples, documentation, archives and any history included in the distribution. Stage an exact candidate separately where useful and preserve the original. Do not rewrite history, delete files by extension or replace internal names blindly. Those actions can lose required behavior and do not prove sanitization.

Trace secrets, private data and internal dependencies into the release boundary. Configuration examples should contain placeholders, never extracted credential values. Report locations and categories without reproducing secrets. A clean pattern scan or single-commit history is not proof of no exposure; encrypted, generated or inaccessible contents create explicit evidence limits. Previously exposed credentials require owner-directed incident/rotation handling as well as artifact correction.

Preserve third-party notices and identify unresolved license/ownership choices for the appropriate owner. Do not select a license or assign copyright on the user's behalf. Reconcile prerequisites, configuration and installation instructions with the actual package. Add only the setup artifacts a new consumer needs; no mandatory setup script, agent instruction file or issue-template suite.

Where independent review is required, give the reviewer the exact staged candidate and distribution boundary, not just the preparer's cleanup report. An authorized fresh-consumer install can verify discoverability, required files and representative usage. Installation success does not prove behavior or authorize release. Use [documentation](documentation-and-references.md) and [security](security-boundaries.md) for focused questions.

Return candidate identity, contents inspected, changes, consumer checks, unresolved exposures and actual review limits. After repairs, refresh evidence for changed artifacts before relying on the old review. Publication, visibility changes and history replacement remain distinct actions requiring applicable authority.
