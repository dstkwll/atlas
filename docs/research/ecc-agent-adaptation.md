# ECC agent adaptation study

Date: 2026-09-06. Atlas baseline: `0d85860a484182ab22b7890be2a3e7c893d85f0f`. Donor: all 68 installed ECC 2.2.1 agent prompts, identified by [source hashes](ecc-2.2.1-source-hashes.json). Upstream repository metadata identifies https://github.com/affaan-m/ECC. The supplied ECC_AGENTS_GUIDE.md helped select the source catalog; recommendations below came from the actual prompts, not the summaries alone. Two read-only researchers examined 24 review donors and 28 build/specialist donors; the primary inspected the remaining 16 and reconciled the findings.

## Decision and adaptation method

The user authorized a broad deep dive and implementation, not merely the previously suggested first four references. The result is 17 specialist runbooks, a selective index, and narrow refinements to the four existing activity guides. This is a bounded implementation of the accepted main-agent model. A required worker roster, ordered workflow, tool subsystem or autonomous controller is incompatible with this adaptation and is not introduced.

Every runbook may guide direct work or an appropriately bounded worker. Independence is a property of the review assignment/context, not of a file name. The lead owns selection, integration and authority. Donor technical questions survive; donor personas, model choices, tool frontmatter, agent-to-agent routing, repeated security boilerplate and report schemas do not.

Generalization retains non-obvious failure mechanisms: missing runtime validation despite types, hidden errors and uncertain effects, dynamic consumers of apparently unused code, framework interception, asynchronous ownership, deployment coexistence, interactive accessibility, data leakage and grounded answers. Principles are expressed through consequences: cohesion and information hiding reduce caller coupling; clear ownership protects invariants; evidence distinguishes accepted intent from observed accidents; measurement justifies optimization; reproducibility and compatibility constrain repair.

Tool neutrality means using approved existing capabilities, not pretending every check can be completed without tools. No new scanner, browser, evaluator, runtime or documentation service is installed or required by Atlas. Missing access produces a bounded evidence gap. Framework/API/standards details must be checked against the actual version when relevant; this library is not a copied vendor manual.

Dedicated network architecture/operations, clinical and campaign workflows remain useful future options with concrete triggers below. General transferable checks are retained now. This keeps the requested software-delivery purpose coherent without discarding the source research.

## Per-agent disposition

Destinations below are reference basenames under `plugins/atlas/skills/atlas/references/`. Multiple donors intentionally share a runbook; this is not a one-agent/one-file conversion. DEFER entries describe future options, not runtime dependencies or required work in this release.

