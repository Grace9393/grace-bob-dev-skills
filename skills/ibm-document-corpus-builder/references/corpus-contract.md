# Corpus Contract

The corpus-builder owns the source-of-truth schema. Retrieval stores are
materialised from the corpus.

## Direct Ingest

For a single document, a manifest is optional:

```bash
uv run skills/ibm-document-corpus-builder/scripts/ingest.py \
  --corpus skills/ibm-bid-library/corpus \
  --source /path/to/document.pdf \
  --document-id document-id \
  --category Documentation \
  --tags policy accessibility
```

Direct ingest creates missing `manifest.yaml` and `taxonomy.yaml` placeholders
if needed. If the target corpus already has taxonomy and metadata, those are
preserved.

For `skills/ibm-bid-library/corpus`, direct ingest is persistent unless
`--no-persist` is supplied. The source file is copied to
`skills/ibm-bid-library/custom-docs/`, and
`skills/ibm-bid-library/src/custom-documents.yaml` receives a manifest entry:

```yaml
schema_version: 1
batch_id: custom-documents
corpus_dir: ../corpus
source_root: ../custom-docs
documents:
  - source: document.pdf
    document_id: document-id
    category: Documentation
    category_source: manual
```

`make db-create-bid-library`, `make db-create-bid-library-no-desc`, and the zvec
and QMD bid-library targets rebuild the base corpus from `all_docs.xlsx`, then
replay `custom-documents.yaml` with `--overwrite`.

For batched additions, use:

```bash
make bid-library-add-document SOURCE=/path/to/doc.docx DOCUMENT_ID=doc-id CATEGORY=Architecture
```

For a directory batch, use:

```bash
make bid-library-add-directory \
  SOURCE_DIR=/path/to/documents \
  CATEGORY="G-Cloud 15 Service Offerings" \
  BATCH_ID=gcloud15-service-offerings \
  TAGS="g-cloud-15 service-offering" \
  PROGRESS_EVERY=10
```

Directory ingest always ignores `.DS_Store` and `.sh` files. It copies included
source files to `skills/ibm-bid-library/custom-docs/<batch-id>/`, writes
replayable entries to `custom-documents.yaml`, and updates the current corpus.
It prints progress during scanning, file preparation, manifest writing, and
document conversion. Existing manifest entries for the same batch are pruned
when files are removed from the source directory.

Use `MANIFEST_ONLY=1` to refresh the durable manifest after removing files from
a batch without running conversion immediately.

These commands only update the durable corpus overlay. After adding one or more
documents or batches, run:

```bash
make bid-library-rebuild-all
```

That rebuilds SQLite, zvec, and QMD from the accumulated corpus. zvec is rebuilt
as a full corpus because BM25 sparse vectors require corpus-level statistics for
consistent scoring. It also describes missing images before target
materialisation with Ollama `gemma3:4b`, using the shared image SHA256 cache.
After all retrieval targets are materialised, the workflow prunes rebuildable
packet artifacts:

```text
documents/*/source.*
documents/*/images/
documents/*/_docling/
```

The retained durable inputs are the base `all_docs.xlsx` import inputs plus the
custom-document overlay in `skills/ibm-bid-library/custom-docs/` and
`skills/ibm-bid-library/src/custom-documents.yaml`. Re-running the corpus
creation workflow recreates the pruned packet artifacts when needed. Keep
`converter-output.json` as the lightweight conversion audit record; remove
Docling's `_docling/` working directories after retrieval targets are built.

## Directory Layout

```text
corpus/
  manifest.yaml
  taxonomy.yaml
  ingest-runs/
  documents/
    <document_id>/
      source.<ext>
      content.md
      metadata.yaml
      converter-output.json
      images/
      _docling/
```

## `metadata.yaml`

Required fields:

```yaml
schema_version: 1
document_id: "4640016"
entry_id: "4640016"
title: "Title"
source:
  path: "source.docx"
  original_filename: "4640016.docx"
  uri: null
  sha256: "..."
  mime_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  byte_size: 123456
content:
  path: "content.md"
  sha256: "..."
  converter: docling
  converter_version: null
classification:
  category: Architecture
  sub_category: Cloud
  tags: [cloud, migration]
  language: en-GB
  confidentiality: internal
  source: manual
  auto:
    category: Architecture
    confidence: 0.86
    evidence: []
bid_library:
  question: null
  library_url: null
  score: null
images: []
status: active
```

## Category Precedence

Manual category values win:

1. Per-document manifest `category`
2. Existing `metadata.yaml` with `classification.source: manual`
3. Rule-based taxonomy aliases and keywords
4. Model-assisted category suggestion
5. Default category if allowed

Auto suggestions should be retained under `classification.auto`.

## Image Records

Each image record should include:

```yaml
path: images/image_000001.png
sha256: "..."
mime_type: image/png
width: 1200
height: 800
alt_text: null
caption: null
description: "..."
description_model: gemma3:4b
description_cache_key: "{sha256}:{model}"
```

The description cache key must use image bytes SHA256, not file path.
