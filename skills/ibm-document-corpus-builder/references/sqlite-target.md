# SQLite Target

The SQLite target preserves the existing `ibm-bid-library/docs.sqlite`
`entries_fts` schema.

```sql
CREATE VIRTUAL TABLE entries_fts USING fts5(
  id UNINDEXED,
  question,
  answer,
  stack,
  category,
  sub_category,
  tags,
  language UNINDEXED,
  library_url UNINDEXED,
  source_path UNINDEXED,
  has_images UNINDEXED,
  images_text,
  images UNINDEXED,
  score UNINDEXED,
  updated_at UNINDEXED,
  tokenize='porter unicode61 remove_diacritics 2'
);
```

`build_sqlite.py` materialises this table from corpus `metadata.yaml` and
`content.md`. Do not add corpus-builder governance tables to this database.

The corpus remains the source of truth.
