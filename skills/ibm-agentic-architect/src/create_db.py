#!/usr/bin/env python3
"""Create SQLite FTS5 database from IBM Agentic Architect markdown files."""

import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from common.markdown_db_builder import (  # noqa: E402
    create_fts_database,
    process_markdown_files,
)

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
SOURCE_DOCS_DIR = SKILL_DIR / "ibm-docs" / "docs"
DB_FILE = SKILL_DIR / "docs.sqlite"


def create_database() -> bool:
    """Create the SQLite FTS5 database from markdown files."""
    try:
        rows = process_markdown_files(SOURCE_DOCS_DIR)
        count = create_fts_database(DB_FILE, "docs_fts", rows)
        print(f"Created {DB_FILE.name} with {count} documents from {SOURCE_DOCS_DIR}")
        return True
    except ValueError as exc:
        print(f"Error: {exc}")
        return False


if __name__ == "__main__":
    create_database()
