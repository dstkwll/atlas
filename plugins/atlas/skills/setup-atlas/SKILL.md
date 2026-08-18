---
name: setup-atlas
description: Configure a machine for the Atlas skills — establish where planning artifacts live. Run once per machine before the other skills are used.
disable-model-invocation: true
---

# Setup Atlas

Establish where Atlas skills read and write. One question has to be answered before any other skill can run: **what is the planning root?** Everything else is deferred until a skill actually needs it.

## Where the configuration file lives

Each operating system designates a location for application configuration, and Atlas uses it. Write to the platform-native path:

| Platform | Path |
|---|---|
| Windows | `%APPDATA%\atlas\config.yaml` |
| macOS, Linux | `$XDG_CONFIG_HOME/atlas/config.yaml`, or `~/.config/atlas/config.yaml` when that variable is unset |

When reading, check the platform-native path first, then `~/.atlas/config.yaml`. The second is a legacy location that still resolves, so a configuration written under either convention is found.

**Configuration is per machine.** The planning root is an absolute path that differs between machines, so a configuration file that syncs would carry one machine's path onto another where it does not resolve — which is why the platform-native locations, outside synchronized document folders, are used. Run this skill once on each machine.

## The planning root

The root is where planning artifacts live. It takes one of two forms, and the choice is the user's:

- **Repository-relative** — `.planning/` inside the repository being changed. The default, and correct where work is confined to one repository. Planning artifacts version alongside the code they describe.
- **External** — an absolute path to a directory that already exists. Correct where one piece of work commonly spans several repositories and no single one of them is an honest home for the artifacts describing it.

An external root is a considered departure: the specification and the code no longer share a commit, and review loses the contract unless the root resolves in the reviewer's environment. Where the work fits in one repository, the repository-relative form is better.

**Ask. Never default to a path.** State both forms, recommend the repository-relative one where the repository is the obvious scope, and let the user answer.

An external root must already exist and be readable. This configuration names a location; it does not clone, authenticate, synchronize, lock, or provision anything.

## Steps

### 1. Establish the current state

Read the configuration file, checking the platform-native path and then `~/.atlas/config.yaml`. Report what is already configured, and where it was found.

A configured machine needs no setup. Say so and stop rather than re-asking settled questions.

Check whether the working directory is inside a git repository, and name it — it decides which root form to recommend.

### 2. Ask for the planning root

Repository-relative `.planning/`, or an external absolute path. Lead with a recommendation — repository-relative where a single repository is the obvious scope — so it can be accepted in a word.

Skip any question the environment has already settled. Where the working directory is a repository and the user names no external root, the answer is repository-relative and the question need not be asked.

### 3. Confirm before writing

Show the exact configuration to be written and the path it goes to, using that platform's separators. Wait for the user to accept it.

Report and stop if an external root does not exist or is not readable. This skill does not create the root.

Stop if the configuration path resolves inside a synchronized folder such as OneDrive, iCloud Drive, or Dropbox. A synchronized configuration carries one machine's absolute planning root onto another where it does not resolve — a hard breakage, not a trade-off.

Warn, and continue, if the planning root itself sits inside one. Synchronized planning artifacts are a legitimate choice; concurrent edits from two machines are the risk, and any absolute path recorded inside them still breaks across machines. The user makes that trade knowingly.

### 4. Write the configuration

```yaml
artifacts:
  planning_root: .planning        # or an absolute path
```

Other `artifacts` keys are left unset and fall back to the defaults in
`architecture/09-reference-config.md` — `evidence/` and `spikes/` beneath the run.

Report the path written and where the next run will land. Placement of an individual run
under an external root is a per-run judgement, not configuration — see
`../discovery/references/run-layout.md`.

## Standing rules

**Configuration is the only source of truth for the root.** No skill hardcodes a path, and no artifact records an absolute path that would resolve differently for a different reader. A root reachable only by its author cannot be referenced by anyone else.

**Ask about what is needed now.** Later skills will want configuration this one does not collect. Each earns its question when a skill actually reads it — a setup that asks twenty questions to save twenty seconds is worse than one that asks two.
