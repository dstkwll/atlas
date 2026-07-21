import json
import os

import pytest

from personal_os.poller.config import load_config, resolve_config_path, ConfigError


def _write_cfg(tmp_path):
    d = tmp_path / "personal-os"
    d.mkdir(parents=True)
    p = d / "config.json"
    p.write_text(json.dumps({"mailbox": "INBOX", "imap_host": "imap.gmail.com"}))
    return str(p)


def test_resolve_explicit_path():
    env = {"PERSONAL_OS_CONFIG": "/x/y/config.json"}
    assert resolve_config_path(env) == "/x/y/config.json"


def test_resolve_from_vault(tmp_path):
    env = {"OBSIDIAN_VAULT_PATH": str(tmp_path)}
    assert resolve_config_path(env) == os.path.join(str(tmp_path), "personal-os", "config.json")


def test_resolve_fails_without_vault():
    with pytest.raises(ConfigError):
        resolve_config_path({})


def test_load_config_merges_secret(tmp_path):
    p = _write_cfg(tmp_path)
    env = {
        "PERSONAL_OS_CONFIG": p,
        "EMAIL_ADDRESS": "dan@example.com",
        "GOOGLE_APP_PASSWORD": "app-pw",
    }
    cfg = load_config(env)
    assert cfg["mailbox"] == "INBOX"
    assert cfg["_secret"] == {"address": "dan@example.com", "password": "app-pw"}


def test_load_config_fails_without_secret(tmp_path):
    p = _write_cfg(tmp_path)
    env = {"PERSONAL_OS_CONFIG": p, "EMAIL_ADDRESS": "dan@example.com"}
    with pytest.raises(ConfigError):
        load_config(env)


def test_load_config_fails_missing_file(tmp_path):
    env = {
        "PERSONAL_OS_CONFIG": str(tmp_path / "nope.json"),
        "EMAIL_ADDRESS": "d@e.com",
        "GOOGLE_APP_PASSWORD": "x",
    }
    with pytest.raises(ConfigError):
        load_config(env)
