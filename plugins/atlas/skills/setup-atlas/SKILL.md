---
name: setup-atlas
description: Configure or verify Atlas on a machine; establish the planning root, dependencies, and installed-host calibration.
disable-model-invocation: true
---

# Setup Atlas

Establish the machine-local planning-artifact location and any repository bindings needed by a run. The planning root remains an artifact-location choice; repository bindings route stable portable identities to exact local Git object sources.

Resolve `<atlas-plugin-root>` from this installed skill before invoking packaged resources: it is the third parent of this file (`SKILL.md` → `setup-atlas/` → `skills/` → the plugin root) and must contain `requirements.txt` and `tools/`. Use that resolved absolute path; never assume the caller's working directory.

## Where the configuration file lives

Each operating system designates a location for application configuration, and Atlas uses it. Write to the platform-native path:

| Platform | Path |
|---|---|
| Windows | `%APPDATA%\atlas\config.yaml` |
| macOS, Linux | `$XDG_CONFIG_HOME/atlas/config.yaml`, or `~/.config/atlas/config.yaml` when that variable is unset |

When reading, check the platform-native path first, then `~/.atlas/config.yaml`. The second is a legacy location that still resolves, so a configuration written under either convention is found.

**Configuration is per machine.** An external planning root and repository bindings contain machine-specific absolute paths, so a configuration file that syncs would carry one machine's paths onto another where they do not resolve — which is why the platform-native locations, outside synchronized document folders, are used. Run this skill once on each machine.

## The planning root

The root is where planning artifacts live. It takes one of two forms, and the choice is the user's:

- **Repository-relative** — `.planning/` inside the repository being changed. The default, and correct where work is confined to one repository. Planning artifacts version alongside the code they describe.
- **External** — an absolute path to a directory that already exists. Correct where one piece of work commonly spans several repositories and no single one of them is an honest home for the artifacts describing it.

An external root is a considered departure: the specification and the code no longer share a commit, atomic contract-plus-code commits are lost, and review loses the contract unless the root resolves in the reviewer's environment. Where the work fits in one repository, the repository-relative form is better.

**Ask. Never default to a path.** State both forms, recommend the repository-relative one where the repository is the obvious scope, and let the user answer.

An external root must already exist and be readable. This configuration names a location; it does not clone, authenticate, synchronize, lock, or provision anything.

## Steps

### 1. Establish the current state

Read the configuration file, checking the platform-native path and then `~/.atlas/config.yaml`. Report what is already configured, and where it was found.

Preserve every existing configuration key and value not explicitly changed. A configured planning root needs no rewrite, and each existing confirmed repository binding remains authoritative unless the user explicitly commissions a replacement.

A configured machine needs no root rewrite. Say so rather than re-asking settled questions.

Check whether the working directory is inside a git repository, and name it — it decides which root form to recommend.

### 2. Ask for the planning root

Repository-relative `.planning/`, or an external absolute path. Lead with a recommendation — repository-relative where a single repository is the obvious scope — so it can be accepted in a word.

Skip the question only when an existing configuration already settles the planning root. Being inside a repository supports the recommendation but does not itself authorize a write.

### 3. Confirm before writing

For each repository needed by the run, commission or change exactly one stable repository identity to one canonical absolute path to an existing local Git repository or object source. A remote URL may help propose a stable identity, and the current checkout may help propose its canonical source path. A proposal grants no authority and never silently creates or changes a binding.

Validate each proposed source without requiring a run or claiming baseline readiness:

```shell
python3 "<atlas-plugin-root>/tools/atlas_repository.py" probe-source --source "<canonical-absolute-local-git-source>"
```

The probe validates only that the path is absolute, already exists without symlink substitution, and is a readable local Git source. It never chooses an identity, baseline, commit, or tree.

Show the exact configuration diff, the exact configuration path, and the exact identity/source pair. Wait for explicit confirmation before creating or changing a binding. Normal runs reuse a confirmed binding without asking again. Setup may inspect and write machine configuration, but must never sync, clone, fetch, authenticate, checkout, create a worktree, or mutate a repository.

