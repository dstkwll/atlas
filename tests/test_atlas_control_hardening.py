import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_control.py"


def canonical_hash(data):
    return hashlib.sha256(json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def write_frontmatter(path, data, body="# Fixture\n"):
    path.write_text(
        "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n\n" + body,
        encoding="utf-8",
    )


def valid_spec_body():
    return """# Spec — Demo

## Problem

Operators cannot observe whether the requested outcome completed.

## Requirements

### R-001 — Observable completion
**Current:** Completion is not externally visible.
**Target:** Completion becomes externally visible.
**Acceptance:** A completed request reports completion; absence of that report falsifies it.
**Derived from:** D-001

## Prohibitions

None applicable — discovery established no work-specific forbidden outcome.

## Constraints

None applicable — discovery established no externally observable limit.

## Invariants

None applicable — discovery established no continuous condition.

## Out of scope

| ID | Excluded | Why | Derived from |
|---|---|---|---|
| X-001 | Implementation design | It belongs to a later stage. | D-002 |

## Edge coverage

| Edge | Category | Resolution |
|---|---|---|
| exact completion boundary | boundary | covered by R-001 |
| adjacent completion states | adjacency | covered by R-001 |
| no completion payload | empty | none applicable — completion is itself the payload |
| completion encoding | encoding | none applicable — the contract does not select an encoding |
| completion order | ordering | none applicable — only one completion is observed |
| completion precision | precision | none applicable — no numeric quantity is exposed |
| repeated completion | idempotency | none applicable — repetition is outside this contract |
| concurrent completion | concurrency | none applicable — concurrency is outside this contract |

## Open questions

None.
"""


def valid_discovery_body(extra=""):
    return """# Decisions — Demo

## Problem test

Operators cannot observe whether the requested outcome completed, so the work is worth doing.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

### D-001 — Should completion be observable?

The settled decision is that completion must be externally observable.

### D-002 — Does implementation design belong in this contract?

The settled decision excludes implementation design from the behavioral contract.
""" + extra


def valid_stage_zero_config():
    gates = {
        "discovery": {"authority": "HUMAN"},
        "spec": {"authority": "HUMAN"},
    }
    return {
        "version": 1,
        "run": "demo",
        "opened": "2026-08-19",
        "goal": "Make completion externally observable",
        "planning_root": {
            "source": "artifacts.planning_root",
            "mode": "repository-relative",
            "path": ".planning",
        },
        "run_path": "demo",
        "recommendation": {
            "workflow": "normal",
            "governance": "standard",
            "execution_policy": "conservative",
            "environment_policy": "local_worktree",
            "roster": "default",
            "gates": gates,
            "reasons": [{"dimension": "workflow", "evidence": "behavior must be specified"}],
        },
        "workflow": "normal",
        "stages": ["discovery", "spec"],
        "governance": "standard",
        "gates": gates,
        "execution_policy": "conservative",
        "environment_policy": "local_worktree",
        "roster": "default",
        "risk": {
            "scope": "medium",
            "reversibility": "medium",
            "architecture_change": False,
            "schema_change": False,
            "public_contract_change": False,
            "security_sensitive": False,
            "operational_impact": "low",
            "testability": "high",
        },
        "repos": [{"repository": "fixture", "baseline": "abc1234"}],
        "overrides": [],
    }


def valid_pristine_state():
    return {
        "feature": "demo",
        "status": "PLANNING",
        "phase": "discovery",
        "revision": 1,
        "effective_config_revision": 0,
        "effective_config_hash": None,
        "base_run_sha256": None,
        "repos": ["fixture"],
        "gates": {"discovery": "PENDING", "spec": "PENDING"},
        "active_ticket": None,
        "blocked_reason": None,
        "pending_amendment": None,
        "approved_artifacts": {},
        "accepted_amendments": {},
    }


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)], text=True, capture_output=True,
    )


