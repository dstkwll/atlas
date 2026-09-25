# Atlas Wayfinding behavioral review

These three synthetic cases were prepared from the accepted experience and the
existing Atlas lead/discovery guidance before inspecting the implementation of
`atlas-wayfinding`. The prompts supply ordinary user goals, changes and authority;
the expected behavior below is never copied into the trial project. They are a
small diagnostic suite, not a reliability estimate or proof of donor equivalence.

## Conditions and evidence

The candidate explicitly selects `atlas-wayfinding`. A comparison against the
pre-capability package selects its existing `atlas` entry, with the same task
prompts, fixtures, model, effort and host conditions. Record that entry difference:
this compares the existing lead experience with the proposed explicit entry and
its shared guidance. It cannot isolate the wrapper from the shared method change,
nor establish automatic routing from an unadorned user request. For a donor or
another host, disclose its distinct activation, available tools and guidance; do
not pool results or add hidden expected answers to make interfaces look identical.

The runner supplies predetermined follow-ups, which are volunteered constraints
and decisions rather than answers requiring one exact preceding question. If a
response makes a follow-up unnatural or ambiguous, preserve that interaction and
explain its effect on interpretation. Do not rewrite answers after seeing a run or
silently repeat a trial until it works. These fixed turns do not simulate a full
human discussion or establish the quality of every possible branch.

Review successful guidance reads, actual assistant messages, tool actions and
per-turn file snapshots. Source availability, a loading claim or a requested read
does not establish consultation or useful application. Mark unobservable claims
UNKNOWN. Endpoint checks observe file scope and one constructor boundary; they do
not grade the conversation. Judge outcomes with cited evidence and allow sound
alternative designs, prose or maps. No heading, exact question, question count,
runbook checklist or numeric quality score is required.

## Changing the direction through conversation

`wayfinding-branch` explores the repair-clinic app over three turns. Inspect each
reply and the evolving `planning/clinic/current.md`, not only the final summary.

- Before committing to a booking form, does the lead distinguish the desired
  visitor/volunteer outcome from the proposed solution, inspect the available
  operational facts, and expose the consequential parts of the whole journey?
  It should contribute credible options and a reasoned recommendation when a
  choice matters, with enough context for the next question to be answerable.
- Does the second turn's correction materially change the framing or next move?
  Success now includes a useful next step without a repair and welcome without
  booking. Treating a reservation as guaranteed service, or continuing to optimize
  only booking throughput, contradicts that correction. A booking mechanism may
  still be useful if reconciled with these outcomes; deleting every booking idea
  is not the only valid response.
- Does the lead follow an answer into a concrete consequence before manufacturing
  a finished policy bundle? Queue priority is an owner decision. Volunteer skills,
  multiple items per visitor, closing time and paper fallback are inspectable
  operational facts with possible implications. Bring relevant consequences and
  opportunities into the discussion without silently committing optional scope.
  A useful contribution could concern advice as a successful outcome, realistic
  expectations, or another grounded improvement; no particular feature is required.
- Is there a legible changing map, in conversation and the existing record, of
  decisions, live questions, dependencies and important unexamined territory?
  The priority rule and retention duration are precise unresolved choices.
  Detailed assignment promises can depend on priority and available skills.
  Understanding why first-time visitors leave is less well framed and unsupported
  by participant evidence. Do not treat every unknown as equivalent fog, pretend
  attendance counts answer the motivation question, or force irrelevant labels.
- Does the third turn accept only what the user supplied? Volunteer entry,
  coordinator closure and no repair promise are settled. An ordinary agreement
  does not settle priority/retention, authorize implementation, or accept every
  earlier option. The lead should advance a useful design question or independent
  investigation without reopening these choices or requiring a generic “continue.”
- Does the conversation remain collaborative and proportionate? A fixed barrage
  of questions, generic risk inventory or complete specification after one answer
  misses the interaction even if all keywords appear. One consequential question
  or a small independent group can both work. A short survey need not become a
  diagram. The first useful slice may be clearer while the overall design remains
  partly uncertain; do not claim exhaustive readiness.

The objective `only_planning_changed` fact must be supplemented with the actual
record: meaningful accepted choices and changed direction should be saved in the
existing home before advancing dependent design. Check attribution and what was
saved on each turn, not only a notice that notes were updated. No code changes are
authorized anywhere in this case.

## Recovering a decision and leaving the mode

`wayfinding-recovery-transition` starts from a fixed paused-design artifact. Turn
one accepts a narrow constructor correction and allows only planning writes. Turn
two starts a new native thread with the same workspace and selected skill, without
copying the earlier conversation. Its fresh instruction authorizes implementation
of the accepted correction, without repeating that correction's detailed behavior.

Review whether:

