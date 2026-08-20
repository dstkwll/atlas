# Autoprompt source map

## Provenance

- Repository: https://github.com/Spielewoy/autoprompt-skill
- Inspected commit: `1a195165c5e54ce33fc357425a0b3af7a8dae96f`
- Upstream CLI version at that commit: `1.0.3`
- License observed at that commit: MIT
- Inspection date: 2026-08-20

This Atlas skill is an original reference card. It does not vendor Autoprompt's prompt, agent,
framework, runtime, image, or installer files.

## What the source contains

Autoprompt combines two systems:

1. a defensive npm lifecycle CLI for install, doctor, update, repair, and receipt-scoped uninstall;
2. a mostly prompt-defined orchestration protocol packaged for six provider hosts.

Executable enforcement is strongest in installation transactions, payload/manifests, selected
Claude runtime helpers, and Prime's native dispatcher. Framework selection, decomposition, TDD
ordering, independent review, and repair routing remain substantially model-interpreted.

## Facet-to-file map

| Facet | Read first | Why |
|---|---|---|
| Provider-neutral protocol | `agents/contracts/generic.md` | Compact mission pointers, retained evidence, explicit invocation, and final assurance shape. |
| VS Code/Copilot Chat entry | `agents/vscode/SKILL.md`, `agents/vscode/README.md` | Exact VS Code 1.133+/Copilot 0.61 host contract and inherited-model behavior. |
| Category/tag/tier routing | `agents/claude/PLAYBOOKS.md`, `agents/contracts/frameworks/README.md` | Three independent execution-framework axes and selector behavior. |
| Conditional apply path | `agents/contracts/frameworks/apply.md` | Narrow execution path that still follows the mandatory roadmap gate. |
| Gate semantics | `agents/claude/GATES.md` | Prompt-level gate contracts and acceptance expectations. |
| Compact bound handoffs | `agents/claude/workflow/autoprompt-gate.js`, `agents/contracts/generic.md` | Hash/byte-length/nonce bindings and typed worker briefs. |
| Claude runtime enforcement | `agents/claude/workflow/autoprompt-gate.js`, `agents/claude/workflow/autoprompt-ledger-check.js`, `agents/claude/workflow/supervisor.sh` | Optional executable gate, ledger validation, resume, and relaunch paths. |
| Prime enforcement | `agents/prime/extensions/autoprompt.ts`, `agents/prime/skills/autoprompt/src/autoprompt/__init__.py` | Strongest executable topology and pointer-binding path in the repository. |
| Machine-readable roles | `agents/contracts/autoprompt.contract.json` | Named personas and declared capabilities. |
| Provider payloads | `scripts/runtime-payload.cjs`, `agents/manifests/*.json` | Generated package contents and payload hash validation. |
| Installer lifecycle | `bin/autoprompt.cjs`, `scripts/install/` | Transaction, collision checks, rollback, doctor, and uninstall scope. |
| Unsupported-host standard | `docs/guides/custom-agent-compatibility.md` | Ten requirements a new native adapter must prove before claiming support. |

## Noncanonical borrowing proposals

These classifications are proposals from source inspection, not accepted Atlas status. They become
Atlas authority only when the current checkout's canonical borrow map and decisions record the same
disposition and maturity.

| Candidate | Proposed disposition / maturity | Revisit trigger |
|---|---|---|
| Hash/length/nonce-bound artifact pointers | `CONCEPT` / `IMPLEMENTATION_REFERENCE` | Stage 5 ticket handoffs or Stage 7 worker envelopes need a compact integrity-bound brief. |
| Preserve accepted evidence; repair only named failures | `CONCEPT` / `ACCEPTED_PRINCIPLE` | Already reflected in boundary-local repair and targeted invalidation. |
| Useful-first dependency lanes | `REFERENCE` / `IMPLEMENTATION_REFERENCE` | Stage 5 ticket compiler is designed against real work. |
| Category + optional playbook + task/depth tier | `ADAPT` / `DEFERRED` | Stage 5–7 has a concrete execution-framework consumer. |
| Independent final goal check | `ADAPT` / `DEFERRED` | Stage 9 whole-feature validation exists. |
| Provider manifests, receipts, repair, and uninstall | `REFERENCE` / `DEFERRED` | Atlas actually ships across several supported hosts. |

## Claims the source does not support

- Direct routing to the earliest unresolved Atlas semantic stage.
- An intent/behavior/design uncertainty model.
- Universal executable enforcement of every documented gate.
- Compatibility with GitHub Copilot CLI merely because a VS Code adapter exists.
- Compatibility with Hermes merely because both systems understand `SKILL.md`.

## Import-time host probe — rerun before any installation

Observed before adding this reference on 2026-08-20:

- GitHub Copilot CLI `1.0.80` was present, with no installed plugins.
- No `code` executable or VS Code user configuration root was detected.
- The upstream VS Code doctor stopped on macOS Bash `3.2`; Autoprompt requires Bash `4.3+`.
- Hermes had no Autoprompt skill or provider adapter installed.

These facts explain why the incubator addition is reference-only. They are not permanent host facts;
rerun the checks before proposing a supported-provider installation.

Post-install discovery smoke on 2026-08-20:

- GitHub Copilot CLI `1.0.80`: `copilot skill list` reported `autoprompt` with the reference-only
  description.
- Hermes: `hermes skills list` reported `autoprompt` in category `incubator` as local and enabled;
  `skill_view(name='autoprompt')` loaded the card and exposed `references/source-map.md`.
- No ordinary-task or explicit-invocation policy test was run on either host. Discovery is not proof
  that host policy prevents implicit selection.

## User-level reference installation

The validated installation is a pinned copy, not a moving symlink:

- Copilot CLI: `~/.copilot/skills/autoprompt/`; remove with `copilot skill remove autoprompt`.
- Hermes: `~/.hermes/skills/incubator/autoprompt/`; removal must be scoped to that one directory.

Updates are intentionally manual. Reinspect and repin upstream first, then synchronize all four skill
files from this plugin and repeat both discovery checks. An automatic pull would silently move the
evidence base this reference exists to preserve.

## Compatibility verdicts at import

| Host | Verdict | Reason |
|---|---|---|
| VS Code + Copilot Chat | **Not installed** | Upstream adapter exists, but the required host was not detected and doctor failed its Bash floor. |
| GitHub Copilot CLI | **Adapter required** | It is not the VS Code custom-agent host; upstream ships no Copilot CLI package. |
| Hermes | **Adapter required** | A skill body can load, but native registration, recursive topology, lifecycle, and real-host tests are absent. |
