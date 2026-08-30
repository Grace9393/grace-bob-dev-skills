-- WCAG22 Guidelines Database Schema
-- FTS5 table with porter stemming for full-text search

CREATE VIRTUAL TABLE IF NOT EXISTS wcag22_guidelines_fts USING fts5(
    title,
    path,
    content,
    tokenize = 'porter unicode61 remove_diacritics 2'
);
