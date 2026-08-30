---
name: web-document-search
description: Search the public web for documents and pages, then open and read them — via a fetch tool when available or by driving the browser (e.g. Chrome extension) when rendering is needed. Use this skill whenever the user asks to search, find, look up, google, or read something online — reports, filings, standards, press releases, documentation, news, "找一下", "search and read X" — or when a task needs facts that are not in context and not in an uploaded file. Also use it when the user provides a URL to open and read. Public sources only; it is the retrieval front-end for downstream analysis skills.
---

# Web Document Search

Find the right public document, open it with the lightest tool that works, read it, and report with attribution. Retrieval only — analysis belongs to downstream skills.

## Step 1 — Construct the search

- Keep queries short and specific: 2–6 content words (`<company> 2025 annual report`, `<regulation> full text pdf`). No filler verbs.
- Add discriminators when the target is a document: `pdf`, `annual report`, `10-K`, `press release`, `official`, the year.
- One search first; refine only if results miss. Vary the terms on retry — repeating a near-identical query returns the same results.
- For date-sensitive topics, include the current year explicitly.

## Step 2 — Rank the results

Trust order: **official source domain** (the company/agency/standards body itself) → **regulator or government repository** (sec.gov, official gazettes) → **primary publisher** → aggregators and news (corroboration only, never the primary source). Prefer the document itself over an article about the document.

Fiscal-year trap: results dated year N frequently cover fiscal year N−1. Verify the document states the period it covers before relying on it.

## Step 3 — Open and read (tool ladder)

Use the cheapest rung that works; escalate only on failure.

1. **Direct fetch tool** (if the environment has one): fetch the URL with text extraction. Fastest, cheapest. Works for most articles and hosted PDFs.
2. **Browser / Chrome extension** (when the page needs rendering — JS-built pages, viewers, interactive reports):
   - Navigate to the URL; wait for the page to finish rendering before reading.
   - Dismiss cookie/consent banners first — they block content extraction.
   - Scroll to trigger lazy-loaded sections before concluding content is missing.
   - Prefer reader mode or the site's print view when available — cleaner extraction.
   - Read in viewport-sized passes for long pages; capture the sections relevant to the question, not the whole site.
3. **PDF targets**: if the fetch tool extracts PDF text, use it. If the PDF opens in a browser viewer, download the file instead and hand it to `pdf-file-reader` — extraction from a viewer is unreliable.
4. **Dead ends**: if a result 404s or is soft-paywalled, try the next-ranked source. Report what could not be accessed rather than substituting a lower-quality source silently.

## Step 4 — Verify before using

- Confirm the document's own stated date, version, and scope — not the search snippet's.
- For anything feeding a decision (figures, legal text, specs), read the primary source directly; never quote a number only seen in a snippet or aggregator.
- If two sources conflict, say so and prefer the primary; do not average.

## Step 5 — Report with attribution

- Synthesize in your own words; quote sparingly (short fragments only) and always link the source URL.
- State retrieval metadata when it matters: publication date, version, and which tool/path was used if extraction was partial.
- If the requested document does not exist or is not public, say so plainly and offer the nearest public alternative — never fabricate a source.

## Boundaries

Public documents only. Do not bypass paywalls, logins, or access controls; do not scrape sites that prohibit it. If the target requires credentials the user holds, ask them to download and upload the file instead (then `pdf-file-reader` takes over).

## Hand-offs

- Retrieved annual report / filing → `annual-report-analyzer` for the structured digest
- Downloaded or uploaded PDF → `pdf-file-reader`
- Retrieved figures needing decomposition → `financial-variance-analysis`
- Multi-company retrieval → `earnings-peer-comparison`
