#!/bin/bash
# personal-os comms-v0 stage-1 poller launcher (cron entrypoint).
# Runs the stdlib poller as a module so package imports resolve.
# Loads secrets from ~/.hermes/.env because cron `script` does NOT inherit the
# gateway environment. Only the keys we need are exported.
set -euo pipefail
cd "$(dirname "$0")/../.."   # -> repo root (~/atlas)

# Load required env from the Hermes .env (cron runs with a clean environment).
ENV_FILE="$HOME/.hermes/.env"
if [ -f "$ENV_FILE" ]; then
  while IFS= read -r line; do
    case "$line" in
      EMAIL_ADDRESS=*|GOOGLE_APP_PASSWORD=*|OBSIDIAN_VAULT_PATH=*)
        key="${line%%=*}"
        val="${line#*=}"
        val="${val%\"}"; val="${val#\"}"   # strip surrounding double quotes if present
        val="${val%\'}"; val="${val#\'}"   # strip surrounding single quotes if present
        export "$key=$val"
        ;;
    esac
  done < "$ENV_FILE"
fi

: "${PERSONAL_OS_CONFIG:=${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Stockwell}/personal-os/config.json}"
export PERSONAL_OS_CONFIG
exec ./.venv/bin/python -m personal_os.poller.poll "$@"
