---
name: personal-comms-reply
description: "Interactive reply handler for personal comms-v0. When Dan replies to a digest in #hermes-chat with '<number> <verb> [args]' (e.g. '2 done', '3 snooze til friday'), parse the intent and apply it via the deterministic apply_verb script. Surface-only — never touches email."
version: 0.1.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [personal-os, comms, reply, interactive, surface-only]
---

# Personal Comms v0 — Interactive Reply Handler

Dan clears his comms board by replying to the digest in natural language. Your
job: parse his reply into a structured verb + target, then call the
**deterministic** applier. You supply the intent parsing (genuine NLU — e.g.
"snooze til friday morning" → an ISO timestamp); the script owns the state
mutation. **You never touch email. Zero sends. T7 Gate-B closed.**

## When this fires

Dan sends a short message in #hermes-chat referencing a digest line, such as:
- `2 done` · `1 ack` · `3 dismiss`
- `2 snooze til friday` · `snooze 3 until tomorrow 9am` · `4 snooze 2 days`
- Multiple: `1 done, 3 ack` (apply each in order)

If a message is clearly NOT a comms reply (no leading/embedded digest number +
verb), ignore it — it's normal conversation.

## The four verbs (state-only)

| verb | meaning | needs |
|------|---------|-------|
| `done` | Dan handled it in Gmail; archive the card off-board | number/card_id |
| `snooze` | re-surface later | number + a `--when` ISO-UTC timestamp |
| `dismiss` | not actionable after all; archive + mark dismissed | number/card_id |
| `ack` | acknowledge; hold quietly, reset the nag for one cycle | number/card_id |

## Procedure

1. **Parse** the reply into one or more `(verb, target, when?)` tuples.
   - `target` = the digest line number (preferred) or a card_id.
   - For `snooze`, convert Dan's natural time expression to an **ISO-8601 UTC**
     timestamp. Interpret relative to now in Dan's local time (America/Los_Angeles)
     then convert to UTC. Examples: "friday" → next Friday 08:00 local;
     "tomorrow 9am" → tomorrow 09:00 local; "2 days" → now + 48h. If genuinely
     ambiguous, ask ONE brief clarifying question (inline, numbered options) —
     but prefer a sensible default (morning = 08:00 local) over interrogating.
2. **Apply** each tuple by running (from workdir `~/atlas`):
   ```
   ~/atlas/.venv/bin/python -m personal_os.agent.apply_verb \
       --verb <verb> --target <number> [--when <iso-utc>]
   ```
   It resolves the number via the latest digest manifest
   (`$VAULT/personal-os/state/digest_manifest.json`), mutates card state, and
   prints a JSON receipt `{ok, verb, card_id, subject, message}`.
3. **Confirm** back to Dan with each receipt's `message` (one line per action).
   If a receipt has `ok:false` (e.g. "card not found — already handled?" or a
   number not in the latest digest), relay that honestly.

## Hard rules

- Surface-only: NEVER send/draft email, never call a Gmail MCP mutation.
- Only the four verbs above. If Dan asks for something else (e.g. "reply to 2"),
  explain v0 is surface-only — he replies in Gmail himself; you can `done` it.
- One confirmation line per applied verb. Be terse.
- The applier is the single source of truth for card mutation — do not hand-edit
  card files.
