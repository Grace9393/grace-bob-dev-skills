---
name: query-expansion-strategy
description: Generates expanded query sets for SQLite FTS (full-text search) indexes. Use when a user needs to fan out a single query into semantically related sub-queries, synonym clusters, or variant phrasings that an FTS tokeniser will match. Covers decomposition into sub-questions, synonym/stemming expansion, entity relationship mapping, and coverage analysis against a target corpus. Trigger on any request involving FTS query expansion, search coverage improvement, or sub-question generation targeting a local full-text index.
---

# Query Expansion Strategy — SQLite FTS

Expands a seed query into a set of variant queries optimised for SQLite FTS matching semantics.

## When to use this skill

**This skill is an escalation tool for complex searches.** Use it when:

- Initial search results are poor (<5 relevant hits or low quality matches)
- User query is ambiguous or multi-faceted requiring comprehensive coverage
- Need to build a reusable query set covering 10 semantic categories
- Analyzing coverage gaps between a query set and target document corpus

**Skills that escalate to this skill:**
- `ibm-bid-customer-stories` - When customer story searches need comprehensive coverage
- `ibm-sf-help` - When Salesforce documentation searches return insufficient results
- `ibm-bid-library` - When bid library searches need exhaustive topic exploration
- `ibm-sf-architect` - When architecture pattern searches require multiple perspectives

**Default search behavior:** Most FTS5 database skills now use simplified 3-step expansion (synonyms → phrasal variants → OR-join) by default. Use this skill for the full 10-category decomposition when simple expansion is insufficient.

## Workflow

1. **Decompose** — Break the seed query into sub-questions. See `references/fts-expansion.md` → *Sub-question Decomposition*.
2. **Expand** — Generate synonym and stemming variants per sub-question. See `references/fts-expansion.md` → *Synonym & Stemming Expansion*.
3. **Map entities** — Identify related entities, concepts, and use-case framings. See `references/fts-expansion.md` → *Entity Relationship Mapping*.
4. **Construct queries** — Render each variant as a raw MATCH expression string. Do not wrap in SQL. See `references/fts-expansion.md` → *FTS Query Construction*.
5. **Analyse coverage** — Score the expanded set against the semantic coverage checklist and output the analysis. See `references/fts-expansion.md` → *Coverage Analysis Output*.

## Key constraints

- SQLite FTS5 tokeniser strips punctuation and lowercases by default. Generated queries must reflect this.
- Boolean operators in FTS5 are `AND`, `OR`, `NOT` (uppercase). Prefix search uses `*` suffix. Phrase search uses double quotes.
- Do not generate queries containing stop-word-only fragments — FTS will return empty result sets.
- If the user specifies a custom tokeniser (e.g. `unicode61` with diacritics removal), adjust variant generation accordingly.
