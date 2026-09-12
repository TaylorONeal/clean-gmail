#!/usr/bin/env python3
"""Check standalone skill packaging; optionally refresh shared references."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SHARED = {"SECURITY.md": ROOT / "SECURITY.md",
          "PERSONALIZATION.md": ROOT / "PERSONALIZATION.md"}


def check(root=ROOT, sync=False):
    errors = []
    shared = {name: root / path.relative_to(ROOT) for name, path in SHARED.items()}
    skills = root / "skills"
    if not skills.is_dir():
        return ["Missing skills directory"]
    folders = sorted(folder for folder in skills.iterdir() if folder.is_dir())
    if not folders:
        return ["No skill folders found"]
    for folder in folders:
        if not folder.is_dir():
            continue
        entry = folder / "SKILL.md"
        if not entry.exists():
            errors.append(f"{folder.name}: missing SKILL.md")
            continue
        text = entry.read_text()
        if not text.startswith(f"---\nname: {folder.name}\n") or "\ndescription: " not in text:
            errors.append(f"{folder.name}: invalid name/description frontmatter")
        for name, source in shared.items():
            target = folder / "references" / name
            if sync:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text())
            if not target.exists() or target.read_bytes() != source.read_bytes():
                errors.append(f"{folder.name}: shared reference drift: {name}")
        for doc in folder.rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", doc.read_text()):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                    continue
                target = (doc.parent / link.split("#")[0]).resolve()
                if folder.resolve() not in target.parents or not target.exists():
                    errors.append(f"{doc.relative_to(root)}: nonportable/missing link {link}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync", action="store_true")
    args = parser.parse_args()
    failures = check(sync=args.sync)
    print("\n".join(failures) if failures else "All standalone skills and shared references verified.")
    raise SystemExit(bool(failures))
