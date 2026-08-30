# Scrapling API reference

Python 3.10+. Install: `pip install "scrapling[fetchers]"` then `scrapling install`.

## Fetchers

All fetchers return a `page` (Selector) object exposing the parsing API below.

### Fetcher — plain HTTP (fastest, no browser)

```python
from scrapling.fetchers import Fetcher, FetcherSession

page = Fetcher.get('https://example.com')
page = Fetcher.post('https://example.com', data={'k': 'v'})

# Persistent cookies/state across requests:
with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com', stealthy_headers=True)
    page = session.post('https://example.com/login', data={...})
```

Key args: `impersonate` (TLS fingerprint, e.g. `'chrome'`), `stealthy_headers`,
`http3`, `timeout`, `proxy`.

### StealthyFetcher — anti-bot bypass (modified Firefox)

```python
from scrapling.fetchers import StealthyFetcher, StealthySession, AsyncStealthySession

page = StealthyFetcher.fetch('https://example.com', headless=True)
page = StealthyFetcher.fetch('https://site.com', solve_cloudflare=True)

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://example.com')

async with AsyncStealthySession() as session:
    page = await session.fetch('https://example.com')
```

Key args: `headless`, `solve_cloudflare`, `network_idle`, `google_search`, `max_pages`.

### DynamicFetcher — full browser automation (Playwright-based)

```python
from scrapling.fetchers import DynamicFetcher, DynamicSession, AsyncDynamicSession

page = DynamicFetcher.fetch('https://example.com')

with DynamicSession(headless=True, network_idle=True) as session:
    page = session.fetch('https://example.com', load_dom=False)

async with AsyncDynamicSession(max_pages=2) as session:
    results = await asyncio.gather(session.fetch(url1), session.fetch(url2))
```

Key args: `headless`, `disable_resources`, `network_idle`, `load_dom`, `timeout`.

## Parser / Selector API (on the returned `page` and on elements)

```python
# CSS
page.css('.quote')                      # list of elements
page.css('.text::text').get()           # first text
page.css('.text::text').getall()        # all texts
page.css('a::attr(href)').get()         # attribute

# XPath
page.xpath('//div[@class="quote"]')
page.xpath('//span[@class="text"]/text()').getall()

# BeautifulSoup-style
page.find_all('div', class_='quote')
page.find_all(class_='quote')
page.find_by_text('quote', tag='div')

# Regex
page.re(r'pattern')          # first match
page.re_all(r'pattern')      # all matches

# Element attributes & navigation
el = page.css('.quote')[0]
el.attrib['href']            # attribute dict
el.text                      # text content
el.parent
el.next_sibling
el.below_elements()
el.find_similar()            # find structurally similar siblings/elements

# Adaptive tracking (relocates elements after site redesign)
page.css('.product', auto_save=True)    # first run: store fingerprint
page.css('.product', adaptive=True)      # later runs: relocate if markup moved
```

## Spider framework

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10        # parallelism
    download_delay = 0.5            # politeness throttle (seconds)
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
result.items.to_jsonl("output.jsonl")
```

Pause/resume: press Ctrl+C mid-run; rerun with the same `crawldir` to continue.

### Multiple session types in one spider

```python
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            sid = "stealth" if "protected" in link else "fast"
            yield Request(link, sid=sid)
```

### Streaming items

```python
async for item in spider.stream():
    print(item)
```

## Standalone parser (parse HTML you already have)

```python
from scrapling import Selector
page = Selector(html_string)
page.css('.title::text').getall()
```

## CLI

```bash
scrapling shell                                  # interactive REPL
scrapling extract get URL out.md --css-selector '#target' --impersonate chrome
scrapling extract fetch URL out.md --css-selector '#target' --no-headless
scrapling extract stealthy-fetch URL out.html --css-selector '#x' --solve-cloudflare
scrapling install            # install browser binaries
scrapling install --force    # reinstall
```

## MCP server (let an agent drive Scrapling directly)

```bash
pip install "scrapling[ai]"
scrapling mcp-server
```

Register it as an MCP server in Claude/Cursor to expose Scrapling fetching/parsing as tools.
