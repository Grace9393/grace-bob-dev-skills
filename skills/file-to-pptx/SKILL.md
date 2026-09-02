---
name: file-to-pptx
description: "Convert uploaded files into a single editable, brand-templated PowerPoint deck (.pptx). Always use this skill whenever the user uploads or references any of these formats and wants slides, a deck, a presentation, a pitch, a report-as-slides, or asks to 'turn into PowerPoint', 'make a deck', 'convert to slides', or anything similar — even if they don't say the word 'skill' or 'convert'. Supported inputs: pptx, xlsx, xlsm, csv, tsv, pdf, html, htm, md, markdown, txt, png, jpg, jpeg, webp, gif, bmp, bpmn. Use this skill when the user wants editable charts and tables (not screenshots), a corporate brand applied (IBM Carbon by default), or multiple input files merged into one deck. Also use this skill when the user mentions BPMN diagrams, business process flows, AP/finance findings, or wants to combine spreadsheets and documents into one presentation."
license: MIT
allowed-tools:
  - Read
  - Write
  - Bash
  - list_skill_files
  - read_skill_file
  - write_temp_file
  - run_skill_script

---

# File → Editable PPTX (IBM-branded)

Convert any supported file (or set of files) into one editable, downloadable
`.pptx` deck. Charts and tables are **native PowerPoint objects** — the user can
double-click any chart to open the data grid in Excel, edit any table cell,
and reposition any BPMN shape.

## Quick Reference

| User has… | Run |
|---|---|
| One or more uploaded files | `python {SKILL}/scripts/universal_to_pptx.py <inputs...> -o /mnt/user-data/outputs/<name>.pptx` |
| A different brand to apply | Add `--template <their .pptx> --brand <their .json>` |
| No template handy | Omit both flags; the script falls back to the built-in IBM Carbon palette |

`{SKILL}` is the absolute path of this skill folder (e.g. `/mnt/skills/.../file-to-pptx`).
Always pass absolute paths.

## Brand assets

The IBM template and Carbon brand pack ship inside the bundle at
`scripts/assets/` and the converter resolves them itself, so **the normal
command passes no `--template` or `--brand`**. They live under `scripts/`
because the execution policy requires every skill file the runtime touches to
sit there; passing the flags explicitly still overrides the defaults when a
different brand is wanted.

## Standard Workflow

When the user uploads files and wants a deck:

1. **List the inputs.** Look at `/mnt/user-data/uploads/` to confirm what's
   there. Tell the user the detected files and their types in one short line.

2. **Pick a descriptive output name.** Derive it from the user's intent
   (e.g. `q4_diagnostic_findings.pptx`), not generic names like `output.pptx`.

3. **Run the converter** with the bundled IBM template and brand pack:

   ```bash
   python /path/to/file-to-pptx/scripts/universal_to_pptx.py \
     /mnt/user-data/uploads/file_a.md \
     /mnt/user-data/uploads/file_b.xlsx \
     /mnt/user-data/uploads/file_c.pdf \
     -o /mnt/user-data/outputs/<descriptive-name>.pptx
   ```

   The script prints a JSON summary with `slide_count`, `sources`, and `warnings`.
   Surface the warnings to the user.

4. **Deliver via `present_files`** — call it with the .pptx path so the user
   can download.

5. **Tell the user three things in one short paragraph:** slide count,
   any lossy decisions (OCR was used, .xlsm macros dropped, etc.), and an
   editing tip — "the charts are native, double-click to edit the data."

## Format Routing (handled by the script)

