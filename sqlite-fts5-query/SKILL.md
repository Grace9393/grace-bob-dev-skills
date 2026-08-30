---
name: sqlite-fts5-query
description: SQLite Full-Text Search (FTS5) query reference for reading FTS5-indexed databases. Use when Claude needs to query SQLite databases with FTS5 virtual tables for text search operations, relevance ranking, snippet generation, or autocomplete functionality.
---

# SQLite FTS5 Query Reference

## Runtime and Safety

Do not call `sqlite3` directly from skills. Use cross-platform Python wrappers instead.

Preferred runtime scripts:

- `uv run $SKILL_DIR/../<sqlite-skill>/scripts/info.py <db_path>`
- `uv run $SKILL_DIR/../<sqlite-skill>/scripts/search.py <db_path> "<fts_query>" --json`
- `uv run $SKILL_DIR/../<sqlite-skill>/scripts/get.py <db_path> <id> --json`

Guidelines:

- Prefer `--json` output for machine-readability and tool-to-tool handoff.
- Keep all queries read-only.
- Do not use shell HEREDOC SQL in skills (Windows incompatibility).
- Use `info.py` before first query to confirm schema/table availability.

Example:

```bash
DB_PATH="$SKILL_DIR/../ibm-bid-library/docs.sqlite"
uv run $SKILL_DIR/../ibm-bid-library/scripts/info.py "$DB_PATH"
uv run $SKILL_DIR/../ibm-bid-library/scripts/search.py "$DB_PATH" \
  "garage AND (methodology OR delivery OR agile)" --json
uv run $SKILL_DIR/../ibm-bid-library/scripts/get.py "$DB_PATH" 4640016 --json
```

## Database Path Parameterization (Multiple Databases)

This skill must work with multiple SQLite database files. Do not hardcode a single DB path.

Use a variable and pass the target DB explicitly:

```bash
DB_PATH="$SKILL_DIR/../ibm-bid-library/docs.sqlite"
uv run $SKILL_DIR/../ibm-bid-library/scripts/search.py "$DB_PATH" \
  "garage AND (methodology OR delivery OR agile)" --json
```

Switching databases should only require changing `DB_PATH` and table/column names:

```bash
DB_PATH="$SKILL_DIR/../ibm-gds-service-manual/gds-service-manual.sqlite"
uv run $SKILL_DIR/../ibm-gds-service-manual/scripts/search.py "$DB_PATH" \
  "agile OR \"user needs\"" --json
```

Quick schema check before querying:

```bash
uv run $SKILL_DIR/../<sqlite-skill>/scripts/info.py "$DB_PATH"
```

## Basic Query Syntax

```sql
-- Simple term
SELECT * FROM docs WHERE docs MATCH 'term';

-- Phrase search
SELECT * FROM docs WHERE docs MATCH '"exact phrase"';

-- Boolean operators
SELECT * FROM docs WHERE docs MATCH 'term1 AND term2';
SELECT * FROM docs WHERE docs MATCH 'term1 OR term2';
SELECT * FROM docs WHERE docs MATCH 'term1 NOT term2';

-- Prefix matching
SELECT * FROM docs WHERE docs MATCH 'prefix*';

-- Prefix with minimum length (2+ chars required)
SELECT * FROM docs WHERE docs MATCH 'sqli*2';

-- Column-specific search
SELECT * FROM docs WHERE docs MATCH 'column_name:term';

-- Multi-column search
SELECT * FROM docs WHERE docs MATCH '{title body}:query';

-- Proximity search (terms within N tokens)
SELECT * FROM docs WHERE docs MATCH 'NEAR(sqlite search, 5)';
SELECT * FROM docs WHERE docs MATCH 'NEAR(term1 term2, 10)';

-- Proximity with range (1-5 tokens separation)
-- FTS5 does not support NEAR/1 5 syntax; use multiple queries if needed.
```

## Ranking Results

BM25 scoring (lower = better match):

```sql
-- Default ranking
SELECT *, rank FROM docs 
WHERE docs MATCH 'query'
ORDER BY rank;

-- Custom weighted ranking
SELECT *, bm25(docs, 10.0, 1.0) as score
FROM docs 
WHERE docs MATCH 'query'
ORDER BY score;

-- Alternative BM25 with matchinfo
SELECT *, bm25(matchinfo(docs)) as rank
FROM docs
WHERE docs MATCH 'query'
ORDER BY rank DESC;

-- Custom ranking by document attributes
SELECT *, rank FROM docs
WHERE docs MATCH 'query'
ORDER BY date DESC;
```

**Note:** Multiple terms without operators default to implicit AND matching.

## Display Functions

```sql
-- Generate snippet with context
-- snippet(table, column_index, start_mark, end_mark, ellipsis, max_tokens)
SELECT snippet(docs, 0, '<mark>', '</mark>', '...', 32)
FROM docs 
WHERE docs MATCH 'query';

-- Highlight matches in full content
SELECT highlight(docs, 0, '<mark>', '</mark>')
FROM docs
WHERE docs MATCH 'query';
```

## Common Patterns

```sql
-- Autocomplete
SELECT title FROM docs 
WHERE docs MATCH 'title:' || ? || '*'
LIMIT 10;

-- Filtered search with soft deletes
SELECT * FROM docs 
WHERE docs MATCH 'query' AND deleted = 0;
```

## Porter Stemming Behaviour

When table uses `tokenize='porter'`:

- Query terms automatically stemmed: 'computing' matches 'compute', 'computer', 'computational'
- Stemming applies to both indexed content and queries
- English only, no runtime language selection
- No per-query control

Examples:
- 'running' → 'run'
- 'computers' → 'comput'
- 'effectiveness' → 'effect'

## Key Constraints

- Use `MATCH` operator (not `LIKE` or `=`)
- Query expressions must be compile-time constants or bound parameters
- Complex WHERE clauses on non-FTS columns trigger full scans
- Maximum term length: 230 bytes
