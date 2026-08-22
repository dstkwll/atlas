import hashlib
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "plugins" / "atlas" / "tools" / "render_system_design.py"

SECTIONS = (
    "Current system",
    "Proposed system",
    "Responsibilities and seams",
    "Authoritative data ownership",
    "Contracts and interfaces",
    "Schema and protocol",
    "Lifecycle and data flow",
    "Failure and recovery",
    "Compatibility",
    "Trust, security, and operations",
    "Rejected alternatives",
    "Open decisions",
)


def run_render(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(RENDER), *map(str, args)],
        cwd=cwd,
        text=True,
        capture_output=True,
    )


def write_system_design(run: Path, section_content=None) -> bytes:
    frontmatter = """---
run: demo
version: 1
status: draft
gate_ready: true
participation: co_design
opened: 2026-08-21
source_binding:
  kind: stage0
  artifact: run.yaml
  sha256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  effective_config_hash: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  effective_config_revision: 0
---

# System design — Demo

"""
    section_content = section_content or {}
    body = "\n".join(
        f"## {heading}\n\n{section_content.get(heading, f'Concrete {heading.lower()} decisions.')}\n"
        for heading in SECTIONS
    )
    content = (frontmatter + body).encode()
    (run / "30-system-design.md").write_bytes(content)
    return content


