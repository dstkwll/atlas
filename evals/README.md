# Atlas behavior evaluation pilot

This is a small maintainer tool, outside the installed plugin. It measures what current Atlas guidance does in actual native Codex sessions. It does not enforce a workflow in Atlas or prove reliability across hosts/models.

The initial twelve tasks in cases.json separate ordinary work from nearby cases requiring diagnosis, caution or deeper discovery. They include actual PRD, ticket, handoff and repair artifacts, multi-turn agreement, uncertain local writes and native compaction. Expected behavior lives in review.md, never in the trial project. The model receives only the raw task, synthetic fixture, local operating boundaries and the selected skill. No hidden assertions or grader feedback are supplied to the model.

## Run

Prerequisites: Python 3.11+, the Codex CLI, an existing authenticated account with local auth.json, and the selected model available to that account. Native trials consume account usage. No extra packages, login, plugin installation or workplace access is performed. The checked host is recorded in each trial's metadata; the app-server protocol is experimental, so an incompatible host is a setup failure, not an Atlas failure.

```sh
python3 -m unittest discover -s evals -p 'test_*.py' -v
python3 evals/run.py --case repair --case continue --model gpt-5.6-sol --effort low --output /tmp/atlas-trial
```

Use a new output directory for every invocation. Repeat --case to choose tasks; --repeat accepts 1–3. Default native time limit is 300 seconds per trial, with an explicit maximum of 600. The pilot schedule is one run per case plus two additional repair and continue runs, regardless of their behavioral results, after the runner is operational. Extra runs after harness repairs are diagnostic/replacement runs and must be labeled rather than silently dropped. A later `continue-ack` variant tests the shorter “Agreed! Thanks!” follow-up against authority supplied in the first turn; report it separately from the preselected schedule. No pass-rate or causal improvement claim is intended from these small counts.

Each trial gets a new workspace, CODEX_HOME, app-server process and fresh thread in that disposable home. Only existing authentication is copied into the temporary home; it is removed after the host stops, and never copied into evidence. Host configuration/history, installed user skills and MCP integrations are not copied. Standard Codex model instructions remain active. Every initial turn selects a project-local skill using native skill input; subsequent turns are plain conversation. This tests explicit skill activation, not automatic discovery from an unadorned prompt, a native Copilot profile or an IDE picker.

The filesystem is the normal native workspace-write sandbox, not a security isolation experiment. The project instruction excludes other projects, user-profile sources, network operations, software installation, delegation and background services. External-write behavior is modeled by a local outbox. Attempts outside authority are failures even if blocked. No personal or work data belongs in fixtures.

## Evidence and grading

The output retains raw native events, tool-call/output records filtered from the native rollout (no reasoning or instruction messages), stderr, prompts/metadata, candidate and runner file identities, per-turn file snapshots, final artifacts and objective facts. The filtered rollout has a tool-records-status.json recording file/record counts and parse errors; a parse-clean capture does not guarantee the host persisted every event. Without usable tool evidence, missing consultation remains UNKNOWN. File snapshots record content hashes, file kind, permission mode and symlink targets, excluding Git internals and Python bytecode. Final change-scope facts include any effects from the evaluator’s repair probe; probe_changes identifies those separately and must not be attributed to the agent’s native turn. They detect retained mutations to the observed project, not every transient write or effect outside it. The host's process group is terminated before final checks; this does not establish absence of deliberately detached descendants. Inspect tool events for such behavior and mark affected state claims UNKNOWN if quiescence cannot be established.

The repair checker runs candidate Python in the synthetic project, under the invoking operator's permissions. This is for trusted local fixtures and bounded non-adversarial trials, not arbitrary hostile code. Do not run it on an untrusted submission. Other checks inspect state without running generated code.

Exit 0 means native turns completed; exit 2 means one or more host trials were blocked. Neither is a behavioral pass. Inspect result.json facts, then apply review.md to completed events and actual artifacts with independent judgment. Failed setup, unavailable traces and unreviewed behavior remain explicit. There is intentionally no keyword-based routing grader, numeric quality score or automatic behavioral PR gate.

The fast tests challenge the objective checks with a real failing boundary, valid alternative repairs, missing/empty-quality artifacts, duplicate writes and forbidden edits/deletion/mode/symlink changes. They test evaluator sensitivity, not model adherence. The separate calibration examples challenge the judgment rubric. Agent assertions and the evaluator's own successful test do not prove that the agent ran that test.

For comparisons, hold task/fixture, host, model, effort, initial instruction source and tooling constant; retain both candidate identities and individual results. Do not feed prior trial outcomes into fresh sessions. A comparative/causal claim requires a suitable baseline; this initial pilot is descriptive. Add held-out task variants before tuning routing on these examples. Test additional models or Copilot only as separately identified conditions, not pooled successes.

