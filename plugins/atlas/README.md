# Atlas

Give your main agent a software goal. Atlas guides discovery, design, implementation, review and recovery as needed, with one skill and four optional runbooks. It needs no runtime dependencies, hooks, extra accounts or ECC installation.

In Copilot Agent mode, start a fresh chat and select the `atlas` skill from the `/` picker, then describe your goal. For example:

```text
/atlas Add cancellation support to queued jobs. Inspect the existing design,
make ordinary implementation decisions, and bring me material choices with
 your recommendation.
```

If your host qualifies plugin skills, select the Atlas plugin's `atlas` entry (it may appear as `/atlas:atlas`). You can also ask: **Use the Atlas skill from the atlas-successor plugin to complete [goal].** The host's main agent remains responsible; no custom agent needs selecting.

This is the lightweight successor from `dstkwll/atlas-successor`, distinct from the original `atlas@dstkwll` pipeline plugin. Enable the intended version for the project. Existing organizational/project instructions and tool permissions continue to apply.

See the repository [setup guide](https://github.com/dstkwll/atlas-successor/blob/main/SETUP.md) for installation, updates, manual skill use and migration. All operational guidance is contained in [the skill](skills/atlas/SKILL.md) and its relative references; no access to the Atlas repository or Drive is required during work.