class RenderSystemDesignTests(unittest.TestCase):
    def test_render_is_deterministic_and_verify_accepts_current_metadata(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as caller_td:
            run = Path(td)
            source = write_system_design(run)

            first = run_render("render", "--run", run, cwd=caller_td)

            self.assertEqual(first.returncode, 0, first.stderr)
            first_bytes = (run / "30-system-design.html").read_bytes()
            self.assertIn(hashlib.sha256(source).hexdigest().encode(), first_bytes)
            self.assertIn(b'atlas-source\" content=\"30-system-design.md', first_bytes)

            second = run_render("render", "--run", run, cwd=caller_td)
            verified = run_render("verify", "--run", run, cwd=caller_td)

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((run / "30-system-design.html").read_bytes(), first_bytes)
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertIn("verified 30-system-design.html", verified.stdout)

    def test_verify_rejects_missing_stale_and_malformed_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            write_system_design(run)

            missing = run_render("verify", "--run", run)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("30-system-design.html", missing.stderr)

            self.assertEqual(run_render("render", "--run", run).returncode, 0)
            html = run / "30-system-design.html"
            source_marker = '<meta name="atlas-source" content="30-system-design.md">'
            text = html.read_text(encoding="utf-8")
            self.assertIn(source_marker, text)
            duplicate_attribute = source_marker.replace(
                'content="30-system-design.md"',
                'content="wrong" content="30-system-design.md"',
            )
            html.write_text(text.replace(source_marker, duplicate_attribute, 1), encoding="utf-8")
            malformed_attribute = run_render("verify", "--run", run)
            self.assertNotEqual(malformed_attribute.returncode, 0)
            self.assertIn("duplicate metadata attribute", malformed_attribute.stderr)

            self.assertEqual(run_render("render", "--run", run).returncode, 0)
            marker = '<meta name="atlas-renderer-version" content="1.0.0">'
            text = html.read_text(encoding="utf-8")
            self.assertIn(marker, text)
            html.write_text(text.replace(marker, marker.replace("1.0.0", "unknown"), 1), encoding="utf-8")
            malformed = run_render("verify", "--run", run)
            self.assertNotEqual(malformed.returncode, 0)
            self.assertIn("atlas-renderer-version", malformed.stderr)

            self.assertEqual(run_render("render", "--run", run).returncode, 0)
            with (run / "30-system-design.md").open("a", encoding="utf-8") as handle:
                handle.write("\nstale source\n")
            stale = run_render("verify", "--run", run)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("sha256", stale.stderr.lower())

    def test_verify_rejects_any_rendered_body_or_css_tampering(self):
        for mutation in ("card-text", "css-import"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                run = Path(td)
                write_system_design(run)
                self.assertEqual(run_render("render", "--run", run).returncode, 0)
                board = run / "30-system-design.html"
                text = board.read_text(encoding="utf-8")
                if mutation == "card-text":
                    text = text.replace("Concrete current system decisions.", "Tampered topology.", 1)
                else:
                    text = text.replace(
                        "body{",
                        '@import url("https://example.com/remote.css");body{',
                        1,
                    )
                board.write_text(text, encoding="utf-8")

                rejected = run_render("verify", "--run", run)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("deterministic projection", rejected.stderr)

    def test_board_has_every_stable_view_and_preserves_matching_inapplicability_reason(self):
        view_labels = (
            "current-topology",
            "proposed-topology",
            "seam-ownership",
            "interface-contract",
            "lifecycle-sequence-data-flow",
            "schema-protocol",
            "failure-recovery",
            "open-decisions",
            "rejected-alternatives",
        )
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            reason = "Inapplicable: no schema or protocol changes cross a system seam."
            write_system_design(run, {"Schema and protocol": reason})

            rendered = run_render("render", "--run", run)

            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            html_path = run / "30-system-design.html"
            html = html_path.read_text(encoding="utf-8")
            for label in view_labels:
                with self.subTest(label=label):
                    self.assertEqual(html.count(f'data-atlas-view="{label}"'), 1)
            self.assertIn(reason, html)
            self.assertNotIn("<script", html.lower())
            self.assertNotIn("<img", html.lower())
            self.assertNotIn("<link", html.lower())

            html_path.write_text(
                html.replace('data-atlas-view="failure-recovery"', 'data-removed-view="failure-recovery"', 1),
                encoding="utf-8",
            )
            missing_view = run_render("verify", "--run", run)
            self.assertNotEqual(missing_view.returncode, 0)
            self.assertIn("failure-recovery", missing_view.stderr)

    def test_board_renders_markdown_safely_without_external_assets(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            write_system_design(run, {
                "Current system": (
                    "- Existing worker owns dispatch.\n"
                    "- [Safe contract](https://example.com/contract)\n"
                    "- [Unsafe](javascript:alert(1))\n"
                    "<script>alert('x')</script>\n"
                    "![remote diagram](https://example.com/diagram.png)\n"
                    "![relative diagram](assets/diagram.png)"
                )
            })

            rendered = run_render("render", "--run", run)

            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            html = (run / "30-system-design.html").read_text(encoding="utf-8")
            self.assertIn("<ul>", html)
            self.assertIn('href="https://example.com/contract"', html)
            self.assertNotIn("<script>alert('x')</script>", html)
            self.assertNotIn('href="javascript:', html)
            self.assertNotIn("<img", html.lower())
            self.assertIn("remote diagram", html)
            self.assertIn("relative diagram", html)
            self.assertEqual(run_render("verify", "--run", run).returncode, 0)

            board = run / "30-system-design.html"
            board.write_text(
                html.replace("</body>", '<img src="https://example.com/tracker.png"></body>'),
                encoding="utf-8",
            )
            tampered = run_render("verify", "--run", run)
            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn("self-contained", tampered.stderr)

    def test_write_installs_markdown_and_board_only_from_reserved_draft(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            original = write_system_design(run)
            self.assertEqual(run_render("render", "--run", run).returncode, 0)
            old_html = (run / "30-system-design.html").read_bytes()
            proposed = original.replace(b"Concrete current system decisions.", b"Changed current topology.")
            draft = run / ".30-system-design.next.md"
            draft.write_bytes(proposed)

            written = run_render("write", "--run", run, "--draft", draft.name)

            self.assertEqual(written.returncode, 0, written.stderr)
            self.assertEqual((run / "30-system-design.md").read_bytes(), proposed)
            self.assertNotEqual((run / "30-system-design.html").read_bytes(), old_html)
            self.assertFalse(draft.exists())
            self.assertEqual(run_render("verify", "--run", run).returncode, 0)

            forbidden = run / "control.json"
            forbidden.write_text('{"do_not_consume": true}\n', encoding="utf-8")
            rejected = run_render("write", "--run", run, "--draft", forbidden.name)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn(".30-system-design.next.md", rejected.stderr)
            self.assertEqual(forbidden.read_text(encoding="utf-8"), '{"do_not_consume": true}\n')

            prior_markdown = (run / "30-system-design.md").read_bytes()
            prior_html = (run / "30-system-design.html").read_bytes()
            draft.write_bytes(b"\xff\xfe\x00")
            failed_render = run_render("write", "--run", run, "--draft", draft.name)
            self.assertNotEqual(failed_render.returncode, 0)
            self.assertIn("valid UTF-8", failed_render.stderr)
            self.assertEqual((run / "30-system-design.md").read_bytes(), prior_markdown)
            self.assertEqual((run / "30-system-design.html").read_bytes(), prior_html)
            self.assertTrue(draft.exists())

            draft.write_bytes(prior_markdown.replace(b"Changed current topology.", b"Interrupted topology."))
            write_canonical = runpy.run_path(str(RENDER))["write_canonical"]
            real_replace = os.replace
            calls = 0

            def fail_second_replace(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated interruption")
                return real_replace(source, destination)

            with mock.patch("os.replace", side_effect=fail_second_replace):
                with self.assertRaisesRegex(OSError, "simulated interruption"):
                    write_canonical(run, draft.name)
            mismatch = run_render("verify", "--run", run)
            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn("sha256", mismatch.stderr.lower())

    def test_commands_refuse_symlinked_run_and_reserved_draft(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = root / "run"
            run.mkdir()
            write_system_design(run)
            alias = root / "run-alias"
            alias.symlink_to(run, target_is_directory=True)

            aliased_run = run_render("render", "--run", alias)

            self.assertNotEqual(aliased_run.returncode, 0)
            self.assertIn("symlink", aliased_run.stderr.lower())
            self.assertFalse((run / "30-system-design.html").exists())

            outside = root / "outside.md"
            outside.write_bytes((run / "30-system-design.md").read_bytes())
            (run / ".30-system-design.next.md").symlink_to(outside)
            symlinked_draft = run_render(
                "write", "--run", run, "--draft", ".30-system-design.next.md"
            )
            self.assertNotEqual(symlinked_draft.returncode, 0)
            self.assertIn("symlink", symlinked_draft.stderr.lower())


if __name__ == "__main__":
    unittest.main()
