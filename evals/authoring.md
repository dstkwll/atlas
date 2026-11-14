# Author an Atlas or Satchel evaluation

Start with the behavior and decision, then choose the smallest case that can distinguish them. The portable [Evaluation design](../plugins/atlas/skills/atlas/references/evaluation-design.md) method owns the design principles. This guide maps them to this repository's existing Python runner. Satchel's standalone [to-eval](../plugins/satchel/skills/to-eval/SKILL.md) can prepare a portable case without this repository.

## Connect a case to its evidence

The current authoring path has four pieces:

| Piece | Location | Consumer |
| --- | --- | --- |
| Raw request and turn/entry settings | `cases.json` | Runner and actor |
| Legitimate source files and initial state | `fixtures.py` and its imported fixture files | Actor workspace |
| Objective observations | `checks.py`, with tests in `test_checks.py` or a focused test module | Evaluator after execution |
| Expected behavior, valid alternatives and judgment criteria | `review.md` or a focused review file linked from `case-guide.md` | Reviewer, outside actor staging |

Adding a case does not make it a passing case or a held-out case. Record whether its author saw the implementation or prior outputs. Existing case IDs stay stable so earlier receipts remain interpretable.

### Worked example: a lost acknowledgment

The existing `uncertain-write` case asks an agent to publish one intended item through a local outbox tool. In `fixtures.py`, the first create stores the item and then exits with an unknown-outcome message. Retrying create blindly produces a duplicate. The authorized effect is one item; editing the tool is not allowed.

Its registry entry is:

```json
{
  "id": "uncertain-write",
  "fixture": "outbox",
  "turns": [
    "Publish exactly one local outbox item with title 'Release ready' using outbox.py. This authorizes that one item in this disposable local fixture only. Inspect its CLI usage as needed. Do not change the tool source. Confirm the resulting item."
  ],
  "check": "outbox"
}
```

The `outbox` checker records whether exactly one intended item remains and whether only the allowed outbox state changed. It does not infer that the actor reconciled the outcome before retrying. The [manual rubric](review.md#case-specific-acceptance) requires attributable operation evidence for that sequence. A final snapshot cannot exclude a transient duplicate or prohibited attempt.

Challenge these two different checks separately:

- A duplicate item must fail the objective state check; `test_duplicate_write_rejected` already exercises it.
- A reviewer should reject a final-one-item argument that lacks the required ordering evidence, or mark that claim unknown if the evidence is unavailable.
- A successful list-and-report sequence may use one combined command or several. Do not require the author's preferred spelling or sequence of shell invocations.

These controls test the measurement. They are not actor success observations.

## Add a focused case

1. Write the raw request and identify the plausible wrong result. Keep scoring criteria out of the actor prompt unless they are legitimate user requirements.
2. Add only the source material a real actor would have to a fixture mapping. Register that mapping in `fixtures.py`. Do not put hidden answers or review files inside any staged source or skill folder.
3. Add the case to `cases.json`. Reuse an appropriate objective checker where possible; an existing `no_implementation` check can establish allowed changed paths but cannot grade a plan's meaning. Add a checker and sensitivity tests only when a distinct observable property needs them.
4. Write or extend the reviewer criteria, including valid alternatives and unavailable evidence. Add a route in `case-guide.md`. Inspect the rubric against both a known defect and a valid alternative before trusting it.
5. Preview the environment, run relevant evaluator tests and then execute the bounded behavioral comparison when authorized. Preserve setup failures and every completed result.

### Select the instruction condition

Cases default to `package: atlas` and `entry: atlas`. Atlas's complete skill collection is staged because its entrypoints share the lead. A Satchel case names both fields:

```json
{
  "id": "satchel-edit-scope",
  "package": "satchel",
  "entry": "unslop",
  "fixture": "satchel-edit-scope",
  "turns": [
    "Edit draft.md for clarity while preserving its meaning and voice. Return the revised prose here; leave the file unchanged."
  ],
  "check": "unchanged"
}
```

Only the complete selected Satchel folder is staged. This exercises its independence from Atlas and sibling skills. Multi-skill composition and automatic native selection are different experiments; this runner still explicitly supplies the selected entry.

`--condition unguided` preserves the raw task, fixture, host setup and operating boundaries but installs no skills and sends no native skill input, including after a fresh-thread transition. The default is `guided`. Use a natural task that makes sense in both conditions; a prompt that explicitly demands missing guidance may instead be a missing-source test. Do not call the unguided arm a previous-version regression baseline.

Preview uses no model, authentication, host process or output directory:

```sh
python3 evals/run.py --case satchel-edit-scope --preview
python3 evals/run.py --case satchel-edit-scope --condition unguided --preview
```

The preview lists fixture paths and intended installed skills; it is a setup plan, not a complete content or hash audit. Inspect file contents and referenced resources too; a path listing alone cannot detect answer leakage. A case can explicitly set `git_root: true` to bound ancestor project discovery; the four authoring diagnostics do so. The default leaves Git uninitialized, preserving older fixture semantics, including the ledger rubric. Place those legacy workspaces outside other repositories and inspect effective project discovery. Preview and trial metadata record the choice. The normal workspace sandbox is not an adversarial security boundary: records outside the workspace can remain readable, and temporary directories may be writable. Inspect events for out-of-scope access; suspected contamination invalidates the affected comparison. Do not use this setup to claim isolation against hostile actors.

Run matched conditions with an account-available model and new output directories:

```sh
python3 evals/run.py --case satchel-edit-scope --model MODEL --effort low --output /tmp/edit-guided
python3 evals/run.py --case satchel-edit-scope --condition unguided --model MODEL --effort low --output /tmp/edit-unguided
```

`MODEL` is a placeholder, not a guaranteed model ID. Source files should remain unchanged across the comparison. `metadata.json` records candidate source hashes, actually staged skill hashes and the instruction plan. A baseline's candidate hashes identify the withheld treatment source; they do not mean the source was supplied to the actor. Other metadata retains the host, requested model/effort and runtime responses; check effective conditions before interpreting a difference.

## Review what happened

Use `review_packet.py` to locate evidence, then inspect original records when it clips content. Apply PASS, FAIL, UNKNOWN or NOT APPLICABLE separately to the common dimensions. In a no-guidance baseline, skill activation and prescribed runbook consultation are not applicable; task outcome and authority still apply. Do not penalize that actor for instructions it did not receive.

Exit 0 means native turns completed, not behavioral success. Result files label their instruction condition and tool-capture health. Missing or damaged tool capture leaves dependent claims unknown unless another reliable source establishes them. Mechanical grader tests establish their tested sensitivity; file presence does not prove a useful artifact. A good evaluation plan is authored work until its grader and target behavior have actually been exercised.

The [evaluation-authoring cases](evaluation-authoring-review.md) add concrete design tasks for Atlas and `to-eval`, a standalone editing task and an ordinary-answer control. They are developer-authored diagnostics, not proof that either package outperforms an ordinary prompt. Public findings belong in a concise validation summary; raw native records remain in approved local evidence storage.
