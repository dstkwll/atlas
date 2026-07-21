# Cron wiring — the dumb clock

Two Hermes cron jobs. **Cron holds zero business logic** — it only schedules the
poller and the digest. All logic lives in `poller/` and `agent/`.

> Do NOT schedule these until go-live. This doc is the wiring reference; the
> build session leaves scheduling to Dan's explicit approval (one state change
> at a time).

## Job 1 — Poll + classify (the incremental loop)

Runs the stage-1 poller as a `script`, then the agent turn consumes the handoff
and runs `agent/classify-and-digest.md`.

- **schedule:** `config.digest.poll_interval_cron` (default `*/30 * * * *`)
- **script:** `~/atlas/personal_os/poller/poll.py`  (stdout receipt feeds the agent prompt)
- **prompt:** "Load the `personal-comms-classify-digest` skill. The poller just
  ran; its receipt is above. Process any new handoff files in
  `$OBSIDIAN_VAULT_PATH/personal-os/state/handoff/`: dedup, classify, mint
  actionable cards, rank. Do NOT send the full digest on this tick unless a
  push-worthy item exists (HUMAN HOLD / consequence-escalation / unrecoverable
  failure). Surface-only, zero sends."
- **enabled_toolsets:** `["file", "terminal"]`
- **deliver:** `origin` (or the `#hermes-chat` channel id) so replies reach an agent.
- **workdir:** `~/atlas`

Env: the job must see `EMAIL_ADDRESS`, `GOOGLE_APP_PASSWORD`, `OBSIDIAN_VAULT_PATH`
(already in `~/.hermes/.env`, loaded by the gateway).

The poller must run with the repo importable. Since `script` runs the file
directly, wrap it so the package import works, e.g. a tiny launcher:
`cd ~/atlas && ./.venv/bin/python -m personal_os.poller.poll`
(create the launcher as `poller/run.sh` at go-live, or set the cron `script` to a
`.sh` that does the `cd` + module invocation).

## Job 2 — Morning digest (the heartbeat / pull-safety valve)

Forces the full two-tier digest once a day even on a quiet night.

- **schedule:** `config.digest.morning_push_cron` (default `0 8 * * *`)
- **prompt:** "Load `personal-comms-classify-digest`. First re-check `queued`
  cards for expired snoozes (move due ones back to actionable). Then compose and
  deliver the full action-first two-tier digest to #hermes-chat. If nothing
  needs Dan, the one-line header is the whole message. Surface-only."
- **enabled_toolsets:** `["file"]`
- **deliver:** `#hermes-chat`
- **workdir:** `~/atlas`

## Copy-paste creation (RUN ONLY AT GO-LIVE)

```
# Job 1 — poll every 30 min
cronjob action=create name="personal-comms poll" schedule="*/30 * * * *" \
  script="~/atlas/personal_os/poller/run.sh" workdir="~/atlas" \
  enabled_toolsets=["file","terminal"] deliver="<#hermes-chat id>" \
  prompt="<Job 1 prompt above>"

# Job 2 — morning digest at 08:00
cronjob action=create name="personal-comms digest" schedule="0 8 * * *" \
  workdir="~/atlas" enabled_toolsets=["file"] deliver="<#hermes-chat id>" \
  prompt="<Job 2 prompt above>"
```

## Why single-job (not two chained) for the loop

Q6 chose one job where `script` runs the poller and its output feeds the same
agent turn. If handoff batches ever grow large enough that inlining strains the
agent context, split into two jobs chained via `context_from`. Not needed at
personal scale (~30 mails/day).
