# Community Garden Tool Checkout System

## Document status

- **Status:** Draft for continued product discovery
- **Purpose:** Define the agreed product behavior and preserve unresolved policy decisions without choosing defaults
- **Authority:** Local planning only; this document does not authorize implementation or publication
- **Source of record:** This PRD is the supplied planning source for this synthetic project.
- **Last updated:** 2026-09-14

## Problem

Community garden members need a quick way to learn whether a shared tool is available and to borrow it. Shed volunteers need enough accountability to manage a finite collection and follow up when tools do not return. The process must support that accountability without publicly identifying or blaming members for late returns.

The desired system is deliberately volunteer-mediated: it should make an in-person shed interaction easy rather than replace the volunteer with self-service checkout.

## Users and responsibilities

### Members

- Join by invitation only.
- View tool availability.
- Borrow one or more tools subject to policies that remain to be defined.
- Must not see the identities of other borrowers.

### Shed volunteers

- Manage the shed's checkout and return interactions.
- Manually record every checkout.
- Manually record every return.
- Need to identify the member involved in a checkout so the system can associate one current borrower with the tool.
- Do not yet have an accepted level of authority for resolving disputed returns.

## Product outcomes

1. An invited member can determine whether a tool is available without learning who has an unavailable or late tool.
2. A volunteer can record a routine checkout and return with little interruption to the physical shed interaction.
3. At most one member is recorded as the current borrower of a tool at any time.
4. Accountability and private follow-up remain possible without public blame.
5. Unsettled governance policies remain changeable rather than being embedded as accidental defaults.

## Design principles

### Low-friction, volunteer-mediated use

The record-keeping step should support a short in-person handoff. This matters because unnecessary data entry or member self-service would conflict with the chosen operating model and discourage consistent use.

### Private accountability

Borrower identity is operational information, not community-facing availability information. This matters because members need to know whether they can borrow a tool, while public identification of a late borrower could create blame or stigma.

### Explicit human authority

The system must not silently grant someone the power to rewrite a disputed return. This matters because resolving a disagreement is a governance decision, not merely routine data correction.

### Purpose-limited history

The system must not assume indefinite borrowing-history retention. This matters because historical identity data may aid operations but also creates privacy and governance obligations.

## Scope

### In scope for the product design

- Invitation-only member access.
- A member-facing view of tool availability.
- Volunteer-recorded checkout and return.
- Enforcement of one current borrower per tool.
- Role-appropriate visibility of current-loan information.
- Future handling of due dates, reminders, disputes, corrections, loss, damage, maintenance, and history retention once their policies are decided.

### Not authorized or not in scope now

- Member self-checkout or self-recorded returns.
- Public borrower names, public overdue notices, or public member rankings.
- Implementation, technology selection, deployment, integration with external services, or publication.
- A default decision for any policy listed as open in this PRD.

## Agreed functional requirements

### Membership and access

- Only invitation-only members participate as borrowers.
- Members can see whether a tool is available.
- How invitations are issued, accepted, revoked, or audited remains open.
- How volunteers identify a member during checkout remains open.

### Checkout

- A shed volunteer manually records each checkout.
- A checkout associates the selected tool with one current borrower.
- The system must prevent a second current borrower from being recorded for the same tool.
- The behavior when a tool is unavailable, reserved, restricted, or already recorded as checked out remains open.

### Return

- A shed volunteer manually records each return.
- A routine recorded return ends the current borrowing association and makes the tool available, unless another future policy places it into a non-borrowable state such as maintenance.
- Who may override the record when the member and system disagree about a return remains open.
- Correction, evidence, and review requirements for a disputed return remain open.

### Visibility and privacy

| Information | Member viewing tools | Shed volunteer performing operations |
| --- | --- | --- |
| Tool availability | Visible | Visible |
| Identity of another tool's current borrower | Not visible | Available as needed to operate the loan and private follow-up |
| Public overdue identity or ranking | Prohibited | Not applicable as a public feature |
| Borrowing history | Visibility and retention are undecided | Visibility and retention are undecided |

Member-facing output must not reveal borrower identity indirectly through an overdue list, activity feed, ranking, or similar presentation. The exact member-visible label for an unavailable, overdue, reserved, or maintenance-held tool is not yet decided.

## Representative workflows

### View availability

1. An invited member accesses the tool list.
2. The system shows whether each tool is available.
3. For an unavailable tool, the system does not reveal the current borrower's identity.

### Routine checkout

1. A member asks to borrow an available tool at the shed.
2. A volunteer identifies the member using a method still to be selected.
3. The volunteer selects the tool and member and records the checkout.
4. The system confirms that this member is the tool's sole current borrower.
5. Other members subsequently see that the tool is unavailable, without seeing the borrower's identity.

### Routine return

1. A member physically returns a borrowed tool to the shed.
2. A volunteer identifies the active checkout and records the return.
3. The system removes the current borrowing association.
4. The tool becomes available unless a future damage or maintenance policy requires another state.

### Disputed return

