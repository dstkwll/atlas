# Minimum-kernel walkthrough — upstream contradiction

**Status:** `EXPLORATION` — non-authoritative.

**Date opened:** 2026-09-01.

**Repository baseline:** `17172644e586e6987c308ed1d8b37edbcf481330`.

This is the first case required by [`minimum-kernel-exploration.md`](minimum-kernel-exploration.md). It tests the smallest safe response when an accepted System Design conflicts with exact frozen production code. It does not amend numbered architecture, revoke D-082, authorize implementation or deletion, or make this proposed path canonical.

## Case and evidence quality

A private multi-repository planning effort accepted a System Design that located one validation behavior at the wrong production stage. During Program Design, inspection of exact frozen repository commits showed the contradiction. The producer did not silently design around it: Program Design returned `DESIGN_BLOCKED`, named the accepted commitment that code could not realize, and downstream work stopped.

The installed workflow could not replace that accepted System Design in place. A corrected successor run was created instead. Surviving exact artifacts from that successor independently show current human-approved System Design and Program Design plus an agent-approved ticket graph at `READY_FOR_EXECUTION`, with exact candidate hashes, source bindings, and applicable repository baselines.

The superseded original run was later intentionally removed. Its accepted candidate, control state, and upstream-block receipt are therefore unavailable for current independent inspection. The non-authoritative retrospective records the original acceptance and `DESIGN_BLOCKED` result, but prose is not a receipt. This walkthrough treats the contradiction sequence as credible but not fully reconstructible. It must not be used to claim that every original transition field or review-envelope detail was verified.

## What the surviving evidence supports

The useful outcome required five properties:

1. the accepted design remained identifiable rather than being rewritten in place;
2. Program Design inspected exact frozen code instead of a nearby checkout or conversational memory;
3. the producer could report a contradiction but could not invalidate its own upstream authority;
4. downstream work stopped visibly rather than improvising a new System Design;
5. a corrected design received fresh judgment and acceptance before planning resumed.

The case does **not** prove that Atlas needed an automatic repair episode, four controller-reserved producer attempts, replacement-review context copies, or automatic Program Design resumption. The observed recovery used a successor run.

## Minimum safe path

```text
accepted System Design + exact frozen code baseline
                    |
                    v
      producer reports a cited contradiction
                    |
                    v
   fresh independent contradiction judgment
                    |
                    v
 deterministic transition: System Design STALE / run BLOCKED
 old acceptance remains immutable non-current provenance
                    |
                    v
 user chooses corrected version or successor run
                    |
                    v
 fresh semantic review + configured acceptance authority
                    |
                    v
 dependents consume only the new accepted binding
```

For the observed case, the smallest trusted outcome is not an autonomously repaired design. It is a durable stop whose bound receipt proves that the old accepted design and exact code cannot both be honored, followed by one user-authorized forward correction and fresh acceptance.

## Judgment ownership

- **Producer:** identifies the mismatch and supplies cited evidence. It cannot change accepted truth.
- **Fresh independent reviewer:** judges whether the exact accepted commitment and exact frozen code really conflict.
- **User:** decides the substantive correction or chooses a successor run when the accepted design must change.
- **Configured System Design authority:** accepts the exact corrected candidate after fresh review.
- **Deterministic controller:** checks identities and records only legal state transitions. It does not judge prose or design quality.

## Deterministic facts that remain necessary

A smaller mechanism still has to check:

- exact current System Design acceptance identity, version, hash, authority, and source binding;
- exact full repository commit identities and readable cited code bytes;
- one contradiction receipt bound to both the accepted design and frozen code evidence;
- an atomic transition that makes the old acceptance non-consumable without erasing it;
- exact identity and source binding of the corrected candidate or successor run;
- fresh review and configured acceptance of that exact candidate;
- direct dependent artifacts are absent, pending, or explicitly stale before they may be consumed.

These checks protect authority. They are not document-format validation.

## What may remain prose

Models and humans can judge and rewrite:

- why the code evidence contradicts the accepted commitment;
- the smallest design correction;
- alternatives and trade-offs;
- whether the correction changes product intent or only system realization;
- whether a successor run is clearer than an in-place new version;
- the revised System Design itself.

Deterministic code needs the identities and legal transition, not a grammar for those explanations.

## Machinery not earned by this case

D-082 is the current accepted solution and remains authoritative. On this exact repository baseline, a conservative AST inventory finds at least ten explicitly named repair/upstream-block functions spanning 505 function lines in `atlas_planning.py`, plus twenty named repair helpers/tests spanning 818 function lines in `test_atlas_planning.py`. This lower bound excludes schema constants, call-site branches, and indirectly named coverage.

The observed case does not independently justify:

- an exact four-attempt producer budget;
- durable reservation before every producer write;
- a multi-state repair episode carried in `blocked_reason`;
- preservation of the initial unaccepted Program Design candidate hash;
- copying the full predecessor acceptance and contradiction into replacement-review context;
- repeated JSON-type-exact equality across each copy and reload;
- automatic return to and resumption of Program Design.

One canonical contradiction receipt, one stale predecessor reference, one atomic block, and one fresh forward acceptance appear sufficient for this case. That is a deletion hypothesis, not permission to remove D-082 yet.

Closed PR [#31](https://github.com/dstkwll/atlas/pull/31) reinforces the cost warning but does not settle the design. A separate projection-format problem expanded into 20 changed files, 759 additions, 208 deletions, intentional-revision discrimination, revision arithmetic, and broad workflow changes before being rejected unmerged. Its evidence argues against extending specialized repair machinery by default; it does not prove which current D-082 pieces can be deleted safely.

## First failure the smaller path cannot handle

The smaller path is insufficient when the contradiction is discovered after accepted Program Design, accepted tickets, or execution work already exists. Then Atlas must determine which downstream acceptances and completed work are invalid, preserve unaffected proof, and prevent a partially stale graph from executing. This case did not exercise that problem.

It also does not provide bounded autonomous retry. If repeated producer attempts without further user judgment are a product requirement, a durable budget may be needed—but that requirement must be demonstrated rather than inherited from D-082.

## Case disposition

**Provisional result:** for a contradiction discovered before Program Design acceptance, prefer:

> producer `DESIGN_BLOCKED` evidence + one independently confirmed contradiction receipt + atomic `BLOCKED`/`STALE` state + immutable stale provenance + user-authorized forward correction + fresh acceptance.

Do not promote this result until:

1. the execution-proof compilation walkthrough identifies any shared provenance needs;
2. the ordinary-planning walkthrough proves the mechanism disappears when no contradiction exists;
3. an accepted `CHANGE` names the exact D-082 behavior retained and removed;
4. separating tests fail against each unsafe deletion and pass with the smaller mechanism.

The missing original receipt remains a material evidence limitation. Current D-082 behavior stays authoritative until those conditions are met.