Raw runs are local-only and ignored under evals/runs/. They can contain host metadata, local paths or unexpected content; review and sanitize any excerpts before publishing. Keep a concise sanitized result report under docs/validation/. Synthetic reusable cases, runner, assertions and rubric belong in this repository because maintainers need reproducible proof; private donor research does not.

For a compact review packet, run `python3 evals/review_packet.py /tmp/atlas-trial/repair-1`. It cites raw event lines and marks clipped outputs; inspect raw evidence before resolving claims that depend on omitted content.

## Pull request checks

The **Evaluator correctness** GitHub Actions check runs the fast unittest command on every pull request and pushes to main, using Python 3.11 on Ubuntu. It needs no Codex installation, model authentication or inference. A green check establishes evaluator correctness for the tested cases, not Atlas adherence. The workflow does not configure repository rules requiring the check before merge; maintainers can enable that once it is established.

Behavioral trials remain optional, local maintainer evidence. Choose relevant cases before running: routing changes warrant activation and trivial-task cases; discovery changes warrant agreement and scope-boundary cases; ticket guidance warrants artifact and accepted-decision review; recovery changes warrant retry and uncertain-write cases. For consequential guidance changes, compare main and the candidate under matching conditions as described above. Retain every attempt, including failures and setup problems, rather than rerunning until a case passes.

Keep exact revisions, candidate differences, host/model settings, repetition counts, raw prompts, setup diagnostics and review history in local maintainer evidence. Public PR descriptions and `docs/validation/` summaries should state the behavior covered, concise observed results and material limitations; include environment details only when needed to interpret compatibility. Separate executed checks from source review and unverified claims. Later changes affecting tested behavior require fresh evidence or a clear qualification of what remains untested. Do not copy trial logs, personal conversation excerpts or machine-specific paths into public documentation, and do not make product use depend on private records.

Native trials currently depend on local account authentication and execute synthetic project code. Hosting them in Actions would require a separate authentication and isolation design. There is no credentialed model workflow or automatic behavioral merge gate in this pilot.

The `continuity` and `continuity-no-write` cases cover unprompted task records and the explicit write prohibition. See [native Copilot continuity evidence](../docs/validation/continuity.md) for separate profile activation trials, source revisions and observed limits. The rubric requires actual record content and update notices; planning-only change facts alone cannot establish success.

The `partial-agreement` and `notes-to-prd` cases probe acceptance boundaries through tickets and continuity across a PRD amendment. See [planning-transition observations](../docs/validation/guidance-consistency.md) for separate native Copilot profile results, intermediate misses and recovery limits.

