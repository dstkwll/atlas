# Specialist runbook validation

Date: 2026-09-06. Baseline: `0d85860a484182ab22b7890be2a3e7c893d85f0f`. Candidate branch: `feat/specialist-runbooks`. [Product hashes](specialist-runbooks-product-hashes.json) identify the exact inspected package independently of later evidence/state-only commits.

## Scope and requirements

The user requested a deep dive into useful ECC agents, adaptation to Atlas, additional runbooks usable directly or through discretionary delegation, no ECC tooling/subsystem dependence, preservation of donor intent, and good coding/architecture principles. This task delivers a draft implementation for review; it does not merge or update existing user/workplace installations.

| Requirement | Evidence |
| --- | --- |
| Source-level deep dive | All 68 actual ECC 2.2.1 prompts were inspected across primary and two read-only research contexts. The per-agent disposition and exact source hashes are in the research record. |
| Adapt rather than duplicate | 17 specialist references consolidate the catalog; the four core guides receive small contextual refinements. Dedicated clinical/network/campaign workflows have concrete deferred triggers. |
| Direct or delegated use | The index states both choices, preserves read-only versus implementation scope and gives a bounded briefing convention. No worker roster or required sequence exists. Two independent exercises selected only relevant references and completed analysis without further workers. |
| Self-contained, no ECC subsystem | Product consists of Markdown and a plugin manifest, with one skill. References resolve inside the skill. Donor tools/models, hooks, services, schemas and fixed workflows are absent. The package includes attribution/license notices, not an ECC installation. |
| Preserve distinctive expertise | Source mapping and independent review cover concrete failure mechanisms and retained runtime/framework distinctions. Generalized rules explicitly correct dangerous donor defaults and avoid unsupported tool/version claims. |
| Coding/architecture principles | Behavior/contract distinction, invariant ownership, cohesion/information hiding, compatible change, bounded side effects, measured optimization and evidence-based assurance appear in relevant procedures. |

## Source and package checks

- Skill-creator quick validator: PASS.
- All skill-relative Markdown links: PASS.
- Manifest and marketplace name/path/version agree at 0.2.0: PASS.
- One skill entrypoint; no runtime dependency files, executables, hooks or model-specific configurations introduced.
- Entrypoint: 1,044 words (baseline 999). Specialist index: 480 words. Entire skill including notices: 24 Markdown files / 9,831 words; this total is not startup context.
- Source inventory matches all 68 actual donor filenames and recorded SHA-256 hashes.
- `git diff --check`: PASS.
- Native Git-backed Copilot CLI 1.0.82 installation: PASS for product commit `e7c15f8b3a4d5b4fc84097961f97543510ae7dd9`. In a fresh disposable `COPILOT_HOME`, adding `dstkwll/atlas-successor#feat/specialist-runbooks` and installing `atlas@atlas-successor` discovered one enabled plugin at 0.2.0 and one enabled Atlas skill, with no discovery errors. All 26 installed files exactly matched the recorded product SHA-256 inventory, with no extra files. No existing user installation was changed.

## Independent forward exercises

Evaluators received a realistic request, the Atlas entrypoint and raw fixture. They were not given the expected answer, suspected defects or a mandated specialist route. Their tool scope was local and bounded; no ECC tools or services were used.

### Import-service review

Request: review the service against its documented contract and determine whether its tests support its claims. The [three-file fixture](fixtures/import-service/README.md) is preserved for reproduction; it intentionally contains the defects below and is not production code.

The evaluator selected independent-review, the specialist index, failure-handling and test-adequacy. It ran the two existing tests successfully and reproduced three material contract violations with injected sources:

1. An OSError becomes empty successful completion.
2. Completion is marked before work, so an exception permanently suppresses retry.
3. Completion keys omit tenant identity, so another tenant's matching job ID is skipped.

It also checked a reentrant duplicate and correctly did not call this a real threaded-concurrency test. The primary independently reproduced all three findings from the preserved fixture, with the existing two tests still passing. This is evidence of useful review and test-adequacy reasoning beyond a green test count.

### Existing-behavior explanation

A separate fresh evaluator was asked to explain the inherited service and what could safely be relied on. It selected discover-and-design, the specialist index and understand-behavior. It traced the actual path, separated happy-path evidence from untested failures, and explicitly distinguished the README's intended guarantees from the observed buggy baseline. It did not promote mined behavior into accepted requirements, mutate files or require a spec format. It ran the two existing tests and accurately labeled further failure conclusions as code inspection.

### Direct cleanup exercise: not executed

A Sol/low worker was asked to simplify a separate small formatter fixture while preserving its documented behavior. It selected only the core delivery guide, identified a bounded simplification and genuinely unused code, and ran the two baseline tests. Automatic approval review rejected its fixture edit as unrelated work. No candidate change was applied and no behavior-preserving implementation pass is claimed. The rejection was not bypassed. This is a host approval limitation, not evidence that the runbook completed an edit; direct mutation behavior remains unverified by this exercise.

## Independent library review

A fresh read-only reviewer inspected all 24 skill Markdown files, all relative links and selected donor originals. It reported no blocking or actionable non-blocking findings. It specifically checked optional use/delegation, authority boundaries, false-positive control, substantive language/framework distinctions and removal of mandatory RAG reranking. This establishes source coherence, not proof of every runtime behavior.

A separate follow-up audit verified that the research map accounts for all 68 donor filenames exactly once, that the recorded source hashes match, that adaptation destinations exist, and that sampled interpretations match the originals. It found no concrete issues.

The implementation is published as [draft PR #6](https://github.com/dstkwll/atlas-successor/pull/6). Subsequent evidence/state-only commits preserve the product inventory above.

## Limits

These are targeted agent-guidance exercises, not a benchmark or a guarantee. The library's language/framework, accessibility, security, database, model and release instructions have not each been executed against live projects. VS Code UI, authenticated Copilot model execution, real concurrency, production operations and workplace policy were not exercised. Missing capabilities remain explicit evidence gaps. No user data, credentials or workplace artifacts were used or exported.
