#!/usr/bin/env python3
"""Render and verify Atlas System Design HTML projections."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


SOURCE_FILE = "30-system-design.md"
OUTPUT_FILE = "30-system-design.html"
RENDERER_VERSION = "1.0.0"
SAFE_SCHEMES = {"http", "https", "mailto"}
REQUIRED_VIEWS = (
    ("current-topology", "Current topology", ("Current system",)),
    ("proposed-topology", "Proposed topology", ("Proposed system",)),
    (
        "seam-ownership",
        "Seam and ownership",
        ("Responsibilities and seams", "Authoritative data ownership"),
    ),
    ("interface-contract", "Interface and contract", ("Contracts and interfaces",)),
    (
        "lifecycle-sequence-data-flow",
        "Lifecycle, sequence, and data flow",
        ("Lifecycle and data flow",),
    ),
    ("schema-protocol", "Schema and protocol", ("Schema and protocol",)),
    ("failure-recovery", "Failure and recovery", ("Failure and recovery",)),
    ("open-decisions", "Open decisions", ("Open decisions",)),
    ("rejected-alternatives", "Rejected alternatives", ("Rejected alternatives",)),
)
STYLE = """
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#111827;background:#f8fafc;margin:0}
main{max-width:80rem;margin:0 auto;padding:2rem}
.board{display:grid;grid-template-columns:repeat(auto-fit,minmax(20rem,1fr));gap:1rem}
.view{background:#fff;border:1px solid #cbd5e1;border-radius:.5rem;padding:1rem}
.view h2{margin-top:0;font-size:1.1rem}
.view h3{font-size:.95rem;color:#475569}
pre{white-space:pre-wrap;font:inherit;margin:0}
"""


class MetaParser(HTMLParser):
    NAMES = {"atlas-source", "atlas-source-sha256", "atlas-renderer-version"}

    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.duplicates: set[str] = set()
        self.malformed_attributes: set[str] = set()
        self.views: list[str] = []
        self.external_assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered_tag = tag.lower()
        pairs = {key.lower(): value or "" for key, value in attrs}
        view = pairs.get("data-atlas-view")
        if view:
            self.views.append(view)
        if lowered_tag in {"script", "img", "link", "iframe", "object", "embed", "audio", "video", "source"}:
            self.external_assets.append(lowered_tag)
        if lowered_tag != "meta":
            return
        keys = [key.lower() for key, _ in attrs]
        name = pairs.get("name")
        if name in self.NAMES:
            if keys.count("name") != 1 or keys.count("content") != 1:
                self.malformed_attributes.add(name)
            if name in self.meta:
                self.duplicates.add(name)
            self.meta[name] = pairs.get("content", "")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def managed_path(run_dir: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise SystemExit(f"render_system_design: invalid managed path: {relative}")
    current = run_dir
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise SystemExit(f"render_system_design: managed path uses a symlink: {relative}")
    return current


def markdown_sections(markdown: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^## ([^\n]+?)\s*$", markdown))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[match.group(1)] = markdown[match.end():end].strip()
    return sections


def safe_href(url: str) -> bool:
    if url != url.strip() or any(ord(character) < 0x20 or ord(character) == 0x7F for character in url):
        return False
    parsed = urlparse(url)
    if not parsed.scheme:
        lowered = url.lower()
        return url.startswith(("/", "#")) or not lowered.startswith(
            ("javascript:", "vbscript:", "data:", "file:")
        )
    return parsed.scheme.lower() in SAFE_SCHEMES


def markdown_renderer():
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:  # pragma: no cover - exercised by the CLI dependency contract
        raise SystemExit(
            "render_system_design render requires markdown-it-py; install it explicitly with "
            "`python3 -m pip install -r plugins/atlas/requirements.txt`"
        ) from exc
    parser = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
    parser.validateLink = safe_href

    def render_image(_renderer, tokens, index, options, env):
        return escape(tokens[index].content)

    parser.add_render_rule("image", render_image)
    return parser


def render_bytes(markdown_bytes: bytes) -> bytes:
    source_sha = hashlib.sha256(markdown_bytes).hexdigest()
    try:
        markdown = markdown_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError as exc:
        raise SystemExit("render_system_design: markdown is not valid UTF-8") from exc
    sections = markdown_sections(markdown)
    parser = markdown_renderer()
    cards = []
    for label, title, source_sections in REQUIRED_VIEWS:
        missing = [name for name in source_sections if not sections.get(name, "").strip()]
        if missing:
            raise SystemExit(
                "render_system_design: required board source section is missing or empty: "
                + ", ".join(missing)
            )
        content = []
        for section_name in source_sections:
            subtitle = f"<h3>{escape(section_name)}</h3>" if len(source_sections) > 1 else ""
            content.append(
                f'{subtitle}<div class="content">{parser.render(sections[section_name])}</div>'
            )
        cards.append(
            f'<section class="view" data-atlas-view="{label}">'
            f"<h2>{escape(title)}</h2>{''.join(content)}</section>"
        )
    board = "\n".join(cards)
    html = (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"  <meta name=\"atlas-source\" content=\"{SOURCE_FILE}\">\n"
        f"  <meta name=\"atlas-source-sha256\" content=\"{source_sha}\">\n"
        f"  <meta name=\"atlas-renderer-version\" content=\"{RENDERER_VERSION}\">\n"
        "  <title>Atlas System Design</title>\n"
        f"  <style>{STYLE.strip()}</style>\n"
        "</head>\n<body>\n<main>\n"
        "<h1>System Design board</h1>\n"
        f"<div class=\"board\">\n{board}\n</div>\n"
        "</main>\n</body>\n</html>\n"
    )
    return html.encode("utf-8")


def render(run_dir: Path) -> str:
    source = managed_path(run_dir, SOURCE_FILE)
    target = managed_path(run_dir, OUTPUT_FILE)
    rendered = render_bytes(source.read_bytes())
    fd, name = tempfile.mkstemp(prefix=".30-system-design.", suffix=".html", dir=run_dir)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(rendered)
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
    return f"rendered {OUTPUT_FILE}"


def write_canonical(run_dir: Path, draft_relative: str) -> str:
    if draft_relative != ".30-system-design.next.md":
        raise SystemExit("render_system_design: --draft must equal .30-system-design.next.md")
    draft = managed_path(run_dir, draft_relative)
    if not draft.is_file():
        raise SystemExit(f"render_system_design: draft is missing: {draft_relative}")
    proposed = draft.read_bytes()
    rendered = render_bytes(proposed)
    source_target = managed_path(run_dir, SOURCE_FILE)
    html_target = managed_path(run_dir, OUTPUT_FILE)
    markdown_fd, markdown_name = tempfile.mkstemp(
        prefix=".30-system-design.", suffix=".md", dir=run_dir
    )
    html_fd, html_name = tempfile.mkstemp(
        prefix=".30-system-design.", suffix=".html", dir=run_dir
    )
    markdown_temp = Path(markdown_name)
    html_temp = Path(html_name)
    try:
        with os.fdopen(markdown_fd, "wb") as handle:
            handle.write(proposed)
            handle.flush()
            os.fsync(handle.fileno())
        with os.fdopen(html_fd, "wb") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(markdown_temp, source_target)
        os.replace(html_temp, html_target)
        draft.unlink()
    finally:
        markdown_temp.unlink(missing_ok=True)
        html_temp.unlink(missing_ok=True)
    return f"wrote {SOURCE_FILE} and rendered {OUTPUT_FILE}"


def verify(run_dir: Path) -> str:
    source = managed_path(run_dir, SOURCE_FILE)
    target = managed_path(run_dir, OUTPUT_FILE)
    if not target.is_file():
        raise SystemExit(f"render_system_design: {OUTPUT_FILE} is missing")
    parser = MetaParser()
    parser.feed(target.read_text(encoding="utf-8"))
    if parser.duplicates:
        raise SystemExit(f"render_system_design: duplicate atlas metadata: {sorted(parser.duplicates)}")
    if parser.malformed_attributes:
        raise SystemExit(
            "render_system_design: duplicate metadata attribute: "
            f"{sorted(parser.malformed_attributes)}"
        )
    if parser.meta.get("atlas-source") != SOURCE_FILE:
        raise SystemExit(f"render_system_design: atlas-source must equal {SOURCE_FILE}")
    if parser.meta.get("atlas-source-sha256") != file_sha256(source):
        raise SystemExit("render_system_design: atlas-source-sha256 does not match the current markdown sha256")
    if parser.meta.get("atlas-renderer-version") != RENDERER_VERSION:
        raise SystemExit("render_system_design: atlas-renderer-version is missing or unknown")
    if parser.external_assets:
        raise SystemExit(
            f"render_system_design: projection is not self-contained: {sorted(parser.external_assets)}"
        )
    expected_views = [label for label, _, _ in REQUIRED_VIEWS]
    if parser.views != expected_views:
        missing = [label for label in expected_views if label not in parser.views]
        duplicates = sorted({label for label in parser.views if parser.views.count(label) > 1})
        raise SystemExit(
            "render_system_design: required board views are missing, duplicated, or out of order; "
            f"missing={missing} duplicates={duplicates}"
        )
    if target.read_bytes() != render_bytes(source.read_bytes()):
        raise SystemExit(
            "render_system_design: board bytes do not match the deterministic projection of "
            f"{SOURCE_FILE}"
        )
    return f"verified {OUTPUT_FILE}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    render_cmd = sub.add_parser("render")
    render_cmd.add_argument("--run", required=True, type=Path)
    write_cmd = sub.add_parser("write")
    write_cmd.add_argument("--run", required=True, type=Path)
    write_cmd.add_argument("--draft", required=True)
    verify_cmd = sub.add_parser("verify")
    verify_cmd.add_argument("--run", required=True, type=Path)
    return parser


def resolve_run_directory(path: Path) -> Path:
    if path.is_symlink():
        raise SystemExit("render_system_design: run directory may not be a symlink")
    resolved = path.resolve()
    if not resolved.is_dir():
        raise SystemExit(f"render_system_design: run directory does not exist: {path}")
    return resolved


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run_dir = resolve_run_directory(args.run)
        if args.command == "render":
            print(render(run_dir))
        elif args.command == "write":
            print(write_canonical(run_dir, args.draft))
        else:
            print(verify(run_dir))
        return 0
    except OSError as exc:
        print(f"render_system_design: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
