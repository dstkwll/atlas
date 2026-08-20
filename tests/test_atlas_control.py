import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_control.py"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        text=True,
        capture_output=True,
    )


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_control(run):
    return json.loads((run / "control.json").read_text(encoding="utf-8"))


def write_markdown(path, frontmatter, body):
    path.write_text(
        "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body,
        encoding="utf-8",
    )


def run_config(discovery="HUMAN", spec="HUMAN"):
    gates = {
        "discovery": {"authority": discovery},
        "spec": {"authority": spec},
        "program_design": {"authority": "HUMAN"},
    }
    return {
        "version": 1,
        "run": "demo",
        "opened": "2026-08-20",
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
        "stages": ["discovery", "spec", "program_design"],
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


def discovery_body():
    return """# Decisions — Demo

## Problem test

Completion is not observable.

## Cold-read evidence

A fresh baseline read found no conflicting behavior; the settled decision below dispositions that finding.

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

### D-001 — Should completion be observable?

```yaml
id: D-001
route: grill
findings: null
status: settled
decided: 2026-08-20
origin: accepted-recommendation
confidence: high
unblocked: []
blocked_by: []
supersedes: null
contribution: load-bearing
```

**Chosen:** Completion must be externally observable.
"""


def discovery_frontmatter(*, version=1, ready=True, stale=False, repos=None, revision=0):
    return {
        "run": "demo",
        "version": version,
        "status": "draft",
        "gate_ready": ready,
        "intake_stale": stale,
        "cold_read": "complete",
        "effective_config_revision": revision,
        "opened": "2026-08-20",
        "repos": repos or ["fixture"],
    }


def spec_body():
    return """# Spec — Demo

## Problem

Completion is not externally observable.

## Requirements

### R-001 — Observable completion
**Current:** Completion is not visible.
**Target:** Completion is visible.
**Acceptance:** A completion indication is observable.
**Derived from:** D-001

## Prohibitions

None.

## Constraints

None.

## Invariants

None.

## Out of scope

| ID | Excluded | Why | Derived from |
|---|---|---|---|
| X-001 | Internal design | Later stage | D-001 |

## Edge coverage

| Edge | Category | Resolution |
|---|---|---|
| exact boundary | boundary | R-001 |

## Open questions

None.
"""


def spec_frontmatter(discovery_record, *, version=1, ready=True):
    return {
        "run": "demo",
        "version": version,
        "status": "draft",
        "gate_ready": ready,
        "effective_config_revision": 0,
        "derived_from": {
            "stage": "discovery",
            "candidate_version": discovery_record["candidate_version"],
            "candidate_sha256": discovery_record["candidate_sha256"],
        },
    }


def make_run(path, *, discovery="HUMAN", spec="HUMAN"):
    config = run_config(discovery, spec)
    (path / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    result = run_cli("initialize", "--run", path)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return config


def write_discovery(path, **kwargs):
    write_markdown(path / "10-decisions.md", discovery_frontmatter(**kwargs), discovery_body())


def advance_discovery(path, *, review=None):
    args = ["advance", "--run", path, "--date", "2026-08-20"]
    if review is None:
        args += ["--approval", "human"]
    else:
        args += ["--review", review]
    result = run_cli(*args)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return read_control(path)["acceptances"]["discovery"]


def write_review(path, record, verdict="PASS", *, candidate_sha256=None):
    review_dir = path / "reviews"
    review_dir.mkdir(exist_ok=True)
    review = review_dir / f"{record['stage']}-v{record['candidate_version']}.json"
    gaps = [] if verdict == "PASS" else [{
        "code": "semantic-consequence-unresolved",
        "artifact": "10-decisions.md",
        "problem": "A consequence is unresolved",
        "resume_stage": "discovery",
        "resume_action": "resolve D-002 and rerun review",
    }]
    review.write_text(json.dumps({
        "version": 1,
        "run": "demo",
        "stage": record["stage"],
        "candidate_version": record["candidate_version"],
        "candidate_sha256": candidate_sha256 or record["candidate_sha256"],
        "verdict": verdict,
        "gaps": gaps,
    }, indent=2) + "\n", encoding="utf-8")
    return review


class AtlasControlTests(unittest.TestCase):
    def test_initialize_creates_machine_authority_and_projection(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = run_cli("initialize", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)
            control = read_control(run)
            self.assertEqual((control["phase"], control["revision"]), ("discovery", 1))
            self.assertEqual(control["base_run_sha256"], sha256(run / "run.yaml"))
            self.assertEqual(control["acceptances"], {"discovery": None, "spec": None})
            self.assertTrue((run / "00-state.md").is_file())

    def test_initialize_requires_authority_only_for_stage02_boundaries(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            config["stages"] = [
                "discovery", "spec", "program_design", "tickets", "execute", "final_review", "pr"
            ]
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = run_cli("initialize", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(read_control(run)["phase"], "discovery")

    def test_producer_readiness_claim_passes_read_only_check_but_is_not_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            before = (run / "control.json").read_bytes()

            result = run_cli("check", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["verdict"], "PASS")
            self.assertEqual((run / "control.json").read_bytes(), before)
            self.assertEqual(read_control(run)["gates"]["discovery"], "PENDING")
            self.assertEqual(read_control(run)["acceptances"], {"discovery": None, "spec": None})

    def test_mechanical_check_does_not_grade_prose_semantics(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_markdown(
                run / "10-decisions.md",
                discovery_frontmatter(),
                discovery_body().replace(
                    "Completion must be externally observable.",
                    "Words exist but their meaning is intentionally not machine-graded.",
                ),
            )

            result = run_cli("check", "--run", run)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["verdict"], "PASS")

    def test_unsettled_decision_record_is_a_mechanical_gap(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_markdown(
                run / "10-decisions.md",
                discovery_frontmatter(),
                discovery_body().replace("status: settled", "status: open"),
            )

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertTrue(any("not settled" in item["problem"] for item in report["gaps"]))

    def test_discovery_requires_reviewable_cold_read_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            body = re.sub(r"(?ms)^## Cold-read evidence\s*$.*?(?=^## )", "", discovery_body())
            write_markdown(run / "10-decisions.md", discovery_frontmatter(), body)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(any(
                "Cold-read evidence" in item["problem"] for item in json.loads(result.stdout)["gaps"]
            ))

    def test_human_discovery_and_spec_transitions_record_current_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            discovery = advance_discovery(run)
            write_markdown(run / "20-spec.md", spec_frontmatter(discovery), spec_body())

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-21"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            control = read_control(run)
            self.assertEqual((control["phase"], control["revision"]), ("program_design", 3))
            self.assertEqual(set(control["acceptances"]), {"discovery", "spec"})
            self.assertEqual(
                [control["acceptances"][stage]["authority"] for stage in ("discovery", "spec")],
                ["HUMAN", "HUMAN"],
            )
            self.assertEqual(discovery["candidate_sha256"], sha256(run / "10-decisions.md"))

    def test_spec_requires_normative_identifier_and_rejects_explicit_blocker(self):
        variants = {
            "missing-normative-id": spec_body().replace("### R-001 — Observable completion", "Observable completion"),
            "explicit-blocker": spec_body().replace("## Open questions\n\nNone.", "## Open questions\n\nBlocking: output encoding is unresolved."),
        }
        for name, body in variants.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                make_run(run)
                write_discovery(run)
                discovery = advance_discovery(run)
                write_markdown(run / "20-spec.md", spec_frontmatter(discovery), body)

                result = run_cli("check", "--run", run)

                self.assertNotEqual(result.returncode, 0)

    def test_tampered_state_projection_is_ignored_for_legality(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            (run / "00-state.md").write_text("---\nphase: fabricated\nrevision: 999\n---\n", encoding="utf-8")

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-20"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(read_control(run)["phase"], "spec")

    def test_agent_review_pass_is_bound_to_candidate_and_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "10-decisions.md"),
            }
            review = write_review(run, candidate)

            result = run_cli(
                "advance", "--run", run, "--review", review.relative_to(run),
                "--date", "2026-08-20",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            record = read_control(run)["acceptances"]["discovery"]
            self.assertEqual(record["authority"], "AGENT_REVIEW")
            self.assertEqual(record["review_reference"], "reviews/discovery-v1.json")
            self.assertEqual(record["review_sha256"], sha256(review))
            self.assertEqual(read_control(run)["gates"]["discovery"], "AGENT_APPROVED")

    def test_agent_review_wrong_hash_and_blocked_verdict_cannot_advance(self):
        for case in ("wrong-hash", "blocked"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                make_run(run, discovery="AGENT_REVIEW")
                write_discovery(run)
                candidate = {
                    "stage": "discovery",
                    "candidate_version": 1,
                    "candidate_sha256": sha256(run / "10-decisions.md"),
                }
                review = write_review(
                    run,
                    candidate,
                    verdict="BLOCKED" if case == "blocked" else "PASS",
                    candidate_sha256="0" * 64 if case == "wrong-hash" else None,
                )
                before = (run / "control.json").read_bytes()

                result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((run / "control.json").read_bytes(), before)

    def test_agent_review_is_bound_to_run_and_gap_schema(self):
        for case in ("wrong-run", "missing-code", "blank-resume-action"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                make_run(run, discovery="AGENT_REVIEW")
                write_discovery(run)
                candidate = {
                    "stage": "discovery",
                    "candidate_version": 1,
                    "candidate_sha256": sha256(run / "10-decisions.md"),
                }
                review = write_review(
                    run,
                    candidate,
                    verdict="BLOCKED" if case != "wrong-run" else "PASS",
                )
                data = json.loads(review.read_text(encoding="utf-8"))
                if case == "wrong-run":
                    data["run"] = "another-run"
                elif case == "missing-code":
                    data["gaps"][0].pop("code")
                else:
                    data["gaps"][0]["resume_action"] = "   "
                review.write_text(json.dumps(data) + "\n", encoding="utf-8")

                result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

                self.assertNotEqual(result.returncode, 0)
                expected = "stage/version is invalid" if case == "wrong-run" else "gaps are malformed"
                self.assertIn(expected, result.stderr)
                self.assertEqual(read_control(run)["revision"], 1)

    def test_auto_is_unavailable_for_discovery_and_spec(self):
        for stage in ("discovery", "spec"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = run_config("AUTO" if stage == "discovery" else "HUMAN", "AUTO")
                (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

                result = run_cli("initialize", "--run", run)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("AGENT_REVIEW or HUMAN", result.stderr)
                self.assertFalse((run / "control.json").exists())

    def test_unknown_semantic_boundary_authority_is_rejected_at_initialization(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config(discovery="UNSUPPORTED")
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = run_cli("initialize", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AGENT_REVIEW or HUMAN", result.stderr)
            self.assertFalse((run / "control.json").exists())

    def test_reopen_preserves_acceptance_and_requires_next_candidate_version(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            accepted = advance_discovery(run)

            reopened = run_cli(
                "reopen", "--run", run, "--to", "discovery", "--reason", "spec exposed a gap"
            )
            self.assertEqual(reopened.returncode, 0, reopened.stderr)
            control = read_control(run)
            self.assertEqual(control["acceptances"]["discovery"], accepted)
            self.assertEqual(control["gates"]["discovery"], "STALE")

            old_version = run_cli("check", "--run", run)
            self.assertNotEqual(old_version.returncode, 0)
            self.assertIn("version 2", old_version.stdout)

            write_discovery(run, version=2)
            passed = run_cli("check", "--run", run)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            self.assertNotEqual(sha256(run / "10-decisions.md"), accepted["candidate_sha256"])

            reaccepted = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-21"
            )
            self.assertEqual(reaccepted.returncode, 0, reaccepted.stderr)
            current = read_control(run)["acceptances"]["discovery"]
            self.assertEqual(current["candidate_version"], 2)
            self.assertNotEqual(current["candidate_sha256"], accepted["candidate_sha256"])

    def test_reject_records_configured_authority_outcome_without_accepting(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)

            result = run_cli("reject", "--run", run, "--reason", "human declined")

            self.assertEqual(result.returncode, 0, result.stderr)
            control = read_control(run)
            self.assertEqual(control["gates"]["discovery"], "REJECTED")
            self.assertEqual(control["blocked_reason"], "human declined")
            self.assertEqual(control["acceptances"], {"discovery": None, "spec": None})


if __name__ == "__main__":
    unittest.main()
