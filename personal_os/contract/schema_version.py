"""Single source of truth for the card contract version.

Bump on any breaking frontmatter change. The poller stamps it onto every card;
the agent validates it. A mismatch is a hard error (drift detector).
"""

SCHEMA_VERSION = "0.1.0"
