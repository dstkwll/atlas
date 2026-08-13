# 00 — Architecture Governance and Continuity Protocol

**Version introduced:** v0.4  
**Snapshot date:** 2026-08-12  
**Purpose:** Preserve architectural integrity as the project evolves across long conversations, different agents/sessions, external reference reviews, and eventually implementation in Git.

---

## 1. Canonical-source rule

The conversation is a reasoning workspace. It is **not** the canonical architecture.

The precedence order is:

```text
versioned architecture documents
        ↓
recorded decisions / learnings
        ↓
current implementation once it exists
        ↓
conversation / model recollection
```

When conversational recollection conflicts with the current canonical packet, the packet wins until intentionally amended.

A consequential architectural answer must never rely on "I think earlier we meant..." when the relevant source documents can be read.

> **Chat is the whiteboard. The versioned design packet is architectural truth. Git will eventually become the permanent artifact authority.**

---

## 2. Mandatory grounding rule for material architecture work

Before recommending a material architectural change:

1. classify the discussion as `EXPLORATION`, `CANDIDATE`, or `CHANGE`;
2. identify the architectural areas the proposal touches;
3. read the relevant current canonical documents;
4. identify affected invariants and prior decisions;
5. check the learnings/course-corrections log for previously explored or reversed variants;
6. evaluate the proposal as a **delta** against the current architecture rather than redesigning from memory;
7. recommend `ACCEPT`, `DEFER`, or `REJECT` with rationale;
8. only if accepted, update the canonical documents surgically and record the decision.

For cross-cutting changes, the rolling monolith may be used as the retrieval source, but edits should still be applied to the modular documents first.

---

## 3. Conversation states

### `EXPLORATION`

An idea is being investigated or compared. No architecture modification is implied.

Examples:

- review an external repository for ideas;
- brainstorm a possible execution mode;
- compare two model-routing approaches.

Exploration may remain conversational and need not trigger document changes.

### `CANDIDATE`

An idea appears applicable enough that it may alter the architecture.

Before recommending adoption, the canonical architecture **must be consulted**.

Candidates do not silently overwrite current decisions.

### `CHANGE`

The proposal has been intentionally accepted.

A change requires:

- surgical updates to affected canonical documents;
- a decision record;
- an entry in the learnings/course-corrections log when the change reverses, supersedes, or meaningfully reframes prior thinking;
- consistency verification before the new snapshot is called canonical.

The user does not need to label these states explicitly; the architecture process should infer and state the transition when material.

---

## 4. Core architecture invariants

These are not immutable forever, but they require explicit challenge and amendment rather than casual drift.

1. **Workflow defines capability; policy defines authority.**
2. **Pre-implementation progressively reduces degrees of freedom.**
3. **Behavioral spec, system design, program design, and executable tickets have distinct responsibilities.**
4. **Downstream execution cannot silently rewrite approved upstream decisions.**
5. **Deterministic code owns deterministic workflow mechanics and authoritative state transitions.**
6. **Agent claims are evidence/proposals, never authoritative lifecycle truth.**
7. **Reviewers remain independent from builders; review and repair are separate responsibilities.**
8. **Human authority is represented explicitly by governance policy, not by prompt convention.**
9. **Features pay for seams.** Do not implement speculative generalization before a real second use case earns it.
10. **External repositories contribute evidence and candidates, not automatic architecture changes.**
11. **V1 complexity must be justified by a current problem or a very cheap invariant.** Future paths may be documented without being implemented.
12. **Models/harnesses are replaceable workers staffing durable project roles.** Historical performance informs but does not create authority.
13. **The canonical architecture must be reconstructable without the conversation.**
14. **Chat is never the sole source of an important architectural decision.**

Any proposal that materially touches one or more of these invariants should say which ones.

---

## 5. Candidate promotion test

Before promoting a candidate into the architecture, answer:

1. **What problem in our current design does this solve?**
2. **Does that problem exist now, or are we imagining a future problem?**
3. **Can we preserve the useful principle now while deferring the mechanism?**
4. **Does the proposal simplify an existing component or add a new noun/subsystem?**
5. **Is it grounded in working implementation, operational failure history, design prose, or speculation?**
6. **If implementation-grounded, what pressure caused the feature to exist?**
7. **Does it conflict with an accepted invariant or decision?**
8. **Have we considered/rejected a similar idea before?**
9. **What is the simplest version that preserves the benefit?**
10. **Can a concrete future trigger be named for deferred complexity?**

Recency, elegance, popularity, or a polished demo are not sufficient promotion criteria.

---

## 6. External-reference maturity model

External ideas should be tracked using two separate dimensions:

### Architectural disposition

```text
REUSE      code may be a practical donor after license/fit review
ADAPT      implementation or pattern is useful but must be reshaped
CONCEPT    idea is useful; do not assume code reuse
REFERENCE  revisit when implementing the affected subsystem
REJECT     deliberately incompatible or unnecessary
```

### Maturity in our design

