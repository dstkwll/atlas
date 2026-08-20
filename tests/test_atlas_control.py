import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_control.py"


def frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    _, raw, _ = text.split("---", 2)
    return yaml.safe_load(raw)


def canonical_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: canonical_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [canonical_value(item) for item in value]
    return value


def seal_state(run: Path):
    path = run / "00-state.md"
    text = path.read_text(encoding="utf-8")
    _, raw, body = text.split("---", 2)
    state = yaml.safe_load(raw)
    config = yaml.safe_load((run / "run.yaml").read_text(encoding="utf-8"))
    state["effective_config_hash"] = hashlib.sha256(json.dumps(
        canonical_value(config), sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()
    state["base_run_sha256"] = hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest()
    path.write_text("---\n" + yaml.safe_dump(state, sort_keys=False) + "---" + body, encoding="utf-8")


class AtlasControlTests(unittest.TestCase):
    def test_human_gate_advances_one_phase_without_mutating_run_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            run_yaml = """version: 1
run: demo
opened: 2026-08-19
stages: [discovery, spec, program_design]
gates:
  discovery:
    authority: HUMAN
  spec:
    authority: HUMAN
repos:
  - repository: demo
    baseline: abc1234
"""
            (run / "run.yaml").write_text(run_yaml, encoding="utf-8")
            (run / "00-state.md").write_text("""---
feature: demo
status: PLANNING
phase: discovery
revision: 1
effective_config_revision: 0
gates:
  discovery: PENDING
  spec: PENDING
  program_design: PENDING
blocked_reason: null
pending_amendment: null
---

# State — demo

## Next

discovery is next. Authority: HUMAN.

## Notes

- Intake accepted.
""", encoding="utf-8")
            (run / "10-decisions.md").write_text("""---
run: demo
version: 1
status: draft
gate_ready: true
intake_stale: false
cold_read: complete
opened: '2026-08-19'
repos: [demo]
approved: null
approved_authority: null
approved_copy: null
approved_sha256: null
effective_config_revision: 0
---

# Decisions — demo

## Problem test

Operators cannot observe whether the requested outcome completed, so the work is worth doing.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

### D-001 — Should completion be observable?

The settled decision is that completion must be externally observable.
""", encoding="utf-8")

            seal_state(run)
            result = subprocess.run(
                [sys.executable, str(CLI), "advance", "--run", str(run),
                 "--approval", "human", "--date", "2026-08-19"],
                text=True, capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((run / "run.yaml").read_text(encoding="utf-8"), run_yaml)
            state = frontmatter(run / "00-state.md")
            candidate = frontmatter(run / "10-decisions.md")
            self.assertEqual((state["phase"], state["revision"]), ("spec", 2))
            self.assertEqual(state["gates"]["discovery"], "HUMAN_APPROVED")
            self.assertEqual(state["gates"]["spec"], "PENDING")
            self.assertEqual(candidate["status"], "approved")
            self.assertEqual(str(candidate["approved"]), "2026-08-19")
            approved_copy = run / candidate["approved_copy"]
            self.assertEqual(approved_copy, run / "approved" / "discovery-r2.md")
            self.assertTrue(approved_copy.is_file())
            digest = hashlib.sha256(approved_copy.read_bytes()).hexdigest()
            self.assertEqual(candidate["approved_sha256"], digest)

    def test_auto_gate_advances_without_fabricating_human_approval(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            (run / "run.yaml").write_text("""version: 1
run: demo
opened: 2026-08-19
stages: [discovery, spec]
gates:
  discovery:
    authority: AUTO
  spec:
    authority: HUMAN
repos:
  - repository: demo
    baseline: abc1234
""", encoding="utf-8")
            (run / "00-state.md").write_text("""---
feature: demo
status: PLANNING
phase: discovery
revision: 1
effective_config_revision: 0
gates: {discovery: PENDING, spec: PENDING}
blocked_reason: null
pending_amendment: null
---

# State — demo
""", encoding="utf-8")
            (run / "10-decisions.md").write_text("""---
run: demo
version: 1
status: draft
gate_ready: true
intake_stale: false
cold_read: complete
opened: '2026-08-19'
repos: [demo]
approved: null
approved_authority: null
approved_copy: null
approved_sha256: null
effective_config_revision: 0
---

# Decisions — demo

## Problem test

Operators cannot observe whether the requested outcome completed, so the work is worth doing.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

### D-001 — Should completion be observable?

The settled decision is that completion must be externally observable.
""", encoding="utf-8")

            seal_state(run)
            result = subprocess.run(
                [sys.executable, str(CLI), "advance", "--run", str(run),
                 "--date", "2026-08-19"], text=True, capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state = frontmatter(run / "00-state.md")
            self.assertEqual(state["gates"]["discovery"], "AGENT_APPROVED")
            self.assertEqual(state["phase"], "spec")
            approved = frontmatter(run / "approved" / "discovery-r2.md")
            self.assertEqual(approved["approved_authority"], "AUTO")

    def test_accepted_amendment_updates_effective_state_without_mutating_run_yaml(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            base = {
                "version": 1,
                "run": "demo",
                "opened": "2026-08-19",
                "goal": "demo",
                "planning_root": {"source": "artifacts.planning_root", "mode": "repository-relative", "path": ".planning"},
                "run_path": "demo",
                "stages": ["discovery", "spec"],
                "gates": {"discovery": {"authority": "HUMAN"}, "spec": {"authority": "HUMAN"}},
                "repos": [{"repository": "old", "baseline": "abc1234"}],
            }
            run_yaml = yaml.safe_dump(base, sort_keys=False).replace("'2026-08-19'", "2026-08-19")
            self.assertIn("opened: 2026-08-19", run_yaml)
            (run / "run.yaml").write_text(run_yaml, encoding="utf-8")
            (run / "00-state.md").write_text("""---
feature: demo
status: PLANNING
phase: discovery
revision: 1
effective_config_revision: 0
repos: [old]
gates: {discovery: PENDING}
blocked_reason: null
pending_amendment: null
---

# State — demo
""", encoding="utf-8")
            (run / "10-decisions.md").write_text("""---
run: demo
version: 1
status: draft
gate_ready: false
intake_stale: true
cold_read: complete
approved: null
approved_authority: null
approved_copy: null
approved_sha256: null
effective_config_revision: 0
opened: '2026-08-19'
repos: [old]
---

# Decisions

## Problem test

Operators cannot observe whether the requested outcome completed, so the work is worth doing.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

### D-001 — Should completion be observable?

The settled decision is that completion must be externally observable.
""", encoding="utf-8")
            seal_state(run)
            stale = subprocess.run(
                [sys.executable, str(CLI), "mark-stale", "--run", str(run),
                 "--reason", "new affected repository"], text=True, capture_output=True,
            )
            self.assertEqual(stale.returncode, 0, stale.stderr)
            stale_state = frontmatter(run / "00-state.md")
            self.assertEqual(stale_state["gates"]["discovery"], "STALE")
            self.assertEqual(stale_state["pending_amendment"], "run-config-001")
            prior = hashlib.sha256(json.dumps(
                base, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            ).encode("utf-8")).hexdigest()
            amendments = run / "amendments"
            amendments.mkdir()
            (amendments / "run-config-001.yaml").write_text(yaml.safe_dump({
                "version": 1,
                "amendment": "run-config-001",
                "applies_to": "run.yaml",
                "status": "accepted",
                "accepted": "2026-08-19",
                "reason": "new affected repository",
                "previous": None,
                "prior_effective_hash": prior,
                "changes": {"repos": [{"repository": "new", "baseline": "def4567"}]},
                "effective_config_revision": 1,
            }, sort_keys=False), encoding="utf-8")

            seal_state(run)
            result = subprocess.run(
                [sys.executable, str(CLI), "apply-amendment", "--run", str(run)],
                text=True, capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((run / "run.yaml").read_text(encoding="utf-8"), run_yaml)
            state = frontmatter(run / "00-state.md")
            self.assertEqual((state["effective_config_revision"], state["revision"]), (1, 3))
            self.assertEqual(state["repos"], ["new"])
            effective = dict(base)
            effective["repos"] = [{"repository": "new", "baseline": "def4567"}]
            self.assertEqual(state["effective_config_hash"], hashlib.sha256(json.dumps(
                effective, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            ).encode("utf-8")).hexdigest())
            self.assertEqual(
                state["accepted_amendments"]["amendments/run-config-001.yaml"],
                hashlib.sha256((amendments / "run-config-001.yaml").read_bytes()).hexdigest(),
            )
            self.assertEqual(state["status"], "PLANNING")
            self.assertIsNone(state["blocked_reason"])
            self.assertIsNone(state["pending_amendment"])

            amendment_path = amendments / "run-config-001.yaml"
            tampered = yaml.safe_load(amendment_path.read_text(encoding="utf-8"))
            tampered["reason"] = "tampered after acceptance"
            amendment_path.write_text(yaml.safe_dump(tampered, sort_keys=False), encoding="utf-8")
            decisions = frontmatter(run / "10-decisions.md")
            decisions.update({"intake_stale": False, "gate_ready": True, "effective_config_revision": 1})
            body = (run / "10-decisions.md").read_text(encoding="utf-8").split("---\n", 2)[2]
            (run / "10-decisions.md").write_text(
                "---\n" + yaml.safe_dump(decisions, sort_keys=False) + "---\n" + body,
                encoding="utf-8",
            )
            tamper_probe = subprocess.run(
                [sys.executable, str(CLI), "advance", "--run", str(run), "--approval", "human"],
                text=True, capture_output=True,
            )
            self.assertNotEqual(tamper_probe.returncode, 0)
            self.assertIn("accepted amendment hash mismatch", tamper_probe.stderr)

    def test_reopen_preserves_approved_copy_and_returns_spec_to_discovery(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            run_yaml = """version: 1
run: demo
opened: 2026-08-19
stages: [discovery, spec]
gates: {discovery: {authority: HUMAN}, spec: {authority: HUMAN}}
repos: [{repository: demo, baseline: abc1234}]
"""
            (run / "run.yaml").write_text(run_yaml, encoding="utf-8")
            approved = run / "approved" / "discovery-r2.md"
            approved.parent.mkdir()
            approved.write_text("---\nrun: demo\nstatus: approved\napproved: 2026-08-19\n---\n\n# Decisions\n", encoding="utf-8")
            digest = hashlib.sha256(approved.read_bytes()).hexdigest()
            (run / "10-decisions.md").write_text(f"""---
run: demo
version: 1
status: approved
gate_ready: true
intake_stale: false
approved: '2026-08-19'
approved_authority: HUMAN
approved_copy: approved/discovery-r2.md
approved_sha256: {digest}
cold_read: complete
opened: '2026-08-19'
repos: [demo]
effective_config_revision: 0
---

# Decisions

## Problem test

Operators cannot observe whether the requested outcome completed, so the work is worth doing.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

### D-001 — Should completion be observable?

The settled decision is that completion must be externally observable.
""", encoding="utf-8")
            (run / "20-spec.md").write_text("""---
run: demo
version: 1
status: draft
gate_ready: false
approved: null
effective_config_revision: 0
---

# Spec
""", encoding="utf-8")
            (run / "00-state.md").write_text(f"""---
feature: demo
status: PLANNING
phase: spec
revision: 2
effective_config_revision: 0
gates: {{discovery: HUMAN_APPROVED, spec: PENDING}}
approved_artifacts:
  approved/discovery-r2.md:
    phase: discovery
    sha256: {digest}
    authority: HUMAN
    approved: '2026-08-19'
blocked_reason: null
pending_amendment: null
---

# State
""", encoding="utf-8")

            seal_state(run)
            result = subprocess.run(
                [sys.executable, str(CLI), "reopen", "--run", str(run),
                 "--to", "discovery", "--reason", "spec exposed an unresolved decision"],
                text=True, capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((run / "run.yaml").read_text(encoding="utf-8"), run_yaml)
            self.assertEqual(hashlib.sha256(approved.read_bytes()).hexdigest(), digest)
            state = frontmatter(run / "00-state.md")
            decisions = frontmatter(run / "10-decisions.md")
            spec = frontmatter(run / "20-spec.md")
            self.assertEqual((state["phase"], state["revision"]), ("discovery", 3))
            self.assertEqual(state["gates"], {"discovery": "STALE", "spec": "STALE"})
            self.assertEqual((decisions["status"], decisions["version"]), ("draft", 2))
            self.assertFalse(decisions["gate_ready"])
            self.assertEqual(decisions["supersedes"], "approved/discovery-r2.md")
            self.assertEqual(spec["status"], "stale")
            self.assertFalse(spec["gate_ready"])

    def test_reject_persists_gate_outcome_and_block_reason(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            (run / "run.yaml").write_text("""version: 1
run: demo
opened: 2026-08-19
stages: [discovery, spec]
gates: {discovery: {authority: HUMAN}, spec: {authority: HUMAN}}
repos: [{repository: demo, baseline: abc1234}]
""", encoding="utf-8")
            (run / "00-state.md").write_text("""---
feature: demo
status: PLANNING
phase: discovery
revision: 1
effective_config_revision: 0
gates: {discovery: PENDING, spec: PENDING}
blocked_reason: null
pending_amendment: null
---

# State
""", encoding="utf-8")
            (run / "10-decisions.md").write_text("""---
run: demo
version: 1
status: draft
gate_ready: true
intake_stale: false
cold_read: complete
opened: '2026-08-19'
repos: [demo]
approved: null
approved_authority: null
approved_copy: null
approved_sha256: null
effective_config_revision: 0
---

# Decisions

## Problem test

Operators cannot observe whether the requested outcome completed, so the work is worth doing.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

### D-001 — Should completion be observable?

The settled decision is that completion must be externally observable.
""", encoding="utf-8")

            seal_state(run)
            result = subprocess.run(
                [sys.executable, str(CLI), "reject", "--run", str(run),
                 "--reason", "problem is not worth solving"], text=True, capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state = frontmatter(run / "00-state.md")
            self.assertEqual(state["phase"], "discovery")
            self.assertEqual(state["revision"], 2)
            self.assertEqual(state["status"], "BLOCKED")
            self.assertEqual(state["gates"]["discovery"], "REJECTED")
            self.assertEqual(state["blocked_reason"], "problem is not worth solving")

            retry = subprocess.run(
                [sys.executable, str(CLI), "advance", "--run", str(run),
                 "--approval", "human", "--date", "2026-08-19"],
                text=True, capture_output=True,
            )
            self.assertNotEqual(retry.returncode, 0)
            self.assertIn("run status is not PLANNING", retry.stderr)
            self.assertEqual(frontmatter(run / "00-state.md")["revision"], 2)


if __name__ == "__main__":
    unittest.main()
