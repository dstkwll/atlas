"""tinyfmt — a trivial vendored string helper (no third-party deps).

Vendored inside ``brokencli.vendor`` so the fixture is fully hermetic: the
package installs and runs offline with zero external dependencies. The bug is
purely a wrong import *path* in ``cli.py``, not a missing installed dependency.
"""

from __future__ import annotations


def leftpad(text: str, width: int) -> str:
    """Right-justify ``text`` in a field of ``width`` (spaces on the left)."""
    return str(text).rjust(int(width))
