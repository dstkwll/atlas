import tempfile
import unittest
from pathlib import Path

from tools.check_architecture import SEPARATOR, validate_repository


class CheckArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.repository_root = Path(self.temporary_directory.name)
        self.architecture_dir = self.repository_root / "architecture"
        self.architecture_dir.mkdir()

    def write_document(self, name, content):
        path = self.architecture_dir / name
        path.write_bytes(content)
        return path

    def write_monolith(self, *contents):
        (self.architecture_dir / "rolling-monolith.md").write_bytes(
            SEPARATOR.join(contents)
        )

    def test_correct_monolith_succeeds(self):
        first = b"# First\n\nExact content.  \n"
        second = b"# Second\n\nFinal line\n"
        self.write_document("00-first.md", first)
        self.write_document("01-second.md", second)
        self.write_monolith(first, second)

        status, _ = validate_repository(self.repository_root)

        self.assertEqual(status, 0)

    def test_changed_source_with_stale_monolith_is_drift(self):
        original = b"# Original\n"
        self.write_document("00-source.md", b"# Changed\n")
        self.write_monolith(original)

        status, message = validate_repository(self.repository_root)

        self.assertEqual(status, 1)
        self.assertIn("drift", message)

    def test_independently_changed_monolith_is_drift(self):
        source = b"# Source\n"
        self.write_document("00-source.md", source)
        self.write_monolith(b"# Independently changed\n")

        status, message = validate_repository(self.repository_root)

        self.assertEqual(status, 1)
        self.assertIn("first difference", message)

    def test_documents_are_assembled_in_canonical_filename_order(self):
        second = b"# Second\n"
        first = b"# First\n"
        self.write_document("02-second.md", second)
        self.write_document("01-first.md", first)
        self.write_monolith(first, second)

        status, _ = validate_repository(self.repository_root)

        self.assertEqual(status, 0)

    def test_missing_monolith_is_validator_error(self):
        self.write_document("00-source.md", b"# Source\n")

        status, message = validate_repository(self.repository_root)

        self.assertEqual(status, 2)
        self.assertIn("missing", message)

    def test_no_canonical_documents_is_validator_error(self):
        self.write_monolith(b"")

        status, message = validate_repository(self.repository_root)

        self.assertEqual(status, 2)
        self.assertIn("no canonical", message)


if __name__ == "__main__":
    unittest.main()
