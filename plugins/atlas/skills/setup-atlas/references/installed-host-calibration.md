# Installed-host calibration

Use this runbook after installation/update, when a host cannot find an Atlas skill, or before claiming that an installed host executes the current plugin. It verifies six separate claims: **installation bytes**, **deterministic runtime readiness**, **host recognition**, **skill discovery**, **procedure completion**, and **cross-skill handoff**. Passing one never implies the next. A dependency/CLI failure makes runtime readiness FAIL without changing a byte-equality PASS.

Inputs are an exact `<installed-plugin-root>`, optional `<source-plugin-root>`, the host executable/version when available, and an optional disposable `<calibration-run>` with its expected starting/ending state declared before invocation. The runbook is complete when every claim is reported `PASS`, `FAIL`, or `UNVERIFIED` with its evidence/reason; unavailable host or fixture surfaces never become inferred PASS.

## 1. Record the subject

Record the date, host and host version, installed plugin root, invocation form, and whether a source checkout is available. Never record credentials or authentication material.

Resolve the installed root from the loaded `setup-atlas/SKILL.md`; do not infer it from caller CWD. Require `plugin.json`, `requirements.txt`, `tools/`, and `skills/` as real non-symlinked entries.

## 2. Verify installation bytes

Enumerate every real `skills/*/SKILL.md`. Require each sibling `agents/openai.yaml`, and verify every manifest retains `policy.allow_implicit_invocation: false`. Require the packaged controllers/renderers named by the installed skills.

When commissioning from a source checkout, compare the source plugin and installed plugin recursively while excluding generated caches only:

```shell
diff -qr --exclude='__pycache__' "<source-plugin-root>" "<installed-plugin-root>"
```

Any source/install difference blocks a current-source claim. Reinstall or update, then repeat the comparison before executing a fixture.

## 3. Verify deterministic dependencies

Run the dependency probe from `setup-atlas/SKILL.md` and record the exact Python launcher/interpreter path that passed it. Invoke exactly these packaged CLIs with `--help` using that same launcher and each installed absolute path: `tools/atlas_control.py`, `tools/atlas_planning.py`, `tools/render_prd.py`, and `tools/render_system_design.py`. A missing dependency or CLI is installation failure, not an optional degradation; success under a different temporary interpreter does not prove the configured/default host launcher is ready.

## 4. Verify host recognition and skill discovery

Use the host's machine-readable inventory/event surface, not an assistant sentence, to record which installed Atlas skills the host recognized and enabled. Compare that inventory with the filesystem enumeration from step 2.

For Copilot CLI, record `copilot --version`, run one non-mutating prompt with `--output-format json`, `--share=<session.md>`, and a dedicated `--log-dir`, then inspect the emitted `session.skills_loaded` event for the exact enabled Atlas inventory. Preserve the command and event path in the calibration report. If that event is absent, host recognition is `UNVERIFIED` even when the filesystem is complete.

If inventory lists a skill but a later lookup reports it missing, record **host recognition PASS / skill lookup FAIL**. Do not reinstall blindly and do not claim the plugin is absent. A direct read of the exact installed `SKILL.md` may be used only as an explicitly labelled diagnostic fallback.

## 5. Verify procedure completion

Use only the predeclared disposable `<calibration-run>`. Before invocation, record its exact phase/gate/revision, expected output or fail-closed result, owned writable paths, and hashes of every state/repository path that must remain unchanged. Invoke one bounded Atlas entry using the normal installed-host command surface (or label an exact installed-`SKILL.md` path as a diagnostic fallback). Verify the expected artifact/state bytes and verify the fixture repository remains clean unless the procedure explicitly owns a repository write. Without this run plus oracle, procedure completion is `UNVERIFIED`.

For an inter-skill workflow, separately verify the required **cross-skill handoff** occurred without another user routing command. Name the expected producer and consumer before invocation and prove both from the host session/event record plus final state. Invocation success alone is not handoff proof; without a handoff-capable fixture this claim is `UNVERIFIED`.

## 6. Report calibrated scope

Report one result per claim in this exact table: `claim | PASS/FAIL/UNVERIFIED | evidence path or command | reason/limitation`. Include exact host version/path and all failures. The outcome is **dated calibration** for that host/version/path—not a continuing compatibility guarantee. Keep fixture/session/log output outside the public plugin tree and redact secrets before sharing any excerpt.
