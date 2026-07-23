"""The broken CLI entrypoint.

BUG (the highest-impact failure): the helper is imported from the top-level
module name ``tinyfmt``, but it is actually vendored at
``brokencli.vendor.tinyfmt``. In a clean environment ``tinyfmt`` is not
importable, so ``main()`` raises ``ModuleNotFoundError`` before it can do any
work — the CLI is not reproducibly runnable.

The fix: ``from brokencli.vendor.tinyfmt import leftpad``.
"""

from __future__ import annotations

import sys

from tinyfmt import leftpad  # noqa: F401  (BUG: wrong module path)


def format_label(text: str, width: int) -> str:
    """Left-pad ``text`` to ``width`` using the vendored helper."""
    return leftpad(text, width)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    text = argv[0] if argv else "hello"
    width = int(argv[1]) if len(argv) > 1 else 8
    print(format_label(text, width))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
