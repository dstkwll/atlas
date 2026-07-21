#!/bin/bash
# personal-os comms-v0 morning digest (cron entrypoint, no_agent job).
# Deterministic ranked digest -> stdout -> delivered verbatim to Discord.
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
exec ./.venv/bin/python -m personal_os.agent.digest
