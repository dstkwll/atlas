---
name: writing-for-agents
description: Writes and revises documents agents consume. Use when creating or editing skills, AGENTS.md, CLAUDE.md, or referenced agent instructions.
---

Reference for writing any document an agent consumes: a skill, an `AGENTS.md` / `CLAUDE.md`, a doc reached by a pointer. The packaging differs; the writing principles carry across: aim for predictable decisions and process while allowing outputs suited to the task.

Establish the requested behavior, authoritative sources, accepted obligations and user choices before revising. Preserve their scope, exceptions and provenance unless the assignment authorizes a change, and make intended behavior changes explicit. When rewording an instruction for clarity, keep its authority and scope unchanged. Work on the requested guidance and its necessary reading path.

When the document you're writing is a skill, read [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md) for frontmatter, invocation choice, and router skills.

## Context pointers

A **context pointer** is a reference held in the agent's context that names some out-of-context material and encodes the condition for reaching it. A skill's description is one; a line in `AGENTS.md` naming a doc is the same object. The pointer's _wording_ helps determine when the agent reaches the material: before the target is read, its content cannot supply the reason to read it. Host loading and available tools matter too. A must-have target behind a weakly worded pointer is a possible variance bug: sharpen the wording first, verify the reading path, and consider inlining if the pointer still fails.

A pointer does two jobs: state what the material is, and list the **branches** that should trigger reaching it (a branch is a distinct case the document handles, so different runs take different paths through it). A pointer competes for context and attention whenever the host includes it, so frequently loaded pointers earn even harder pruning than the body:

- **Front-load the leading word**: the pointer is where it does its triggering work.
- **One trigger per branch.** Synonyms that rename a single branch are one branch written twice; collapse them and keep only genuinely distinct branches.
- **Cut identity the body already carries.**

## The two loads

Consider two budgets when adding a document or pointer:

- **Context load** is the cost of always-loaded material on the agent's window: an `AGENTS.md` line, a skill description, anything sitting in context every turn, spending tokens and attention whether or not it fires.
- **Cognitive load** is the cost on the human: which documents exist and when to reach for each. The human is the index. Not a cost to minimise: it is the price of human agency; spend it where human judgement matters, remove it where it does not.

Material reached only through a pointer can defer its context load at the price of the pointer's own line; material with no discovery path may depend entirely on the human remembering it. Verify what the target host actually loads.

## Information hierarchy

