# Selective coding methods

The change adds focused methods to three existing references: diagnosing failures across repeated or parallel tests, evaluating tool-using agents, and comparing technical alternatives. Existing specialist routing descriptions expose those methods; test-first work routes to the existing Test adequacy reference. The lead contract, authority boundaries and optional consultation model remain unchanged.

## Executed checks

The existing evaluator correctness suite passed all 39 tests using `python3 -m unittest discover -s evals -p 'test_*.py' -v`. All 34 local link targets in the four edited references resolve. The plugin, marketplace metadata and Atlas marketplace entry agree on version 0.8.0. `git diff --check` passed.

These checks establish evaluator behavior on existing fixtures and package consistency. They do not establish that an agent will select or apply the new guidance.

## Review scope and limits

A fresh context-only Copilot review (Claude Sonnet 5, high effort) inspected the candidate and applied it to five supplied scenarios: shared-account E2E interference, an agent export with incomplete action evidence, dependency claims for different tiers, a deterministic CSV fix and a single API lookup. The scenarios overlap the examples used during drafting, so this is a consistency check, not held-out generalization evidence.

The reviewer kept the two ordinary tasks small and identified two wording clarifications: explicit event-listener registration order and concise evidence retention for every evaluation attempt. Both were applied and checked locally; no second inference review was run for those wording changes. A suggested expansion into one-off agent-run auditing was not adopted: the existing Independent review reference already routes agent-report checks, while this addition concerns evaluation design.

The export scenario exposed a reviewer error: it proposed resulting-state/backup checks as an alternative way to conclude no prohibited intermediate write occurred. Those checks cannot establish that claim. The candidate explicitly preserves the distinction and requires missing action evidence to remain unknown. This miss limits the scenario result; reviewer completion is not a behavioral pass.

No native host activation trial or matched baseline/candidate efficacy experiment was run for this change. Improved coding outcomes and automatic runbook selection remain unverified.
