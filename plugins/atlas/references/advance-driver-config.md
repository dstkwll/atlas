# Advance driver configuration contract

Per-user settings for the guided `/atlas:advance` driver. This contract is **pinned ahead
of the driver implementation**: it fixes the schema, keys, and defaults now so the
behavioral work (judge/drive seam, leash, worker orchestration, terminal ship rung) lands
against a settled surface. `tests/Test-DriverConfig.ps1` holds the example below to this
document.

- **Location:** `~/.copilot/config/mp-advance.json`.
- **Scope:** per user. No per-repository override tier in this revision.
- **Absent file:** every key falls back to the default below; a missing file is never an error.
- **Invalid file:** an unknown key, a missing required child, an invalid enum, or an
  unsupported worker setting is a `config-invalid` fault. The read-only judge still reports;
  the drive half stops before any dispatch or mutation.

The object has exactly these six top-level keys.

## `workerLadder`

Resolves a work class to the worker that runs it. Exactly four rows, each with `workerKind`
(`child-session` or `sub-agent`), `model` (a host model id or `auto`), and `effort` (`low`,
`medium`, `high`, or `xhigh`).

| Row | `workerKind` | `model` | `effort` |
|---|---|---|---|
| `orchestrator` | `child-session` | `auto` | `high` |
| `tight-bounded-quick` | `sub-agent` | `auto` | `low` |
| `code-implement` | `child-session` | `auto` | `medium` |
| `design-prose-judgment` | `child-session` | `auto` | `high` |

`model: auto` defers to the host default. A specific model is honored reliably only on the
`sub-agent` dispatch path; a `child-session` model is **best-effort** — the kickoff override
is not always applied, so the driver surfaces the effective model and never assumes the
requested one took. The `orchestrator` row is a host preference for a session that launches
advance; a running advance never replaces its own session to satisfy it.

## `phaseSkillMap`

Resolves each internal acting phase to the skill that performs it, so lifecycle routing is
data, not hardcoded names. These keys are configuration codes, not the phase words the board
reports: a board reporting `implementation` maps to `implement`, while discovery gaps route
internally through `grilling` or `wayfinder`. Exactly six string entries.

| Entry | Default |
|---|---|
| `grilling` | `grill-with-docs` |
| `wayfinder` | `wayfinder` |
| `spec` | `to-spec` |
| `tickets` | `to-tickets` |
| `implement` | `factory-implement` |
| `ship` | `internal:ship` |

## `parallelism`

Governs implementation dispatch. Parallel work is earned by objective independence, never
assumed.

- `policy`: `eligible-only`.
- `requireParallelSafe`: `true` - a ticket must be explicitly declared parallel-safe. Dependency
  independence is enforced separately by the wave's dependency barrier and never substitutes for
  this declaration; an undeclared ticket is unknown, and unknown is treated exactly as false.
- `codeOnly`: `true` — non-code work runs sequentially.
- `requireNoHitl`: `true` — a ticket that may need human input runs sequentially.
- `integration`: `sequential` — even when workers ran concurrently, the controller integrates
  one at a time.

## `leash`

How far the driver may traverse before it stops. The leash authorizes traversal, not mutation.

- `default`: `one-step`. Judge the current rung, show the board, recommend, and stop when no
  further grant is given.
- Accepted ceilings: `one-step`, `spec`, `tickets`, `implementation`, `ship`, `pr`.
- `archive` is deliberately **not** a ceiling. It is always human-approved.
- Natural-language grants normalize to these ceiling values. Autopilot uses the same leash
  representation with ceiling `ship` unless the grant explicitly names PR creation.

## `coverage`

The spec-to-tickets traceability fallback.

- `fallback`: `soft-advisory` (a spec with no enumerated work items yields an advisory, not a
  block) or `hard` (missing enumeration blocks). Default `soft-advisory`; tighten to `hard`
  once enumeration is universal.

## `receipt`

The terminal ship receipt.

- `destination`: `local-topic` — written beside the topic.
- `fileName`: `ship-receipt.md`.
- `write`: `silent-on-green` — a green (or green-with-accepted-debt) verdict writes the receipt
  as the last automated act; a blocked verdict writes nothing.
- `prLink`: `refresh-after-authorized-create` — when a grant names PR creation, the receipt is
  refreshed with the PR link.
