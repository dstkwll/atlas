# Check an evaluation artifact through a fresh consumer

Use `artifact-consumer-original` and `artifact-consumer-clarified` to test whether a plan's evidence rules survive implementation. The fixtures minimize an inconsistency observed in an actual `atlas-to-eval` outbox plan: its main rubric treated malformed required JSON as failure, but its later control treated malformed and unavailable evidence alike as unknown/setup error. The partially clarified condition separates complete bad output, failed capture and independently verified absence. It remains an experimental artifact: its undefined item-shape wording and blanket treatment of unavailable capture are retained for diagnosis, not endorsed as a finished grader specification.

Both conditions give the consumer the same task and small local adapter interface: implement `classify(raw, capture_status)` in `planning/checker.py`, returning a verdict and reason. `capture_status` describes independent observations, not a claim from the actor. The brief asks the consumer to report unresolved rules instead of silently inventing a policy. The adapter is disposable test plumbing, not a new product interface. The original artifact is not edited in place.

## Freeze and separate the two sources of truth

The consumer implements its supplied plan. The evaluator separately derives expected outcomes from the authoritative task: deliver a valid JSON array containing exactly one requested item and no extra effects. `artifact-consumer-controls.json` preserves seven diagnostic vectors selected before the consumers ran. Neither this guide nor those vectors is staged into the actor's project. The fixture contains only `BRIEF.md` and `plan.md`; the standard runner adds project-local operating constraints and any explicitly selected skills.

Keep the original generated plan, the minimized excerpts, condition mapping, task-derived expectations and every attempted consumer. Label the excerpt transformation: both share an explicit required output shape and interface; the original retains the two conflicting rules, while the clarified excerpt replaces them and adds an item-shape checklist and explicit provenance rules. Those extra differences are potential confounds; do not attribute every result to removal of the contradiction alone. These exposed diagnostic cases do not estimate general performance or isolate every possible consumer variation.

## Run and inspect the real consumer

Run both cases through the [native runner](README.md), holding model, effort, context, host and permissions constant. An unguided run measures this artifact transfer without installed Atlas or Satchel guidance. Check actual inputs, reads and changes; source accessibility or a skill name does not prove use.

Read the produced code before executing it. In a disposable local environment, import the exact generated `planning/checker.py`, call `classify` on each preserved vector and retain the unmodified return or exception. Do not repair generated code, normalize an unexpected verdict into success, or replace the consumer with your own implementation. If code is absent, incompatible or unsafe to execute under existing authority, retain that limitation and the actual explanation. Consumer-authored smoke tests are separate evidence.

Inspect three questions separately:

- Did the consumer faithfully implement the supplied plan and expose unresolved contradictions?
- Does the resulting checker agree with the independently derived task requirements, including valid alternatives?
- Does the supplied plan itself preserve those requirements and make evidence provenance usable?

An `UNKNOWN` caused by an acknowledged specification conflict can be faithful consumption while still failing to establish the task's correct judgment. Likewise, passing tests written from a faulty plan may only demonstrate fidelity to that fault. Trace a discrepancy to the responsible layer before changing agent guidance.

The vectors cover complete malformed JSON, the same prefix after lost capture, a valid exact state, a wrong root shape, independently verified absence, an unauthorized extra item and a valid serialization alternative. Judge only the declared final-artifact boundary. This adapter does not establish report truthfulness, retry ordering, real collector reliability or live outbox behavior. Broader claims need independent task families and corresponding observations.

The [observed outcomes](../docs/validation/artifact-evidence-boundaries.md) include both the resolved malformed-file distinction and the new valid-input ambiguity; registration is not a passing result.
