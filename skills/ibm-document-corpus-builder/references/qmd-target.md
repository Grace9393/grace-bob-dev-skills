# QMD Target

`build_qmd.py` materialises the corpus as a QMD-compatible markdown collection.

Recommended output:

```text
qmd-collections/
  ibm-bid-library/
    4640016.md
```

Each markdown file should include frontmatter with stable IDs and source
metadata:

```markdown
---
document_id: "4640016"
entry_id: "4640016"
source_path: "source.docx"
category: "Architecture"
tags:
  - cloud
---

...
```

Materialised QMD markdown includes cached image descriptions from
`metadata.yaml` as a text section and strips local `images/...` markdown links
because corpus image files are pruned after target creation.

QMD can then own indexing, BM25/FTS, vector embeddings, reranking, and retrieval.
Use `--run-qmd-index` to call:

```bash
qmd collection add <output> --name <collection-name> --mask "**/*.md"
```

The corpus-builder should not duplicate QMD's search stack.

## Rebuild Policy

For the bid-library QMD target, the collection directory is generated from the
canonical corpus. Do not add or edit markdown files in the collection directly.

Use `make bid-library-add-document` to persist new source documents into the
corpus overlay, then `make bid-library-rebuild-all` to refresh SQLite, zvec, and
QMD together. `make qmd-create-bid-library` is available for a QMD-only rebuild
when the corpus is already current.
