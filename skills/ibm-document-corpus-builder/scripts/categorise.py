# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.0",
# ]
# ///

from __future__ import annotations

import argparse
from pathlib import Path

from corpus_lib import iter_document_dirs, load_metadata, load_yaml, resolve_category, save_metadata, text_from_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto-categorise corpus documents or apply manual overrides.")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--missing-only", action="store_true")
    parser.add_argument("--review", action="store_true", help="Print category suggestions without writing")
    parser.add_argument("--reclassify", action="store_true")
    parser.add_argument("--overwrite-manual", action="store_true")
    parser.add_argument("--document", help="Document ID for manual override")
    parser.add_argument("--category", help="Manual category override")
    parser.add_argument("--sub-category", help="Manual sub-category override")
    parser.add_argument("--manual", action="store_true", help="Mark override as manual")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    corpus = args.corpus.resolve()
    taxonomy = load_yaml(corpus / "taxonomy.yaml")
    if args.document and args.category:
        return apply_manual(corpus, taxonomy, args)

    changed = 0
    for doc_dir in iter_document_dirs(corpus):
        metadata = load_metadata(doc_dir)
        classification = metadata.setdefault("classification", {})
        if args.missing_only and classification.get("category"):
            continue
        if classification.get("source") == "manual" and not args.overwrite_manual:
            continue
        if not args.reclassify and classification.get("category") and classification.get("source") == "auto":
            continue
        content_path = doc_dir / (metadata.get("content", {}) or {}).get("path", "content.md")
        content = text_from_markdown(content_path) if content_path.exists() else ""
        suggestion = suggest_category(metadata, content, taxonomy)
        if args.review:
            print(f"{metadata.get('document_id')}: {suggestion}")
            continue
        if suggestion.get("category"):
            classification["category"] = suggestion["category"]
            classification["source"] = "auto"
            classification["auto"] = suggestion
            save_metadata(doc_dir, metadata)
            changed += 1
    print(f"Updated: {changed}")
    return 0


def apply_manual(corpus: Path, taxonomy: dict, args: argparse.Namespace) -> int:
    target = corpus / "documents" / args.document / "metadata.yaml"
    if not target.exists():
        print(f"Document not found: {args.document}")
        return 4
    category = resolve_category(args.category, taxonomy) or args.category
    metadata = load_yaml(target)
    classification = metadata.setdefault("classification", {})
    classification["category"] = category
    if args.sub_category:
        classification["sub_category"] = args.sub_category
    classification["source"] = "manual" if args.manual else "override"
    save_metadata(target.parent, metadata)
    print(f"Updated {args.document}: {category}")
    return 0


def suggest_category(metadata: dict, content: str, taxonomy: dict) -> dict:
    haystack = " ".join(
        [
            str(metadata.get("title") or ""),
            str(metadata.get("document_id") or ""),
            " ".join((metadata.get("classification", {}) or {}).get("tags", []) or []),
            content[:12000],
        ]
    ).lower()
    best_name = None
    best_score = 0
    best_evidence: list[str] = []
    for category in taxonomy.get("categories", []) or []:
        name = str(category.get("name") or category.get("id") or "")
        terms = [name, *(category.get("aliases", []) or []), *(category.get("keywords", []) or [])]
        score = 0
        evidence = []
        for term in terms:
            term_text = str(term).strip()
            if term_text and term_text.lower() in haystack:
                score += 1
                evidence.append(f"Matched term: {term_text}")
        if score > best_score:
            best_name = name
            best_score = score
            best_evidence = evidence
    confidence = min(0.95, best_score / 4) if best_score else 0.0
    return {"category": best_name, "confidence": confidence, "evidence": best_evidence}


if __name__ == "__main__":
    raise SystemExit(main())
