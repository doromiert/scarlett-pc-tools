"""Reject unexpected artifacts from the Git index, including force-added binaries."""
from pathlib import PurePosixPath
import subprocess
import sys

ALLOWED = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}
SPECIAL = {".gitignore", ".gitattributes", "LICENSE"}
MAX_BYTES = 256 * 1024


def check():
    names = subprocess.check_output(["git", "ls-files", "-z"]).split(b"\0")
    errors = []
    for raw in filter(None, names):
        name = raw.decode("utf-8")
        p = PurePosixPath(name)
        if p.suffix not in ALLOWED and p.name not in SPECIAL:
            errors.append(f"Unapproved tracked file type: {name}")
            continue
        # Check staged bytes rather than a possibly different working-tree file.
        content = subprocess.check_output(["git", "show", ":" + name])
        if len(content) > MAX_BYTES or b"\0" in content:
            errors.append(f"Binary or oversized tracked file: {name}")
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"Non-UTF-8 tracked content: {name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Tracked tree contains only small, approved text files.")
    return 0


if __name__ == "__main__":
    sys.exit(check())
