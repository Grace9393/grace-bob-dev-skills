# zvec Target

`build_zvec.py` reads the corpus and materialises markdown files for
`zvec_hybrid.ingest.ingest_directory`.

Compatibility rule:

- Name generated source files `{entry_id}.md`.

The existing `ibm-bid-library-zvec/scripts/get.py` retrieves documents by
filtering zvec rows where `path = '{doc_id}.md'`, so preserving this convention
keeps retrieval stable.

Recommended zvec settings:

- dense backend: `zvec-local`
- sparse backend: `bm25`
- chunk size: `1000`
- chunk overlap: `200`

The builder should prepend compact metadata to the markdown if the corpus
content does not already contain category, tags, language, source path, and
library URL.

It should also append cached image descriptions from `metadata.yaml` as text and
strip local `images/...` markdown links. The image files are rebuildable corpus
artifacts and may be pruned after zvec materialisation.

## Rebuild Policy

For the bid-library zvec target, treat the store as a materialised full-corpus
output. Add new documents to the durable corpus overlay with
`make bid-library-add-document`, then run `make bid-library-rebuild-all` when
ready.

This is deliberate for BM25 sparse stores. BM25 document vectors depend on
corpus-level statistics, so rebuilding from the accumulated corpus keeps new
and existing chunks scored consistently.