| ECC donor | Destination / disposition | Preserved expertise | Removed or corrected assumptions |
| --- | --- | --- | --- |
| architect | discover-and-design | Responsibilities, quality trade-offs, cohesion and clear interfaces | No automatic services, scalability tiers, pattern shopping or compulsory ADR suite |
| planner | discover-and-design; deliver-and-repair | Concrete affected paths, dependencies, risks and verifiable increments | No fixed horizontal phases, prescribed coverage or feature inflation |
| code-architect | discover-and-design | Fit real repository patterns; smallest useful blueprint | No universal types-to-UI-to-tests build sequence |
| code-explorer | understand-behavior | Entry-to-effect tracing, branches, integrations and caller reliance | No compulsory whole-system map or named worker |
| spec-miner | understand-behavior | Evidence-anchored behavior and invariants, uncertainty and bounded expansion | No OpenSpec schema, file quotas, tool chain or automatic promotion of observations into accepted requirements |
| type-design-analyzer | types-and-invariants | Construction/mutation invariants, representation and escape paths | No numeric type score or hypothetical redesign |
| a11y-architect | user-journeys | Semantics, keyboard/focus, assistive interaction and platform context | No required tool, ADR set or unverified standards/conformance claims |
| homelab-architect | DEFER: actual gateway/DNS/VLAN/VPN work | Recoverable management and network access, hardware/operator fit | No imported home-lab topology or ECC skill chain |
| network-architect | DEFER: actual topology/routing/segmentation change | Flow boundaries, fault domains, phased cutover and recovery | No network subsystem or protocol prescribed by scale folklore |
| tdd-guide | test-adequacy | Separating failure, behavior assertions and regression discipline | No universal test-first mandate, 80% threshold, metric suite or named test tools |
| code-reviewer | independent-review | Concrete trigger, contextual guards, defensible impact and valid zero findings | No mandatory review for every edit, fixed severity/style thresholds or merge verdict authority |
| code-simplifier | simplify-and-clean | Local clarity with observable behavior preservation | No automatic helper extraction, immutability or cleanup sweep |
| refactor-cleaner | simplify-and-clean | Consumer verification, dynamic/public references and bounded removal | No required knip/depcheck tools, per-batch commits or automatic safe label for unused exports |
| comment-analyzer | documentation-and-references | Comment/contract accuracy, side effects and durable rationale | No compulsory comment coverage or stale-doc mass rewrite |
| silent-failure-hunter | failure-handling | Error propagation, false success, fallback meaning and recovery | No zero-tolerance persona or blanket log/rethrow mandate |
| pr-test-analyzer | test-adequacy | Behavior-to-assertion coverage, reachable gaps and test quality | No fixed report or line-coverage acceptance |
| agent-evaluator | independent-review; guidance-improvement | Compare original assignment and actual artifacts; evidence for completion | No five-axis scorecard, ECC evaluator service or self-approval |
| performance-optimizer | performance | Representative baselines, bottleneck attribution, memory and trade-offs | No universal web budgets, memoization/caching mandates or required profilers |
| security-reviewer | security-boundaries | Trust paths, object authorization, sensitive data and contextual proof | No scanner dependency, pattern-only severity or unrequested secret rotation |
| database-reviewer | data-and-migrations | Integrity, query evidence, tenancy, locks and connection lifetime | No PostgreSQL/Supabase-only conventions, universal indexes/types or automatic plan execution |
| build-error-resolver | build-and-runtime-diagnosis | Type/module/dependency/configuration failure classification | No lockfile deletion, cache wiping, broad autofix or plausible defaults to silence errors |
| cpp-build-resolver | build-and-runtime-diagnosis | Compile versus link, symbols, source membership and ABI | No required CMake/tool suite or casts as mechanical repairs |
| dart-build-resolver | build-and-runtime-diagnosis | Nullability, code generation, packages and platform compatibility | No empty IDs, forced dynamic/non-null casts or global cache repair |
| django-build-resolver | build-and-runtime-diagnosis; data-and-migrations | Interpreter/settings/imports and migration graph versus data state | No fake/reset migrations, arbitrary port kills or secret configuration dumps |
| go-build-resolver | build-and-runtime-diagnosis | Receiver/interface, module/workspace, cycles and value semantics | No automatic module cleanup, package extraction or discarded errors |
| java-build-resolver | build-and-runtime-diagnosis | Effective dependencies, processors, wrappers and framework discovery | No wrapper bypass, mandatory framework pipelines, upgrades or lazy/proxy workaround |
| kotlin-build-resolver | build-and-runtime-diagnosis | Toolchain alignment, mutable smart casts and exhaustive cases | No catch-all branch, detached coroutine or visibility widening by default |
| pytorch-build-resolver | build-and-runtime-diagnosis; model-and-retrieval-quality | Shape/dtype/device/gradient tracing and representative batches | No CUDA/tool assumptions, clamping, reshaping or training changes merely to stop crashes |
| react-build-resolver | build-and-runtime-diagnosis; client-state-checks | Bundler failure layers, imports, server/client and hydration | No blind client marker, stack update or configuration replacement |
| rust-build-resolver | build-and-runtime-diagnosis | Ownership/lifetime, trait/features, toolchain and suspension context | No blind clone/static/unsafe/interior-mutability workaround or ordering changes |
| swift-build-resolver | build-and-runtime-diagnosis | Actual target, signing, deployment and actor/sendability checks | No cache reset, toolchain upgrade or isolation suppression by default |
| cpp-reviewer | language-runtime-checks | RAII, reference invalidation, bounds, threading and ownership | No mandatory analyzer/compiler flags or allocation/style bans |
| csharp-reviewer | language-runtime-checks; service-framework-checks | Cancellation, sync-over-async, disposal, nullable and DI/ORM lifetime | No universal ConfigureAwait, sealing or tool suite |
| fsharp-reviewer | language-runtime-checks | DU exhaustiveness, Result/Option, resource/task and lazy-sequence lifetime | No mandatory functional rewrite or formatter/style gate |
| go-reviewer | language-runtime-checks | Goroutine exits, context/channel ownership and deferred cleanup | No fixed linter stack or universal wrapping/interface style |
| swift-reviewer | language-runtime-checks | Actor reentrancy, ARC lifetime, cancellation and failure boundaries | No universal weak captures, value/protocol redesign or forced-unwrap severity |
| rust-reviewer | language-runtime-checks | Unsafe invariant proof, panics, lock/suspension and bounded channels | No required Tokio/error library, green-build prerequisite or blanket unwrap verdict |
| kotlin-reviewer | language-runtime-checks; client-state-checks | Structured scopes, Flow semantics, Compose state and platform lifetime | No forced Clean Architecture, UseCases or remembered-callback rule |
| java-reviewer | language-runtime-checks; service-framework-checks | Framework/version context, proxies, transactions, shared services and events | No fixed layers, DTO/injection mandate or forced reviewer handoff |
| python-reviewer | language-runtime-checks | Mutable defaults, exceptions, async boundaries and resource lifetime | No universal annotations/docstrings/comprehensions or tool stack |
| php-reviewer | language-runtime-checks; service-framework-checks | Coercion, mass assignment, policies, serialization and queue behavior | No mandatory Actions/Services, static analyzer stack or style gates |
| typescript-reviewer | language-runtime-checks | Runtime validation versus assertions, promises and module boundaries | No forced paired reviewer, universal parallelism or strictness suppression |
| django-reviewer | service-framework-checks | ORM evaluation, transactions, deployment data, serializers and object permissions | No Celery/services/factory mandates or version-insensitive bulk-operation claims |
| fastapi-reviewer | service-framework-checks | Dependency/override identity, sessions, async clients and schema exposure | No inline-session verdict or compulsory architecture layers |
| react-reviewer | client-state-checks | Hook identity/dependencies, stale closures, effect cleanup and server boundaries | No paired reviewer, memoization mandate or prop-depth thresholds |
| vue-reviewer | client-state-checks | Reactive sources, watchers, cleanup, SSR isolation and public configuration | No forced Composition API migration or library choices |
| flutter-reviewer | client-state-checks | Widget/state identity, mounted context, disposal and chosen state manager | No new state framework, telemetry service or golden-test mandate |
| harmonyos-app-resolver | client-state-checks; DEFER detailed syntax until actual ArkUI work | API/device level, observed state, navigation, resources and permissions | No forced V2/Navigation migration or permanent version-specific manual |
| e2e-runner | user-journeys | Meaningful end-to-end assertions, isolation, condition waits and honest flaky evidence | No browser install, artifact upload, fixed repetition counts or quarantine-as-success |
| doc-updater | documentation-and-references | Docs versus code, usable setup/examples and targeted navigation | No compulsory CODEMAPS tree, generator, dates or exact format |
| docs-lookup | documentation-and-references | Version-matched authoritative evidence and sourced examples | No Context7 dependency, fixed call budget or remembered syntax presented as verified |
| mle-reviewer | model-and-retrieval-quality | Point-in-time data, leakage, serving parity, error slices and reproducible artifacts | No iteration compact, production machinery for every experiment or universal promotion gate |
| rag-pipeline-reviewer | model-and-retrieval-quality | Retrieval versus faithfulness, source grounding, isolation and baseline queries | No required reranker/RAGAS or top-result-change metric |
| healthcare-reviewer | DEFER: actual clinical decision/record/interchange change | Domain units, provenance, failure costs and authorized clinical judgment | No generic SAFE TO DEPLOY verdict, universal alert trade-off or imposed clinical platform |
| network-config-reviewer | DEFER: network config diff | Referenced ACL/route consistency, management exposure and cutover risk | No Cisco assumptions or static verdict as change authority |
| network-troubleshooter | build-and-runtime-diagnosis; DEFER device details until network incident | Causal layering, scope/time, discriminating comparisons and counter deltas | No automatic device remediation or disabling protection for diagnosis |
| marketing-agent | DEFER: requested launch/campaign | Audience evidence, supported claims and coherent user promise | No full campaign sequence, fixed deliverables or locked positioning |
| seo-specialist | user-journeys | Conditional public-page indexing, canonicals, redirects and truthful structured data | No ECC SEO dependency, folklore thresholds or indexability requirement for private apps |
| chief-of-staff | continuity-and-decisions; DEFER channel workflow until explicitly requested | Distinguish information, decisions, commitments and follow-through | Reject communication integrations, automatic archive/calendar writes and unsupported recall claims |
| harness-optimizer | guidance-improvement | Diagnose observed guidance failure, bounded correction and baseline comparison | No audit/eval subsystem, fixed trial score, automatic revert or universal approval gate |
| loop-operator | deliver-and-repair; continuity-and-decisions; guidance-improvement | Detect no-progress retries, preserve objective and bounded recovery | Reject loop controller, scheduler and scope shrinkage as recovery |
| conversation-analyzer | guidance-improvement | Repeated explicit corrections/reversions as evidence to investigate | No hookify/regex blocks or automatic promotion of anecdotes into policy |
| gan-planner | discover-and-design; user-journeys | User flows, acceptance evidence and intentional interaction direction | Reject fixed sprints/features/stack and aesthetic weights that override function |
| gan-generator | deliver-and-repair; client-state-checks | Accepted intent, interaction states and accountable corrections | Reject mandatory obedience to wrong evaluator, fixed state/commits/loops |
| gan-evaluator | user-journeys; independent-review | Exercise actual journeys, error/keyboard/responsive states and expose evidence limits | Reject weighted approval score, browser dependency and hostile persona |
| opensource-forker | release-preparation | Exact staged distribution, configuration/dependency exposure and source preservation | No history reset, blind replacements or secrets in example configuration |
| opensource-sanitizer | release-preparation; security-boundaries | Independent exact-artifact exposure review including relevant history | No one-commit proof, regex certainty or secret-value reproduction |
| opensource-packager | release-preparation; documentation-and-references | Fresh-consumer install, actual prerequisites and useful package docs | No forced setup script/instruction file/templates or implied licensing choice |

## Provenance and maintenance

The shipped skill includes [third-party attribution and the ECC MIT notice](../../plugins/atlas/skills/atlas/THIRD_PARTY_NOTICES.md), so both plugin and standalone copies preserve the notice. The database source also credits Supabase; Atlas retains general integrity/measurement principles rather than copying vendor-specific SQL conventions.

Do not automatically synchronize donor updates. A future source update is evidence to inspect and adapt against the same boundaries, then validate. The per-file hashes identify the reviewed snapshot; they are research evidence, not a workflow registry or runtime schema. Review a new specialized addition when an actual task or failure shows the existing reference is insufficient.

The implementation and forward-test evidence are recorded in [runbook validation](../validation/specialist-runbooks.md). No claim is made that every supported language/framework or domain has been executed in a live host.
