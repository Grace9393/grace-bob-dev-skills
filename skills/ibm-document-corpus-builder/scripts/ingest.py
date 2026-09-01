# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

from corpus_lib import (
    collect_images,
    convert_document,
    corpus_dir_from_manifest,
    document_dir,
    load_metadata,
    load_yaml,
    resolve_path,
    route_converter,
    safe_id,
    save_metadata,
    sha256_file,
    source_root_from_manifest,
    utc_stamp,
    write_json,
    write_yaml,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or refresh a canonical markdown corpus.")
    parser.add_argument("manifest", nargs="?", type=Path, help="Path to manifest.yaml")
    parser.add_argument("--corpus", type=Path, help="Corpus directory for direct single-document ingest")
    parser.add_argument("--source", type=Path, help="Source document for direct single-document ingest")
    parser.add_argument("--document-id", help="Document ID for direct ingest")
    parser.add_argument("--entry-id", help="Entry ID for direct ingest")
    parser.add_argument("--title", help="Document title for direct ingest")
    parser.add_argument("--category", help="Manual category for direct ingest")
    parser.add_argument("--sub-category", help="Manual sub-category for direct ingest")
    parser.add_argument("--tags", nargs="*", default=None, help="Tags for direct ingest")
    parser.add_argument("--converter", default="auto", help="Converter for direct ingest")
    parser.add_argument("--fallback", help="Fallback converter for direct ingest")
    parser.add_argument("--language", default="en-GB")
    parser.add_argument("--confidentiality", default="internal")
    parser.add_argument("--library-url")
    parser.add_argument("--question")
    parser.add_argument("--stack")
    parser.add_argument("--persist-manifest", type=Path, help="Append/update this manifest so direct ingest survives corpus rebuilds")
    parser.add_argument(
        "--copy-source-to",
        type=Path,
        help="Copy direct-ingest source to this durable directory and reference the copied file in --persist-manifest",
    )
    parser.add_argument("--no-persist", action="store_true", help="Do not persist direct-ingest documents for future rebuilds")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing document packets")
    parser.add_argument("--progress-every", type=int, default=1, help="Print progress every N documents")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.source:
        return run_direct_ingest(args)
    if not args.manifest:
        print("Error: provide a manifest path or use --source with --corpus for direct ingest.")
        return 2
    manifest_path = args.manifest.resolve()
    manifest = load_yaml(manifest_path)
    corpus_dir = corpus_dir_from_manifest(manifest_path, manifest)
    source_root = source_root_from_manifest(manifest_path, manifest)
    defaults = manifest.get("defaults", {}) or {}

    corpus_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest_path, corpus_dir / "manifest.yaml")

    taxonomy_cfg = manifest.get("taxonomy", {}) or {}
    taxonomy_source = taxonomy_cfg.get("path")
    if taxonomy_source:
        taxonomy_path = resolve_path(taxonomy_source, manifest_path.parent)
        if taxonomy_path.exists():
            shutil.copy2(taxonomy_path, corpus_dir / "taxonomy.yaml")
    elif not (corpus_dir / "taxonomy.yaml").exists():
        write_yaml(corpus_dir / "taxonomy.yaml", {"schema_version": 1, "categories": [], "rules": {}})

    docs = manifest.get("documents", []) or []
    run = {
        "schema_version": 1,
        "ingest_run_id": utc_stamp(),
        "started_at": utc_stamp(),
        "status": "running",
        "document_count": 0,
        "warning_count": 0,
        "error_count": 0,
        "tool_version": "0.1.0",
        "events": [],
    }

    total_docs = len(docs)
    for index, doc_config in enumerate(docs, start=1):
        try:
            print_document_progress("Converting", index, total_docs, doc_config, args.progress_every)
            process_document(doc_config, manifest, defaults, source_root, corpus_dir, args.overwrite, run)
        except Exception as exc:
            run["error_count"] += 1
            run["events"].append({"level": "error", "message": str(exc), "document": doc_config})

    ensure_taxonomy_categories(corpus_dir, docs)
    run["completed_at"] = utc_stamp()
    run["status"] = "completed" if run["error_count"] == 0 else "completed_with_errors"
    write_json(corpus_dir / "ingest-runs" / f"{run['ingest_run_id']}.json", run)
    print(f"Corpus: {corpus_dir}")
    print(f"Documents: {run['document_count']}")
    print(f"Warnings: {run['warning_count']}")
    print(f"Errors: {run['error_count']}")
    return 0 if run["error_count"] == 0 else 1


