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

The output retains raw native events, tool-call/output records filtered from the native rollout (no reasoning or instruction messages), stderr, prompts/metadata, candidate and runner file identities, per-turn file snapshots, final artifacts and objective facts. The filtered rollout has a tool-records-status.json recording file/record counts and parse errors; a parse-clean capture does not guarantee the host persisted every event. Without usable tool evidence, missing consultation remains UNKNOWN. File snapshots include content, file kind, permission mode and symlink targets, excluding Git internals and Python bytecode. Final change-scope facts include any effects from the evaluator’s repair probe; probe_changes identifies those separately and must not be attributed to the agent’s native turn. They detect retained mutations to the observed project, not every transient write or effect outside it. The host's process group is terminated before final checks; this does not establish absence of deliberately detached descendants. Inspect tool events for such behavior and mark affected state claims UNKNOWN if quiescence cannot be established.

The repair checker runs candidate Python in the synthetic project, under the invoking operator's permissions. This is for trusted local fixtures and bounded non-adversarial trials, not arbitrary hostile code. Do not run it on an untrusted submission. Other checks inspect state without running generated code.

Exit 0 means native turns completed; exit 2 means one or more host trials were blocked. Neither is a behavioral pass. Inspect result.json facts, then apply review.md to completed events and actual artifacts with independent judgment. Failed setup, unavailable traces and unreviewed behavior remain explicit. There is intentionally no keyword-based routing grader, numeric quality score or automatic behavioral PR gate.

The fast tests challenge the objective checks with a real failing boundary, valid alternative repairs, missing/empty-quality artifacts, duplicate writes and forbidden edits/deletion/mode/symlink changes. They test evaluator sensitivity, not model adherence. The separate calibration examples challenge the judgment rubric. Agent assertions and the evaluator's own successful test do not prove that the agent ran that test.

For comparisons, hold task/fixture, host, model, effort, initial instruction source and tooling constant; retain both candidate identities and individual results. Do not feed prior trial outcomes into fresh sessions. A comparative/causal claim requires a suitable baseline; this initial pilot is descriptive. Add held-out task variants before tuning routing on these examples. Test additional models or Copilot only as separately identified conditions, not pooled successes.

Raw runs are local-only and ignored under evals/runs/. They can contain host metadata, local paths or unexpected content; review and sanitize any excerpts before publishing. Keep a concise sanitized result report under docs/validation/. Synthetic reusable cases, runner, assertions and rubric belong in this repository because maintainers need reproducible proof; private donor research does not.

For a compact review packet, run `python3 evals/review_packet.py /tmp/atlas-trial/repair-1`. It cites raw event lines and marks clipped outputs; inspect raw evidence before resolving claims that depend on omitted content.

## Pull request checks

The **Evaluator correctness** GitHub Actions check runs the fast unittest command on every pull request and pushes to main, using Python 3.11 on Ubuntu. It needs no Codex installation, model authentication or inference. A green check establishes evaluator correctness for the tested cases, not Atlas adherence. The workflow does not configure repository rules requiring the check before merge; maintainers can enable that once it is established.

Behavioral trials remain optional, local maintainer evidence. Choose relevant cases before running: routing changes warrant activation and trivial-task cases; discovery changes warrant agreement and scope-boundary cases; ticket guidance warrants artifact and accepted-decision review; recovery changes warrant retry and uncertain-write cases. For consequential guidance changes, compare main and the candidate under matching conditions as described above. Retain every attempt, including failures and setup problems, rather than rerunning until a case passes.

Include a concise sanitized report in the PR description or link a report under `docs/validation/`. Identify the exact tested revision (and any uncommitted candidate changes), host, model/effort, selected cases and repetition count. Separate native execution status, objective facts, reviewed routing/behavior findings, and UNKNOWN or UNREVIEWED claims; cite evidence for findings and state who reviewed it. Later commits affecting the tested behavior require fresh evidence or an explicit statement that the report covers an earlier revision. Do not upload raw trial directories automatically.

Native trials currently depend on local account authentication and execute synthetic project code. Hosting them in Actions would require a separate authentication and isolation design. There is no credentialed model workflow or automatic behavioral merge gate in this pilot.

The `continuity` and `continuity-no-write` cases cover unprompted task records and the explicit write prohibition. See [native Copilot continuity evidence](../docs/validation/continuity.md) for separate profile activation trials, source revisions and observed limits. The rubric requires actual record content and update notices; planning-only change facts alone cannot establish success.

The `partial-agreement` and `notes-to-prd` cases probe acceptance boundaries through tickets and continuity across a PRD amendment. See [planning-transition observations](../docs/validation/guidance-consistency.md) for separate native Copilot profile results, intermediate misses and recovery limits.

Documentation routing, reflection persistence, impact assessment, Arena confirmation and acknowledgment continuation have reusable cases and manual criteria. See [capability observations](../docs/validation/documentation-and-reflection.md) for native Copilot evidence, including the unresolved acknowledgment failure and picker limitations.

[Turn-ending guidance](../docs/validation/turn-ending-guidance.md) evaluates the actual naming decision, ordinary design progression, short replies, corrections and pauses with native Copilot profile conditions. It separates source availability from use and judges useful guidance rather than phrase matches.
