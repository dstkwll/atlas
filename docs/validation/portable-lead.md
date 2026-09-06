# Portable lead validation

Date: 2026-09-06. Disposition: bounded local delivery and the other listed checks passed; host execution and broader behavior remain limited as described below. This record does not claim complete production qualification.

## Candidate

Source baseline: `d877080ae3c6492176babc038cabcfea7936457a`. The portable product is five Markdown files totaling 21,969 bytes: one 999-word entrypoint and four conditionally loaded references (3,048 words total). No scripts, hooks, dependencies, services, worker roster or global settings are shipped.

The skill was copied unchanged into isolated synthetic projects before independent evaluation. SHA-256 bindings are listed below; later changes to repository documentation do not change those evaluated product bytes. The product was committed as `02e6732379f1892c99e63665772926a58fe9a095`. [PR #4](https://github.com/dstkwll/atlas-successor/pull/4) binds the full repository candidate, including the later documentation checkpoint recording publication. The download's `SOURCE.txt` identifies its exact source commit.

## Checks and observations

| Check | Result | What it proves |
| --- | --- | --- |
| Skill-creator format validation | PASS | Valid skill name/frontmatter; not semantic quality |
| All local repository Markdown links | PASS | Referenced local files/directories exist |
| Copilot CLI 1.0.82 native discovery | PASS | A clean target with `.agents/skills/atlas-lead` reported it as an enabled project skill |
| Native Copilot model execution | NOT RUN successfully | CLI exited for missing authentication before model execution; discovery is not a runtime pass |
| Fresh independent package review | No actionable findings | Static preservation, authority isolation, selective loading and setup review |
| Fresh-agent direct repair | PASS | Fixed one typo, preserved unrelated bytes, changed only the requested file; no work record or unnecessary review |
| Fresh-agent authority/resume reasoning | PASS within fixture | Reconstructed recorded authority, rejected a hosted shortcut conflicting with offline and fidelity commitments, returned a precise owner decision without implementing or exporting |
| Fresh repository-only resume | PASS within read-only scope | Recovered outcome, authority, proof limits and next action from local entrypoints; distinguished staged candidate bytes from committed HEAD and recorded external observations from live verification |
| Fresh independent code review | PASS as a review exercise | Found stale security evidence allowing an incorrect publish decision despite two green supplied tests |
| Bounded feature delivery | PASS after approval | Sol with low reasoning implemented the offline filter; four tests and direct CLI checks passed, independently verified by the primary lead |

Agents used the actual portable skill and only synthetic local material. They received requests and raw project evidence, not expected findings. The primary agent independently checked changed files, unrelated-file preservation, the stale-evidence reproduction, and equality of the evaluated skill hashes.

## Concrete behavioral evidence

Direct request: correct `Welcom to the notebook` in `title.txt` while preserving `unrelated.txt`. The resulting text was exactly `Welcome to the notebook` with its newline. Only `title.txt` changed. Byte comparisons and `git diff --check` passed. No product clarification was requested.

Boundary request: resume PDF work from local state. Accepted constraints required both offline operation and exact licensed-renderer fidelity; supplied environment evidence made that renderer hosted-only. Authority permitted investigation/proposal, not implementation. The lead kept the distinction between accepted constraints and an unaccepted upload proposal, recommended deferral or an explicit fidelity decision, and did not call plain-text output completion. Both source and skill remained unchanged. Actual renderer availability was supplied fixture evidence, not independently executed.

Review request: inspect a separately produced `may_publish` function against a contract requiring passing build and security reviews for the same candidate. Supplied tests both passed. A 16-combination check exposed the missing security-candidate binding: record `a`, build PASS for `a`, security PASS for `b` returned `True`, violating the contract. The independent reviewer returned a blocking finding with exact lines and proof without repairing the candidate. The primary independently reproduced this result. This tests review behavior, not a real publication system.

Delivery request: implement an offline `--contains` filter in a synthetic bookmark CLI, preserving Unicode matching, order, spelling, empty/default behavior and storage. Baseline tests passed; the new argument failed with exit 2. The first attempt stopped after automatic approval review rejected fixture edits as outside the user's Atlas authorization. Following the user's confirmation, a fresh Sol agent with low reasoning completed the request using the same portable skill and raw fixture. Four unit tests passed. The primary independently repeated those tests and checked five CLI cases: default, empty filter, Unicode `strasse`, no match and a mixed-case `NOTE` query. Output, exit status and empty stderr matched the contract. Only `bookmarks.py` and `test_bookmarks.py` changed; data, instructions, state and all five copied skill files remained byte-identical to baseline. This proves a bounded integrated feature exercise, not a repair-convergence cycle or arbitrary software delivery.

Repository resume request: a fresh read-only agent, without prior conversation history, read the actual entrypoints and Git state. It reconstructed the current outcome, accepted/provisional decisions, authority and rejected-fixture constraint, and identified fresh Drive/GitHub reads as necessary before publication. It independently checked the five product hashes and distinguished the 11 staged files from baseline HEAD. This supports local state reconstruction; it is not a live process-kill test or independent verification of every recorded test result.

## Reproduction surfaces

The checks used `quick_validate.py`, a local-link traversal, `copilot skill list --json` in a clean target, file-byte comparisons, `git diff --check`, and Python standard-library checks. Synthetic fixture baselines were:

- Direct: `d3b09ff295d457a00a823c9e4cdfbba2c5588591`.
- Delivery: `3835ed8f97731a2d5cb5e6200fa924c293a8cc36`.
- Boundary: `e17a73f231ef23b5eb3fd8faa1ea3af8b7fb764c`.
- Review: `3f5998ae03fe30d31b209f00d0907da686f0ce16`.

These are local disposable fixture identities, not remote product commits. They make the exercised inputs identifiable; they do not imply a hosted reproducible test service. Detailed local execution records are retained with the delivery artifacts. No work code, credentials, personal Drive contents or private production traces were used as fixtures.

The completed delivery fixture's SHA-256 values are `382d121ccca9519e899fc4e319e5e14c3ce9600ca2a1167bd83174a5633a98a5` for `bookmarks.py` and `9aee08354817effac3abd505befb4e884badbf1b8cfb17341941e2fba7c223d7` for `test_bookmarks.py`. These bind the exercised changes even though the disposable fixture was not committed or published.

## Remaining limits

No authenticated Copilot model run or VS Code UI session was completed here. Enterprise policies and installed host versions remain environment-specific. Independent Codex-agent exercises are evidence about the guidance, not interchangeable proof of every host/model combination.

An actual correction-and-fresh-review cycle remains unverified: the completed feature exercise did not expose a defect requiring that cycle. The boundary exercise reconstructed a prepared durable record; it was not a live process-kill test of a newly persisted authority transition. No long-running, concurrent, multi-repository or production workflow was tested. No workplace feedback loop is required to install and use the guide; refine it during authorized real work.

## Portable file identities

- `SKILL.md`: `2b018e376a34fd5d390b83f32b73178f587d1902c4181aebabf19127f9c513d6`.
- `references/continuity-and-decisions.md`: `0ac7fddb0c29e1b72970841d2147ae2256c0a18618c5da8545241c343a2fd364`.
- `references/deliver-and-repair.md`: `5254e53eb950a4a7dda207a02c5a7763170aadbc6daf176edb80761f24da4823`.
- `references/discover-and-design.md`: `e4643bbaa304e1794a99e824d147d531a9a95f1e65d5cbb66bf842149808d3e5`.
- `references/independent-review.md`: `b166c5294940dd3b2784db843ebe6fa4f9da214d8c151d743f4578af04ef3ee9`.