```text
OBSERVED
    Interesting external idea.

CANDIDATE
    Appears to solve a problem we actually have.

ACCEPTED_PRINCIPLE
    Belongs in the architecture independent of exact mechanism.

IMPLEMENTATION_REFERENCE
    Grounding material to revisit when implementing the subsystem.

DEFERRED
    Valuable only after a named trigger occurs.

ADOPTED
    Actually implemented in our system.

REJECTED
    Considered and intentionally not pursued.
```

A new repository review should not silently change either dimension for prior references.

---

## 7. Surgical-delta rule

Future architecture versions should be generated as:

```text
current canonical snapshot
        +
accepted deltas
        ↓
surgical modifications
        ↓
consistency audit
        ↓
new snapshot
```

Do **not** regenerate the architecture wholesale from conversation memory.

The modular documents are edited first. The rolling monolith is generated from those sources afterward.

A version bump is appropriate when a meaningful architectural/process decision has been accepted. Minor typo/format corrections need not create a conceptual version change unless they alter meaning.

---

## 8. Snapshot consistency audit

Every substantial snapshot should verify at least:

### Structural consistency

- all numbered canonical documents are present;
- the rolling monolith contains the canonical documents exactly and in order;
- README/version labels match the actual snapshot;
- Markdown/code fences are balanced;
- checksums/package integrity succeed.

### Semantic consistency

- principles and concrete workflow do not contradict each other;
- artifact responsibilities remain non-overlapping;
- examples/config do not encode superseded policy;
- open questions that were resolved are marked resolved or removed;
- deferred ideas are not presented as V1 requirements;
- rejected ideas are not reintroduced without explicit reconsideration;
- terminology is consistent across documents;
- current standing can be reconstructed without reading the chat;
- new decisions are reflected in all affected documents, not only the decision log.

### Complexity audit

Ask:

- Did this version add an abstraction before a second real use case exists?
- Did an external reference introduce platform complexity that our V1 does not need?
- Could a mechanism be documented as a future path instead of implemented now?
- Did a new subsystem earn its operational cost?

---

## 9. Environment migration health check

At every substantial architecture checkpoint, explicitly assess whether chat remains an appropriate primary design room.

### `CHAT_NATIVE`

Use while:

- work is predominantly architecture reasoning/comparison;
- canonical docs can be updated as manageable deltas;
- implementation details do not yet materially constrain architecture;
- a future agent can reconstruct current standing by reading the packet;
- snapshot packaging is cheap relative to the reasoning work.

### `GIT_READY`

Migration would materially improve work, but chat can still remain the reasoning interface.

Signals include:

- frequent multi-file architecture edits where real diffs would help;
- need for branches or competing architecture proposals;
- multiple agents/people need to consume or modify the packet independently;
- architecture starts naming concrete source interfaces/modules;
- version packaging becomes repetitive or error-prone;
- implementation is about to begin.

### `GIT_REQUIRED`

Continuing without a repository creates unacceptable architecture risk.

Triggers include:

- implementation code materially influences architecture decisions;
- architecture and implementation must evolve atomically;
- important decisions cannot be reconstructed from the packet alone;
- changes require reliable merge/diff/review history;
- multiple concurrent writers need conflict-safe coordination;
- artifact authority is ambiguous without repository history.

### Current status at v0.4

```text
CHAT_NATIVE — approaching GIT_READY
```

Reasoning is still architecture-heavy and reconstructable from the canonical packet. However, Git will become increasingly valuable as soon as we begin specifying implementation interfaces/source layout or repeatedly updating the architecture across many files.

---

## 10. Immediate migration trigger

If a consequential discussion reaches:

> “I think earlier we meant...”

and the answer cannot be resolved by reading the canonical packet, **stop architectural evolution** until the missing intent is reconstructed and recorded.

That is evidence that chat history has become an unsafe hidden dependency.

---

## 11. Recommended Git transition model

When migration becomes appropriate, preserve the conversational design room but move artifact authority into a repository:

```text
Chat / architecture discussion
        ↓
proposed delta
        ↓
Git branch / patch
        ↓
diff + architecture consistency review
        ↓
merge into canonical architecture
```

Suggested eventual layout:

```text
factory-design/
├── README.md
├── architecture/
│   ├── 00-architecture-governance.md
│   ├── 01-principles.md
│   └── ...
├── references/
│   └── upstreams.lock.yaml
├── CHANGELOG.md
└── implementation/   # only once implementation begins
```

The exact repository structure is a future implementation decision; the important change is that Git becomes the canonical history while chat remains the reasoning interface.

---

## 12. Instructions for future agents/sessions

When asked to continue this project:

1. do not assume conversational memory is sufficient;
2. locate/read `00-architecture-governance.md` first;
3. identify the latest canonical snapshot/version;
4. read the relevant modular docs or rolling monolith before material recommendations;
5. respect recorded `ACCEPTED`, `DEFERRED`, `REJECTED`, and course-correction history;
6. treat external repositories as candidate evidence only;
7. propose deltas rather than rewriting architecture from memory;
8. report the current migration-health status at substantial checkpoints;
9. if implementation now materially constrains architecture, recommend moving artifact authority into Git.

> **The process is successful when a future agent can forget the conversation and still reconstruct the architecture, its rationale, and the legal way to evolve it from the repository/design packet alone.**
