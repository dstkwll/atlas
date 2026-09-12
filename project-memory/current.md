# Current work

Branch: `feat/copilot-core-preload`. The user authorized native core preload on the Copilot profile and a reviewable change. Merge is not authorized. Preserve one shared Atlas core, selective runbooks, existing file-loading/recovery instructions and host authority. Hooks remain outside this change.

The profile declares `skills: [atlas]`; its instructions and shared skill bytes remain unchanged. Setup guidance explains host-dependent core-only preload, the continued availability of the optional skills, and compatibility limits. Detailed experiments remain in local maintainer evidence; the public [compatibility summary](../docs/validation/copilot-core-preload.md) records relevant coverage and unresolved behavior.

The candidate profile matches retained native preload evidence apart from YAML key order, and all shared skill files match exactly. All 17 evaluator tests, package/link checks and whitespace checks passed. Independent review established no product defect; the test-host description was clarified. Retained behavioral trials cover the equivalent package; no new behavioral trial or workplace testing was needed.

Next: review the draft change and merge only with explicit authorization.
