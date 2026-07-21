import os

from personal_os.poller.cursor import load_cursor, save_cursor, needs_rebaseline


def test_missing_file_is_cold_start(tmp_path):
    assert load_cursor(str(tmp_path / "nope.json")) is None


def test_round_trip(tmp_path):
    p = str(tmp_path / "state" / "cursor.json")
    save_cursor(p, uidvalidity=111, uid=42)
    assert load_cursor(p) == {"uidvalidity": 111, "uid": 42}
    assert os.path.exists(p)


def test_needs_rebaseline_on_uidvalidity_change():
    stored = {"uidvalidity": 111, "uid": 42}
    assert needs_rebaseline(stored, 999) is True
    assert needs_rebaseline(stored, 111) is False


def test_cold_start_is_not_rebaseline():
    assert needs_rebaseline(None, 111) is False


def test_atomic_overwrite(tmp_path):
    p = str(tmp_path / "cursor.json")
    save_cursor(p, 111, 1)
    save_cursor(p, 111, 5)
    assert load_cursor(p)["uid"] == 5
