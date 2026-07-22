"""Fake IMAP conn tests -- no network, no live Gmail.

The fake exposes only the methods imap_client uses: select, status, uid.
Read-only invariant is asserted by checking select(readonly=True) and that
only BODY.PEEK fetches are issued (never BODY[...] which would set \\Seen).
"""

from personal_os.poller.imap_client import (
    fetch_since, get_uidvalidity, get_uidnext, semantic_source_key,
)


def _raw_email(sender, subject, msgid, extra_headers=""):
    return (
        f"From: {sender}\r\n"
        f"Subject: {subject}\r\n"
        f"Message-ID: {msgid}\r\n"
        f"Date: Tue, 21 Jul 2026 09:00:00 -0700\r\n"
        f"{extra_headers}"
        f"\r\n"
    ).encode("utf-8")


class FakeIMAP:
    def __init__(self, messages, uidvalidity=111, uidnext=1000, gm_msgids=None):
        # messages: dict uid -> (header_bytes, text_bytes)
        # gm_msgids: optional dict uid -> decimal X-GM-MSGID string
        self.messages = messages
        self.gm_msgids = gm_msgids or {}
        self.uidvalidity = uidvalidity
        self.uidnext = uidnext
        self.select_calls = []
        self.fetch_specs = []

    def select(self, mailbox, readonly=False):
        self.select_calls.append((mailbox, readonly))
        return ("OK", [b"1"])

    def status(self, mailbox, what):
        return ("OK", [f'"{mailbox}" (UIDVALIDITY {self.uidvalidity} UIDNEXT {self.uidnext})'.encode()])

    def uid(self, cmd, *args):
        cmd = cmd.lower()
        if cmd == "search":
            uids = " ".join(str(u) for u in sorted(self.messages))
            return ("OK", [uids.encode()])
        if cmd == "fetch":
            uid = int(args[0])
            spec = args[1]
            self.fetch_specs.append(spec)
            header_bytes, text_bytes = self.messages[uid]
            if "HEADER" in spec:
                # Gmail returns X-GM-MSGID in the untagged FETCH line prefix.
                prefix = f"{uid} (X-GM-MSGID {self.gm_msgids[uid]} UID {uid} ".encode() \
                    if uid in self.gm_msgids else b"x"
                return ("OK", [(prefix, header_bytes)])
            if "TEXT" in spec:
                return ("OK", [(b"x", text_bytes)])
        return ("NO", [b""])


def test_get_uidvalidity_and_uidnext():
    fake = FakeIMAP({}, uidvalidity=222, uidnext=555)
    assert get_uidvalidity(fake, "INBOX") == 222
    assert get_uidnext(fake, "INBOX") == 555


def test_fetch_since_returns_only_newer_uids():
    msgs = {
        900: (_raw_email("aunt@gmail.com", "Malcolm bday", "<a@x>"), b"come to the party"),
        950: (_raw_email("boss@work.com", "Q3 review", "<b@x>"), b"see attached"),
    }
    fake = FakeIMAP(msgs)
    out = fetch_since(fake, "INBOX", after_uid=920)
    uids = [m["uid"] for m in out]
    assert uids == [950]              # 900 filtered out (<= cursor)
    assert out[0]["from"] == "boss@work.com"
    assert out[0]["subject"] == "Q3 review"
    assert out[0]["source_key"] == semantic_source_key("boss@work.com", "Q3 review")
    assert "attached" in out[0]["snippet"]


def test_fetch_is_readonly_and_peek_only():
    msgs = {950: (_raw_email("x@y.com", "hi", "<c@x>"), b"body")}
    fake = FakeIMAP(msgs)
    fetch_since(fake, "INBOX", after_uid=0)
    # readonly select issued
    assert all(readonly for _, readonly in fake.select_calls)
    # every fetch used PEEK -- never a bare BODY[...] that would set \Seen
    assert all("PEEK" in spec for spec in fake.fetch_specs)


def test_source_key_ignores_reply_prefix():
    assert semantic_source_key("a@b.com", "Re: Dinner") == semantic_source_key("a@b.com", "Dinner")


def test_fetch_captures_gm_msgid():
    msgs = {950: (_raw_email("x@y.com", "hi", "<c@x>"), b"body")}
    fake = FakeIMAP(msgs, gm_msgids={950: "1770000000000000001"})
    out = fetch_since(fake, "INBOX", after_uid=0)
    assert out[0]["gm_msgid"] == "1770000000000000001"
    # X-GM-MSGID must be requested in the fetch spec
    assert any("X-GM-MSGID" in spec for spec in fake.fetch_specs)
