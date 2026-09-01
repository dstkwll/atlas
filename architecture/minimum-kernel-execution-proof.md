# Minimum-kernel walkthrough — execution-proof compilation

**Status:** `EXPLORATION` — non-authoritative.

**Date opened:** 2026-09-01.

**Repository baseline:** `17172644e586e6987c308ed1d8b37edbcf481330`.

This is the second case required by [`minimum-kernel-exploration.md`](minimum-kernel-exploration.md). It asks which planning facts must be machine-readable before an executor can implement and prove accepted work. It does not amend numbered architecture, authorize implementation or deletion, or settle the future ticket representation.

## Case and evidence quality

A private multi-repository planning run reached `READY_FOR_EXECUTION` only after three materially different proof packages:

1. The first ticket graph passed mechanical shape checks but named temporary validator files and verification debt that did not exist and had no declared materialization path. Fresh semantic review blocked it because execution would have required invention.
2. A revised graph replaced placeholders with self-contained commands and improved ticket boundaries, dependencies, prerequisites, and debt checks. A second fresh review still blocked it because source-text checks did not prove runtime behavior, old/candidate binary provenance was incomplete, fixture overlays were not bound, and evidence had no durable destination.
3. The accepted graph bound runtime validators, exact validator bytes, old/candidate artifact identities, disjoint fixtures, persistent evidence, positive and negative behavior markers, and unresolved device-level debt. Fresh review passed and the controller legally recorded exact graph, review, upstream, and repository-baseline bindings at `READY_FOR_EXECUTION`.

The surviving `planning-control.json`, `50-ticket-graph.json`, indexed ticket bytes, and ticket-graph review receipt independently prove the final acceptance record and recorded `READY_FOR_EXECUTION` state. Direct hash verification confirmed the accepted graph, review, indexed ticket files, and accepted source files still match every recorded binding. A fresh current-controller check could not complete because this machine has no local bindings for the frozen private repositories; their original code trees were therefore not reverified. The non-authoritative retrospective supplies the chronology of rejected candidates; those superseded exact graph bytes and review receipts do not survive. This walkthrough therefore treats the failure sequence as credible process evidence but does not claim exact reconstruction of either rejected candidate.

Later implementation evidence exposed a material false-positive in that readiness judgment. The first two accepted literal validator commands failed before reaching their behavioral assertions because of quoting, build-property, process-architecture, and runtime-API problems. Corrected commands later passed. The exact acceptance therefore proves a reviewed planning package and legal state transition, not that every accepted validator entry point was executable in its intended host.

The validators were designed and inspected during planning but were not smoke-tested as execution contracts before acceptance. The case proves that semantic review alone cannot establish literal executability. The currently unimplemented Atlas executor also has not consumed the accepted representation end to end.

## Smallest trusted outcome

The smallest trusted outcome is not a perfectly formatted ticket set. It is an accepted execution contract in which:

- each unit of work has one stable identity and exact target repository baseline;
- prerequisite edges and canonical order are unambiguous;
- every promised behavior names executable proof;
- every non-repository input has an observable availability check;
- validator assets and candidate inputs are content-addressed and materializable without invention;
- evidence has a durable destination and enough identity to bind it to the tested candidate;
- unresolved proof debt remains explicit and cannot be retired by simulation;
- every validator entry point has a bound smoke-test receipt showing that it reaches an expected behavioral assertion or control result in the intended host rather than failing in harness plumbing; and
- the exact contract, semantic judgment, upstream sources, and repository baselines are accepted together.

The current graph is one possible carrier of those facts. This case does not prove that its current Markdown-plus-JSON representation is minimal.

## Judgment ownership

- **Ticket compiler:** proposes decomposition, dependencies, commands, proof bindings, and semantic context. It cannot accept its own output.
- **Fresh independent reviewer:** judges verticality, dependency truth, validator sufficiency, no-redesign, and whether the package really avoids executor invention.
- **Configured tickets authority:** accepts the exact reviewed contract.
- **Deterministic controller:** verifies identities, closed mechanical relationships, and legal acceptance. It does not decide whether a validator proves the intended behavior.
- **Future executor:** must consume the accepted machine facts, materialize exact assets, run validators, persist evidence, and bind proof to exact candidate bytes. That consumption remains unimplemented and therefore unproven here.

## Facts that genuinely need machine structure

### Authority and provenance

- exact execution-contract identity and content hash;
- exact accepted upstream artifact bindings;
- exact target repository and baseline for each unit of work;
- exact independent review receipt and configured acceptance authority;
- current-versus-stale state after any bound source or baseline changes.

### Scheduling and admission

- stable work identity;
- target repository;
- prerequisite identities;
- deterministic order among simultaneously ready work;
- observable external-prerequisite checks where execution cannot establish the fact itself.

### Execution and proof

