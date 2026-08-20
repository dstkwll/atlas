# Run layout

Where a discovery run writes, and what its file starts as.

## Resolving the run directory

The planning root is configured, not fixed — see `architecture/03-artifact-model.md`. Read `artifacts.planning_root` from the configuration `setup-atlas` writes — on Windows
`%APPDATA%\atlas\config.yaml`, elsewhere `$XDG_CONFIG_HOME/atlas/config.yaml` or
`~/.config/atlas/config.yaml`, falling back to `~/.atlas/config.yaml`. A run directory sits
under that root, and `discovery` never invents a path outside it.

Where the root is repository-relative, a run is `<planning-root>/<slug>/` and the project
level below does not apply.

Where the root is external and the work belongs to an existing project:

```
<planning-root>/<project>/runs/<YYYY-MM>-<slug>/
```

Where it has no natural parent — a one-off change, an experiment belonging to nothing already tracked — it sits at the root as its own project:

```
<planning-root>/<slug>/
```

When it is unclear which applies, place the run under a project. Promoting it later is a move; splitting a project that grew around the wrong run is not.

Where no configuration exists, say so and offer `setup-atlas`, or take a root the user names
for this run alone. Never default to a path.

## Files

`discovery` writes exactly one file:

```
<run>/10-decisions.md
```

`20-spec.md` and everything after it belong to later stages. Evidence from a dispatched research or explore route lands under `<run>/evidence/`; a spike lands under `<run>/spikes/`. These fixed subdirectories are part of the V1 artifact layout in `architecture/03-artifact-model.md`; only the planning root above the run is configurable.

## `10-decisions.md` at creation

```markdown
---
run: <slug>
project: <project or null>
status: discovery
opened: <YYYY-MM-DD>
repos: []
---

# Decisions — <title>

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

## Decisions
```

`repos` names every repository the work is expected to affect — descriptive metadata that grants no access and does not imply execution spans them. Starts empty; step 5 fills it as decisions establish scope.

Records append under `## Decisions` in the order they settle. The open frontier table is rewritten at every round boundary.
