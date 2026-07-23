"""Ports — the harness-neutral seams the engine core talks to.

Everything crossing a port speaks opaque ``ArtifactHandle``s, never filesystem
paths (invariant 9), so each adapter (Hermes now, Copilot/ADO later) can resolve
handles to its own substrate without the core ever minting a path.
"""
