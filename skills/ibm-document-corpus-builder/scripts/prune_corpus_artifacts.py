from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from corpus_lib import iter_document_dirs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove rebuildable corpus artifacts after retrieval targets have been materialised."
    )
    parser.add_argument("corpus", type=Path)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be removed without deleting files.",
    )
    args = parser.parse_args()

    corpus = args.corpus.resolve()
    source_count = 0
    image_dir_count = 0
    docling_dir_count = 0
    source_bytes = 0
    image_bytes = 0
    docling_bytes = 0

    for doc_dir in iter_document_dirs(corpus):
        for source_path in doc_dir.glob("source.*"):
            if not source_path.is_file():
                continue
            source_count += 1
            source_bytes += source_path.stat().st_size
            if not args.dry_run:
                source_path.unlink()

        images_dir = doc_dir / "images"
        if images_dir.is_dir():
            image_dir_count += 1
            image_bytes += directory_size(images_dir)
            if not args.dry_run:
                shutil.rmtree(images_dir)

        docling_dir = doc_dir / "_docling"
        if docling_dir.is_dir():
            docling_dir_count += 1
            docling_bytes += directory_size(docling_dir)
            if not args.dry_run:
                shutil.rmtree(docling_dir)

    action = "Would remove" if args.dry_run else "Removed"
    print(
        f"{action} {source_count} source files ({human_size(source_bytes)}) "
        f"{image_dir_count} image directories ({human_size(image_bytes)}), "
        f"and {docling_dir_count} _docling directories ({human_size(docling_bytes)})."
    )
    return 0


def directory_size(path: Path) -> int:
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


if __name__ == "__main__":
    raise SystemExit(main())
