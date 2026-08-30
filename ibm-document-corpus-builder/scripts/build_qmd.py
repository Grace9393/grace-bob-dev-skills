# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from corpus_lib import iter_document_dirs, load_metadata, materialised_content, metadata_frontmatter, text_from_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialise corpus documents as a QMD-compatible markdown collection.")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--run-qmd-index", action="store_true", help="Run qmd index after writing collection files")
    parser.add_argument("--qmd-command", default="qmd")
    parser.add_argument("--collection-name", default="ibm-bid-library")
    parser.add_argument("--mask", default="**/*.md")
    parser.add_argument("--qmd-home", type=Path, help="HOME directory to use for the qmd subprocess")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    corpus = args.corpus.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    count = 0
    for doc_dir in iter_document_dirs(corpus):
        metadata = load_metadata(doc_dir)
        if metadata.get("status") == "inactive":
            continue
        content_path = doc_dir / (metadata.get("content", {}) or {}).get("path", "content.md")
        content = text_from_markdown(content_path) if content_path.exists() else ""
        entry_id = str(metadata.get("entry_id") or metadata.get("document_id"))
        target = output / f"{entry_id}.md"
        target.write_text(
            metadata_frontmatter(metadata) + materialised_content(metadata, content, include_header=False),
            encoding="utf-8",
        )
        count += 1

    if args.run_qmd_index:
        if shutil.which(args.qmd_command) is None:
            print(f"QMD command not found: {args.qmd_command}")
            return 2
        env = os.environ.copy()
        if args.qmd_home:
            qmd_home = args.qmd_home.resolve()
            qmd_home.mkdir(parents=True, exist_ok=True)
            env["HOME"] = str(qmd_home)
            env["XDG_CACHE_HOME"] = str(qmd_home / ".cache")
            env["XDG_CONFIG_HOME"] = str(qmd_home / ".config")

        subprocess.run(
            [
                args.qmd_command,
                "collection",
                "add",
                str(output),
                "--name",
                args.collection_name,
                "--mask",
                args.mask,
            ],
            check=True,
            env=env,
        )

    print(f"QMD collection: {output}")
    print(f"Documents written: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