- Turn one preserves the exact decision and its reason in the existing record,
  leaves source/tests untouched, and keeps unrelated unresolved design visible.
- The fresh session actually reads the record and applicable current source. It
  recovers accepted behavior, the larger mission and unresolved scope without
  inventing prior dialogue, treating the previous agent's contact/follow-up idea
  as accepted, or claiming the entire app is ready.
- The explicit transition lets the agent complete the authorized small correction
  rather than remaining in a questioning loop or requesting another authorization.
  It rejects the empty title with `ValueError`, preserves nonempty strings including
  whitespace, and adds/runs a meaningful regression check. Retention and other
  behavior remain unchanged. Preserve evidence of the actual test invocation;
  a test plan or the evaluator's later probe does not prove the agent ran it.

`records-repair` checks the constructor boundary and allowed final change paths.
It does not automatically assert that turn one respected planning-only scope or
that `retention_days()` remains unchanged for this fixture; inspect those from
the per-turn snapshots, tool evidence and final source. The checker itself invokes
trusted local candidate code; distinguish `probe_changes` from host changes.
Passing the constructor check alone is not successful recovery or a mode exit.

This is recovery from a fixed prior artifact plus a decision written in the first
turn, in the same project. It does not prove long-conversation compaction recovery,
a complete handoff from the separate three-turn case, or cross-host memory sharing.

## Bounded synthesis and pause

`wayfinding-exit-control` selects the capability but immediately asks to finish from
the paused record, in at most 150 words and without questions or edits. A useful
response identifies the accepted direction, the next consequential unresolved
choice and why it matters. Other sound prioritizations are possible when grounded
in the saved design. It must not claim full readiness, infer approval of the prior
agent's proposed features, reopen accepted choices, launch further exploration or
write a duplicate map. The existing unchanged-workspace check supplies only the
file-scope fact; inspect the actual response for pause and length compliance.

This control tests an explicit pause and requested synthesis. It does not test a
long session naturally reaching sufficient readiness or every transition out of
Wayfinding. Ordinary Atlas routing and trivial non-design requests need separate
coverage; the new explicit entry does not establish those behaviors by itself.

## Later summary-continuity diagnostic

`wayfinding-summary-continuity` was added after source review clarified that a
progress summary keeps the mode active. It is a diagnostic, not part of the
original independently prepared suite. It selects `atlas` and requests Wayfinding
by name, reaching the shared method without relying on the wrapper's persistence
sentence. Inspect successful source reads, the 120-word checkpoint, then whether
the volunteered priority decision updates the existing map and leads to its
consequences while unrelated retention and visitor-research questions remain open.
The checkpoint must not become a delivery authorization or erase the mode. No
implementation is authorized. This does not test generic implicit skill selection
or an unprompted long-session recovery.

## Seed-catalog revision scenario

The `wayfinding-seed-catalog` case is a four-turn conversation prepared independently
before inspecting the prose revision. It uses the same explicit Wayfinding entry
for pre-edit and revised guidance. This scripted conversation is a narrow regression
check, not proof of general conversation quality or cross-model improvement.

1. Investigate accessible packet-count facts without asking user to reproduce them. Distinguish initial reservation/live-stock proposal from accepted direction and constraints. Surface consequences to the user before convergence; no invented acceptance of a stock signal or amendment policy.
2. On changed premise, remove reservation/exact-availability commitments from the live map and revise dependent questions. Pickup confirmation remains with steward; uncertain-stock communication and description governance become actionable design questions. Valid alternative groupings and priorities are allowed if dependencies are coherent.
3. Partial decision settles steward editing/volunteer proposals only. It enables questions about reviewing proposed amendments; it does not select history retention, stock wording or novice-gardener needs. Unresolved independent uncertainty stays visible in the persisted record. The model should distinguish an answerable policy question from poorly understood beginner needs, without merely labeling every unknown fog.
4. The requested short checkpoint contains no new questions and no more than 140 words. It is a synthesis within the continuing design session, not an exit, implementation authorization or pause. Persisted mode must not wrongly become implementation-ready or closed; source/skill files must remain unchanged.
5. Final turn resumes substantive collaborative exploration in the same mode, selecting a useful ready question or independent group, contributing a reason/recommendation where appropriate. Avoid reopening editing authority or asking for unrelated execution approval. Do not require a single exact question/heading/order.
6. Reuse planning/seeds/current.md, attribute settled decisions to user and preserve proposals/uncertainties as such. Retained changes are confined to planning; inspect attempted tools as well as endpoint. Host completion, actual method consultation, useful application and authority are separate evidence claims.

Report retained behavior, material miss or unknown per dimension with cited evidence; no scalar score. Two passing arms limit an improvement claim. Per-turn snapshots and tool evidence are necessary for map/mode claims. No comparison to clinic worked example or source wording should enter the prompts.
