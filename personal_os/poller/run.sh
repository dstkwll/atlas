#!/bin/bash
# personal-os comms-v0 stage-1 + stage-2 chain (cron entrypoint).
# Runs the dumb poller, then the deterministic classifier. Both are scripts —
# NO open-ended agent turn (the agent-driven stage-2 stalled on MCP init).
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

: "${PERSONAL_OS_CONFIG:=${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Stockwell}/personal-os/config.json}"
export PERSONAL_OS_CONFIG
PY=./.venv/bin/python

# Stage 1: poll (prints its own receipt line)
"$PY" -m personal_os.poller.poll
# Stage 2: classify + mint (prints a JSON receipt). Runs even if poll found nothing —
# it will discover any orphaned/leased handoffs on disk.
"$PY" -m personal_os.agent.classify
