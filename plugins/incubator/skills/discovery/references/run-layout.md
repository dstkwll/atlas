# Run layout

Where a discovery run writes, and what its file starts as.

## Resolving the run directory

The planning root is configured, not fixed — see `architecture/03-artifact-model.md`. Read
`artifacts.planning_root` from `~/.atlas/config.yaml`, written by `setup-atlas`. A run
directory sits under that root, and `discovery` never invents a path outside it.

Where the root is repository-relative, a run is `<planning-root>/<slug>/` and the project
level below does not apply.

Where the root is external and `artifacts.run_placement` is `project`, and the work belongs
to an existing project:

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

`20-spec.md` and everything after it belong to later stages. Evidence produced by a dispatched research or explore route lands in `<run>/evidence/`; a spike writes to `<run>/spikes/<name>/`.

## `10-decisions.md` at creation

```markdown
---
run: <slug>
project: <project or null>
status: discovery
opened: 2026-08-16
repos: []
---

# Decisions — <title>

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

## Decisions
```

`repos` names every repository the work is expected to affect. It is descriptive planning metadata: it records what the work concerns, grants no access, and does not imply that execution spans those repositories. Leave it empty until the work's reach is known, and fill it as decisions establish scope.

Records append under `## Decisions` in the order they settle. The open frontier table is rewritten at every round boundary.
