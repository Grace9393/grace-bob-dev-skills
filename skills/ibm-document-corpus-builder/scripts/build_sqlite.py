# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from corpus_lib import iter_document_dirs, load_metadata, parse_question_answer, text_from_markdown

SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts
USING fts5(
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
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialise corpus documents into legacy ibm-bid-library SQLite FTS.")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overwrite", action="store_true", default=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    corpus = args.corpus.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(output)
    conn.executescript(SCHEMA)
    conn.execute("DELETE FROM entries_fts")

    insert_sql = """
    INSERT INTO entries_fts (
      rowid, id, question, answer, stack, category, sub_category, tags,
      language, library_url, source_path, has_images, images_text, images,
      score, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'));
    """
    inserted = 0
    for doc_dir in iter_document_dirs(corpus):
        metadata = load_metadata(doc_dir)
        if metadata.get("status") == "inactive":
            continue
        content_path = doc_dir / (metadata.get("content", {}) or {}).get("path", "content.md")
        content = text_from_markdown(content_path) if content_path.exists() else ""
        question, answer = parse_question_answer(metadata, content)
        bid = metadata.get("bid_library", {}) or {}
        if "question" in bid and bid.get("question") is not None:
            question = str(bid.get("question"))
        if "answer" in bid and bid.get("answer") is not None:
            answer = str(bid.get("answer"))
        classification = metadata.get("classification", {}) or {}
        images = metadata.get("images", []) or []
        images_text = "\n".join(str(img.get("description")) for img in images if img.get("description")) or None
        images_payload = [sqlite_image_payload(image) for image in images]
        entry_id = str(metadata.get("entry_id") or metadata.get("document_id"))
        rowid = numeric_rowid(entry_id, inserted + 1)
        conn.execute(
            insert_sql,
            (
                rowid,
                entry_id,
                question,
                answer,
                bid.get("stack"),
                classification.get("category"),
                classification.get("sub_category"),
                ", ".join(classification.get("tags", []) or []),
                classification.get("language"),
                bid.get("library_url"),
                (metadata.get("source", {}) or {}).get("path"),
                bool(images),
                images_text,
                json.dumps(images_payload) if images_payload else None,
                bid.get("score"),
            ),
        )
        inserted += 1
    conn.commit()
    conn.close()
    print(f"SQLite database: {output}")
    print(f"Entries inserted: {inserted}")
    return 0


def numeric_rowid(entry_id: str, fallback: int) -> int:
    try:
        return int(entry_id)
    except (TypeError, ValueError):
        return fallback


def sqlite_image_payload(image: dict) -> dict:
    return {
        "path": image.get("legacy_path") or image.get("path"),
        "alt": image.get("alt_text"),
        "description": image.get("description"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