1. A member states that a tool was returned, but the current record or physical inventory does not agree.
2. Routine return handling stops before an override is made.
3. The system must preserve the disagreement for resolution without exposing it to other members.
4. The authorized resolver, required evidence, record changes, and member communication are all open decisions.

## Tool-state model

Only the following minimum meanings are currently settled:

- **Available:** no current borrower is recorded and the tool can be considered for checkout.
- **Checked out / unavailable:** exactly one current borrower is recorded; members may see unavailability but not borrower identity.

Additional states—such as reserved, overdue, return disputed, damaged, lost, or under maintenance—are candidates, not accepted requirements. Their names, transitions, visibility, and effects require policy decisions.

## Acceptance examples for settled behavior

1. **Available tool checkout:** Given an invited member and an available tool, when a volunteer records checkout, then that member becomes the tool's only current borrower and members see the tool as unavailable.
2. **Prevent double checkout:** Given a tool with a current borrower, when a volunteer attempts another checkout for that tool, then the system does not create a second current borrower.
3. **Routine return:** Given a checked-out tool, when a volunteer records its routine return, then the current borrowing association ends and the tool becomes available unless a future non-borrowable-state policy applies.
4. **Borrower privacy:** Given a tool borrowed by Member A, when Member B views availability, then Member B can see that the tool is unavailable but cannot see or infer that Member A has it.
5. **No public blame:** Given any late or disputed loan, no member-facing list, notice, feed, or ranking identifies the borrower.
6. **No assumed dispute override:** Given a disputed return, the system does not treat ordinary volunteer return entry as proof that an undecided override policy has been satisfied.

## Success indicators requiring later definition

The goals imply that success should eventually measure both ease and trust, but no targets or instrumentation have been accepted. Candidate questions include:

- Can volunteers complete routine checkout and return without delaying the physical handoff?
- Can members reliably determine availability?
- Are double checkouts prevented?
- Are borrower identities absent from every member-facing path?
- Can volunteers resolve operational problems without preserving more personal history than the garden decides is necessary?

These are evaluation themes, not approved metrics or thresholds.

## Open policy decisions

The following questions are deliberately unresolved:

1. **Disputed-return authority:** Who may override or resolve a disputed return? Is another person's review required, and what evidence or audit trail is appropriate?
2. **History retention:** Which borrowing events are retained, for how long, who may view them, and whether older records should be deleted or anonymized?
3. **Loan timing:** Are there standard due dates, tool-specific periods, extensions, grace periods, or quantity limits?
4. **Private reminders:** Are reminders automatic, volunteer-led, or hybrid? Which private channels and tone are appropriate, and when does escalation occur?
5. **Invitation lifecycle:** Who invites members, how access is revoked, and what happens to active loans when membership changes?
6. **Member identification:** What low-friction method lets a volunteer select the correct borrower?
7. **Shed availability:** What happens when a member arrives and no volunteer is available?
8. **Reservations and restricted tools:** Are reservations offered? Do scarce, valuable, or higher-risk tools follow different rules?
9. **Damage, loss, and maintenance:** Who records these conditions, what members see, and when a tool may return to circulation?
10. **Ordinary correction:** Which mistakes may volunteers correct without invoking the disputed-return process?
11. **Offline fallback:** How are checkouts and returns captured during an outage, and how are conflicts reconciled later?
12. **Operational reporting:** What minimal reporting do volunteers need without creating a member reputation system?

## Risks and constraints

- A member-facing surface could reveal identity indirectly even if it omits a name; privacy must apply to all member-visible paths.
- Volunteer-mediated entry reduces ambiguity about who records transactions but may create queues or gaps when no volunteer is available.
- Treating ordinary corrections and disputed overrides as the same permission could either block harmless fixes or allow consequential records to be rewritten too easily.
- Retaining too little history may hinder dispute resolution; retaining too much may conflict with the privacy intent. The balance requires an explicit garden policy.
- The workspace contains no implementation or established technical system to inspect, so this PRD defines product intent rather than implementation readiness.

## Decision record

### Accepted by the product owner

- Membership is invitation-only.
- Checkout is manually recorded by a shed volunteer.
- Return is manually recorded by a shed volunteer.
- Each tool has at most one current borrower.
- Members see availability but not borrower identities.
- Use should be low friction.
- Late returns must not produce public blame.

### Explicitly left open by the product owner

- Who may override a disputed return.
- How long borrowing history is retained.

### Additional uncertainty surfaced during discovery

All other questions in **Open policy decisions** remain proposals for further discovery. Their inclusion records design territory; it does not commit the product to those features or any default answer.

## Planning resume point

Continue discovery with the overdue experience: decide whether private reminders are automatic, volunteer-led, or hybrid, and define what the borrower and volunteers can see. Do not resolve disputed-return authority or borrowing-history retention unless the product owner supplies those decisions.

Planning continues through the local [`tickets/index.md`](tickets/index.md); [`handoff.md`](handoff.md) contains the bounded resume brief and authority limits.
