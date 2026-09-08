# Atlas

Give your main agent a software goal. Atlas guides discovery, design, implementation, review and recovery as needed, using one skill with core activity guides and optional specialist runbooks. It needs no runtime dependencies, hooks or extra accounts.

In Copilot Agent mode, start a fresh chat and choose the **Atlas** profile from the agent picker, then describe your goal. In Copilot CLI, use `/agent` and select `atlas:atlas`, or start with `copilot --agent atlas:atlas`. For example:

```text
Add cancellation support to queued jobs. Inspect the existing design,
make ordinary implementation decisions, and bring me material choices with
 your recommendation.
```

The profile directs the main session to load the same canonical skill. It specifies no model or tool override; the host controls tool availability, permissions and project instructions. Atlas remains active for ordinary follow-ups on that task. Asking it to explore, explain, critique, advise or design can be the whole assignment and does not grant permission to implement.

If the profile is unavailable, invoke the Atlas plugin's skill from the `/` picker (it may appear as `/atlas` or `/atlas:atlas`) or ask: **Use the Atlas skill from the atlas plugin for this task: [goal].**

This is Atlas from `dstkwll/atlas`, formerly Atlas successor. The original `atlas@dstkwll` pipeline plugin belongs to the separate legacy product now preserved in private `dstkwll/legacy-Atlas`. Enable the intended version for the project. Existing organizational/project instructions and tool permissions continue to apply.

See the repository [setup guide](https://github.com/dstkwll/atlas/blob/main/SETUP.md) for installation, updates, manual skill use, continuity and migration. All operational guidance is contained in [the skill](skills/atlas/SKILL.md) and its relative references; the profile is only a native entrypoint. No access to the Atlas repository or Drive is required during work.
