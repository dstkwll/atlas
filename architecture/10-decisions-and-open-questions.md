# 10 — Decisions, Rationale, and Open Questions

## Settled or strongly preferred decisions

### D-001 — Build a software factory, but start it at execution

**Decision:** Initial autonomous factory boundary begins with an approved vertical ticket and can run through draft PR creation.

**Why:** This captures the strongest SSSF leverage without asking post-hoc reviewers to compensate for poor architectural decisions.

---

### D-002 — Planning is a compiler pipeline, not one giant planning activity

**Decision:** Separate decision discovery, behavioral spec, system design, program design, and execution compilation.

**Why:** Each stage resolves a different class of uncertainty and prevents repeated redesign at increasingly detailed levels.

---

### D-003 — Program design is a first-class layer

**Decision:** Explicitly resolve file/module placement, important types, signatures, ownership, call chains, and test seams before implementation for work that warrants it.

**Why:** These decisions otherwise emerge implicitly during coding and are expensive to reverse in review.

---

### D-004 — Use Markdown files on disk as primary planning contracts

**Decision:** Specs, designs, and tickets live as filesystem-backed Markdown under the configured planning root rather than GitHub Issues as the canonical store. The default planning root is repository-relative `.planning/`; an external root is permitted where explicitly configured.

**Why:** Local files are portable, inspectable, versionable, agent-friendly, and usable without external tracker coupling.

**Refined by:** D-055 governs the location portion of this decision. The choice of filesystem-backed Markdown over an issue tracker is unchanged.

---

### D-005 — Separate workflow depth from governance profile

**Decision:** Model the amount of planning decomposition independently from how much authority the factory receives.

**Why:** Risk/assurance and task complexity are not the same dimension.

---

### D-006 — Gate authority is richer than boolean HITL

**Decision:** Support at least:

- `AUTO`
- `AGENT_REVIEW`
- `HUMAN`
- `CONDITIONAL`
- `HUMAN_IF_CHANGED`

**Why:** This allows realistic governance without proliferating workflows.

---

### D-007 — Classifier recommends; user selects/accepts initially

**Decision:** Automatic routing is advisory at first.

**Why:** The system has not yet earned authority to choose its own assurance level.

---

### D-008 — Profiles control execution policy too

**Decision:** Governance profiles can alter retries, parallelism, reviewers, checkpoints, push/PR behavior, etc., not just human gates.

**Why:** A profile represents the factory's operating posture.

---

### D-009 — Reviewer does not repair

**Decision:** Reviewer is read-only and emits structured findings; executor performs repairs.

**Why:** Separate authorities reduce self-approval and role collapse.

---

### D-010 — Preserve executor context during repairs, refresh reviewers

**Decision:** Same executor session can handle validator/reviewer repair loops; re-review should prefer fresh reviewer context.

**Why:** Implementation memory helps repairs while fresh reviewers reduce anchoring.

---

### D-011 — Add `DESIGN_BLOCKED` as a first-class state

**Decision:** Distinguish contract/design invalidation from ordinary implementation failure.

**Why:** “Try harder” is the wrong response when upstream assumptions are wrong.

---

### D-012 — PR creation belongs inside the factory; merge initially does not

**Decision:** Push and create a draft PR after final automated gates. Human remains merge authority.

**Why:** PR packaging is mechanical; final maintainability/product judgment still benefits from HITL.

---

### D-013 — Prefer `spike` over overloaded `prototype` for uncertainty-reduction experiments

**Decision:** Use **spike** to mean bounded learning experiment whose primary output is evidence.

**Why:** “Prototype” often implies a user-visible artifact or candidate product and can incorrectly imply required human review.

**Important:** A spike does not inherently require HITL. The consequential decision it informs may require HITL.

---

## Important open questions

### OQ-001 — Exact artifact schema

Need to validate through real usage:

- minimum useful fields
- frontmatter vs separate machine files
- how much duplication/reference is acceptable
- whether decision logs deserve their own file

---

### OQ-002 — Canonical machine state format

Options:

- YAML/JSON state file + human Markdown mirror
- SQLite/event log
- pure frontmatter initially

Recommendation: begin boring and file-based; add stronger machinery only after failure modes justify it.

---

### OQ-003 — Change detection for `HUMAN_IF_CHANGED`

Need a robust definition of “material change.”

Likely solution:

- stage-specific semantic dimensions
- structured agent classification with evidence
- deterministic policy mapping classification → gate

Avoid raw text-diff-only semantics.

---

### OQ-004 — Ticket sizing algorithm

Need empirical guidance for:

- context-window fit
- target changed-line scope
- dependency granularity
- tracer-slice selection

Do not overfit before trying real projects.

---

### OQ-005 — Parallel ticket execution

Likely defer initially.

Need confidence around:

- true independence
- merge conflicts
- shared state/files
- validator interference
- reviewer context

Sequential execution is safer for V1.

---

### OQ-006 — Whether final PR gate is always human

Initial answer: yes.

Long term, perhaps allow auto-merge for extremely narrow, well-characterized categories after sufficient evidence.

Do not design around that yet.

---

### OQ-007 — Model assignment policy — **STRUCTURALLY RESOLVED IN v0.3**

The architecture now separates role packages, task shapes, worker configurations, and rosters. Routing may depend on `role × task_shape`, while exact model/harness assignments remain empirical configuration rather than architecture.

Still intentionally open:

- which concrete workers should staff each role/task shape;
- evidence thresholds for recommending roster changes;
- how often roster telemetry should be reviewed.

Standing rule: telemetry may recommend; humans promote. See `17-agent-roles-rosters-and-model-policy.md` and `18-v0.3-decisions.md`.

---

### OQ-008 — Skill packaging

Likely custom skills:

- `discover` / modified grilling router
- `system-design`
- `program-design`
- `compile-tickets`
- possibly `preflight`

Existing Pocock primitives can remain available beneath these.

---

### OQ-009 — How much of pre-implementation belongs under deterministic orchestration

Current recommendation:

- same control plane may eventually orchestrate all stages;
- high-leverage design stages remain human-gated according to policy;
- autonomy can increase without changing artifact contracts.

The system should be able to automate generation while preserving separate acceptance authority.

---

## Suggested validation experiments before building a large orchestrator

Run the process manually on 5–10 meaningful changes and record:

1. Which artifact boundaries repeatedly duplicate information?
2. Where do implementers still make unexpected design decisions?
3. Which gates catch real problems vs produce ceremony?
4. How often does `DESIGN_BLOCKED` occur?
5. Which reviewer findings are useful vs noisy?
6. How many repair loops typically converge?
7. Which “human required” gates become routine rubber stamps?
8. Which classifier risk signals correlate with actual problems?
9. Are tickets genuinely vertical and independently verifiable?
10. What evidence would make the final PR review faster and safer?

Use those observations to evolve the system rather than copying a large pre-existing factory architecture wholesale.

---

## Current north-star statement

> Convert fuzzy engineering intent into progressively more constrained, durable contracts; preserve human authority at high-leverage decision points; let deterministic orchestration and bounded agents execute approved slices; and produce a draft PR backed by explicit evidence rather than model confidence alone.
