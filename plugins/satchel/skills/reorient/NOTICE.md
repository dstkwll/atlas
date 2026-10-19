# Source notice

Adapted from Lauren Tan's (`poteto`) MIT-licensed `ketchup` in [cursor/plugins](https://github.com/cursor/plugins/blob/978ca6e9c0e012047cd5058b8e829240336e704e/pstack/skills/ketchup/SKILL.md), original shipped commit `978ca6e9c0e012047cd5058b8e829240336e704e`. The unchanged upstream license is included in `LICENSE`.

The [later source](https://github.com/cursor/plugins/blob/8838150c6b4829ea3c01782631213776d86df14a/pstack/skills/ketchup/SKILL.md), inspected at `8838150c6b4829ea3c01782631213776d86df14a`, supplies the explicit rule that pending items must not disappear behind counts or links to satisfy a word limit. The [upstream change rationale](https://github.com/cursor/plugins/pull/692) is source-reported evidence, not a reproduced Satchel result.

Changes: names the skill `reorient`; enables normal host discovery with a task-state catch-up trigger; preserves the time window, older pending user decisions, read-only catch-up and self-contained choices; removes the sibling `bro` dependency and mandatory presentation/visual rules; replaces checking every touched resource with narrowly scoped checks when they affect the next action; handles unavailable history and separately requested actions explicitly. There is no hard response word limit or required menu.

The owner's report that a previous reorientation skill became verbose motivated the shorter default. The adaptation summarizes established tradeoffs and recommendations; new advice is conditional on a request for it. No text from that private archived skill is distributed here. The [adaptation account](https://github.com/dstkwll/atlas/blob/main/docs/satchel/adaptations.md) records the retained behavior and deliberate changes. No external source or sibling skill is needed to use Reorient.
