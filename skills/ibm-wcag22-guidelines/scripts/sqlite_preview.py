#!/usr/bin/env python3
"""Preview SQLite schema and sample rows for a table."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect SQLite tables, schema, and sample rows."
    )
    parser.add_argument(
        "db_path",
        nargs="?",
        help="Path to a SQLite database file (defaults to databases/docs.sqlite)",
    )
    parser.add_argument(
        "--table",
        help="Optional table to preview rows from",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Max number of rows to preview (default: 5)",
    )
    return parser.parse_args()


def quote_ident(name: str) -> str:
    """Safely quote a SQLite identifier."""
    return '"' + name.replace('"', '""') + '"'


def default_db_path() -> Path:
    """Return the repo test database used by this example skill."""
    return Path(__file__).resolve().parents[3] / "databases" / "docs.sqlite"


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path) if args.db_path else default_db_path()

    if not db_path.exists():
        print(f"error: database not found: {db_path}")
        return 1

    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
        tables = [row[0] for row in cur.fetchall()]

        if not tables:
            print("No user tables found.")
            return 0

        print("Tables:")
        for table in tables:
            print(f"- {table}")

        print("\nSchema:")
        for table in tables:
            print(f"\n[{table}]")
            cur.execute(f"PRAGMA table_info({quote_ident(table)})")
            cols = cur.fetchall()
            for col in cols:
                nullability = "NOT NULL" if col[3] else "NULL"
                pk = " PK" if col[5] else ""
                print(f"  - {col[1]}: {col[2]} {nullability}{pk}")

        if args.table:
            if args.table not in tables:
                print(f"\nerror: table not found: {args.table}")
                return 1

            limit = max(1, args.limit)
            print(f"\nSample rows from {args.table} (limit={limit}):")
            cur.execute(
                f"SELECT * FROM {quote_ident(args.table)} LIMIT ?",
                (limit,),
            )
            rows = cur.fetchall()

            if not rows:
                print("  (no rows)")
                return 0

            for idx, row in enumerate(rows, 1):
                printable = {key: row[key] for key in row.keys()}
                print(f"  {idx}. {printable}")

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
