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

## Mobile projection contract

The board is a **Decide / Learn** surface, not a dashboard. It remains one readable content column at desktop and phone widths; stable-view navigation may wrap, but cards never compete in a narrow auto-fit grid.

- Markdown pipe tables render as semantic tables. Below `48rem`, each body row becomes one stacked labelled record using deterministic header-derived labels; the page itself must not scroll sideways.
- Fenced `text` diagrams preserve exact monospace whitespace with `white-space: pre` inside a focusable local overflow region. `pre-wrap` is forbidden because it changes diagram meaning.
- Other fenced code remains overflow-safe without being labelled as a diagram.
- Mermaid is not a runtime dependency or implied capability. Until a separately accepted bounded build-time Mermaid-to-safe-inline-SVG path exists, Mermaid source is labelled as source/fallback rather than claimed as rendered.
- Light and dark tokens, mobile-safe padding, and touch-sized navigation remain self-contained in inline CSS.

Renderer verification remains necessary but is not sufficient for visual acceptance. Use a Chromium-compatible browser when available with CSS viewports `390×844` and `1280×900`; device pixel ratio is not fixed because geometry checks use CSS pixels. At both widths require `document.documentElement.scrollWidth <= innerWidth`, and require every navigation target to be at least `44px` high. The browser `<title>` must exactly match the visible document H1. Inspect phone-scale screenshots in both light and dark schemes: the header, one table with at least three columns and three body rows, and the widest diagram whose `scrollWidth > clientWidth` (or the longest diagram when none overflow). Check clipping, illegible type, broken grouping, altered arrow geometry, and both the start and end of any locally scrollable diagram.
