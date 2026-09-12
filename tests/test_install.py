"""Exercise distributable artifacts, not just documentation phrases."""
import importlib.util
from pathlib import Path
import re
import shutil
from unittest.mock import patch
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
NAMES = sorted(path.name for path in (ROOT / "skills").iterdir() if path.is_dir())


class InstallationTests(unittest.TestCase):
    def test_all_bundles_are_independent_and_links_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            bundles = installer.install(Path(directory), NAMES)
            self.assertEqual(len(bundles), 5)
            for bundle in bundles:
                for shared in installer.SHARED:
                    self.assertEqual((bundle / "references" / shared).read_bytes(),
                                     (ROOT / shared).read_bytes())
                for file in bundle.rglob("*.md"):
                    for link in re.findall(r"\]\(([^)]+)\)", file.read_text()):
                        if "://" in link or link.startswith("#"):
                            continue
                        target = (file.parent / link.split("#")[0]).resolve()
                        self.assertTrue(target.is_relative_to(bundle.resolve()), link)
                        self.assertTrue(target.exists(), link)

    def test_existing_installation_is_preserved_before_any_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            existing = destination / NAMES[-1]
            existing.mkdir()
            sentinel = existing / "SKILL.md"
            sentinel.write_text("user modifications")
            with self.assertRaises(FileExistsError):
                installer.install(destination, NAMES)
            self.assertEqual(sentinel.read_text(), "user modifications")
            self.assertEqual(list(destination.iterdir()), [existing])

    def test_rejects_path_traversal_and_duplicate_names(self):
        with tempfile.TemporaryDirectory() as directory:
            for names in [["../outside"], [NAMES[0], NAMES[0]], []]:
                with self.assertRaises(ValueError):
                    installer.install(Path(directory), names)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_dangling_symlink_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            target = destination / NAMES[0]
            target.symlink_to(destination / "missing")
            with self.assertRaises(FileExistsError):
                installer.install(destination, [NAMES[0]])
            self.assertTrue(target.is_symlink())

    def test_local_personal_files_are_not_bundled(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            shutil.copytree(ROOT / "skills", source / "skills")
            for shared in installer.SHARED:
                shutil.copyfile(ROOT / shared, source / shared)
            skill = source / "skills" / NAMES[0]
            (skill / "profile.json").write_text('{"synthetic_private": true}')
            (skill / "personal-notes.md").write_text("synthetic private notes")
            (skill / "state").mkdir()
            (skill / "state" / "journal.jsonl").write_text("synthetic journal")
            with patch.object(installer, "ROOT", source):
                bundle = installer.install(Path(directory) / "output", [NAMES[0]])[0]
            self.assertFalse((bundle / "profile.json").exists())
            self.assertFalse((bundle / "personal-notes.md").exists())
            self.assertFalse((bundle / "state").exists())

    def test_linked_source_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            skill = source / "skills" / NAMES[0]
            skill.mkdir(parents=True)
            private = Path(directory) / "private.md"
            private.write_text("synthetic private content")
            (skill / "SKILL.md").symlink_to(private)
            with patch.object(installer, "ROOT", source):
                with self.assertRaises(ValueError):
                    installer.install(Path(directory) / "output", [NAMES[0]])
            self.assertFalse((Path(directory) / "output" / NAMES[0]).exists())

    def test_checkout_is_not_an_install_destination(self):
        with self.assertRaises(ValueError):
            installer.install(ROOT / "installed", [NAMES[0]])


if __name__ == "__main__":
    unittest.main()
