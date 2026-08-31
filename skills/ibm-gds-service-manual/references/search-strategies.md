# Search Strategies

Advanced search patterns for `ibm-gds-service-manual` using Python runtime scripts only.

## Runtime-first approach

```bash
DB_PATH="$SKILL_DIR/gds-service-manual.sqlite"
uv run $SKILL_DIR/scripts/info.py "$DB_PATH"
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" "<fts_query>" --json
uv run $SKILL_DIR/scripts/get.py "$DB_PATH" <id> --json
```

Search options (sqlite-skill):
- `--offset <n>` pagination
- `--show-status` or `--json-pretty` for query status/warnings
- `--show-scores` or `--min-score <0-1>` for normalized scores
- `--snippet`, `--snippet-length <n>`, `--snippet-column <col>`
- `--query-timeout-ms <ms>`

Get options:
- `--preview-length <n>` (>= 1)

Exit codes:
- `2` database path errors
- `3` invalid/empty query or timeout (also invalid preview length)
- `4` no results / not found

Do not use direct `sqlite3` or HEREDOC SQL in this skill.

## Coverage loop (default)

Run these passes in order:

1. **Lifecycle pass** - discovery, alpha, beta, live, retirement.
2. **Practice pass** - agile delivery, service design, accessibility, assurance.
3. **Governance pass** - standards, spend controls, service assessments.

Merge and deduplicate IDs before retrieval.

## Strategy patterns

```bash
# Delivery lifecycle guidance
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(discovery OR alpha OR beta OR live) AND (service standard OR assessment)" --json
```

```bash
# User-needs and design guidance
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(user needs OR journey OR research) AND (design OR prototyping OR testing)" --json
```

```bash
# Path-aware narrowing
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "path:agile-delivery AND (governance OR planning OR roadmap)" --json
```

## Result triage rubric

Review top 10-15 and prioritize:

- **Policy fit (0-3)**: directly answers the procurement or delivery question.
- **Lifecycle fit (0-3)**: aligns to the service phase in scope.
- **Evidence strength (0-2)**: clear standards or mandated practices.
- **Reusability (0-2)**: direct applicability to bid narrative.

Prioritize entries scoring 7+.

## Failure recovery playbook

If fewer than 5 strong hits:

1. Replace broad terms (`delivery`) with GDS-native terms (`discovery`, `service standard`).
2. Add or remove `path:` scoping to widen/narrow.
3. Split policy and implementation queries.
4. Add synonyms (`citizen`, `users`, `people`).
5. Escalate to `$query-expansion-strategy`.

## Anti-patterns

- **Too broad**: `agile government`.
- **Over-scoped path**: strict `path:` term that excludes relevant sections.
- **No lifecycle context**: missing phase terms in the query.
- **One query only**: no multi-pass coverage.

## JSON post-filter examples

```bash
# Keep agile delivery path results only
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(roadmap OR governance) AND agile" --json \
  | jq 'map(select((.path // "") | test("agile-delivery"; "i")))'
```

```bash
# Prioritize standards-related results
uv run $SKILL_DIR/scripts/search.py "$DB_PATH" \
  "(service OR delivery) AND (standard OR assessment)" --json \
  | jq 'map(select((.title // "") | test("standard|assessment"; "i"))) | .[:10]'
```
