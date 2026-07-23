"""Task 0.1 — the engine schema version is a valid, stable semver string."""

from __future__ import annotations

import re

from personal_os.engine.contract import ENGINE_SCHEMA_VERSION


def test_engine_schema_version_is_semver():
    assert isinstance(ENGINE_SCHEMA_VERSION, str)
    assert re.fullmatch(r"\d+\.\d+\.\d+", ENGINE_SCHEMA_VERSION)


def test_engine_schema_version_is_v0():
    assert ENGINE_SCHEMA_VERSION == "0.1.0"
