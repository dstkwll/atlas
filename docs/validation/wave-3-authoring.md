# Atlas Wave 3: technical-method authoring and validation

Atlas’s technical methods already described many of the right boundaries, but a few passages made those boundaries harder to recognize or find. A short interface could appear simpler while moving sequencing and error handling into every caller; general closing guidance sat beneath the last language or framework heading; and three links landed in broader sections than their referring sentences named. Wave 3 selected five small changes to address those problems and retained ten other targets. Independent source assessments found the selected revision eligible within the routes they examined. Eight fixed design trials produced useful bounded outcomes, **but did not show that the changes improved behavior**: both baselines met the material goals, and several notice and attribution defects remain in the observations.

## Source and selection

The wave baseline was `046d864a2bb164f9053661634c7b6adf76fa43e5`. Its fifteen target bodies were identical to those in the accepted program original, `9dcf142d1ecdaac90394df9e9490b1e6e246187c`; earlier selected guidance elsewhere remained part of the wave baseline. The tested product revision was `70b0d25633b2c71bd36d0e8731686dc1d1f2b2a4`, packaged as Atlas **0.10.4**.

Native Copilot Astra/max and Opus 5.5/xhigh drafted independently, exchanged frozen reciprocal critiques, and completed revisions. All six scheduled authoring turns completed. The coordinator selected the **whole Astra revision**, without blending candidates or adding coordinator-written product prose. Astra’s architecture wording compares useful behavior with what a caller must know for the same task, while keeping the warning that a shorter call can lose necessary control or guarantees. That was a source-selection judgment, not measured superiority over the other author or baseline retention. There was no architecture or decision amendment, shared-lead edit, new public entry point, or installed-copy change.

In the table, names without a longer prefix are under `plugins/atlas/skills/atlas/references/`. “Retained” means the target is unchanged from the wave baseline.

| Target | Disposition |
| --- | --- |
| `plugins/atlas/skills/atlas-blast-radius/SKILL.md` | Retained; its lead dependency and missing-source boundary still fit. |
| `architecture-design.md` | Changed; adds the same-task deep-module recognition test and two more precise decision links. |
| `blast-radius.md` | Retained; consumer tracing and claim-specific evidence remain intact. |
| `build-and-runtime-diagnosis.md` | Changed; points uncertain-effect retries to the repetition-safety section. |
| `client-state-checks.md` | Changed; makes the shared transition checks visibly cross-framework and clarifies framework selection. |
| `data-and-migrations.md` | Retained; writer, restore, deletion and coexistence obligations remain. |
| `language-runtime-checks.md` | Changed; separates the existing general result guidance from the Swift section. |
| `performance.md` | Retained; measurement and correctness tradeoffs remain explicit. |
| `reconstruct-rationale.md` | Retained; history, inference and present authority remain distinct. |
| `release-preparation.md` | Retained; distribution, exposure and recovery evidence boundaries remain. |
| `security-boundaries.md` | Retained; effect authorization, revocation and data-lifecycle limits remain. |
| `service-framework-checks.md` | Changed; separates general evidence reporting from Node and clarifies framework selection. |
| `simplify-and-clean.md` | Retained; its deletion test still protects useful short layers. |
| `types-and-invariants.md` | Retained; writer, consumer and supported-contract qualifications remain. |
| `understand-behavior.md` | Retained; actual paths and observed-versus-accepted behavior remain central. |

The added “deep module” wording supplies **recognition criteria**, not a rule to create larger modules, count methods, or infer quality from implementation size. Its presence is not proof that a model-training concept activated in a trial. Existing third-party notices were left unchanged; no loss of a required notice was established.

## Source review and local checks

A first requirements-first independent review read all fifteen originals and candidate targets and found no blocking defect. It disclosed narrower coverage of several connected bodies and did not itself establish that files outside the targets were unchanged. A separately prepared fresh connected-source assessment closed the requested route-coverage gap: it examined the governing guidance, connected methods, earlier selected changes and all five changed bodies, and found no supported compatibility defect. Its reported complete reads comprised 48 program-original bodies, six differing wave-baseline bodies and five changed candidate bodies, with identical-copy reuse stated rather than counted as another read. The coordinator mechanically checked the claimed source deliveries and ordering. These are qualified **source-eligibility** findings, not evidence of host triggering or useful application.

The coordinator checked the seven-file product integration: five method files and two manifests. The remaining tracked product bytes were unchanged. Three recorded version values align at `0.10.4`. Local checks passed **39 evaluator unit tests**, examined **229 local package link destinations** with none missing, and confirmed the headings for **three new fragment links**. Evaluator tests validate evaluator code; source-link checks do not establish browser rendering, external-link reachability, host loading or product behavior.

