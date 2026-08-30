---
name: scrapling-scraper
description: >-
  Scrape and crawl websites with Scrapling, the adaptive Python web-scraping
  framework. Use when the user wants to extract data from web pages, scrape a
  site, crawl multiple pages, parse HTML, bypass anti-bot protection (Cloudflare
  Turnstile, bot detection), automate a browser for scraping, build a spider/
  crawler, or pull structured data (prices, listings, quotes, articles, tables,
  links) from one or many URLs. Covers plain HTTP fetching, stealth browser
  fetching, full browser automation, CSS/XPath/regex parsing, adaptive element
  tracking that survives site redesigns, and concurrent crawling with pause/
  resume. Triggers on "scrape", "crawl", "extract from <url>", "parse this page",
  "get data off this site", "bypass Cloudflare", "build a scraper".
---

# Scrapling web scraper

Scrapling is an adaptive web-scraping framework for Python 3.10+. It spans a
single request to a full-scale crawl, adapts when sites change structure, and
bypasses common anti-bot protections. This skill is the playbook for using it.

## Setup (do this first, once)

```bash
pip install "scrapling[fetchers]"   # parser + HTTP/browser fetchers
scrapling install                   # install the browser binaries (needed for stealth/dynamic)
```

- Parser only (no fetching): `pip install scrapling`
- Everything (MCP server + shell): `pip install "scrapling[all]"`

If a script fails with a missing-browser error, the user skipped `scrapling install` — run it.

## Choosing a fetcher — decision rule

Pick the **lightest** fetcher that works; only escalate when blocked or when the
data is rendered by JavaScript.

| Situation | Use |
|-----------|-----|
| Static HTML, no JS, no bot wall | `Fetcher` (plain HTTP, fastest) |
| Site blocks bots / Cloudflare Turnstile | `StealthyFetcher` with `solve_cloudflare=True` |
| Data only appears after JS runs / needs clicks/scrolling | `DynamicFetcher` (full browser) |
| Many pages, follow links, resumable | `Spider` framework |

Always start with `Fetcher`. If you get a 403/429, an empty result, or a
challenge page, escalate to `StealthyFetcher`. Use `DynamicFetcher` only when
content is genuinely client-rendered.

## Minimal workflow

1. **Fetch** the page with the chosen fetcher → returns a `page` object.
2. **Select** with `.css(...)`, `.xpath(...)`, `.find_all(...)`, or `.re(...)`.
3. **Extract** with `::text` / `::attr(name)` plus `.get()` (first) or `.getall()` (all).
4. **Save** results (JSON/JSONL/CSV) and report a short summary to the user.

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = [
    {
        "text": q.css('.text::text').get(),
        "author": q.css('.author::text').get(),
        "tags": q.css('.tag::text').getall(),
    }
    for q in page.css('.quote')
]
```

## Bypassing anti-bot protection

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://example.com',
    headless=True,
    solve_cloudflare=True,    # solves Cloudflare Turnstile automatically
    network_idle=True,        # wait for network to settle
)
```

## JavaScript-rendered pages

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://example.com', network_idle=True)
data = page.css('#app .item::text').getall()
```

## Adaptive selectors (survive site redesigns)

When building a scraper meant to run repeatedly, pass `auto_save=True` on first
run and `adaptive=True` on later runs so Scrapling relocates elements after the
site's markup changes:

```python
products = page.css('.product', auto_save=True)   # first run: remember these
products = page.css('.product', adaptive=True)     # later: relocate if markup moved
```

## Multi-page crawling — use the Spider framework

For more than a handful of pages, or any link-following, write a `Spider`
instead of looping fetchers manually. It gives concurrency, polite throttling,
robots.txt obedience, and Ctrl+C pause / resume (rerun with the same
`crawldir`). See `references/api-reference.md` for the full spider API.

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10
    robots_txt_obey = True

    async def parse(self, response: Response):
        for q in response.css('.quote'):
            yield {"text": q.css('.text::text').get(),
                   "author": q.css('.author::text').get()}
        nxt = response.css('.next a')
        if nxt:
            yield response.follow(nxt[0].attrib['href'])

result = QuotesSpider(crawldir="./crawl_data").start()
result.items.to_json("output.json")
```

## Quick one-offs without writing a script — the CLI

```bash
scrapling extract get 'https://example.com' out.md --css-selector '#target'
scrapling extract stealthy-fetch 'https://site.com' out.html --solve-cloudflare
scrapling shell    # interactive REPL with a fetched page in scope
```

## Alternative: Scrapling's own MCP server

Scrapling ships an MCP server that exposes its fetching/parsing as native tools,
so an agent can scrape without writing or running any Python. This is an
alternative to the write-and-run-Python path above — useful for repeated
interactive scraping or when you'd rather call a tool than manage a script.

```bash
pip install "scrapling[ai]"
scrapling mcp-server          # starts the server (stdio)
```

Register it once in Claude Code, then the tools are available in every session:

```bash
claude mcp add scrapling -- scrapling mcp-server
```

Or add it manually to `~/.claude.json` (or a project `.mcp.json`):

```json
{
  "mcpServers": {
    "scrapling": { "command": "scrapling", "args": ["mcp-server"] }
  }
}
```

When to prefer which:
- **This skill (Python)** — full control, custom logic, spiders, exporting,
  anything multi-step or programmatic.
- **MCP server** — quick interactive fetch/parse as tool calls, no script to
  manage. The two coexist; the skill's guidance (fetcher choice, selectors,
  operating rules) still applies when driving the MCP tools.

## Reference files

- `references/api-reference.md` — complete fetcher/session/parser/spider API,
  every method, arguments, async variants, and the MCP server.
- `references/recipes.md` — copy-paste patterns: pagination, tables, proxies,
  sessions/login, concurrent async fetching, exporting data.

## Operating rules

- **Respect the target.** Obey robots.txt (`robots_txt_obey = True`), set a
  reasonable `download_delay`, and don't hammer a site. Only scrape data the
  user is authorized to collect; decline clearly abusive targets (login-walled
  private data, credential stuffing, mass PII harvesting).
- **Escalate fetchers, don't over-reach.** Reach for stealth/browser modes only
  after plain HTTP fails — they are slower and heavier.
- **Verify selectors before scaling.** Fetch one page, confirm your CSS/XPath
  returns the expected values, *then* run the full crawl.
- **Report honestly.** If a fetch returned a challenge page or empty result, say
  so and show what you got — don't fabricate scraped values.
