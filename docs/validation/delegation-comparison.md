# Direct and delegated review: initial pilot

The bounded comparison adds maintainer evaluation support while preserving Atlas's
one portable lead and selectively used runbooks. It does not install specialists,
change accepted architecture, or establish that either arrangement is superior.
See the [operator protocol](../../evals/delegation-review.md) for repeatable setup
and the outcome rubric.

## Candidate and method

The 2026-09-20 pilot used the unchanged Atlas guidance from main revision
`22acf149551e0a4961a240f82fa68d65683c19cd` (package 0.7.4), copied into fresh
review workspaces. A standard-library packet builder prepared three scenarios
under three conditions, once per cell: a direct lead review, a lead with one
fresh worker given an inline contract, and a lead with one fresh worker loading
that same contract from a saved reviewer definition. All conditions received
identical case source, acceptance requirements and runbook information.

Execution used ChatGPT Work Mode collaboration sessions. Leads started without
parent conversation history; workers were requested with fresh history. The
current inherited model and reasoning settings were retained, without overrides;
exact model identifiers and effort metadata were unavailable. Codex and Copilot
CLIs were unavailable. This is not native CLI, installed-profile activation or
native named-agent registration validation. The saved definition tests reusable
contract invocation, not a specialist's different model, tools, memory or training.

Each trial had a 180-second total lead/worker ceiling and at most one worker.
The regression and control batches launched three leads concurrently. Following
a worker-capacity rejection, the uncertain batch launched its defined and direct
leads together, with the briefed lead afterward. No blocked cell was replaced.
This concurrency variation prevents controlled latency comparisons.

## Outcomes

All nine cells were attempted: eight returned completed reviews and one had a
blocked worker setup. Completion of a review does not establish timing compliance;
see the protocol deviations below. The table records report-content judgments
against source, confirmed by the later independent saved-output assessment below.
It is not a grade of host execution or timing compliance.

| Scenario | Direct | Inline worker contract | Saved reviewer contract |
| --- | --- | --- | --- |
| Regression: changed retry key and truthy rejected response | Both real defects identified | Both real defects retained in synthesis | Both real defects retained in synthesis |
| Control: stable key and explicit response handling | No supported defects | BLOCKED: host rejected worker launch | No supported defects |
| Uncertain: unspecified production deduplication retention | Correctly identified contract/evidence gap | Correctly identified contract/evidence gap | Correctly identified contract/evidence gap |

The successful regression reports traced duplicate committed effects after a lost
acknowledgment and false caller completion on explicit rejection. The successful
control reports accepted the documented guards without inventing a local-deadline
requirement. Completed uncertain reports separated passing fake-provider behavior
from missing production retention guarantees; hypothetical expiry probes were
identified as conditional demonstrations, not production reproductions.

The blocked control lead recorded `agent thread limit reached`, retained its
lead-only observations and did not claim successful delegated review. Its
`worker.md` is a failure record, not evidence that a worker ran. Artifact presence
alone therefore cannot establish successful routing.

## Evidence and limitations

- Implementation review by a separate context found no blockers. Its two optional
  improvements were incorporated: qualify snapshot exclusions and test the actual
  caller's false completion, not only the delivery function. All 29 evaluator
  tests passed, including the four new fixture/packet/observation tests.
- All 39 current evaluator tests passed. Subsequent reconciliation and the
  saved-output assessment did not rerun or replace any model trial.
- The operator observed actual child-session identities for completed delegated
  treatments. Their source/probe reports and lead syntheses support useful
  application of Independent review and Failure handling. Full host tool traces
  were not exported; consultation frequency, exact worker briefs and all claimed
  probe executions cannot be independently reconstructed from these artifacts.
- All observed endpoint changes were under `results/`. Snapshots exclude `.git`
  and `__pycache__` and do not prove absence of transient writes or external
  access. Workspaces were instruction-scoped, not security sandboxes.
- The two delegated regression completion receipts were recorded approximately
  222 seconds after the common batch start, across an operator context-recovery
  gap. The briefed uncertain receipt was recorded at approximately 180.7 seconds.
  Actual finish timestamps were unavailable. Deadline adherence is **unverified**
  for these three trials; their review content is retained as diagnostic evidence,
  not successful bounded trials. Other receipts were recorded within 180 seconds.
  A report's own within-budget claim is insufficient.
- Token usage, API cost and separate lead/worker timings were unavailable. The
  observed repeated investigation by leads and workers is not a measured cost
  difference. Operator receipt intervals include launch and notification delays.
- In the original host, a fresh independent outcome assessor could not start:
  the host rejected the launch with `agent thread limit reached`. Resuming the
  independent implementation
  reviewer for outcome assessment was also rejected. That original limitation is
  retained; the separate receiving-session assessment below resolves only the
  pending semantic assessment, not missing execution evidence.
- One observation per cell, incomplete setup and timing coverage, small seeded
  cases and explicitly cued runbooks prevent reliability or superiority claims.
  This does not test autonomous role selection, spontaneous runbook discovery,
  deep runbook navigation or coupled implementation work. A whole specialist team
  would require a different comparison; these results cannot settle that design.

## Independent saved-output assessment

On 2026-09-20, a fresh context-only Copilot reviewer (gpt-5.6-sol, high reasoning)
assessed all nine shuffled source/requirements/report packets. The trial mapping,
prior outcome summary and evaluator rubric were withheld until its judgments were
recorded. Reports themselves disclosed some routing, so blinding was imperfect.
The reviewer had no execution tools and did not produce the fixtures or reports.

It supported both defects in all three regression reports, the zero-finding
conclusions in the two completed control reviews, and the explicit retention
contract gap in all three uncertain-case reports. It found no material missing
source-level finding or false semantic claim. All five completed worker returns
retained their valid findings and uncertainty in the lead syntheses. The blocked
control packet's lead-only observations were consistent with source, but its
failure record was not a worker review or a completed delegated treatment.

Severity labels were not independently graded: the packets supplied no severity
rubric, and review recommendations are not integration authority. The assessor
also could not verify task-specific routing requirements, reported probes, timing
or file activity from report prose. The receiving lead subsequently checked the
mapping against the saved schedule, matched every packet's fixture bytes to the
recovered generator, and verified that shuffled reports matched their saved trial
copies. These provenance checks do not recover the missing host traces. The
original blocked setup and three unverified deadlines remain unchanged.

## Disposition

Keep the current portable-lead architecture. The completed examples show that both
bounded delegation styles can return useful review evidence and that direct review
can succeed on these cases. They provide no demonstrated need for a mandatory
roster. Host capacity and reliable timing evidence must be established before a
future controlled run. Such a run would be a separate follow-up, not a hidden retry
or a reason to expand this pilot. Raw reports and operator evidence remain outside
the repository; this summary retains only coverage, observations and limitations.
