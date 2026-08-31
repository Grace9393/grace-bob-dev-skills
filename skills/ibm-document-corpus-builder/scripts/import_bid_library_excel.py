# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas>=2.0.0",
#   "openpyxl>=3.0.0",
#   "PyYAML>=6.0.0",
#   "Pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import math
import re
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
from corpus_lib import image_record, safe_id, sha256_file, write_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import the current IBM bid-library Excel export into a corpus.")
    parser.add_argument("xlsx", type=Path, help="Path to all_docs.xlsx")
    parser.add_argument("corpus", type=Path, help="Output corpus directory")
    parser.add_argument("--source-docs-dir", type=Path, help="Directory containing {id}.docx source documents")
    parser.add_argument("--images-dir", type=Path, help="Directory containing {id}_artifacts image folders")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--copy-images", action="store_true", default=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    xlsx = args.xlsx.resolve()
    corpus = args.corpus.resolve()
    source_docs_dir = args.source_docs_dir.resolve() if args.source_docs_dir else None
    images_dir = args.images_dir.resolve() if args.images_dir else None

    if not xlsx.exists():
        print(f"Excel source not found: {xlsx}")
        return 2

    df = pd.read_excel(xlsx)
    df = df.rename(
        columns={
            "Library Entry Id": "id",
            "Question *": "question",
            "Answer *": "answer",
            "Sub-Category": "sub_category",
            'Tags (separated by commas ",")': "tags",
            "Library Entry URL": "library_url",
        }
    )
    if args.limit:
        df = df.head(args.limit)

    corpus.mkdir(parents=True, exist_ok=True)
    docs_dir = corpus / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)

    category_values = [clean_text(value) for value in df.get("Category", [])]
    categories = sorted({value for value in category_values if value})
    has_blank_categories = any(not value for value in category_values)
    taxonomy = {
        "schema_version": 1,
        "categories": [{"id": safe_id(category).lower(), "name": category, "status": "active"} for category in categories],
        "rules": {"require_primary_category": True, "allow_uncategorized": has_blank_categories},
    }
    write_yaml(corpus / "taxonomy.yaml", taxonomy)

    manifest = {
        "schema_version": 1,
        "batch_id": "ibm-bid-library-excel-import",
        "source_root": str(xlsx.parent),
        "defaults": {"language": "en-GB", "confidentiality": "internal", "converter": "excel"},
        "targets": {
            "sqlite": {"enabled": True, "output": "skills/ibm-bid-library/docs.sqlite"},
            "zvec": {"enabled": True, "output": "skills/ibm-bid-library-zvec/references/bid_library_zvec"},
            "qmd": {"enabled": False, "collection": "ibm-bid-library"},
        },
        "documents": [],
    }

    count = 0
    for _, row in df.iterrows():
        entry_id = clean_text(row.get("id"))
        if not entry_id:
            continue
        doc_dir = docs_dir / safe_id(entry_id)
        doc_dir.mkdir(parents=True, exist_ok=True)

        question = raw_text(row.get("question"))
        answer = raw_text(row.get("answer"))
        (doc_dir / "content.md").write_text(answer + "\n", encoding="utf-8")

        source_path = None
        source_sha = None
        source_size = None
        if source_docs_dir:
            candidate = source_docs_dir / f"{entry_id}.docx"
            if candidate.exists():
                source_path = f"docs/{entry_id}.docx"
                source_sha = sha256_file(candidate)
                source_size = candidate.stat().st_size

        images = []
        if images_dir:
            artifact_dir = images_dir / f"{entry_id}_artifacts"
            if artifact_dir.exists():
                target_images_dir = doc_dir / "images"
                target_images_dir.mkdir(parents=True, exist_ok=True)
                for index, image_path in enumerate(sorted(artifact_dir.iterdir()), start=1):
                    if not image_path.is_file() or image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}:
                        continue
                    target = target_images_dir / f"image_{index:06d}{image_path.suffix.lower()}"
                    if args.copy_images:
                        shutil.copy2(image_path, target)
                        record = image_record(target, doc_dir)
                        record["legacy_path"] = f"docs/images/{entry_id}_artifacts/{image_path.name}"
                        images.append(record)

        tags = [tag.strip() for tag in clean_text(row.get("tags")).split(",") if tag.strip()]
        category = clean_text(row.get("Category")) or None
        metadata = {
            "schema_version": 1,
            "document_id": entry_id,
            "entry_id": entry_id,
            "title": question.strip() or f"Bid Library Entry {entry_id}",
            "source": {
                "path": source_path,
                "original_filename": f"{entry_id}.docx" if source_path else None,
                "uri": None,
                "sha256": source_sha,
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if source_path else None,
                "byte_size": source_size,
            },
            "content": {
                "path": "content.md",
                "sha256": sha256_file(doc_dir / "content.md"),
                "converter": "excel",
                "converter_version": None,
                "converter_output_path": None,
            },
            "classification": {
                "category": category,
                "sub_category": clean_text(row.get("sub_category")) or None,
                "tags": tags,
                "language": clean_text(row.get("Language")) or "en-GB",
                "confidentiality": "internal",
                "source": "imported" if category else "auto",
                "auto": None,
            },
            "bid_library": {
                "question": question,
                "answer": answer,
                "library_url": clean_text(row.get("library_url")) or None,
                "score": extract_score(answer),
                "stack": clean_text(row.get("Stack")) or None,
            },
            "images": images,
            "status": "active",
            "warnings": [],
        }
        write_yaml(doc_dir / "metadata.yaml", metadata)
        manifest["documents"].append({"source": source_path or str(xlsx), "document_id": entry_id, "category": category, "tags": tags})
        count += 1

    write_yaml(corpus / "manifest.yaml", manifest)
    print(f"Corpus: {corpus}")
    print(f"Entries imported: {count}")
    print(f"Categories: {len(categories)}")
    return 0


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value)
    if text == "nan":
        return ""
    return text.strip()


def raw_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value)
    if text == "nan":
        return ""
    return text


def extract_score(answer: str) -> float | None:
    match = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*%?", answer or "", re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1))


if __name__ == "__main__":
    raise SystemExit(main())
