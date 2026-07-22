"""Read-only IMAP capture (Q3/Q5).

Stdlib `imaplib` only. Never mutates the mailbox:
  * SELECT is issued readonly (EXAMINE) so no flags change.
  * Bodies fetched with BODY.PEEK[...] so the \\Seen flag is never set.

The transport is injectable: `fetch_new` takes a `conn` object exposing the
imaplib.IMAP4 methods we use, so unit tests run against a fake with zero network.
"""

from __future__ import annotations

import email
import hashlib
import re
from email.header import decode_header, make_header


def _decode(raw) -> str:
    if raw is None:
        return ""
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return str(raw)


def _normalize_subject(subject: str) -> str:
    s = subject.lower().strip()
    s = re.sub(r"^(re|fwd|fw):\s*", "", s)          # strip one reply/forward prefix
    s = re.sub(r"\s+", " ", s)
    return s


def semantic_source_key(sender: str, subject: str) -> str:
    """Layer-2 dedup key: hash(sender | normalized-subject)."""
    basis = f"{sender.lower().strip()}|{_normalize_subject(subject)}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def _strip_html(html: str) -> str:
    """Very small HTML→text fallback for emails that ship only text/html.
    Drops script/style, converts breaks to newlines, strips tags + entities."""
    import html as _htmlmod

    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?i)<br\s*/?>", "\n", html)
    html = re.sub(r"(?i)</p>", "\n\n", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = _htmlmod.unescape(html)
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n\s*\n\s*\n+", "\n\n", html)
    return html.strip()


def _clean_body(full_bytes: bytes) -> str:
    """Extract a human-readable body from a full RFC822 message.

    Walks the MIME tree, prefers the first text/plain part; falls back to a
    stripped text/html part. This is what fixes the garbled '--_----DvM...'
    MIME-soup snippet: we never render raw multipart bytes, only the decoded
    text of the chosen part.
    """
    try:
        msg = email.message_from_bytes(full_bytes)
    except Exception:
        return ""

    def _decode_part(part) -> str:
        try:
            payload = part.get_payload(decode=True)
            if payload is None:
                return ""
            charset = part.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
        except Exception:
            return ""

    plain, html = "", ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.is_multipart():
                continue
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if "attachment" in disp.lower():
                continue
            if ctype == "text/plain" and not plain:
                plain = _decode_part(part)
            elif ctype == "text/html" and not html:
                html = _decode_part(part)
    else:
        if msg.get_content_type() == "text/html":
            html = _decode_part(msg)
        else:
            plain = _decode_part(msg)

    text = plain.strip() or _strip_html(html)
    # collapse excessive blank lines / trailing whitespace
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()
    return text


def _parse_headers_and_snippet(header_bytes: bytes, full_bytes: bytes) -> dict:
    msg = email.message_from_bytes(header_bytes)
    sender = _decode(msg.get("From"))
    subject = _decode(msg.get("Subject"))
    message_id = (msg.get("Message-ID") or "").strip()
    date = (msg.get("Date") or "").strip()
    list_unsub = msg.get("List-Unsubscribe")
    headers = {}
    if list_unsub:
        headers["List-Unsubscribe"] = list_unsub
    snippet = _clean_body(full_bytes) if full_bytes else ""
    return {
        "from": sender,
        "subject": subject,
        "message_id": message_id,
        "date": date,
        "headers": headers,
        "snippet": snippet[:2048],
    }


def get_uidvalidity(conn, mailbox: str) -> int:
    """EXAMINE (readonly select) the mailbox and return its UIDVALIDITY."""
    typ, _ = conn.select(mailbox, readonly=True)
    if typ != "OK":
        raise RuntimeError(f"could not EXAMINE mailbox {mailbox}")
    typ, data = conn.status(mailbox, "(UIDVALIDITY UIDNEXT)")
    if typ != "OK":
        raise RuntimeError("could not read UIDVALIDITY/UIDNEXT")
    line = data[0].decode() if isinstance(data[0], bytes) else str(data[0])
    m = re.search(r"UIDVALIDITY (\d+)", line)
    if not m:
        raise RuntimeError(f"no UIDVALIDITY in status response: {line!r}")
    return int(m.group(1))


def get_uidnext(conn, mailbox: str) -> int:
    typ, data = conn.status(mailbox, "(UIDNEXT)")
    if typ != "OK":
        raise RuntimeError("could not read UIDNEXT")
    line = data[0].decode() if isinstance(data[0], bytes) else str(data[0])
    m = re.search(r"UIDNEXT (\d+)", line)
    if not m:
        raise RuntimeError(f"no UIDNEXT in status response: {line!r}")
    return int(m.group(1))


def fetch_since(conn, mailbox: str, after_uid: int) -> list[dict]:
    """Return metadata dicts for messages with UID strictly greater than after_uid.

    Read-only: EXAMINE select + BODY.PEEK fetch. Each dict carries a `uid` field.
    """
    typ, _ = conn.select(mailbox, readonly=True)
    if typ != "OK":
        raise RuntimeError(f"could not EXAMINE mailbox {mailbox}")

    typ, data = conn.uid("search", None, f"UID {after_uid + 1}:*")
    if typ != "OK":
        raise RuntimeError("UID SEARCH failed")
    raw = data[0].decode() if data and isinstance(data[0], bytes) else (data[0] or "")
    uids = [int(x) for x in raw.split() if x.isdigit() and int(x) > after_uid]

    out = []
    for uid in sorted(uids):
        typ, hdr = conn.uid("fetch", str(uid), "(BODY.PEEK[HEADER] X-GM-MSGID)")
        if typ != "OK" or not hdr or hdr[0] is None:
            continue
        header_bytes = hdr[0][1] if isinstance(hdr[0], tuple) else b""
        # X-GM-MSGID (Gmail extension) rides in the untagged FETCH response line,
        # e.g. b'12 (X-GM-MSGID 1770... UID 138432 BODY[HEADER] {NNNN}'. Parse it
        # from whichever part of the response carries it.
        gm_msgid = ""
        for part in hdr:
            blob = part[0] if isinstance(part, tuple) else part
            if isinstance(blob, bytes):
                m = re.search(rb"X-GM-MSGID\s+(\d+)", blob)
                if m:
                    gm_msgid = m.group(1).decode()
                    break
        # Fetch the full raw message (PEEK, capped) so we can parse the MIME
        # tree and pull a clean text/plain (or stripped HTML) body instead of
        # rendering raw multipart soup. 64KB cap keeps it bounded.
        typ2, txt = conn.uid("fetch", str(uid), "(BODY.PEEK[]<0.65536>)")
        full_bytes = b""
        if typ2 == "OK" and txt and txt[0] is not None and isinstance(txt[0], tuple):
            full_bytes = txt[0][1] or b""
        meta = _parse_headers_and_snippet(header_bytes, full_bytes)
        meta["uid"] = uid
        meta["gm_msgid"] = gm_msgid
        meta["source_key"] = semantic_source_key(meta["from"], meta["subject"])
        out.append(meta)
    return out
