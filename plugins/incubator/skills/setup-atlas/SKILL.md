---
name: setup-atlas
description: Configure a machine for the Atlas skills — where planning artifacts live, and how runs are placed under that root. Run once per machine before the other skills are used.
disable-model-invocation: true
---

# Setup Atlas

Establish where Atlas skills read and write. One question has to be answered before any other skill can run: **what is the planning root?**

Everything else is derived from that answer or deferred until a skill actually needs it.

## Where the configuration file lives

Each operating system designates a location for application configuration, and Atlas uses it. Write to the platform-native path:

| Platform | Path |
|---|---|
| Windows | `%APPDATA%\atlas\config.yaml` |
| macOS, Linux | `$XDG_CONFIG_HOME/atlas/config.yaml`, or `~/.config/atlas/config.yaml` when that variable is unset |

When reading, check the platform-native path first, then `~/.atlas/config.yaml`. The second is a legacy location that still resolves, so a configuration written under either convention is found.

**Configuration is per machine, and never inside a synchronized folder.** The planning root is an absolute path that differs between machines, so a configuration file that syncs carries one machine's path onto another where it does not resolve. The platform-native locations sit outside synchronized document folders, which is most of why they are used. Run this skill once on each machine.

## The planning root

The root is where planning artifacts live. It takes one of two forms, and the choice is the user's:

- **Repository-relative** — `.planning/` inside the repository being changed. The default, and correct where work is confined to one repository. Planning artifacts version alongside the code they describe.
- **External** — an absolute path to a directory that already exists. Correct where one piece of work commonly spans several repositories and no single one of them is an honest home for the artifacts describing it.

An external root is a considered departure. It gives up properties the repository-relative form provides for free: the specification and the code no longer share a commit, review loses the contract unless the root resolves in the reviewer's environment, and atomicity across specification and code is gone. Where the work fits in one repository, the repository-relative form is better.

**Ask. Never default to a path.** State both forms, recommend the repository-relative one where the repository is the obvious scope, and let the user answer.

An external root must already exist and be readable. This configuration names a location; it does not clone, authenticate, synchronize, lock, or provision anything.

## Run placement

Under an external root, runs are placed one of two ways:

```
<planning-root>/<project>/runs/<YYYY-MM>-<slug>/     work belonging to an ongoing project
<planning-root>/<slug>/                              work with no natural parent
```

When it is unclear which applies, place the run under a project — promoting it later is a move, while splitting a project that grew around the wrong run is not.

Under a repository-relative root, a run is `<planning-root>/<feature-slug>/` and the project level does not apply.

## Steps

### 1. Establish the current state

Read the configuration file, checking the platform-native path and then `~/.atlas/config.yaml`. Report what is already configured, and where it was found.

A configured machine needs no setup. Say so and stop rather than re-asking settled questions.

Check whether the working directory is inside a git repository, and name it — it decides which root form to recommend.

### 2. Ask the questions

Lead each with a recommended answer so it can be accepted in a word.

1. **Planning root.** Repository-relative `.planning/`, or an external absolute path. Recommend repository-relative where a single repository is the obvious scope.
2. **Run placement**, only when the root is external. Whether runs nest under a project directory or sit directly at the root. Recommend nesting.

Skip any question the environment has already settled. Where the working directory is a repository and the user names no external root, the answer is repository-relative and the question need not be asked.

### 3. Confirm before writing

Show the exact configuration to be written and the path it goes to, using that platform's separators. Wait for the user to accept it.

Report and stop if an external root does not exist or is not readable. This skill does not create the root.

Report and stop if the configuration path resolves inside a synchronized folder such as OneDrive, iCloud Drive, or Dropbox — a synchronized configuration carries absolute paths onto machines where they do not resolve.

### 4. Write the configuration

```yaml
artifacts:
  planning_root: .planning        # or an absolute path
  run_placement: project          # project | flat — external roots only
```

Report the path written and what the values mean for where the next run will land.

## Standing rules

**Configuration is the only source of truth for the root.** No skill hardcodes a path, and no artifact records an absolute path that would resolve differently for a different reader. A root reachable only by its author cannot be referenced by anyone else.

**Ask about what is needed now.** Later skills will want configuration this one does not collect. Each earns its question when a skill actually reads it — a setup that asks twenty questions to save twenty seconds is worse than one that asks two.
