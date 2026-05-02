# Crawlerdex

> the bestiary of bots

Structured database of 1600+ web crawler user agents for bot detection, filtering, and classification — paired with a live "bestiary" frontend that visualizes how often the top 25k sites block each one.

## crawlers.json

Array of crawler entries:

```json
[
    {
        "pattern": "Googlebot\\/",
        "url": "http://www.google.com/bot.html",
        "description": "Google's main web crawling bot for search indexing",
        "tags": ["search-engine"],
        "instances": [
            "Googlebot/2.1 (+http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        ]
    }
]
```

| Field         | Type     | Description                                      |
| ------------- | -------- | ------------------------------------------------ |
| `pattern`     | string   | Regex to match against `User-Agent`              |
| `url`         | string   | Official bot documentation page                  |
| `description` | string   | ≤10 word summary                                 |
| `tags`        | string[] | Purpose tags (see below)                         |
| `instances`   | string[] | Real-world `User-Agent` strings seen in the wild |

### Tags

| Tag                  | Purpose                                  | Block risk  |
| -------------------- | ---------------------------------------- | ----------- |
| `search-engine`      | Web search indexing                      | Low         |
| `ai-crawler`         | AI/LLM training or inference             | Varies      |
| `social-preview`     | Link previews in social/messaging apps   | Low         |
| `seo`                | SEO tools, backlink analyzers            | Medium      |
| `monitoring`         | Uptime checks, health probes             | Low         |
| `feed-reader`        | RSS/Atom feed fetchers                   | Low         |
| `archiver`           | Web archiving and preservation           | Low         |
| `advertising`        | Ad quality checks, conversion tracking   | Low–Medium  |
| `scanner`            | Security scanners, vulnerability testers | High        |
| `http-library`       | Generic HTTP client libraries            | Medium–High |
| `browser-automation` | Headless browsers, automation frameworks | Medium–High |
| `academic`           | Research and academic crawlers           | Low         |

## Frontend (`docs/`)

Static site deployed to [crawlerdex.tn3w.dev](https://crawlerdex.tn3w.dev) via GitHub Pages.

| File                                          | Purpose                                                                   |
| --------------------------------------------- | ------------------------------------------------------------------------- |
| `index.html`                                  | Bestiary UI: search, UA paste-match, tag chips, modal w/ block-rate chart |
| `404.html`                                    | Themed not-found page                                                     |
| `_crawler-template.html`                      | Placeholder template (`{{NAME}}`, `{{PATTERN}}`, …) for per-crawler page  |
| `CNAME`                                       | Custom domain                                                             |
| `robots.txt`, `sitemap.xml`, `<Crawler>.html` | Generated in CI by `tools/build_pages.py` (gitignored)                    |

- Hero search → live filter across pattern/description/instances
- Paste full `User-Agent` (>40 chars or contains `Mozilla`/`compatible;`) → longest-pattern regex wins
- Category chips → multi-select tag filter
- Each card is `<a href="/<Name>">` → static SEO page (left-click intercepted → modal; cmd/ctrl/middle-click → page)
- Block-rate: [robots-radar](https://github.com/tn3w/robots-radar) `crawler-block-percentages.json` → SVG line+area chart
- Favicons: DuckDuckGo `icons.duckduckgo.com/ip3/{domain}.ico` (fallback: initials)
- Aesthetic: Fraunces/JetBrains Mono, dotted paper bg, drifting bot emojis, hard offset shadows

## Static SEO pages

`tools/build_pages.py` reads `crawlers.json`, fills `docs/_crawler-template.html`, and writes:

- `docs/<CrawlerName>.html` — one per crawler, with `<title>`, meta description, keywords, OpenGraph, JSON-LD `TechArticle`/`SoftwareApplication`, canonical URL
- `docs/robots.txt` — `Allow: /` for `*` and every named crawler, plus sitemap link
- `docs/sitemap.xml` — homepage + every crawler URL with `lastmod`

Triggered by GitHub Actions (`.github/workflows/deploy-pages.yml`) on every push, release, robots-radar feed update, and daily cron.

Run locally:

```bash
python3 tools/build_pages.py
python3 -m http.server -d docs
```

## Social preview banner

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install Pillow
python banner.py
```

## Credits

Special thanks to [monperrus/crawler-user-agents](https://github.com/monperrus/crawler-user-agents).
