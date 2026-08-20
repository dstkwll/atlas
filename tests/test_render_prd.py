import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_atlas_control import write_decisions, write_prd, write_prd_html


ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "plugins" / "atlas" / "tools" / "render_prd.py"
RENDER_MODULE = runpy.run_path(str(RENDER))
SAFE_HREF = RENDER_MODULE["safe_href"]
WRITE_CANONICAL = RENDER_MODULE["write_canonical"]
RENDERER_VERSION = RENDER_MODULE["RENDERER_VERSION"]


def run_render(*args):
    return subprocess.run(
        [sys.executable, str(RENDER), *map(str, args)],
        text=True,
        capture_output=True,
    )


def run_verify_without_site_packages(*args):
    return subprocess.run(
        [sys.executable, "-S", str(RENDER), *map(str, args)],
        text=True,
        capture_output=True,
    )


class RenderPrdTests(unittest.TestCase):
    def write_run(self, run: Path) -> None:
        write_decisions(run)
        write_prd(run)

    def test_render_is_deterministic_for_identical_source_and_changes_with_input(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)

            first = run_render("render", "--run", run)

            self.assertEqual(first.returncode, 0, first.stderr)
            first_bytes = (run / "20-prd.html").read_bytes()

            second = run_render("render", "--run", run)

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((run / "20-prd.html").read_bytes(), first_bytes)

            with (run / "20-prd.md").open("a", encoding="utf-8") as handle:
                handle.write("\nchanged input\n")
            changed = run_render("render", "--run", run)

            self.assertEqual(changed.returncode, 0, changed.stderr)
            self.assertNotEqual((run / "20-prd.html").read_bytes(), first_bytes)

    def test_write_is_the_canonical_prd_write_path(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)
            draft = run / ".20-prd.next.md"
            proposed = (run / "20-prd.md").read_bytes() + b"\nfinal obligation\n"
            draft.write_bytes(proposed)

            result = run_render("write", "--run", run, "--draft", draft.name)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((run / "20-prd.md").read_bytes(), proposed)
            self.assertFalse(draft.exists())
            self.assertEqual(run_render("verify", "--run", run).returncode, 0)

    def test_write_refuses_every_draft_name_except_the_reserved_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)
            write_prd_html(run)
            control = run / "control.json"
            control.write_text('{"authority": "do not consume"}\n', encoding="utf-8")
            old_markdown = (run / "20-prd.md").read_bytes()
            old_html = (run / "20-prd.html").read_bytes()

            result = run_render("write", "--run", run, "--draft", control.name)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(".20-prd.next.md", result.stderr)
            self.assertEqual(control.read_text(encoding="utf-8"), '{"authority": "do not consume"}\n')
            self.assertEqual((run / "20-prd.md").read_bytes(), old_markdown)
            self.assertEqual((run / "20-prd.html").read_bytes(), old_html)

    def test_failed_render_before_install_preserves_the_last_canonical_markdown_and_html_pair(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)
            self.assertEqual(run_render("render", "--run", run).returncode, 0)
            old_markdown = (run / "20-prd.md").read_bytes()
            old_html = (run / "20-prd.html").read_bytes()
            draft = run / ".20-prd.next.md"
            draft.write_bytes(b"\xff\xfe\x00")

            result = run_render("write", "--run", run, "--draft", draft.name)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("valid UTF-8", result.stderr)
            self.assertEqual((run / "20-prd.md").read_bytes(), old_markdown)
            self.assertEqual((run / "20-prd.html").read_bytes(), old_html)
            self.assertTrue(draft.exists())

    def test_interrupted_pair_install_is_detected_as_stale(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)
            self.assertEqual(run_render("render", "--run", run).returncode, 0)
            draft = run / ".20-prd.next.md"
            draft.write_bytes((run / "20-prd.md").read_bytes() + b"\nnew requirement\n")
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
                    WRITE_CANONICAL(run, draft.name)

            stale = run_render("verify", "--run", run)

            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("sha256", stale.stderr.lower())

    def test_render_escapes_raw_html_and_disables_unsafe_links_while_preserving_safe_links(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)
            with (run / "20-prd.md").open("a", encoding="utf-8") as handle:
                handle.write(
                    "\n<script>alert('x')</script>\n"
                    "[unsafe](javascript:alert('x'))\n"
                    "[ftp](ftp://example.com/archive)\n"
                    "[editor](vscode://file/tmp/secret)\n"
                    "[safe](https://example.com/docs)\n"
                    "[relative](docs/requirements.md)\n"
                    "![remote image](https://example.com/tracker.png)\n"
                    "![protocol image](//example.com/tracker.png)\n"
                    "![relative image](assets/diagram.png)\n"
                )

            result = run_render("render", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)
            html = (run / "20-prd.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>alert('x')</script>", html)
            self.assertNotIn('href="javascript:alert(', html)
            self.assertNotIn('href="ftp://', html)
            self.assertNotIn('href="vscode://', html)
            self.assertIn("https://example.com/docs", html)
            self.assertIn("docs/requirements.md", html)
            self.assertNotIn('src="https://', html)
            self.assertNotIn('src="//example.com', html)
            self.assertIn('src="assets/diagram.png"', html)

    def test_href_policy_rejects_disguised_active_content(self):
        for href in (
            "javascript:alert(1)",
            " javascript:alert(1)",
            "\x00javascript:alert(1)",
            "data:text/html,boom",
            "file:///etc/passwd",
        ):
            with self.subTest(href=href):
                self.assertFalse(SAFE_HREF(href))

    def test_verify_detects_missing_and_stale_html_without_rendering(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)

            missing = run_render("verify", "--run", run)

            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("20-prd.html", missing.stderr)

            write_prd_html(run)
            fresh = run_render("verify", "--run", run)
            self.assertEqual(fresh.returncode, 0, fresh.stderr)

            with (run / "20-prd.md").open("a", encoding="utf-8") as handle:
                handle.write("\nstale now\n")
            stale = run_render("verify", "--run", run)

            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("sha256", stale.stderr.lower())

    def test_verify_rejects_duplicate_projection_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)
            write_prd_html(run)
            html = run / "20-prd.html"
            text = html.read_text(encoding="utf-8")
            marker = '  <meta name="atlas-source" content="20-prd.md">\n'
            self.assertIn(marker, text)
            html.write_text(text.replace(marker, marker + marker, 1), encoding="utf-8")

            result = run_render("verify", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate atlas metadata", result.stderr)

    def test_render_rejects_a_symlinked_managed_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = root / "run"
            run.mkdir()
            outside = root / "outside.md"
            outside.write_text("# outside\n", encoding="utf-8")
            (run / "20-prd.md").symlink_to(outside)

            result = run_render("render", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("managed path uses a symlink", result.stderr)

    def test_verify_rejects_a_wrong_renderer_version_directly(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)
            write_prd_html(run)
            html = run / "20-prd.html"
            text = html.read_text(encoding="utf-8")
            marker = f'<meta name="atlas-renderer-version" content="{RENDERER_VERSION}">'
            self.assertIn(marker, text)
            html.write_text(text.replace(marker, marker.replace(RENDERER_VERSION, "wrong-version"), 1), encoding="utf-8")

            result = run_render("verify", "--run", run)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("atlas-renderer-version", result.stderr)

    def test_verify_uses_only_the_standard_library_and_never_loads_the_renderer(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            self.write_run(run)
            write_prd_html(run)

            result = run_verify_without_site_packages("verify", "--run", run)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("verified 20-prd.html", result.stdout)


if __name__ == "__main__":
    unittest.main()