def run_direct_ingest(args: argparse.Namespace) -> int:
    if not args.corpus:
        print("Error: --corpus is required with --source.")
        return 2
    source_path = args.source.resolve()
    if not source_path.exists():
        print(f"Error: source not found: {source_path}")
        return 2

    corpus_dir = args.corpus.resolve()
    persist_manifest, copy_source_to = persistence_paths(args, corpus_dir)
    corpus_dir.mkdir(parents=True, exist_ok=True)
    if not (corpus_dir / "taxonomy.yaml").exists():
        write_yaml(corpus_dir / "taxonomy.yaml", {"schema_version": 1, "categories": [], "rules": {"allow_uncategorized": True}})
    if not (corpus_dir / "manifest.yaml").exists():
        write_yaml(
            corpus_dir / "manifest.yaml",
            {
                "schema_version": 1,
                "batch_id": "direct-ingest",
                "corpus_dir": str(corpus_dir),
                "source_root": str(source_path.parent),
                "defaults": {
                    "language": args.language,
                    "confidentiality": args.confidentiality,
                    "converter": args.converter,
                },
                "documents": [],
            },
        )

    manifest = {
        "defaults": {
            "language": args.language,
            "confidentiality": args.confidentiality,
            "converter": args.converter,
        },
        "converter_routes": [],
    }
    doc_config: dict[str, Any] = {
        "source": str(source_path),
        "document_id": args.document_id,
        "entry_id": args.entry_id,
        "title": args.title,
        "category": args.category,
        "sub_category": args.sub_category,
        "category_source": "manual" if args.category else "auto",
        "tags": args.tags,
        "converter": args.converter,
        "fallback": args.fallback,
        "language": args.language,
        "confidentiality": args.confidentiality,
        "library_url": args.library_url,
        "question": args.question,
        "stack": args.stack,
    }
    doc_config = {key: value for key, value in doc_config.items() if value is not None}
    run = {
        "schema_version": 1,
        "ingest_run_id": utc_stamp(),
        "started_at": utc_stamp(),
        "status": "running",
        "document_count": 0,
        "warning_count": 0,
        "error_count": 0,
        "tool_version": "0.1.0",
        "mode": "direct",
        "events": [],
    }
    try:
        print_document_progress("Converting", 1, 1, doc_config, args.progress_every)
        process_document(doc_config, manifest, manifest["defaults"], source_path.parent, corpus_dir, args.overwrite, run)
        ensure_taxonomy_categories(corpus_dir, [doc_config])
        if persist_manifest and run["error_count"] == 0:
            persist_direct_document(args, doc_config, source_path, corpus_dir, persist_manifest, copy_source_to)
    except Exception as exc:
        run["error_count"] += 1
        run["events"].append({"level": "error", "message": str(exc), "document": doc_config})
    run["completed_at"] = utc_stamp()
    run["status"] = "completed" if run["error_count"] == 0 else "completed_with_errors"
    write_json(corpus_dir / "ingest-runs" / f"{run['ingest_run_id']}.json", run)
    print(f"Corpus: {corpus_dir}")
    print(f"Documents: {run['document_count']}")
    print(f"Warnings: {run['warning_count']}")
    print(f"Errors: {run['error_count']}")
    return 0 if run["error_count"] == 0 else 1


def persistence_paths(args: argparse.Namespace, corpus_dir: Path) -> tuple[Path | None, Path | None]:
    if args.no_persist:
        return None, None
    if args.persist_manifest:
        return args.persist_manifest.resolve(), args.copy_source_to.resolve() if args.copy_source_to else None
    if corpus_dir.name == "corpus" and corpus_dir.parent.name == "ibm-bid-library":
        library_dir = corpus_dir.parent
        return library_dir / "src" / "custom-documents.yaml", library_dir / "custom-docs"
    return None, None


