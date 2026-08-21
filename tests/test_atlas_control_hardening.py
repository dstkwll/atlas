import json
import runpy
import tempfile
import unittest
from pathlib import Path

import yaml

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None

from tests.test_atlas_control import (
    ALL_PRD_IDS,
    advance_discovery,
    decision_log_body,
    decision_log_frontmatter,
    make_run,
    initialize_cli,
    prd_body,
    prd_frontmatter,
    read_control,
    run_cli,
    run_config,
    sha256,
    write_decisions,
    write_discovery,
    write_markdown,
    write_prd,
    write_prd_html,
    write_review,
)


class AtlasControlHardeningTests(unittest.TestCase):
    def initialize_product_closure_run(self, run: Path, *, authority: str = "HUMAN") -> None:
        (run / "run.yaml").write_text(
            yaml.safe_dump(run_config(discovery=authority), sort_keys=False),
            encoding="utf-8",
        )
        result = initialize_cli(run)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_resolve_run_path_rejects_unsafe_slugs_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "planning"
            root.mkdir()

            safe = run_cli("resolve-run-path", "--planning-root", root, "--slug", "offline-mode")
            self.assertEqual(safe.returncode, 0, safe.stderr)
            prepared = json.loads(safe.stdout)
            self.assertEqual(Path(prepared["path"]), (root / "offline-mode").resolve())
            self.assertGreaterEqual(prepared["device"], 0)
            self.assertGreater(prepared["inode"], 0)
            self.assertTrue((root / "offline-mode").is_dir())

            for slug in ("../escape", "/tmp/escape", "a/b", "a\\b", "C:\\escape", ".", "..", "-bad", "bad-", "Bad", "bad--slug"):
                with self.subTest(slug=slug):
                    result = run_cli("resolve-run-path", "--planning-root", root, "--slug", slug)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("slug", result.stderr.lower())

            root_link = base / "planning-link"
            root_link.symlink_to(root, target_is_directory=True)
            linked_root = run_cli("resolve-run-path", "--planning-root", root_link, "--slug", "safe-run")
            self.assertNotEqual(linked_root.returncode, 0)
            self.assertIn("symlink", linked_root.stderr.lower())

            target = root / "symlinked-run"
            target.symlink_to(base / "outside", target_is_directory=True)
            escaped = run_cli("resolve-run-path", "--planning-root", root, "--slug", "symlinked-run")
            self.assertNotEqual(escaped.returncode, 0)
            self.assertIn("symlink", escaped.stderr.lower())

    def test_initialize_rejects_target_replaced_by_symlink_after_resolution(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "planning"
            root.mkdir()
            target = root / "swap-run"
            outside = base / "outside"
            outside.mkdir()

            resolved = run_cli("resolve-run-path", "--planning-root", root, "--slug", "swap-run")
            self.assertEqual(resolved.returncode, 0, resolved.stderr)
            prepared = json.loads(resolved.stdout)
            target.rmdir()
            target.symlink_to(outside, target_is_directory=True)

            config = run_config()
            config["run"] = "swap-run"
            config["run_path"] = "swap-run"
            (outside / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = initialize_cli(
                target,
                device=prepared["device"],
                inode=prepared["inode"],
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stderr.lower())
            self.assertFalse((outside / "control.json").exists())

    def test_initialize_rejects_target_replaced_by_a_different_real_directory(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = base / "planning"
            root.mkdir()
            target = root / "swap-run"

            resolved = run_cli("resolve-run-path", "--planning-root", root, "--slug", "swap-run")
            self.assertEqual(resolved.returncode, 0, resolved.stderr)
            prepared = json.loads(resolved.stdout)
            target.rename(root / "original-run")
            target.mkdir()

            config = run_config()
            config["run"] = "swap-run"
            config["run_path"] = "swap-run"
            (target / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = initialize_cli(
                target,
                device=prepared["device"],
                inode=prepared["inode"],
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("prepared directory identity", result.stderr.lower())
            self.assertFalse((target / "control.json").exists())

    def test_initialize_requires_prepared_directory_identity(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            (run / "run.yaml").write_text(yaml.safe_dump(run_config(), sort_keys=False), encoding="utf-8")

            result = run_cli("initialize", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("prepared-device", result.stderr)
            self.assertFalse((run / "control.json").exists())

    def test_initialize_rejects_an_unsafe_run_slug(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            config["run"] = "../escape"
            config["run_path"] = "../escape"
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = initialize_cli(run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("slug", result.stderr.lower())
            self.assertFalse((run / "control.json").exists())

    def write_product_closure_candidate(self, run: Path, *, decisions=None, retrospective_rows=None, body_kwargs=None) -> None:
        write_markdown(
            run / "10-decisions.md",
            decision_log_frontmatter(),
            decision_log_body(decisions=decisions, retrospective_rows=retrospective_rows),
        )
        write_markdown(
            run / "20-prd.md",
            prd_frontmatter(run / "10-decisions.md"),
            prd_body(**(body_kwargs or {})),
        )
        write_prd_html(run)

    def test_control_transition_replaces_one_authoritative_file_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            run_before = (run / "run.yaml").read_bytes()
            candidate_before = (run / "20-prd.md").read_bytes()
            inode_before = (run / "control.json").stat().st_ino

            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-20")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual((run / "control.json").stat().st_ino, inode_before)
            self.assertEqual((run / "run.yaml").read_bytes(), run_before)
            self.assertEqual((run / "20-prd.md").read_bytes(), candidate_before)
            self.assertFalse((run / ".atlas-control-transaction.json").exists())
            self.assertEqual(list(run.glob(".*.txn-*")), [])

    @unittest.skipUnless(fcntl is not None, "requires POSIX file locking")
    def test_concurrent_writer_is_excluded_before_it_can_commit(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            lock_path = run / ".atlas-control.lock"
            assert fcntl is not None
            with lock_path.open("a+") as held:
                fcntl.flock(held.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                before = (run / "control.json").read_bytes()

                result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-20")

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

            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-20")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base run.yaml byte hash mismatch", result.stderr)
            self.assertEqual(read_control(run)["revision"], 1)

    def test_initialize_rejects_legacy_or_malformed_stage_orders(self):
        cases = {
            "legacy-spec": ["discovery", "spec", "program_design"],
            "non-string": ["discovery", 7],
        }
        for name, stages in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = run_config()
                config["stages"] = stages
                config["gates"] = {
                    str(stage): {"authority": "HUMAN"} for stage in stages
                }
                config["recommendation"]["gates"] = config["gates"]
                (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

                result = initialize_cli(run)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("stages", result.stderr)
                self.assertFalse((run / "control.json").exists())

    def test_initialize_supports_selected_or_omitted_discovery(self):
        cases = {
            "selected": {
                "stages": ["discovery", "program_design"],
                "gates": {"discovery": "PENDING"},
                "acceptances": {"discovery": None},
                "phase": "discovery",
            },
            "omitted": {
                "stages": ["program_design", "tickets"],
                "gates": {},
                "acceptances": {},
                "phase": "program_design",
            },
        }
        for name, expected in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = run_config()
                config["stages"] = expected["stages"]
                if name == "omitted":
                    config["gates"].pop("discovery")
                config["recommendation"]["gates"] = config["gates"]
                (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

                initialized = initialize_cli(run)

                self.assertEqual(initialized.returncode, 0, initialized.stderr)
                control = read_control(run)
                self.assertEqual(control["phase"], expected["phase"])
                self.assertEqual(control["gates"], expected["gates"])
                self.assertEqual(control["acceptances"], expected["acceptances"])
                if name == "omitted":
                    checked = run_cli("check", "--run", run)
                    self.assertNotEqual(checked.returncode, 0)
                    self.assertIn("outside the Stage", checked.stdout)
                    self.assertIn("use the next-stage controller", checked.stdout)

    def test_initialize_allows_a_preexisting_prd_without_accepting_it(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
            (run / "20-prd.md").write_text("# Reused but untrusted PRD\n", encoding="utf-8")
            before = (run / "20-prd.md").read_bytes()

            initialized = initialize_cli(run)

            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            control = read_control(run)
            self.assertEqual(control["phase"], "discovery")
            self.assertEqual(control["gates"], {"discovery": "PENDING"})
            self.assertEqual(control["acceptances"], {"discovery": None})
            self.assertEqual((run / "20-prd.md").read_bytes(), before)
            checked = run_cli("check", "--run", run)
            self.assertNotEqual(checked.returncode, 0)
            self.assertEqual(read_control(run)["acceptances"], {"discovery": None})

    def test_discovery_gate_exists_exactly_when_discovery_is_selected(self):
        cases = {
            "selected-without-gate": (["discovery", "program_design"], False),
            "omitted-with-gate": (["program_design", "tickets"], True),
        }
        for name, (stages, keep_discovery_gate) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                config = run_config()
                config["stages"] = stages
                if not keep_discovery_gate:
                    config["gates"].pop("discovery")
                config["recommendation"]["gates"] = config["gates"]
                (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

                result = initialize_cli(run)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("discovery gate must exist exactly when discovery is selected", result.stderr)
                self.assertFalse((run / "control.json").exists())

    def test_selected_discovery_remains_the_first_phase(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            config = run_config()
            config["stages"] = ["program_design", "discovery"]
            config["recommendation"]["gates"] = config["gates"]
            (run / "run.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

            result = initialize_cli(run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("selected discovery must be the first stage", result.stderr)
            self.assertFalse((run / "control.json").exists())

    def test_candidate_version_rejects_yaml_boolean_before_state_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            prd = run / "20-prd.md"
            prd.write_text(
                prd.read_text(encoding="utf-8").replace("version: 1\n", "version: true\n", 1),
                encoding="utf-8",
            )
            write_prd_html(run)
            before = (run / "control.json").read_bytes()

            checked = run_cli("check", "--run", run)
            advanced = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-20")

            self.assertNotEqual(checked.returncode, 0)
            self.assertIn("positive integer", checked.stdout)
            self.assertNotEqual(advanced.returncode, 0)
            self.assertEqual((run / "control.json").read_bytes(), before)

    def test_derived_from_version_rejects_yaml_boolean(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            prd = run / "20-prd.md"
            text = prd.read_text(encoding="utf-8")
            marker = "derived_from:\n  artifact: 10-decisions.md\n  version: 1\n"
            self.assertIn(marker, text)
            prd.write_text(text.replace(marker, marker.replace("version: 1", "version: true"), 1), encoding="utf-8")
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("derived_from.version must be a positive integer", result.stdout)

    def test_effective_config_revision_rejects_yaml_boolean(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            prd = run / "20-prd.md"
            text = prd.read_text(encoding="utf-8").replace(
                "effective_config_revision: 0\n",
                "effective_config_revision: false\n",
                1,
            )
            prd.write_text(text, encoding="utf-8")
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate uses a stale effective configuration revision", result.stdout)

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
                state.__setitem__("phase", "program_design"),
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
                self.assertTrue("control.json" in result.stderr or "accepted PRD" in result.stderr)

    def test_stale_gate_cannot_retain_an_acceptance_after_reopen_was_removed(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            advanced = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-20")
            self.assertEqual(advanced.returncode, 0, advanced.stderr)
            state = read_control(run)
            state["phase"] = "discovery"
            state["gates"]["discovery"] = "STALE"
            (run / "control.json").write_text(json.dumps(state) + "\n", encoding="utf-8")

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("STALE gate cannot retain an acceptance", result.stderr)

    def test_accepted_agent_review_file_remains_bound_and_required(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
            }
            review = write_review(run, candidate, verdict="PASS")
            advanced = run_cli("advance", "--run", run, "--review", review.relative_to(run), "--date", "2026-08-20")
            self.assertEqual(advanced.returncode, 0, advanced.stderr)
            review.unlink()

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("accepted review evidence is missing", result.stderr)

    def test_advance_rechecks_candidate_bytes_after_review_before_commit(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
            }
            review = write_review(run, candidate, verdict="PASS")
            module = runpy.run_path(str(Path(__file__).resolve().parents[1] / "plugins/atlas/tools/atlas_control.py"))
            advance = module["advance"]
            original_validate_review = advance.__globals__["validate_review"]

            def validate_then_drift(*args, **kwargs):
                validated = original_validate_review(*args, **kwargs)
                with (run / "20-prd.md").open("a", encoding="utf-8") as handle:
                    handle.write("\nconcurrent drift\n")
                return validated

            advance.__globals__["validate_review"] = validate_then_drift
            before = (run / "control.json").read_bytes()
            try:
                with self.assertRaisesRegex(module["ControlError"], "candidate bytes changed"):
                    advance(run, None, str(review.relative_to(run)), "2026-08-20")
            finally:
                advance.__globals__["validate_review"] = original_validate_review
            self.assertEqual((run / "control.json").read_bytes(), before)

    def test_blocked_agent_review_leaves_gate_pending_for_repair(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
            }
            review = write_review(run, candidate, verdict="BLOCKED")

            result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

            self.assertNotEqual(result.returncode, 0)
            control = read_control(run)
            self.assertEqual(control["status"], "PLANNING")
            self.assertEqual(control["gates"]["discovery"], "PENDING")
            self.assertIsNone(control["blocked_reason"])
            self.assertIsNone(control["acceptances"]["discovery"])

    def test_duplicate_review_json_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
            }
            review = write_review(run, candidate, verdict="PASS")
            review.write_text(
                review.read_text(encoding="utf-8").replace(
                    '  "verdict": "PASS",\n',
                    '  "verdict": "BLOCKED",\n  "verdict": "PASS",\n',
                    1,
                ),
                encoding="utf-8",
            )

            result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate JSON key", result.stderr)
            self.assertEqual(read_control(run)["revision"], 1)

    def test_review_version_rejects_json_boolean(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
            }
            review = write_review(run, candidate, verdict="PASS")
            envelope = json.loads(review.read_text(encoding="utf-8"))
            envelope["version"] = True
            review.write_text(json.dumps(envelope) + "\n", encoding="utf-8")

            result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stage/version", result.stderr)
            self.assertEqual(read_control(run)["revision"], 1)

    def test_review_candidate_version_rejects_json_boolean(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
            }
            review = write_review(run, candidate, verdict="PASS")
            envelope = json.loads(review.read_text(encoding="utf-8"))
            envelope["candidate_version"] = True
            review.write_text(json.dumps(envelope) + "\n", encoding="utf-8")

            result = run_cli("advance", "--run", run, "--review", review.relative_to(run))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate version", result.stderr)
            self.assertEqual(read_control(run)["revision"], 1)

    def test_agent_review_must_use_the_canonical_versioned_reference(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run, discovery="AGENT_REVIEW")
            write_discovery(run)
            candidate = {
                "stage": "discovery",
                "candidate_version": 1,
                "candidate_sha256": sha256(run / "20-prd.md"),
            }
            generated = write_review(run, candidate, verdict="PASS")
            wrong = run / "reviews" / "arbitrary.json"
            generated.replace(wrong)

            result = run_cli("advance", "--run", run, "--review", wrong.relative_to(run))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reviews/product_closure-v1.json", result.stderr)
            self.assertEqual(read_control(run)["revision"], 1)

    def test_minimal_ordered_amendment_updates_count_and_effective_hash(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run, ready=False, stale=True)
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

            write_discovery(run, revision=1)
            self.assertEqual(run_cli("check", "--run", run).returncode, 0)

    def test_amendments_must_be_contiguous_and_only_correct_repos(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run, ready=False, stale=True)
            self.assertEqual(run_cli("mark-stale", "--run", run, "--reason", "scope corrected").returncode, 0)
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
                [".atlas-control.lock", "00-state.md", "10-decisions.md", "20-prd.html", "20-prd.md", "control.json", "run.yaml"],
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

            result = run_cli("advance", "--run", run, "--approval", "human", "--date", "2026-08-20")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(read_control(run)["phase"], "program_design")
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside must not change\n")
            self.assertIn("projection was not regenerated", result.stderr)

    def test_accepted_prd_source_drift_fails_closed_on_next_state_verification(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            make_run(run)
            write_discovery(run)
            advance_discovery(run)
            with (run / "10-decisions.md").open("a", encoding="utf-8") as handle:
                handle.write("\nunauthorized mutation\n")

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("accepted PRD no longer matches its bound decision source", result.stderr)

    def test_live_decisions_must_appear_once_in_the_prd_retrospective(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)

            control = run_cli("check", "--run", run)

            self.assertEqual(control.returncode, 0, control.stdout + control.stderr)

            write_markdown(
                run / "10-decisions.md",
                decision_log_frontmatter(),
                decision_log_body(retrospective_rows=[]),
            )
            write_prd(run)
            write_prd_html(run)

            missing = run_cli("check", "--run", run)

            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("retrospective is missing live decisions: ['D-001']", missing.stdout)

            decisions = [
                {"id": "D-001", "status": "settled", "supersedes": "null", "chosen": "Completion must be observable."},
                {"id": "D-002", "status": "settled", "supersedes": "null", "chosen": "No normative effect."},
            ]
            rows = [{"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""}]
            write_markdown(run / "10-decisions.md", decision_log_frontmatter(), decision_log_body(decisions=decisions, retrospective_rows=rows))
            write_prd(run)
            write_prd_html(run)

            uncited_missing = run_cli("check", "--run", run)

            self.assertNotEqual(uncited_missing.returncode, 0)
            self.assertIn("retrospective is missing live decisions: ['D-002']", uncited_missing.stdout)

            rows.append({"decision": "D-002", "disposition": "NO_NORMATIVE_EFFECT", "prd_ids": "", "reason": "Pure rationale only."})
            write_markdown(run / "10-decisions.md", decision_log_frontmatter(), decision_log_body(decisions=decisions, retrospective_rows=rows))
            write_prd(run)
            write_prd_html(run)

            complete = run_cli("check", "--run", run)

            self.assertEqual(complete.returncode, 0, complete.stdout + complete.stderr)

    def test_retrospective_rejects_nonexistent_and_superseded_decision_rows(self):
        valid_decisions = [
            {"id": "D-001", "status": "settled", "supersedes": "null", "chosen": "Completion must be observable."},
            {"id": "D-002", "status": "superseded", "supersedes": "null", "chosen": "Old choice."},
        ]
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(
                run,
                decisions=valid_decisions,
                retrospective_rows=[{"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""}],
            )

            control = run_cli("check", "--run", run)

            self.assertEqual(control.returncode, 0, control.stdout + control.stderr)

            for name, rows in (
                ("nonexistent", [{"decision": "D-003", "disposition": "NORMATIVE", "prd_ids": "R-001", "reason": ""}]),
                ("superseded", [{"decision": "D-002", "disposition": "NORMATIVE", "prd_ids": "R-001", "reason": ""}]),
            ):
                with self.subTest(name=name):
                    write_markdown(
                        run / "10-decisions.md",
                        decision_log_frontmatter(),
                        decision_log_body(decisions=valid_decisions, retrospective_rows=rows),
                    )
                    write_prd(run)
                    write_prd_html(run)

                    blocked = run_cli("check", "--run", run)

                    self.assertNotEqual(blocked.returncode, 0)
                    self.assertIn("D-00", blocked.stdout)

    def test_normative_bijection_requires_matching_rows_and_prd_citations(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)

            control = run_cli("check", "--run", run)

            self.assertEqual(control.returncode, 0, control.stdout + control.stderr)

            write_markdown(
                run / "10-decisions.md",
                decision_log_frontmatter(),
                decision_log_body(retrospective_rows=[{"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": "R-999", "reason": ""}]),
            )
            write_prd(run)
            write_prd_html(run)
            missing_from_prd = run_cli("check", "--run", run)
            self.assertNotEqual(missing_from_prd.returncode, 0)
            self.assertIn("R-999", missing_from_prd.stdout)

            write_decisions(run)
            write_prd(run, body_kwargs={"derived_from": "D-002"})
            write_prd_html(run)
            missing_from_retrospective = run_cli("check", "--run", run)
            self.assertNotEqual(missing_from_retrospective.returncode, 0)
            self.assertIn("D-002", missing_from_retrospective.stdout)

    def test_decision_log_frontmatter_is_exact_and_bound_to_the_run(self):
        for name, frontmatter in (
            ("wrong-run", {"run": "other", "version": 1}),
            ("extra-field", {"run": "demo", "version": 1, "status": "draft"}),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                self.initialize_product_closure_run(run)
                write_markdown(run / "10-decisions.md", frontmatter, decision_log_body())
                write_prd(run)
                write_prd_html(run)

                blocked = run_cli("check", "--run", run)

                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn("decision-log frontmatter", blocked.stdout.lower())

    def test_duplicate_yaml_keys_fail_closed_in_closure_artifacts(self):
        cases = (
            ("decision-frontmatter", "10-decisions.md", "version: 1\n", "version: 1\nversion: 1\n"),
            ("prd-frontmatter", "20-prd.md", "gate_ready: true\n", "gate_ready: true\ngate_ready: true\n"),
            ("decision-record", "10-decisions.md", "status: settled\n", "status: settled\nstatus: settled\n"),
        )
        for name, filename, anchor, replacement in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                self.initialize_product_closure_run(run)
                self.write_product_closure_candidate(run)
                target = run / filename
                target.write_text(
                    target.read_text(encoding="utf-8").replace(anchor, replacement, 1),
                    encoding="utf-8",
                )
                if filename == "10-decisions.md":
                    write_prd(run)
                write_prd_html(run)

                blocked = run_cli("check", "--run", run)

                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn("duplicate yaml key", blocked.stdout.lower())

    def test_retrospective_normative_ids_must_point_to_items_that_cite_the_same_decision(self):
        decisions = [
            {"id": "D-001", "status": "settled", "supersedes": "null", "chosen": "Completion must be observable."},
            {"id": "D-002", "status": "settled", "supersedes": "null", "chosen": "Research uses a cold read."},
        ]
        rows = [
            {"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""},
            {"decision": "D-002", "disposition": "NORMATIVE", "prd_ids": "P-001", "reason": ""},
        ]
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run, decisions=decisions, retrospective_rows=rows)

            blocked = run_cli("check", "--run", run)

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("does not cite d-002", blocked.stdout.lower())

    def test_retrospective_identifier_cells_reject_junk_and_duplicates(self):
        decisions = [
            {"id": "D-001", "status": "settled", "supersedes": "null", "chosen": "Completion must be observable."},
            {"id": "D-002", "status": "settled", "supersedes": "null", "chosen": "Research uses a cold read."},
        ]
        malformed_rows = (
            [
                {"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS + ", R-001", "reason": ""},
                {"decision": "D-002", "disposition": "NO_NORMATIVE_EFFECT", "prd_ids": "", "reason": "Research-only."},
            ],
            [
                {"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""},
                {"decision": "D-002", "disposition": "NO_NORMATIVE_EFFECT", "prd_ids": "none", "reason": "Research-only."},
            ],
        )
        for rows in malformed_rows:
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                self.initialize_product_closure_run(run)
                self.write_product_closure_candidate(run, decisions=decisions, retrospective_rows=rows)

                blocked = run_cli("check", "--run", run)

                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn("retrospective", blocked.stdout.lower())

    def test_retrospective_requires_the_exact_table_header(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            decisions = run / "10-decisions.md"
            decisions.write_text(
                decisions.read_text(encoding="utf-8").replace(
                    "| Decision | Disposition | PRD identifiers | Reason (required iff NO_NORMATIVE_EFFECT) |",
                    "| Guess | Disposition | PRD identifiers | Reason |",
                    1,
                ),
                encoding="utf-8",
            )
            write_prd(run)
            write_prd_html(run)

            blocked = run_cli("check", "--run", run)

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("table header", blocked.stdout.lower())

    def test_retrospective_is_unique_and_final(self):
        suffixes = (
            "\n## PRD alignment retrospective\n\n| Decision | Disposition | PRD identifiers | Reason (required iff NO_NORMATIVE_EFFECT) |\n|---|---|---|---|\n",
            "\n## Notes\n\nNothing further.\n",
        )
        for suffix in suffixes:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                self.initialize_product_closure_run(run)
                self.write_product_closure_candidate(run)
                decisions = run / "10-decisions.md"
                decisions.write_text(decisions.read_text(encoding="utf-8") + suffix, encoding="utf-8")
                write_prd(run)
                write_prd_html(run)

                blocked = run_cli("check", "--run", run)

                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn("retrospective", blocked.stdout.lower())

    def test_prd_citations_reject_nonexistent_and_superseded_decisions(self):
        decisions = [
            {"id": "D-001", "status": "settled", "supersedes": "null", "chosen": "Completion must be observable."},
            {"id": "D-002", "status": "superseded", "supersedes": "null", "chosen": "Old decision."},
        ]
        rows = [{"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""}]
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run, decisions=decisions, retrospective_rows=rows)

            control = run_cli("check", "--run", run)

            self.assertEqual(control.returncode, 0, control.stdout + control.stderr)

            for derived_from in ("D-003", "D-002"):
                with self.subTest(derived_from=derived_from):
                    write_markdown(
                        run / "20-prd.md",
                        prd_frontmatter(run / "10-decisions.md"),
                        prd_body(derived_from=derived_from, out_of_scope_from=derived_from),
                    )
                    write_prd_html(run)

                    blocked = run_cli("check", "--run", run)

                    self.assertNotEqual(blocked.returncode, 0)
                    self.assertIn(derived_from, blocked.stdout)

    def test_superseded_targets_must_be_marked_superseded(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(
                run,
                decisions=[
                    {"id": "D-001", "status": "superseded", "supersedes": "null", "chosen": "Old decision."},
                    {"id": "D-002", "status": "settled", "supersedes": "D-001", "chosen": "Replacement decision."},
                ],
                retrospective_rows=[{"decision": "D-002", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""}],
                body_kwargs={"derived_from": "D-002", "out_of_scope_from": "D-002"},
            )

            control = run_cli("check", "--run", run)

            self.assertEqual(control.returncode, 0, control.stdout + control.stderr)

            self.write_product_closure_candidate(
                run,
                decisions=[
                    {"id": "D-001", "status": "settled", "supersedes": "null", "chosen": "Old decision."},
                    {"id": "D-002", "status": "settled", "supersedes": "D-001", "chosen": "Replacement decision."},
                ],
                retrospective_rows=[
                    {"decision": "D-001", "disposition": "NO_NORMATIVE_EFFECT", "prd_ids": "", "reason": "Superseded."},
                    {"decision": "D-002", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""},
                ],
            )

            blocked = run_cli("check", "--run", run)

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("supersed", blocked.stdout.lower())

    def test_prd_section_sequence_is_exact(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            prd = run / "20-prd.md"
            prd.write_text(
                prd.read_text(encoding="utf-8") + "\n## Rationale\n\nThis belongs in the decision log.\n",
                encoding="utf-8",
            )
            write_prd_html(run)

            blocked = run_cli("check", "--run", run)

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("section sequence", blocked.stdout.lower())

    def test_each_product_closure_readiness_rule_has_a_specific_witness(self):
        cases = (
            ("prohibited section", "PRD contains an internal design or ticket section"),
            ("blocking question", "PRD contains a blocking open question"),
            ("gate readiness", "producer has not recorded gate readiness"),
            ("cold read", "cold-read evidence is incomplete"),
            ("renderer version", "renderer version is missing or unknown"),
            ("HTML source name", "does not declare 20-prd.md as its source"),
            ("no-effect reason", "must include a reason"),
        )
        for trigger, expected_gap in cases:
            with self.subTest(trigger=trigger), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                self.initialize_product_closure_run(run)
                self.write_product_closure_candidate(run)
                prd_path = run / "20-prd.md"
                decisions_path = run / "10-decisions.md"
                if trigger == "prohibited section":
                    prd_path.write_text(prd_path.read_text(encoding="utf-8") + "\n## Work Items\n\n- forbidden\n", encoding="utf-8")
                    write_prd_html(run)
                elif trigger == "blocking question":
                    prd_path.write_text(prd_path.read_text(encoding="utf-8").replace("## Open questions\n\nNone.", "## Open questions\n\nBlocking: unresolved behavior"), encoding="utf-8")
                    write_prd_html(run)
                elif trigger == "gate readiness":
                    prd_path.write_text(prd_path.read_text(encoding="utf-8").replace("gate_ready: true", "gate_ready: false", 1), encoding="utf-8")
                    write_prd_html(run)
                elif trigger == "cold read":
                    prd_path.write_text(prd_path.read_text(encoding="utf-8").replace("cold_read: complete", "cold_read: pending", 1), encoding="utf-8")
                    write_prd_html(run)
                elif trigger == "renderer version":
                    html_path = run / "20-prd.html"
                    html_path.write_text(html_path.read_text(encoding="utf-8").replace('atlas-renderer-version" content="1.0.0', 'atlas-renderer-version" content="0.0.0'), encoding="utf-8")
                elif trigger == "HTML source name":
                    html_path = run / "20-prd.html"
                    html_path.write_text(html_path.read_text(encoding="utf-8").replace('atlas-source" content="20-prd.md', 'atlas-source" content="other.md'), encoding="utf-8")
                else:
                    decisions_path.write_text(decisions_path.read_text(encoding="utf-8").replace(
                        "| D-001 | NORMATIVE | P-001, R-001, I-001, C-001, X-001 |  |",
                        "| D-001 | NO_NORMATIVE_EFFECT |  |  |",
                    ), encoding="utf-8")
                    write_prd(run)
                    write_prd_html(run)

                blocked = run_cli("check", "--run", run)

                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn(expected_gap, blocked.stdout)

    def test_frontier_rows_are_not_hidden_by_the_word_question(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            body = decision_log_body().replace(
                "|---|---|---|\n\n",
                "|---|---|---|\n| Q-001 — Question about pricing | grill | — |\n\n",
                1,
            )
            write_markdown(run / "10-decisions.md", decision_log_frontmatter(), body)
            write_prd(run)
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("open frontier still contains unresolved entries", result.stdout)

    def test_markdown_list_and_emphasis_cannot_hide_a_blocking_open_question(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            prd = run / "20-prd.md"
            prd.write_text(
                prd.read_text(encoding="utf-8").replace(
                    "## Open questions\n\nNone.",
                    "## Open questions\n\n- **Blocking:** which behavior wins?",
                ),
                encoding="utf-8",
            )
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("blocking open question", result.stdout)

    def test_cold_read_placeholder_cannot_claim_completion(self):
        for placeholder in (
            "Pending.",
            "| Finding | Disposition |\n|---|---|\n| Pending. | Pending. |",
        ):
            with self.subTest(placeholder=placeholder), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                self.initialize_product_closure_run(run)
                write_markdown(
                    run / "10-decisions.md",
                    decision_log_frontmatter(),
                    decision_log_body(cold_read_text=placeholder),
                )
                write_prd(run)
                write_prd_html(run)

                result = run_cli("check", "--run", run)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Cold-read evidence table is malformed", result.stdout)

    def test_normative_item_cannot_borrow_a_citation_from_a_later_section(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            prd = run / "20-prd.md"
            text = prd.read_text(encoding="utf-8")
            marker = "**Derived from:** D-001\n\n## Observability\n\n- Completion state is externally inspectable."
            self.assertIn(marker, text)
            prd.write_text(
                text.replace(
                    marker,
                    "## Observability\n\n- Completion state is externally inspectable.\n\n**Derived from:** D-001",
                    1,
                ),
                encoding="utf-8",
            )
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("X-001 is missing a Derived from list", result.stdout)

    def test_every_decision_requires_a_closed_contribution_grade(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            body = decision_log_body().replace("contribution: load-bearing", "contribution: null", 1)
            write_markdown(run / "10-decisions.md", decision_log_frontmatter(), body)
            write_prd(run)
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contribution grade is invalid", result.stdout)

    def test_supersedes_must_name_an_earlier_distinct_decision(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            decisions = [
                {"id": "D-001", "status": "settled", "supersedes": "D-002", "chosen": "Use the final behavior."},
                {"id": "D-002", "status": "superseded", "supersedes": "null", "chosen": "Use the discarded behavior."},
            ]
            rows = [{"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": ALL_PRD_IDS, "reason": ""}]
            self.write_product_closure_candidate(run, decisions=decisions, retrospective_rows=rows)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must name an earlier distinct decision", result.stdout)

    def test_prd_derived_from_and_html_metadata_bind_current_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)

            control = run_cli("check", "--run", run)

            self.assertEqual(control.returncode, 0, control.stdout + control.stderr)

            with (run / "10-decisions.md").open("a", encoding="utf-8") as handle:
                handle.write("\nbyte drift\n")
            derived_from_drift = run_cli("check", "--run", run)
            self.assertNotEqual(derived_from_drift.returncode, 0)
            self.assertIn("derived_from", derived_from_drift.stdout.lower())

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            (run / "20-prd.html").unlink()

            missing_html = run_cli("check", "--run", run)

            self.assertNotEqual(missing_html.returncode, 0)
            self.assertIn("20-prd.html", missing_html.stdout)

        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            with (run / "20-prd.md").open("a", encoding="utf-8") as handle:
                handle.write("\nchanged markdown byte\n")

            stale_html = run_cli("check", "--run", run)

            self.assertNotEqual(stale_html.returncode, 0)
            self.assertIn("20-prd.html", stale_html.stdout)

    def test_controller_rejects_duplicate_projection_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            html = run / "20-prd.html"
            text = html.read_text(encoding="utf-8")
            marker = '  <meta name="atlas-source" content="20-prd.md">\n'
            self.assertIn(marker, text)
            html.write_text(text.replace(marker, marker + marker, 1), encoding="utf-8")

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate atlas metadata", result.stdout)

    def test_normative_retrospective_reason_must_be_empty_is_a_separating_witness(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(
                run,
                retrospective_rows=[
                    {
                        "decision": "D-001",
                        "disposition": "NORMATIVE",
                        "prd_ids": ALL_PRD_IDS,
                        "reason": "not allowed",
                    }
                ],
            )

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("retrospective NORMATIVE row D-001 must leave reason empty", result.stdout)

    def test_each_prd_citation_requires_its_own_reverse_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(
                run,
                retrospective_rows=[
                    {"decision": "D-001", "disposition": "NORMATIVE", "prd_ids": "P-001", "reason": ""}
                ],
            )

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("R-001 cites D-001 but the retrospective does not point back to it", result.stdout)

    def test_candidate_status_must_remain_draft_is_a_separating_witness(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            prd = run / "20-prd.md"
            prd.write_text(
                prd.read_text(encoding="utf-8").replace("status: draft\n", "status: approved\n", 1),
                encoding="utf-8",
            )
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("producer candidate status must remain draft", result.stdout)

    def test_wrong_integer_derived_from_version_is_a_separating_witness(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            prd = run / "20-prd.md"
            marker = "derived_from:\n  artifact: 10-decisions.md\n  version: 1\n"
            text = prd.read_text(encoding="utf-8")
            self.assertIn(marker, text)
            prd.write_text(text.replace(marker, marker.replace("version: 1", "version: 2"), 1), encoding="utf-8")
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("derived_from.version does not match the decision-log version", result.stdout)

    def test_intake_stale_true_is_a_separating_witness(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.initialize_product_closure_run(run)
            self.write_product_closure_candidate(run)
            prd = run / "20-prd.md"
            prd.write_text(
                prd.read_text(encoding="utf-8").replace("intake_stale: false\n", "intake_stale: true\n", 1),
                encoding="utf-8",
            )
            write_prd_html(run)

            result = run_cli("check", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("discovery reports stale intake", result.stdout)


if __name__ == "__main__":
    unittest.main()
