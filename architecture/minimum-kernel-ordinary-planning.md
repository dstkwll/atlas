# Minimum-kernel walkthrough — ordinary planning

**Status:** `EXPLORATION` — non-authoritative.

**Date opened:** 2026-09-01.

**Repository baseline:** `17172644e586e6987c308ed1d8b37edbcf481330`.

This is the third case required by [`minimum-kernel-exploration.md`](minimum-kernel-exploration.md). It tests whether a low-complexity, single-repository correction can remain small instead of inheriting the machinery needed for multi-repository design, upstream repair, or proof compilation. It does not amend numbered architecture or authorize implementation or deletion.

## Case and evidence quality

The empirical case is merged public PR [#34](https://github.com/dstkwll/atlas/pull/34). Accepted co-design Markdown could be invalidated after acceptance when its non-authoritative HTML projection was missing, stale, or damaged. The correction:

- removed five post-acceptance HTML-verification lines from the accepted-state loader;
- changed one existing test into a separating behavior witness covering missing HTML, stale metadata, and a tampered rendered body;
- preserved pre-acceptance board enforcement;
- preserved accepted Markdown identity, source binding, and authority checks;
- added no schema, state, version, repair path, or renderer mechanism; and
- was independently reviewed before human merge.

The exact public diff, branch commit, merge commit, PR body, and current tests survive. The separating witness was run against both pre-change and changed behavior, and the broader planning suite passed before merge.

This was not produced through an Atlas Stage 0–5 planning run. Inventory found no completed or substantially progressed low-complexity, single-repository, repair-free planning case: one surviving private run is large and still pending Program Design, while the other is the multi-repository contradiction and proof-compilation case used by the first two walkthroughs. PR #34 is therefore evidence of the proportional workflow Atlas should preserve, not proof that the currently implemented `trivial` planning path delivers that experience.

The repository's synthetic one-node `trivial` acceptance test passes and stops at `READY_FOR_EXECUTION`, but no acceptance record demonstrates a real user reaching that result through Gazetteer. Test coverage is not a substitute for the missing empirical run.

## Smallest trusted outcome

The trusted outcome was one precise behavior change:

> After canonical System Design Markdown is accepted, missing or damaged HTML cannot invalidate it; before acceptance, the co-design board remains mandatory and current.

Trust required the exact changed behavior, a separating witness, preservation checks at the neighboring authority boundary, independent semantic review, and human merge. It did not require a new PRD, System Design, Program Design, ticket graph, repair episode, or execution manifest.

## Judgment ownership

- **User and current architecture:** supplied the authority boundary—canonical Markdown remains authoritative and HTML is a decision aid.
- **Implementer:** located the contradicting loader check and proposed the smallest correction.
- **Deterministic tests:** proved all three post-acceptance triggers changed behavior and that pre-acceptance enforcement remained.
- **Fresh independent reviewers:** checked architecture alignment, scope, red/green separation, and preservation of source/acceptance checks.
- **Human merger:** accepted the exact repository change.

No producer self-attestation granted authority.

## Deterministic facts that were necessary

- exact repository baseline and candidate diff;
- exact files and behavior boundary changed;
- one regression that failed against the actual pre-change behavior and passed afterward for all three real triggers;
- preserved pre-acceptance enforcement;
- preserved accepted Markdown hash and source-binding validation;
- exact test results and clean public diff;
- human merge of the reviewed commit.

Those facts were supplied by Git, tests, and review evidence. A separate planning-state schema would not have made them truer.

## What remained prose

Models and humans interpreted:

- why HTML is useful before acceptance but non-authoritative afterward;
- why the behavior was a defect against existing architecture rather than a new design choice;
- why five deleted lines were sufficient;
- why no migration or compatibility mechanism was required;
- review rationale and residual limitations.

No deterministic parser needed to validate the headings, wording, comparison structure, or section order of those explanations.

## Machinery absent without loss

The case completed safely without:

- Discovery or a PRD;
- a new System Design or Program Design artifact;
- ticket compilation or a one-node ticket manifest;
- exact-H2 context selection;
- producer `status` or `gate_ready` fields;
- a seven-dimension structured planning review envelope;
- cross-repository baselines, dependency edges, external prerequisites, or evidence-output schemas;
- repair reservations, revision arithmetic, replacement context, or automatic resumption.

The absence was not a loophole. The work had one repository, one localized authority defect, one implementation unit, no external delivery condition, and a direct behavior witness.

## First failure the smaller path cannot handle

This path stops being sufficient when any of the following is true:

- the correct behavior is not already determined by accepted architecture or explicit user judgment;
- more than one independently deployable unit has real prerequisite ordering;
- multiple repositories or frozen upstream source baselines affect correctness;
- validators require undeclared assets, external inputs, durable evidence, or candidate-tree binding;
- a discovered contradiction would change accepted upstream truth; or
- completed downstream work may become stale.

Those conditions justify additional source binding, design judgment, execution structure, or stale-state handling. They do not justify imposing all such machinery before one of them exists.

## Case disposition

**Provisional result:** an ordinary single-repository correction can use:

> explicit intent + current accepted boundary + exact baseline + one implementation unit + separating behavior proof + independent review + human merge.

No separate machine-readable planning artifact is required unless an executor, scheduler, restart path, or proof consumer needs facts beyond the repository change and tests.

This case supports a proportional admission rule but leaves one important evidence gap: Atlas's implemented `trivial` path has test coverage, not a surviving real user run. Before canonical architecture changes, run one genuine low-complexity goal through Gazetteer and measure whether the system actually produces this small experience without invented approval or hidden ceremony.
