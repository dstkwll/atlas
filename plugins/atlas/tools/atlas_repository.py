#!/usr/bin/env python3
"""Read exact Git repository baselines recorded by a verified Atlas run."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping, Optional, Sequence

import atlas_control

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment failure
    raise SystemExit("atlas_repository requires PyYAML (`python -m pip install pyyaml`)") from exc


REPORT_VERSION = 1
LFS_VERSION_LINE = b"version https://git-lfs.github.com/spec/v1"
OID_PATTERN = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")


@dataclass(frozen=True)
class BoundRepository:
    """One verified portable repository/baseline pair and its local route."""

    identity: str
    baseline: str
    source: Path
    git_dir: Path
    commit: str
    tree: str


@dataclass(frozen=True)
class TreeEntry:
    """One exact entry returned from an immutable baseline tree."""

    mode: str
    object_type: str
    oid: str
    path: str

    @property
    def is_gitlink(self) -> bool:
        return self.mode == "160000"

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "type": self.object_type,
            "oid": self.oid,
            "path": self.path,
            "gitlink": self.is_gitlink,
        }


@dataclass(frozen=True)
class Gap:
    code: str
    repository: Optional[str]
    problem: str
    resume_action: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "repository": self.repository,
            "problem": self.problem,
            "resume_action": self.resume_action,
        }


class RepositoryBlocked(RuntimeError):
    def __init__(self, code: str, problem: str, resume_action: str) -> None:
        super().__init__(problem)
        self.code = code
        self.problem = problem
        self.resume_action = resume_action


@dataclass(frozen=True)
class Verification:
    run: str
    config_path: Optional[Path]
    repositories: tuple[BoundRepository, ...]
    repository_rows: tuple[dict[str, Any], ...]
    gaps: tuple[Gap, ...]

    @property
    def verdict(self) -> str:
        return "PASS" if not self.gaps else "BLOCKED"

    def report(self) -> dict[str, Any]:
        return {
            "version": REPORT_VERSION,
            "command": "verify",
            "run": self.run,
            "config_path": str(self.config_path) if self.config_path is not None else None,
            "verdict": self.verdict,
            "repositories": list(self.repository_rows),
            "gaps": [gap.as_dict() for gap in self.gaps],
        }


def native_config_path() -> Path:
    if os.name == "nt":  # pragma: no cover - exercised on Windows
        root = os.environ.get("APPDATA")
        if root:
            return Path(root) / "atlas" / "config.yaml"
    root = os.environ.get("XDG_CONFIG_HOME")
    if root:
        return Path(root) / "atlas" / "config.yaml"
    return Path.home() / ".config" / "atlas" / "config.yaml"


def legacy_config_path() -> Path:
    return Path.home() / ".atlas" / "config.yaml"


def selected_config_path() -> Optional[Path]:
    native = native_config_path()
    if native.exists() or native.is_symlink():
        return native
    legacy = legacy_config_path()
    if legacy.exists() or legacy.is_symlink():
        return legacy
    return None


def load_machine_config() -> tuple[Optional[Path], Mapping[str, Any]]:
    """Load the selected native/legacy machine config as one validated map."""

    path = selected_config_path()
    if path is None:
        return None, {}
    try:
        data = atlas_control.load_yaml(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise RepositoryBlocked(
            "invalid_config",
            f"machine config is unreadable or malformed: {exc}",
            f"repair {path}",
        ) from exc
    if not isinstance(data, dict):
        raise RepositoryBlocked(
            "invalid_config", "machine config must be a map", f"repair {path}"
        )
    return path, data


def load_bindings() -> tuple[Optional[Path], Mapping[str, str]]:
    """Load the native bindings, or legacy bindings only when native is absent."""

    path, data = load_machine_config()
    if path is None:
        return None, {}
    repositories = data.get("repositories")
    if not isinstance(repositories, dict) or set(repositories) != {"bindings"}:
        raise RepositoryBlocked(
            "invalid_config",
            "machine config repositories must be an exact bindings map",
            f"repair repositories.bindings in {path}",
        )
    bindings = repositories.get("bindings")
    if not isinstance(bindings, dict):
        raise RepositoryBlocked(
            "invalid_config",
            "machine config repositories.bindings must be a map",
            f"repair repositories.bindings in {path}",
        )
    if any(
        not isinstance(identity, str)
        or not identity.strip()
        or not isinstance(source, str)
        or not source.strip()
        for identity, source in bindings.items()
    ):
        raise RepositoryBlocked(
            "invalid_config",
            "machine config bindings must map non-empty string identities to non-empty string paths",
            f"repair repositories.bindings in {path}",
        )
    return path, bindings


def repository_identity_for_location(
    location: Path,
    bindings: Mapping[str, str],
) -> Optional[str]:
    """Return the one configured stable identity whose Git root contains location."""

    try:
        root_raw = _git_text(
            ("rev-parse", "--show-toplevel"),
            source=location,
            code="repository_unavailable",
            problem="current location is not inside a readable Git repository",
            resume_action="open a configured repository",
        )
    except RepositoryBlocked:
        return None
    root = Path(root_raw).resolve(strict=True)
    matches = [
        identity
        for identity, raw_source in bindings.items()
        if _canonical_source(raw_source, identity) == root
    ]
    if len(matches) > 1:
        raise RepositoryBlocked(
            "ambiguous_binding",
            "multiple repository identities bind the current Git root",
            "keep one stable identity for this repository source",
        )
    return matches[0] if matches else None


def _git_environment() -> dict[str, str]:
    env = os.environ.copy()
    for name in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
    ):
        env.pop(name, None)
    env.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_LITERAL_PATHSPECS": "1",
        }
    )
    return env


def _git(
    arguments: Sequence[str],
    *,
    source: Optional[Path] = None,
    git_dir: Optional[Path] = None,
) -> subprocess.CompletedProcess[bytes]:
    if (source is None) == (git_dir is None):
        raise ValueError("exactly one of source or git_dir is required")
    prefix = ["git"]
    if source is not None:
        prefix.extend(("-C", str(source)))
    else:
        prefix.append(f"--git-dir={git_dir}")
    try:
        return subprocess.run(
            [*prefix, *arguments],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_git_environment(),
            check=False,
        )
    except OSError as exc:
        raise RepositoryBlocked(
            "git_unavailable", f"Git could not be executed: {exc}", "install or repair Git"
        ) from exc


def _git_text(
    arguments: Sequence[str],
    *,
    source: Optional[Path] = None,
    git_dir: Optional[Path] = None,
    code: str,
    problem: str,
    resume_action: str,
) -> str:
    result = _git(arguments, source=source, git_dir=git_dir)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        suffix = f": {detail}" if detail else ""
        raise RepositoryBlocked(code, problem + suffix, resume_action)
    try:
        return result.stdout.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise RepositoryBlocked(code, problem + ": Git returned non-UTF-8 output", resume_action) from exc


def _canonical_source(raw: str, identity: str) -> Path:
    source = Path(raw)
    if not source.is_absolute():
        raise RepositoryBlocked(
            "source_not_absolute",
            f"binding for {identity} is not an absolute path",
            "configure one canonical absolute Git source path",
        )
    try:
        resolved = source.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RepositoryBlocked(
            "source_unavailable",
            f"binding for {identity} does not resolve to an existing source: {exc}",
            "repair the machine-local repository binding",
        ) from exc
    if resolved != source:
        raise RepositoryBlocked(
            "source_symlink",
            f"binding for {identity} requires path or symlink substitution",
            "configure the real canonical source path directly",
        )
    if not source.is_dir() or not os.access(source, os.R_OK | os.X_OK):
        raise RepositoryBlocked(
            "source_unreadable",
            f"binding for {identity} is not a readable directory",
            "configure a readable Git repository or object source",
        )
    return source


def _discover_git_dir(source: Path, identity: str) -> Path:
    raw = _git_text(
        ("rev-parse", "--absolute-git-dir"),
        source=source,
        code="source_not_git",
        problem=f"binding for {identity} is not a readable Git repository/object source",
        resume_action="configure an already-usable local Git repository or object source",
    )
    git_dir = Path(raw)
    try:
        resolved = git_dir.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RepositoryBlocked(
            "source_not_git",
            f"Git object source for {identity} is unavailable: {exc}",
            "repair the local Git object source",
        ) from exc
    if not resolved.is_dir() or not os.access(resolved, os.R_OK | os.X_OK):
        raise RepositoryBlocked(
            "source_not_git",
            f"Git object source for {identity} is not readable",
            "repair the local Git object source",
        )
    return resolved


def probe_source(raw_source: str) -> None:
    """Prove only that an absolute canonical path is a readable local Git source."""

    source = _canonical_source(raw_source, "proposed source")
    git_dir = _discover_git_dir(source, "proposed source")
    if source == git_dir:
        return
    top_level_raw = _git_text(
        ("rev-parse", "--show-toplevel"),
        source=source,
        code="source_not_repository_root",
        problem="proposed source is not a repository worktree root or Git object source",
        resume_action="propose the canonical worktree root or Git directory directly",
    )
    try:
        top_level = Path(top_level_raw).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RepositoryBlocked(
            "source_not_repository_root",
            f"proposed repository root is unavailable: {exc}",
            "propose the canonical worktree root or Git directory directly",
        ) from exc
    if source != top_level:
        raise RepositoryBlocked(
            "source_not_repository_root",
            "proposed source is nested inside a repository rather than naming its canonical root",
            "propose the canonical worktree root or Git directory directly",
        )


def bind_repository(identity: str, baseline: str, raw_source: str) -> BoundRepository:
    source = _canonical_source(raw_source, identity)
    git_dir = _discover_git_dir(source, identity)
    commit_result = _git(
        ("rev-parse", "--verify", f"{baseline}^{{commit}}"), git_dir=git_dir
    )
    if commit_result.returncode != 0:
        object_result = _git(("cat-file", "-e", baseline), git_dir=git_dir)
        if object_result.returncode == 0:
            raise RepositoryBlocked(
                "baseline_not_commit",
                f"baseline for {identity} does not name a commit object",
                "correct the portable baseline through the legal intake path or a new run",
            )
        raise RepositoryBlocked(
            "baseline_unavailable",
            f"baseline for {identity} is not locally available",
            "provide the exact object locally or correct the portable baseline through the legal intake path",
        )
    try:
        commit = commit_result.stdout.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise RepositoryBlocked(
            "baseline_not_canonical",
            f"baseline for {identity} did not resolve to an ASCII canonical object ID",
            "record the full canonical commit object ID",
        ) from exc
    if commit != baseline or OID_PATTERN.fullmatch(commit) is None:
        raise RepositoryBlocked(
            "baseline_not_canonical",
            f"baseline for {identity} is not the full canonical commit object ID",
            "record the exact full canonical commit object ID",
        )
    tree = _git_text(
        ("rev-parse", "--verify", f"{baseline}^{{tree}}"),
        git_dir=git_dir,
        code="tree_unavailable",
        problem=f"baseline tree for {identity} is not locally readable",
        resume_action="repair the local Git object source",
    )
    if OID_PATTERN.fullmatch(tree) is None:
        raise RepositoryBlocked(
            "tree_unavailable",
            f"baseline tree for {identity} is not a canonical object ID",
            "repair the local Git object source",
        )
    return BoundRepository(identity, baseline, source, git_dir, commit, tree)


def verify_run(run_dir: Path) -> Verification:
    try:
        resolved_run = atlas_control.resolve_existing_run_directory(run_dir)
        _, effective = atlas_control.verified_state(resolved_run)
    except (OSError, UnicodeError, yaml.YAMLError, atlas_control.ControlError) as exc:
        gap = Gap(
            "invalid_stage0_state",
            None,
            f"verified Stage 0 state is unavailable: {exc}",
            "repair the Atlas run before repository inspection",
        )
        return Verification("", None, (), (), (gap,))

    run_identity = str(effective.get("run", ""))
    effective_repos = effective.get("repos")
    if not isinstance(effective_repos, list):  # verified_state should make this unreachable
        gap = Gap(
            "invalid_stage0_state",
            None,
            "verified Stage 0 state has no effective repositories",
            "repair the Atlas run before repository inspection",
        )
        return Verification(run_identity, None, (), (), (gap,))

    config_error: Optional[RepositoryBlocked] = None
    try:
        config_path, bindings = load_bindings()
    except RepositoryBlocked as exc:
        config_path = selected_config_path()
        bindings = {}
        config_error = exc

    bound: list[BoundRepository] = []
    rows: list[dict[str, Any]] = []
    gaps: list[Gap] = []
    for item in effective_repos:
        identity = str(item["repository"])
        baseline = str(item["baseline"])
        error = config_error
        if error is None and identity not in bindings:
            error = RepositoryBlocked(
                "missing_binding",
                f"no machine-local repository binding exists for {identity}",
                "configure repositories.bindings for this exact stable identity",
            )
        if error is None:
            try:
                repository = bind_repository(identity, baseline, bindings[identity])
            except RepositoryBlocked as exc:
                error = exc
            else:
                bound.append(repository)
                rows.append(
                    {
                        "repository": identity,
                        "baseline": baseline,
                        "source": str(repository.source),
                        "commit": repository.commit,
                        "tree": repository.tree,
                        "result": "PASS",
                        "gaps": [],
                    }
                )
                continue
        assert error is not None
        gap = Gap(error.code, identity, error.problem, error.resume_action)
        gaps.append(gap)
        rows.append(
            {
                "repository": identity,
                "baseline": baseline,
                "result": "BLOCKED",
                "gaps": [gap.as_dict()],
            }
        )
    return Verification(
        run_identity,
        config_path,
        tuple(bound),
        tuple(rows),
        tuple(gaps),
    )


def _parse_tree_entries(raw: bytes, repository: str) -> tuple[TreeEntry, ...]:
    entries: list[TreeEntry] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode, object_type, oid = metadata.decode("ascii").split(" ", 2)
            path = raw_path.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise RepositoryBlocked(
                "tree_unreadable",
                f"baseline tree for {repository} contains an unrepresentable entry",
                "repair or replace the local Git object source",
            ) from exc
        if OID_PATTERN.fullmatch(oid) is None:
            raise RepositoryBlocked(
                "tree_unreadable",
                f"baseline tree for {repository} returned a malformed object ID",
                "repair the local Git object source",
            )
        entries.append(TreeEntry(mode, object_type, oid, path))
    return tuple(entries)


def list_tree(repository: BoundRepository) -> tuple[TreeEntry, ...]:
    result = _git(("ls-tree", "-rz", "--full-tree", repository.tree), git_dir=repository.git_dir)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryBlocked(
            "tree_unavailable",
            f"baseline tree for {repository.identity} is not locally readable: {detail}",
            "repair the local Git object source",
        )
    return _parse_tree_entries(result.stdout, repository.identity)


def read_blob(repository: BoundRepository, oid: str) -> bytes:
    result = _git(("cat-file", "blob", oid), git_dir=repository.git_dir)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryBlocked(
            "blob_unavailable",
            f"blob {oid} for {repository.identity} is not locally readable: {detail}",
            "repair the local Git object source",
        )
    return result.stdout


def search_tree(repository: BoundRepository, needle: bytes) -> tuple[dict[str, Any], ...]:
    if not needle:
        raise RepositoryBlocked(
            "invalid_needle", "search needle must be non-empty", "provide a non-empty UTF-8 literal"
        )
    matches: list[dict[str, Any]] = []
    for entry in list_tree(repository):
        if entry.is_gitlink:
            raise RepositoryBlocked(
                "gitlink_content_unavailable",
                f"path {entry.path!r} is a Git submodule link, so repository-wide search is incomplete",
                "make required submodule content locally available outside Atlas and retry with an approved source policy",
            )
        if entry.object_type != "blob":
            continue
        content = read_blob(repository, entry.oid)
        if is_lfs_pointer(content):
            raise RepositoryBlocked(
                "lfs_content_unavailable",
                f"path {entry.path!r} is a Git LFS pointer, so repository-wide search is incomplete",
                "hydrate required LFS content outside Atlas and provide an approved readable source",
            )
        occurrences = content.count(needle)
        if occurrences:
            matches.append({"path": entry.path, "occurrences": occurrences})
    return tuple(matches)


def validate_tree_path(value: str) -> str:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise RepositoryBlocked(
            "invalid_tree_path",
            "tree path must be valid UTF-8",
            "provide one exact relative baseline tree path",
        ) from exc
    if (
        not value
        or "\x00" in value
        or Path(value).is_absolute()
        or PureWindowsPath(value).is_absolute()
        or ".." in value.split("/")
    ):
        raise RepositoryBlocked(
            "invalid_tree_path",
            "tree path must be a non-empty confined relative UTF-8 path without '..'",
            "provide one exact relative baseline tree path",
        )
    return value


def exact_tree_entry(repository: BoundRepository, path: str) -> TreeEntry:
    confined = validate_tree_path(path)
    result = _git(
        ("ls-tree", "-z", "--full-tree", repository.tree, "--", confined),
        git_dir=repository.git_dir,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryBlocked(
            "tree_unavailable",
            f"baseline tree for {repository.identity} is not locally readable: {detail}",
            "repair the local Git object source",
        )
    entries = _parse_tree_entries(result.stdout, repository.identity)
    exact = tuple(entry for entry in entries if entry.path == confined)
    if len(exact) != 1:
        raise RepositoryBlocked(
            "path_not_found",
            f"path {confined!r} is not one exact baseline tree entry",
            "provide one exact path from the baseline tree",
        )
    return exact[0]


def is_lfs_pointer(content: bytes) -> bool:
    lines = content.splitlines()
    if not lines or lines[0] != LFS_VERSION_LINE:
        return False
    has_oid = any(re.fullmatch(rb"oid sha256:[0-9a-f]{64}", line) for line in lines[1:])
    has_size = any(re.fullmatch(rb"size [0-9]+", line) for line in lines[1:])
    return has_oid and has_size


def read_tree_path(repository: BoundRepository, path: str) -> bytes:
    entry = exact_tree_entry(repository, path)
    if entry.is_gitlink:
        raise RepositoryBlocked(
            "gitlink_content_unavailable",
            f"path {path!r} is a Git submodule link, not referenced source content",
            "make required submodule content locally available outside Atlas and retry with an approved source policy",
        )
    if entry.object_type == "tree":
        raise RepositoryBlocked(
            "path_is_tree",
            f"path {path!r} is a tree, not a blob",
            "request one exact blob path",
        )
    if entry.object_type != "blob":
        raise RepositoryBlocked(
            "path_not_blob",
            f"path {path!r} is {entry.object_type}, not a blob",
            "request one exact blob path",
        )
    content = read_blob(repository, entry.oid)
    if is_lfs_pointer(content):
        raise RepositoryBlocked(
            "lfs_content_unavailable",
            f"path {path!r} is a Git LFS pointer, not referenced source content",
            "hydrate required LFS content outside Atlas and provide an approved readable source",
        )
    return content


def _repository_from_verification(
    verification: Verification, identity: str
) -> BoundRepository:
    if verification.verdict != "PASS":
        raise RepositoryBlocked(
            "repository_verification_blocked",
            "one or more effective repositories could not be verified",
            "resolve every reported repository gap and retry",
        )
    for repository in verification.repositories:
        if repository.identity == identity:
            return repository
    raise RepositoryBlocked(
        "repository_not_in_run",
        f"repository {identity!r} is not in the verified effective run",
        "select one exact effective repository identity",
    )


def _blocked_report(
    command: str,
    verification: Verification,
    error: Optional[RepositoryBlocked] = None,
    repository: Optional[str] = None,
) -> dict[str, Any]:
    if error is None:
        gaps = [gap.as_dict() for gap in verification.gaps]
    else:
        gaps = [Gap(error.code, repository, error.problem, error.resume_action).as_dict()]
    return {
        "version": REPORT_VERSION,
        "command": command,
        "run": verification.run,
        "repository": repository,
        "verdict": "BLOCKED",
        "gaps": gaps,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser(
        "probe-source", help="verify one proposed local Git source without a run"
    )
    probe.add_argument("--source", required=True)

    verify = sub.add_parser("verify", help="verify every effective repository baseline")
    verify.add_argument("--run", required=True, type=Path)

    listed = sub.add_parser("list", help="list the exact baseline tree")
    listed.add_argument("--run", required=True, type=Path)
    listed.add_argument("--repository", required=True)

    search = sub.add_parser("search", help="search baseline blob bytes for a UTF-8 literal")
    search.add_argument("--run", required=True, type=Path)
    search.add_argument("--repository", required=True)
    search.add_argument("--needle", required=True)

    read = sub.add_parser("read", help="write one exact baseline blob to stdout")
    read.add_argument("--run", required=True, type=Path)
    read.add_argument("--repository", required=True)
    read.add_argument("--path", required=True)
    return parser


def _write_json(report: Mapping[str, Any], stream: Any = sys.stdout) -> None:
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), file=stream)


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "probe-source":
        try:
            probe_source(args.source)
        except RepositoryBlocked as exc:
            _write_json(
                {
                    "version": REPORT_VERSION,
                    "command": "probe-source",
                    "verdict": "BLOCKED",
                    "gaps": [Gap(exc.code, None, exc.problem, exc.resume_action).as_dict()],
                }
            )
            return 1
        _write_json(
            {
                "version": REPORT_VERSION,
                "command": "probe-source",
                "verdict": "PASS",
                "gaps": [],
            }
        )
        return 0

    verification = verify_run(args.run)
    if args.command == "verify":
        _write_json(verification.report())
        return 0 if verification.verdict == "PASS" else 1

    if verification.verdict != "PASS":
        report = _blocked_report(args.command, verification, repository=args.repository)
        _write_json(report, sys.stderr if args.command == "read" else sys.stdout)
        return 1

    try:
        repository = _repository_from_verification(verification, args.repository)
        if args.command == "list":
            entries = list_tree(repository)
            _write_json(
                {
                    "version": REPORT_VERSION,
                    "command": "list",
                    "run": verification.run,
                    "repository": repository.identity,
                    "baseline": repository.baseline,
                    "tree": repository.tree,
                    "verdict": "PASS",
                    "entries": [entry.as_dict() for entry in entries],
                    "gaps": [],
                }
            )
            return 0
        if args.command == "search":
            try:
                needle = args.needle.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise RepositoryBlocked(
                    "invalid_needle",
                    "search needle must be valid UTF-8",
                    "provide a non-empty UTF-8 literal",
                ) from exc
            matches = search_tree(repository, needle)
            _write_json(
                {
                    "version": REPORT_VERSION,
                    "command": "search",
                    "run": verification.run,
                    "repository": repository.identity,
                    "baseline": repository.baseline,
                    "tree": repository.tree,
                    "needle": args.needle,
                    "verdict": "PASS",
                    "matches": list(matches),
                    "gaps": [],
                }
            )
            return 0
        content = read_tree_path(repository, args.path)
    except RepositoryBlocked as exc:
        report = _blocked_report(args.command, verification, exc, args.repository)
        _write_json(report, sys.stderr if args.command == "read" else sys.stdout)
        return 1

    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:  # pragma: no cover - ordinary CLI pipe closure
        raise SystemExit(1)
