"""Core behavior — the deterministic engine internals.

Everything here is deterministic Python: staging, patch application, discharge,
refine, routing, scheduling, synthesis. LLM/worker labor is reached ONLY
through ports; Core validates every worker proposal before acting on it.
"""
