"""Keep the brokencli *fixture* out of the engine test suite's collection.

``fixtures/brokencli/`` is an installable sample project the HARD validator
builds and runs in an isolated venv — its ``test_brokencli.py`` is DELIBERATELY
broken (the bug the engine fixes) and uses stdlib ``unittest``. Collecting it as
part of the parent pytest run would (a) fail at import (the intentional bug) and
(b) misrepresent an engine test. Ignore the whole sample tree here.
"""

from __future__ import annotations

collect_ignore_glob = ["brokencli/*"]
