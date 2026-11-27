"""Structural checks for the Satchel package. They do not judge skill prose."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plugins/satchel'
SKILLS = sorted(path for path in (PACKAGE / 'skills').iterdir() if path.is_dir())


def frontmatter(skill):
    text = (skill / 'SKILL.md').read_text()
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        return {}
    block = text[4:].split('\n---\n', 1)[0]
    fields = dict(line.split(': ', 1) for line in block.splitlines() if ': ' in line)
    return {key: value.strip().strip('"\'') for key, value in fields.items()}


class SatchelPackage(unittest.TestCase):
    def test_package_has_skills(self):
        self.assertTrue(SKILLS)

    def test_each_skill_is_named_for_its_folder_and_described(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                fields = frontmatter(skill)
                self.assertEqual(fields.get('name'), skill.name)
                self.assertTrue(fields.get('description', '').strip())

    def test_each_skill_folder_carries_a_license(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                self.assertTrue((skill / 'LICENSE').is_file() or (skill / 'LICENSE.txt').is_file())

    def test_readme_links_and_provenance_names_each_skill(self):
        readme = (PACKAGE / 'README.md').read_text()
        provenance = (PACKAGE / 'PROVENANCE.md').read_text()
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                self.assertIn('(skills/' + skill.name + '/SKILL.md)', readme)
                entry = r'(^## |`)' + re.escape(skill.name) + r'(`|$)'
                self.assertRegex(provenance, re.compile(entry, re.M))

    def test_relative_link_targets_exist(self):
        for page in sorted(PACKAGE.rglob('*.md')):
            for target in re.findall(r'\]\(([^)#\s]+)', page.read_text()):
                if re.match(r'[a-z]+:', target):
                    continue
                with self.subTest(page=str(page.relative_to(ROOT)), target=target):
                    self.assertTrue((page.parent / target).exists())

    def test_manifest_and_marketplace_versions_match(self):
        manifest = json.loads((PACKAGE / 'plugin.json').read_text())
        marketplace = json.loads((ROOT / '.github/plugin/marketplace.json').read_text())
        entries = [entry for entry in marketplace['plugins'] if entry['name'] == 'satchel']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['version'], manifest['version'])
        self.assertEqual((ROOT / entries[0]['source']).resolve(), PACKAGE)


if __name__ == '__main__':
    unittest.main()