See [capability coverage and limits](../docs/validation/documentation-and-reflection.md) for documentation, reflection, impact assessment and Arena checks, including [brief alignment through revisions](../docs/validation/documentation-and-reflection.md#arena-brief-alignment).

See [turn-ending guidance checks](../docs/validation/turn-ending-guidance.md) for conversational progression, closing guidance and resumption limits.

The `discovery-frontier` and `discovery-delegated` cases examine collaborative exploration and explicitly delegated planning. See [collaborative discovery observations](../docs/validation/collaborative-discovery.md) for the matched samples, diagnostic follow-up and remaining limitations.

The `design-visible-choices`, `specialist-activity-triggers` and `design-constrained-choice` cases cover spontaneous visible comparison, activity-based specialist selection and a nearby case that needs no alternatives. Grade actual responses, successful source reads and artifacts with the semantic criteria in `review.md`. See [trigger and design observations](../docs/validation/runbook-triggers-and-visible-design.md) for coverage and remaining limitations.

The twenty-two `specialist-*` cases documented in [the specialist rubric](specialist-review.md)
exercise product critique, real-user research, feedback evidence, sensitive-data and
identity lifecycles, recovery, charts, localization, command-line use, post-training,
model-tool authority, unit cost, retrieval candidates and test-result reconciliation.
Four nearby negative controls and a two-turn activity transition
check selectivity as well as coverage. They use the existing native runner and file
scope observations; their semantic rubric stays outside trial projects. The older
`specialist-activity-triggers` case remains separate and unchanged.
The fixed-text endpoint and caller-selected download cases are diagnostics
added after source review, separately identified in the rubric; they are not held-out
evidence from the initial nineteen-case selection.
The archive-transcription UI variant was prepared independently after a prior UI
failure without reading the revised design method. It is a fresh diagnostic scenario,
not fully blinded or held-out evidence; the prior twenty-one cases are unchanged.

The extended discovery scenarios exercise longer conversations, a fictional provider contract, wrong-problem proposals, paired authority conditions, and planning transitions. `transition-chain` starts a new native thread before its final recovery turn (`fresh_thread_before`, zero-based), reselects the local skill, and retains the generated workspace without copying conversation messages. Metadata records both thread IDs. This is artifact-based recovery in the same project, not a claim that the handoff file alone is sufficient. See the extended rubric in review.md before interpreting results.

See [extended discovery and transition observations](../docs/validation/discovery-transitions.md) for completed scenario coverage, verified planning defects, correction scope and model/host limitations. `transition-plan-replay` is a diagnostic using a fixed generated PRD; it must not be reported as held-out generalization.

The four `mission-*` cases cover a direct implementation route, a warranted feasibility probe, recovery after a successful probe, and an exhausted inconclusive investigation. Expected behavior is specified in `review.md`. The recovery case uses a fresh native thread with existing project artifacts; it does not emulate long-session compaction. See [mission continuity observations](../docs/validation/mission-continuity.md) for results and limits.

Ledger recovery coverage: `ledger-disposable-driver`, `ledger-required-fixture`, and `ledger-stale-source` exercise different artifact roles and a historical passing report for changed code. Their objective checks include signed decimal previews, local export and source preservation when destination aliases input. The [review rubric](review.md#ledger-recovery-and-evidence-applicability) separately evaluates actual report consumption, applicability and candidate identity. See [coverage evidence](../docs/validation/ledger-recovery.md) for sensitivity results and limits.

The [direct/delegated review pilot](delegation-review.md) prepares matched packets
for direct runbook use, a bounded worker and an identical saved reviewer contract.
It reuses evaluator snapshots but needs a host/operator with actual fresh-worker
support; `run.py` keeps its no-delegation boundary. Preparation and endpoint facts
are not model trials or behavioral grades.

See [observations and limits](../docs/validation/delegation-comparison.md) for the
initial Work Mode pilot, including blocked setup and incomplete timing evidence.

See [specialist integration observations](../docs/validation/specialist-methods.md) for completed native coverage, retained interruptions and pending acceptance.

The `composition-onboarding` and `composition-reveal` cases exercise combining
interface, identity and approval concerns, then revising a search proposal when
new access constraints emerge. Their [semantic rubric](composition-review.md)
was prepared independently of the candidate instructions and stays outside trial
projects. It distinguishes useful integration from consultation, including valid
alternative designs and authority limits. See [lead composition observations](../docs/validation/lead-composition.md)
for the matched comparison and its limits.

The later `guidance-truncated-read` diagnostic reuses onboarding with an induced
first-read output limit. Its [recovery rubric](composition-review.md#truncated-guidance-diagnostic)
separates actual clipping and timely recovery from task quality, and records the
prompt's attention cue. It is not an independent natural-request routing test.

The three `wayfinding-*` cases cover a changing collaborative design conversation,
artifact-based recovery followed by an explicit implementation request, and a
bounded synthesis/pause. Their [independently prepared rubric](wayfinding-review.md)
requires trace and per-turn artifact review; endpoint checks alone cannot establish
mode continuity or conversational quality. The candidate uses `atlas-wayfinding`;
a pre-capability baseline uses `atlas`, with that activation difference disclosed.
The later `wayfinding-summary-continuity` diagnostic checks a progress summary
through the shared Atlas entry after source-review clarifications; it is separate
from the original suite. See [Wayfinding observations](../docs/validation/atlas-wayfinding.md)
for native host coverage and remaining limits.

The later `wayfinding-seed-catalog` scenario compares the same explicit entry
before and after a prose revision, using a new four-turn catalog conversation.
Its [rubric](wayfinding-review.md#seed-catalog-revision-scenario) covers a changed
premise, partial acceptance, a short checkpoint and continued discovery.


The `arena-core-calendar` and `arena-core-recovery` cases check connected lead,
discovery, Wayfinding and continuity behavior during a writing revision. They use
an existing HTML planning home, changed premises, partial acceptance, a suspended
authorized correction and fresh-thread recovery followed by narrow delivery. The
[semantic rubric](core-authoring-review.md) separates preservation and practical
usefulness from consultation, saved-file presence and host completion. Raw fixture
material stays separate from reviewer expectations. Reuse of an established
regression boundary limits claims that these are wholly independent benchmarks.

See [connected-core authoring observations](../docs/validation/connected-core-authoring.md)
for the matched native comparison, file dispositions and preservation limits.


The `atlas-wave1-interrupted-return` case supplies a partially completed local
integration and unresolved operation evidence with remaining repair/test bounds.
Its [rubric](wave-authoring-review.md) distinguishes a verified local repair from
whole-task acceptance, request records from remote effects, and substantive
changes from truthful bookkeeping. See [wave-1 observations](../docs/validation/wave-1-authoring.md)
for the matched comparison with `hardware-deferred-repair` and its limits.

See [wave-2 planning-artifact observations](../docs/validation/wave-2-authoring.md)
for the fixed `notes-to-prd` and `transition-plan-replay` comparisons, separate
HTML-only readers, complete-artifact review, and retained mixed outcomes.

See [wave-3 technical-method observations](../docs/validation/wave-3-authoring.md)
for source selection, the fixed architecture/composition trials, and their limitations.
