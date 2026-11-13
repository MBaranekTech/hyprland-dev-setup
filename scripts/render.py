#!/usr/bin/env python3
"""Render portable home-directory templates into a separate preview directory."""
import argparse
from pathlib import Path
import re
import shutil


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home(),
                        help="Home path to substitute into the generated configuration")
    parser.add_argument("--output", type=Path, default=root / ".rendered",
                        help="New or empty destination; defaults to ignored .rendered/")
    args = parser.parse_args()
    home = args.home.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("The output directory must be new or empty.")
    if output in (home, root) or output in root.parents:
        parser.error("Choose a separate preview directory.")
    if not re.fullmatch(r"/[A-Za-z0-9_./-]+", str(home)):
        parser.error("Use a standard Linux home path without whitespace or shell metacharacters.")
    output.mkdir(parents=True, exist_ok=True)
    count = 0
    for source in sorted((root / "templates/home").rglob("*")):
        if not source.is_file():
            continue
        target = output / source.relative_to(root / "templates/home")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text().replace("@HOME@", str(home)))
        shutil.copymode(source, target)
        count += 1
    print(f"Rendered {count} files into {output}")
    print("Review the generated files before installing them. Your live configuration was not changed.")


if __name__ == "__main__":
    main()
