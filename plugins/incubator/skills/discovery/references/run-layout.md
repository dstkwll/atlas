# Run layout

Where a discovery run writes, and what its file starts as.

## Resolving the run directory

The planning root is configured, not fixed — see `architecture/03-artifact-model.md`. A run directory sits under it, and `discovery` never invents a path outside it.

Where the work belongs to an existing project:

```
<planning-root>/<project>/runs/<YYYY-MM>-<slug>/
```

Where it has no natural parent — a one-off change, an experiment belonging to nothing already tracked — it sits at the root as its own project:

```
<planning-root>/<slug>/
```

When it is unclear which applies, place the run under a project. Promoting it later is a move; splitting a project that grew around the wrong run is not.

Ask for the planning root when configuration does not supply one. Never default to a path.

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
