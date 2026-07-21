"""Config + secret loader (Q2).

Non-secret config lives in the VAULT as JSON (config-in-vault rule); the poller
reads it with stdlib `json` -- no pyyaml, stays dependency-free/portable.

Secret comes from the environment (never the vault, never the repo):
    EMAIL_ADDRESS, GOOGLE_APP_PASSWORD   (already live in ~/.hermes/.env)

Config path resolution order:
    1. PERSONAL_OS_CONFIG env var (explicit)
    2. $OBSIDIAN_VAULT_PATH/personal-os/config.json (default vault location)
"""

from __future__ import annotations

import json
import os


class ConfigError(RuntimeError):
    pass


_DOTENV_KEYS = ("EMAIL_ADDRESS", "GOOGLE_APP_PASSWORD", "OBSIDIAN_VAULT_PATH", "PERSONAL_OS_CONFIG")


def _hydrate_from_dotenv(e: dict) -> dict:
    """Self-healing fallback: if the needed keys aren't in the environment, read them
    from ~/.hermes/.env directly. This makes every entrypoint (poller, classify,
    digest, apply_verb) work whether or not the caller sourced .env first — the
    interactive reply path in particular runs from a gateway shell that may not have
    sourced it. Values already present in the environment always win (never overridden).
    """
    if all(e.get(k) for k in ("EMAIL_ADDRESS", "GOOGLE_APP_PASSWORD")):
        return e  # already have the secrets; nothing to do
    dotenv = os.path.expanduser("~/.hermes/.env")
    if not os.path.exists(dotenv):
        return e
    e = dict(e)
    try:
        with open(dotenv, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                if key in _DOTENV_KEYS and not e.get(key):
                    val = val.strip().strip('"').strip("'")
                    e[key] = val
    except OSError:
        pass
    return e


def resolve_config_path(env: dict | None = None) -> str:
    # Only self-heal from ~/.hermes/.env for the REAL environment; an explicit env
    # dict (tests, embedding) is taken as authoritative and never hydrated.
    e = _hydrate_from_dotenv(dict(os.environ)) if env is None else env
    explicit = e.get("PERSONAL_OS_CONFIG")
    if explicit:
        return explicit
    vault = e.get("OBSIDIAN_VAULT_PATH")
    if not vault:
        raise ConfigError(
            "no PERSONAL_OS_CONFIG and no OBSIDIAN_VAULT_PATH set -- cannot locate config"
        )
    return os.path.join(vault, "personal-os", "config.json")


def load_config(env: dict | None = None) -> dict:
    """Load merged config: file JSON + secret from env. Fail loud if secret missing."""
    e = _hydrate_from_dotenv(dict(os.environ)) if env is None else env
    path = resolve_config_path(e)
    if not os.path.exists(path):
        raise ConfigError(f"config file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)

    address = e.get("EMAIL_ADDRESS")
    password = e.get("GOOGLE_APP_PASSWORD")
    if not address:
        raise ConfigError("EMAIL_ADDRESS not set in environment")
    if not password:
        raise ConfigError("GOOGLE_APP_PASSWORD not set in environment")

    cfg["_secret"] = {"address": address, "password": password}
    return cfg


def vault_state_dir(env: dict | None = None) -> str:
    """Where the poller writes cursor / handoff / traces. Under the vault, alongside config."""
    path = resolve_config_path(env)
    return os.path.join(os.path.dirname(path), "state")
