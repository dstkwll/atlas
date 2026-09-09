# Locate topic artifacts

Use the current project's approved artifact location for PRDs, tickets and handoffs. Keep one topic together; do not create a second home merely because a new skill was invoked.

Resolve the destination from explicit task instructions, then the project's existing instructions/configuration and topic records. Where Atlas configuration is used, read the location value `artifacts.planning_root` in the applicable project configuration or `~/.config/atlas/config.yaml`; project restrictions take precedence over a personal default. This setting supplies only a candidate path; it does not itself authorize writing or exporting material there, or importing other policies from that file. Inspect only the relevant setting and never include unrelated configuration or secrets in an artifact.

An absolute planning root can be an approved vault or separate planning repository. Resolve a repository-relative value from the target repository root, not the plugin directory or whichever shell directory happens to be active. Check that the destination is usable and appropriate for the task's information boundary. A personal vault setting must not route protected workplace material outside its approved environment. If routing is conflicting, inaccessible or ambiguous, report the specific issue and prepare safe content without silently switching destinations or provisioning synchronization.

Reuse an existing topic folder and its names. For a new topic use a descriptive slug beneath the resolved root. If there is no configured or established location, use `.planning/<topic>/` within the target repository when appropriate and report that choice; if there is no suitable repository, establish an approved destination before writing.

Default artifact shape when no project convention overrides it:

```text
<planning-root>/<topic>/
  prd.html
  tickets/
    index.md
    01-<slice>.md
  handoff.md
```

Create only requested artifacts. Use separate named handoffs for distinct recipients/transfers when needed, preserving earlier material decisions rather than overwriting them. Ticket numbering aids navigation; dependency links determine order. Reuse existing issue identities if a tracker is authoritative rather than create an unsynchronized second backlog.

Keep links within the topic relative when possible. Record target repositories and source relevance, but avoid embedding machine-specific vault roots in portable documents. Honor the destination's own format/index conventions: if a vault requires a Markdown catalog entry, it may point to the HTML source of record without duplicating the PRD. Do not migrate or delete an established canonical source as an incidental format change.
