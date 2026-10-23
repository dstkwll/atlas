# Discover and maintain a session canvas

Accepted October 22, 2026, after collaborative design and explicit implementation authorization. This adds an independently usable Satchel skill; Atlas's lead contract is unchanged.

## Decision and reason

Session Canvas helps each user discover what visual orientation would serve their conversation, then generates and maintains that view. It reads existing context, develops missing direction with focused questions and meaningful alternatives, and confirms a short text-only brief before rendering. Delaying the first visual reduces anchoring on the first layout. The project itself need not be settled: choices and uncertainty can be the content.

Choose and combine useful patterns for exploration, progress or understanding after discovery. A fixed dashboard would be easier to maintain but would impose needs on every user. Entirely bespoke construction without backing guidance would offer freedom but less reusable help. The accepted middle course keeps shared discovery and upkeep while consulting only relevant methods. Chat steering, direct interaction, level of detail and upkeep remain choices for each invocation. A combined overview with inspectable reasons was the design walkthrough's preference, not a universal layout.

The existing lead performs a brief alignment check after each completed user exchange by default, updating changed content and preserving a useful layout. This retains the requested ongoing orientation without a second reviewer or full redraw every turn. A visible assessment cutoff is distinct from file modification time; checking and finding no change still counts. A passive signal may indicate activity since that cutoff only after the actual host behavior is verified. Activity is not an assessed mismatch. Reconnection or missing history must not imply freshness, and revising the map must not legitimize agent drift from accepted intent.

Copilot desktop is the primary target, using its existing canvas builder and session-scoped extension mechanism where available. Codex uses an available saved-artifact/preview surface, with separate verification. Host mechanics belong in conditional guidance; they do not become a shared runtime or a promise of parity. The package ships instructions, not an extension, listener, controller, scheduler or fixed renderer.

Maintenance is scoped to one conversation. Preserve ordinary outputs without promising automatic cross-session discovery or synchronization. Same-session recovery requires checking saved content against context. Skill invocation authorizes the requested canvas work within existing permissions, not the underlying tasks depicted in it.

## Consequences and evidence

The skill installs independently; Atlas and Show Me are optional companions. Its entry describes ongoing session maps, preserving ordinary one-off explanations and diagrams without imposing canvas discovery on them. Supporting view and host guidance ships within the same folder.

This is instructional behavior, not enforcement of every-exchange updates. The [validation summary](../validation/session-canvas.md) distinguishes source checks, fictional behavioral trials and actual host observations. Unavailable desktop evidence limits the release claim rather than becoming evidence that the design works or fails. No automatic activity indicator should be advertised from SDK declarations alone.
