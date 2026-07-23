"""Goal Engine — the harness-agnostic proof-carrying refinement spine.

A deterministic-Python CORE (state machine, router, journal, receipts,
validators) that invokes LLM work only through a ``WorkerPort`` speaking
opaque artifact handles (never filesystem paths). The engine is never itself
an agent: it decides control flow from *validated* data; LLMs are edge
functions whose output is untrusted until Core validates it.

See ``~/Documents/Stockwell/Personal/wiki/projects/goal-engine/design.md`` for
the north-star architecture and ``decisions.md`` for the locked decisions.
"""