## Eight fixed native trials

The original schedule used two unchanged synthetic, design-only cases: a quote architecture boundary and a two-turn job-search recommendation revised after workshop switching and assignment removal were disclosed. Each source ran once per case on native Codex and Copilot, using Astra at medium effort with a 360-second trial bound. There were no outcome-driven reruns. “Completed” below means a terminal trial, **not a blanket PASS**; reviewers assessed activation, consultation, material outcome and authority separately.

| Attempt | Case | Source / host | Terminal time | Reviewed outcome and retained qualification |
| --- | --- | --- | ---: | --- |
| 01 | Quote architecture | Baseline / Codex | 80.8 s | Useful advisory note; first-write continuity notice incomplete. |
| 02 | Quote architecture | Candidate / Copilot | 69.614 s | Useful advisory note; first-write continuity notice incomplete. |
| 03 | Quote architecture | Candidate / Codex | 69.9 s | Useful advisory note; first-write continuity notice incomplete. |
| 04 | Quote architecture | Baseline / Copilot | 69.717 s | Useful advisory note; continuity was read, but its first-write notice was incomplete. |
| 05 | Search composition | Candidate / Codex | 201.6 s | Useful initial advice and substantive revision. |
| 06 | Search composition | Baseline / Copilot | 164.077 s | Useful initial advice and substantive revision. |
| 07 | Search composition | Baseline / Codex | 190.6 s | Useful initial advice and substantive revision. |
| 08 | Search composition | Candidate / Copilot | 138.089 s | Useful revision; incorrect source labels and incomplete first-write notice. |

For the quote case, all four notes inspected the implementation and both callers, kept independent estimates free of submission side effects, and preserved the interval between preparing a quote and approving it. They rejected silently repricing a saved quote at confirmation and identified the gap in comparing only aggregate prices when item changes offset. Proposed per-item checks and representation decisions were distinguished from existing behavior; no implementation or quote-runtime test occurred. Candidate attempts consulted and applied architecture reasoning, but both baselines also achieved the central caller-grounded outcome.

The original [continuity guidance](../../plugins/atlas/skills/atlas/references/continuity-and-decisions.md) calls for a first-write explanation that Atlas stores recovery notes, the actual location, and the option of another approved location. **All four quote attempts missed part of that notice.** Three did not retrieve the continuity body; attempt 04 retrieved it fully and still omitted the recovery explanation and alternative-location option. The real saved notes and useful recommendations do not erase those misses.

In the search case, the first-turn ten-minute persistent cache was a team proposal, not a measured need or accepted freshness policy. Initial recommendations varied: some conditionally considered sharing pending requests, while one baseline considered a conditional memory preview. After the follow-up, all four withdrew the mechanism that could disclose details under an outdated permission or context. Their revised notes clear previous-workshop details, reject late responses and saved-result resurrection, require current server permission before details on a new search, and keep client response guards distinct from server authorization. They continue to address waiting through conditional request handling while acknowledging missing workshop-binding details and unmeasured timing. These were proposed designs and checks, not implemented security or measured speedups.

Attempt 08 nevertheless reverses the README/API source labels in both note versions and attributes the single-workshop pilot to the API document rather than the README. It also names a note destination without the complete first-write recovery and alternative-location introduction. Relevant method use and a materially sound design revision do not make those defects disappear.

The first composition review was **partial**: it relied on limited reads and saw attempt 08 only through final prose. Its time-bound explanation is not supported by its terminal receipt, which records completion in **356.216 seconds** within a 1,200-second review bound; tool starts alone were not accepted as proof of successful consultation. A fresh review of the **same unchanged trials**, not producer reruns, completed in **839.843 seconds** and examined both artifact versions and focused native content and actions for all four attempts. The coordinator also checked the original fixture, resulting artifacts and turn returns, retaining the first review’s coverage limitation rather than treating it as a complete verdict.

## What this record supports

Wave 3 supports a narrow source-preservation and local-check result, plus useful outcomes in these fixed development cases. It does **not** establish a candidate-only gain, causal improvement, general implicit-routing reliability, regression freedom, live search latency, runtime quote or authorization correctness, rendering, compaction recovery or hosted Wave 3 behavior. Native host-stop receipts are not independent operating-system process-tree proof. Hosted package checks are reported on the pull request.

The documentation following the tested product commit adds this report and its evaluator-index link. Product bytes were checked against the tested revision and remain unchanged.
