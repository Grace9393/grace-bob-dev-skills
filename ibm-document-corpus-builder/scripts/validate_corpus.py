# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.0",
# ]
# ///

from __future__ import annotations

import argparse
from pathlib import Path

from corpus_lib import iter_document_dirs, load_metadata, load_yaml, resolve_category, sha256_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a canonical document corpus.")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    corpus = args.corpus.resolve()
    taxonomy = load_yaml(corpus / "taxonomy.yaml")
    errors: list[str] = []
    warnings: list[str] = []

    if not (corpus / "manifest.yaml").exists():
        warnings.append("manifest.yaml missing")
    if not (corpus / "taxonomy.yaml").exists():
        warnings.append("taxonomy.yaml missing")

    docs = iter_document_dirs(corpus)
    for doc_dir in docs:
        metadata_path = doc_dir / "metadata.yaml"
        content_path = doc_dir / "content.md"
        if not metadata_path.exists():
            errors.append(f"{doc_dir.name}: metadata.yaml missing")
            continue
        metadata = load_metadata(doc_dir)
        if not metadata.get("document_id"):
            errors.append(f"{doc_dir.name}: document_id missing")
        if not content_path.exists():
            errors.append(f"{doc_dir.name}: content.md missing")
        else:
            expected = (metadata.get("content", {}) or {}).get("sha256")
            if expected and sha256_file(content_path) != expected:
                errors.append(f"{doc_dir.name}: content.md sha256 mismatch")
        source = metadata.get("source", {}) or {}
        source_path = doc_dir / str(source.get("path") or "")
        if (
            source.get("path")
            and source_path.exists()
            and source.get("sha256")
            and sha256_file(source_path) != source.get("sha256")
        ):
            errors.append(f"{doc_dir.name}: source sha256 mismatch")
        category = (metadata.get("classification", {}) or {}).get("category")
        if category and taxonomy.get("categories"):
            if not resolve_category(category, taxonomy):
                errors.append(f"{doc_dir.name}: unknown category {category!r}")
        elif not category:
            if (taxonomy.get("rules", {}) or {}).get("allow_uncategorized"):
                warnings.append(f"{doc_dir.name}: category missing")
            else:
                errors.append(f"{doc_dir.name}: category missing")

    if args.as_json:
        import json

        print(json.dumps({"documents": len(docs), "errors": errors, "warnings": warnings}, indent=2))
    else:
        print(f"Documents: {len(docs)}")
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        if not errors:
            print("Validation passed")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
