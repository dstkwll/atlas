"""Adapters — concrete implementations of the engine's ports.

An adapter resolves opaque ``ArtifactHandle``s to its own substrate (a
FakeWorker to in-run artifacts; a HermesWorker to absolute files it feeds a
detached ``hermes`` process). Core stays harness-neutral; adapters absorb the
harness specifics behind the ``WorkerPort`` protocol.
"""