Report and stop if an external root does not exist or is not readable. This skill does not create the root.

Stop if the configuration path resolves inside a synchronized folder such as OneDrive, iCloud Drive, or Dropbox. A synchronized configuration carries one machine's absolute planning root onto another where it does not resolve — a hard breakage, not a trade-off.

Warn, and continue, if the planning root itself sits inside one. Synchronized planning artifacts are a legitimate choice; concurrent edits from two machines are the risk, and any absolute path recorded inside them still breaks across machines. The user makes that trade knowingly.

### 4. Write the configuration

```yaml
artifacts:
  planning_root: .planning        # or an absolute path
repositories:
  bindings:
    "stable-repository-id": /canonical/absolute/existing/local/git/source
```

`artifacts.planning_root` is the only V1 artifact-location setting, not the only machine configuration. `repositories.bindings` is machine-local routing and never enters portable run, control, candidate, review, or acceptance artifacts. `evidence/` and `spikes/` are fixed beneath each run by `architecture/03-artifact-model.md`; setup does not configure them.

Merge only the confirmed changes into the existing configuration; do not replace unrelated keys or bindings. Report the path written. Every run will land at `<planning-root>/<feature-slug>/`; `atlas:start-run` chooses and validates the slug. An external root changes only the configured root, never the layout beneath it.

### 5. Verify the deterministic dependencies

The installed plugin includes `<atlas-plugin-root>/tools/atlas_control.py`, `<atlas-plugin-root>/tools/atlas_planning.py`, `<atlas-plugin-root>/tools/atlas_repository.py`, and the mandatory renderers. They require Python 3.9 or newer plus the packages pinned in `<atlas-plugin-root>/requirements.txt`. Verify with the platform-native Python launcher:

```shell
python3 -c "import sys, yaml, markdown_it; assert sys.version_info >= (3, 9)"
```

On Windows, use `py -3 -c "import sys, yaml, markdown_it; assert sys.version_info >= (3, 9)"`. If Python or a pinned dependency is missing, stop and explain that discovery may only prepare non-canonical `.20-prd.next.md`; Atlas cannot update the canonical PRD or legally close discovery without the deterministic tooling. Offer the exact installation command (`python3 -m pip install -r "<atlas-plugin-root>/requirements.txt"` or `py -3 -m pip install -r "<atlas-plugin-root>/requirements.txt"`) and run it only after explicit approval; installing packages is an external side effect.

Report whether the deterministic dependencies are ready. Never pretend a missing dependency is optional.

### 6. Verify repository readiness only when a run exists

Before a run exists, stop after source probing and confirmed configuration; do not invoke run-specific `verify --run`. Only after an initialized run exists, use `verify --run` to prove every effective identity/full-baseline pair against current confirmed machine bindings:

```shell
python3 "<atlas-plugin-root>/tools/atlas_repository.py" verify --run "<run-directory>"
```

On Windows use the same recorded `py -3` launcher. Report every gap and resume action from the complete verification report. A `BLOCKED` result is ordinary setup/dependency output: repair machine config or make the exact objects available offline, then rerun; setup does not canonicalize intake or provision repositories.

### 7. Calibrate an installed host when needed

After a new install or update, before claiming the installed host runs the current source, or when a host reports an enabled skill missing, follow [`references/installed-host-calibration.md`](references/installed-host-calibration.md). Keep installation bytes, deterministic runtime readiness, host recognition, skill discovery, procedure completion, and cross-skill handoff as separate claims. A one-host success is dated calibration only.

## Standing rules

**Configuration is the only source of truth for the root and local repository routes.** No skill hardcodes a path, and no portable artifact records a machine-local absolute path. A root reachable only by its author cannot be referenced by anyone else.

**Ask about what is needed now.** Later skills will want configuration this one does not collect. Each earns its question when a skill actually reads it — a setup that asks twenty questions to save twenty seconds is worse than one that asks two.
