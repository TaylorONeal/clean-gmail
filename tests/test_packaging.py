"""Exercise portable installation checks without touching installed skills."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check", ROOT / "scripts/check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "skills", self.root / "skills")
        shutil.copytree(ROOT / "docs", self.root / "docs")
        shutil.copy2(ROOT / "SECURITY.md", self.root / "SECURITY.md")
        shutil.copy2(ROOT / "PERSONALIZATION.md", self.root / "PERSONALIZATION.md")
        self.skill = self.root / "skills/gmail-personal-assistant"

    def test_repository_is_portable(self):
        self.assertEqual(checker.check(self.root), [])

    def test_missing_collection_fails_cleanly(self):
        shutil.rmtree(self.root / "skills")
        self.assertTrue(checker.check(self.root))

    def test_empty_collection_does_not_pass(self):
        shutil.rmtree(self.root / "skills")
        (self.root / "skills").mkdir()
        self.assertTrue(checker.check(self.root))

    def test_missing_safety_blocks_validation(self):
        (self.skill / "references/SECURITY.md").unlink()
        self.assertTrue(checker.check(self.root))

    def test_drift_is_detected_and_sync_preserves_entrypoint(self):
        original = (self.skill / "SKILL.md").read_bytes()
        (self.root / "SECURITY.md").write_text("Updated safety contract\n")
        self.assertTrue(checker.check(self.root))
        self.assertEqual(checker.check(self.root, sync=True), [])
        self.assertEqual((self.skill / "SKILL.md").read_bytes(), original)

    def test_root_dependency_breaks_standalone_install(self):
        with (self.skill / "SKILL.md").open("a") as stream:
            stream.write("\n[Missing after installation](../../SECURITY.md)\n")
        self.assertTrue(checker.check(self.root))

    def test_missing_internal_reference_is_detected(self):
        with (self.skill / "SKILL.md").open("a") as stream:
            stream.write("\n[Missing](references/not-here.md)\n")
        self.assertTrue(checker.check(self.root))


if __name__ == "__main__":
    unittest.main()
