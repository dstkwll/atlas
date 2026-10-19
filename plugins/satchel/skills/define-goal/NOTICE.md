# Source and modifications

Adapted from OpenAI's public [`define-goal` skill](https://github.com/openai/skills/tree/b0401f07213a66414d84a65cb50c1d226f99485a/skills/.curated/define-goal), commit `b0401f07213a66414d84a65cb50c1d226f99485a`, in `openai/skills`. The unchanged upstream Apache License 2.0 is included in [LICENSE.txt](LICENSE.txt). The upstream `agents/openai.yaml` is unchanged.

Modified for Satchel:

- Make native goal-state checks conditional on available goal tools and the user's explicit request for goal-backed work; follow the host's tool instructions and supported operations.
- For hosts without native goal tools, return a copyable final objective, disclose that no persistent goal was created, and begin execution only when the user has also authorized that work. Existing execution authorization needs no additional confirmation.
- Apply the existing goal quality bar to the text-only objective as well as native goal creation.
- Make the draft-only path explicit on any host, distinguish defining wording from requesting native creation, and report the actual creation result without treating a missing acknowledgment as failure.
- Preserve a conflicting unfinished goal; offer separate goal-backed work only where the host supports it.
- Add a modification notice to `SKILL.md`.

The goal-definition method, examples, quantification guidance and upstream UI metadata are otherwise preserved. No external source is required to use this skill.
