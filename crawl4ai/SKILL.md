---
name: crawl4ai
description: >
  Crawl websites into LLM-ready Markdown or structured JSON with Crawl4AI —
  a headless-browser crawler with content filtering, schema extraction, deep
  crawling and batch dispatch. Use when asked to scrape or crawl a site, turn
  documentation or a docs tree into Markdown for a RAG corpus, pull the same
  fields off many pages, follow links N levels deep, or crawl a JavaScript-
  rendered page that a plain fetch returns empty. Trigger on: "crawl this
  site", "scrape these pages", "turn these docs into markdown", "build a
  corpus from this domain", "crawl4ai", "crwl", "抓整個網站", "把文件轉成
  markdown 餵給模型". Not for reading a single static page (use WebFetch), not
  for exploring an app's UI (browser-recon), not for anti-bot-heavy targets
  needing adaptive selectors (scrapling-scraper).
metadata:
  model: opus
  effort: high
  source: grace-skill-pack
  upstream: https://github.com/Grace9393/crawl4ai
  verified_against: crawl4ai 0.9.2
---

# Crawl4AI

<!-- grace-skill-pack: run this on **opus** at effort `high` — crawls run
     unattended for many steps and a bad filter wastes the whole run. Route a
     subagent to it rather than switching the session. -->

An async Playwright-backed crawler whose output is shaped for models rather
than for browsers: Markdown with the navigation and boilerplate already pruned,
or JSON matching a schema you declare.

Verified against **0.9.2**. Check `crawl4ai.__version__` before trusting any
signature below on a different install.

## Pick the right tool first

| Situation | Use |
|---|---|
| One page, static HTML, you want the text | `WebFetch` — do not spin up a browser |
| Many pages, or JS-rendered, or you want clean Markdown | **this skill** |
| Documenting a live app's UI and its options | `browser-recon` |
| Target fights you — rotating selectors, bot walls | `scrapling-scraper` |
| You need the page's own network/console behaviour | browser tools directly |

## Install

```bash
pip install -U crawl4ai
crawl4ai-setup
```

`crawl4ai-setup` installs the Playwright browser. Without it every crawl fails
at launch — this is the single most common "it doesn't work" report. Verify:

```bash
crwl https://example.com -o markdown
```

## The minimum that works

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://www.nbcnews.com/business")
        print(result.markdown)

asyncio.run(main())
```

Always use the async context manager. It owns the browser lifecycle; without it
you leak a Chromium process per crawl.

## The four things worth reaching for it

### 1. Markdown that is actually clean

`result.markdown` is a `MarkdownGenerationResult`, not a string:

| Attribute | What it is |
|---|---|
| `.raw_markdown` | The whole page converted |
| `.fit_markdown` | Boilerplate pruned — nav, footers, ad rails |
| `.markdown_with_citations` / `.references_markdown` | Links moved to a reference list |

**Gotcha:** `result.fit_markdown` and `result.markdown_v2` were removed and now
raise `AttributeError` with a message pointing at the replacement. Use
`result.markdown.fit_markdown`. Code written against older tutorials breaks here.

`.fit_markdown` is only populated when a content filter is configured on the
markdown generator — `PruningContentFilter` for heuristic pruning,
`BM25ContentFilter` when you have a query, `LLMContentFilter` when neither is
good enough and you accept the cost.

### 2. Structured extraction without an LLM

Reach for the LLM strategy last, not first.

| Strategy | Use when |
|---|---|
| `JsonCssExtractionStrategy` | The fields sit at stable CSS selectors. **Default choice.** |
| `JsonXPathExtractionStrategy` / `JsonLxmlExtractionStrategy` | XPath is the cleaner expression |
| `RegexExtractionStrategy` | Prices, dates, IDs — anything a pattern nails |
| `LLMExtractionStrategy` | Layout varies per page and no selector generalises |
| `CosineStrategy` | Semantic clustering of blocks |

A schema strategy costs one browser fetch per page. `LLMExtractionStrategy`
costs that plus a model call per chunk — on a 500-page crawl that is the
difference between minutes and a bill. Write the selector.

### 3. Deep crawling

`BFSDeepCrawlStrategy` (breadth), `DFSDeepCrawlStrategy` (depth),
`BestFirstCrawlingStrategy` (scored frontier — usually what you want).

Constrain it or it wanders off-domain and burns the run:

- `FilterChain` of `DomainFilter`, `URLPatternFilter`, `ContentTypeFilter`,
  `SEOFilter`, `ContentRelevanceFilter`
- scorers to order the frontier: `KeywordRelevanceScorer`, `PathDepthScorer`,
  `FreshnessScorer`, `DomainAuthorityScorer`, `CompositeScorer`

**Always set a page cap.** An uncapped deep crawl on a docs site with a
calendar widget is effectively infinite.

```bash
crwl https://docs.crawl4ai.com --deep-crawl bfs --max-pages 10
```

### 4. Batch with backpressure

```python
results = await crawler.arun_many(urls, config=run_config, dispatcher=dispatcher)
```

`MemoryAdaptiveDispatcher` throttles on host memory — the right default for a
few hundred URLs on a laptop. `SemaphoreDispatcher` for a fixed concurrency.
`RateLimiter` when the target's limits, not yours, are the constraint.
`config` also accepts a **list** of `CrawlerRunConfig`, one per URL.

## Caching

`CacheMode.ENABLED` (read+write) · `DISABLED` · `READ_ONLY` · `WRITE_ONLY` ·
`BYPASS`. Set it on `CrawlerRunConfig`.

Develop against `ENABLED` so iterating on a selector does not re-fetch. Switch
to `BYPASS` for the real run when freshness matters. Silently crawling a stale
cache and reporting it as current is the failure this parameter causes.

## CLI

```bash
crwl https://www.nbcnews.com/business -o markdown
crwl https://docs.crawl4ai.com --deep-crawl bfs --max-pages 10
crwl https://www.example.com/products -q "Extract all product prices"
```

Good for a one-off or for sanity-checking that the browser install works.
Anything repeatable belongs in a script.

## Also in the box

- `AdaptiveCrawler.digest(start_url, query, resume_from=...)` — crawls until it
  has enough to answer `query` rather than to a fixed depth, and **resumes**.
  The right shape for "research this topic on this site".
- `AsyncUrlSeeder` / `DomainMapper` — enumerate a site's URLs before crawling.
- `PDFContentScrapingStrategy` — PDFs through the same pipeline.
- `LLMTableExtraction` / `DefaultTableExtraction` — tables as data, not as text.
- `VirtualScrollConfig` — infinite-scroll feeds.
- `BrowserProfiler` / `ProxyConfig` / `GeolocationConfig` — persistent logged-in
  profiles, proxy rotation, locale pinning.
- `Crawl4aiDockerClient` — talk to a `crawl4ai` server instead of a local browser.

## Run discipline

1. **Say what you are crawling and how many pages, before starting.** A deep
   crawl is an unattended run; the user should not learn its size from the bill.
2. **Test on 2–3 URLs first.** Confirm the selector or filter produces what you
   expect, then scale. Never debug a schema at 500 pages.
3. **Respect the target.** Check `robots.txt` and keep a rate limiter on. Do not
   crawl behind a login the user has not told you to use.
4. **Report what failed.** `arun_many` returns results for the failures too —
   count them and name the failing URLs. A crawl that silently dropped 40% of
   its pages is worse than one that errored.
5. **Write the corpus to one canonical path** and end with a manifest: absolute
   path, page count, total bytes, and the URLs that did not make it.
