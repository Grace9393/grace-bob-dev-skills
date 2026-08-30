#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "sqlite-skill==0.2.2",
# ]
# [tool.uv.sources]
# sqlite-skill = { path = "../assets/wheels/sqlite_skill-0.2.2-py3-none-any.whl" }
# ///

from __future__ import annotations

import sys

from sqlite_skill.cli import main as sqlite_skill_main


def main() -> int:
    sqlite_skill_main(["get", *sys.argv[1:]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
