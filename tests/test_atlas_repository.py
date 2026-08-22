import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_repository.py"
CONTROL_CLI = ROOT / "plugins" / "atlas" / "tools" / "atlas_control.py"
REAL_GIT = shutil.which("git")
if REAL_GIT is None:  # pragma: no cover - the test environment requires Git
    raise RuntimeError("git is required")


def command(*args, cwd=None, env=None, text=True, check=True):
    result = subprocess.run(
        [*map(str, args)],
        cwd=cwd,
        env=env,
        text=text,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {args}\nstdout={result.stdout!r}\nstderr={result.stderr!r}"
        )
    return result


def git(repo, *args, env=None):
    merged = os.environ.copy()
    merged.update(
        {
            "GIT_AUTHOR_NAME": "Atlas Test",
            "GIT_AUTHOR_EMAIL": "atlas@example.invalid",
            "GIT_COMMITTER_NAME": "Atlas Test",
            "GIT_COMMITTER_EMAIL": "atlas@example.invalid",
        }
    )
    if env:
        merged.update(env)
    return command(REAL_GIT, "-C", repo, *args, env=merged).stdout.strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initialize_repository(path: Path) -> None:
    path.mkdir()
    command(REAL_GIT, "init", "-q", path)


def commit_file(repo: Path, relative: str, content: bytes, message: str) -> str:
    target = repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    git(repo, "add", "--", relative)
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def run_config(repos):
    gates = {
        "discovery": {"authority": "HUMAN"},
        "program_design": {"authority": "HUMAN"},
    }
    return {
        "version": 1,
        "run": "demo",
        "opened": "2026-08-22",
        "goal": "Inspect exact repository baselines",
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
            "reasons": [
                {"dimension": "workflow", "evidence": "repository grounding is required"}
            ],
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
            "reversibility": "high",
            "architecture_change": False,
            "schema_change": False,
            "public_contract_change": False,
            "security_sensitive": False,
            "operational_impact": "low",
            "testability": "high",
        },
        "repos": repos,
        "overrides": [],
    }


class AtlasRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / "home"
        self.native_root = self.root / "native-config"
        self.home.mkdir()
        self.native_root.mkdir()
        self.run_dir = self.root / "run"
        self.run_dir.mkdir()
        self.repo = self.root / "repository"
        initialize_repository(self.repo)
        self.baseline = commit_file(
            self.repo,
            "src/message.txt",
            b"baseline A needle\n",
            "baseline A",
        )

    def tearDown(self):
        self.temp.cleanup()

    @property
    def native_config(self):
        return self.native_root / "atlas" / "config.yaml"

    @property
    def legacy_config(self):
        return self.home / ".atlas" / "config.yaml"

    def environment(self, extra=None):
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(self.home),
                "XDG_CONFIG_HOME": str(self.native_root),
            }
        )
        if extra:
            env.update(extra)
        return env

    def write_config(self, bindings, *, legacy=False, extra=None):
        path = self.legacy_config if legacy else self.native_config
        path.parent.mkdir(parents=True, exist_ok=True)
        config = {"repositories": {"bindings": bindings}}
        if extra:
            config.update(extra)
        path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        return path

    def write_raw_config(self, text, *, legacy=False):
        path = self.legacy_config if legacy else self.native_config
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def initialize_run(self, repos=None):
        repos = repos or [{"repository": "fixture", "baseline": self.baseline}]
        (self.run_dir / "run.yaml").write_text(
            yaml.safe_dump(run_config(repos), sort_keys=False), encoding="utf-8"
        )
        identity = os.stat(self.run_dir, follow_symlinks=False)
        command(
            sys.executable,
            CONTROL_CLI,
            "initialize",
            "--run",
            self.run_dir,
            "--prepared-device",
            identity.st_dev,
            "--prepared-inode",
            identity.st_ino,
        )

    def run_cli(self, *args, cwd=None, env=None):
        return command(
            sys.executable,
            CLI,
            *args,
            cwd=cwd,
            env=env or self.environment(),
            check=False,
        )

    def read_cli(self, *args, cwd=None, env=None):
        return command(
            sys.executable,
            CLI,
            *args,
            cwd=cwd,
            env=env or self.environment(),
            text=False,
            check=False,
        )

    def parse_report(self, result, *, stderr=False):
        raw = result.stderr if stderr else result.stdout
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return json.loads(raw)

    def assert_blocked(self, result, *codes, stderr=False):
        self.assertEqual(result.returncode, 1, result.stderr)
        report = self.parse_report(result, stderr=stderr)
        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertEqual({gap["code"] for gap in report["gaps"]}, set(codes))
        return report

    def verify(self, *, cwd=None, env=None):
        return self.run_cli("verify", "--run", self.run_dir, cwd=cwd, env=env)

    def test_verify_uses_native_config_before_legacy_fallback(self):
        self.initialize_run()
        self.write_config({"fixture": str(self.repo)})
        self.write_config({"fixture": str(self.root / "wrong")}, legacy=True)

        result = self.verify()

        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.parse_report(result)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["config_path"], str(self.native_config))
        self.assertEqual(report["repositories"][0]["commit"], self.baseline)
        self.assertRegex(report["repositories"][0]["tree"], r"^[0-9a-f]{40,64}$")

    def test_verify_uses_legacy_config_only_when_native_is_absent(self):
        self.initialize_run()
        self.write_config({"fixture": str(self.repo)}, legacy=True)

        result = self.verify()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.parse_report(result)["config_path"], str(self.legacy_config))

    def test_verify_reports_missing_binding_without_mutation(self):
        self.initialize_run()
        self.write_config({"other": str(self.repo)})
        before = {name: sha256(self.run_dir / name) for name in ("run.yaml", "control.json")}

        result = self.verify()

        report = self.assert_blocked(result, "missing_binding")
        self.assertEqual(report["repositories"][0]["repository"], "fixture")
        self.assertEqual(report["repositories"][0]["result"], "BLOCKED")
        self.assertEqual(
            before,
            {name: sha256(self.run_dir / name) for name in ("run.yaml", "control.json")},
        )

    def test_verify_rejects_malformed_and_non_exact_config_schema(self):
        self.initialize_run()
        cases = {
            "malformed": "repositories: [\n",
            "missing-bindings": "repositories: {}\n",
            "extra-repository-key": "repositories:\n  bindings: {}\n  candidates: {}\n",
            "non-string-identity": "repositories:\n  bindings:\n    7: /tmp/repo\n",
            "non-string-path": "repositories:\n  bindings:\n    fixture: [repo]\n",
        }
        for label, text in cases.items():
            with self.subTest(label=label):
                if self.native_config.exists():
                    self.native_config.unlink()
                self.write_raw_config(text)
                result = self.verify()
                report = self.assert_blocked(result, "invalid_config")
                self.assertIn("config", report["gaps"][0]["problem"].lower())

    def test_verify_rejects_duplicate_yaml_keys(self):
        self.initialize_run()
        self.write_raw_config(
            "repositories:\n"
            "  bindings:\n"
            f"    fixture: {self.repo}\n"
            f"    fixture: {self.repo}\n"
        )

        result = self.verify()

        report = self.assert_blocked(result, "invalid_config")
        self.assertIn("duplicate YAML key", report["gaps"][0]["problem"])

    def test_verify_rejects_relative_and_symlink_sources(self):
        self.initialize_run()
        link = self.root / "repository-link"
        link.symlink_to(self.repo, target_is_directory=True)
        for label, source, code in (
            ("relative", "repository", "source_not_absolute"),
            ("symlink", str(link), "source_symlink"),
        ):
            with self.subTest(label=label):
                self.write_config({"fixture": source})
                result = self.verify()
                self.assert_blocked(result, code)

    def test_verify_rejects_non_git_source(self):
        self.initialize_run()
        source = self.root / "plain"
        source.mkdir()
        self.write_config({"fixture": str(source)})

        result = self.verify()

        self.assert_blocked(result, "source_not_git")

    def test_verify_rejects_abbreviated_missing_and_non_commit_baselines(self):
        blob_oid = git(self.repo, "rev-parse", f"{self.baseline}:src/message.txt")
        tree_oid = git(self.repo, "rev-parse", f"{self.baseline}^{{tree}}")
        cases = {
            "abbreviated": (self.baseline[:8], "baseline_not_canonical"),
            "missing": ("f" * 40, "baseline_unavailable"),
            "blob": (blob_oid, "baseline_not_commit"),
            "tree": (tree_oid, "baseline_not_commit"),
        }
        self.write_config({"fixture": str(self.repo)})
        for label, (baseline, code) in cases.items():
            with self.subTest(label=label):
                self.run_dir = self.root / f"run-{label}"
                self.run_dir.mkdir()
                self.initialize_run([{"repository": "fixture", "baseline": baseline}])
                before = {
                    child.name: sha256(child)
                    for child in self.run_dir.iterdir()
                    if child.is_file()
                }
                result = self.verify()
                self.assert_blocked(result, code)
                self.assertEqual(
                    before,
                    {
                        child.name: sha256(child)
                        for child in self.run_dir.iterdir()
                        if child.is_file()
                    },
                )

    def test_verify_reports_every_repository_gap(self):
        second_repo = self.root / "second"
        initialize_repository(second_repo)
        second_baseline = commit_file(second_repo, "two.txt", b"two\n", "two")
        self.initialize_run(
            [
                {"repository": "first", "baseline": self.baseline},
                {"repository": "second", "baseline": second_baseline},
            ]
        )
        self.write_config({})

        result = self.verify()

        report = self.assert_blocked(result, "missing_binding")
        self.assertEqual(
            [(item["repository"], item["result"]) for item in report["repositories"]],
            [("first", "BLOCKED"), ("second", "BLOCKED")],
        )
        self.assertEqual(
            [gap["repository"] for gap in report["gaps"]], ["first", "second"]
        )

    def test_list_search_and_read_use_baseline_not_head_index_or_worktree(self):
        self.initialize_run()
        self.write_config({"fixture": str(self.repo)})
        baseline_blob = git(self.repo, "rev-parse", f"{self.baseline}:src/message.txt")
        head = commit_file(
            self.repo,
            "src/message.txt",
            b"HEAD B different\n",
            "HEAD B",
        )
        (self.repo / "src" / "message.txt").write_bytes(b"dirty worktree C\n")
        (self.repo / "dirty-only.txt").write_text("dirty only C\n", encoding="utf-8")
        before_status = git(self.repo, "status", "--porcelain=v1", "--untracked-files=all")
        before_head = git(self.repo, "rev-parse", "HEAD")
        before_index = sha256(self.repo / ".git" / "index")
        before_run = {name: sha256(self.run_dir / name) for name in ("run.yaml", "control.json")}

        listed = self.run_cli(
            "list", "--run", self.run_dir, "--repository", "fixture"
        )
        searched_a = self.run_cli(
            "search",
            "--run",
            self.run_dir,
            "--repository",
            "fixture",
            "--needle",
            "baseline A needle",
        )
        searched_b = self.run_cli(
            "search",
            "--run",
            self.run_dir,
            "--repository",
            "fixture",
            "--needle",
            "HEAD B",
        )
        searched_c = self.run_cli(
            "search",
            "--run",
            self.run_dir,
            "--repository",
            "fixture",
            "--needle",
            "dirty worktree C",
        )
        read = self.read_cli(
            "read",
            "--run",
            str(self.run_dir),
            "--repository",
            "fixture",
            "--path",
            "src/message.txt",
        )

        self.assertEqual(listed.returncode, 0, listed.stderr)
        entry = self.parse_report(listed)["entries"][0]
        self.assertEqual(
            entry,
            {
                "gitlink": False,
                "mode": "100644",
                "oid": baseline_blob,
                "path": "src/message.txt",
                "type": "blob",
            },
        )
        self.assertEqual(self.parse_report(searched_a)["matches"][0]["path"], "src/message.txt")
        self.assertEqual(self.parse_report(searched_a)["matches"][0]["occurrences"], 1)
        self.assertEqual(self.parse_report(searched_b)["matches"], [])
        self.assertEqual(self.parse_report(searched_c)["matches"], [])
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertEqual(read.stdout, b"baseline A needle\n")
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), before_head)
        self.assertEqual(
            git(self.repo, "status", "--porcelain=v1", "--untracked-files=all"),
            before_status,
        )
        self.assertEqual(sha256(self.repo / ".git" / "index"), before_index)
        self.assertEqual(
            {name: sha256(self.run_dir / name) for name in ("run.yaml", "control.json")},
            before_run,
        )

    def test_list_marks_gitlinks_and_read_refuses_them(self):
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{self.baseline},vendor/sub")
        git(self.repo, "commit", "-q", "-m", "gitlink")
        baseline = git(self.repo, "rev-parse", "HEAD")
        self.initialize_run([{"repository": "fixture", "baseline": baseline}])
        self.write_config({"fixture": str(self.repo)})

        listed = self.run_cli("list", "--run", self.run_dir, "--repository", "fixture")
        searched = self.run_cli(
            "search",
            "--run",
            self.run_dir,
            "--repository",
            "fixture",
            "--needle",
            "content that could exist in the submodule",
        )
        read = self.read_cli(
            "read",
            "--run",
            str(self.run_dir),
            "--repository",
            "fixture",
            "--path",
            "vendor/sub",
        )

        gitlink = next(
            item for item in self.parse_report(listed)["entries"] if item["path"] == "vendor/sub"
        )
        self.assertEqual(gitlink["mode"], "160000")
        self.assertEqual(gitlink["type"], "commit")
        self.assertIs(gitlink["gitlink"], True)
        self.assert_blocked(searched, "gitlink_content_unavailable")
        self.assert_blocked(read, "gitlink_content_unavailable", stderr=True)
        self.assertEqual(read.stdout, b"")

    def test_read_refuses_tree_and_git_lfs_pointer(self):
        pointer = (
            b"version https://git-lfs.github.com/spec/v1\n"
            b"oid sha256:" + b"a" * 64 + b"\n"
            b"size 123\n"
        )
        baseline = commit_file(self.repo, "large.bin", pointer, "lfs pointer")
        self.initialize_run([{"repository": "fixture", "baseline": baseline}])
        self.write_config({"fixture": str(self.repo)})

        tree = self.read_cli(
            "read", "--run", str(self.run_dir), "--repository", "fixture", "--path", "src"
        )
        lfs = self.read_cli(
            "read", "--run", str(self.run_dir), "--repository", "fixture", "--path", "large.bin"
        )
        searched = self.run_cli(
            "search",
            "--run",
            self.run_dir,
            "--repository",
            "fixture",
            "--needle",
            "content that could exist behind the LFS pointer",
        )

        self.assert_blocked(tree, "path_is_tree", stderr=True)
        self.assert_blocked(lfs, "lfs_content_unavailable", stderr=True)
        self.assert_blocked(searched, "lfs_content_unavailable")
        self.assertEqual(tree.stdout, b"")
        self.assertEqual(lfs.stdout, b"")

    def test_read_confines_paths_and_requires_an_exact_entry(self):
        self.initialize_run()
        self.write_config({"fixture": str(self.repo)})
        for path, code in (
            ("", "invalid_tree_path"),
            ("/src/message.txt", "invalid_tree_path"),
            ("../src/message.txt", "invalid_tree_path"),
            ("src/../src/message.txt", "invalid_tree_path"),
            ("src", "path_is_tree"),
            ("src/missing.txt", "path_not_found"),
        ):
            with self.subTest(path=path):
                result = self.read_cli(
                    "read",
                    "--run",
                    str(self.run_dir),
                    "--repository",
                    "fixture",
                    "--path",
                    path,
                )
                self.assert_blocked(result, code, stderr=True)

    def test_search_is_literal_utf8_over_blob_bytes(self):
        baseline = commit_file(
            self.repo,
            "unicode.bin",
            "héllo [x] héllo".encode("utf-8") + b"\x00tail",
            "unicode",
        )
        self.initialize_run([{"repository": "fixture", "baseline": baseline}])
        self.write_config({"fixture": str(self.repo)})

        unicode_result = self.run_cli(
            "search", "--run", self.run_dir, "--repository", "fixture", "--needle", "héllo"
        )
        literal_result = self.run_cli(
            "search", "--run", self.run_dir, "--repository", "fixture", "--needle", "[x]"
        )
        regex_result = self.run_cli(
            "search", "--run", self.run_dir, "--repository", "fixture", "--needle", ".*"
        )

        unicode_matches = self.parse_report(unicode_result)["matches"]
        literal_matches = self.parse_report(literal_result)["matches"]
        self.assertEqual(unicode_matches, [{"occurrences": 2, "path": "unicode.bin"}])
        self.assertEqual(literal_matches, [{"occurrences": 1, "path": "unicode.bin"}])
        self.assertEqual(self.parse_report(regex_result)["matches"], [])

    def test_commands_are_independent_of_caller_cwd(self):
        self.initialize_run()
        self.write_config({"fixture": str(self.repo)})
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()

        result = self.run_cli(
            "list", "--run", self.run_dir, "--repository", "fixture", cwd=elsewhere
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.parse_report(result)["entries"][0]["path"], "src/message.txt")

    def test_git_subprocesses_receive_read_only_environment_and_devnull_stdin(self):
        self.initialize_run()
        self.write_config({"fixture": str(self.repo)})
        wrapper_dir = self.root / "wrapper"
        wrapper_dir.mkdir()
        log = self.root / "git-log.jsonl"
        wrapper = wrapper_dir / "git"
        wrapper.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, stat, sys\n"
            "null = os.stat(os.devnull)\n"
            "stdin = os.fstat(0)\n"
            "row = {\n"
            "  'args': sys.argv[1:],\n"
            "  'optional_locks': os.environ.get('GIT_OPTIONAL_LOCKS'),\n"
            "  'no_replace': os.environ.get('GIT_NO_REPLACE_OBJECTS'),\n"
            "  'no_lazy_fetch': os.environ.get('GIT_NO_LAZY_FETCH'),\n"
            "  'terminal_prompt': os.environ.get('GIT_TERMINAL_PROMPT'),\n"
            "  'stdin_devnull': stat.S_ISCHR(stdin.st_mode) and stdin.st_rdev == null.st_rdev,\n"
            "}\n"
            "with open(os.environ['ATLAS_GIT_LOG'], 'a', encoding='utf-8') as handle:\n"
            "    handle.write(json.dumps(row) + '\\n')\n"
            "os.execv(os.environ['ATLAS_REAL_GIT'], [os.environ['ATLAS_REAL_GIT'], *sys.argv[1:]])\n",
            encoding="utf-8",
        )
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
        env = self.environment(
            {
                "PATH": str(wrapper_dir) + os.pathsep + os.environ.get("PATH", ""),
                "ATLAS_GIT_LOG": str(log),
                "ATLAS_REAL_GIT": REAL_GIT,
            }
        )

        result = self.verify(env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertGreaterEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(row["optional_locks"], "0")
            self.assertEqual(row["no_replace"], "1")
            self.assertEqual(row["no_lazy_fetch"], "1")
            self.assertEqual(row["terminal_prompt"], "0")
            self.assertIs(row["stdin_devnull"], True)

    def test_help_exists_for_top_level_and_every_command(self):
        for args in (
            ("--help",),
            ("verify", "--help"),
            ("list", "--help"),
            ("search", "--help"),
            ("read", "--help"),
        ):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()
