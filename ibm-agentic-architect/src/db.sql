-- IBM Agentic Architect Database Schema
-- Standard FTS5-only pattern (title/path/content)

CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
    title,
    path,
    content,
    tokenize = 'porter unicode61 remove_diacritics 2'
);
