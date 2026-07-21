# Cron wiring — the dumb clock

Two Hermes cron jobs. **Cron holds zero business logic** — both are `no_agent`
script jobs that just run a launcher on a schedule. All logic lives in `poller/`
and `agent/` as deterministic Python.

> This is the as-shipped wiring reference. Both jobs are live. Scheduling is a
> state change — do it deliberately, one at a time.

## Architecture (as built)

Stage-2 is **deterministic scripts**, not an agent turn (an unattended cron agent
stalled on MCP init; scripts are reliable and cheaper). The only agent-in-the-loop
piece is the **interactive reply** (`agent/reply.md` skill), which runs in the live
gateway session, not a cron spawn.

```
poll+classify job ──> personal-comms-poll.sh ──> poll.py (stage-1, stdlib)
                                              └─> classify.py (stage-2, 1 LLM call/microbatch)
                                                     └─> mint_cards.py (deterministic)
digest job ─────────> personal-comms-digest.sh ─> digest.py (deterministic ranked digest)
reply (interactive) ─> personal-comms-reply skill ─> apply_verb.py (deterministic mutation)
```

## Job 1 — Poll + classify (the incremental loop)

- **schedule:** `*/30 * * * *`
- **no_agent:** `true`  (script's stdout delivered verbatim; silent on no-op)
- **script:** `personal-comms-poll.sh` (thin wrapper in `~/.hermes/scripts/` →
  `~/atlas/personal_os/poller/run.sh`, which runs poll.py then classify.py)
- **deliver:** `#hermes-chat` channel id
- **workdir:** `~/atlas`

Silent watchdog pattern: prints nothing when there's no new mail (no Discord
spam); logs receipts to `$VAULT/personal-os/state/poll.log`; a non-zero exit
surfaces an error alert.

## Job 2 — Morning digest (the heartbeat / pull-safety valve)

- **schedule:** `0 8 * * *`
- **no_agent:** `true`
- **script:** `personal-comms-digest.sh` → `~/atlas/personal_os/agent/run_digest.sh`
  (runs digest.py: reactivates due snoozes, ranks, writes the immutable per-digest
  manifest `state/digests/<digest_id>.json` + `latest_digest.json`, prints the
  two-tier digest with a `Digest: <id>` footer)
- **deliver:** `#hermes-chat` channel id
- **workdir:** `~/atlas`

## Reply loop (no cron — interactive)

A bare `<n> <verb>` reply (done/snooze/dismiss/ack) in #hermes-chat is recognized
via a memory steer → the `personal-comms-reply` skill loads → resolves the number
against the immutable disk manifest (keyed by the digest's `Digest: <id>`) → runs
`apply_verb.py`. Stateless and durable: survives `/new` because recognition is in
memory and the source of truth is the disk manifest, not any session transcript.

## Env

Both scripts self-heal: `poller/config.py` auto-hydrates `EMAIL_ADDRESS`,
`GOOGLE_APP_PASSWORD`, `OBSIDIAN_VAULT_PATH` from `~/.hermes/.env` when absent, so
every entrypoint works whether or not the caller sourced env.

## Why deterministic scripts (not an agent turn) for stage-2

An unattended cron agent stalled every run (MCP servers fail to connect on session
spawn, ~30s of retries). Collapsing stage-2 to one tool-less LLM classification
call wrapped in a deterministic script removed the flaky orchestration — and, since
email is untrusted input, a tool-less classifier also closes the prompt-injection
→ tool boundary. The agent is reserved for the interactive reply path only.
