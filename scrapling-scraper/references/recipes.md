# Scrapling recipes

Copy-paste patterns for common scraping tasks. Start with `Fetcher`; escalate
to `StealthyFetcher`/`DynamicFetcher` only when blocked or JS-rendered.

## Pagination (single-fetcher loop)

```python
from scrapling.fetchers import Fetcher

items, url = [], 'https://quotes.toscrape.com/'
while url:
    page = Fetcher.get(url)
    for q in page.css('.quote'):
        items.append({"text": q.css('.text::text').get(),
                      "author": q.css('.author::text').get()})
    nxt = page.css('.next a::attr(href)').get()
    url = page.urljoin(nxt) if nxt else None
```

For many pages, prefer the `Spider` framework (see api-reference.md) — it adds
concurrency and resume.

## Extract a table

```python
page = Fetcher.get(url)
rows = []
for tr in page.css('table#data tr'):
    cells = tr.css('td::text').getall()
    if cells:
        rows.append(cells)
```

## Follow detail links (list → detail page)

```python
page = Fetcher.get('https://site.com/list')
records = []
for link in page.css('.item a::attr(href)').getall():
    detail = Fetcher.get(page.urljoin(link))
    records.append({
        "title": detail.css('h1::text').get(),
        "price": detail.css('.price::text').get(),
    })
```

## Login / session-based scraping

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as s:
    s.post('https://site.com/login', data={'user': 'x', 'pass': 'y'})
    page = s.get('https://site.com/dashboard')   # cookies persist
    data = page.css('.private::text').getall()
```

## Proxy

```python
page = Fetcher.get('https://example.com', proxy='http://user:pass@host:port')
```

## Concurrent async fetching

```python
import asyncio
from scrapling.fetchers import AsyncDynamicSession

async def main(urls):
    async with AsyncDynamicSession(max_pages=4) as s:
        pages = await asyncio.gather(*(s.fetch(u) for u in urls))
        return [p.css('h1::text').get() for p in pages]

asyncio.run(main(['https://a.com', 'https://b.com']))
```

## Cloudflare-protected site

```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://protected.com', solve_cloudflare=True,
                             headless=True, network_idle=True)
```

## Export results

```python
import json, csv

with open('out.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

with open('out.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=items[0].keys())
    w.writeheader(); w.writerows(items)
```

From a Spider, use the built-in exporters: `result.items.to_json(...)`,
`result.items.to_jsonl(...)`.

## Adaptive scraper (re-runnable, survives redesigns)

```python
# First run records element fingerprints; later runs relocate them.
page = Fetcher.get(url)
products = page.css('.product', auto_save=True)      # switch to adaptive=True on subsequent runs
```

## Debugging an empty result

1. Print the status / a slice of `page.html_content` to confirm you got real HTML.
2. If it's a challenge/redirect page → escalate to `StealthyFetcher`.
3. If the data is missing from HTML but visible in a browser → it's JS-rendered;
   use `DynamicFetcher` with `network_idle=True`.
4. Re-check the selector in `scrapling shell` against the live page.
