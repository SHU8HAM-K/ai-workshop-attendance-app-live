#!/usr/bin/env python3
"""Rename the template for a new application. Run once, right after cloning.

    make init NAME=orders          # or: python3 scripts/init_project.py orders
    make init NAME=orders --dry-run

It rewrites four spellings of the placeholder across the repo:

    myapp        -> orders          python package, compose project, DB name
    MYAPP_       -> ORDERS_         environment variable prefix
    MyApp        -> Orders          window title, FastAPI title, UI heading
    myapp-       -> orders-         S3 bucket and npm package (hyphenated, since
                                    S3 bucket names cannot contain underscores)

then moves `backend/src/myapp/` to `backend/src/orders/` and deletes itself
along with the `make init` target, so the scaffolding leaves no trace.

Stdlib only, so it runs on a bare checkout before anything is installed.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PLACEHOLDER_SNAKE = "myapp"
PLACEHOLDER_UPPER = "MYAPP_"
PLACEHOLDER_PASCAL = "MyApp"

# Directories that are generated, vendored or version control — never rewritten.
# Note `.vscode` and `.claude` are NOT here: both are committed configuration
# that names the package (launch.json runs `myapp.main:app`), so skipping them
# would leave a debugger config pointing at a module that no longer exists.
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".idea", "htmlcov",
}
# Lockfiles ARE rewritten: both record the project's own package name, and a
# stale one breaks `uv sync --frozen` and `npm ci` in the Docker build.
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2", ".ttf",
    ".pdf", ".zip", ".db", ".sqlite", ".pyc", ".map",
}


def validate(name: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        sys.exit(
            f"error: '{name}' is not a valid name.\n"
            "Use lowercase letters, digits and underscores, starting with a letter "
            "(it becomes a Python package name). Examples: orders, patient_intake."
        )
    if name in {PLACEHOLDER_SNAKE, "app", "src", "test", "backend", "frontend"}:
        sys.exit(f"error: '{name}' would collide with an existing module name.")
    if len(name) > 40:
        sys.exit("error: pick something shorter than 40 characters.")
    return name


def replacements(name: str) -> list[tuple[str, str]]:
    kebab = name.replace("_", "-")
    pascal = "".join(part.capitalize() for part in name.split("_"))
    # Order matters: the hyphenated and prefixed forms must be replaced before
    # the bare "myapp", or "myapp-local" would become "orders-local" only by
    # luck and "MYAPP_" would already have lost its stem.
    return [
        (f"{PLACEHOLDER_SNAKE}-", f"{kebab}-"),
        (PLACEHOLDER_UPPER, f"{name.upper()}_"),
        (PLACEHOLDER_PASCAL, pascal),
        (PLACEHOLDER_SNAKE, name),
    ]


def candidate_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        files.append(path)
    return sorted(files)


def strip_init_target(makefile: Path) -> None:
    """Remove the `make init` target — it exists only for this one run."""
    text = makefile.read_text(encoding="utf-8")
    cleaned = re.sub(
        r"# >>> template-init.*?# <<< template-init\n", "", text, flags=re.DOTALL
    )
    # Tidy the now-orphaned `init` from .PHONY.
    cleaned = cleaned.replace(".PHONY: help init dev", ".PHONY: help dev")
    makefile.write_text(cleaned, encoding="utf-8")


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("-")]
    dry_run = "--dry-run" in argv
    if len(args) != 1:
        print(__doc__)
        return 2

    name = validate(args[0])
    rules = replacements(name)
    package_dir = ROOT / "backend" / "src" / PLACEHOLDER_SNAKE

    if not package_dir.is_dir():
        sys.exit(
            "error: backend/src/myapp not found — either this is not the template "
            "root, or `make init` has already been run here."
        )

    changed: list[tuple[Path, int]] = []
    for path in candidate_files():
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable; nothing to rewrite

        updated = original
        for old, new in rules:
            updated = updated.replace(old, new)

        if updated != original:
            hits = sum(original.count(old) for old, _ in rules)
            changed.append((path.relative_to(ROOT), hits))
            if not dry_run:
                path.write_text(updated, encoding="utf-8")

    if dry_run:
        print(f"Dry run — would rewrite {len(changed)} files for '{name}':\n")
        for path, hits in changed:
            print(f"  {path}  ({hits} replacements)")
        print(f"\n  backend/src/{PLACEHOLDER_SNAKE}/  ->  backend/src/{name}/")
        return 0

    # Move the package directory. `git mv` when possible so history follows the
    # rename instead of showing a delete plus an add.
    destination = package_dir.parent / name
    try:
        subprocess.run(
            ["git", "mv", str(package_dir), str(destination)],
            cwd=ROOT, check=True, capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        shutil.move(str(package_dir), str(destination))

    strip_init_target(ROOT / "Makefile")
    Path(__file__).unlink()

    print(
        f"""
✓ Renamed the template to '{name}' ({len(changed)} files, plus the package directory).

  Environment variables are now prefixed {name.upper()}_
  The Python package is  backend/src/{name}/
  This script and the `make init` target have removed themselves.

Next:
  1. make install          install backend + frontend dependencies
  2. make dev              http://localhost:5173  (API on :8000, docs at /docs)
  3. make check            lint, typecheck, dependency rule, tests — all green

Then read docs/adding-a-feature.md and replace the Note example with something
real. Deleting it is one commit: see the file list at the top of that doc.
"""
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
