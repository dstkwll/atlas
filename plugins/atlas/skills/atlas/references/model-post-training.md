# Model post-training diagnostics

Use for fine-tuning or post-training work involving supervised targets, preference optimization, reward-based updates or distributed checkpoint integrity. Falling loss, rising reward, unexplained training stalls and a proposed scale-up can trigger this method before a defect is diagnosed. Ordinary prompt edits, inference-only changes or retrieval tuning use [Model and retrieval quality](model-and-retrieval-quality.md) without requiring a training investigation.

Establish the behavioral objective, allowed data/compute, actual framework and candidate/baseline identities. Bind model, dataset, tokenizer/chat template, preprocessing, decoding and evaluator revisions tightly enough to compare meaningfully. Use existing project facilities; this guide grants no additional compute, upload, training or publication authority.

## Find the discriminating check

Classify the observed failure using actual examples and intermediate artifacts. Prefer a small test that separates explanations over another expensive run with many changed settings. Choose applicable checks, not a universal training sequence:

- **Supervised targets:** inspect rendered examples, token IDs, labels, ignored spans and truncation. Falling loss can coexist with the wrong target or prompt tokens being trained unintentionally. Verify the intended objective before correcting a mask; not every training objective masks the same spans.
- **Preference pairs:** compare chosen and rejected sequences after preprocessing and truncation. If the distinguishing response disappears, diagnose the effective training pairs before tuning optimization parameters. Retain sanitized evidence of affected counts and the transformation; private raw examples remain in their approved location.
- **Reward-based updates:** inspect sampled responses, reward parsing, verifier behavior, grouping and reward variance. Working throughput with a degenerate advantage signal proves execution, not learning. Distinguish absent response diversity from a parser or reward-definition failure before scaling.
- **Reward exploitation or drift:** compare held-out task quality with response length, reward and relevant update diagnostics. A reward increase with flat useful quality can warrant a controlled length-matched or otherwise discriminating comparison. Correlation alone does not identify the optimizer cause.
- **Mixture-of-experts divergence:** when routing is implicated, compare model/configuration identity and equivalent token sequences across the relevant paths before attributing quality changes to aggregate expert counts. Collect only the bounded routing evidence necessary to discriminate the cause.

Start with the weakest sufficient experiment for the available trusted signal. Establish what a preflight or small run must demonstrate and what stops progression. A named gate or completed job is not evidence by itself. If the evaluator is invalid, repair it and reestablish a comparable baseline rather than preserving an invalid comparison or mixing incompatible results.

## Separate saved artifacts from usable checkpoints

Derive the required inventory from the actual framework and save format: shards or consolidated weights, indexes where required, configuration, tokenizer and any optimizer/resume state needed for the intended operation. Compare expected and present artifacts, inspect save completion evidence, and validate the manifest or integrity mechanism supported by the project. Do not require one checkpoint layout universally.

Exercise a clean load in an authorized bounded environment before claiming the checkpoint usable for its intended resume or inference path. A directory, exit code or hashes alone do not prove loadability; a clean load does not prove model quality. Preserve evidence before replacing or cleaning an incomplete artifact. Do not register, resume from or publish a candidate whose required integrity remains unresolved.

For apparent stalls, use [Build/runtime diagnosis](build-and-runtime-diagnosis.md) to locate the last active phase and compare bounded process, log and resource observations. A process that exists is not proof of progress; missing telemetry is not proof it is dead. Reconcile task status before another launch or cleanup.

Return observed facts, plausible cause, the smallest discriminating next test or completed correction, preserved evidence and the progression boundary. Use held-out behavior under matched conditions for quality claims and disclose data/evaluator limits. No scalar, successful load, diagnostic outcome or runbook verdict supplies release authority.
