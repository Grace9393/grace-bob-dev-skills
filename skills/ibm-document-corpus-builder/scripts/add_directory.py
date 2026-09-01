# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from corpus_lib import load_yaml, safe_id, write_yaml

ALWAYS_IGNORE_FILENAMES = {".DS_Store"}
ALWAYS_IGNORE_EXTENSIONS = {".sh"}
DEFAULT_EXTENSIONS = {
    ".docx",
    ".pdf",
    ".pptx",
    ".md",
    ".qmd",
    ".markdown",
    ".txt",
    ".html",
    ".htm",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add a directory of documents to the durable bid-library corpus overlay.")
    parser.add_argument("source_dir", type=Path, help="Directory containing source documents")
    parser.add_argument("--corpus", type=Path, default=Path("skills/ibm-bid-library/corpus"))
    parser.add_argument("--persist-manifest", type=Path, default=Path("skills/ibm-bid-library/src/custom-documents.yaml"))
    parser.add_argument("--copy-source-to", type=Path, default=Path("skills/ibm-bid-library/custom-docs"))
    parser.add_argument("--batch-id", help="Stable batch ID; defaults to the source directory name")
    parser.add_argument("--category", required=True, help="Manual category for every document in this batch")
    parser.add_argument("--sub-category-from-folder", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--tag", dest="tags", action="append", default=[], help="Tag to add to every document; repeatable")
    parser.add_argument("--include-extension", action="append", default=[], help="Extra file extension to include, e.g. .xlsx")
    parser.add_argument("--progress-every", type=int, default=10, help="Print progress every N documents")
    parser.add_argument("--manifest-only", action="store_true", help="Copy sources and update the durable manifest without converting documents")
    parser.add_argument("--prune-missing", action=argparse.BooleanOptionalAction, default=True, help="Remove existing entries for this batch that are no longer present")
    parser.add_argument("--dry-run", action="store_true", help="List files that would be added without copying or ingesting")
    parser.add_argument("--overwrite", action="store_true", default=True, help="Overwrite existing corpus document packets")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = args.source_dir.expanduser().resolve()
    if not source_dir.is_dir():
        print(f"Error: source directory not found: {source_dir}")
        return 2

    batch_id = safe_id(args.batch_id or source_dir.name).lower()
    include_extensions = {normalise_ext(ext) for ext in args.include_extension}
    supported_extensions = DEFAULT_EXTENSIONS | include_extensions
    print(f"Scanning: {source_dir}", flush=True)
    files = discover_files(source_dir, supported_extensions)
    if args.dry_run:
        print(f"Batch: {batch_id}")
        print(f"Source: {source_dir}")
        print(f"Documents: {len(files)}")
        for path in files:
            rel = path.relative_to(source_dir)
            print(rel.as_posix())
        return 0
    if not files:
        print("No supported documents found.")
        return 0

    print(f"Batch: {batch_id}", flush=True)
    print(f"Documents discovered: {len(files)}", flush=True)
    durable_root = args.copy_source_to.expanduser().resolve()
    copy_root = durable_root / batch_id
    copy_root.mkdir(parents=True, exist_ok=True)
    manifest_docs = []
    for index, source_path in enumerate(files, start=1):
        rel = source_path.relative_to(source_dir)
        print_progress("Preparing", index, len(files), rel, args.progress_every)
        target = copy_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target)
        manifest_docs.append(document_entry(source_dir, source_path, target, durable_root, batch_id, args))

    print("Writing durable manifest entries...", flush=True)
    merge_persist_manifest(
        args.persist_manifest.resolve(),
        durable_root,
        args.corpus.resolve(),
        manifest_docs,
        batch_id,
        args.prune_missing,
    )
    if args.manifest_only:
        print(f"Updated durable manifest with {len(manifest_docs)} documents.")
        print(f"Persisted manifest: {args.persist_manifest}")
        print("Skipped corpus conversion because --manifest-only was supplied.")
        return 0
    print("Converting documents into corpus packets...", flush=True)
    if not ingest_batch(args, durable_root, manifest_docs):
        return 1
    shutil.copy2(args.persist_manifest.resolve(), args.corpus.resolve() / "manifest.yaml")
    print(f"Added {len(manifest_docs)} documents to durable corpus overlay.")
    print(f"Persisted manifest: {args.persist_manifest}")
    print("Run 'make bid-library-rebuild-all' to refresh SQLite, zvec, and QMD.")
    return 0


def print_progress(phase: str, index: int, total: int, rel: Path, every: int) -> None:
    if index == 1 or index == total or every <= 1 or index % every == 0:
        print(f"{phase} {index}/{total}: {rel.as_posix()}", flush=True)


def normalise_ext(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return value
    return value if value.startswith(".") else f".{value}"


def discover_files(source_dir: Path, supported_extensions: set[str]) -> list[Path]:
    files = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in ALWAYS_IGNORE_FILENAMES:
            continue
        if path.suffix.lower() in ALWAYS_IGNORE_EXTENSIONS:
            continue
        if path.suffix.lower() not in supported_extensions:
            continue
        files.append(path)
    return files


def document_entry(
    source_dir: Path,
    source_path: Path,
    copied_path: Path,
    durable_root: Path,
    batch_id: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    rel = source_path.relative_to(source_dir)
    stem = source_path.stem.removeprefix("IBM - ").strip()
    document_id = stable_document_id(batch_id, rel)
    tags = list(dict.fromkeys([*args.tags, batch_id]))
    entry: dict[str, Any] = {
        "source": copied_path.relative_to(durable_root).as_posix(),
        "document_id": document_id,
        "entry_id": document_id,
        "title": stem,
        "category": args.category,
        "category_source": "manual",
        "tags": tags,
        "converter": converter_for(source_path),
        "fallback": fallback_for(source_path),
    }
    if args.sub_category_from_folder and rel.parent.as_posix() != ".":
        entry["sub_category"] = rel.parent.as_posix()
    return entry


def stable_document_id(batch_id: str, rel: Path, max_length: int = 180) -> str:
    raw = f"{batch_id}-{rel.with_suffix('').as_posix()}"
    document_id = safe_id(raw).lower()
    if len(document_id) <= max_length:
        return document_id

    digest = hashlib.sha256(rel.as_posix().encode("utf-8")).hexdigest()[:12]
    stem_id = safe_id(f"{batch_id}-{rel.stem}").lower()
    suffix = f"-{digest}"
    return f"{stem_id[: max_length - len(suffix)].rstrip('-._')}{suffix}"


def converter_for(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".docx", ".pdf", ".pptx"}:
        return "docling"
    if ext in {".md", ".qmd", ".markdown"}:
        return "passthrough"
    if ext in {".txt", ".html", ".htm"}:
        return "plain_text"
    return "auto"


def fallback_for(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext == ".docx":
        return "docx_basic"
    if ext in {".pdf", ".pptx"}:
        return "markitdown"
    return None


def merge_persist_manifest(
    manifest_path: Path,
    source_root: Path,
    corpus_dir: Path,
    entries: list[dict[str, Any]],
    batch_id: str,
    prune_missing: bool,
) -> None:
    manifest = load_yaml(manifest_path)
    if not manifest:
        manifest = {
            "schema_version": 1,
            "batch_id": "custom-documents",
            "corpus_dir": relative_or_absolute(corpus_dir, manifest_path.parent),
            "source_root": relative_or_absolute(source_root, manifest_path.parent),
            "defaults": {
                "language": "en-GB",
                "confidentiality": "internal",
                "converter": "auto",
            },
            "documents": [],
        }
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("batch_id", "custom-documents")
    manifest["corpus_dir"] = relative_or_absolute(corpus_dir, manifest_path.parent)
    manifest["source_root"] = relative_or_absolute(source_root, manifest_path.parent)
    manifest.setdefault(
        "defaults",
        {
            "language": "en-GB",
            "confidentiality": "internal",
            "converter": "auto",
        },
    )
    docs = manifest.setdefault("documents", [])
    if prune_missing:
        current_sources = {str(entry["source"]) for entry in entries}
        batch_prefix = f"{batch_id}/"
        before = len(docs)
        docs[:] = [
            item
            for item in docs
            if not (
                isinstance(item, dict)
                and str(item.get("source") or "").startswith(batch_prefix)
                and str(item.get("source") or "") not in current_sources
            )
        ]
        pruned = before - len(docs)
        if pruned:
            print(f"Pruned {pruned} stale manifest entries for batch {batch_id}.", flush=True)
    by_id = {str(item.get("document_id")): index for index, item in enumerate(docs) if isinstance(item, dict)}
    by_source = {str(item.get("source")): index for index, item in enumerate(docs) if isinstance(item, dict)}
    for entry in entries:
        document_id = str(entry["document_id"])
        source = str(entry["source"])
        if document_id in by_id:
            docs[by_id[document_id]] = entry
        elif source in by_source:
            docs[by_source[source]] = entry
        else:
            by_id[document_id] = len(docs)
            by_source[source] = len(docs)
            docs.append(entry)
    write_yaml(manifest_path, manifest)


def ingest_batch(args: argparse.Namespace, source_root: Path, entries: list[dict[str, Any]]) -> bool:
    manifest = {
        "schema_version": 1,
        "batch_id": safe_id(args.batch_id or args.source_dir.name).lower(),
        "corpus_dir": str(args.corpus.resolve()),
        "source_root": str(source_root),
        "defaults": {
            "language": "en-GB",
            "confidentiality": "internal",
            "converter": "auto",
        },
        "documents": entries,
    }
    with tempfile.TemporaryDirectory(prefix="ibm-corpus-batch-") as tmp:
        manifest_path = Path(tmp) / "manifest.yaml"
        write_yaml(manifest_path, manifest)
        command = [
            sys.executable,
            str(Path(__file__).with_name("ingest.py")),
            str(manifest_path),
            "--overwrite",
            "--progress-every",
            str(max(args.progress_every, 1)),
        ]
        completed = subprocess.run(command, check=False)
        if completed.returncode == 0:
            return True
        print_latest_ingest_errors(args.corpus.resolve())
        return False


def print_latest_ingest_errors(corpus_dir: Path) -> None:
    runs_dir = corpus_dir / "ingest-runs"
    runs = sorted(runs_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not runs:
        print("Ingest failed, but no ingest-run report was found.", flush=True)
        return
    latest = runs[0]
    try:
        report = json.loads(latest.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Ingest failed. Could not read report {latest}: {exc}", flush=True)
        return
    print(f"Ingest failed. Report: {latest}", flush=True)
    for event in report.get("events", []) or []:
        if event.get("level") != "error":
            continue
        doc = event.get("document", {}) or {}
        label = doc.get("title") or doc.get("document_id") or doc.get("source") or "document"
        print(f"Error: {label}", flush=True)
        print(f"  {event.get('message')}", flush=True)


def relative_or_absolute(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
