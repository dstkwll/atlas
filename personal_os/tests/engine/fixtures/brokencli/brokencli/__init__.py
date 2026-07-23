"""brokencli — a deliberately broken tiny CLI (goal-engine test fixture).

This package is the v0 bounded goal: "make this supplied tiny Python CLI
reproducibly runnable; fix the highest-impact failure; produce a verified
report."

It is GENUINELY BROKEN in a clean environment: ``cli.py`` imports its helper
from the wrong module path (``tinyfmt`` instead of the vendored
``brokencli.vendor.tinyfmt``), so a clean offline install succeeds but the
documented run command and the test suite BOTH fail with ``ModuleNotFoundError:
No module named 'tinyfmt'``.

The fix is a one-line import correction (the KNOWN-good patch the FakeWorker
emits). Chosen over a separately-installed vendored *wheel* dependency because
this toolchain (py3.9 + setuptools, no ``wheel``) can't reliably build/install a
second wheel offline — a wiring failure is the same class of "not reproducibly
runnable" defect while staying hermetic and deterministic.
"""
