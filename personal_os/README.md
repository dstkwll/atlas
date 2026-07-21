# personal-os — comms v0 (surface-only email loop)

The first executable capability of the personal agentic OS: a **surface-only**
email responsiveness loop. New Gmail is captured, noise-sieved, classified into
ranked cards in your Obsidian vault, and surfaced as a two-tier digest in
Discord. **v0 sends nothing** — it's a responsiveness *tracker*, not an email
client. You act in Gmail; you tell the board what happened.

## Architecture (three decoupled components, one contract)

```
poller/   stage-1 capture edge — dumb, stdlib-only, cron-invoked.
          Fetches UID>cursor, fail-open noise sieve, emits handoff JSONL + trace.
agent/    stage-2 LLM — reads handoff, classifies, mints cards, ranks, digests.
contract/ THE canonical card schema + ranking. Every component binds here,
          never to each other. This is the abstraction boundary.
cron/     the dumb clock — schedules poller + morning digest. Zero logic.
```

Components coordinate **only** through vault cards (queue-as-interface).
Any component can crash/restart/be rewritten; truth lives in the vault.

## The public-code / vault-config rule

This code is public. **Nothing personal is ever hardcoded** — every personal
value is a config entry set at install time. Code here = forcing function.

- **Code:** this repo (`atlas/personal_os/`), public.
- **Config:** `$OBSIDIAN_VAULT_PATH/personal-os/config.json` (in the vault,
  gitignored, synced to your other machines). Copy from `config/config.example.json`.
- **Secret:** `EMAIL_ADDRESS` + `GOOGLE_APP_PASSWORD` in `~/.hermes/.env`
  (already present). Never in the vault, never in the repo.
- **State:** `$OBSIDIAN_VAULT_PATH/personal-os/state/` (cursor, handoff, traces)
  and `.../cards/` (the board). Also in the vault, not the repo.

## Install

1. `cp personal_os/config/config.example.json "$OBSIDIAN_VAULT_PATH/personal-os/config.json"`
   and edit: noise rules, priority hierarchy, `malcolm_terms`, digest cadence.
2. Confirm `~/.hermes/.env` has `EMAIL_ADDRESS` and `GOOGLE_APP_PASSWORD` (Gmail
   app password, IMAP read is enough).
3. **Read-only smoke:** `PERSONAL_OS_CONFIG=... python3 -m personal_os.poller.poll --dry-run`
   → expect `cold-start-baseline`, `survivors: 0`. Your inbox is untouched
   (read-only, no `\Seen`, backlog quarantined behind the fresh cursor).
4. Schedule the two cron jobs — see `cron/install.md`. Do this only at go-live.

## Portability

The poller is Python-3.9 **stdlib only** (imaplib/email/json/hashlib) — it runs
on any machine with Python and the two env vars, no pip install. The interactive
Gmail MCP / WorkIQ MCP are a *separate, later* surface; the poller never depends
on them.

## Tests

```
python -m pytest personal_os/tests/ -v
```

## Scope (v0)

IN: capture, sieve, classify, rank, digest, state-only reply verbs
(`done`/`snooze`/`dismiss`/`ack`).
OUT: any email send/draft, the 12.7k backlog sweep (a future opt-in `--sweep`
seam), Todoist/Calendar, the plan layer (present but dormant — all cards atomic),
cross-instance isolation (work-integration effort).
