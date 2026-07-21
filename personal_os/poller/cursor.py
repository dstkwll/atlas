"""UID cursor with UIDVALIDITY self-heal guard (Q5).

The cursor is a tiny JSON file in the vault state dir. It stores the last
processed IMAP UID plus the mailbox's UIDVALIDITY. If the server ever resets
UIDVALIDITY (rare, but it invalidates all UIDs), the poller must re-baseline to
"now" rather than silently reprocessing the whole mailbox or missing everything.

Read-only capture edge: the cursor is the ONLY state the poller writes.
"""

from __future__ import annotations

import json
import os
import tempfile


def load_cursor(path: str):
    """Return {"uidvalidity": int, "uid": int} or None on cold-start (missing file)."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {"uidvalidity": int(data["uidvalidity"]), "uid": int(data["uid"])}


def save_cursor(path: str, uidvalidity: int, uid: int) -> None:
    """Atomic write (temp + os.replace) so an interrupted poll never corrupts the cursor."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = json.dumps({"uidvalidity": int(uidvalidity), "uid": int(uid)})
    dir_name = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def needs_rebaseline(stored: dict | None, live_uidvalidity: int) -> bool:
    """True when stored cursor exists but the server's UIDVALIDITY has changed."""
    if stored is None:
        return False  # cold-start is handled by baseline, not rebaseline
    return int(stored["uidvalidity"]) != int(live_uidvalidity)