| Input | Slide(s) produced |
|---|---|
| `.pptx` | Each source slide appended (shapes/text preserved) |
| `.xlsx` / `.xlsm` | Per chartable sheet: one chart slide + paginated table slides. Macros dropped. |
| `.csv` / `.tsv` | One chart slide (if data is chartable) + paginated table slides |
| Text-based `.pdf` | Per page: native title, body bullets/headings in document order, **native PPTX table for each detected PDF table**, **embedded image slides** for each picture, hyperlinks preserved. Auto-paginates — text on one slide, each table/image on its own slide. |
| Scanned `.pdf` | OCR (tesseract) per page → title + body bullets. (Tables/images aren't detectable in raster-only PDFs.) |
| `.html` / `.htm` | h1/h2/h3 → slide titles. Body items rendered as **native** elements: paragraphs, bullets at any nesting depth, numbered lists, `<blockquote>` (italic + muted color), `<pre>`/`<code>` (monospace, blue-bordered light-blue rectangle), `<table>` (native PPTX table, blue header, white data cells, left-aligned text) |
| `.md` / `.markdown` | Pipes through HTML → same rules; original filename preserved in footer |
| `.txt` | First line → title; paragraphs → bullets; auto-paginates over 7 lines |
| Image (png/jpg/webp/gif/bmp) | Configurable via `options["image_mode"]`: `"embed"` (default — full-bleed image, OCR text in speaker notes), `"transcript"` (image at half size on left, editable OCR text on right — best when the user wants to keep visual reference AND edit text), `"overlay"` (experimental — places editable textboxes over the image with sampled background fills; works for clean document scans, looks patchy on multi-color slides) |
| `.bpmn` | One slide with native editable shapes — rounded rect = task, oval = start/end event, diamond = gateway |

A final **Source Index** slide is always appended (toggle off via
`options["include_source_index_slide"] = False`).

## Editability Guarantees

Every output slide consists of native, individually-clickable shapes. No
flattened images of slides; no rasterized tables or charts. Specifically:

- **Charts** use `CategoryChartData` — double-click in PowerPoint to open
  the embedded Excel data grid.
- **Tables** are native `add_table()` shapes — every cell editable; header
  row formatted in IBM blue with white bold text; data cells force white
  fill (overrides any banded-row master style that would reduce contrast).
- **Bullets** carry their nesting level (PPT indent levels 0–4) so the
  user can demote/promote in the outline.
- **Code blocks** are styled rectangles + text — re-color, re-size, paste
  new code without re-running the script.
- **Quotes** are italic-styled paragraphs in muted text color.
- **BPMN flow elements** are native MSO shapes — drag any task, gateway,
  or event individually.
- **Image-transcript mode** keeps both the original image (visual fidelity)
  and an editable text frame (full editability) on one slide — pick this
  mode when both matter.

## Editable Charts (the key guarantee)

The script uses `python-pptx`'s `add_chart()` with `CategoryChartData`. This
embeds an Excel workbook inside the .pptx. In PowerPoint or Keynote:

- Double-click any chart → the data grid opens in Excel
- Editing values updates the chart immediately
- Chart type (bar/line/pie) is auto-picked from data shape:
  - Date-like first column or > 12 rows → **line chart**
  - One numeric column with ≤ 6 rows → **pie chart**
  - Otherwise → **clustered column**

Override via `options["xlsx_chart_mode"]` = `"always"`, `"auto"` (default), or `"never"`.

## Brand Inheritance

The script opens the template with `python-pptx`, **strips the existing slides
while keeping the slide masters / layouts / theme intact**, then writes new
slides into that branded shell. This is how IBM Plex fonts, Carbon colors, and
the IBM Consulting footer carry through automatically.

To apply a different brand:
1. Drop the new corporate `.pptx` template into the user's uploads.
2. (Optional) Generate a matching brand JSON — same shape as `ibm_carbon.json`.
3. Pass both via `--template` and `--brand`.

## Dependencies

The script needs:

```bash
pip install python-pptx openpyxl pandas pdfplumber pillow markdown \
            beautifulsoup4 pytesseract lxml
# system: tesseract-ocr   (only needed for scanned PDFs and image OCR)
```

In Anthropic's standard sandboxed environment these are typically already
installed. If `python-pptx` is missing, install with `--break-system-packages`.

## Common Pitfalls (already handled, but worth knowing)

- **"NA" parsed as NaN**: pandas treats "NA" (a valid region code) as missing
  by default. The script reads spreadsheets with `keep_default_na=False` to
  preserve the literal string.
- **Pre-1900 dates**: month abbreviations like "Jan" parse to year 0001, which
  xlsxwriter (used by python-pptx for embedded chart data) cannot serialize.
  The script rejects date inferences outside the 1900–2200 range.
- **`.tmp.html` showing in footer**: the markdown handler converts to HTML
  internally; the script preserves the original `.md` filename in the footer.
- **Charts as images**: never deliver chart slides as exported PNGs; always
  use the native chart path. If a source xlsx has charts inside it that
  python-pptx can't recreate, fall back to a native chart from the same data
  rather than a screenshot.

## QA Checklist Before Delivery

Before calling `present_files`, confirm:

- [ ] The output exists at `/mnt/user-data/outputs/...`
- [ ] The `slide_count` looks reasonable (one per page, sheet, or h2 section)
- [ ] `warnings` is empty, or each warning is surfaced to the user
- [ ] The filename describes the content (not `output.pptx`)

Optional visual QA — render with LibreOffice and inspect:

```bash
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf <output>.pptx
pdftoppm -jpeg -r 110 <output>.pdf slide
```

Use `view slide-N.jpg` on a few pages to spot overflow, missing footers,
or unbranded color drift.

## When NOT to use this skill

- The user wants to **read** a `.pptx` (extract text/data) — use the `pptx`
  skill instead.
- The user wants to **create slides from scratch** with no input file —
  use the `pptx` skill's `pptxgenjs` flow.
- The user wants a Word doc, PDF, or spreadsheet output — use the `docx`,
  `pdf`, or `xlsx` skills respectively.
