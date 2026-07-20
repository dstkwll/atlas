# CONTEXT — Unified Agentic OS (glossary)

> Ubiquitous language for the OS design. Glossary only — no implementation detail.
> Terms crystallize as wayfinder decision tickets resolve.

## Terms

- **Instance** — one deployed copy of the OS spine-design. There are two: **work** and **personal**. **Deployment model = ONE repo (the spine-design), installed and configured twice — NOT one live linked spine with two interfaces.** Like the same app installed on two separate machines with two separate accounts, not one server with a work tab and a home tab. What's **shared** = the *design* (improve a skill / tighten the constitution once → both installs adopt it on next pull). What's **separate** = everything that runs and everything stored (own process, own queue/card-folder, own traces, own memory, own vault, own config profile). They never talk at runtime. **This runtime isolation IS the confidentiality wall — physics, not policy:** work data cannot reach the personal vault because no channel exists between them. Each install carries its own config (work → Teams/Copilot vessel, conservative calibration; personal → Hermes/Discord vessel, permissive calibration). A deliberate, human-driven, one-way publish of a *non-confidential* asset into the shared repo is allowed (that's editing the shared *design*); a runtime link between the two live systems is never.

- **Spine** — the common, largely-shared *design* underneath both instances: the execution engine, roles, skills, gating. Shared as a design, NOT as a running system.

- **Cost-tier engine** (the spine's execution model, T1) — frontier "head" writes specs + reviews results; cheap generic **worker lanes** implement; an **executed check** is the only evidence believed (never a self-report). Bounded, hard-gated worker only at a money/external/credential boundary.

- **Worker lane** — a generic, pluggable execution slot that claims one specced task and runs it. Capability = scoped tool/skill grants per task, NOT a standing domain agent. Stateless/disposable.

- **The check is the contract** — "done" is defined as an executable check; exit-code-zero against the artifact is the only proof of completion. Self-reported "done" is never trusted.

- **Dispatcher** (the front door, T2) — the single intake **role** per instance. Receives intent, does intake reasoning (investigate → ground → triage → rank), and **enqueues** tracked tasks. Thin on *execution*, not on *judgment*. NOT a long-lived session — a *role* that any fresh, disposable session assumes by loading durable state. Deliberately NOT named "chief-of-staff" (reserved for a possible future role that represents Dan / owns judgment).

- **Input vessel** — a stateless transport surface (personal: Hermes/Discord; work: Teams/Copilot). Carries intent in, digest out. Holds no memory. Many capture-inputs (voice memo, forwarded email, a chat line) converge on ONE Dispatcher per instance.

- **The queue** — the durable, tracked surface of work (issues/tasks) that IS the interface. Replaces many ephemeral sessions. The Dispatcher writes to it; worker lanes claim from it. Its status-ledger is the ranked-digest / final-checkpoint surface Dan reviews.

- **Traces** — full run-logs of every worker attempt (spec, engine, model, pass/fail/timeout, tokens, raw check output). The continuity + drift-control + self-improvement substrate. Distinct from a **receipt** (the short outcome summary surfaced to Dan).

- **Sessions are cattle, not pets** — every session (Dispatcher or worker) is fresh, disposable, and reconstitutes its context by reading durable state (queue + traces + wiki + memory). Crash/close/`/new` resilience is free; nothing real lives only in a session's head.

- **Capture inputs (many) ≠ front doors (one per instance)** — you can capture from anywhere; it all converges on one Dispatcher per domain.

- **Card** (T3) — one markdown **note** = one unit of work. Lifecycle state lives in its **YAML frontmatter** (`status`, `claimed_by`, `created`, `modified`, back-refs); the task is the body. The queue is a *folder of cards*, one folder per instance (isolation is just separate folders). This is the durable substrate of record.

- **Vault-as-substrate** (T3) — the continuity substrate is **markdown-on-disk in the Obsidian vault**, not a hosted tracker. Portable, greppable, git-able, tool-agnostic. GitHub Issues is held only as an escape hatch (hosted concurrency + mobile board) we don't expect to need at personal scale.

- **Glance layer** (T3) — a **Bases view** (Obsidian core Bases + a Bases-kanban plugin) renders cards as a board grouped by `status`. It is Dan's human surface ONLY — **agents never touch the plugin**, they read/write frontmatter directly. Truth is per-note frontmatter, so the board/plugin is disposable (swap at zero data cost).

- **The board (Option B)** (T3) — 4 live columns **Inbox → Queued → Working → Review**; **Done is archived OFF-board** (a card leaving the active folder = "emptied"; traces persist in archive). **`blocked` + `needs-input` are flags, not columns.** **Standing/recurring work = a generator** that drops cards into Inbox, never a column. **Working→Review = the executed-check gate** (a worker can never self-promote — the check is the contract). **Review, ranked = the single digest = the North-Star final checkpoint.**

- **The Constitution** (T5) — the 9 shape-independent standing principles every capability in both instances obeys. Full text in ticket #6's resolution comment. Load-bearing terms below.

- **The consequence gate** (T5) — a T3 action's safety is *structural*, not discretionary: generic worker lanes are only ever granted read/reversible capability scopes, so they physically cannot touch money/external/credentials. Anything irreversible routes to the one **bounded hard-gated worker** — the only lane holding those keys, which additionally **runs frontier-tier** and **cannot start without an explicit per-card human approval**. "Take away the keys," never "trust the agent to ask." Fail-closed by construction.

- **T3 = irreversible external side-effect** (T5) — the gating tier is defined by a bright-line undo test: *if this goes wrong, can the system undo it with nobody outside noticing?* No → T3. Default is T1/T2; tasks are **decomposed so only the irreversible verb is T3** (a bill = 9 reversible steps + 1 T3 "pay"). Genuine classification ambiguity **routes up** (fail-closed) and is captured as a durable **per-instance classification rule** so the same ambiguity never pauses twice.

- **BLOCKED vs HUMAN HOLD** (T5) — the two pause types. **BLOCKED** = stuck on the *work* → the answer belongs **on the record, on the card** (any fresh session resumes it). **HUMAN HOLD** = stuck on *authority/permission/credentials* → the answer belongs to the **owner privately, off the record**. Every T3 approval is a HUMAN HOLD; this is the same channel as the confidentiality wall.

- **Receipt** (T5, refined) — the mandatory explicit outcome written at every task close (what was done · which check proved it · what's left / any HUMAN HOLD). **No-receipt = not-done** (fail-closed). Receipts are the **atoms of the ranked digest** (the Review column). Distinct from a **trace** (full run-log, for the system's drift-control + self-improvement). NOTE: how receipts *surface* to Dan (notification / response UX) is deferred to ticket #7.

- **Self-pruning** (T5) — the OS periodically tries its own machinery (skills, gates, generators) against its **traces**; anything that can't demonstrate value from usage evidence is retired. Periodic audit, never per-task.

- **Agenticity dimmer** (T5) — how a capability earns autonomy: **caged start** → **graduate by trace evidence** → **consent-bound scope that re-asks on expansion** → **symmetric demotion**. **T3 never graduates** (irreversible actions stay hard-gated forever). **One mechanism, two calibration profiles** — personal tuned permissive, work tuned conservative (the concrete example of what legitimately diverges between the two instances: *calibration* diverges, *mechanism* stays common).

- **Define-done-before-work** (T5) — no task enters a worker lane without a written **done-contract**, and that contract **IS the executed check** (defined at spec-time by the head, run at close-time). Unspecifiable-done = the task isn't ready → route back. Fail-closed at the front mirrors fail-closed at the back; this is what makes the cheap-worker model safe.

- **Cost posture: performance-first** (T5) — spend on **judgment** (spec/synthesis/review = frontier head) and on **irreversibility** (T3 executing worker = frontier); economize on **legwork** (gather/fetch/edit = cheapest reliable actor, often no LLM). **Delegate for breadth, never delegate judgment.** Thrift survives only for trivial, reversible, high-confidence T1 work.
