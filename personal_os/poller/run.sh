#!/bin/bash
# personal-os comms-v0 stage-1 poller launcher (cron entrypoint).
# Runs the stdlib poller as a module so package imports resolve.
# Secrets (EMAIL_ADDRESS, GOOGLE_APP_PASSWORD, OBSIDIAN_VAULT_PATH) come from
# the gateway environment (~/.hermes/.env). PERSONAL_OS_CONFIG defaults to the
# vault location if unset.
set -euo pipefail
cd "$(dirname "$0")/../.."   # -> repo root (~/atlas)
: "${PERSONAL_OS_CONFIG:=${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Stockwell}/personal-os/config.json}"
export PERSONAL_OS_CONFIG
exec ./.venv/bin/python -m personal_os.poller.poll "$@"
