# Intake correction

Use this branch only when discovery proves that a repository identity or baseline in immutable `run.yaml` is wrong.

1. Discovery writes `.20-prd.next.md` with `intake_stale: true` and `gate_ready: false`, then installs it through the canonical writer; it never edits `run.yaml` or `control.json`.
2. Run `python3 tools/atlas_control.py mark-stale --run <run-directory> --reason <persisted-finding>`. This blocks the run and authorizes only the next intake amendment.
3. After explicit human acceptance, write exactly the next contiguous `amendments/NNN-*.md` using `skills/start-run/references/run-amendment.md`.
4. Run `python3 tools/atlas_control.py apply-amendment --run <run-directory>`.
5. Resume discovery against the new effective configuration revision and rerun Product Definition Approval from the cold-read sequence.

run.yaml remains byte-for-byte unchanged. The controller stores only the accepted amendment count and resulting effective configuration hash. There is no amendment ledger, receipt, or hash chain.