- literal validator command or a content-addressed validator asset plus its materialization method;
- runtime prerequisites and exact input identities;
- old/candidate artifact role, source identity, destination/fixture identity, and hashes when compatibility proof depends on them;
- durable evidence destination and the minimum output identity/schema the proof consumer must read;
- explicit binding from every promised behavior to sufficient deterministic validator/evidence, with semantic, design, or quality review only supplemental;
- a pre-acceptance validator smoke-test receipt bound to validator identity, intended host/toolchain facts, invocation, result class, and evidence output;
- unresolved verification debt and the authority allowed to retire it.

These are executor inputs or authority facts. They cannot safely exist only in explanatory prose if deterministic admission, restart, or proof binding depends on them.

## What may remain prose

Models and humans can read and judge:

- why a ticket boundary is a coherent vertical outcome;
- why a dependency is real rather than merely preferred order;
- the behavioral promise and acceptance explanation;
- why a validator is sufficient, including positive and negative reasoning;
- design context, alternatives, trade-offs, and implementation constraints;
- detailed reviewer evidence and the explanation for any block;
- the meaning of retained verification debt.

A small verdict envelope must bind judgment to exact candidate bytes. This case does not show that the explanation must be decomposed into an exact seven-row machine protocol.

## Machinery not earned by this case

The case supports structured executable truth, but not every current representation rule. It does not independently justify:

- producer-owned `status: draft`, ticket `status: ready`, and `gate_ready: true` self-attestations when authoritative readiness lives in controller state;
- exact ticket-body H2 names or an `Execution context` paragraph that mirrors frontmatter;
- requiring every selected source to be represented by exact H2 names and a duplicated purpose string rather than letting the worker or reviewer read the bound accepted document;
- treating the seven semantic-review dimensions, their order, and their evidence strings as controller protocol when the transition consumes the exact bound overall verdict;
- `kind`, `enabling`, and tracer bookkeeping for cases in which no actual scheduler or policy consumer uses those distinctions;
- embedding large compressed validator programs inside YAML commands merely because validator assets lack a smaller content-addressed carrier;
- separate Markdown ticket files plus a JSON index when a simpler accepted execution manifest could carry all executor-consumed facts without mirrored prose;
- separate `preferred_order` when canonical manifest order can express the same deterministic choice;
- duplicating source and baseline objects in graph, review, and control records when one accepted package hash can bind them once;
- universal schemas for validator-specific artifact roles, fixture overlays, or result details that only one validator consumes.

Some of these fields may still improve producer or reviewer discipline. That is not enough to make them authority or executor protocol. Each must name its real consumer before promotion into the kernel.

## First failure the smaller shape cannot handle

A compact execution manifest cannot determine whether a validator is semantically sufficient. The first rejected packages were mechanically runnable or nearly runnable but proved the wrong thing. Fresh independent judgment remains necessary.

The accepted package also demonstrated an earlier mechanical failure: a command can be present, hash-bound, and semantically plausible yet fail before it reaches the behavior under test. A smaller contract that omits execution-contract smoke testing would preserve this false `READY_FOR_EXECUTION` result.

After command viability is proven, the next failure is a cross-repository compatibility validator whose result depends on exact runtime-produced binaries filling named baseline/candidate roles in isolated fixtures. A plain ordered ticket list cannot express those inputs safely. The smallest additional mechanism is a validator-local typed input manifest bound to upstream artifact receipts—not an Atlas-wide artifact ontology.

The smaller shape also fails if it cannot express exact external inputs, content-addressed validator assets, durable evidence, and outcome-to-proof bindings. Those are not optional complexity in compatibility, migration, binary, or cross-repository work. A design that reduces the graph to task text plus shell commands would recreate the observed invention gap.

Finally, the case did not exercise restart, candidate-tree drift, or proof consumption by the future executor. Before replacing the current representation, an execution owner must demonstrate that the smaller contract can reconstruct one legal next action and reject proof from different candidate bytes after interruption.

## Case disposition

**Provisional result:** retain one small machine-readable execution contract at the final planning boundary, but restrict it to facts consumed by authority, admission, execution, restart, or proof. Keep semantic rationale in readable documents, bind one independent verdict to the exact contract, and require a pre-acceptance smoke-test receipt for every validator entry point.

This case argues for collapsing representation, not deleting executable structure. It specifically supports a content-addressed asset/input/output model, behavior-to-proof bindings, and literal validator viability while placing Markdown grammar, mirrored context, self-attested readiness, and exact review-dimension protocol on the deletion side of the ledger. It also shows that the recorded `READY_FOR_EXECUTION` state was semantically premature even though its authority record is exact.

Do not promote this result until:

1. the ordinary-planning walkthrough confirms that the execution contract collapses to one small unit when complexity is absent;
2. a concrete future executor consumption path identifies the minimum fields it actually reads;
3. exact candidate-tree and evidence bindings receive separating behavior tests; and
4. an accepted `CHANGE` states the representation retained and removed.
