#!/usr/bin/env python3
"""Display information about the IBM Agentic Enterprise documentation database."""

import sqlite3
import sys
from pathlib import Path


def display_info(db_path: str) -> None:
    """Display database information."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("IBM Agentic Enterprise Documentation Database - Information")
    print("=" * 80)
    print(f"\n📁 Database: {db_path}")

    db_size = Path(db_path).stat().st_size
    db_size_mb = db_size / (1024 * 1024)
    print(f"💾 Size: {db_size_mb:.2f} MB ({db_size:,} bytes)")

    cursor.execute("SELECT COUNT(*) FROM docs_fts")
    total_docs = cursor.fetchone()[0]
    print(f"\n📊 Total documents: {total_docs}")

    rows = cursor.execute("SELECT path, content FROM docs_fts").fetchall()
    total_words = 0
    category_counts: dict[str, int] = {}
    category_words: dict[str, int] = {}

    for row in rows:
        words = len((row["content"] or "").split())
        total_words += words
        parts = Path(row["path"]).parts
        category = parts[0] if len(parts) >= 2 else "general"
        category_counts[category] = category_counts.get(category, 0) + 1
        category_words[category] = category_words.get(category, 0) + words

    print(f"📝 Total words: {total_words:,}")

    print("\n📚 Documents by category:")
    for category, count in sorted(category_counts.items(), key=lambda item: item[1], reverse=True):
        print(f"  {category:20s}: {count:3d} docs ({category_words[category]:7,d} words)")

    print("\n📏 Longest documents:")
    longest = sorted(
        (
            (row["path"], row["content"], len((row["content"] or "").split()))
            for row in rows
        ),
        key=lambda item: item[2],
        reverse=True,
    )[:5]

    for i, (path, content, words) in enumerate(longest, 1):
        first_line = (content or "").splitlines()[0] if (content or "").splitlines() else path
        print(f"  {i}. {first_line[:50]:50s} ({words:,} words)")
        print(f"     {path}")

    print(f"\n🔍 FTS5 index: {total_docs} documents indexed")
    conn.close()

    print("\n" + "=" * 80)
    print("\n💡 Quick commands:")
    print("  Search: python3 scripts/search.py 'orchestration'")
    print("  Get doc: python3 scripts/get.py 'patterns/multi-agent-orchestration/overview.md'")
    print("=" * 80)


def main() -> int:
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "docs.sqlite"

    if not db_path.exists():
        print(f"❌ Error: Database not found: {db_path}")
        print("   Run: make db-create-agentic-architect")
        return 1

    display_info(str(db_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
