# Atlas activation and continuity checks

Checked on 2026-09-08 in disposable local projects. This record covers the native Copilot profile and shared activation/continuity changes accompanying it. Earlier discovery and handoff evidence covers earlier candidates; it does not establish the new activation behavior.

## Claims and method

Atlas should be selected once for an assignment, load its canonical guidance, handle ordinary follow-ups, retain discovery-only scope, and report unavailable guidance honestly. Compaction must be tested through the host rather than simulated by asking a model to forget. Loading instructions and following them reliably are separate claims.

The shared discovery scenario was a team request inbox choosing manual claiming or automatic assignment. The initial prompt prohibited implementation and publication. The next message accepted manual claiming and requested `DISCOVERY.md`, without invoking Atlas again. After native compaction, the follow-up was simply: “Sounds good. What should we do next?” Only the discovery document was created in each project, apart from installed test guidance. File writing was available during the follow-up checks; these scope observations were not obtained solely by preventing writes.

## Observations

| Host/check | Observed outcome | Limit |
| --- | --- | --- |
| Copilot CLI 1.0.82, local plugin | Recognized the namespaced profile as `atlas:atlas`; unqualified `atlas` was rejected. Loaded this plugin's shared skill and discovery reference. | No VS Code picker or marketplace install of this new profile was exercised. |
| Copilot session resume | Reopened the existing session without `--agent`; the host restored the selected Atlas profile. The ordinary follow-up wrote only the requested discovery note. | One session; this is not evidence for every resume or client. |
| Copilot native `/compact` | Host reported successful compaction. Its summary retained task scope, accepted choice, unresolved fallback and canonical source path. The ordinary follow-up reread the candidate skill and `DISCOVERY.md`, then asked about the response window without implementing. | The discovery reference itself was not reread. The first activation preceded a small metadata/continuity wording refinement; the post-compaction skill read used the updated candidate. |
| Codex 0.153.4, project-local skill | Loaded the candidate skill and discovery reference. After native `thread/compact/start`, a completed `contextCompaction` item confirmed real compaction. The ordinary follow-up retained the unresolved exclusive-claiming question and requested judgment without implementation. | No post-compaction skill reread was observed. This supports scope continuity in this example, not full skill restoration or guaranteed reload. |
| Codex with optional project `AGENTS.md` default | Activated from the project instruction without an explicit skill input. After native compaction, the ordinary follow-up reread the candidate skill, discovery reference and decision note; it continued discovery without implementation. | One example supports this recovery path; it does not establish a causal improvement or guaranteed restoration rate. |
| Unavailable Copilot guidance | With the shared skill omitted from a disposable package and filesystem searches denied by the host, the profile reported that no shared guidance was loaded and that Atlas procedures remained unverified. It offered clearly separated general advice. | Covers unavailable/access-denied guidance, not every missing-file or duplicate-installation path. |

The Copilot check used its native CLI and isolated `COPILOT_HOME`. The initial activation exposed read tools; resumed checks also exposed file editing, with native approval for writes in the disposable project. The Codex checks used the installed native app-server, ephemeral sessions, ordinary host instructions, workspace-write sandbox and no escalation approval. The model was `gpt-5.6-sol`; low reasoning was selected for resumed Copilot checks and Codex checks. Initial Copilot activation used the host's default reasoning setting.

An exploratory Codex call supplying a skill path outside the project's discovered skill locations loaded an older personal Atlas copy. It was stopped and excluded from candidate proof. The project-local candidate was then installed and explicitly identified. This is evidence to verify the loaded source and avoid duplicate installations, not a general claim about host precedence.

The exercises also show imperfect adherence: the Copilot discovery note supplied a rationale the user had not stated, and the skill-only Codex follow-up did not visibly reload guidance after compaction. Neither was treated as proof of accepted user rationale or complete instruction compliance. These checks establish bounded observations, not a reliability rate.

Independent source and evidence review found no blocking findings after inspecting the sanitized native events, test drivers and discovery artifacts. Both Codex test installations were independently confirmed byte-identical to the delivered skill. Skill format, 76 relative file links, profile frontmatter, manifest agreement and whitespace checks passed. These objective checks establish package structure, not behavioral reliability.

## Host documentation and remaining limits

- [Copilot context management](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management) distinguishes persistent system instructions from summarized conversation history and describes preserved user instructions and checkpoints.
- [Claude skill lifecycle](https://code.claude.com/docs/en/skills#skill-content-lifecycle) documents reattachment after compaction subject to per-skill and combined content limits. Claude Code was unavailable locally; no Claude execution is claimed.
- [Codex project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md) provide a host-loaded entry path. A skill cannot arrange its own reload if both its activation instruction and source pointer disappear. A project default is optional and still depends on host loading and model adherence.
- [VS Code plugin packaging](https://code.visualstudio.com/docs/agent-customization/agent-plugins) supports the namespaced profile directory; [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents) support the linked instruction body. Documentation support is distinct from native execution.

Repeated automatic compactions in large sessions, every runbook's restoration, context drift rates, VS Code UI behavior, workplace policy and mobile/Remote selection remain unverified. No user's installed Atlas copy was changed. Sanitized local event extracts, native test drivers and synthetic discovery notes are retained in the workspace's sibling `research/2026-09-08-activation/` directory; they are not installed product resources.
