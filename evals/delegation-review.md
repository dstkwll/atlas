# Direct versus delegated review pilot

This maintainer-only experiment asks whether a saved specialist contract improves
one recurring failure-handling review over the existing runbook/worker contract.
It adds no installed role, model choice, runtime or product policy. It is a
diagnostic pilot, not an architectural contest or reliability estimate.

## Prepare and execute

```sh
python3 -m unittest discover -s evals -p 'test_*.py' -v
python3 evals/delegation.py prepare --output /tmp/atlas-delegation-pilot
python3 evals/delegation.py observe /tmp/atlas-delegation-pilot/trial-01
```

Preparation creates nine fresh workspaces and an operator-only schedule. It does
not invoke a model, configure a native named-agent registry, copy credentials or
change `run.py`'s no-delegation boundaries. The existing native Codex runner is
not a driver for these packets. Use a host that explicitly supports fresh workers
and record its actual execution evidence. If unavailable, record BLOCKED; never
substitute persona switching or three differently worded single-agent answers.

Give each fresh lead only its absolute workspace path and the instruction to read
`AGENTS.md` and `task.md`. No inherited conversation or grader findings. Use the
same available model and reasoning setting for leads and workers, without model
overrides. Keep tools/capabilities comparable. The operator records actual settings,
any unavailable model metadata, start/end times, session and worker identifiers,
exact input, final returns and tool evidence where accessible outside workspaces.
Do not put this file, the evaluator or schedule in a lead or worker's context.

The schedule rotates conditions across three neighboring scenarios, once per
cell. Run conditions sequentially if concurrency changes tool access or resource
contention; otherwise record the concurrency used and do not treat elapsed times
as controlled latency measurements. Stop each trial at 180 seconds across lead
and worker together. No repair rounds, replacement trials after behavioral misses,
new dependencies or additional experiments. Preserve setup failures separately.
Deadline enforcement is the operator/host's responsibility; the prompt itself
does not enforce it. Reserve host capacity for each lead's required worker before
starting that trial. If a worker launch is rejected, record setup BLOCKED and do
not score a lead-only substitute as that delegated treatment. A late completion
receipt without a trustworthy finish timestamp leaves deadline adherence unknown. A blocked setup can be repaired, but keep the original attempt
and label a subsequent attempt rather than replacing an unfavorable result.

| Condition | Intervention |
| --- | --- |
| direct | A fresh lead applies the common contract and runbooks itself. |
| briefed | A fresh lead delegates to one fresh worker with the verbatim contract and workspace path, then integrates the return. |
| defined | A fresh lead delegates to one fresh worker told to load a saved specialist definition containing that identical contract, then integrates the return. |

Every packet contains the same role file, runbooks and case-specific sources.
No condition receives extra domain knowledge or a better acceptance rubric.
Worker history is fresh, but filesystem visibility is shared; it can read task.md.
The role-file treatment measures reusable contract invocation, not a trained
specialist, private memory, restricted tools, autonomous routing or a host's named
agent registration. A separate native-profile experiment would be needed for those.
The direct lead is also independent of the candidate producer. Review independence
is therefore not reserved for the delegated arms.

## Outcome assessment (withhold from executing agents)

Inspect the final review and actual source/probe evidence before checking the
condition mapping. Preserve raw outputs. Use a fresh assessor that did not author
the fixture, candidate, or trial results. Judge claims on merit, without a required
wording, heading, finding count or numeric score standing in for correctness.

| Scenario | Evidence-sensitive expected assessment |
| --- | --- |
| regression | New idempotency key per retry duplicates effects after an acknowledged-lost commit; truthiness of a rejected reply falsely returns complete, which caller.py accepts. Check a concrete triggering trace for each. Do not demand particular severity labels. |
| control | Stable key, authoritative cached response, explicit rejection and bounded unknown result satisfy the supplied contract. No defect is required. Catching TimeoutError and missing a local deadline are not automatically findings given the stated caller/provider guards. |
| uncertain | Production deduplication retention is unspecified. A local passing fake does not substantiate production retry safety. Identify this evidence/contract gap without claiming a demonstrated duplicate in the fake, inventing a retention interval, or insisting on a particular repair. Other supported behavior remains assessable. |

For each trial record: supported defects found/missed; unsupported defect claims;
correct treatment of unknown requirements; endpoint write-scope facts; observed
runbook consultation versus useful application; and final acceptance judgment.
Use UNREVIEWED/UNKNOWN for missing evidence, never assume a transcript omission is
proof of omission. Retain legitimate additional findings if supported by a reachable
path under the actual contract; the two seeded defects are not a finding quota.

For delegated arms separately inspect the worker return and lead synthesis: which
valid findings survived, which were dropped or distorted, and whether the lead
checked artifacts. Count actual workers/repair interactions from host receipts,
not self-reported role labels. Note duplicated investigation and integration effort.
Record operator elapsed time and human interventions. Token usage, reasoning tokens,
API cost and separate lead/worker timings remain null unless the host exposes them;
do not estimate tokens from prose length or treat unavailable cost as zero.

`observe` reuses the existing snapshot mechanism and never executes reviewed code.
It reports endpoint changes and presence of a nonempty review; those facts do not
establish semantic success, actual delegation, a deadline, or absence of transient
and out-of-workspace effects. As in the existing evaluator, `.git` and `__pycache__`
paths are excluded; scope facts describe only observed paths. Local fixture probes
are tested separately. These workspaces are instruction-scoped, not hostile-code sandboxes. Permission denials
must not be worked around.

## Interpretation

One observation per cell can expose failures and protocol problems. It cannot
establish superiority, stable latency/cost differences or performance in coupled
implementation work. All arms are explicitly cued to consult the runbooks; this
does not test spontaneous discovery. Easy fixtures may produce a ceiling effect.
Do not tune on these cases then present them as held-out evidence. Add realistic
unseen tasks only under a separately agreed follow-up if the result warrants one.

Publish concise observations and limitations under `docs/validation/`; retain raw
traces outside the repository. Keep the current Atlas architecture unless useful
differences survive controlled evaluation. An equal result is a valid reason to
stop without introducing a roster.
