---
name: compile-tickets
description: Compile the Atlas Stage 5 graph and hand it to planning control.
disable-model-invocation: true
---

# Compile tickets

Compile the exact Stage 5 candidate. This is decomposition and proof planning under accepted design, not another design stage and not execution. D-084 governs vertical ticket semantics; D-085 governs execution-complete readiness and deterministic proof; D-087 fixes the current candidate and ticket-context contract. Ticket-graph manifest version is exact integer `2`; version 1 is raw historical evidence only and is not loadable or factory-executable.

Resolve `<atlas-plugin-root>` from this installed skill before invoking a packaged tool: it is the third parent of this file (`SKILL.md` → `compile-tickets/` → `skills/` → plugin root). Use that absolute path; never rely on the caller's working directory.

## 1. Resume frozen authority

Read immutable `run.yaml`, authoritative Stage 0 `control.json`, and `planning-control.json` before any producer action. Require current status `PLANNING`, phase `tickets`, gate `PENDING`, and no ticket-graph acceptance. Require exact configured tickets authority `AGENT_REVIEW` or `HUMAN`. Reject every other status, phase, gate, prior acceptance, aliased authority, or incomplete state rather than repairing it or routing elsewhere.

Derive every applicable source only from effective selected stages and exact current acceptances:

- Product Definition Approval selected: bind exact accepted `20-prd.md`.
- System Design selected: additionally bind exact accepted `30-system-design.md`.
- Program Design selected: additionally bind exact accepted `40-program-design.md`; a direct Program Design path also binds frozen Stage 0.
- All semantic producers omitted: bind only frozen effective Stage 0 `run.yaml`, effective configuration, and target baselines.

Never read an omitted source or infer applicability from artifact presence. The trivial path has exactly one one-node ticket graph and manufactures no PRD or design artifact.

## 2. Verify exact target baselines

Before drafting, run:

```shell
python3 "<atlas-plugin-root>/tools/atlas_repository.py" verify --run "<run-directory>"
```

A repository `BLOCKED` report stops before candidate readiness. After PASS, use only the packaged `list`, `search`, and `read` commands when exact frozen-baseline inspection is needed to ground validator commands or repository targets. Current checkout bytes are drift/context, never a replacement for the frozen baseline. Keep machine-local binding paths out of portable candidates.

## 3. Compile one complete graph

Use [`references/ticket-graph-file.md`](references/ticket-graph-file.md) as the exact candidate shape. Write ticket files first, then hash those exact bytes into canonical `50-ticket-graph.json`. The manifest is the single hashable graph root; it is not a second accepted packet.

Apply these contracts:

1. Every non-enabling ticket is the smallest independently verifiable outcome-bearing behavior that crosses each implementation boundary that behavior needs. It does not mechanically touch irrelevant layers.
2. The first non-enabling frontier proves the riskiest or most important seams early. `preferred_order` carries that preference; `blocked_by` contains only real prerequisites and states what each establishes.
3. A standalone enabling ticket names one imminent vertical consumer, is a real prerequisite of that consumer, and explains why it cannot safely be incorporated there. Generic foundations and integration-later layer slabs are invalid.
4. Every ticket has exact top-level `context: {sources: [...]}` and no top-level `references`. Each context source has exactly `kind`, `sections`, and nonempty `purpose`. Every applicable selected-path source kind appears exactly once. Stage 0 has `sections: []`; every semantic source lists unique exact existing `##` headings. The ticket's `Execution context` body mirrors the ordered declarations exactly—one canonical line per source with the same kind, sections, and normalized purpose. Program Design touchpoints are normative expectations, not an exhaustive file allowlist. compile-tickets owns semantic context selection; the supervisor only validates and materializes that accepted declaration plus current runtime facts. No automatic projection or supervisor gap filling is allowed.
5. Every promised behavioral outcome has observable acceptance and at least one deterministic exit-zero validator. `semantic`, `design`, or `quality` review may supplement that proof and may never substitute for it.
6. Every external prerequisite records the accepted execution-preventing condition and either a deterministic exit-zero satisfaction command or a provenance-bearing `HUMAN` assertion. `continue` later revalidates; it never satisfies the condition.
7. Ticket identities, repository targets, ticket hashes, dependency references, preferred order, tracer identity, validator references, and external-condition identities are stable and complete. Self-dependencies and cycles are invalid.

Selected Program Design is the exact decomposition contract when present. Otherwise the applicable accepted selected-path source governs. Missing declared source material is a packaging/preflight blocker. If the accepted design does not contain the judgment needed to choose semantic context—or compilation otherwise needs a new architecture, code shape, publication, consumption, or delivery decision—return structured read-only `DESIGN_BLOCKED` naming the applicable `upstream_source`, exact `upstream_issue`, matching `resume_boundary`, and smallest `resume_action`; stop before candidate readiness. Repository facts within granted inspection authority remain discoverable and do not become declared semantic context unless the compiler selects them. Do not invent the missing truth.

## 4. Preserve producer ownership

On the normal path, write only canonical `tickets/*.md` and `50-ticket-graph.json` candidate/readiness bytes. The producer must never create or modify `reviews/ticket-graph-v1.json`, never write `planning-control.json`, never rewrite an upstream artifact, and never create `.factory/`, worker briefs, worktrees, execution attempts, commits, branches, or publication state.

## 5. Check and continue internally

Run the exact read-only mechanical boundary:

```shell
python3 "<atlas-plugin-root>/tools/atlas_planning.py" check --run "<run-directory>" --stage tickets
```

`BLOCKED` returns every mechanical gap to this producer without changing authoritative state. Repair only candidate-owned bytes and rerun. PASS proves mechanics only; it is not semantic judgment or acceptance.

After mechanical `PASS`, perform the exact named internal handoff to `atlas:control-planning` without asking the user to issue another routing command. Load that exact owner under [`../../references/internal-owner-loading.md`](../../references/internal-owner-loading.md). Pass the unchanged `<run-directory>` and explicit stage `tickets`; do not invoke a reviewer, request approval, or record acceptance in this producer.

After the authority adapter returns, re-read `planning-control.json`. Success is exact current ticket-graph acceptance with status `READY_FOR_EXECUTION`. Stop at that execution boundary. Do not select or execute a ticket.
