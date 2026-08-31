---
name: pdf-file-reader
description: Read, inspect, and extract content from local or user-uploaded PDF files — text, tables, scanned pages (OCR incl. Traditional Chinese), charts, and form fields. Use this skill whenever a PDF is attached, uploaded, or referenced by local path and its content is not already in context — e.g. "read this PDF", "summarize the attached report", "pull the numbers from this statement", "分析這份 PDF" — and as the ingestion step before any analysis of a PDF-based financial report, board pack, invoice, or contract. Reading and extraction only; for creating, filling, merging, or editing PDFs use a dedicated pdf-manipulation skill.
---

# PDF File Reader

Get the content out of a local or uploaded PDF reliably, choosing the cheapest method that answers the question. Never guess at a PDF's contents — inspect first, then extract.

## Step 1 — Triage (always, before extracting)

```bash
pdfinfo file.pdf            # page count, size, metadata
pdffonts file.pdf           # empty font table = scanned/raster → go to OCR path
pdftotext -f 1 -l 1 file.pdf - | head -20   # sample: clean text or garbled?
```

Decide the path:
- **Fonts present, sample clean** → text-layer extraction (Step 2)
- **No fonts** → scanned document → OCR path (Step 4)
- **Fonts present but sample garbled** (mojibake, wrong characters — check non-embedded fonts or Custom/Identity-H encoding in pdffonts) → treat as scanned: rasterize and read visually or OCR
- Large document (>30 pages) → extract the table of contents / first pages first, then read only sections relevant to the question

## Step 2 — Text extraction

```bash
pdftotext -layout file.pdf out.txt     # layout mode: best for multi-column and statements
pdftotext -f 5 -l 12 file.pdf out.txt  # page ranges: never extract 200 pages for one section
```

Python alternative when positioning matters:

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Step 3 — Tables

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    for t in pdf.pages[7].extract_tables():
        for row in t: print(row)
```

If a table comes back merged or misaligned, rasterize that page (Step 5) and read it visually rather than trusting broken extraction.

**Finance-table rules:** parenthetical values `(1,234)` are negatives — convert them; strip thousands separators before math; multi-level column headers usually span two extracted rows — reconstruct before labeling; footnote markers (¹, \*, (a)) attach to values — capture the footnote text too; after extraction, cross-check that line items sum to their printed totals — a failed check means extraction error, not a source error.

## Step 4 — Scanned documents (OCR)

```bash
pip install pytesseract pdf2image --quiet
apt list --installed 2>/dev/null | grep tesseract || sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-tra tesseract-ocr-chi-sim
```

```python
from pdf2image import convert_from_path
import pytesseract
pages = convert_from_path("file.pdf", dpi=200, first_page=1, last_page=5)
for img in pages:
    print(pytesseract.image_to_string(img, lang="eng+chi_tra"))
```

Use `lang="chi_tra"` for Traditional Chinese documents, `eng+chi_tra` for mixed. OCR numbers are error-prone (1/l, 0/O, 8/B) — verify any figure that feeds a calculation against the rasterized page image before using it.

## Step 5 — Visual pages (charts, layouts, verification)

Text extraction is blind to charts, diagrams, and visual layout. Rasterize the specific page and read the image:

```bash
pdftoppm -jpeg -r 150 -f 3 -l 3 file.pdf /tmp/page && ls /tmp/page-*.jpg
```

Cost guide: text ≈ 200–400 tokens/page; image ≈ 1,600 tokens/page. Rasterize only pages that matter — for a chart question that's the chart page, not the document.

## Extras when relevant

- **Embedded attachments** (spreadsheets inside PDF portfolios): `pdfdetach -list file.pdf`, then `pdfdetach -saveall -o /tmp/att/ file.pdf`
- **Form field values**: `from pypdf import PdfReader; PdfReader("f.pdf").get_fields()`
- **Embedded raster images**: `pdfimages -png file.pdf /tmp/img` (vector charts won't appear — rasterize the page instead)

## Output norms

State which extraction path was used and any pages where extraction was unreliable. Quote figures exactly as printed (then converted values separately if normalized). If a requested section doesn't exist in the file, say so — never fill gaps from general knowledge.

## Hand-offs

- Extracted financials → `financial-variance-analysis` or `earnings-peer-comparison`
- Full structured export to Excel/Markdown → `pdf-to-data`
- PDF creation, filling, merging, signing → `pdf` / `pdf-fill-and-sign`
- Web-hosted report (URL, not a file) → `annual-report-analyzer`
