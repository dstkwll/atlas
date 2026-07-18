# atlas — Agent Guide

Instructions for AI agents working in this repo.

atlas is a growing collection of agentic workflows, skills, and agents — the building blocks of a personal operating system for working with AI. See [`README.md`](README.md) for the human-facing overview.

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues (`dstkwll/atlas`), via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles, each label string equal to its name. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Working conventions

- **Commit directly to `main`** — no PR flow for this repo (solo/owner workflow).
- **Design work uses the wayfinding pattern** — big efforts are charted as a `wayfinder:map` issue with decision tickets as child issues, resolved one at a time. See the `wayfinder` skill.
- Keep the repo portable: skills follow the `SKILL.md` standard so they drop into any Agent Skills-compatible harness.
