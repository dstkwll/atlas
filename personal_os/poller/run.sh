#!/bin/bash
# personal-os comms-v0 stage-1 + stage-2 chain (cron entrypoint, no_agent job).
# Runs the dumb poller, then the deterministic classifier. Both are scripts —
# NO open-ended agent turn (the agent-driven stage-2 stalled on MCP init).
#
# SILENT by design: receipts go to a log file, NOT stdout. Under a no_agent cron
# job, empty stdout = no Discord message. Cards are minted quietly in the
# background; the morning digest job surfaces them. Only a hard error prints to
# stdout (so a broken poller can't fail silently).
#
# Loads secrets from ~/.hermes/.env (cron runs with a clean environment).
set -uo pipefail
cd "$(dirname "$0")/../.."   # -> repo root (~/atlas)

ENV_FILE="$HOME/.hermes/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS= read -r line; do
    case "$line" in
      EMAIL_ADDRESS=*|GOOGLE_APP_PASSWORD=*|OBSIDIAN_VAULT_PATH=*)
        key="${line%%=*}"; val="${line#*=}"
        val="${val%\"}"; val="${val#\"}"; val="${val%\'}"; val="${val#\'}"
        export "$key=$val"
        ;;
    esac
  done < "$ENV_FILE"
fi

: "${PERSONAL_OS_CONFIG:=${OBSIDIAN_VAULT_PATH:-$HOME/vault}/personal-os/config.json}"
export PERSONAL_OS_CONFIG
PY=./.venv/bin/python
LOG="${OBSIDIAN_VAULT_PATH:-$HOME/vault}/personal-os/state/poll.log"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Stage 1: poll. Stage 2: classify + mint. Receipts -> log file (silent on stdout).
poll_out="$("$PY" -m personal_os.poller.poll 2>&1)"; poll_rc=$?
classify_out="$("$PY" -m personal_os.agent.classify 2>&1)"; classify_rc=$?

{
  echo "[$TS] poll(rc=$poll_rc): $poll_out"
  echo "[$TS] classify(rc=$classify_rc): $classify_out"
} >> "$LOG" 2>/dev/null

# Only surface a hard failure (nonzero exit) to Discord; success stays silent.
if [ "$poll_rc" -ne 0 ] || [ "$classify_rc" -ne 0 ]; then
  echo "⚠️ personal-comms poll/classify error @ $TS"
  echo "poll(rc=$poll_rc): $poll_out"
  echo "classify(rc=$classify_rc): $classify_out"
  exit 1
fi
exit 0
