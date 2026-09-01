#!/usr/bin/env python3
"""
Create SQLite FTS5 database from WCAG22 markdown files.
"""

import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from common.markdown_db_builder import (
    process_markdown_files,
    create_fts_database,
)

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references" / "wcag"
DB_FILE = SKILL_DIR / "wcag22-guidelines.sqlite"
SQL_SCHEMA_FILE = SCRIPT_DIR / "db.sql"
DEBUG_DUMP_DIR = Path("~/tmp/wcag22-tmp").expanduser()
REMOVE_SECTIONS = set()
REMOVE_LINE_CONTAINS = set()


def create_database() -> bool:
    """Create the SQLite FTS5 database from markdown files."""

    try:
        rows = process_markdown_files(
            REFERENCES_DIR,
            remove_sections=REMOVE_SECTIONS,
            remove_line_contains=REMOVE_LINE_CONTAINS,
            debug_dump_dir=DEBUG_DUMP_DIR,
        )

        count = create_fts_database(
            DB_FILE,
            "wcag22_guidelines_fts",
            rows,
        )

        print(f"Created {DB_FILE.name} with {count} documents")
        return True

    except ValueError as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    create_database()
