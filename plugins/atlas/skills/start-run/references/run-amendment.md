# Run-configuration amendment

Use an amendment only when accepted Stage 0 intake becomes stale. `run.yaml` remains byte-for-byte immutable; accepted amendments provide reproducible replacement values for the effective configuration.

```yaml
version: 1
amendment: run-config-001
applies_to: run.yaml
status: accepted
accepted: "<YYYY-MM-DD>"
reason: <persisted repository or baseline finding>
previous: null
prior_effective_hash: <sha256 of canonical effective YAML before this amendment>
changes:
  repos:
    - repository: <stable repository identity>
      baseline: <commit SHA>
effective_config_revision: 1
```

## Rules

- Store records at `<run>/amendments/run-config-NNN.yaml` with contiguous numbering.
- Use exactly the version-1 fields shown above. `version` must be `1`, `accepted` must be a quoted canonical `YYYY-MM-DD` string, and `reason` must be a non-empty string; deterministic control rejects malformed records before applying them.
- Stage 0 previews the full replacement values and requires human acceptance before writing `status: accepted`.
- `prior_effective_hash` is SHA-256 over canonical JSON of the effective configuration before this amendment: parse YAML into ordinary data, serialize UTF-8 with lexicographically sorted object keys, no insignificant whitespace, separators `,` and `:`, and no trailing newline. A consumer stops on mismatch.
- `changes` uses top-level replacement semantics. A named map or list replaces that complete value; it is never recursively merged.
- A `repos` replacement is a non-empty list of exact `repository`/`baseline` maps. Repository identities are non-empty strings and unique within the replacement; baselines are 7–64 hexadecimal commit SHAs. Nulls, booleans, blank values, duplicate identities, and extra nested keys are invalid.
- The V1 executable amendment surface is deliberately narrow: `changes` may replace only `repos`. This covers discovery's stale repository/baseline recovery while ensuring the state mirror cannot drift from workflow, gate, roster, or policy changes it does not yet project. Start a different run for those changes until a later controller explicitly supports them.
- `version`, `run`, `opened`, `goal`, `planning_root`, and `run_path` cannot be amended. Start a different run when one of those identities is wrong.
- `previous` is null for the first amendment and names the preceding amendment thereafter.
- The control plane reconstructs effective intake by applying accepted amendments in numeric order. Stage skills read that effective view rather than global configuration.
- After acceptance, `tools/atlas_control.py apply-amendment` updates `00-state.md.effective_config_revision` and `effective_config_hash`, appends the amendment file's byte-level SHA-256 to `accepted_amendments`, mirrors effective repositories, clears the stale-intake blocker, and increments state revision. Every later transition verifies both the amendment receipt and reconstructed effective configuration, so modifying an already accepted record fails closed even when its configuration result would be unchanged. Stage 0 never edits authoritative state directly. Discovery then revalidates its decision log against the effective repository set.
