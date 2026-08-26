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
RENDERER_VERSION = "2.0.0"
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
:root{color-scheme:light;--bg:#f4f6fa;--surface:#fff;--surface-soft:#f8fafc;--text:#172033;--muted:#5d6b82;--line:#d8e0ec;--accent:#165dce;--accent-soft:#eaf2ff;--code:#101827;--code-text:#e7eef9;--font:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;--mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}
*{box-sizing:border-box}
html{background:var(--bg);scroll-behavior:smooth}
body{font-family:var(--font);color:var(--text);background:var(--bg);line-height:1.58;margin:0;overflow-wrap:anywhere}
main{width:min(100%,68rem);margin:0 auto;padding:clamp(1rem,4vw,3rem)}
.board-header{padding:.5rem 0 clamp(1.25rem,4vw,2.5rem)}
.eyebrow{color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.12em;margin:0 0 .45rem;text-transform:uppercase}
.board-header h1{font-size:clamp(2rem,7vw,3.5rem);letter-spacing:-.045em;line-height:1.04;margin:0}
.lede{color:var(--muted);font-size:clamp(1rem,2.8vw,1.15rem);margin:.8rem 0 1.1rem;max-width:60ch}
.board-nav{display:flex;flex-wrap:wrap;gap:.45rem}
.board-nav a{align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:999px;color:var(--text);display:inline-flex;font-size:.8rem;font-weight:650;min-height:44px;padding:.4rem .75rem;text-decoration:none}
.board-nav a:focus-visible,.board-nav a:hover{border-color:var(--accent);outline:2px solid var(--accent-soft);outline-offset:2px}
.board{display:grid;grid-template-columns:minmax(0,1fr);gap:clamp(.85rem,2.5vw,1.35rem)}
.view{background:var(--surface);border:1px solid var(--line);border-radius:1rem;box-shadow:0 1px 2px rgba(15,23,42,.05);min-width:0;padding:clamp(1rem,3.5vw,2rem);scroll-margin-top:1rem}
.view h2{font-size:clamp(1.35rem,4.5vw,1.85rem);letter-spacing:-.025em;line-height:1.15;margin:0 0 1rem}
.view h3{border-top:1px solid var(--line);color:var(--muted);font-size:.8rem;letter-spacing:.08em;margin:1.5rem 0 .75rem;padding-top:1rem;text-transform:uppercase}
.content{min-width:0}
.content>:first-child{margin-top:0}.content>:last-child{margin-bottom:0}
p,li{max-width:76ch}
a{color:var(--accent);text-decoration-thickness:.08em;text-underline-offset:.16em}
ul,ol{padding-left:1.35rem}
code{background:var(--accent-soft);border-radius:.3rem;font-family:var(--mono);font-size:.88em;padding:.12rem .3rem}
.code-scroll,.diagram-scroll{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.code-scroll{background:var(--code);border-radius:.75rem;margin:1rem 0}
pre{font-family:var(--mono);font-size:.82rem;line-height:1.5;margin:0;min-width:max-content;padding:1rem;white-space:pre}
pre code{background:transparent;color:var(--code-text);font-size:inherit;padding:0}
.diagram{margin:1rem 0}
.diagram-scroll{background:var(--code);border:1px solid #24324a;border-radius:.75rem}
.diagram figcaption{color:var(--muted);font-size:.75rem;margin-top:.45rem}
.table-scroll{border:1px solid var(--line);border-radius:.75rem;margin:1rem 0;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;min-width:44rem;width:100%}
th,td{border-bottom:1px solid var(--line);padding:.72rem .8rem;text-align:left;vertical-align:top}
th{background:var(--surface-soft);color:var(--muted);font-size:.75rem;letter-spacing:.05em;text-transform:uppercase}
tbody tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:#fbfcfe}
blockquote{border-left:.25rem solid var(--accent);color:var(--muted);margin:1rem 0;padding:.15rem 0 .15rem 1rem}
@media (max-width:48rem){
  main{padding:.75rem}
  .board-header{padding:.5rem .25rem 1.25rem}
  .view{border-radius:.8rem;padding:1rem}
  .table-scroll{border:0;overflow:visible}
  table,thead,tbody,tr,th,td{display:block;min-width:0;width:100%}
  thead{height:1px;margin:-1px;overflow:hidden;padding:0;position:absolute;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap;width:1px}
  tbody{display:grid;gap:.7rem}
  tbody tr{background:var(--surface-soft);border:1px solid var(--line);border-radius:.7rem;overflow:hidden}
  tbody tr:nth-child(even){background:var(--surface-soft)}
  td{border-bottom:1px solid var(--line);display:grid;gap:.65rem;grid-template-columns:minmax(6.5rem,34%) minmax(0,1fr);padding:.65rem .75rem}
  td:last-child{border-bottom:0}
  td::before{color:var(--muted);content:attr(data-label);font-size:.7rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
  .diagram-scroll{margin-inline:-.15rem}
  .diagram pre{font-size:.72rem}
}
@media (prefers-color-scheme:dark){
  :root{color-scheme:dark;--bg:#0d1420;--surface:#141d2b;--surface-soft:#192436;--text:#edf2f9;--muted:#aab7ca;--line:#2d3b50;--accent:#78a9ff;--accent-soft:#1a3154;--code:#080d16;--code-text:#e7eef9}
  tbody tr:nth-child(even){background:#172234}
}
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


def inline_text(token) -> str:
    if not token.children:
        return token.content.strip()
    parts = []
    for child in token.children:
        if child.type in {"text", "code_inline"}:
            parts.append(child.content)
        elif child.type in {"softbreak", "hardbreak"}:
            parts.append(" ")
    return "".join(parts).strip()


def table_headers(tokens, table_index: int) -> list[str]:
    headers = []
    index = table_index + 1
    while index < len(tokens) and tokens[index].type != "thead_close":
        if tokens[index].type == "th_open" and index + 1 < len(tokens):
            headers.append(inline_text(tokens[index + 1]))
        index += 1
    return headers


def table_column(tokens, index: int) -> tuple[list[str], int]:
    table_index = next(
        position for position in range(index, -1, -1)
        if tokens[position].type == "table_open"
    )
    row_index = next(
        position for position in range(index, table_index, -1)
        if tokens[position].type == "tr_open"
    )
    column = sum(1 for token in tokens[row_index:index] if token.type == "td_open")
    return table_headers(tokens, table_index), column


def markdown_renderer():
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:  # pragma: no cover - exercised by the CLI dependency contract
        raise SystemExit(
            "render_system_design render requires markdown-it-py; install it explicitly with "
            "`python3 -m pip install -r plugins/atlas/requirements.txt`"
        ) from exc
    parser = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
    parser.enable("table")
    parser.validateLink = safe_href

    def render_image(_renderer, tokens, index, options, env):
        return escape(tokens[index].content)

    def render_table_open(_renderer, _tokens, _index, _options, _env):
        return '<div class="table-scroll" role="region" aria-label="Comparison table"><table>\n'

    def render_table_close(_renderer, _tokens, _index, _options, _env):
        return "</table></div>\n"

    def render_table_cell_open(_renderer, tokens, index, _options, _env):
        headers, column = table_column(tokens, index)
        label = headers[column] if column < len(headers) else ""
        return f'<td data-label="{escape(label, quote=True)}">'

    def render_fence(_renderer, tokens, index, _options, _env):
        token = tokens[index]
        info = token.info.strip().split(maxsplit=1)[0] if token.info.strip() else ""
        language = re.sub(r"[^a-zA-Z0-9_-]", "", info)
        class_name = f' class="language-{language}"' if language else ""
        code = escape(token.content)
        if language in {"text", "mermaid"}:
            label = "Mermaid source" if language == "mermaid" else "Text diagram"
            caption = (
                "Mermaid source — not rendered."
                if language == "mermaid"
                else "Diagram — scroll horizontally if needed."
            )
            return (
                '<figure class="diagram">'
                f'<div class="diagram-scroll" role="region" aria-label="{label}" tabindex="0">'
                f"<pre><code{class_name}>{code}</code></pre></div>"
                f"<figcaption>{caption}</figcaption></figure>\n"
            )
        return (
            '<div class="code-scroll" role="region" aria-label="Code block" tabindex="0">'
            f"<pre><code{class_name}>{code}</code></pre></div>\n"
        )

    parser.add_render_rule("image", render_image)
    parser.add_render_rule("table_open", render_table_open)
    parser.add_render_rule("table_close", render_table_close)
    parser.add_render_rule("td_open", render_table_cell_open)
    parser.add_render_rule("fence", render_fence)
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
            f'<section class="view" id="view-{label}" data-atlas-view="{label}">'
            f"<h2>{escape(title)}</h2>{''.join(content)}</section>"
        )
    board = "\n".join(cards)
    title_match = re.search(r"(?m)^# ([^\n]+?)\s*$", markdown)
    document_title = title_match.group(1) if title_match else "System Design"
    navigation = "".join(
        f'<a href="#view-{label}">{escape(title)}</a>'
        for label, title, _ in REQUIRED_VIEWS
    )
    html = (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"  <meta name=\"atlas-source\" content=\"{SOURCE_FILE}\">\n"
        f"  <meta name=\"atlas-source-sha256\" content=\"{source_sha}\">\n"
        f"  <meta name=\"atlas-renderer-version\" content=\"{RENDERER_VERSION}\">\n"
        f"  <title>{escape(document_title)}</title>\n"
        f"  <style>{STYLE.strip()}</style>\n"
        "</head>\n<body>\n<main>\n"
        '<header class="board-header">'
        '<p class="eyebrow">Atlas planning artifact</p>'
        f"<h1>{escape(document_title)}</h1>"
        '<p class="lede">A self-contained decision board projected from the canonical Markdown. '
        'The Markdown remains authoritative.</p>'
        f'<nav class="board-nav" aria-label="System Design views">{navigation}</nav>'
        "</header>\n"
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
