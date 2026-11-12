"""Regression checks: cleanup skills never trash codes or setup mail on arrival."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
STARTERS = ["gmail-safe-trash-starter", "gmail-cleanup-starter"]


def normalized(path):
    return re.sub(r"\s+", " ", path.read_text())


class FilterSafetyTests(unittest.TestCase):
    def test_starters_require_label_only_filters(self):
        for name in STARTERS:
            text = normalized(ROOT / "skills" / name / "SKILL.md")
            with self.subTest(skill=name):
                self.assertIn("the safe shape is label-only", text)
                self.assertIn("no Skip Inbox, no Mark as read, no Delete", text)
                self.assertIn("propose a label-only replacement", text)

    def test_starters_preserve_future_dated_codes(self):
        for name in STARTERS:
            text = normalized(ROOT / "skills" / name / "SKILL.md")
            with self.subTest(skill=name):
                self.assertIn("stays until that date passes", text)

    def test_security_contract_limits_filters_to_labels(self):
        text = normalized(ROOT / "SECURITY.md")
        self.assertIn("may only add a label", text)

    def test_no_skill_recommends_delete_on_arrival(self):
        pattern = re.compile(r"skip (the )?inbox\s*\+\s*delete", re.IGNORECASE)
        for doc in (ROOT / "skills").rglob("*.md"):
            with self.subTest(doc=str(doc.relative_to(ROOT))):
                self.assertIsNone(pattern.search(doc.read_text()))


if __name__ == "__main__":
    unittest.main()
