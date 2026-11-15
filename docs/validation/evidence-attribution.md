# Evidence-attribution clarification follow-up

On November 15, 2026, four fresh unguided implementers received the two preserved PRDs from the [real-conflict replay](real-evidence-conflict.md), each with and without the same clarification. All used Codex CLI 0.153.4 / `gpt-5.6-sol` / low with a 300-second limit. Within each pair, the PRD, pre-fix sources and common request were unchanged; the clarification was the only packet difference. All four attempts completed and were retained without replacement or artifact repair before grading.

The exact clarification tested was:

> Keep the PRD's repair scope and preserve the historical evidence. In your new local verification record, connect each reported command and outcome to the versions of the project code, checks, fixtures and any helper dependencies actually used. Make that connection inspectable by another reader, using file identities, an applicable revision or another concrete method. Distinguish results you executed from expectations or old results, and state any gap in attribution. No particular report format is required.

“Guided” below identifies the historical PRD author; every new recipient was unguided. Note linkage, operator evidence of the executed version and execution honesty were assessed separately.

| Historical PRD / new packet | Note linkage | Executed-version evidence | Execution honesty | Original / supplemental probes |
| --- | --- | --- | --- | --- |
| Unguided author / original | FAIL | PASS | PASS | 12/12 + 4/4 |
| Unguided author / clarified | PASS | PASS | PASS | 12/12 + 4/4 |
| Guided author / original | FAIL | PASS | PASS | 12/12 + 4/4 |
| Guided author / clarified | FAIL: inline-check gap | PASS | PASS | 12/12 + 4/4 |

Both original-packet notes again omitted repaired checker/helper identities. Both clarified notes identified all eight relevant project Python files, but one omitted the source or a resolvable reference for its separately reported inline check. Operator capture supports that execution; it cannot supply the missing linkage in the delivered note. All four preserved original evidence, examples and received documents.

This one exposed task, with one attempt per cell, shows improved file attribution in the clarified attempts while retaining a gap. It establishes no causal, reliability, latency or package-advantage claim. No installed guidance changed.

The [original experiment tree](https://github.com/dstkwll/atlas/tree/d86de45af3e88b88e310dcff15f7dca4956331d2) preserves the task-specific adapter, addendum, rubric, tests and detailed report. Those one-off additions were retired after the experiment; replay requires that tree and the retained producer artifacts. Raw trials remain maintainer evidence. The four verification-note identities are:

| Note | SHA-256 |
| --- | --- |
| Unguided author / original | `7479aafb75daaf1d4f09dd701b7287fbda1457c26dd009e72e80d390db485ac7` |
| Unguided author / clarified | `149e5df9018fbb5f08b9cc1b5b217fa82573b8aa45a64d260c5f78158f5362f7` |
| Guided author / original | `d48e1d00be3a6f9a6c1b01a986207ba9aeaf1ab88e81e4096e06bedced168a29` |
| Guided author / clarified | `90c1d260a15cb66a8127ba698d454f86025308ed80859c6e8454a2cd7fcd9d89` |

This investigation is complete. [Issue 66](https://github.com/dstkwll/atlas/issues/66) retains the broader initiative; this result schedules no further experiment or infrastructure work.
