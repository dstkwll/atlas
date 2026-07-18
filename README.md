# atlas

A growing, open collection of **agentic workflows, skills, and agents** — the building blocks of a personal operating system for working with AI agents.

Everything here is portable [Agent Skills](https://agentskills.io/) (the open `SKILL.md` standard originated by Anthropic and adopted across the ecosystem). Skills are plain markdown with a little frontmatter, so they drop into [Hermes Agent](https://hermes-agent.nousresearch.com), Claude Code (`~/.claude/skills/`), and any other agent that speaks the format.

## Why "atlas"

An atlas is a collection of maps — each one self-contained, all of them part of one navigable whole. That's the intent here: a personal system that grows one useful capability at a time, where each piece stands on its own but they compound into something larger.

## What's inside

```
atlas/
├── skills/        # SKILL.md capabilities — reusable procedures an agent loads on demand
├── agents/        # agent definitions / personas (coming as the collection grows)
└── workflows/     # multi-step orchestrations that chain skills + agents (coming)
```

### Skills

| Skill | What it does |
|---|---|
| [`pixar-story-spine`](skills/pixar-story-spine/) | Turn a complex work problem, design, or decision into a Pixar-style narrative using Kenn Adams' Story Spine — with anti-slop guardrails so the audience stays the hero and the "so what" is measurable. |

*More landing over time. Agents and workflows will populate their directories as the system fills in.*

## Install a skill

Each skill is a self-contained directory. To use one, copy it into your agent's skills folder:

**Hermes Agent**
```bash
git clone https://github.com/dstkwll/atlas.git
cp -r atlas/skills/pixar-story-spine ~/.hermes/skills/creative/
```

**Claude Code**
```bash
cp -r atlas/skills/pixar-story-spine ~/.claude/skills/
```

Your agent auto-discovers the skill on its next session and loads it when a prompt matches the skill's trigger description.

## Structure & conventions

Every skill follows the same shape so the collection stays consistent and portable — see [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full convention. In short:

- One directory per skill under `skills/<skill-name>/`, containing a `SKILL.md`.
- YAML frontmatter with `name`, `description` (with trigger phrases), `version`, `author`, `license`, `platforms`.
- Body: when to use / when NOT to use, a numbered procedure, an anti-pattern or pitfalls section, and a worked example.
- Attribution preserved for anything derived from upstream work.

## License

[MIT](LICENSE). Individual skills preserve upstream attribution in their own `SKILL.md` where they build on prior work.
