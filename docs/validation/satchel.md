# Satchel validation

This report separates source review, package discovery and behavioral evidence for the independently installable Satchel skills. [Adaptations](../satchel/adaptations.md) identifies sources and deliberate changes; [issue #50](https://github.com/dstkwll/atlas/issues/50) owns delivery. The observations below are bounded evidence, not a claim of improved reliability over the base model.

Satchel was developed and evaluated under the provisional name **Toolbox** through commit `8e4bea37fd6d5a7eb97c9b4954601ece674da0d8`. The historical observations below retain that name, its commands and its recorded source identities. Renaming the package changes its installation identifier and documentation pointers; the five skill bodies, conditional mechanics reference, case definitions and bundled license text are unchanged.

## Source review and structural checks

Copilot Claude Opus 5.5 at xhigh completed the candidate-design review. It supported the five-skill collection, identified semantic risks in `re-pitch`, pruning and automatic discovery, and required full donor inspection before finalizing questionnaire and teaching adaptations. The maintainer read the pinned sources and checked recommendations against them.

A first combined implementation review used the actual candidate files and pinned donor sources, but reached its 300-second deadline without a completed result. Partial observations were retained and checked as provisional findings, not counted as a completed review. Narrower completed reviews used the same model and effort. They found inconsistent shared-reference packaging guidance, overbroad loading and word-compression claims, a baseline that fit only new methods, and missing source-account details. Verified findings were repaired. Five completed source reviews and a completed concept review used the requested model and effort. The last writing review prescribed two final clarifications (the instruction pronoun and the definition/example scope); the exact two-change diff was checked after applying them. No review agreement is treated as a behavioral guarantee.

All five final skills pass the available skill-creator frontmatter/scaffold check. Each required relative reference stays within its skill folder and resolves. Each adapted skill includes byte-identical Matt Pocock MIT license text. These checks establish structural properties, not instruction adherence. The repository's 39 existing evaluator tests pass; those tests exercise the Atlas evaluator, not Toolbox behavior.

## Native packaging and discovery

On October 18, 2026, isolated offline Copilot CLI **1.0.91** checks exercised the actual package, not just a fixture:

- A local marketplace with metadata version `0.11.0`, Atlas `0.11.0` and Toolbox `0.1.0` registered successfully.
- Installing `toolbox@atlas` exposed exactly its five skills and left Atlas disabled.
- Installing Atlas alongside Toolbox exposed five Toolbox and eight Atlas skills.
- Copying each complete Toolbox skill folder into an otherwise empty project's skill directory exposed exactly that one skill.
- Thirteen native commands completed successfully, with empty stderr and unchanged candidate bytes during the run.

The check used separate temporary configuration/cache and no inference or user-install changes. It invoked the cached 1.0.91 runtime directly with `node <runtime>/index.js --no-auto-update`; the recorded version check used that same launch path. Reproduction must verify the executable version.

The native operations were `plugin marketplace add <temporary-local-marketplace>`, `plugin install toolbox@atlas`, `plugin list --json` and `skill list --json`, followed by co-installation and individual-folder checks. The local host described these plugins as **live**. This proves local registration and discovery, not Git-backed transfer, VS Code UI, Claude Code invocation, Codex skill selection, policy enforcement or useful application of instructions. No current user installation was refreshed. README paths and invocation syntax for Codex and Claude Code are documented installation routes, not exercised host sessions. Remote installation requires the new entry on the marketplace default branch; draft reviewers use the local checkout.

## Behavioral protocol

[Reusable fictional cases](../../evals/satchel-cases.json) contain raw requests separately from qualitative rubrics. They were authored from one-line candidate purposes before reading implementations: two cases per skill and three routing controls. They cover non-engineering and engineering work, mistaken explanations, authority-preserving rewrites, asynchronous recipient roles, quantitative and causal overclaims, and two three-turn teaching exchanges. The controls include exact-output arithmetic, ordinary prose editing and an interactive quiz that should not become an asynchronous questionnaire.

Actors receive the actual candidate instruction files and only their raw case material. Expected answers, prior reviews and grading criteria are withheld. All actors use authenticated Copilot Claude Opus 5.5 at xhigh with at most two concurrent jobs. The same model and case protocol run without skills for five pre-specified baseline cases, one per skill. Completed outputs are retained; they are not rerun to obtain preferred results.

The supervisor supplies text context only. It does not give these actors files, shell or network access. Multi-turn teaching uses exact prior-transcript replay in new jobs, delivering each fixed follow-up only after the preceding answer. Thus these trials can assess returned reasoning and teaching responses, but cannot prove native persistence, reference-tool use, actual file creation, absence of intermediate tool effects or automatic host routing. Catalog-only controls examine selection from supplied metadata, not discovery by a real host.

## Initial observations and independent grading

All **25 initial actor jobs completed**: 18 jobs cover the 13 candidate cases/controls, and seven cover five matched no-skill baseline cases, including teaching follow-ups. Receipts identify `claude-opus-5.5` / `xhigh`; no result truncation or event gap was observed for those actor jobs. Prompt/source hashes, fixture equality and exact prior-transcript replay were checked. These are execution-integrity findings, not a pass rate.

A fresh Opus 5.5/xhigh reviewer received the full outputs with treatment labels withheld, raw fixtures and qualitative rubrics. Two seeded grading controls accompanied the real outputs: an obviously false claim check and a short correct explanation repair. The reviewer rejected the former and accepted the latter. This modest calibration does not establish grader reliability. Source use is sometimes inferable from the text, so label masking is not perfect blinding.

The reviewer called all 18 real transcript groups passing, with qualifications. Primary inspection did **not** treat that as acceptance of every result:

| Case | Observed outcome and retained limitation |
| --- | --- |
| C01: museum explanation | Both arms corrected the wrong admission advice and required three tickets. No added benefit established. |
| C02: recovery explanation | The candidate separated application/data state and retracted the no-loss assurance. It nevertheless stated that restoring the database leaves application C live, where the supplied notes did not establish the binary effect. The reviewer called this borderline; primary assessment is partial. The skill already asks for uncertainty preservation, so this remains an observed adherence limit rather than justification for another generic warning. |
| C03: instruction rewrite | Both arms retained the major source/authority boundaries and partial progress, but added interpretations. The candidate placed a broader privacy rule, including attendee-email scope, inside operative instructions before asking for confirmation. Primary assessment is partial despite the grader's pass. The baseline also broadened privacy and invented “Staff send all messages.” Final guidance now keeps consequential unsettled interpretations outside operative rules unless deciding them is authorized. |
| C04: release instructions | The candidate retained explicit approvals, kept automatic shipping as an unaccepted proposal, and labeled the remote-draft-release question open. Its temporary local-only treatment is disclosed; this is not evidence that the open policy was decided. |
| C05–C06: questionnaires | Drafts separated program/budget authority from staffing knowledge, preserved settled opening time, and handled an unknown recipient role without appointing authority. The matched baseline was also useful. Drafts were longer than the user's “short” preference; neither arm establishes a five-minute response time. |
| C07–C08: evidence checks | Correct quantities and bounded conclusions generally survived: 50% to 75% is +25 percentage points, not doubling; 12 passing bench devices do not establish fleet repair. C07's candidate heading called attribution “contradicted” while its body correctly treated causality as unresolved. Both C07 arms added their own labeled statistical approximations; these are not supplied study findings and do not establish sampling assumptions or generalization. |
| C09–C10: teaching | Both baker-percentage arms explained the flour denominator and confirmed scaling; the SQL exchange elicited a prediction and corrected the join/filter misconception. Fixed follow-ups sometimes skipped the actor's question, and the candidate grew wordier. Transcript replay does not establish native session continuity or lasting learning. |
| C11–C13: controls | Arithmetic and a warm invitation received direct answers without a body request; the live quiz selected `teach-me` and asked one question. This tests the supplied catalog in a harness, not automatic host selection. |

The successful baselines limit any incremental-value claim. No general reliability or superiority claim is supported by this small fictional sample. Final revisions also clarify source-versus-recall, offer optional practice without an extra interaction gate, preserve all requested questionnaire items, and keep original-source preference within the requested evidence boundary. Those source-review repairs are distinct from the observed behavioral defect in C03.

## Final candidate checks

Seven follow-up actor jobs completed: diagnostic rechecks C03 and C05, new task fixtures H01–H03, and a second C03 recheck after the first writing correction remained insufficient. They use separate frozen source snapshots. H02 has a second turn that declines exercises. The [new fixture definitions](../../evals/satchel-heldout-cases.json) disclose that their author had seen the original skills while executing the initial study and knew the revision brief, but had not read revised implementations or outcome grading. They are new tasks, not fully blind test design. Rechecks do not replace initial findings. All seven completed on the requested model/effort without observed actor gaps or truncated results, and prompt/transcript/source integrity checks passed.

The first C03 recheck again put a stricter privacy interpretation inside the instructions and requested confirmation afterward. The second preserved the ambiguous source clause and placed alternative readings outside the instruction block. This supports a narrow diagnostic repair, not general authority preservation. The second C03's writing snapshot is SHA-256 `04a13676b637c47911cdba05fc7fd5fd121db23df00f6cdad207db8a65ec53f2`. The shipped text then received the two source-reviewed clarifications described above; it was not subjected to another actor run. H01 remains evidence for the earlier writing snapshot, not a rerun of shipped bytes.

Final package discovery passed again for **17 files / 13 native commands**, with empty stderr. Its identity is `01ce4f147ef968942662fd0cb4e15c4fb510724bfb00c580340e25fd78cfe7fe`: SHA-256 of compact JSON with sorted relative-path keys and each file's SHA-256 value. The tested native package bytes matched the Toolbox package at commit `8e4bea37`; this identity does not describe the renamed Satchel package. Atlas files and its existing marketplace fields remain unchanged against refreshed main `57225e63ee31b8e477dcdd9d6eacd89cf5a45095`.

A fresh Opus 5.5/xhigh reviewer assessed seven version-masked groups: the original C03, both C03 rechecks, C05, and H01–H03. This diagnostic brief explicitly emphasized comparing operative rules with source obligations after the earlier grader missed that pattern; it is not independent discovery of the defect. The reviewer classified the two earlier C03 outputs as partial and the latest as passing, consistent with primary inspection. It also found the following bounded outcomes:

- **H01:** consent, editorial approval and release-owner approval remained separate; original recordings remained protected, and private work continued. The instruction block was 280 whitespace-delimited words, under the requested 300. This used the earlier writing snapshot.
- **H02:** the explanation distinguished 9/10 spam caught from 9/18 flags correct, offered practice, then honored the no-exercise preference. The first answer expanded well beyond the tiny example; the follow-up was shorter.
- **H03:** the model withdrew its unsourced 90-day recollection and retained the policy's consent exception and unknown notes-retention scope. Its suggested phrase “is removed after 30 days” softened a requirement into a claim about practice; primary review retains that wording defect. No actual retention practice was observed.
- **C05:** recipient authority and conditional staffing were preserved, but the drafts remained lengthy for a requested five-minute reply.
- **Latest C03:** the key privacy ambiguity remained unresolved outside the operative instructions; its added completion check was less complete than the body. The narrow successful recheck does not prove every completion condition or future rewrite is correct.

These are reviews of returned artifacts and teaching responses. The rewritten instructions were not subsequently exercised by a downstream operational assistant. All original attempts and adverse findings remain part of the evidence; the last two source clarifications received diff review, not an additional behavioral run.

## Satchel rename verification

The owner selected **Satchel** before release; version `0.1.0` is unchanged. The five skill bodies, writing's mechanics reference, four upstream licenses and two case-definition files match the Toolbox commit `8e4bea37` byte for byte. The remaining package edits change the name, installation identifier and documentation links. All 60 Atlas files, its marketplace entry and the marketplace metadata remain unchanged.

An isolated offline check on macOS arm64 used the same cached Copilot CLI **1.0.91** runtime with fresh temporary configuration/cache. Three native commands registered the renamed local marketplace, installed `satchel@atlas` and listed its skills. All three exited successfully with empty stderr. Exactly the five expected plugin skills were enabled, each under `plugins/satchel/skills/`; the 17 package files remained unchanged during the check. Their aggregate identity, using the compact sorted-JSON method above, is `10fa4a1a6dcee29581cd39533d67463c860b7207f22d8ccf9af3c5e63978b264`.

This verifies the renamed installation entry and local discovery. It does not repeat the historical co-installation, individual-copy or behavioral trials. No inference ran and no user installation or settings changed.
