# Converter Routing

Converters are selected in this order:

1. Document-level `converter`
2. First matching `converter_routes` entry
3. `defaults.converter`
4. Extension-based `auto`

Supported converter names:

- `passthrough`: copy `.md` or `.qmd` to `content.md`
- `plain_text`: copy text-like files into markdown
- `docx_basic`: extract text from DOCX XML without external dependencies
- `docling`: run local Docling CLI
- `markitdown`: run local MarkItDown
- `auto`: `.md/.qmd` passthrough, `.txt/.csv/.json/.html` plain text,
  `.docx` docx_basic, otherwise placeholder with warning

Routes may include a `fallback` converter:

```yaml
converter_routes:
  - match:
      extension: .pdf
    converter: docling
    fallback: markitdown
```

If both primary and fallback fail, the ingest script creates a minimal
`content.md` with an error note and records the warning in metadata.

Prefer Docling for layout-heavy PDFs, scanned PDFs, tables, and image-rich
documents. Prefer MarkItDown for simple Office/PDF/HTML conversion where clean
markdown is enough.

The default Docling route uses referenced image export:

```bash
DOCLING_LIBREOFFICE_CMD=/Applications/LibreOffice.app \
PATH=/opt/homebrew/bin:${PATH} \
/Users/telcott/.pyenv/shims/docling "$1" \
  --image-export-mode referenced \
  --output "$(dirname "$1")"
```

The corpus-builder also post-processes Docling markdown: referenced local image
paths are normalised to `images/image_000001.png`, and any inline
`data:image/...;base64,...` links are extracted to files as a fallback.
