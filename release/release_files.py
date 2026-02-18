#!/usr/bin/env python3
import os
import re
from pathlib import Path

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = HERE + "/.."

blacklist = [
  ".git/",
  ".github/workflows/",

  "matlab.*.md",

  # build/runtime caches
  "__pycache__/",
  "\\.pyc$",
  "\\.pyo$",
  "\\.pytest_cache/",
  "\\.mypy_cache/",
  "\\.ruff_cache/",

  # no LFS or submodules in release
  ".lfsconfig",
  ".gitattributes",
  ".git$",
  ".gitmodules",
  ".run/",
  ".idea/",
]

# gets you through the blacklist
whitelist: list[str] = [
]


if __name__ == "__main__":
  for f in Path(ROOT).rglob("**/*"):
    if not (f.is_file() or f.is_symlink()):
      continue

    rf = str(f.relative_to(ROOT))
    blacklisted = any(re.search(p, rf) for p in blacklist)
    whitelisted = any(re.search(p, rf) for p in whitelist)
    if blacklisted and not whitelisted:
      continue

    print(rf)
