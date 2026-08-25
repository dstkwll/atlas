---
name: gazetteer
description: Orient, start, resume, inspect, or continue Atlas work.
---

# Atlas Gazetteer

Gazetteer is Atlas's canonical user-facing entry point. Interpret the user's interaction intent, resolve the relevant Atlas run conservatively, and enter the existing workflow owner from authoritative state.

> **Gazetteer may decide which safe Atlas entry point applies. It never decides workflow truth.**

Gazetteer owns conversational navigation and orientation only. Controllers own lifecycle authority, producers own stage work, judges supply semantic evidence, and deterministic packaged tools validate or mutate state. Model strength never grants authority.

Normal users should use Gazetteer. Direct internal Atlas skills remain available for diagnosis, testing, and advanced bounded entry, but they are not required knowledge for continuing a normal workflow.

## 1. Establish availability and inventory

Resolve `<atlas-plugin-root>` from this installed skill: it is the third parent of this file (`SKILL.md` → `gazetteer/` → `skills/` → plugin root) and must contain `tools/atlas_gazetteer.py`. Use that absolute path and run the read-only inventory from the user's current location:

```shell
python3 "<atlas-plugin-root>/tools/atlas_gazetteer.py" inventory --cwd "<current-working-directory>"
```

If the result is `NOT_CONFIGURED`, invoke `atlas:setup-atlas` internally. Preserve the user's complete request and return to the original request after setup; a new-goal user never has to retype the goal. If setup is declined, forbidden by the current request, or fails, report that boundary and stop without starting a run. Never tell a normal user to invoke `setup-atlas` or `start-run`; those are internal owners. When setup is needed but not yet authorized, offer one natural-language continue affordance through Gazetteer, such as “Continue with Atlas setup?” If the user continues, Gazetteer invokes setup and resumes the original request itself.

Treat `BLOCKED` inventory as a global configuration/root/identity failure and stop. Treat `PARTIAL` as an inventory with isolated diagnostics: keep valid runs available, never present an invalid run as valid, and do not let an unrelated run or binding diagnostic block orientation. If the explicitly named, session-focused, or otherwise selected run appears in `gaps[].run` or `repository_blocked_runs`, report that blocker and stop. Before any action, enter the existing owner, which revalidates that exact run completely and fails closed. Do not infer state from artifact presence, repair control files, or substitute conversation memory. A bare Gazetteer invocation means **orient me**: report the relevant run, meaningful current phase, completed boundaries, blocker or owner, and next legal/recommended action. With no active run, invite a new engineering goal.

## 2. Interpret interaction intent

Use the model to understand natural prose. Do not build or emulate a keyword table. The small conceptual classes are:

- `NEW_GOAL` — a genuinely new engineering request, including “implement X” when X is new;
- `CONTINUE` — continue or resume existing Atlas work;
- `INSPECT` — status, orientation, what-is-next, or what-is-blocked without requested progression;
- `ACT_ON_NAMED_WORK` — an exact named run or accepted work item;
- `PROVIDE_JUDGMENT` — an answer to the current owner's pending question or authority surface.

These labels are conversational reasoning only: never persist or expose them as workflow state. The word “implement” does not authorize skipping selected planning. A short answer such as “option 2” belongs to the current focused owner's pending interaction when one exists; do not reinterpret it as a new goal.

## 3. Resolve the relevant run conservatively

Apply this precedence:

1. the exact run explicitly named by the user;
2. an unambiguous session-local conversational focus selected earlier in this conversation;
3. exactly one structurally relevant active run;
4. otherwise present a concise candidate selection with durable goal, phase/status, and blocker summaries.

Structural relevance may use the inventory's `current_repository_identity` and `repository_relevant_runs`, active/incomplete status, exact run slug, or durable goal text. Repository relevance is exact configured identity matching, never path-name or semantic guessing; multiple matching runs still require selection. Semantic similarity may rank or suggest candidates; it never silently binds apparently new intent to an existing run. When a new statement plausibly matches existing work, ask whether to continue that run or start separate work. Never create a durable active-run pointer, registry, similarity index, or routing state. Session focus is convenience only and must be discarded or re-resolved when ambiguous.

Every real action re-runs inventory or enters an existing owner that rereads and validates authoritative state. Conversation history can identify intent or focus but never overrides durable Atlas state.

## 4. Preserve prompt and authority propagation

For `NEW_GOAL`, pass the fuzzy goal to `atlas:start-run` only for new intake. If setup was needed, pass the unchanged original request after setup returns.

After `run.yaml` and control authority exist, carry run identity and explicit new user judgments, not the original fuzzy prompt, into continuation. Accepted decisions, product/design artifacts, tickets, and controllers remain the engineering truth; downstream owners must not independently reinterpret the intake prompt as coequal instruction.

