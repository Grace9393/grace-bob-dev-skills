#!/usr/bin/env python3
"""Search IBM Agentic Enterprise documentation using FTS5 full-text search."""

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def split_path(path: str) -> Tuple[str, Optional[str]]:
    """Extract category/subcategory from a relative markdown path."""
    parts = Path(path).parts
    if len(parts) >= 2:
        category = parts[0]
        subcategory = parts[1] if len(parts) > 2 else None
        return category, subcategory
    return "general", None


def search_docs(db_path: str, query: str, category: str = None, limit: int = 10) -> List[Dict]:
    """Search documentation using FTS5."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if category:
        sql = """
            SELECT
                rowid AS id,
                title,
                path,
                content,
                bm25(docs_fts) AS rank
            FROM docs_fts
            WHERE docs_fts MATCH ? AND path LIKE ?
            ORDER BY rank
            LIMIT ?
        """
        cursor.execute(sql, (query, f"{category}/%", limit))
    else:
        sql = """
            SELECT
                rowid AS id,
                title,
                path,
                content,
                bm25(docs_fts) AS rank
            FROM docs_fts
            WHERE docs_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        cursor.execute(sql, (query, limit))

    results = []
    for row in cursor.fetchall():
        content = row["content"] or ""
        category_name, subcategory = split_path(row["path"])
        results.append(
            {
                "id": row["id"],
                "file_path": row["path"],
                "category": category_name,
                "subcategory": subcategory,
                "title": row["title"],
                "snippet": content[:300] + "..." if len(content) > 300 else content,
                "word_count": len(content.split()),
                "rank": row["rank"],
            }
        )

    conn.close()
    return results


def format_results(results: List[Dict], verbose: bool = False) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    output = []
    output.append(f"\n🔍 Found {len(results)} result(s):\n")
    output.append("=" * 80)

    for i, result in enumerate(results, 1):
        output.append(f"\n{i}. {result['title']}")
        output.append(f"   📁 {result['file_path']}")
        output.append(
            f"   🏷️  {result['category']}"
            + (f" → {result['subcategory']}" if result["subcategory"] else "")
        )
        output.append(
            f"   📊 {result['word_count']} words | Relevance: {result['rank']:.2f}"
        )

        if verbose:
            output.append("\n   Preview:")
            output.append(f"   {result['snippet']}")

        output.append("")

    output.append("=" * 80)
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search IBM Agentic Enterprise documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "orchestration patterns"
  %(prog)s "circuit breaker" --category patterns
  %(prog)s "oauth security" --limit 5 --verbose
        """,
    )

    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--category",
        "-c",
        help="Filter by top-level folder (patterns, standards, architecture, etc.)",
    )
    parser.add_argument(
        "--limit", "-l", type=int, default=10, help="Maximum number of results"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show preview")

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "docs.sqlite"

    if not db_path.exists():
        print(f"❌ Error: Database not found: {db_path}")
        print("   Run: make db-create-agentic-architect")
        return 1

    results = search_docs(str(db_path), args.query, args.category, args.limit)
    print(format_results(results, args.verbose))
    return 0


if __name__ == "__main__":
    sys.exit(main())
