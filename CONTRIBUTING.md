# Contributing to atlas

atlas is a personal collection, but it's public so others can use and learn from it. These conventions keep every skill portable, consistent, and safe to drop into any agent.

## Skill structure

One directory per skill:

```
skills/<skill-name>/
├── SKILL.md              # required — the skill itself
├── references/           # optional — deep-dive docs the skill links to
├── templates/            # optional — files the skill fills in
├── scripts/              # optional — helper scripts the skill runs
└── assets/               # optional — images, data, etc.
```

`<skill-name>` is lowercase, hyphenated, and matches the `name` in frontmatter.

## SKILL.md frontmatter

```yaml
---
name: skill-name
description: "One line describing what it does. Include the trigger phrases an agent should match on."
version: 1.0.0
author: Who wrote it / what it was distilled from.
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [comma, separated, tags]
    category: creative        # or devops, research, productivity, etc.
    related_skills: [other-skill]
---
```

The `metadata.hermes` block is optional and Hermes-specific; it's ignored by other agents but helps Hermes organize and cross-link skills. The top-level fields are the portable core.

## SKILL.md body

A good skill reads like a runbook, not an essay. Include, in roughly this order:

1. **Title + one-paragraph summary** — what it does and the core idea.
2. **When to use / when NOT to use** — explicit trigger conditions and clear hand-offs to other skills. The "when NOT to use" list is what stops an agent reaching for the wrong tool.
3. **The procedure** — numbered steps with concrete detail. Exact commands where relevant.
4. **Pitfalls / anti-patterns** — a checklist of failure modes to avoid. This is often the highest-value section.
5. **Worked example** — a real input → output. Dogfood the skill on something real.
6. **Attribution** — if it's derived from upstream work, credit it and preserve the original license.

## Quality bar

- **Self-contained.** A skill should work without external context beyond what it names. Pass file paths, commands, and constraints explicitly.
- **Portable.** Prefer standard tools and clear prose over agent-specific tool calls, except where a skill is intentionally Hermes-native (note it if so).
- **Honest.** Don't invent capabilities. If a step can fail, say how and what to do about it.
- **Attributed.** Building on someone's work is encouraged — crediting it is required.

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` following the conventions above.
2. Add a row to the skills table in `README.md`.
3. Open a PR (or just commit, if it's your own atlas).

## License

By contributing you agree your contribution is licensed under the repository's [MIT license](LICENSE).
