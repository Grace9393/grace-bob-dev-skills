# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.0",
#   "zvec-hybrid==0.1.8",
#   "zvec>=0.3.1",
#   "bm25s",
#   "sentence-transformers>=5.3.0",
# ]
# [tool.uv.sources]
# zvec-hybrid = { path = "../../ibm-bid-library-zvec/assets/wheels/zvec_hybrid-0.1.8-py3-none-any.whl" }
# ///

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

from corpus_lib import iter_document_dirs, load_metadata, rendered_content, text_from_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialise corpus documents into a zvec hybrid store.")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("store", type=Path)
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--no-optimize", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        from zvec_hybrid.ingest import IngestionConfig, ingest_directory
    except ImportError:
        print("zvec_hybrid is not available. Run with uv so inline dependencies are provisioned.")
        return 2

    tmp_dir = Path(tempfile.mkdtemp(prefix="corpus_zvec_"))
    try:
        count = 0
        for doc_dir in iter_document_dirs(args.corpus.resolve()):
            metadata = load_metadata(doc_dir)
            if metadata.get("status") == "inactive":
                continue
            content_path = doc_dir / (metadata.get("content", {}) or {}).get("path", "content.md")
            content = text_from_markdown(content_path) if content_path.exists() else ""
            entry_id = str(metadata.get("entry_id") or metadata.get("document_id"))
            (tmp_dir / f"{entry_id}.md").write_text(rendered_content(metadata, content), encoding="utf-8")
            count += 1

        config = IngestionConfig(
            source_dir=tmp_dir,
            store_path=args.store.resolve(),
            pattern="**/*",
            overwrite=True,
            dense_embedding_backend="zvec-local",
            sparse_embedding_backend="bm25",
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            optimize=not args.no_optimize,
            progress_every=args.progress_every,
        )
        summary = ingest_directory(config)
        print(f"Documents materialised: {count}")
        print(f"Store: {args.store.resolve()}")
        print(summary)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
