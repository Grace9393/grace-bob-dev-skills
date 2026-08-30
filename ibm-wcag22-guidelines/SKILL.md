---
name: ibm-wcag22-guidelines
description: Search the Web Content Accessibility Guidelines (WCAG) 2.2 database via SQLite FTS5 for accessibility guidance, success criteria interpretation, conformance expectations, and implementation-aligned evidence for bid and delivery responses.
---

# WCAG22 Guidelines Search

## PREREQUISITES - MANDATORY

Use the cross-platform Python runtime scripts from `$SKILL_DIR/scripts/` for all database access.

Do not use shell HEREDOC SQL patterns in this skill (they are not reliable on Windows).

## Quick Reference

| Item        | Value                                                         |
| ----------- | ------------------------------------------------------------- |
| Database    | `$SKILL_DIR/wcag22-guidelines.sqlite` |
| FTS5 Table  | `wcag22_guidelines_fts` (tokenize = 'porter unicode61')      |
| Columns     | `rowid`, `title`, `path`, `content`                           |

## Context Management

Write search results to `./tmp/ibm-wcag22-guidelines.md` immediately after retrieval. Only copy final deliverables to `./outputs` at completion.

## Search Workflow

Do NOT read markdown files directly. Search the database using the Python runtime scripts.

### Step 1: Expand Query Terms (Default)

**Apply simplified query expansion before searching to improve recall:**

1. **Generate synonym variants** (5-7 alternatives for each core concept):
   - "keyboard access" → add "keyboard operable", "keyboard navigation", "no keyboard trap", "focus order"
   - "contrast" → add "colour contrast", "minimum contrast", "visual contrast ratio", "text contrast"
   - "form errors" → add "error identification", "error prevention", "input assistance", "validation feedback"

2. **Add phrasal alternatives** (rephrase using common variations):
   - "how to meet SC 2.4.7" → also search "Focus Visible implementation", "visible focus indicators", "focus styling guidance"
   - "accessible authentication" → also search "cognitive function test", "login accessibility", "non-memory based authentication"
   - "non-text content" → also search "alternative text", "alt text", "text alternatives for images"

3. **Construct OR-joined FTS5 query** (combine variants for better recall):
   ```bash
   # Original query: "focus visible"
   # Expanded query: "(focus OR keyboard-focus) AND (visible OR indicator OR outline OR highlight)"
   ```

**This 3-step expansion takes ~10 seconds and significantly improves search results.**

### Step 2: Execute Search

Use only the Python scripts in `$SKILL_DIR/scripts/`:

- `info.py` (schema/metadata checks)
- `search.py` (FTS search)
- `get.py` (retrieve full record by ID)

```bash
DB_PATH="$SKILL_DIR/wcag22-guidelines.sqlite"

# Confirm schema/table availability
uv run $SKILL_DIR/scripts/info.py "$DB_PATH"

# Success criteria + implementation terms
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(\"success criterion\" OR SC OR criterion) AND (focus OR keyboard OR contrast)" --json

# Specific WCAG 2.2 criterion focus
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(\"2.4.7\" OR \"focus visible\") AND (indicator OR outline OR styling OR implementation)" --json

# Accessibility outcome-oriented search
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(forms OR authentication OR errors) AND (accessible OR conformance OR guidance)" --json

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
DB_PATH="$SKILL_DIR/wcag22-guidelines.sqlite"

# Get complete WCAG entry by ID
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
- Use success criterion terms (`2.x.x`, criterion names, conformance language) to narrow result sets
- For proposal writing, cross-reference with `ibm-bid-writer` and `ibm-bid-fact-checker`
- For FTS5 syntax and dataset-specific columns, see [references/sqlite-fts5-query.md](references/sqlite-fts5-query.md)
- For retrieval coverage loops, triage rubric, and post-filter patterns, see [references/search-strategies.md](references/search-strategies.md)
