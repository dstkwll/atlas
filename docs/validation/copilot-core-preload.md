# Copilot core preload

The Copilot profile declares `skills: [atlas]` to request native preload of the shared core. Its existing file-loading, missing-source and recovery instructions remain intact. Runbooks still load selectively. [GitHub's SDK documentation](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents#per-agent-skills) describes eager per-agent skill loading; native observations determine compatibility with the tested host.

## Coverage and observations

Checks ran in an isolated harness using the SDK bundled with GitHub Copilot desktop 1.1.14 to drive standalone Copilot CLI 1.0.83, with Sol at low reasoning. File-loaded native profiles exercised activation, ordinary follow-ups, design-only scope and real compaction. Baseline and preload design sessions both consulted Architecture design and produced usable design/handoff records; independent review found minor notice and provisional-design issues. No improvement in task quality was established. Preload added about 4,400 system-prompt tokens in that comparison.

Unavailable-source handling honestly reported that Atlas could not be confirmed active. The same case attempted overly broad searches that were denied; preload does not fix retrieval judgment. Other cases also attempted denied reads of isolated session files. These scope findings remain distinct from acceptable task outcomes.

Separate native probes confirmed the selected profile advertised the requested skill. Prior transport checks used a value present only in the skill body to distinguish actual context availability from profile discovery. Package comparison ties the shipped profile and shared guidance to the current-source preload design evidence. Detailed traces and instrument history remain local maintainer evidence.

The candidate profile matches the tested preload profile apart from YAML key order; all 46 shared skill files match exactly. No new model trial was run for this packaging change. The 17 evaluator tests, manifest parsing, changed-document relative links and whitespace checks passed; these checks do not grade model adherence.

## Limits

These are bounded compatibility observations, not reliability estimates or proof that loading instructions ensures adherence. Desktop UI integration, Windows, other host versions and models remain unverified. Hosts may ignore preload metadata; explicit file-loading and recovery guidance remains necessary. The comparison does not establish every recovery path or remove earlier context when a profile is deselected. No hook or SDK runtime is distributed with this change.