def persist_direct_document(
    args: argparse.Namespace,
    doc_config: dict[str, Any],
    source_path: Path,
    corpus_dir: Path,
    manifest_path: Path,
    copy_source_to: Path | None,
) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = load_yaml(manifest_path)
    manifest_base = manifest_path.parent
    source_root = copy_source_to.resolve() if copy_source_to else source_path.parent.resolve()
    if not manifest:
        manifest = {
            "schema_version": 1,
            "batch_id": "custom-documents",
            "corpus_dir": relative_or_absolute(corpus_dir, manifest_base),
            "source_root": relative_or_absolute(source_root, manifest_base),
            "defaults": {
                "language": args.language,
                "confidentiality": args.confidentiality,
                "converter": args.converter,
            },
            "documents": [],
        }
    else:
        manifest.setdefault("schema_version", 1)
        manifest.setdefault("batch_id", "custom-documents")
        manifest.setdefault("corpus_dir", relative_or_absolute(corpus_dir, manifest_base))
        manifest.setdefault("source_root", relative_or_absolute(source_root, manifest_base))
        manifest.setdefault(
            "defaults",
            {
                "language": args.language,
                "confidentiality": args.confidentiality,
                "converter": args.converter,
            },
        )

    persisted_source = source_path
    docs = manifest.setdefault("documents", [])
    document_id = str(doc_config.get("document_id") or safe_id(source_path.stem))
    existing_entry = next((item for item in docs if str(item.get("document_id") or "") == document_id), None)
    manifest_source_root = source_root_from_manifest(manifest_path, manifest)
    if copy_source_to:
        target_dir = copy_source_to.resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        target = (
            existing_source_target(existing_entry, manifest_source_root, target_dir, source_path.name)
            if existing_entry
            else target_dir / source_path.name
        )
        if not existing_entry and target.exists() and target.resolve() != source_path:
            target = unique_path(target)
        if target.resolve() != source_path:
            shutil.copy2(source_path, target)
        persisted_source = target

    entry = dict(doc_config)
    entry["source"] = relative_or_absolute(persisted_source, manifest_source_root)
    entry.pop("category_source", None)
    if args.category:
        entry["category_source"] = "manual"

    replaced = False
    for index, existing in enumerate(docs):
        if str(existing.get("document_id") or "") == str(document_id):
            docs[index] = entry
            replaced = True
            break
    if not replaced:
        docs.append(entry)
    write_yaml(manifest_path, manifest)
    print(f"Persisted direct ingest entry: {manifest_path}")


def existing_source_target(
    existing_entry: dict[str, Any] | None,
    source_root: Path,
    target_dir: Path,
    fallback_name: str,
) -> Path:
    if not existing_entry:
        return target_dir / fallback_name
    existing_source = existing_entry.get("source")
    if not existing_source:
        return target_dir / fallback_name
    existing_path = resolve_path(existing_source, source_root)
    if existing_path.parent.resolve() == target_dir.resolve():
        return existing_path
    return target_dir / existing_path.name


def unique_path(path: Path) -> Path:
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    candidate = path
    while candidate.exists():
        candidate = parent / f"{stem}-{counter}{suffix}"
        counter += 1
    return candidate


