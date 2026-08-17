# Issue tracker: Dev-workflow wiki topics (vault-backed local markdown)

Issues, specs, and tickets for this repo live as markdown **inside the dev-workflow
topic folder** in the Obsidian vault — co-located with that thread's `manifest.md`,
`brainstorm.md`, and `plan.md`. This maps Matt Pocock's engineering artifacts onto the
existing `/dev:*` topic convention instead of creating a parallel `.scratch/` tree.

This is a local-markdown tracker (no `gh`/`glab`); the files just live in the vault,
not in the repo.

## Resolving the topic folder

Read the same config the `/dev:*` skills use — `~/.copilot/config/copilot-vault.json`
— and join `vaultRoot` + `paths.topics` + `<slug>` to get the topic folder:

```
<vaultRoot>/<paths.topics>/<slug>/
```

Do **not** hard-code the resolved path in `docs/agents/issue-tracker.md`; always read it
from the config so it stays correct across machines. (`paths.topics` defaults to
`topics`.)

`<slug>` is the **dev-workflow topic slug** — the same slug `/dev:*` uses. Resolve it
in this order (first match wins):

1. If you're working an active dev thread, use the `thread_id` from that topic's
   `manifest.md`.
2. Otherwise derive per `copilot-vault.contract.md` §1 and normalize per §3
   (lowercase ASCII kebab-case; reserved words
   `archive/topics/sessions/weekly/reports/quarterly` rejected).

Lazy-create `<topics>/<slug>/` (and its `issues/` subdir) if missing.

## Conventions

- The spec is `<topics>/<slug>/spec.md`
- Implementation tickets are one file per ticket at
  `<topics>/<slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order
  (blockers first) — never a single combined tickets file
- Triage state is a `Status:` line near the top of each issue file (role strings in
  `triage-labels.md`)
- Blocking edges are a `Blocked by: <NN>, <NN>` line near the top; a ticket is
  unblocked when every file it lists is resolved/closed
- Comments and conversation history append to the bottom under a `## Comments` heading

**Boundary with the dev workflow:** these files sit alongside the thread's
`manifest.md` / `brainstorm.md` / `plan.md`, but the Matt Pocock skills write **only**
`spec.md`, `issues/*.md`, and `map.md`. They do **not** modify `manifest.md` — the
`/dev:*` skills own that file.

## When a skill says "publish to the issue tracker"

Create a new file under `<topics>/<slug>/` (creating the directory if needed). A spec
goes to `spec.md`; tickets go to `issues/<NN>-<slug>.md`.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path within the current topic's `issues/` directory.
The user will normally pass the path or the ticket number (`NN`) directly.

## Pull requests as a request surface

**PRs as a request surface: no.** Pull-request flows are handled by `/dev:pr-create`,
`/dev:pr-feedback`, and `/dev:pr-review`; leave this off so `/triage-tasks` doesn't
pull PRs into the queue.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket, both
inside the topic folder.

- **Map**: `<topics>/<slug>/map.md` — the Notes / Decisions-so-far / Fog body.
- **Child ticket**: `<topics>/<slug>/issues/<NN>-<slug>.md`, numbered from `01`, with
  the question in the body. A `Type:` line records the ticket type
  (`research`/`prototype`/`grilling`/`task`); a `Status:` line records
  `claimed`/`resolved`.
- **Blocking**: a `Blocked by: <NN>, <NN>` line near the top. A ticket is unblocked
  when every file it lists is `resolved`.
- **Frontier**: scan `<topics>/<slug>/issues/` for files that are open, unblocked, and
  unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`,
  then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.
