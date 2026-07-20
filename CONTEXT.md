# CONTEXT — Unified Agentic OS (glossary)

> Ubiquitous language for the OS design. Glossary only — no implementation detail.
> Terms crystallize as wayfinder decision tickets resolve.

## Terms

- **Instance** — one deployed copy of the OS spine-design. There are two: **work** and **personal**, isolated (no shared runtime/memory → hard confidentiality wall). Both are the same *design*, deployed twice.

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