Status and orientation are read-only. `INSPECT` reports the validated inventory and must not advance merely because a next action exists. `CONTINUE` and unambiguous “what's next?” may enter the current owner when the user's wording requests progression. `ACT_ON_NAMED_WORK` resolves the exact run/work first; legality still belongs to its controller. `PROVIDE_JUDGMENT` returns the exact user judgment to the focused current owner without laundering it into approval of any other boundary.

## 5. Enter the existing owner

Route only at the product-level seams already owned by Atlas:

- new goal → `atlas:start-run`, with the unchanged fuzzy goal;
- existing planning run → `atlas:start-run`, with exact run path/identity and the invocation-local continuation posture;
- inspection/orientation → report the validated inventory read-only;
- pending judgment → the current focused interaction owner, preserving the user's exact answer;
- `READY_FOR_EXECUTION` → execution entry only when a first-party owner exists;
- complete work → summarize without reopening it;
- `BLOCKED` or `DESIGN_BLOCKED` → explain the durable blocker and substantive resume action without routing around it.

Every existing run enters `atlas:start-run` first with its exact run identity and continuation posture. Gazetteer never invokes Discovery or a downstream producer directly; `start-run` validates authoritative state and owns all producer dispatch.

Do not reproduce stage-to-skill routing. `start-run` already validates and continues current planning; producers already perform their named control handoffs. Prefer the host's safe nested skill invocation mechanism. If the host refuses nested invocation because the sibling is intentionally non-implicit, load the exact installed sibling `SKILL.md` as the current owner procedure using [`../../references/internal-owner-loading.md`](../../references/internal-owner-loading.md); that is the calibrated procedure-load fallback, not broader invocation. Once Gazetteer enters an interactive owner, that owner retains the conversation through its questions until its defined stopping condition or handoff; Gazetteer does not interject between co-design or Discovery questions. Do not encode `next_skill`, derive a producer from the configured stage list, or teach an internal command as the normal next action.

If the user names an accepted ticket while no first-party execution owner exists, report the exact run, accepted graph, and ticket, then state that no first-party execution owner exists. Do not substitute ad hoc coding. The word “implement” still does not authorize planning bypass. When execution later exists, Gazetteer may identify the requested ticket and enter that high-level owner; only the execution controller may decide readiness.

## 6. Continue coherently

`INTERACTIVE` is the default continuation posture. Select `AUTO_CONTINUE` only from an explicit current user request or supported host posture that clearly asks this invocation to keep crossing already-legal handoffs. Never derive continuation posture from `governance: autonomous`, a gate's authority, or artifact presence, and never persist it in Atlas V1.

Pass the posture to `atlas:start-run` as invocation context, not as authority or durable state. Mechanical internal handoffs continue in either posture: producer → configured controller/authority adapter → deterministic transition result. Once the entered owner returns, follow this exact loop:

1. After the entered owner returns, re-run inventory and re-read authoritative state.
2. If the same gate remains pending, the owner asks for a user decision, or progress is otherwise unchanged, stop rather than retrying.
3. A required HUMAN judgment always stops and asks at its authority surface, including under `AUTO_CONTINUE`. A HUMAN gate stops at its approval surface after the selected producer has prepared its candidate; it does not block entry into that already-selected producer.
4. `BLOCKED` or `DESIGN_BLOCKED` always stops; explain the substantive issue and exact available action in user concepts.
5. Ambiguous run/work resolution always asks rather than choosing.
6. At `READY_FOR_EXECUTION`, report the accepted graph version/hash and stop when no execution owner exists.
7. Under `INTERACTIVE`, explain what completed, name the recommended meaningful next phase and why, then ask “Continue?” without exposing its skill name.
8. Under `AUTO_CONTINUE`, announce the next meaningful phase briefly and re-enter `atlas:start-run`; stop only for judgment, ambiguity, blocker, completion, or an unimplemented lifecycle owner.

Continuation is never acceptance or approval. It may enter an already-selected stage; it cannot decide that an artifact passed, synthesize evidence, satisfy a HUMAN gate, turn `gate_ready` into acceptance, or mutate any control state itself.

## 7. Present meaningful phases, not plumbing

Hide skill plumbing, not engineering meaning. Say that product decisions settled, code-level realization is next, or ticket compilation is ready; do not say “call program-design” or “invoke control-planning.” For manual continuation, state what just completed, the recommended next phase, why it matters, and one concise continue affordance. In auto-continuation, concise phase announcements are sufficient.

Explain blockers in user concepts. A design contradiction names the accepted upstream truth that must be revisited; an unavailable repository names the dependency to restore. Never ask the user to choose an internal resume enum or command. Directly invoked internal skills may suggest “Use Gazetteer to continue,” but must remain independently usable and must not recurse through Gazetteer for their own authority.

## 8. Staffing

Gazetteer is a `workflow_guide` reasoning role with a `workflow_navigation` task shape. Where current host/config routing supports role/task-shape staffing, prefer the strongest configured reasoning worker for that role and shape. Where it does not, treat this as an operational host/configuration preference and use the current host's strongest configured reasoning tier. Never hard-code a provider or model name, create a parallel model router, or let model strength grant authority.
