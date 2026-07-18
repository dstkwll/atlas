---
name: pixar-story-spine
description: "Turn a complex work problem, design, or decision into a Pixar-style narrative using the Story Spine. Triggers on 'pixar story', 'story spine', 'tell the story of', 'narrate this work', 'pitch this as a story'."
version: 1.0.0
author: Distilled from Kenn Adams' Story Spine + Pixar's 22 Rules (Emma Coats); Saga narrative-design contract (simota/agent-skills, MIT). Ported by Hermes Agent.
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [storytelling, narrative, pitch, communication, writing, presentation, pixar, story-spine]
    category: creative
    related_skills: [humanizer, plan]
---

# Pixar Story Spine: narrate complex work as a story

Take a tangled piece of work — a debugging saga, an architecture decision, a migration, a research finding, a design proposal — and retell it as a story people actually remember and act on. Facts get remembered ~10% of the time; the same facts inside a story land at ~65%. This skill gives you the skeleton (the Story Spine) plus the craft rules to make the retelling land without turning it into fluff.

**Core move:** the audience (user, customer, teammate, stakeholder) is the hero. Your work/product/fix is the *guide* that helps the hero win. A narrative that makes the work the hero leaves the audience cold.

## When to use this skill

Load this skill when the user wants to:
- Turn a complex problem, design, incident, or decision into a story or narrative
- Pitch work to stakeholders, execs, or investors in a memorable way
- Write a launch narrative, demo script, retro story, or "why this matters" framing
- Explain a technical outcome to a non-technical audience
- Reframe dry release notes / a PRD section / a status update as something with an arc
- Anything triggered by "pixar story", "story spine", "tell the story of X", "narrate this", "pitch this as a story"

Do **not** reach for this when the user wants:
- Plain technical documentation, an API reference, or a precise runbook → keep it literal
- To strip AI-isms from existing prose → `humanizer`
- To actually plan/execute the work → `plan`
- Fictional screenwriting for its own sake → this is work-narrative, not a screenplay engine

## The Story Spine (the 8-beat skeleton)

Kenn Adams' Story Spine, adopted into Pixar's writing culture. Fill each beat:

1. **Once upon a time…** — the stable status quo. Who the hero is and their normal world.
2. **Every day…** — what reinforced that status quo; the routine, the accepted constraints.
3. **Until one day…** — the inciting incident. The thing that broke, changed, or got noticed.
4. **Because of that…** — the first consequence / action taken.
5. **Because of that…** — the follow-on consequence. (Repeat this beat as needed — this is the rising action, the messy middle where stakes escalate.)
6. **Until finally…** — the climax. The turning point where it resolves.
7. **And ever since then…** — the new status quo. What's different now, ideally measurable.
8. **The moral / because…** — the point. Why it mattered, what the audience should take away or do.

Beats 4-5 are where honesty lives: real work has false starts and escalating stakes. Don't flatten the middle into "and then we fixed it."

## Non-negotiable contracts (what makes it good, not slop)

Apply every one of these before you deliver:

