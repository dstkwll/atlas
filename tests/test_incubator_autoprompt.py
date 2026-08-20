import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "incubator" / "skills" / "autoprompt"
PIN = "1a195165c5e54ce33fc357425a0b3af7a8dae96f"


class IncubatorAutopromptReferenceTests(unittest.TestCase):
    def test_reference_is_explicit_only_and_has_linked_files(self):
        content = (SKILL / "SKILL.md").read_text()
        self.assertTrue(content.startswith("---\n"))
        _, frontmatter, body = content.split("---\n", 2)
        metadata = yaml.safe_load(frontmatter)

        self.assertEqual(metadata["name"], "autoprompt")
        self.assertTrue(metadata["disable-model-invocation"])
        self.assertTrue(metadata["description"].startswith("Use only when explicitly asked"))
        self.assertLessEqual(len(metadata["description"]), 1024)
        self.assertIn("reference-only", body.lower())
        self.assertIn("NONCANONICAL PROPOSAL", body)
        self.assertNotIn("**Atlas status**", body)
        self.assertIn("Copilot CLI discovered this reference through `copilot skill list`", body)
        self.assertIn("Copilot content loading remains untested", body)
        self.assertNotIn("both hosts can inspect", body)
        self.assertNotIn("discovered and read successfully on Copilot CLI and Hermes", body)
        self.assertIn("/incubator:autoprompt", body)
        self.assertIn("/autoprompt", body)
        self.assertIn("/skill autoprompt", body)
        self.assertTrue((SKILL / "references" / "source-map.md").is_file())
        self.assertTrue((SKILL / "UPSTREAM-PIN.txt").is_file())

        openai = yaml.safe_load((SKILL / "agents" / "openai.yaml").read_text())
        self.assertFalse(openai["policy"]["allow_implicit_invocation"])

    def test_pin_and_status_are_consistent_across_reference_files(self):
        pin_text = (SKILL / "UPSTREAM-PIN.txt").read_text()
        source_map = (SKILL / "references" / "source-map.md").read_text()
        readme = (ROOT / "plugins" / "incubator" / "README.md").read_text()

        self.assertEqual(re.findall(r"^commit=([0-9a-f]{40})$", pin_text, re.MULTILINE), [PIN])
        self.assertIn(PIN, source_map)
        self.assertIn(PIN, readme)
        self.assertIn("reference / needs-reconciliation", readme)
        self.assertIn("canonical borrow decision is not present", (SKILL / "SKILL.md").read_text())
        self.assertIn("Noncanonical borrowing proposals", source_map)
        self.assertIn("not accepted Atlas status", source_map)
        self.assertIn("Updates are intentionally manual", source_map)
        self.assertIn("copilot skill list", readme)
        self.assertIn("hermes skills list", readme)
        self.assertIn("explicit-only enforcement on both hosts remains unverified", readme)
        self.assertIn("no Copilot CLI or Hermes runtime adapter", pin_text)

    def test_maturity_vocabulary_matches_canonical_architecture(self):
        architecture = (ROOT / "architecture" / "00-architecture-governance.md").read_text()
        maturity_block = architecture.split("### Maturity in our design", 1)[1].split(
            "A new repository review", 1
        )[0]
        canonical = re.findall(r"^([A-Z_]+)$", maturity_block, re.MULTILINE)

        skill_text = (SKILL / "SKILL.md").read_text()
        skill_line = next(line for line in skill_text.splitlines() if line.startswith("- **Maturity:**"))
        skill_line += next(
            line for line in skill_text.splitlines()[skill_text.splitlines().index(skill_line) + 1 :]
            if line.startswith("  `")
        )
        advertised = re.findall(r"`([A-Z_]+)`", skill_line)

        self.assertEqual(advertised, canonical)

    def test_incubator_manifests_are_synchronized(self):
        manifests = [
            json.loads((ROOT / "plugins" / "incubator" / "plugin.json").read_text()),
            json.loads(
                (ROOT / "plugins" / "incubator" / ".codex-plugin" / "plugin.json").read_text()
            ),
        ]

        for marketplace in [
            ROOT / ".github" / "plugin" / "marketplace.json",
            ROOT / ".agents" / "plugins" / "marketplace.json",
        ]:
            plugins = json.loads(marketplace.read_text())["plugins"]
            manifests.append(next(plugin for plugin in plugins if plugin["name"] == "incubator"))

        self.assertEqual([manifest["version"] for manifest in manifests], ["0.2.0"] * 4)
        descriptions = [manifest["description"] for manifest in manifests]
        self.assertEqual(len(set(descriptions)), 1)
        self.assertIn("source-pinned reference", descriptions[0])


if __name__ == "__main__":
    unittest.main()
