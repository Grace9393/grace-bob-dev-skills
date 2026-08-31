#!/usr/bin/env python3
"""Get a specific document from IBM Agentic Enterprise documentation database."""

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Optional


def get_doc_by_path(db_path: str, file_path: str) -> Optional[Dict]:
    """Get document by file path from docs_fts."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT rowid AS id, path AS file_path, title, content
        FROM docs_fts
        WHERE path = ?
        """,
        (file_path,),
    )

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_doc_by_id(db_path: str, doc_id: int) -> Optional[Dict]:
    """Get document by rowid from docs_fts."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT rowid AS id, path AS file_path, title, content
        FROM docs_fts
        WHERE rowid = ?
        """,
        (doc_id,),
    )

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def format_doc(doc: Dict) -> str:
    """Format document for display."""
    output = []
    output.append("=" * 80)
    output.append(f"📄 {doc['title']}")
    output.append("=" * 80)
    output.append(f"ID: {doc['id']}")
    output.append(f"Path: {doc['file_path']}")
    output.append(f"Words: {len((doc.get('content') or '').split())}")
    output.append("-" * 80)
    output.append(doc["content"])
    output.append("-" * 80)
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Get document from IBM Agentic Enterprise documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "patterns/multi-agent-orchestration/overview.md"
  %(prog)s 5
        """,
    )

    parser.add_argument("identifier", help="File path or document ID")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "docs.sqlite"

    if not db_path.exists():
        print(f"❌ Error: Database not found: {db_path}")
        print("   Run: make db-create-agentic-architect")
        return 1

    doc = None
    try:
        doc = get_doc_by_id(str(db_path), int(args.identifier))
    except ValueError:
        doc = get_doc_by_path(str(db_path), args.identifier)

    if not doc:
        print(f"❌ Document not found: {args.identifier}")
        return 1

    print(format_doc(doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
