import json
import os
import tempfile
import unittest
from pathlib import Path

import yaml

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None

from tests.test_atlas_control import (
    CLI,
    advance_discovery,
    discovery_frontmatter,
    discovery_body,
    make_run,
    read_control,
    run_cli,
    sha256,
    write_discovery,
    write_markdown,
)


class AtlasControlHardeningTests(unittest.TestCase):
    def test_control_transition_replaces_one_authoritative_file_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            run_before = (run / "run.yaml").read_bytes()
            candidate_before = (run / "10-decisions.md").read_bytes()
            inode_before = (run / "control.json").stat().st_ino

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-20"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual((run / "control.json").stat().st_ino, inode_before)
            self.assertEqual((run / "run.yaml").read_bytes(), run_before)
            self.assertEqual((run / "10-decisions.md").read_bytes(), candidate_before)
            self.assertFalse((run / ".atlas-control-transaction.json").exists())
            self.assertEqual(list(run.glob(".*.txn-*")), [])

    @unittest.skipUnless(fcntl is not None, "requires POSIX file locking")
    def test_concurrent_writer_is_excluded_before_it_can_commit(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            lock_path = run / ".atlas-control.lock"
            lock_api = fcntl
            assert lock_api is not None
            with lock_path.open("a+") as held:
                lock_api.flock(held.fileno(), lock_api.LOCK_EX | lock_api.LOCK_NB)
                before = (run / "control.json").read_bytes()

                result = run_cli(
                    "advance", "--run", run, "--approval", "human", "--date", "2026-08-20"
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("another atlas-control process", result.stderr)
                self.assertEqual((run / "control.json").read_bytes(), before)

    def test_byte_level_run_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            with (run / "run.yaml").open("a", encoding="utf-8") as handle:
                handle.write("# byte-only tamper\n")

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-20"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base run.yaml byte hash mismatch", result.stderr)
            self.assertEqual(read_control(run)["revision"], 1)

    def test_malformed_authoritative_control_state_fails_closed(self):
        cases = {
            "bad-acceptance": lambda state: state["acceptances"].__setitem__(
                "discovery",
                {
                    "candidate_version": "1",
                    "candidate_sha256": "not-a-hash",
                    "authority": "HUMAN",
                    "accepted": "not-a-date",
                    "review_reference": None,
                    "review_sha256": None,
                },
            ),
            "bad-gates": lambda state: state["gates"].__setitem__("unexpected", "PENDING"),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                make_run(run)
                state = read_control(run)
                mutate(state)
                (run / "control.json").write_text(json.dumps(state) + "\n", encoding="utf-8")

                result = run_cli("check", "--run", run)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("control.json", result.stderr)

    def test_authoritative_control_rejects_impossible_gate_acceptance_combinations(self):
        accepted = {
            "candidate_version": 1,
            "candidate_sha256": "0" * 64,
            "authority": "HUMAN",
            "accepted": "2026-08-20",
            "review_reference": None,
            "review_sha256": None,
        }
        cases = {
            "binding-while-pending": lambda state: state["acceptances"].__setitem__("discovery", accepted),
            "approved-without-binding": lambda state: state["gates"].__setitem__("discovery", "HUMAN_APPROVED"),
            "accepted-current-phase": lambda state: (
                state["acceptances"].__setitem__("discovery", accepted),
                state["gates"].__setitem__("discovery", "HUMAN_APPROVED"),
            ),
            "authority-gate-mismatch": lambda state: (
                state["acceptances"].__setitem__("discovery", accepted),
                state["gates"].__setitem__("discovery", "AGENT_APPROVED"),
                state.__setitem__("phase", "spec"),
            ),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                make_run(run)
                state = read_control(run)
                mutate(state)
                (run / "control.json").write_text(json.dumps(state) + "\n", encoding="utf-8")

                result = run_cli("check", "--run", run)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("control.json", result.stderr)

    def test_blocked_agent_review_leaves_gate_pending_for_repair(self):
        from tests.test_atlas_control import write_review

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "10-decisions.md"),
            }
            review = write_review(run, candidate, verdict="BLOCKED")

            result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

            self.assertNotEqual(result.returncode, 0)
            control = read_control(run)
            self.assertEqual(control["status"], "PLANNING")
            self.assertEqual(control["gates"]["discovery"], "PENDING")
            self.assertIsNone(control["blocked_reason"])
            self.assertIsNone(control["acceptances"]["discovery"])

    def test_minimal_ordered_amendment_updates_count_and_effective_hash(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_markdown(
                run / "10-decisions.md",
                discovery_frontmatter(ready=False, stale=True),
                discovery_body(),
            )
            marked = run_cli("mark-stale", "--run", run, "--reason", "baseline corrected")
            self.assertEqual(marked.returncode, 0, marked.stderr)
            old_hash = read_control(run)["effective_config_hash"]

            amendments = run / "amendments"
            amendments.mkdir()
            write_markdown(amendments / "001-repository-baseline.md", {
                "version": 1,
                "amendment": 1,
                "applies_to": "run.yaml",
                "status": "accepted",
                "accepted": "2026-08-20",
                "reason": "Discovery found the preserved baseline was wrong",
                "changes": {"repos": [{"repository": "fixture", "baseline": "def4567"}]},
            }, "# Repository baseline correction\n")

            result = run_cli("apply-amendment", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)
            control = read_control(run)
            self.assertEqual(control["accepted_amendment_count"], 1)
            self.assertEqual(control["effective_config_revision"], 1)
            self.assertNotEqual(control["effective_config_hash"], old_hash)
            self.assertNotIn("accepted_amendments", control)
            self.assertEqual(control["gates"]["discovery"], "PENDING")

            write_markdown(
                run / "10-decisions.md",
                discovery_frontmatter(repos=["fixture"], revision=1),
                discovery_body(),
            )
            self.assertEqual(run_cli("check", "--run", run).returncode, 0)

    def test_amendments_must_be_contiguous_and_only_correct_repos(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_markdown(
                run / "10-decisions.md",
                discovery_frontmatter(ready=False, stale=True),
                discovery_body(),
            )
            self.assertEqual(
                run_cli("mark-stale", "--run", run, "--reason", "scope corrected").returncode,
                0,
            )
            amendments = run / "amendments"
            amendments.mkdir()
            write_markdown(amendments / "002-wrong.md", {
                "version": 1,
                "amendment": 2,
                "applies_to": "run.yaml",
                "status": "accepted",
                "accepted": "2026-08-20",
                "reason": "wrong sequence",
                "changes": {"repos": [{"repository": "fixture", "baseline": "def4567"}]},
            }, "# Wrong\n")

            result = run_cli("apply-amendment", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("001", result.stderr)
            self.assertEqual(read_control(run)["accepted_amendment_count"], 0)

    def test_no_approved_receipt_or_transaction_artifacts_are_created(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)

            advance_discovery(run)

            self.assertFalse((run / "approved").exists())
            self.assertFalse((run / ".atlas-control-transaction.json").exists())
            self.assertEqual(list(run.glob("*receipt*")), [])
            self.assertEqual(list(run.glob("*.jsonl")), [])
            self.assertEqual(
                sorted(path.name for path in run.iterdir()),
                [".atlas-control.lock", "00-state.md", "10-decisions.md", "control.json", "run.yaml"],
            )

    def test_projection_failure_cannot_fail_an_authoritative_transition(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside_td:
            run = Path(td)
            outside = Path(outside_td) / "state.md"
            outside.write_text("outside must not change\n", encoding="utf-8")
            make_run(run)
            write_discovery(run)
            (run / "00-state.md").unlink()
            (run / "00-state.md").symlink_to(outside)

            result = run_cli(
                "advance", "--run", run, "--approval", "human", "--date", "2026-08-20"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(read_control(run)["phase"], "spec")
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside must not change\n")
            self.assertIn("projection was not regenerated", result.stderr)

    def test_spec_check_binds_to_accepted_discovery_hash(self):
        from tests.test_atlas_control import spec_body, spec_frontmatter

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            accepted = advance_discovery(run)
            write_markdown(run / "20-spec.md", spec_frontmatter(accepted), spec_body())
            with (run / "10-decisions.md").open("a", encoding="utf-8") as handle:
                handle.write("\nunauthorized mutation\n")

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertEqual(report["verdict"], "BLOCKED")
            self.assertTrue(any("accepted discovery" in gap["problem"] for gap in report["gaps"]))


if __name__ == "__main__":
    unittest.main()
