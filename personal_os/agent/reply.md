---
name: personal-comms-reply
description: "Interactive reply handler for personal comms-v0 digest threads. When Dan replies to a comms digest (in its attached thread or #hermes-chat) with '<number> <verb>' (e.g. '1 done', '2 snooze til friday'), parse it against that digest's immutable manifest and apply via the deterministic apply_verb script. Freeform replies ('2 lets review together') open the card for discussion, never mutate. Surface-only — never touches email."
version: 0.2.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [personal-os, comms, reply, interactive, surface-only]
---

# Personal Comms v0 — Interactive Reply Handler

Dan clears his comms board by replying to a digest. The digest is delivered by a
cron job (often in its own attached thread). Each digest carries a `Digest: <id>`
footer and wrote an **immutable manifest** to disk at
`$VAULT/personal-os/state/digests/<id>.json` mapping number → card_id.

Your job: recognise a digest reply, resolve numbers **against the specific digest
they answer** (never "the latest"), and either apply an allowlisted verb or open
the card for discussion. **You never touch email. Zero sends. T7 Gate-B closed.**

## When this fires

A short message that answers a comms digest — in the digest's attached thread, or
in #hermes-chat referencing digest line numbers. Examples:
- `1 done` · `2 ack` · `3 dismiss` · `2 snooze til friday` · `1 done, 3 ack`
- `2 lets review together` (freeform — discuss, do NOT mutate)

If a message clearly isn't a digest reply, ignore it — normal conversation.

## Step 1 — Find the digest scope (which digest?)

A positional number is ONLY meaningful within a specific digest.
1. If the message (or its thread's opening brief) shows a `Digest: <id>`, use that id.
2. Else read the newest snapshot in `$VAULT/personal-os/state/digests/` (or the
   `latest_digest.json` pointer) — but ONLY when you're confident the reply
   answers that most-recent digest (e.g. it's the only one today). If ambiguous,
   ask Dan one brief question ("which digest — the 8am one?") rather than guess.

The vault path is `$OBSIDIAN_VAULT_PATH` (`/Users/danstockwell/Documents/Stockwell`).

## Step 2 — Parse each clause: verb vs conversation (STRICT grammar)

A clause **mutates only if it exactly matches** `<number> <verb> [args]` where verb
∈ {done, dismiss, ack, snooze}. Normalise trivial variants ("mark 1 done" → `1 done`),
but require an explicit verb token. **Everything else is conversation.**

- `1 done` → mutate (done)
- `2 snooze til friday` → mutate (snooze; convert time — see below)
- `1 done, 3 ack` → two mutations
- `2 lets review together` → NO mutation → open card 2, discuss
- `maybe dismiss 2?` / `reply to 2` → NO mutation → discuss/confirm first
- `1 done, 2 lets review` → apply 1, then open card 2 for discussion

Fail closed: "number + arbitrary text" is NOT authorization. When unsure, treat as
conversation and confirm before mutating.

## Step 3 — Apply verbs deterministically

For each verb clause, run (from workdir `~/atlas`):
```
cd ~/atlas && set -a && . ~/.hermes/.env && set +a && \
PERSONAL_OS_CONFIG="$OBSIDIAN_VAULT_PATH/personal-os/config.json" \
./.venv/bin/python -m personal_os.agent.apply_verb \
    --verb <verb> --target <number> --digest-id <id> [--when <iso-utc>]
```
**Env MUST be sourced first.** `apply_verb` reads `EMAIL_ADDRESS` +
`GOOGLE_APP_PASSWORD` + `OBSIDIAN_VAULT_PATH` from `~/.hermes/.env` (or it throws
ConfigError). The `set -a && . ~/.hermes/.env && set +a` prefix above loads them;
always include it. If you skip it you'll get a config error, not a silent wrong result.

**Just run it — do not ask permission first.** The applier is surface-only,
idempotent, and only moves a card between vault folders (never sends email, never
irreversible). Use your terminal tool and execute it directly; then relay the
receipt. Asking Dan to run it himself defeats the whole point — he replied so that
YOU would handle it. The only time to pause is genuine ambiguity about intent
(verb vs conversation) or which digest — never about permission to run the applier.

- `--digest-id` is REQUIRED for numbered targets (the applier fails closed without it).
- For `snooze`, convert Dan's natural time to **ISO-8601 UTC**. Interpret relative
  to now in America/Los_Angeles, then convert to UTC. "friday" → next Fri 08:00
  local; "tomorrow 9am" → tomorrow 09:00 local; "2 days" → now+48h. Prefer a
  sensible default (morning = 08:00 local) over interrogating.
- The applier is idempotent: acting on an already-handled card returns a truthful
  no-op receipt (`noop:true`), not an error. Relay it as-is.

Use each JSON receipt's `message` verbatim in your confirmation (one line per verb).

## Step 4 — Handle conversation clauses

For a freeform clause about card N: resolve N → card_id via the same digest
manifest, read the card at `$VAULT/personal-os/cards/<col>/<card_id>.md`, and
discuss its content with Dan (summarise the email, help him think it through).
Do NOT mutate, do NOT send/draft email. If he then says "ok done" / "snooze it",
apply the verb.

## Hard rules

- Surface-only: NEVER send/draft email or call a Gmail MCP mutation.
- Numbered mutations REQUIRE the digest id — never resolve a number against a
  mutable "latest" for a mutation.
- Explicit allowlisted verb required to mutate; everything else is conversation.
- The applier is the single source of truth for card mutation — never hand-edit cards.
- One confirmation line per applied verb. Be terse.
