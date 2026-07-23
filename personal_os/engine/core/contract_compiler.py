"""Task 2.1 / 2.1a — the canonical execution-leaf contract compiler (SSOT).

This module is the SINGLE author of the canonical, versioned execution-leaf
contract. A refiner proposes a loose dict; ``compile_leaf_contract`` normalizes
it into exactly ``LEAF_CONTRACT_FIELDS`` (+ ``schema_version``), raising on any
missing OR extra field (fail-closed — Task 2.1a). Nothing else in the engine
hand-writes this schema: the ``HardCliValidator`` derives its expected fields
from ``LEAF_CONTRACT_FIELDS`` so the compiler and validator can never drift
(Panel P1-Arch-2).

``fingerprint(contract)`` is a stable canonical hash (``json.dumps`` with
``sort_keys``) used to prove refiner-emitted and fake-fulfilled contracts are
identical (Task 2.2 parity).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from personal_os.engine.contract import ENGINE_SCHEMA_VERSION

# The ONE canonical schema for an execution leaf. Order is the canonical order.
LEAF_CONTRACT_FIELDS = (
    "target",       # run-relative file the execution leaf must fix
    "objective",    # human-readable done statement
    "install_cmd",  # documented clean-env install command
    "run_cmd",      # documented run command
    "test_cmd",     # the executable test command (the HARD oracle)
)


def compile_leaf_contract(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a refiner proposal into the canonical versioned leaf contract.

    Raises ``ValueError`` on any missing or unexpected field (fail-closed). The
    input may or may not already carry ``schema_version`` (idempotent); the
    output always carries the current one.
    """
    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a dict")

    # Ignore an incoming schema_version (we restamp), but reject any OTHER extra.
    provided = {k: v for k, v in proposal.items() if k != "schema_version"}
    extra = set(provided) - set(LEAF_CONTRACT_FIELDS)
    if extra:
        raise ValueError(f"unexpected contract field(s): {sorted(extra)}")
    missing = set(LEAF_CONTRACT_FIELDS) - set(provided)
    if missing:
        raise ValueError(f"missing contract field(s): {sorted(missing)}")

    contract = {"schema_version": ENGINE_SCHEMA_VERSION}
    for field in LEAF_CONTRACT_FIELDS:
        contract[field] = provided[field]
    return contract


def fingerprint(contract: Dict[str, Any]) -> str:
    """Stable canonical hash of a contract (key-order independent)."""
    canonical = json.dumps(contract, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
