"""Task 2.4 — deterministic failure selection (in refine.py).

``select_failure(candidates)`` picks the worst failure by ``FailureClass`` total
order, tiebreaking on a RUN-RELATIVE locator (never an absolute path — Skeptic
E6), so selection is fully deterministic and reproducible.
"""

from __future__ import annotations

import pytest

from personal_os.engine.contract.enums import FailureClass
from personal_os.engine.core.refine import select_failure


def test_selects_worst_class():
    cands = [
        {"failure_class": "TEST_FAILURE", "locator": "a.py"},
        {"failure_class": "CLEAN_INSTALL_BLOCKER", "locator": "b.py"},
        {"failure_class": "DOCUMENTED_COMMAND_FAILURE", "locator": "c.py"},
    ]
    chosen = select_failure(cands)
    assert chosen["failure_class"] == FailureClass.CLEAN_INSTALL_BLOCKER.name


def test_tiebreak_is_stable_run_relative_locator():
    cands = [
        {"failure_class": "TEST_FAILURE", "locator": "z_later.py"},
        {"failure_class": "TEST_FAILURE", "locator": "a_earlier.py"},
    ]
    # Same class -> lexicographically-smallest run-relative locator wins.
    assert select_failure(cands)["locator"] == "a_earlier.py"


def test_tiebreak_rejects_absolute_locator():
    cands = [{"failure_class": "TEST_FAILURE", "locator": "/abs/path.py"}]
    with pytest.raises(ValueError):
        select_failure(cands)


def test_empty_candidates_raises():
    with pytest.raises(ValueError):
        select_failure([])


def test_deterministic_across_input_order():
    a = [
        {"failure_class": "TEST_FAILURE", "locator": "b.py"},
        {"failure_class": "TEST_FAILURE", "locator": "a.py"},
    ]
    b = list(reversed(a))
    assert select_failure(a) == select_failure(b)
