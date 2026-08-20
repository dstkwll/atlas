---
name: autoprompt
description: Use only when explicitly asked about Autoprompt prior art. Inspect the pinned source; do not run orchestration.
argument-hint: "[question|facet]"
disable-model-invocation: true
---

# Autoprompt — Incubator Reference

**Invocation:**

- incubator plugin: `/incubator:autoprompt [question|facet]`
- personal GitHub Copilot CLI skill: `/autoprompt [question|facet]`
- Hermes: `/skill autoprompt`, then ask the question or name the facet

> **Status: reference / needs reconciliation. This is not an Autoprompt runtime adapter.**
>
> The Atlas architecture and repository operating contract win every conflict. Report a conflict;
> never reinterpret canonical Atlas behavior to make this reference fit.

## Purpose

Keep the inspected Autoprompt implementation available as exact, source-pinned prior art while
Atlas designs its later execution and verification stages. This skill helps an agent answer
questions such as:

- Which Autoprompt mechanism is relevant to this Atlas design seam?
- Is a proposal implemented by Autoprompt, merely described there, or absent?
- Should Atlas reuse, adapt, reference, defer, or reject that mechanism?
- Which exact upstream files must be re-read before making that decision?

This reference does **not** reproduce or activate Autoprompt's 25-role orchestration system.
Read `references/source-map.md` before answering, and verify the pin in `UPSTREAM-PIN.txt`.

## When to use

Use only after the caller explicitly names Autoprompt or explicitly asks to inspect, compare,
borrow from, or revisit it. Loading this skill is not permission to:

- start an Autoprompt mission;
- resume files left by an earlier Autoprompt run;
- write `PROMPTS.txt`, `ROADMAP.md`, or `GATELOG.md`;
- dispatch an Autoprompt role hierarchy;
- install or update any provider adapter.

An ordinary implementation, architecture, planning, or review request must not trigger this skill.

## Host boundary

The upstream packages and the two user-level hosts targeted by this reference are not interchangeable:

- **VS Code package:** upstream targets VS Code 1.133+ with GitHub Copilot 0.61 custom agents.
- **Copilot CLI:** a different host. Upstream ships no Copilot CLI provider package.
- **Hermes:** upstream ships no Hermes provider package. A copied `SKILL.md` cannot provide the
  named-role registration, recursive depth, lifecycle transaction, or runtime enforcement that
  Autoprompt requires.

Copilot CLI discovered this reference through `copilot skill list`; Hermes discovered it and loaded
the card plus linked source map. That proves packaging/discovery only, not Copilot content loading,
explicit-invocation enforcement, or native Autoprompt behavior. It must fail closed if asked to claim
or simulate a native Autoprompt run. Installing this reference makes its listing discoverable on
both hosts; Hermes content loading was verified, while Copilot content loading remains untested. It
does not mean Autoprompt itself is installed.

## Procedure

### 1. Bind the source

Read `UPSTREAM-PIN.txt`. Use only the recorded commit. If a local checkout is available, verify:

```text
git -C <checkout> rev-parse HEAD
```

The result must equal the pin. Otherwise fetch or clone the exact commit into a temporary inspection
checkout. Never silently use a moving branch or an unverified copy.

### 2. Read the canonical Atlas position

At this skill's import baseline, Atlas `main` had no canonical Autoprompt donor entry. When inside
Atlas, read:

1. `architecture/15-reference-implementation-borrow-map.md` — disposition/maturity vocabulary and
   any newer explicitly accepted Autoprompt entry;
2. `architecture/16-learnings-and-course-corrections.md` — course-correction format and any newer
   source comparison;
3. the canonical architecture document governing the requested seam.

The borrow map says what is currently accepted, deferred, or rejected. If the current checkout has
no Autoprompt entry, say that the canonical borrow decision is not present there and do not infer
one from this card. This skill does not override architecture or convert a deferred idea into
implementation authority.

### 3. Read the minimum upstream evidence

Use the facet-to-file table in `references/source-map.md`. Read executable code and machine-readable
contracts where they exist; use prompt prose only for behaviors that remain prompt-defined.
Ignore promotional and benchmark claims unless the caller asks to audit them separately.

For every conclusion, distinguish:

- **code-enforced** — an executable path validates or mutates it;
- **host-enforced** — a supported host feature enforces it when correctly installed;
- **prompt-defined** — the model is instructed to do it, without universal runtime enforcement;
- **absent** — the inspected source does not implement the claimed mechanism.

### 4. Compare without importing authority

Use both Atlas dimensions as classification vocabulary:

- **Disposition:** `REUSE`, `ADAPT`, `CONCEPT`, `REFERENCE`, or `REJECT`.
- **Maturity:** `OBSERVED`, `CANDIDATE`, `ACCEPTED_PRINCIPLE`, `IMPLEMENTATION_REFERENCE`,
  `DEFERRED`, `ADOPTED`, or `REJECTED`.

If canonical architecture records the Autoprompt item, report that exact status. If it does not,
prefix the classification **`NONCANONICAL PROPOSAL`**. Never present this skill's proposal as an
accepted Atlas decision.

Name the Atlas seam and the trigger for revisiting any deferred item. Do not say "borrow later"
without naming the stage, artifact, or runtime pressure that should reopen it.

### 5. Return a bounded result

Return at most five items:

1. **Question answered** — one sentence.
2. **Source evidence** — exact upstream file paths and pin.
3. **Classification** — canonical disposition/maturity when architecture records it; otherwise
   explicitly `NONCANONICAL PROPOSAL`.
4. **Conflict or limitation** — especially prompt-defined versus executable behavior.
5. **Revisit trigger** — only when deferred.

If the request is to run or install full Autoprompt on Copilot CLI or Hermes, stop with:

```text
BLOCKED — no native adapter for this host is present. This incubator skill is reference-only.
```

Then name the smallest missing adapter capability; do not offer a pretend run.

## Explicit non-goals

- No wholesale import of the 25 personas, five-level hierarchy, 18 frameworks, or three-file ledger.
- No claim that Autoprompt routes to Atlas's earliest unresolved semantic stage.
- No uncertainty scoring attributed to Autoprompt; the inspected source has no such model.
- No replacement of Atlas `run.yaml`, `control.json`, generated `00-state.md`, or boundary authority.
- No automatic semantic approval, controller prose grading, signatures, PKI, or generic boundary engine.
- No provider installation, Bash upgrade, configuration mutation, or background supervisor.

## Verification checklist

- [ ] Invocation explicitly named Autoprompt.
- [ ] Exact commit matches `UPSTREAM-PIN.txt`.
- [ ] Relevant source files were read, not inferred from the README.
- [ ] Code-enforced, host-enforced, prompt-defined, and absent claims are separated.
- [ ] Disposition and maturity are both stated and labeled canonical or `NONCANONICAL PROPOSAL`.
- [ ] Canonical Atlas authority remains unchanged.
- [ ] No orchestration, provider installation, or governance ledger was started.