def relative_or_absolute(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return str(path)


def print_document_progress(phase: str, index: int, total: int, doc_config: dict[str, Any], every: int) -> None:
    if index != 1 and index != total and every > 1 and index % every != 0:
        return
    label = doc_config.get("title") or doc_config.get("document_id") or doc_config.get("source") or "document"
    print(f"{phase} {index}/{total}: {label}", flush=True)


def ensure_taxonomy_categories(corpus_dir: Path, docs: list[dict[str, Any]]) -> None:
    categories = sorted({str(doc.get("category")).strip() for doc in docs if doc.get("category")})
    if not categories:
        return
    taxonomy_path = corpus_dir / "taxonomy.yaml"
    taxonomy = load_yaml(taxonomy_path)
    taxonomy.setdefault("schema_version", 1)
    existing = {str(category.get("name") or "").strip().lower() for category in taxonomy.get("categories", []) or []}
    taxonomy_categories = taxonomy.setdefault("categories", [])
    changed = False
    for category in categories:
        if category.lower() in existing:
            continue
        taxonomy_categories.append({"id": safe_id(category).lower(), "name": category, "status": "active"})
        existing.add(category.lower())
        changed = True
    taxonomy.setdefault("rules", {"require_primary_category": True, "allow_uncategorized": True})
    if changed:
        write_yaml(taxonomy_path, taxonomy)


def process_document(
    doc_config: dict[str, Any],
    manifest: dict[str, Any],
    defaults: dict[str, Any],
    source_root: Path,
    corpus_dir: Path,
    overwrite: bool,
    run: dict[str, Any],
) -> None:
    source_value = doc_config.get("source")
    if not source_value:
        raise ValueError("Document entry missing source")

    source_path = resolve_path(source_value, source_root)
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")

    document_id = safe_id(str(doc_config.get("document_id") or source_path.stem))
    entry_id = str(doc_config.get("entry_id") or document_id)
    doc_dir = document_dir(corpus_dir, document_id)
    if doc_dir.exists() and overwrite:
        shutil.rmtree(doc_dir)
    doc_dir.mkdir(parents=True, exist_ok=True)

    source_target = doc_dir / f"source{source_path.suffix.lower()}"
    if not source_target.exists() or overwrite:
        shutil.copy2(source_path, source_target)

    existing = load_metadata(doc_dir)
    converter, fallback = route_converter(source_path, doc_config, manifest)
    result = convert_document(source_target, converter, doc_dir, doc_config.get("converter_options") or {})
    if result.warnings and fallback:
        fallback_result = convert_document(source_target, str(fallback), doc_dir, doc_config.get("fallback_options") or {})
        if not fallback_result.warnings:
            result = fallback_result

    content_path = doc_dir / "content.md"
    content_path.write_text(result.content, encoding="utf-8")

    classification_source = "manual" if doc_config.get("category") else (existing.get("classification", {}) or {}).get("source", "auto")
    category = doc_config.get("category") or (existing.get("classification", {}) or {}).get("category")
    sub_category = doc_config.get("sub_category") or (existing.get("classification", {}) or {}).get("sub_category")
    tags = doc_config.get("tags") or (existing.get("classification", {}) or {}).get("tags") or []

    metadata = {
        "schema_version": 1,
        "document_id": document_id,
        "entry_id": entry_id,
        "title": doc_config.get("title") or existing.get("title") or source_path.stem,
        "source": {
            "path": source_target.name,
            "original_filename": source_path.name,
            "uri": doc_config.get("uri"),
            "sha256": sha256_file(source_target),
            "mime_type": doc_config.get("mime_type"),
            "byte_size": source_target.stat().st_size,
        },
        "content": {
            "path": "content.md",
            "sha256": sha256_file(content_path),
            "converter": result.converter,
            "converter_version": None,
            "converter_output_path": "converter-output.json" if (doc_dir / "converter-output.json").exists() else None,
        },
        "classification": {
            "category": category,
            "sub_category": sub_category,
            "tags": tags,
            "language": doc_config.get("language") or defaults.get("language"),
            "confidentiality": doc_config.get("confidentiality") or defaults.get("confidentiality"),
            "source": doc_config.get("category_source") or classification_source,
            "auto": (existing.get("classification", {}) or {}).get("auto"),
        },
        "bid_library": {
            "question": doc_config.get("question") or existing.get("bid_library", {}).get("question"),
            "library_url": doc_config.get("library_url") or existing.get("bid_library", {}).get("library_url"),
            "score": doc_config.get("score") or existing.get("bid_library", {}).get("score"),
            "stack": doc_config.get("stack") or existing.get("bid_library", {}).get("stack"),
        },
        "images": collect_images(doc_dir),
        "status": doc_config.get("status", "active"),
        "warnings": result.warnings,
    }
    save_metadata(doc_dir, metadata)
    run["document_count"] += 1
    run["warning_count"] += len(result.warnings)


if __name__ == "__main__":
    raise SystemExit(main())
