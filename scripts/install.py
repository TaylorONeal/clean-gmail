#!/usr/bin/env python3
"""Install self-contained skill bundles without overwriting existing skills."""
import argparse
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHARED = ("SECURITY.md", "PERSONALIZATION.md")
# Deliberate distribution manifest: never pick up local profiles or journals.
BUNDLE_FILES = {
    "gmail-cleanup-starter": ("SKILL.md",),
    "gmail-safe-trash-starter": ("SKILL.md",),
    "spam-cleanup": ("SKILL.md", "lists/allowlist.txt", "lists/denylist.txt"),
    "gmail-unsubscribe": (
        "SKILL.md", "README.md", "unsubscribe-config.yaml", "scheduled-task.md",
        "queue-template.md", "lists/always-cut.txt", "lists/never-touch.txt",
    ),
}


def install(destination: Path, names: list[str]) -> list[Path]:
    """Bundle references in a temporary directory, then publish new folders."""
    available = set(BUNDLE_FILES)
    if not names or len(names) != len(set(names)) or not set(names) <= available:
        raise ValueError("Choose distinct skill names from this repository.")
    destination = destination.expanduser().resolve()
    # Avoid accidentally installing personal/runtime material into this checkout.
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("Choose an installation directory outside the checkout.")
    for name in names:
        target = destination / name
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"Existing skill left unchanged: {target}")
    destination.mkdir(parents=True, exist_ok=True)
    installed = []
    with tempfile.TemporaryDirectory(prefix=".clean-gmail-", dir=destination) as staging:
        for name in names:
            bundle = Path(staging) / name
            bundle.mkdir()
            for relative in BUNDLE_FILES[name]:
                source = ROOT / "skills" / name / relative
                # Reject links, including a linked parent, rather than copying
                # private content from outside the intended source tree.
                if source.is_symlink() or any(parent.is_symlink()
                                             for parent in source.parents
                                             if ROOT in parent.parents):
                    raise ValueError(f"Symlink source is not distributable: {relative}")
                target = bundle / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            references = bundle / "references"
            references.mkdir(exist_ok=True)
            for filename in SHARED:
                source = ROOT / filename
                if source.is_symlink():
                    raise ValueError(f"Symlink reference is not distributable: {filename}")
                shutil.copyfile(source, references / filename)
            entrypoint = bundle / "SKILL.md"
            content = entrypoint.read_text()
            for filename in SHARED:
                content = content.replace(f"../../{filename}", f"references/{filename}")
            entrypoint.write_text(content)
        for name in names:
            target = destination / name
            # mkdir is exclusive, including against concurrent installers/symlinks.
            target.mkdir()
            installed.append(target)
            shutil.copytree(Path(staging) / name, target, dirs_exist_ok=True)
    return installed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", required=True, type=Path,
                        help="Host's skill directory; existing skills are never replaced")
    parser.add_argument("--skill", action="append", dest="names",
                        help="Skill to install (repeatable); default: all four")
    args = parser.parse_args()
    names = args.names or sorted(BUNDLE_FILES)
    try:
        for target in install(args.dest, names):
            print(f"Installed {target}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installation stopped: {error}\n"
                       "Existing skills were not overwritten. Inspect destination for partial new bundles.\n")


if __name__ == "__main__":
    main()
