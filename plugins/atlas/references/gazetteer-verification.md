# Gazetteer verification evidence

Dated calibration record for the Gazetteer implementation. This file records proof; it is not workflow authority and does not replace installed-host recalibration.

## Source and deterministic gate

- Frozen handoff SHA-256: `bcb12596b1f1e1fa228c78ce6449496e1b8175626b012c22da5294f99f6483df`.
- Evidence ledger matched scenarios A–V and completion criteria 1–18.
- Complete repository gate after implementation and review fixes: 339 unit tests passed; architecture checker reported 29 consistent documents; seam checker reported zero findings, zero weak, zero skipped; Python compilation and `git diff --check` passed.
- Hermes Plugin Doctor passed runtime discovery, manifest parsing, import, and registration.

## Fresh Copilot host — read-only resume

Host: GitHub Copilot CLI 1.0.80, isolated plugin home, exact installed/source byte parity.

A fresh session began with Gazetteer and no chat history. It recovered the exact `demo` run, entered `start-run`, resumed the persisted Discovery frontier, surfaced the exact HUMAN question, and stopped without mutating the fixture. The before/after fixture fingerprint was identical.

This proves the fresh-session resume, mid-Discovery recovery, HUMAN stop, no internal command burden, and read-only status behavior classes.

## Fresh Copilot host — partial inventory isolation

Fixture: one valid Discovery run plus one tampered unrelated run under the same planning root.

Two fresh read-only sessions executed only `atlas_gazetteer.py inventory`:

- an exact request for the tampered `invalid` run stopped on its `gaps[].run` diagnostic and made no repair;
- an exact request for `valid` returned `PARTIAL`, oriented the valid run, retained the invalid-run diagnostic, and did not continue or mutate workflow state.

This proves that entry corruption is isolated during inventory while exact selected-run validation remains fail closed. A separate binding fixture likewise preserved `current-run` while projecting `stale-run` in `repository_blocked_runs`; a fresh host request for `stale-run` stopped on its unavailable binding and offered the unblocked current run separately.

## Fresh Copilot host — manual continuation

Fixture: a mechanically ready Discovery/Product Closure candidate with configured HUMAN authority and Program Design selected next.

The user supplied one explicit approval. Gazetteer entered the exact installed `start-run`, Discovery, and `control-run` procedures through the calibrated owner-loading path. Product Closure recorded `HUMAN_APPROVED`, `control.json` advanced to revision 2, `planning-control.json` initialized at `program_design/PLANNING`, and the assistant stopped before Program Design while explaining why that phase was next.

This is the separating behavioral witness for Discovery → Product Closure return and `INTERACTIVE` continuation. Product artifacts remained bound to their pre-existing hashes; only authoritative control/handoff state changed.

## Fresh Copilot host — automatic continuation

Fixture: `program_design/PLANNING`, current Program Design candidate plus matching AGENT_REVIEW PASS evidence, and tickets selected next with HUMAN authority.

The first execution exposed a real defect: continuation stopped merely because the next stage would eventually require HUMAN acceptance. The procedure was corrected so HUMAN blocks authority consumption, not entry into the already-selected producer.

The separating rerun:

1. revalidated the existing Program Design candidate, repository baseline, and AGENT_REVIEW evidence;
2. recorded Program Design as `AGENT_APPROVED` without a user prompt;
3. advanced to tickets and entered the ticket producer under `AUTO_CONTINUE`;
4. produced a mechanically valid one-ticket candidate;
5. stopped with `planning-control.json.phase=tickets`, `status=PLANNING`, tickets gate `PENDING`, and ticket acceptance `null`;
6. requested explicit HUMAN review rather than approving or executing the graph.

This proves automatic continuation across a legal non-HUMAN boundary and the separate HUMAN authority stop.

## Invocation-policy calibration

A prior attempt removed `disable-model-invocation: true` from internal skills to make Copilot nested invocation work. Spec review correctly rejected that broadening. Final behavior restores all internal guards and keeps every internal `agents/openai.yaml` non-implicit. Hosts that cannot nest-invoke a non-implicit sibling use only the exact already-selected installed-procedure fallback in `internal-owner-loading.md`; the fallback never chooses a stage or broadens discovery.

## Known limits

- Exact-ticket execution and completed-work authority remain future boundaries; no execution state is invented.
- Frontier-tier Gazetteer staffing is advisory and configuration-driven. This change adds no cross-host model router or self-escalation mechanism; the actual worker remains host/roster policy.
- `AUTO_CONTINUE` is invocation-local. It is not persisted in Atlas V1 and is never inferred from `governance: autonomous`.
- Host calibration is dated to the stated Copilot version and isolated install. Other hosts require their own runbook result.
