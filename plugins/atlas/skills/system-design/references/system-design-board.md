# System Design board

`30-system-design.html` is a deterministic, non-authoritative projection of canonical `30-system-design.md`. These labels are the stable chat-feedback and rendered-view identities.

| Stable label | Board title | Matching Markdown section(s) |
|---|---|---|
| `current-topology` | Current topology | `Current system` |
| `proposed-topology` | Proposed topology | `Proposed system` |
| `seam-ownership` | Seam and ownership | `Responsibilities and seams`; `Authoritative data ownership` |
| `interface-contract` | Interface and contract | `Contracts and interfaces` |
| `lifecycle-sequence-data-flow` | Lifecycle, sequence, and data flow | `Lifecycle and data flow` |
| `schema-protocol` | Schema and protocol | `Schema and protocol` |
| `failure-recovery` | Failure and recovery | `Failure and recovery` |
| `open-decisions` | Open decisions | `Open decisions` |
| `rejected-alternatives` | Rejected alternatives | `Rejected alternatives` |

Each matching Markdown section contains substantive commitments or an explicit reason beginning with `Inapplicable:`. The renderer displays that source text inside its labelled view; it does not invent a reason for a missing or empty section.

`Compatibility` and `Trust, security, and operations` remain required canonical Markdown sections even though they do not create additional board labels in Slice 2A. Their commitments constrain the labelled topology, contract, lifecycle, and failure views.

The HTML embeds the exact run-relative source path `30-system-design.md`, its SHA-256, and renderer version. It uses inline CSS only, contains no external assets or decorative image generation, and receives no independent acceptance hash. Chat snapshots are ephemeral.
