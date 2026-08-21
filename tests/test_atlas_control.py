import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_control.py"

ALL_PRD_IDS = "P-001, R-001, I-001, C-001, X-001"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        text=True,
        capture_output=True,
    )


def initialize_cli(path, *, device=None, inode=None):
    identity = os.stat(path, follow_symlinks=False)
    return run_cli(
        "initialize", "--run", path,
        "--prepared-device", identity.st_dev if device is None else device,
        "--prepared-inode", identity.st_ino if inode is None else inode,
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


def run_config(discovery="HUMAN"):
    gates = {
        "discovery": {"authority": discovery},
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
        "stages": ["discovery", "program_design"],
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


def decision_log_frontmatter(*, version=1):
    return {"run": "demo", "version": version}


def decision_log_body(decisions=None, retrospective_rows=None, cold_read_text=None):
    decisions = decisions or [
        {
            "id": "D-001",
            "status": "settled",
            "supersedes": "null",
            "chosen": "Completion must be externally observable.",
        }
    ]
    retrospective_rows = retrospective_rows if retrospective_rows is not None else [
        {"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""}
    ]
    decision_sections = []
    for item in decisions:
        decision_sections.append(
            f"""### {item['id']} — Decision

```yaml
id: {item['id']}
route: grill
findings: null
status: {item['status']}
decided: 2026-08-20
origin: accepted-recommendation
confidence: high
unblocked: []
blocked_by: []
supersedes: {item['supersedes']}
contribution: load-bearing
```

**Chosen:** {item['chosen']}
"""
        )
    rows = "\n".join(
        f"| {row['decision']} | {row['disposition']} | {row['prd_ids']} | {row['reason']} |"
        for row in retrospective_rows
    )
    cold_read_text = cold_read_text or """| Finding | Disposition |
|---|---|
| No unresolved contradictions found. | No action required. |"""
    return f"""# Decisions — Demo

## Problem test

Completion is not externally observable.

## Cold-read evidence

{cold_read_text}

## Open frontier

| Question | Route | Blocked by |
|---|---|---|

{''.join(decision_sections)}
## PRD alignment retrospective

| Decision | Disposition | PRD identifiers | Reason (required iff NO_NORMATIVE_EFFECT) |
|---|---|---|---|
{rows}
"""


def prd_frontmatter(decisions_path, *, version=1, ready=True, stale=False, cold_read="complete", revision=0):
    text = decisions_path.read_text(encoding="utf-8")
    raw, _ = text[4:].split("\n---\n", 1)
    decision_frontmatter = yaml.safe_load(raw)
    return {
        "run": "demo",
        "version": version,
        "status": "draft",
        "gate_ready": ready,
        "intake_stale": stale,
        "cold_read": cold_read,
        "effective_config_revision": revision,
        "opened": "2026-08-20",
        "repos": ["fixture"],
        "derived_from": {
            "artifact": "10-decisions.md",
            "version": decision_frontmatter["version"],
            "sha256": sha256(decisions_path),
        },
    }


def prd_body(*, derived_from="D-001", out_of_scope_from="D-001", open_questions="None.", problem="Completion is not externally observable."):
    return f"""# Product requirements — Demo

## Problem

{problem}

## Goals and outcomes

- Users can tell when the product finished work.

## Non-goals

- Internal design choices.

## Actors

- Operator

## Scenarios

### P-001 — Observe completion
**Current:** Completion is unclear.
**Target:** Completion is obvious.
**Acceptance:** An operator can tell when processing ends.
**Derived from:** {derived_from}

## Requirements

### R-001 — Observable completion
**Current:** Completion is not visible.
**Target:** Completion is visible.
**Acceptance:** A completion indication is observable.
**Derived from:** {derived_from}

## Invariants

### I-001 — Stable completion signal
**Rule:** Completion remains externally observable.
**Derived from:** {derived_from}

## Contracts and interfaces

### C-001 — Completion surface
**Contract:** The product boundary exposes completion.
**Derived from:** {derived_from}

## Edge and failure cases

### X-001 — Internal design remains downstream
**Case:** Internal design is excluded.
**Resolution:** Later stage.
**Derived from:** {out_of_scope_from}

## Observability

- Completion state is externally inspectable.

## Acceptance outcomes

- Users observe completion without internal knowledge.

## Open questions

{open_questions}
"""


def write_decisions(path, **kwargs):
    write_markdown(path / "10-decisions.md", decision_log_frontmatter(), decision_log_body(**kwargs))


def write_prd(path, *, version=1, ready=True, stale=False, cold_read="complete", revision=0, body_kwargs=None):
    decisions_path = path / "10-decisions.md"
    write_markdown(
        path / "20-prd.md",
        prd_frontmatter(
            decisions_path,
            version=version,
            ready=ready,
            stale=stale,
            cold_read=cold_read,
            revision=revision,
        ),
        prd_body(**(body_kwargs or {})),
    )


def write_prd_html(path, *, source="20-prd.md", source_sha=None, renderer_version="1.0.0"):
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="atlas-source" content="{source}">
  <meta name="atlas-source-sha256" content="{source_sha or sha256(path / '20-prd.md')}">
  <meta name="atlas-renderer-version" content="{renderer_version}">
</head>
<body><p>Living PRD</p></body>
</html>
"""
    (path / "20-prd.html").write_text(html, encoding="utf-8")


def write_discovery(path, *, version=1, ready=True, stale=False, cold_read="complete", revision=0, decisions=None, retrospective_rows=None, body_kwargs=None):
    write_decisions(path, decisions=decisions, retrospective_rows=retrospective_rows)
    write_prd(
        path,
        version=version,
        ready=ready,
        stale=stale,
        cold_read=cold_read,
        revision=revision,
        body_kwargs=body_kwargs,
    )
    write_prd_html(path)


def make_run(path, *, discovery="HUMAN"):
    config = run_config(discovery)
    (path / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    result = initialize_cli(path)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return config


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
    review = review_dir / f"product_closure-v{record['candidate_version']}.json"
    gaps = [] if verdict == "PASS" else [{
        "code": "semantic-consequence-unresolved",
        "artifact": "20-prd.md",
        "problem": "A consequence is unresolved",
        "resume_stage": "discovery",
        "resume_action": "repair the PRD and rerun product closure",
    }]
    review.write_text(json.dumps({
        "version": 1,
        "run": "demo",
        "stage": "product_closure",
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

            result = initialize_cli(run)

            self.assertEqual(result.returncode, 0, result.stderr)
            control = read_control(run)
            self.assertEqual((control["phase"], control["revision"]), ("discovery", 1))
            self.assertEqual(control["base_run_sha256"], sha256(run / "run.yaml"))
            self.assertEqual(control["acceptances"], {"discovery": None})
            self.assertEqual(control["gates"], {"discovery": "PENDING"})
            self.assertTrue((run / "00-state.md").is_file())

    def test_initialize_requires_authority_only_for_stage02_boundaries(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            config["stages"] = ["discovery", "program_design", "tickets", "execute", "final_review", "pr"]
            config["gates"]["tickets"] = {"authority": "AGENT_REVIEW"}
            config["recommendation"]["gates"] = config["gates"]
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = initialize_cli(run)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(read_control(run)["phase"], "discovery")

    def test_producer_readiness_claim_passes_read_only_check_but_is_not_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            before = (run / "control.json").read_bytes()

            result = run_cli("check", "--run", run)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["verdict"], "PASS")
            self.assertEqual(report["boundary"], "product_closure")
            self.assertEqual((run / "control.json").read_bytes(), before)
            self.assertEqual(read_control(run)["gates"]["discovery"], "PENDING")
            self.assertEqual(read_control(run)["acceptances"], {"discovery": None})

    def test_mechanical_check_does_not_grade_prose_semantics(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_decisions(run, decisions=[{
                "id": "D-001",
                "status": "settled",
                "supersedes": "null",
                "chosen": "Words exist but their meaning is intentionally not machine-graded.",
            }])
            write_prd(run, body_kwargs={"problem": "Words exist but their meaning is intentionally not machine-graded."})
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["verdict"], "PASS")

    def test_unsettled_decision_record_is_a_mechanical_gap(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run, decisions=[{
                "id": "D-001",
                "status": "open",
                "supersedes": "null",
                "chosen": "Completion must be externally observable.",
            }])

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertTrue(any("not settled or superseded" in item["problem"] for item in report["gaps"]))

    def test_discovery_requires_reviewable_cold_read_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            body = decision_log_body().replace(
                "## Cold-read evidence\n\n| Finding | Disposition |\n|---|---|\n| No unresolved contradictions found. | No action required. |\n\n",
                "",
            )
            write_markdown(run / "10-decisions.md", decision_log_frontmatter(), body)
            write_prd(run)
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(any(
                "Cold-read evidence" in item["problem"] for item in json.loads(result.stdout)["gaps"]
            ))

    def test_human_product_closure_transition_records_current_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)

            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-21")

            self.assertEqual(result.returncode, 0, result.stderr)
            control = read_control(run)
            self.assertEqual((control["phase"], control["revision"]), ("program_design", 2))
            self.assertEqual(control["gates"], {"discovery": "HUMAN_APPROVED"})
            self.assertEqual(set(control["acceptances"]), {"discovery"})
            self.assertEqual(control["acceptances"]["discovery"]["authority"], "HUMAN")
            self.assertEqual(control["acceptances"]["discovery"]["candidate_sha256"], sha256(run / "20-prd.md"))

            before_handoff = (run / "control.json").read_bytes()
            handoff = run_cli("check", "--run", run)
            self.assertNotEqual(handoff.returncode, 0)
            handoff_report = json.loads(handoff.stdout)
            self.assertEqual(handoff_report["verdict"], "BLOCKED")
            self.assertIn("outside the Stage 0–2 controller", handoff_report["gaps"][0]["problem"])
            self.assertEqual((run / "control.json").read_bytes(), before_handoff)

    def test_tampered_state_projection_is_ignored_for_legality(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            (run / "00-state.md").write_text("---\nphase: fabricated\nrevision: 999\n---\n", encoding="utf-8")

            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-20")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(read_control(run)["phase"], "program_design")

    def test_agent_review_pass_is_bound_to_candidate_and_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
            }
            review = write_review(run, candidate)

            result = run_cli(
                "advance", "--run", run, "--review", review.relative_to(run), "--date", "2026-08-20"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            record = read_control(run)["acceptances"]["discovery"]
            self.assertEqual(record["authority"], "AGENT_REVIEW")
            self.assertEqual(record["review_reference"], "reviews/product_closure-v1.json")
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
                    "candidate_sha256": sha256(run / "20-prd.md"),
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

    def test_agent_review_is_bound_to_boundary_run_and_gap_schema(self):
        for case in ("wrong-run", "wrong-stage", "missing-code", "blank-resume-action"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                make_run(run, discovery="AGENT_REVIEW")
                write_discovery(run)
                candidate = {
                    "stage": "discovery",
                    "candidate_version": 1,
                    "candidate_sha256": sha256(run / "20-prd.md"),
                }
                review = write_review(
                    run,
                    candidate,
                    verdict="BLOCKED" if case in {"missing-code", "blank-resume-action"} else "PASS",
                )
                data = json.loads(review.read_text(encoding="utf-8"))
                if case == "wrong-run":
                    data["run"] = "another-run"
                elif case == "wrong-stage":
                    data["stage"] = "discovery"
                elif case == "missing-code":
                    data["gaps"][0].pop("code")
                else:
                    data["gaps"][0]["resume_action"] = "   "
                review.write_text(json.dumps(data) + "\n", encoding="utf-8")

                result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

                self.assertNotEqual(result.returncode, 0)
                expected = "stage/version is invalid" if case in {"wrong-run", "wrong-stage"} else "gaps are malformed"
                self.assertIn(expected, result.stderr)
                self.assertEqual(read_control(run)["revision"], 1)

    def test_auto_remains_unavailable_for_product_closure_boundary(self):
        for authority, expected in (("AUTO", False), ("BOGUS", False), ("HUMAN", True), ("AGENT_REVIEW", True)):
            with self.subTest(authority=authority), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = run_config(discovery=authority)
                (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

                result = initialize_cli(run)

                self.assertEqual(result.returncode == 0, expected, result.stderr)
                if not expected:
                    self.assertIn("AGENT_REVIEW or HUMAN", result.stderr)

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
            self.assertEqual(control["acceptances"], {"discovery": None})

    def test_initialize_product_closure_run_uses_only_discovery_gate_and_acceptance_slot(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = initialize_cli(run)

            self.assertEqual(result.returncode, 0, result.stderr)
            control = read_control(run)
            self.assertEqual(control["phase"], "discovery")
            self.assertEqual(control["gates"], {"discovery": "PENDING"})
            self.assertEqual(control["acceptances"], {"discovery": None})

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            config["gates"] = {"program_design": {"authority": "HUMAN"}}
            config["recommendation"]["gates"] = config["gates"]
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            blocked = initialize_cli(run)

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("discovery gate must exist exactly when discovery is selected", blocked.stderr)

    def test_product_closure_uses_prd_candidate_without_requiring_spec_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)

            result = run_cli("check", "--run", run)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["stage"], "discovery")
            self.assertEqual(report["boundary"], "product_closure")
            self.assertEqual(report["candidate_version"], 1)
            self.assertEqual(report["candidate_sha256"], sha256(run / "20-prd.md"))
            self.assertFalse((run / "20-spec.md").exists())

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_decisions(run)
            write_prd_html(run, source_sha="0" * 64)

            blocked = run_cli("check", "--run", run)

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("20-prd.md", blocked.stdout)

    def test_product_closure_blocked_review_preserves_lifecycle_state(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            review_dir = run / "reviews"
            review_dir.mkdir()
            review = review_dir / "product_closure-v1.json"
            review.write_text(json.dumps({
                "version": 1,
                "run": "demo",
                "stage": "product_closure",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
                "verdict": "BLOCKED",
                "gaps": [{
                    "code": "prd-omits-observable-outcome",
                    "artifact": "20-prd.md",
                    "problem": "A product consequence is understated.",
                    "resume_stage": "discovery",
                    "resume_action": "repair the cited PRD obligation and rerun closure",
                }],
            }, indent=2) + "\n", encoding="utf-8")
            before = (run / "control.json").read_bytes()

            result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((run / "control.json").read_bytes(), before)
            self.assertEqual(read_control(run)["phase"], "discovery")
            self.assertEqual(read_control(run)["gates"]["discovery"], "PENDING")

    def test_product_closure_review_must_bind_current_prd_and_records_discovery_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            review_dir = run / "reviews"
            review_dir.mkdir()
            wrong = review_dir / "wrong.json"
            wrong.write_text(json.dumps({
                "version": 1,
                "run": "demo",
                "stage": "product_closure",
                "candidate_version": 2,
                "candidate_sha256": "0" * 64,
                "verdict": "PASS",
                "gaps": [],
            }, indent=2) + "\n", encoding="utf-8")

            rejected = run_cli("advance", "--run", run, "--review", wrong.relative_to(run))

            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(read_control(run)["acceptances"], {"discovery": None})

            accepted = review_dir / "product_closure-v1.json"
            accepted.write_text(json.dumps({
                "version": 1,
                "run": "demo",
                "stage": "product_closure",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
                "verdict": "PASS",
                "gaps": [],
            }, indent=2) + "\n", encoding="utf-8")

            result = run_cli(
                "advance", "--run", run, "--review", accepted.relative_to(run), "--date", "2026-08-20"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            control = read_control(run)
            self.assertEqual(control["phase"], "program_design")
            self.assertEqual(control["gates"], {"discovery": "AGENT_APPROVED"})
            self.assertEqual(set(control["acceptances"]), {"discovery"})
            self.assertEqual(control["acceptances"]["discovery"]["authority"], "AGENT_REVIEW")
            self.assertEqual(control["acceptances"]["discovery"]["candidate_sha256"], sha256(run / "20-prd.md"))
            self.assertEqual(
                control["acceptances"]["discovery"]["review_reference"],
                "reviews/product_closure-v1.json",
            )


if __name__ == "__main__":
    unittest.main()
