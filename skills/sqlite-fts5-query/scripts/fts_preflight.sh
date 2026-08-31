#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <db_path> <fts_table> [required_column ...]" >&2
  exit 2
fi

DB_PATH="$1"
FTS_TABLE="$2"
shift 2
REQUIRED_COLUMNS=("$@")

is_ident() {
  case "$1" in
    ''|*[!A-Za-z0-9_]* ) return 1 ;;
    [0-9]* ) return 1 ;;
    * ) return 0 ;;
  esac
}

if [ ! -f "$DB_PATH" ]; then
  echo "Preflight failed: database file not found: $DB_PATH" >&2
  exit 1
fi

if [ ! -r "$DB_PATH" ]; then
  echo "Preflight failed: database file is not readable: $DB_PATH" >&2
  exit 1
fi

if ! is_ident "$FTS_TABLE"; then
  echo "Preflight failed: invalid table name: $FTS_TABLE" >&2
  exit 1
fi

for col in "${REQUIRED_COLUMNS[@]}"; do
  if ! is_ident "$col"; then
    echo "Preflight failed: invalid column name: $col" >&2
    exit 1
  fi
done

if ! sqlite3 -readonly -safe "$DB_PATH" "SELECT 1;" >/dev/null 2>&1; then
  echo "Preflight failed: unable to open DB in read-only safe mode: $DB_PATH" >&2
  exit 1
fi

TABLE_EXISTS="$(sqlite3 -readonly -safe "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE (type='table' OR type='view') AND name='$FTS_TABLE';")"
if [ "$TABLE_EXISTS" != "1" ]; then
  echo "Preflight failed: table not found: $FTS_TABLE" >&2
  echo "Available tables:" >&2
  sqlite3 -readonly -safe "$DB_PATH" ".tables" >&2 || true
  exit 1
fi

# Validate this is an FTS5 virtual table.
IS_FTS5="$(sqlite3 -readonly -safe "$DB_PATH" "SELECT CASE WHEN sql LIKE 'CREATE VIRTUAL TABLE%USING fts5(%' THEN 1 ELSE 0 END FROM sqlite_master WHERE name='$FTS_TABLE' LIMIT 1;")"
if [ "$IS_FTS5" != "1" ]; then
  echo "Preflight failed: table exists but is not an FTS5 virtual table: $FTS_TABLE" >&2
  exit 1
fi

COLUMNS_CSV="$(sqlite3 -readonly -safe "$DB_PATH" "SELECT group_concat(name, ',') FROM pragma_table_info('$FTS_TABLE');")"
if [ -z "$COLUMNS_CSV" ]; then
  echo "Preflight failed: could not read schema for table: $FTS_TABLE" >&2
  exit 1
fi

for col in "${REQUIRED_COLUMNS[@]}"; do
  HAS_COL="$(sqlite3 -readonly -safe "$DB_PATH" "SELECT COUNT(*) FROM pragma_table_info('$FTS_TABLE') WHERE name='$col';")"
  if [ "$HAS_COL" != "1" ]; then
    echo "Preflight failed: missing required column '$col' in table '$FTS_TABLE'" >&2
    echo "Available columns: $COLUMNS_CSV" >&2
    exit 1
  fi
done

echo "Preflight OK"
echo "- DB: $DB_PATH"
echo "- Table: $FTS_TABLE"
echo "- Columns: $COLUMNS_CSV"
