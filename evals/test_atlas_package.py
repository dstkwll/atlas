"""Structural checks for the Atlas package. They do not judge guidance prose."""
import json
from pathlib import Path
import re
import unittest

import test_satchel_package as satchel

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plugins/atlas'
SKILLS = sorted(path for path in (PACKAGE / 'skills').iterdir() if path.is_dir())
PAGES = sorted(PACKAGE.rglob('*.md'))
LINK = re.compile(r'\]\(([^)\s]+)\)')


def links(page):
    """Yield (target file, anchor) for each relative Markdown link in a page."""
    for target in LINK.findall(page.read_text()):
        if re.match(r'[a-z]+:', target):
            continue
        path, _, anchor = target.partition('#')
        yield ((page.parent / path).resolve() if path else page.resolve()), anchor


def anchors(page):
    """Heading anchors as GitHub renders them, including repeated-heading suffixes."""
    found, seen, fenced = set(), {}, False
    for line in page.read_text().splitlines():
        if line.startswith('```'):
            fenced = not fenced
        match = None if fenced else re.match(r'#{1,6}\s+(.*?)\s*$', line)
        if not match:
            continue
        slug = re.sub(r'[^\w\- ]', '', match.group(1).lower()).replace(' ', '-')
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        found.add(slug if not count else slug + '-' + str(count))
    return found


class AtlasPackage(unittest.TestCase):
    def test_package_has_the_lead_and_companion_skills(self):
        self.assertIn('atlas', [skill.name for skill in SKILLS])
        self.assertGreater(len(SKILLS), 1)

    def test_each_skill_is_named_for_its_folder_described_and_licensed(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                fields = satchel.frontmatter(skill)
                self.assertEqual(fields.get('name'), skill.name)
                self.assertTrue(fields.get('description', '').strip())
                self.assertTrue((skill / 'LICENSE').is_file())

    def test_manifest_marketplace_entry_and_metadata_versions_match(self):
        manifest = json.loads((PACKAGE / 'plugin.json').read_text())
        marketplace = json.loads((ROOT / '.github/plugin/marketplace.json').read_text())
        entries = [entry for entry in marketplace['plugins'] if entry['name'] == 'atlas']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['version'], manifest['version'])
        self.assertEqual(marketplace['metadata']['version'], manifest['version'])
        self.assertEqual((ROOT / entries[0]['source']).resolve(), PACKAGE)

    def test_relative_links_resolve_to_files_and_headings_inside_the_package(self):
        for page in PAGES:
            for target, anchor in links(page):
                with self.subTest(page=str(page.relative_to(ROOT)), target=str(target), anchor=anchor):
                    self.assertTrue(target.exists())
                    self.assertTrue(target.is_relative_to(PACKAGE))
                    if anchor and target.suffix == '.md':
                        self.assertIn(anchor, anchors(target))

    def test_every_reference_page_is_linked_from_another_package_page(self):
        linked = {target for page in PAGES for target, _ in links(page) if target != page.resolve()}
        for page in sorted((PACKAGE / 'skills/atlas/references').glob('*.md')):
            with self.subTest(page=page.name):
                self.assertIn(page.resolve(), linked)

    def test_agent_profile_preloads_only_packaged_skills(self):
        profiles = sorted((PACKAGE / 'com.github.copilot/agents').glob('*.agent.md'))
        self.assertTrue(profiles)
        names = {skill.name for skill in SKILLS}
        for profile in profiles:
            block = profile.read_text().split('\n---\n', 1)[0]
            listed = re.search(r'^skills: \[(.*)\]$', block, re.M)
            with self.subTest(profile=profile.name):
                self.assertIsNotNone(listed)
                preloaded = [name.strip() for name in listed.group(1).split(',') if name.strip()]
                self.assertTrue(preloaded)
                self.assertLessEqual(set(preloaded), names)


if __name__ == '__main__':
    unittest.main()
