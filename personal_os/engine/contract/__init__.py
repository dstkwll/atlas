"""Frozen protocol layer — pure data + serializers, stdlib only, NO behavior.

Everything in this package is a contract: enums, the ``ProofObligationNode``,
evidence, the validator protocol + Core-minted ``Receipt``, the append-only
per-run journal, the containment ``Workspace``, and the run-dir/handle manager.
Behavior (staging, discharge, refine, scheduling, synthesis) lives in sibling
packages and depends on these frozen shapes.

``ENGINE_SCHEMA_VERSION`` is the single version constant for the engine's
on-disk contracts (nodes, evidence, receipts, journal events). Bump it when any
serialized contract shape changes.
"""

from __future__ import annotations

ENGINE_SCHEMA_VERSION = "0.1.0"
