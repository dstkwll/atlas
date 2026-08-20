#!/usr/bin/env python3
"""Render and verify Atlas PRD HTML projections."""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


SOURCE_FILE = "20-prd.md"
OUTPUT_FILE = "20-prd.html"
RENDERER_VERSION = "1.0.0"
SAFE_SCHEMES = {"http", "https", "mailto"}
STYLE = """
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.5;color:#111827;background:#fff;margin:0}
main{max-width:56rem;margin:0 auto;padding:2rem 1.5rem 4rem}
h1,h2,h3{line-height:1.25}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
pre{overflow:auto;padding:1rem;background:#f3f4f6;border-radius:.5rem}
table{border-collapse:collapse;width:100%;margin:1rem 0}
th,td{border:1px solid #d1d5db;padding:.5rem;vertical-align:top}
a{color:#2563eb}
"""

class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.duplicates: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta":
            return
        pairs = {key.lower(): value or "" for key, value in attrs}
        name = pairs.get("name")
        if name in {"atlas-source", "atlas-source-sha256", "atlas-renderer-version"}:
            if name in self.meta:
                self.duplicates.add(name)
            self.meta[name] = pairs.get("content", "")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_markdown(markdown_bytes: bytes) -> str:
    return markdown_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


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


def render_bytes(markdown_bytes: bytes) -> bytes:
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:  # pragma: no cover - exercised by the CLI dependency contract
        raise SystemExit(
            "render_prd render requires markdown-it-py; install it explicitly with "
            "`python3 -m pip install -r plugins/atlas/requirements.txt`"
        ) from exc

    source_sha = hashlib.sha256(markdown_bytes).hexdigest()
    try:
        markdown = normalize_markdown(markdown_bytes)
    except UnicodeDecodeError as exc:
        raise SystemExit("render_prd: markdown is not valid UTF-8") from exc
    parser = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
    parser.validateLink = safe_href
    default_image_rule = getattr(parser.renderer, "image")

    def render_image(_renderer, tokens, index, options, env):
        token = tokens[index]
        source = token.attrGet("src") or ""
        parsed = urlparse(source)
        if parsed.scheme or source.startswith("//"):
            return escape(token.content)
        return default_image_rule(tokens, index, options, env)

    parser.add_render_rule("image", render_image)
    tokens = parser.parse(markdown)
    body = parser.renderer.render(tokens, parser.options, {})
    html = (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"  <meta name=\"atlas-source\" content=\"{SOURCE_FILE}\">\n"
        f"  <meta name=\"atlas-source-sha256\" content=\"{source_sha}\">\n"
        f"  <meta name=\"atlas-renderer-version\" content=\"{RENDERER_VERSION}\">\n"
        "  <title>Atlas PRD</title>\n"
        f"  <style>{STYLE.strip()}</style>\n"
        "</head>\n"
        "<body>\n"
        "<main>\n"
        f"{body}"
        "\n</main>\n"
        "</body>\n"
        "</html>\n"
    )
    return html.encode("utf-8")


def managed_path(run_dir: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise SystemExit(f"render_prd: invalid managed path: {relative}")
    current = run_dir
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise SystemExit(f"render_prd: managed path uses a symlink: {relative}")
    return current


def render(run_dir: Path) -> str:
    source = managed_path(run_dir, SOURCE_FILE)
    target = managed_path(run_dir, OUTPUT_FILE)
    rendered = render_bytes(source.read_bytes())
    fd, name = tempfile.mkstemp(prefix=".20-prd.", suffix=".html", dir=run_dir)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(rendered)
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
    return f"rendered {OUTPUT_FILE}"


def write_canonical(run_dir: Path, draft_relative: str) -> str:
    if draft_relative != ".20-prd.next.md":
        raise SystemExit("render_prd: --draft must equal .20-prd.next.md")
    draft = managed_path(run_dir, draft_relative)
    if not draft.is_file():
        raise SystemExit(f"render_prd: draft is missing: {draft_relative}")

    proposed = draft.read_bytes()
    rendered = render_bytes(proposed)
    source_target = managed_path(run_dir, SOURCE_FILE)
    html_target = managed_path(run_dir, OUTPUT_FILE)
    markdown_fd, markdown_name = tempfile.mkstemp(prefix=".20-prd.", suffix=".md", dir=run_dir)
    html_fd, html_name = tempfile.mkstemp(prefix=".20-prd.", suffix=".html", dir=run_dir)
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
        raise SystemExit("render_prd: 20-prd.html is missing")
    parser = MetaParser()
    parser.feed(target.read_text(encoding="utf-8"))
    if parser.duplicates:
        raise SystemExit(f"render_prd: duplicate atlas metadata: {sorted(parser.duplicates)}")
    meta = parser.meta
    if meta.get("atlas-source") != SOURCE_FILE:
        raise SystemExit("render_prd: atlas-source must equal 20-prd.md")
    if meta.get("atlas-source-sha256") != file_sha256(source):
        raise SystemExit("render_prd: atlas-source-sha256 does not match the current markdown sha256")
    if meta.get("atlas-renderer-version") != RENDERER_VERSION:
        raise SystemExit("render_prd: atlas-renderer-version is missing or unknown")
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


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_dir = args.run.resolve()
    try:
        if args.command == "render":
            print(render(run_dir))
        elif args.command == "write":
            print(write_canonical(run_dir, args.draft))
        else:
            print(verify(run_dir))
        return 0
    except OSError as exc:
        print(f"render_prd: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
