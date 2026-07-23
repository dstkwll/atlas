"""Task 0.5 — the ``Validator`` protocol.

A validator has a stable identity (``id``/``version``) and a ``strength``, and
runs ``validate(workspace, node, config) -> Receipt``. Only validator/Core code
constructs the returned ``Receipt`` (invariant 1). Runtime-checkable so tests
and the router can assert conformance structurally.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .enums import ValidationStrength
from .receipt import Receipt


@runtime_checkable
class Validator(Protocol):
    """A deterministic check that mints a Core ``Receipt`` for a node."""

    id: str
    version: str
    strength: ValidationStrength

    def validate(self, workspace: Any, node: Any, config: Any) -> Receipt:
        """Run the check against the workspace/node; return a Core-minted receipt."""
        ...
