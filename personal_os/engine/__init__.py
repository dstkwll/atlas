"""Goal Engine — the harness-agnostic proof-carrying refinement spine.

A deterministic-Python CORE (state machine, router, journal, receipts,
validators) that invokes LLM work only through a ``WorkerPort`` speaking
opaque artifact handles (never filesystem paths). The engine is never itself
an agent: it decides control flow from *validated* data; LLMs are edge
functions whose output is untrusted until Core validates it.

See the project's design + decisions notes (the north-star architecture and the
locked decisions) for the full spec.
"""
