---
name: ibm-gds-service-manual
description: Search the UK Government Digital Service (GDS) Service Manual via SQLite FTS5 for guidance on agile delivery, service design, and delivery practices used in bids and proposals.
---

# GDS Service Manual Search

## PREREQUISITES - MANDATORY

Use the cross-platform Python runtime scripts from `$SKILL_DIR/scripts/` for all database access.

Do not use shell HEREDOC SQL patterns in this skill (they are not reliable on Windows).

## Quick Reference

| Item        | Value                                                         |
| ----------- | ------------------------------------------------------------- |
| Database    | `$SKILL_DIR/gds-service-manual.sqlite` |
| FTS5 Table  | `service_manual_fts` (tokenize = 'porter unicode61')             |
| Columns     | `rowid`, `title`, `path`, `content`                           |

## Context Management

Write search results to `./tmp/ibm-gds-service-manual.md` immediately after retrieval. Only copy final deliverables to `./outputs` at completion.

## Search Workflow

Do NOT read markdown files directly. Search the database using the Python runtime scripts.

### Step 1: Expand Query Terms (Default)

**Apply simplified query expansion before searching to improve recall:**

1. **Generate synonym variants** (5-7 alternatives for each core concept):
   - "lead scoring" → add "prospect evaluation", "lead ranking", "contact qualification"
   - "cloud migration" → add "cloud transformation", "cloud adoption", "cloud modernization"
   - "customer portal" → add "self-service portal", "client portal", "customer hub"

2. **Add phrasal alternatives** (rephrase using common variations):
   - "how to implement X" → also search "X implementation", "deploying X", "X rollout"
   - "benefits of X" → also search "X advantages", "X outcomes", "X results"
   - Technical terms → add colloquial equivalents users actually type

3. **Construct OR-joined FTS5 query** (combine variants for better recall):
   ```bash
   # Original query: "lead scoring healthcare"
   # Expanded query: "(lead OR prospect OR contact) AND (scoring OR ranking OR evaluation OR qualification) AND (healthcare OR medical OR clinical OR hospital)"
   ```

**This 3-step expansion takes ~10 seconds and significantly improves search results.**

### Step 2: Execute Search

Use only the Python scripts in `$SKILL_DIR/scripts/`:

- `info.py` (schema/metadata checks)
- `search.py` (FTS search)
- `get.py` (retrieve full record by ID)

```bash
DB_PATH="$SKILL_DIR/gds-service-manual.sqlite"

# Confirm schema/table availability
uv run $SKILL_DIR/scripts/info.py "$DB_PATH"

# Expanded keyword search
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(agile OR iterative OR incremental) AND (delivery OR implementation OR approach)" --json

# Multi-concept expansion
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(service OR product) AND (design OR discovery OR planning) AND (\"user needs\" OR requirements OR outcomes)" --json

# Path/topic-oriented search
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "agile-delivery OR service-standard" --json

# Retrieve full document by rowid/id from search output
uv run $SKILL_DIR/scripts/get.py "$DB_PATH" 42 --json
```

Search options (sqlite-skill) - tighten results first:
- `--offset <n>` pagination
- `--show-status` or `--json-pretty` for query status/warnings
- `--show-scores` or `--min-score <0-1>` for normalized scores
- `--snippet`, `--snippet-length <n>`, `--snippet-column <col>`
- `--query-timeout-ms <ms>`
- `--limit 10`

### Step 3: Evaluate Results & Escalate if Needed

If search results are poor (<5 relevant hits or low quality):
- Use `$query-expansion-strategy` for comprehensive multi-angle expansion.

If results are good (5+ relevant hits):
- Review top 10-15 by relevance order
- Retrieve full content for shortlisted IDs only
- Extract evidence with clear citations

### Step 4: Retrieve Content by ID

Use `get.py` from `$SKILL_DIR/scripts/`:

```bash
DB_PATH="$SKILL_DIR/gds-service-manual.sqlite"

# Get complete story by ID
uv run $SKILL_DIR/scripts/get.py "$DB_PATH" 42

# JSON output for structured processing
uv run $SKILL_DIR/scripts/get.py "$DB_PATH" 42 --json
```

Get options:
- `--preview-length <n>` (>= 1)

Exit codes:
- `2` database path errors
- `3` invalid/empty query or timeout (also invalid preview length)
- `4` no results / not found

## Notes

- Use `search.py` and `get.py` for all retrieval
- Keep full-content retrieval to shortlisted IDs only
- Use path/topic terms to narrow result sets
- Cross-reference with `ibm-bid-writer` and `ibm-bid-requirements-analysis`
- For FTS5 syntax and dataset-specific columns, see [references/sqlite-fts5-query.md](references/sqlite-fts5-query.md)
- For retrieval coverage loops, triage rubric, and post-filter patterns, see [references/search-strategies.md](references/search-strategies.md)