- **Hero = the audience, guide = the work.** Never let the tool/team be the hero. Ask "who wins at the end, and is it the person I'm telling this to?"
- **One core problem.** A story chases a single central tension. Multiple problems dilute the point and kill the call to action. Split into separate stories if needed.
- **Connect three problem levels:**
  - *External* — the tangible, technical obstacle (the 400 error, the slow query).
  - *Internal* — the emotional frustration it caused (the dread, the lost trust, the 3am page).
  - *Philosophical* — why it matters universally (reliability is respect for the user's time).
  A story that only names the external problem stays forgettable.
- **Measurable Before→After.** The "ever since then" beat needs an observable change — a number, a behavior, a removed pain. "Metric-free success" is an anti-pattern.
- **Real tension.** Resolution without struggle doesn't engage. Keep the stakes and the near-misses in.
- **Concrete scenes over abstractions.** "Every council call died with a red 400" beats "reliability was suboptimal." Use sensory, specific detail.
- **Name your framework fit.** Story Spine is the default. If a different frame fits better, say which and why:
  - *Before-After-Bridge (ABT)* — quick pitches: here's the world, here's the better world, here's the bridge.
  - *Hero's Journey* — long transformation arcs with a real ordeal.
  - *And-But-Therefore (ABT, South Park causality)* — tight cause-and-effect for a punchy 3-sentence version.
- **State assumptions.** If you invented or inferred any fact to make the story flow, list it in an "Assumptions" section. Bending facts to fit the arc is the cardinal sin (narrative bias).
- **Target the audience.** Tune depth and language:
  - *Eng team* → hypothesis-driven, keep the technical texture.
  - *Execs / stakeholders* → transformation arc + the number, low jargon.
  - *End users* → empathetic, relatable, zero jargon.
  - *Investors* → the Promised Land: the future this makes possible.

## Anti-pattern checklist (fail any → revise before delivering)

- AP-1 Work is the hero, audience is a bystander.
- AP-2 More than one central problem.
- AP-3 Only the external problem named; no internal/philosophical stakes.
- AP-4 No measurable or observable change at the end.
- AP-5 Resolution with no struggle (flat middle).
- AP-6 Abstract feature-speak instead of concrete scenes.
- AP-7 Facts distorted to fit the arc, with no Assumptions note.
- AP-8 Length/register wrong for the audience (a 2000-word saga for a Slack update).
- AP-9 A tidy inspirational kicker that says nothing ("the future is bright").

## Length targets

- Elevator / ABT version: 200-500 chars (3 sentences).
- Use-case / incident story: 300-800 chars.
- Full narrative with arc: 500-1500 chars.
- Stakeholder pitch: keep it under a minute spoken.

Always offer the short version first; expand only if asked or if the audience warrants it.

## Process

1. **Extract the raw material.** Read the work artifact (use `read_file` for a file, or take it inline). Identify: who the hero is, the single core problem, what actually happened in sequence, and the outcome.
2. **Name the three problem levels** (external / internal / philosophical) in one line each before drafting. If you can't name the internal stake, dig — that's usually where the story is.
3. **Fill the 8 Story Spine beats.** Let beats 4-5 breathe; keep the real escalation.
4. **Draft the story** at the length the audience needs. Concrete scenes, audience as hero.
5. **Run the AP-1…AP-9 checklist.** Fix every failure.
6. **Add an Assumptions section** if you inferred anything.
7. **Offer variants:** the 3-sentence ABT version and (if useful) an audience-retuned cut.
8. Optionally run the result through the `humanizer` skill to strip any AI tells before final delivery.

## Output format

Deliver in this order:
1. **The story** (default length; hero = audience).
2. **Story Spine beats** (the 8-beat breakdown, so the user sees the scaffold and can remix).
3. **Framework used + why** (one line).
4. **Assumptions** (only if any).
5. **Short version** (3-sentence ABT) — always include; it's the most reusable.

## Worked example (input → output)

**Input (raw work):** "We fixed a bug where GPT-5.x models on the Copilot provider returned HTTP 400 whenever passed as a `-m` override, because the resolver read the api_mode from the stale config default instead of the model you actually asked for."

**The story (eng-team register):**
> Every model on the seat had a home. Claude spoke Chat Completions; the new GPT-5.x models spoke only Responses. Day to day nobody noticed — the default model was Claude, and Claude's door was the one the resolver always knocked on.
>
> Until one day you asked for gpt-5.6-sol directly. The door opened onto a wall: `HTTP 400 — not accessible via /chat/completions`. Every council call died the same red death, while gpt-5.4 sailed through and made it look like a fluke.
>
> Because of that, we followed the 400 past the loud culprit — a config pin — and found the quiet one underneath: the resolver computed the endpoint from the *default* model, never from the model you actually passed. gpt-5.4 only worked by luck, caught by a downstream allow-list the newer models missed.
>
> Because of that, we threaded the real target model through the resolver so the endpoint is chosen for the model in your hand, not the one in your config.
>
> Until finally every GPT-5.x — sol, luna, terra, 5.5, 5.4, mini, codex — answered on the first try, with five regression tests pinning the invariant so it can't silently rot.
>
> And ever since then, the council runs on any model you name, and the fix is documented so an update can't quietly undo it.

**Story Spine beats:**
1. Once upon a time — a Copilot seat served many models, each on its own API surface.
2. Every day — the Claude default hid the mismatch; the resolver always asked the default's endpoint.
3. Until one day — an explicit `-m gpt-5.6-sol` hit a hard 400 on every call.
4. Because of that — we traced past the obvious config pin to the resolver logic.
5. Because of that — found it derived the endpoint from the stale default, not the requested model (5.4 passed only by luck).
6. Until finally — threaded the target model through; all GPT-5.x pass, guarded by tests.
7. And ever since then — council works on any named model, durably documented.
8. Moral — a fix that only handles the models on your hardcoded list isn't fixed; route by what's actually asked for.

**Framework used:** Story Spine — the work had a clear inciting incident and escalating investigation, which the 8 beats carry naturally.

**Assumptions:** none; drawn directly from the work log.

**Short version (ABT):** GPT-5.x models on Copilot worked as the default *but* died with a 400 the moment you named one explicitly, *therefore* we routed the endpoint by the requested model instead of the stale default — and now every model answers on the first call, test-locked.

## Attribution

Built on Kenn Adams' **Story Spine** (1991), popularized through Pixar's writing culture, and Emma Coats' **Pixar 22 Rules of Storytelling**. The customer-as-hero / guide framing, three-problem-levels contract, and the AP-1…AP-9 anti-pattern discipline are distilled from the **Saga** narrative-design agent in [simota/agent-skills](https://github.com/simota/agent-skills) (MIT), which itself synthesizes StoryBrand SB7, JTBD, Hero's Journey, and Promised Land. Adapted here into a single self-contained Hermes skill focused on narrating real work rather than fiction.
