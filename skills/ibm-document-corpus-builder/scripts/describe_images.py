# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.0",
#   "Pillow>=10.0.0",
#   "diskcache",
#   "openai>=1.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from corpus_lib import iter_document_dirs, load_metadata, save_metadata, sha256_file

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from common.vlm_processor import (  # noqa: E402
    apply_provider_defaults,
    create_vlm_arg_parser,
    create_vlm_client,
    describe_image,
)


def parse_args() -> argparse.Namespace:
    parser = create_vlm_arg_parser("Describe corpus images and write SHA256-keyed metadata.")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--missing-only", action="store_true", default=False)
    parser.add_argument("--refresh", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = apply_provider_defaults(parse_args())
    corpus = args.corpus.resolve()
    client = create_vlm_client(args.base_url, args.provider)
    prompt = "Describe this document image in 1-2 sentences. Focus on diagrams, tables, labels, and key content."
    updated = 0
    skipped = 0

    for doc_dir in iter_document_dirs(corpus):
        metadata = load_metadata(doc_dir)
        images = metadata.get("images", []) or []
        changed = False
        for image in images:
            rel_path = image.get("path")
            if not rel_path:
                continue
            image_path = doc_dir / rel_path
            if not image_path.exists():
                continue
            if args.missing_only and image.get("description"):
                skipped += 1
                continue
            if image.get("description") and not args.refresh:
                skipped += 1
                continue
            checksum = sha256_file(image_path)
            description = describe_image(client, args.model, image_path, prompt, args.provider == "ollama")
            image["sha256"] = checksum
            image["description"] = description or image.get("description")
            image["description_model"] = args.model
            image["description_cache_key"] = f"{checksum}:{args.model}"
            changed = True
            updated += 1
        if changed:
            save_metadata(doc_dir, metadata)

    print(f"Updated image descriptions: {updated}")
    print(f"Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