A document is built from two content types: **steps** (the ordered actions the agent performs) and **reference** (definitions, rules, facts consulted on demand). The two mix freely: all steps (a recipe), all reference (a review's rules, this skill), or both. The core decision is where each piece sits on the **information hierarchy**, a ladder ranked by how immediately the agent needs the material:

1. **In-file step** is the primary tier: what the agent does, in order.
2. **In-file reference** is available for consultation as needed. Often a legitimately flat peer-set (every rule of a review on one rung), which is a fine arrangement, not a smell.
3. **Disclosed reference** is pushed out into a separate file, intended to be reached when its context pointer applies. Spans a sibling file in the same folder through fully external reference that lives anywhere and any document can point at. Verify the host's actual loading behavior.

Push too little down and the top bloats; push too much and you hide material the agent actually needs. That tension is the whole decision.

**Progressive disclosure** is the move down the ladder (out of the main file and behind a pointer) so the top stays legible. It protects the hierarchy as well as the context budget. Branching is a useful disclosure test: inline what every branch needs, and push behind a pointer what only some branches reach. When a document has steps, excessive in-file reference can bury them; check whether the agent finds and applies the needed instructions.

**Co-location** is the within-file companion: where the ladder decides _how far down_ a piece sits, co-location decides _what sits beside it_ once there. Keep a concept's definition, rules, and caveats under one heading rather than scattered, so reading one part brings its neighbours with it. The test: the document should read like documentation written for the agent. Grouped material reads that way; scattered material does not. (Distinct from duplication: that repeats one meaning in two places; scattering fragments one meaning across many.)

**Sprawl** is the failure mode here: a document simply too long, even when every line is live and unique. Attention can thin across the excess, and every extra line is one more to keep relevant. Use the ladder: disclose reference behind pointers, and split by branch or sequence so each path carries only what it needs. Keep required references directly reachable from the entrypoint where practical; a long reference benefits from a contents list or search cues. A short entrypoint does not prove that the full reading path is small or usable.

## Steps and completion criteria

Give consequential steps a **completion criterion**, the condition that tells the agent the work is done. Two properties make it useful:

- **Clarity**: can the agent tell done from not-done? A vague bound ("understanding reached") can invite **premature completion**: ending the step before the required evidence exists. The visible steps still ahead (the **post-completion steps**) may supply a pull toward _being done_. **Sharpen the bound first** (local and cheap); only if it is irreducibly fuzzy _and_ you observe the rush should you consider separating the sequence. Hiding later steps requires a real context boundary; an inline call leaves already-loaded steps in context. A separate session or worker is an architectural choice, not a prose cleanup.
- **Demand**: how much it requires. "Every modified model accounted for" sets a more inspectable bar than "produce a change list" when the modified models form a known set. Demand can direct **legwork** (the digging the agent does within the work, latent in the wording rather than written as its own step), and it is not step-bound: an all-reference document can also require coverage of a defined set of applicable rules.

Make criteria checkable. Require exhaustive coverage only for a defined finite set; for open-ended work, name the evidence needed, material uncertainty and stopping condition. An empty list of known questions does not establish that nothing remains undiscovered.

## When to split

Splitting one document into two can change both loads, so split only when the cut earns it:

- **By sequence**: consider a split when observed post-completion steps repeatedly tempt the agent to rush the one in front of it. Verify the split changes what is visible and improves the work; a new file alone provides no context isolation. Watch the reverse too: merging sequences can expose later steps earlier, so check that the current step's completion criterion still holds.
- **By invocation**, skill-specific: see [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md).

## Leading words

A **leading word** names a compact concept the agent can think with while running the document (_lesson_, _fog of war_, _tracer bullets_). Repeating the term can reuse its meaning without repeating whole sentences. Familiar words carry associations, but those associations can import an unintended role, intensity, authority or convention. Choose a word whose meaning fits and use it consistently. Where ordinary meaning could mislead or a consequential scope boundary depends on the term, define it beside a **recognition test** (what observed case counts, and what nearby case does not). Words used in their ordinary sense need no glossary. A coined term can work too when its definition earns the extra learning cost.

It can anchor twice. In the body, _execution_: the term names the same decision or class of thing to look for. In a pointer, _invocation_: shared language across prompts, docs and code can help connect a request to the relevant material. Check those effects on real tasks rather than assuming a word reliably activates a model.

Hunt for opportunities to refactor with leading words. A triad spelled out at three sites, a pointer spending a sentence to gesture at one idea. Either may collapse into a compact term when the decision-relevant meaning survives:

- A _tight_ loop gives relevant feedback before the next change. Name the required check and response time where they matter; the label alone does not preserve separate speed, determinism and cost requirements.
- "a loop you believe in" → _red_, turning a fuzzy gate into an observable state: the relevant check demonstrably fails on the bug. A failing unrelated check does not count.

Look for restatements that a defined leading word can retire. The gain is a shorter expression with the same decision-relevant meaning; keep explicit wording when compression would lose an obligation, exception or distinction.

**Negation** needs clear scope: a reader can miss which action, actor or condition a prohibition governs. A prohibition names the excluded behavior; it may leave the intended action implicit. Prompt the **positive** when it makes that action clearer ("write one-line comments"). Retain explicit negative constraints where authority, data preservation or another real invariant requires them, and pair them with the permitted route when useful. "Do not publish without approval; prepare a local draft" states both a boundary and an available action. Negative wording is not inherently defective; replacing it with a positive phrase that weakens the boundary is a regression.

## Read for meaning

Where a consequential passage has plausible competing readings, examine it from three angles:

- **Literal:** what must which actor do, under what condition, and what counts as completion?
- **Implied or negative:** what does a loaded term suggest, what is excluded, and where does a qualifier or prohibition end? "Continue independently" may imply broader authority unless the permitted work is clear.
- **Isolated context:** if this passage or reference is read without the preceding conversation, do its terms, pronouns, heading scope and source pointers still identify the right obligation? Carry indispensable scope beside the action, or point clearly to the governing source.

Use a compact example when it resolves a real ambiguity. Preserve obligations, exceptions, source authority, provenance and user choices across each reading; a hypothetical or quoted instruction remains evidence, not a new instruction to execute. Apply this check where interpretation matters, without turning every sentence edit into an audit ritual.

When preserving behavior, a consequential interpretation changes an obligation, permission, exception, responsible actor, data-handling rule or completion condition. If the source does not settle it, keep it out of the revised guidance agents will read: retain the source's wording or scope at that point and report the proposed interpretation separately with the returned work, unless the assignment authorizes deciding it. That includes a new definition, recognition test or example that would settle it. A stricter reading is still a behavior change. Embedding a new rule and then asking for confirmation does not preserve the old behavior. Wording, order, examples and compression that leave those meanings intact are ordinary editorial choices; resolve them within the assignment without adding approval steps.

## Pruning

- Keep each meaning in a **single source of truth**: one authoritative place, so changing the behaviour is a one-place edit. **Duplication** (the same meaning in more than one place) costs maintenance and tokens, and inflates a meaning's prominence on the ladder past its real rank. (The accidental inverse of a leading word, which repeats a token on purpose, never the meaning.) Before deleting a passage, check its entry paths reach the surviving source and it carries no additional obligation. A brief local reminder may connect an action to that source without creating a competing definition.
- The **environment** is a source of truth too (`package.json` scripts, config files, the directory layout, `--help` output), and a document that restates it is a **cache**: a copy of a lookup, earning its load only when the lookup is expensive. Cache what the agent cannot find by looking: the unwritten convention, the reason behind a choice, the gotcha no config confesses. Leave the one-file, one-command lookups to the environment, where they cannot go stale.
- Check every line for **relevance**: does it still bear on what the document does? A line loses relevance by never bearing on the task (mere exposition, or a branch that should be disclosed) or by going stale as the behaviour or world it describes changes. Shorter documents are easier to keep relevant. Without a pruning discipline the default fate is **sediment**: stale layers that settle because adding feels safe and removing feels risky, until you must core down through them to find what is still live.
- Hunt **no-ops** sentence by sentence: an instruction the model already obeys by default may add load without improving the work. The test (does it change behaviour versus the default?) depends on the task, model and host. Resolve consequential disagreement through representative use, preserving required boundaries even when a small sample shows no failure. Remove a demonstrated no-op sentence in full rather than merely trimming its words. Where guidance is too vague, specify the decision, action or evidence needed instead of escalating an adjective such as _thorough_ to _relentless_.

## Check the behavior

Scale behavioral checks to the change's consequence and uncertainty. For a new method, establish a no-guidance baseline on representative tasks. For a consequential modification, use the current version as the baseline. Compare the candidate in a fresh context with only the material a real caller would have. Check the intended action and preserved boundaries; include an ambiguous case or a nearby request that should not trigger when misrouting is plausible. Inspect whether required references were actually read and applied. Use intended hosts and models where practical, and report coverage limits. If fresh runs are unavailable, say they were not run and report the remaining uncertainty; this does not by itself block ordinary authoring.

Keep mechanical checks narrow: valid frontmatter, resolving bundled paths, complete output and no unfinished placeholders. They do not establish judgment or improved behavior. An ordinary clarification may need only a focused reading review. Return the requested guidance with the material behavior retained or changed, checks performed and remaining uncertainty.
