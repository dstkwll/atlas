# Atlas Wave 5: authoring and validation

Atlas’s core guidance already distinguished exploration from implementation, accepted decisions from proposals, and source preservation from demonstrated behavior. Wave 5 addressed narrower recognition and navigation problems: recurring domain words can conceal different meanings; retained exploratory code can be mistaken for either a disposable probe or a proven outcome; and headings or links can give a selective reader the wrong scope. The selected **complete Opus 5.5/xhigh revision** changes four of nineteen Wave 5 targets and retains fifteen. Final cumulative source review found the five-wave source eligible, and the fixed Wave 5 cases produced useful bounded outcomes. Both original and candidate arms also succeeded at central tasks, while routing, notice, guidance-read and presentation gaps remain. **No candidate-caused improvement or general regression freedom is demonstrated.**

## Findings / selected proposal

The four selected changes are:

| Target | Selected explanation and preserved boundary |
| --- | --- |
| `SETUP.md` | List the already existing Wayfinding entry alongside the other optional entries. Only the shared Atlas core is preloaded; host permissions and source-recovery qualifications remain. |
| `plugins/atlas/skills/atlas/references/continuity-and-decisions.md` | Point interrupted-worker classification to the selected Wave 1 [inspection and recovery subsection](../../plugins/atlas/skills/atlas/references/deliver-and-repair.md#inspect-and-recover-worker-returns), rather than its broader parent section. Existing liveness, effects, authority, evidence and cumulative-bound rules remain. This link depends on the Wave 1 change and is not a standalone backport to unchanged 0.10.1. |
| `plugins/atlas/skills/atlas/references/discover-and-design.md` | Explain shared domain language through concrete cases, existing vocabulary, legitimate contextual meanings, ownership and the difference between proposed and settled terms. Explain how a walking skeleton or first slice intended to remain can serve as a tracer bullet, while distinguishing intended use and integration feedback from actual-use assurance or an observable outcome. No glossary, renaming sweep, architecture amendment or new implementation authority follows. |
| `plugins/atlas/skills/atlas/references/writing-agent-guidance.md` | Make heading scope and links to an owning section an explicit editing check for a selective reader, without imposing a template or moving all guidance into one file. |

The coordinator considered retaining the baseline, the complete Astra revision (three changed and sixteen retained targets), the complete Opus revision (four changed and fifteen retained), and a file-level blend. Astra’s shorter treatment and the existing probe, skeleton, slice and common-path rules were credible reasons not to add prose. The selected Opus wording was preferred for its concrete intended-use distinction, domain examples and cross-branch editing test—not for length, agreement between authors or trial wins. No coordinator-written product wording or blend was added. The final authors’ `SETUP.md` and continuity texts matched after peer exchange; that convergence is not independent corroboration.

### All nineteen Wave 5 target dispositions

Here and in the cumulative table, `R/` means `plugins/atlas/skills/atlas/references/`. “Retained” means byte-identical to the program original for that active target.

| Target | Disposition and relevant retained contract |
| --- | --- |
| `AGENTS.md` | **Retained:** repository authority, source recovery, scope, versioning and draft/merge boundaries. |
| `CONTRIBUTING.md` | **Retained:** authoritative homes, issue continuity and review workflow. |
| `README.md` | **Retained:** one lead, six optional entries, advisory outcomes and evidence limits. |
| `SETUP.md` | **Changed:** add Wayfinding to the existing entry list; preserve core-only preload and host/recovery caveats. |
| `.github/copilot-instructions.md` | **Retained:** portable maintenance pointer, without installed-product policy expansion. |
| `docs/writing-agent-guidance.md` | **Retained:** pointer to the canonical authoring method. |
| `plugins/atlas/README.md` | **Retained:** package scope and dependency promises. |
| `plugins/atlas/com.github.copilot/agents/atlas.agent.md` | **Retained:** main-session lead, core-only preload, canonical-source recovery and host controls. |
| `plugins/atlas/skills/atlas/SKILL.md` | **Retained:** selective composition, decision and delegation boundaries, whole-mission recovery and continued authorized work. |
| `plugins/atlas/skills/atlas-reflect/SKILL.md` | **Retained:** requested reflection, sibling dependency and explicit-only policy. |
| `plugins/atlas/skills/atlas-wayfinding/SKILL.md` | **Retained:** discovery entry in the same lead, shared methods and source recovery. |
| `R/arena.md` | **Retained:** bounded comparison, original brief, eligibility before preference, and no forced winner or extra rounds. |
| `R/continuity-and-decisions.md` | **Changed:** narrow the recovery link; retain the interrupted-work safeguards described above. |
| `R/discover-and-design.md` | **Changed:** add the domain-language and tracer-bullet explanations; retain probe/skeleton/slice differences, delegated judgment, acceptance and permission limits. |
| `R/guidance-improvement.md` | **Retained:** diagnose observed failures before making durable policy; distinguish source from behavior. |
| `R/reflect.md` | **Retained:** contextual, request-only retrospective without automatic policy promotion. |
| `R/specialist-runbooks.md` | **Retained:** conditional internal routing and composition; no new public roster or mandatory sequence. |
| `R/wayfinding.md` | **Retained:** adaptive inquiry, frontier/blocked/fog map, existing planning home and transition from suspended delivery. |
| `R/writing-agent-guidance.md` | **Changed:** clarify selective-reader heading/link scope under the existing [authoring standard](../../plugins/atlas/skills/atlas/references/writing-agent-guidance.md); retain recognition tests, local qualifications, examples, source homes and proportionate evidence. |

## Evidence

### Identity, process and cumulative coverage

The permanent program original—and the Wave 5 behavioral trial baseline—is `9dcf142d1ecdaac90394df9e9490b1e6e246187c`. The entering Wave 5 product is `cf4b959e7983d9776652e40b9ee777700935e6b5`. Its report-only integration parent, `cea9ff09c25e6ff36d4dcf760130b472999f1d69`, differs only by the Wave 4 public report and evaluation-index link. The tested final candidate is `1366134900c283a9781ac09708b89f2e784aed1d`, package **0.10.6**. All forty earlier-wave target bodies remain exact in that candidate; the only selected instructional edits are the four above.

Across five waves, **all thirty author phases completed**: for each wave, Astra/max and Opus 5.5/xhigh made independent drafts, critiqued one another after both drafts froze, then separately revised after both critiques froze. The complete Astra revisions were selected in Waves 1–4 and the complete Opus revision in Wave 5. Final revisions were *peer-informed*, not independent drafts or independent corroboration. Source reviews, behavioral reviewers, preflights, readers, diagnostic probes, fixed producer attempts and the repository’s evaluator unit tests are separate populations.

The following is the cumulative **active-surface** disposition, not a claim that Wave 5 newly changed earlier files. It accounts for every target against the program original: **20 changed and 39 retained by byte comparison**. The Wave 5 table above supplies the nineteen local rows; this table supplies the forty earlier-wave rows.

| Wave | Active target | Final byte disposition |
| --- | --- | --- |
| 1 | `R/deliver-and-repair.md` | **Changed** — worker-return inspection and recovery structure. |
| 1 | `R/coordinate-work.md` | **Retained**. |
| 1 | `R/independent-review.md` | **Retained**. |
| 1 | `R/test-adequacy.md` | **Retained**. |
| 1 | `R/project-verification.md` | **Changed** — general return made visible. |
| 1 | `R/failure-handling.md` | **Changed** — recovery cases and return structure clarified. |
| 2 | `plugins/atlas/skills/atlas-handoff/SKILL.md` | **Retained**. |
| 2 | `plugins/atlas/skills/atlas-to-documentation/SKILL.md` | **Retained**. |
| 2 | `plugins/atlas/skills/atlas-to-tickets/SKILL.md` | **Retained**. |
| 2 | `plugins/atlas/skills/atlas/assets/prd-starter.html` | **Retained**. |
| 2 | `R/artifact-location.md` | **Changed** — existing-home reuse, destination fallback and first-write route. |
| 2 | `R/handoff.md` | **Changed** — conditional route to ticket-plan readiness. |
| 2 | `R/html-document.md` | **Retained**. |
| 2 | `R/to-documentation.md` | **Retained**. |
| 2 | `R/to-prd.md` | **Retained**. |
| 2 | `R/to-tickets.md` | **Changed** — whole-plan readiness distinction. |
| 3 | `plugins/atlas/skills/atlas-blast-radius/SKILL.md` | **Retained**. |
| 3 | `R/architecture-design.md` | **Changed** — deep-module recognition through same-task caller knowledge, plus precise decision links. |
| 3 | `R/blast-radius.md` | **Retained**. |
| 3 | `R/build-and-runtime-diagnosis.md` | **Changed** — uncertain-effect retry link. |
| 3 | `R/client-state-checks.md` | **Changed** — cross-framework transition scope. |
| 3 | `R/data-and-migrations.md` | **Retained**. |
| 3 | `R/language-runtime-checks.md` | **Changed** — general return separated from Swift. |
| 3 | `R/performance.md` | **Retained**. |
| 3 | `R/reconstruct-rationale.md` | **Retained**. |
| 3 | `R/release-preparation.md` | **Retained**. |
| 3 | `R/security-boundaries.md` | **Retained**. |
| 3 | `R/service-framework-checks.md` | **Changed** — general reporting separated from Node. |
| 3 | `R/simplify-and-clean.md` | **Retained**. |
| 3 | `R/types-and-invariants.md` | **Retained**. |
| 3 | `R/understand-behavior.md` | **Retained**. |
| 4 | `plugins/atlas/skills/atlas/assets/diagram-starter.html` | **Retained**. |
| 4 | `R/data-visualization.md` | **Changed** — evidence and consequence in chart findings. |
| 4 | `R/diagram-craft.md` | **Retained**. |
| 4 | `R/documentation-and-references.md` | **Changed** — general return exposed outside conditional comparison. |
| 4 | `R/model-and-retrieval-quality.md` | **Changed** — general evaluation return exposed. |
| 4 | `R/model-post-training.md` | **Changed** — stall diagnostics placed with diagnostics; general return exposed. |
| 4 | `R/product-design-review.md` | **Retained**. |
| 4 | `R/user-journeys.md` | **Retained**. |
| 4 | `R/user-research.md` | **Changed** — existing plan-or-synthesis return exposed. |

Thus the per-wave changed/retained counts are **3/3, 3/7, 5/10, 5/4 and 4/15**. Sixty-five other original files are separately classified as historical, evaluation or package metadata; they are not additional rewritten guidance surfaces.

The earlier public records support narrower, wave-specific conclusions, not new Wave 5 behavioral evidence:

| Earlier wave | Recorded result that remains qualified |
| --- | --- |
| [1 — delivery and assurance](wave-1-authoring.md) | Offline and interrupted-return repairs were useful in both sources; they did not establish improvement, physical or remote acceptance, or exhausted-bound behavior. Heading-scope reading risks and a candidate Copilot close without the literal `Next` paragraph remained. |
| [2 — artifact, ticket and handoff](wave-2-authoring.md) | HTML planning preserved accepted and open decisions. Ticket artifacts had consequential return-contract, source-attribution or dependency-gate qualifications. One candidate Copilot ticket/handoff attempt timed out without a conversational return; its written artifacts do not replace that return. |
| [3 — technical methods](wave-3-authoring.md) | Eight design attempts gave useful quote and search advice, including successful baselines. First-write notices and one search source attribution remained deficient; neither runtime correctness nor improvement was established. |
| [4 — specialist methods](wave-4-authoring.md) | Twelve attempts gave useful advice with successful baselines. The activity screen-coverage omission, incomplete evaluation-independence checks and guidance/host-read qualifications remained; no causal gain or rendered, participant or held-out result was established. |

### Final source assessment

The first independent Opus source assessment was useful **locally**, but it did not read the forty earlier-wave originals. It read nineteen local originals, reused fifteen identical local bodies and reconstructed four changed candidates from originals and the complete local diff rather than directly reading those four candidate bodies. Its original-to-entering patch read was partial. Its completion and local no-blocker finding were not a complete cumulative review.

A fresh independent Astra/max assessment supplied the missing scope without the first verdict, author notes, selection narrative or current trial outcomes. Original-derived requirements preceded candidate access. All **59 original target bodies** were delivered, as were the relevant charter and accepted decisions. Of the candidate targets, it directly read all **20 changed full bodies**, including the four local changes, and reused **39 verified byte-identical originals**. All forty-four mandatory originals—forty earlier-wave targets plus four changed local targets—were fully delivered. Named original/candidate hashes supported each reuse; identity did not substitute for examining connected responsibilities, callers and retained obligations. That examination found no supported blocking or nonblocking source defect, and the final root source disposition accepts source eligibility.

The coverage remains precise rather than absolute. The identity packet incorrectly marked generic `byteIdentical` true for four changed local files; the reviewer noticed, directly read them and used the correct named hash fields for reuse. Its cumulative-diff read omitted one final blank context line, not substantive diff text. Historical patches and reports were read selectively, so the review was source-first, not wholly historically blinded. Neither source reviewer ran product code or audited packaging, licensing, external destinations or runtime behavior comprehensively. The earlier suggestion that no additional notice was required is not accepted as a legal conclusion, because notices were not audited. No notice was removed and no concrete missing distribution notice was established. Separately, the suggested intended-use declaration near a probe statement was optional, not a new artifact requirement. **Whole-source availability, delivered bodies, verified byte reuse and semantic source judgment are separate claims; source eligibility is not demonstrated agent adherence.**

### Fixed Wave 5 behavior

Sixteen scheduled attempts ran once with actual Astra/medium, a 360-second whole-attempt bound, and no outcome-driven reruns: each of four synthetic cases used original and candidate sources on Codex and Copilot. All sixteen completed. The two source copies had matching read-only guidance modes before inference. Completion and mechanical identity or file-effect checks are not behavioral grades. Four independent behavioral assessments completed; the final root behavior disposition qualifies their broad labels against native actions, returns and artifacts.

| Case | Useful observed outcome in original and candidate arms | Retained distinction or miss |
| --- | --- | --- |
| Hall calendar and Wayfinding, four three-turn attempts | All challenged a live-availability promise using the export, paper diary and missing holds; compared room-first and date-first directions; incorporated the owner’s volunteer/caretaker, no-reservation and timestamp decisions; kept unconfirmed visibility open; and continued design in the existing HTML rather than implementing or creating a second map. | Both Codex attempts omitted applicable user-research and product-interface method bodies before dependent work. Both Copilot attempts obtained them; an early high-level comparison preceded product-interface consultation, but detailed status/action treatment followed it. Candidate Copilot’s recovered discovery read still missed 65 characters about an unperformed probe, with no established downstream design failure. Candidate Codex’s first-write recovery purpose was less explicit, although path and alternative were supplied. |
| Archive pause and fresh-session recovery, four three-turn attempts | All paused the prior delivery, kept imported labels as exact paper-sheet lookup keys, produced a checkpoint within 120 words without a question, then used saved files in a **distinct native session** to complete only the authorized exact-empty-title correction. Each witnessed a failing regression and passing rerun, retained nonempty strings and return shape, left retention `None`, and updated the same record. | Candidate Codex’s fresh-session lead read has an unresolved gap despite recovered continuity and useful completion. Original Codex used overbroad checkpoint wording attributing more naming resolution to the owner than was settled; its patch did not implement extra policy. Both Copilot replies omitted the standing `Next` paragraph, although they stated completion and open wider questions, and their records stated no correction work remained. Host test permissions differed; this is file-based session recovery, not compaction proof. |
| Arena finalists, four one-turn attempts | All saved a recommendation and declined a qualifying winner: Lumen required hosted processing, Feather discarded invalid rows, and Halo had not established rejected-row lifecycle or all-invalid accounting. Halo remained conditional, with the accepted offline, row, error, edit, export and disposal requirements intact. No new workers, rounds or implementation followed. | All four omitted the first-write recovery/location-choice notice; none consulted the continuity body. One candidate Copilot read an earlier artifact-location pointer without applying that notice. Both Copilot conversational closes lacked explicit forward orientation, though their saved records supplied closure and later-repair conditions. A durable recommendation does not require a second artifact. |
| Exact-output typo control, four one-turn attempts | All returned only `The reports are ready.`, with no artifact, reference tour, file read or mutation. Codex made no tool calls; Copilot redundantly invoked the supplied Atlas skill, without a file tool. | The selected lead bytes were unchanged and no changed reference was consulted. This tests the exact-output exception and observed scope, not the effect of Wave 5 edits, an Atlas-caused answer or general regression freedom. |

The calendar and archive outcomes are bounded design and local-code observations, not measured resident benefit or completion of the wider designs. The Arena recommendations are decisions about supplied alternatives, not live tournament supervision or implemented CSV behavior. Consultation, useful application and successful baseline behavior must not be collapsed into evidence that new wording caused an improvement. No direct native case isolates the shared-domain-language or tracer-bullet additions; neither a training-data keyword effect nor a particular book’s presence in training was established.

## Uncertainty

Review coverage and native delivery were not universally direct whole-trace reads. Calendar review’s projected trace omitted separately available artifact-location prose. Archive review reconstructed candidate files from delivered originals and successful patches rather than directly opening every final whole file; targeted native guidance and test-return samples are not complete reads. Its broader PASS wording does not erase the candidate lead gap, original attribution wording or Copilot presentation omissions. Arena’s complete recommendation artifacts and central decisions were checked, while separately captured Copilot tool/permission files were absent. In the typo review, duplicate artifact indexes were auditor-verified rather than all directly opened by the assessor, and Copilot trace reading was bounded. These limits qualify *how* evidence was obtained; they do not negate the specified observed returns or artifacts.

Across the program there were **52 fixed behavioral attempts: 51 completed and the preserved Wave 2 candidate Copilot ticket/handoff timeout at its declared bound**. Wave counts were 8/8, 7/8, 8/8, 12/12 and 16/16 completed/scheduled. There was no rerun to turn the timeout into a return. These counts are neither a pass rate nor a pool combining author phases, source reviews, behavioral reviewers, preflights, readers, diagnostic probes or evaluator tests.

The cases were explicitly activated synthetic development/regression exercises. They do not establish unscripted routing, natural long-session reliability, context compaction, workplace/IDE or profile loading, rendering and usability, actual participant outcomes, generic runtime correctness, held-out performance, host effects or causal improvement. Earlier-wave limitations remain attached to their own records. The broader reported routing-reliability issue remains open; the final dispositions found no required source loss or new product defect calling for another author round, without converting these observations into an overall behavioral PASS.

## Verification and integration boundary

Recorded checks on the tested Wave 5 candidate show **39 existing evaluator unit tests passing once**, a clean diff check, **229 package-local paths** and **22 applicable fragments** checked, and all three version fields at **0.10.6**. The source identity check accounted for **130 tracked files**, **124 unchanged against the report-only parent**, the four selected guidance files and two version-manifest files, all nineteen Wave 5 target identities and all forty earlier target identities. These are static, evaluator and integration checks—not behavioral scores, rendered results, host checks or a comprehensive licensing audit.

The final root dispositions retain the tested candidate and the fixed trials without a further product edit, producer rerun or author wave. This report describes that record; it does not claim a later report commit, merge, hosted check, installed-copy change or release. Public [evaluator context](../../evals/README.md) and the [authoring review rubric](../../evals/wave-authoring-review.md) remain distinct from the observed outcomes and final root judgments.