def make_gate_fixture(run, *, status="PLANNING", blocked_reason=None, candidate_run="demo"):
    base = {
        "version": 1, "run": "demo", "opened": "2026-08-19", "stages": ["discovery", "spec"],
        "gates": {"discovery": {"authority": "HUMAN"}, "spec": {"authority": "HUMAN"}},
        "repos": [{"repository": "fixture", "baseline": "abc1234"}],
    }
    (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
    write_frontmatter(run / "00-state.md", {
        "feature": "demo", "status": status, "phase": "discovery", "revision": 1,
        "effective_config_revision": 0, "effective_config_hash": canonical_hash(base),
                "base_run_sha256": hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest(),
        "gates": {"discovery": "PENDING", "spec": "PENDING"},
        "approved_artifacts": {}, "blocked_reason": blocked_reason, "pending_amendment": None,
    })
    write_frontmatter(run / "10-decisions.md", {
        "run": candidate_run, "version": 1, "status": "draft", "gate_ready": True,
        "intake_stale": False, "approved": None, "approved_authority": None,
        "approved_copy": None, "approved_sha256": None, "effective_config_revision": 0,
        "cold_read": "complete", "opened": "2026-08-19", "repos": ["fixture"],
    }, valid_discovery_body())


def make_pending_amendment_fixture(run):
    make_gate_fixture(run)
    candidate = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
    candidate.update({"gate_ready": False, "intake_stale": True})
    write_frontmatter(run / "10-decisions.md", candidate, valid_discovery_body())
    marked = run_cli("mark-stale", "--run", run, "--reason", "new repository")
    if marked.returncode != 0:
        raise AssertionError(marked.stderr)
    base = yaml.safe_load((run / "run.yaml").read_text())
    amendment = {
        "version": 1,
        "amendment": "run-config-001",
        "applies_to": "run.yaml",
        "status": "accepted",
        "accepted": "2026-08-19",
        "reason": "new repository",
        "previous": None,
        "prior_effective_hash": canonical_hash(base),
        "changes": {"repos": [{"repository": "new", "baseline": "def4567"}]},
        "effective_config_revision": 1,
    }
    amendment_dir = run / "amendments"
    amendment_dir.mkdir()
    return amendment_dir / "run-config-001.yaml", amendment


def make_spec_gate_fixture(run):
    make_gate_fixture(run)
    base = yaml.safe_load((run / "run.yaml").read_text())
    base["stages"].append("program_design")
    base["gates"]["spec"]["authority"] = "AUTO"
    base["gates"]["program_design"] = {"authority": "HUMAN"}
    (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
    state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
    state["effective_config_hash"] = canonical_hash(base)
    state["base_run_sha256"] = hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest()
    state["gates"]["program_design"] = "PENDING"
    write_frontmatter(run / "00-state.md", state)
    advanced = run_cli(
        "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
    )
    if advanced.returncode != 0:
        raise AssertionError(advanced.stderr)


def approve_and_reopen(run):
    make_gate_fixture(run)
    advanced = run_cli(
        "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
    )
    if advanced.returncode != 0:
        raise AssertionError(advanced.stderr)
    reopened = run_cli(
        "reopen", "--run", run, "--to", "discovery", "--reason", "new decision"
    )
    if reopened.returncode != 0:
        raise AssertionError(reopened.stderr)


class AtlasControlHardeningTests(unittest.TestCase):
    def test_amendment_rejects_noncanonical_acceptance_date(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            amendment_path, amendment = make_pending_amendment_fixture(run)
            amendment["accepted"] = "08/19/2026"
            amendment_path.write_text(yaml.safe_dump(amendment, sort_keys=False), encoding="utf-8")

            result = run_cli("apply-amendment", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("amendment accepted date", result.stderr)

    def test_amendment_rejects_wrong_version(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            amendment_path, amendment = make_pending_amendment_fixture(run)
            amendment["version"] = 999
            amendment_path.write_text(yaml.safe_dump(amendment, sort_keys=False), encoding="utf-8")

            result = run_cli("apply-amendment", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("amendment version", result.stderr)

    def test_amendment_rejects_empty_reason(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            amendment_path, amendment = make_pending_amendment_fixture(run)
            amendment["reason"] = None
            amendment_path.write_text(yaml.safe_dump(amendment, sort_keys=False), encoding="utf-8")

            result = run_cli("apply-amendment", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("amendment reason", result.stderr)

    def test_apply_amendment_requires_state_identity(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            amendment_path, amendment = make_pending_amendment_fixture(run)
            amendment_path.write_text(yaml.safe_dump(amendment, sort_keys=False), encoding="utf-8")
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            state["feature"] = "other-run"
            write_frontmatter(run / "00-state.md", state)

            result = run_cli("apply-amendment", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("state feature does not match run identity", result.stderr)

    def test_amendment_rejects_invalid_repository_identity(self):
        invalid_repos = {
            "null repository": [{"repository": None, "baseline": "def4567"}],
            "empty repository": [{"repository": " ", "baseline": "def4567"}],
            "boolean repository": [{"repository": True, "baseline": "def4567"}],
            "null baseline": [{"repository": "new", "baseline": None}],
            "empty baseline": [{"repository": "new", "baseline": " "}],
            "boolean baseline": [{"repository": "new", "baseline": False}],
            "non-SHA baseline": [{"repository": "new", "baseline": "not-a-sha"}],
            "duplicate identity": [
                {"repository": "new", "baseline": "def4567"},
                {"repository": "new", "baseline": "fedcba9"},
            ],
            "extra nested key": [
                {"repository": "new", "baseline": "def4567", "extra": "forged"},
            ],
        }
        for name, repos in invalid_repos.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                amendment_path, amendment = make_pending_amendment_fixture(run)
                amendment["changes"]["repos"] = repos
                amendment_path.write_text(yaml.safe_dump(amendment, sort_keys=False), encoding="utf-8")

                result = run_cli("apply-amendment", "--run", run)

                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, "repository|baseline|repos")

    def test_auto_gate_rejects_schema_incomplete_discovery_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            base = yaml.safe_load((run / "run.yaml").read_text())
            base["opened"] = "2026-08-19"
            base["gates"]["discovery"]["authority"] = "AUTO"
            (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            state["effective_config_hash"] = canonical_hash(base)
            state["base_run_sha256"] = hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest()
            write_frontmatter(run / "00-state.md", state)
            candidate = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            candidate.pop("cold_read")
            write_frontmatter(run / "10-decisions.md", candidate)

            result = run_cli("advance", "--run", run, "--date", "2026-08-19")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("discovery candidate", result.stderr)

    def test_auto_gate_rejects_empty_discovery_body(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            base = yaml.safe_load((run / "run.yaml").read_text())
            base["gates"]["discovery"]["authority"] = "AUTO"
            (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            state["effective_config_hash"] = canonical_hash(base)
            state["base_run_sha256"] = hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest()
            write_frontmatter(run / "00-state.md", state)
            candidate = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            write_frontmatter(run / "10-decisions.md", candidate, "# Decisions — Demo\n")

            result = run_cli("advance", "--run", run, "--date", "2026-08-19")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("discovery body", result.stderr)

    def test_auto_gate_rejects_schema_incomplete_spec_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_spec_gate_fixture(run)
            write_frontmatter(run / "20-spec.md", {
                "run": "demo", "version": 1, "status": "draft", "gate_ready": True,
                "approved": None, "approved_authority": None, "approved_copy": None,
                "approved_sha256": None, "amendment": None,
                "derived-from": "10-decisions.md", "effective_config_revision": 0,
            }, "# Spec\n")

            result = run_cli("advance", "--run", run, "--date", "2026-08-19")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("spec candidate fields do not match version-1 schema", result.stderr)

    def test_discovery_candidate_rejects_unexpected_frontmatter(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            candidate = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            candidate["rogue"] = "accepted"
            write_frontmatter(run / "10-decisions.md", candidate)

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fields do not match", result.stderr)

    def test_intake_stale_requires_a_boolean_for_human_and_auto(self):
        for authority in ("HUMAN", "AUTO"):
            with self.subTest(authority=authority), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                make_gate_fixture(run)
                base = yaml.safe_load((run / "run.yaml").read_text())
                base["gates"]["discovery"]["authority"] = authority
                (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
                state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
                state["effective_config_hash"] = canonical_hash(base)
                state["base_run_sha256"] = hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest()
                write_frontmatter(run / "00-state.md", state)
                candidate = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
                candidate["intake_stale"] = "true"
                write_frontmatter(run / "10-decisions.md", candidate)

                args = ["advance", "--run", run, "--date", "2026-08-19"]
                if authority == "HUMAN":
                    args += ["--approval", "human"]
                result = run_cli(*args)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("intake_stale must be a boolean", result.stderr)

    def test_discovery_candidate_accepts_an_unquoted_canonical_opened_date(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            text = (run / "10-decisions.md").read_text(encoding="utf-8")
            text = text.replace("opened: '2026-08-19'", "opened: 2026-08-19")
            (run / "10-decisions.md").write_text(text, encoding="utf-8")

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_auto_gate_rejects_empty_specification_body(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_spec_gate_fixture(run)
            write_frontmatter(run / "20-spec.md", {
                "run": "demo", "version": 1, "status": "draft", "gate_ready": True,
                "approved": None, "approved_authority": None, "approved_copy": None,
                "approved_sha256": None, "supersedes": None, "amendment": None,
                "derived-from": "10-decisions.md", "effective_config_revision": 0,
            }, "# Empty spec\n")

            result = run_cli("advance", "--run", run, "--date", "2026-08-19")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("spec body", result.stderr)

    def test_specification_requires_each_contract_section_independently(self):
        for heading in (
            "Problem", "Requirements", "Prohibitions", "Constraints", "Invariants",
            "Out of scope", "Edge coverage", "Open questions",
        ):
            with self.subTest(heading=heading), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                make_spec_gate_fixture(run)
                body = valid_spec_body().replace(f"## {heading}\n", f"## Missing {heading}\n")
                write_frontmatter(run / "20-spec.md", {
                    "run": "demo", "version": 1, "status": "draft", "gate_ready": True,
                    "approved": None, "approved_authority": None, "approved_copy": None,
                    "approved_sha256": None, "supersedes": None, "amendment": None,
                    "derived-from": "10-decisions.md", "effective_config_revision": 0,
                }, body)

                result = run_cli("advance", "--run", run, "--date", "2026-08-19")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"missing required section: {heading}", result.stderr)

    def test_auto_gate_advances_a_structurally_valid_specification(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_spec_gate_fixture(run)
            write_frontmatter(run / "20-spec.md", {
                "run": "demo", "version": 1, "status": "draft", "gate_ready": True,
                "approved": None, "approved_authority": None, "approved_copy": None,
                "approved_sha256": None, "supersedes": None, "amendment": None,
                "derived-from": "10-decisions.md", "effective_config_revision": 0,
            }, valid_spec_body())

            result = run_cli("advance", "--run", run, "--date", "2026-08-19")

            self.assertEqual(result.returncode, 0, result.stderr)
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            self.assertEqual(state["phase"], "program_design")
            self.assertEqual(state["gates"]["spec"], "AGENT_APPROVED")

    def test_spec_rejects_reference_absent_from_immutable_approved_discovery(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_spec_gate_fixture(run)
            body = valid_spec_body().replace("D-001", "D-999")
            write_frontmatter(run / "20-spec.md", {
                "run": "demo", "version": 1, "status": "draft", "gate_ready": True,
                "approved": None, "approved_authority": None, "approved_copy": None,
                "approved_sha256": None, "supersedes": None, "amendment": None,
                "derived-from": "10-decisions.md", "effective_config_revision": 0,
            }, body)

            result = run_cli("advance", "--run", run, "--date", "2026-08-19")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not present in immutable approved discovery", result.stderr)

    def test_spec_candidate_rejects_nonnull_supersedes_until_amendments_exist(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_spec_gate_fixture(run)
            write_frontmatter(run / "20-spec.md", {
                "run": "demo", "version": 1, "status": "draft", "gate_ready": True,
                "approved": None, "approved_authority": None, "approved_copy": None,
                "approved_sha256": None, "supersedes": 1, "amendment": None,
                "derived-from": "10-decisions.md", "effective_config_revision": 0,
            }, valid_spec_body())

            result = run_cli("advance", "--run", run, "--date", "2026-08-19")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("spec candidate supersedes", result.stderr)

    def test_spec_candidate_rejects_nonnull_amendment_until_transition_exists(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_spec_gate_fixture(run)
            write_frontmatter(run / "20-spec.md", {
                "run": "demo", "version": 1, "status": "draft", "gate_ready": True,
                "approved": None, "approved_authority": None, "approved_copy": None,
                "approved_sha256": None, "supersedes": None,
                "amendment": "run-config-001.yaml",
                "derived-from": "10-decisions.md", "effective_config_revision": 0,
            }, valid_spec_body())

            result = run_cli("advance", "--run", run, "--date", "2026-08-19")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("spec candidate amendment", result.stderr)

    def test_initialize_seals_base_run_before_discovery(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            base = valid_stage_zero_config()
            (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
            write_frontmatter(run / "00-state.md", valid_pristine_state())
            result = run_cli("initialize", "--run", run)
            self.assertEqual(result.returncode, 0, result.stderr)
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            self.assertEqual(state["effective_config_hash"], canonical_hash(base))
            self.assertEqual(
                state["base_run_sha256"], hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest()
            )
            self.assertEqual(state["revision"], 1)
            self.assertFalse((run / "10-decisions.md").exists())

    def test_initialize_rejects_schema_incomplete_stage_zero_intake(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            base = valid_stage_zero_config()
            base.pop("goal")
            (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
            write_frontmatter(run / "00-state.md", valid_pristine_state())

            result = run_cli("initialize", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("run.yaml fields do not match version-1 schema", result.stderr)

    @unittest.skipUnless(hasattr(signal, "SIGSTOP"), "requires POSIX process suspension")
    def test_concurrent_commands_cannot_both_commit_from_one_revision(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            candidate = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            write_frontmatter(
                run / "10-decisions.md",
                candidate,
                valid_discovery_body("\n" + ("race-window-padding\n" * 4_000_000)),
            )
            advance = subprocess.Popen(
                [sys.executable, str(CLI), "advance", "--run", str(run),
                 "--approval", "human", "--date", "2026-08-19"],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            deadline = time.monotonic() + 20
            stopped = False
            while time.monotonic() < deadline and advance.poll() is None:
                if list(run.glob("approved/.discovery-r2.md.txn-*")):
                    os.kill(advance.pid, signal.SIGSTOP)
                    stopped = True
                    break
                time.sleep(0.0005)
            self.assertTrue(stopped, "failed to suspend first writer inside its transition")
            self.assertFalse(
                (run / ".atlas-control-transaction.json").exists(),
                "writer reached the journal before suspension; witness was not separating",
            )
            try:
                reject = run_cli("reject", "--run", run, "--reason", "withdrawn concurrently")
            finally:
                os.kill(advance.pid, signal.SIGCONT)
            advance_out, advance_err = advance.communicate(timeout=30)

            successes = int(advance.returncode == 0) + int(reject.returncode == 0)
            self.assertEqual(
                successes, 1,
                f"both stale-snapshot commands committed; advance={advance_out!r}/{advance_err!r}, "
                f"reject={reject.stdout!r}/{reject.stderr!r}",
            )

    def test_base_run_policy_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            tampered = yaml.safe_load((run / "run.yaml").read_text())
            tampered["gates"]["discovery"]["authority"] = "AUTO"
            (run / "run.yaml").write_text(yaml.safe_dump(tampered, sort_keys=False), encoding="utf-8")
            result = run_cli("advance", "--run", run, "--date", "2026-08-19")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("effective configuration hash", result.stderr)

    def test_base_run_byte_only_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            with (run / "run.yaml").open("a", encoding="utf-8") as handle:
                handle.write("# byte-only tamper\n")

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base run.yaml byte hash mismatch", result.stderr)

    def test_interrupted_multifile_transition_recovers_on_retry(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            env = os.environ.copy()
            env["ATLAS_CONTROL_TEST_CRASH_AFTER_REPLACES"] = "1"
            crashed = subprocess.run(
                [sys.executable, str(CLI), "advance", "--run", str(run),
                 "--approval", "human", "--date", "2026-08-19"],
                text=True, capture_output=True, env=env,
            )
            self.assertNotEqual(crashed.returncode, 0)
            self.assertTrue((run / ".atlas-control-transaction.json").exists())

            recovered = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
            )

            self.assertNotEqual(recovered.returncode, 0)
            self.assertIn("recovered an interrupted transaction", recovered.stderr)
            self.assertIn("no requested operation was executed", recovered.stderr)
            self.assertFalse((run / ".atlas-control-transaction.json").exists())
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            self.assertEqual((state["phase"], state["revision"]), ("spec", 2))
            self.assertEqual(len(list((run / "approved").glob("discovery-r*.md"))), 1)

    def test_recovery_never_reports_a_different_requested_command_as_complete(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            env = os.environ.copy()
            env["ATLAS_CONTROL_TEST_CRASH_AFTER_REPLACES"] = "1"
            crashed = subprocess.run(
                [sys.executable, str(CLI), "advance", "--run", str(run),
                 "--approval", "human", "--date", "2026-08-19"],
                text=True, capture_output=True, env=env,
            )
            self.assertNotEqual(crashed.returncode, 0)

            recovered = run_cli("reject", "--run", run, "--reason", "withdrawn")

            self.assertNotEqual(recovered.returncode, 0)
            self.assertIn("no requested operation was executed", recovered.stderr)
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            self.assertEqual(state["phase"], "spec")
            self.assertEqual(state["gates"]["discovery"], "HUMAN_APPROVED")
            self.assertIsNone(state["blocked_reason"])

    def test_advance_cannot_clear_an_unrelated_run_block(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run, status="BLOCKED", blocked_reason="unrelated hard block")
            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-19")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("run status is not PLANNING", result.stderr)

    def test_spec_advance_requires_approved_discovery_history(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            base = {
                "version": 1, "run": "demo", "opened": "2026-08-19",
                "stages": ["discovery", "spec", "program_design"],
                "gates": {
                    "discovery": {"authority": "HUMAN"},
                    "spec": {"authority": "HUMAN"},
                    "program_design": {"authority": "HUMAN"},
                },
                "repos": [{"repository": "fixture", "baseline": "abc1234"}],
            }
            (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
            write_frontmatter(run / "00-state.md", {
                "feature": "demo", "status": "PLANNING", "phase": "spec", "revision": 2,
                "effective_config_revision": 0, "effective_config_hash": canonical_hash(base),
                "base_run_sha256": hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest(),
                "gates": {"discovery": "PENDING", "spec": "PENDING", "program_design": "PENDING"},
                "approved_artifacts": {}, "accepted_amendments": {},
                "blocked_reason": None, "pending_amendment": None,
            })
            write_frontmatter(run / "20-spec.md", {
                "run": "demo", "version": 1, "status": "draft", "gate_ready": True,
                "approved": None, "approved_authority": None, "approved_copy": None,
                "approved_sha256": None, "supersedes": None, "amendment": None,
                "derived-from": "10-decisions.md", "effective_config_revision": 0,
            }, valid_spec_body())

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("predecessor discovery", result.stderr)

    def test_mark_stale_cannot_replace_an_unrelated_run_block(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run, status="BLOCKED", blocked_reason="unrelated hard block")
            candidate = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            candidate.update({"gate_ready": False, "intake_stale": True})
            write_frontmatter(run / "10-decisions.md", candidate)
            result = run_cli("mark-stale", "--run", run, "--reason", "new repository")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("run status is not PLANNING", result.stderr)
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            self.assertEqual(state["blocked_reason"], "unrelated hard block")

    def test_mark_stale_requires_run_state_and_candidate_identity(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            state["feature"] = "other-state"
            write_frontmatter(run / "00-state.md", state)
            candidate = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            candidate.update({"run": "other-candidate", "gate_ready": False, "intake_stale": True})
            write_frontmatter(run / "10-decisions.md", candidate)

            result = run_cli("mark-stale", "--run", run, "--reason", "new repository")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("state feature does not match run identity", result.stderr)

    def test_advance_rejects_candidate_for_a_different_run(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run, candidate_run="other-run")
            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-19")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate run identity", result.stderr)

    def test_advance_rejects_noncanonical_approval_date(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "not-a-date")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("approval date", result.stderr)

    def test_approved_directory_symlink_cannot_escape_run(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside_td:
            run = Path(td)
            outside = Path(outside_td)
            make_gate_fixture(run)
            (run / "approved").symlink_to(outside, target_is_directory=True)
            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-19")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("managed path uses a symlink", result.stderr)
            self.assertEqual(list(outside.iterdir()), [])

    def test_stale_intake_amendment_rejects_workflow_reclassification(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            base = {
                "version": 1,
                "run": "demo",
                "stages": ["discovery", "spec"],
                "gates": {"discovery": {"authority": "HUMAN"}, "spec": {"authority": "HUMAN"}},
                "repos": [{"repository": "old", "baseline": "abc1234"}],
            }
            (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
            write_frontmatter(run / "00-state.md", {
                "feature": "demo", "status": "BLOCKED", "phase": "discovery", "revision": 2,
                "effective_config_revision": 0, "effective_config_hash": canonical_hash(base),
                "base_run_sha256": hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest(),
                "repos": ["old"],
                "gates": {"discovery": "STALE", "spec": "PENDING"},
                "blocked_reason": "scope changed", "pending_amendment": "run-config-001",
            })
            amendment_dir = run / "amendments"
            amendment_dir.mkdir()
            (amendment_dir / "run-config-001.yaml").write_text(yaml.safe_dump({
                "version": 1,
                "amendment": "run-config-001",
                "applies_to": "run.yaml",
                "status": "accepted",
                "accepted": "2026-08-19",
                "reason": "reclassify workflow",
                "previous": None,
                "prior_effective_hash": canonical_hash(base),
                "changes": {"stages": ["spec"]},
                "effective_config_revision": 1,
            }, sort_keys=False), encoding="utf-8")

            result = run_cli("apply-amendment", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden fields: ['stages']", result.stderr)
            self.assertEqual(yaml.safe_load((run / "run.yaml").read_text()), base)

    def test_reopened_discovery_reapproves_and_preserves_both_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            approve_and_reopen(run)
            decisions = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            self.assertIn("approved_copy", decisions)
            self.assertIn("approved_sha256", decisions)
            self.assertIsNone(decisions["approved_copy"])
            self.assertIsNone(decisions["approved_sha256"])
            decisions["gate_ready"] = True
            write_frontmatter(run / "10-decisions.md", decisions, valid_discovery_body())

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-20"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            self.assertEqual(state["phase"], "spec")
            self.assertEqual(set(state["approved_artifacts"]), {
                "approved/discovery-r2.md", "approved/discovery-r4.md",
            })
            self.assertTrue((run / "approved" / "discovery-r2.md").is_file())
            self.assertTrue((run / "approved" / "discovery-r4.md").is_file())

    def test_reopened_discovery_rejects_a_forged_predecessor(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            approve_and_reopen(run)
            decisions = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            decisions.update({
                "approved_copy": None,
                "approved_sha256": None,
                "supersedes": "approved/discovery-r999.md",
                "gate_ready": True,
            })
            write_frontmatter(run / "10-decisions.md", decisions, valid_discovery_body())

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-20"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("supersede the active approved copy", result.stderr)

    def test_reopened_discovery_can_amend_stale_scope_and_reapprove(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            approve_and_reopen(run)
            decisions = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            decisions.update({
                "approved_copy": None,
                "approved_sha256": None,
                "intake_stale": True,
                "gate_ready": False,
            })
            write_frontmatter(run / "10-decisions.md", decisions, valid_discovery_body())

            stale = run_cli("mark-stale", "--run", run, "--reason", "new repository")
            self.assertEqual(stale.returncode, 0, stale.stderr)

            base = yaml.safe_load((run / "run.yaml").read_text())
            amendment_dir = run / "amendments"
            amendment_dir.mkdir()
            amendment = {
                "version": 1,
                "amendment": "run-config-001",
                "applies_to": "run.yaml",
                "status": "accepted",
                "accepted": "2026-08-20",
                "reason": "new repository",
                "previous": None,
                "prior_effective_hash": canonical_hash(base),
                "changes": {"repos": [{"repository": "new", "baseline": "def4567"}]},
                "effective_config_revision": 1,
            }
            (amendment_dir / "run-config-001.yaml").write_text(
                yaml.safe_dump(amendment, sort_keys=False), encoding="utf-8"
            )
            applied = run_cli("apply-amendment", "--run", run)
            self.assertEqual(applied.returncode, 0, applied.stderr)

            decisions = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            decisions.update({
                "intake_stale": False,
                "gate_ready": True,
                "effective_config_revision": 1,
                "repos": ["new"],
            })
            write_frontmatter(run / "10-decisions.md", decisions, valid_discovery_body())
            reapproved = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-20"
            )

            self.assertEqual(reapproved.returncode, 0, reapproved.stderr)
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            self.assertEqual((state["phase"], state["effective_config_revision"]), ("spec", 1))
            self.assertEqual(state["repos"], ["new"])

    def test_reopen_requires_approved_source_identity(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_gate_fixture(run)
            advanced = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
            )
            self.assertEqual(advanced.returncode, 0, advanced.stderr)
            decisions = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            decisions["run"] = "other-run"
            write_frontmatter(run / "10-decisions.md", decisions)

            result = run_cli(
                "reopen", "--run", run, "--to", "discovery", "--reason", "missing decision"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("predecessor discovery candidate has wrong run identity", result.stderr)

    def test_predraft_reopen_does_not_require_spec_file(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            base = {
                "version": 1, "run": "demo", "opened": "2026-08-19", "stages": ["discovery", "spec"],
                "gates": {"discovery": {"authority": "HUMAN"}, "spec": {"authority": "HUMAN"}},
                "repos": [{"repository": "fixture", "baseline": "abc1234"}],
            }
            (run / "run.yaml").write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
            write_frontmatter(run / "00-state.md", {
                "feature": "demo", "status": "PLANNING", "phase": "spec", "revision": 2,
                "effective_config_revision": 0, "effective_config_hash": canonical_hash(base),
                "base_run_sha256": hashlib.sha256((run / "run.yaml").read_bytes()).hexdigest(),
                "gates": {"discovery": "HUMAN_APPROVED", "spec": "PENDING"},
                "blocked_reason": None, "pending_amendment": None,
            })
            approved = run / "approved" / "discovery-r2.md"
            approved.parent.mkdir()
            write_frontmatter(approved, {"run": "demo", "status": "approved"}, "# Approved decisions\n")
            approved_hash = hashlib.sha256(approved.read_bytes()).hexdigest()
            state_data = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            state_data["approved_artifacts"] = {
                "approved/discovery-r2.md": {
                    "phase": "discovery", "sha256": approved_hash,
                    "authority": "HUMAN", "approved": "2026-08-19",
                }
            }
            write_frontmatter(run / "00-state.md", state_data)
            write_frontmatter(run / "10-decisions.md", {
                "run": "demo", "version": 1, "status": "approved", "gate_ready": True,
                "intake_stale": False, "approved": "2026-08-19",
                "approved_authority": "HUMAN",
                "approved_copy": "approved/discovery-r2.md",
                "approved_sha256": approved_hash,
                "effective_config_revision": 0,
            }, "# Decisions\n")

            result = run_cli("reopen", "--run", run, "--to", "discovery", "--reason", "missing behavior decision")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((run / "20-spec.md").exists())
            state = yaml.safe_load((run / "00-state.md").read_text().split("---", 2)[1])
            self.assertEqual(state["phase"], "discovery")
            self.assertEqual(state["approved_artifacts"]["approved/discovery-r2.md"]["sha256"], approved_hash)

            approved.write_text("tampered", encoding="utf-8")
            decisions = yaml.safe_load((run / "10-decisions.md").read_text().split("---", 2)[1])
            decisions["gate_ready"] = True
            write_frontmatter(run / "10-decisions.md", decisions)
            tamper_probe = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-19"
            )
            self.assertNotEqual(tamper_probe.returncode, 0)
            self.assertIn("approved artifact hash mismatch", tamper_probe.stderr)


if __name__ == "__main__":
    unittest.main()
