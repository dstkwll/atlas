# Atlas

Give your main agent a software goal. Atlas guides discovery, design, implementation, review and recovery as needed, using one lead skill, optional artifact entry points, core activity guides and specialist runbooks. It needs no runtime dependencies, hooks or extra accounts.

In Copilot Agent mode, start a fresh chat and choose the **Atlas** profile from the agent picker, then describe your goal. In Copilot CLI, use `/agent` and select `atlas:atlas`, or start with `copilot --agent atlas:atlas`. For example:

```text
Add cancellation support to queued jobs. Inspect the existing design,
make ordinary implementation decisions, and bring me material choices with
 your recommendation.
```

The profile directs the main session to load the same canonical skill. It specifies no model or tool override; the host controls tool availability, permissions and project instructions. Atlas remains active for ordinary follow-ups on that task. Asking it to explore, explain, critique, advise or design can be the whole assignment and does not grant permission to implement.

If the profile is unavailable, invoke the Atlas plugin's skill from the `/` picker (it may appear as `/atlas` or `/atlas:atlas`) or ask: **Use the Atlas skill from the atlas plugin for this task: [goal].**

Existing organizational/project instructions and tool permissions continue to apply.

See the repository [setup guide](https://github.com/dstkwll/atlas/blob/main/SETUP.md) for installation, updates, manual skill use and continuity. All operational guidance is contained in [the skill](skills/atlas/SKILL.md) and its relative references; the profile is only a native entrypoint. No access to the Atlas repository or Drive is required during work.

For a concrete planning deliverable, ask Atlas to turn the discussion into a PRD, executable vertical slices or a recipient-oriented handoff. Optional `atlas-to-documentation`, `atlas-to-tickets` and `atlas-handoff` entry points load those same runbooks. Keep all sibling skill folders together when copying the full package; the wrappers depend on `skills/atlas/`. Producing the artifact does not authorize publishing tickets or starting implementation.

`atlas-to-documentation` defaults to PRD and also supports guides, architecture documents and references. `atlas-blast-radius` assesses wider effects; `atlas-reflect` runs a requested retrospective and writes a separate contextual file. Arena is a confirmed, bounded runbook only.
