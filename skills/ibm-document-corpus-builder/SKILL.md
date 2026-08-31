---
name: ibm-document-corpus-builder
description: Build a canonical markdown corpus from mixed document sets and materialise retrieval stores. Use when users need to ingest DOCX, PDF, PPTX, XLSX, HTML, markdown, text, or image-rich document packs; route documents through configurable converters such as Docling, MarkItDown, passthrough, or plain text; extract images and cache image descriptions by SHA256; auto-categorise documents with manual overrides; validate corpus metadata; or build SQLite FTS, zvec, or QMD indexes from the same corpus.
---

# IBM Document Corpus Builder

## Purpose

Use this skill to convert mixed source documents into a canonical corpus:

```text
corpus/
  manifest.yaml
  taxonomy.yaml
  ingest-runs/
  documents/<document_id>/
    source.<ext>
    content.md
    metadata.yaml
    converter-output.json
    images/
```

Then build retrieval targets from the same corpus:

- SQLite FTS (`ibm-bid-library/docs.sqlite`)
- zvec hybrid stores (`ibm-bid-library-zvec/references/bid_library_zvec`)
- QMD markdown collections

The corpus is the source of truth. Retrieval stores are materialised outputs.

## Quick Commands

Create or refresh a corpus:

```bash
uv run $SKILL_DIR/scripts/ingest.py path/to/manifest.yaml
```

Add one document directly:

```bash
uv run $SKILL_DIR/scripts/ingest.py \
  --corpus skills/ibm-bid-library/corpus \
  --source path/to/document.docx \
  --document-id document-id \
  --category Architecture \
  --tags cloud migration
```

When `--corpus` is `skills/ibm-bid-library/corpus`, direct ingest is durable
by default: the source is copied to `skills/ibm-bid-library/custom-docs/` and a
replayable entry is written to `skills/ibm-bid-library/src/custom-documents.yaml`.
Future bid-library rebuild targets recreate the corpus from `all_docs.xlsx` and
then re-apply those custom documents. Use `--no-persist` only for temporary
experiments.

Add one durable bid-library document without rebuilding retrieval targets:

```bash
make bid-library-add-document \
  SOURCE=/path/to/document.docx \
  DOCUMENT_ID=document-id \
  CATEGORY=Architecture
```

This command is intended for batching: add documents one at a time during the
week, then rebuild all targets when ready:

Add a durable directory batch without rebuilding retrieval targets:

```bash
make bid-library-add-directory \
  SOURCE_DIR=/path/to/documents \
  CATEGORY="G-Cloud 15 Service Offerings" \
  BATCH_ID=gcloud15-service-offerings \
  TAGS="g-cloud-15 service-offering" \
  PROGRESS_EVERY=10
```

Directory ingest always ignores `.DS_Store` and `.sh` files. By default it
includes DOCX, PDF, PPTX, markdown, text, and HTML files. Folder names are kept
as sub-categories. Existing entries for the same batch are pruned when files
are removed from the source directory. Progress is printed while files are
prepared and while documents are converted.

Refresh only the durable manifest after removing files from a batch:

```bash
make bid-library-add-directory \
  SOURCE_DIR=/path/to/documents \
  CATEGORY="G-Cloud 15 Service Offerings" \
  BATCH_ID=gcloud15-service-offerings \
  TAGS="g-cloud-15 service-offering" \
  MANIFEST_ONLY=1
```

```bash
make bid-library-rebuild-all
```

`bid-library-rebuild-all` recreates the corpus from `all_docs.xlsx`, replays
durable custom documents, and rebuilds SQLite, zvec, and QMD from the same
corpus. It also runs image description generation with `--missing-only` before
materialising retrieval targets, so SHA256-cached descriptions are reused and
only new images are described. The default image provider/model is Ollama
`gemma3:4b`. After retrieval targets are built, it prunes rebuildable corpus
artifacts (`documents/*/source.*`, `documents/*/images/`, and
`documents/*/_docling/`) so the durable overlay in
`skills/ibm-bid-library/custom-docs/` remains the retained source copy for
custom documents. This keeps zvec BM25 statistics consistent across the full
corpus while avoiding duplicated source, image, and converter-artifact storage.

Validate:

```bash
uv run $SKILL_DIR/scripts/validate_corpus.py path/to/corpus
```

Categorise:

```bash
uv run $SKILL_DIR/scripts/categorise.py path/to/corpus --missing-only
uv run $SKILL_DIR/scripts/categorise.py path/to/corpus --document 4640016 --category Delivery --manual
```

Describe images using the shared SHA256 cache:

```bash
uv run $SKILL_DIR/scripts/describe_images.py path/to/corpus --missing-only --provider ollama --model gemma3:4b
```

Build targets:

```bash
uv run $SKILL_DIR/scripts/build_sqlite.py path/to/corpus path/to/docs.sqlite
uv run $SKILL_DIR/scripts/build_zvec.py path/to/corpus path/to/bid_library_zvec
uv run $SKILL_DIR/scripts/build_qmd.py path/to/corpus path/to/qmd-collections/ibm-bid-library
```

SQLite stores image descriptions in `images_text` and `images`. zvec and QMD
materialise cached image descriptions into the markdown body under `## Image
Descriptions` and strip local `images/...` links, because extracted image files
and Docling converter artifacts are pruned after target creation.

Prune rebuildable artifacts after targets are materialised:

```bash
uv run $SKILL_DIR/scripts/prune_corpus_artifacts.py path/to/corpus
```

## Workflow

1. Start from `assets/manifest-template.yaml`.
2. Configure source documents, converter routes, taxonomy, and targets.
3. Run `ingest.py`.
4. Run `categorise.py` if categories are missing or need refresh.
5. Run `describe_images.py` if image descriptions are needed.
6. Run `validate_corpus.py`.
7. Build one or more retrieval targets.

## Converter Routing

Use manifest routes to select converters by extension, glob, or explicit
document override. Manual document-level converter settings win over routes.

Supported converter names:

- `passthrough`: copy existing markdown/qmd as `content.md`
- `plain_text`: read text-like files as markdown code/text
- `docx_basic`: dependency-free DOCX text extraction fallback
- `docling`: call the local Docling CLI when installed
- `markitdown`: call MarkItDown when installed
- `auto`: choose a conservative default from extension

For detailed schema and routing rules, read:

- `references/corpus-contract.md`
- `references/converter-routing.md`
- `references/sqlite-target.md`
- `references/zvec-target.md`
- `references/qmd-target.md`

## Category Rules

Manual category overrides always win. Auto-categorisation writes its suggestion
under `classification.auto` so users can inspect or override it without losing
the evidence.

Final categories must resolve to an active category or alias in `taxonomy.yaml`
unless the manifest explicitly allows missing categories.

## Image Descriptions

Image descriptions must use `common/vlm_processor.py`. That module caches by
`{image_sha256}:{model}`, so repeated diagrams are described once even if paths
change.

## Target Compatibility

When building `ibm-bid-library/docs.sqlite`, preserve the existing
`entries_fts` schema. Do not add corpus-builder tables to that database.

When building zvec, preserve `{entry_id}.md` source filenames so existing
`ibm-bid-library-zvec/scripts/get.py` behaviour remains compatible.
