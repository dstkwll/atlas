"""Trivial self-test for brokencli — currently RED (import bug in cli.py).

Uses stdlib ``unittest`` (NOT pytest) on purpose: the goal-engine HARD validator
runs this in a FRESH, isolated, OFFLINE venv that has no third-party test
runner and can't install one (--no-index). stdlib unittest needs nothing but
the installed package, so the fixture is fully hermetic and durable.

Documented command: ``python -m unittest discover -p 'test_*.py'`` (run from the
package root), or directly ``python -m unittest test_brokencli``.
"""

import unittest

from brokencli.cli import format_label


class TestFormatLabel(unittest.TestCase):
    def test_leftpads(self):
        self.assertEqual(format_label("hello", 8), "   hello")

    def test_no_pad_when_wide_enough(self):
        self.assertEqual(format_label("hello", 3), "hello")


if __name__ == "__main__":
    unittest.main()
