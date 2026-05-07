# 🕷️ Crawlerdex

> the bestiary of bots

**1600+ crawler user-agents.** Detection regex, real UA samples, rDNS verification, live block-rates. → [crawlerdex.tn3w.dev](https://crawlerdex.tn3w.dev)

Download:

```
https://github.com/tn3w/Crawlerdex/releases/latest/download/crawlers.json       # full
https://github.com/tn3w/Crawlerdex/releases/latest/download/crawlers.min.json   # no instances, no addition_date, minified (~57% smaller)
```

---

## Entry shape

```jsonc
{
  "pattern": "Googlebot\\/", // regex tested against User-Agent
  "description": "Google search indexing bot",
  "tags": ["search-engine"], // 1+ from the whitelist
  "instances": ["Googlebot/2.1 (+http://www.google.com/bot.html)", "..."],
  "url": "https://www.google.com/bot.html", // optional, official docs
  "addition_date": "2017/08/21", // optional, YYYY/MM/DD
  "depends_on": ["heritrix"], // optional, parent libs
  "rdns": [".google.com", ".googlebot.com"], // optional, FCrDNS suffixes
}
```

`rdns` = forward-confirmed reverse-DNS suffixes. A bot is genuine only when its IP rDNS ends in one of these **and** a forward lookup returns the same IP.

## Tags

| Tag                  | Block risk  |                            |
| -------------------- | ----------- | -------------------------- |
| `search-engine`      | Low         | web search indexing        |
| `ai-crawler`         | High        | autonomous AI training     |
| `ai-fetcher`         | Varies      | user-prompted single fetch |
| `social-preview`     | Low         | link previews              |
| `seo`                | Medium      | SEO / backlink analysis    |
| `monitoring`         | Low         | uptime / health probes     |
| `feed-reader`        | Low         | RSS / Atom                 |
| `archiver`           | Low         | preservation               |
| `advertising`        | Low/Medium  | ad quality, conversion     |
| `scanner`            | High        | security / vuln scanners   |
| `http-library`       | Medium/High | generic HTTP clients       |
| `browser-automation` | Medium/High | headless browsers          |
| `academic`           | Low         | research crawlers          |

## Frontend

`docs/` = source (`index.html`, `404.html`, `_crawler-template.html`, `CNAME`). `tools/build_pages.py` reads template + `docs/data/` → emits per-crawler pages, `robots.txt`, `sitemap.xml`, copies sources into `dist/`. Pages deploy from `dist/`. rDNS suffixes shown in modal + per-crawler page (FCrDNS section). Block-rate from [robots-radar](https://github.com/tn3w/robots-radar).

```bash
mkdir -p docs/data && cp crawlers.json docs/data/
python3 tools/build_pages.py
python3 -m http.server -d dist
```

## Validation

`tools/validate.py`: schema, types, tag whitelist, ReDoS (static + dynamic 50 ms probe), pattern/instance match, cross-matches, browser smoke test (~30k real + 2000 synthetic UAs), canonical formatting.

```bash
python3 tools/validate.py
```

Stats summary printed after every run. Exit `1` on any error.

## Format & lint

```bash
python3 -m venv .venv && .venv/bin/pip install ruff
.venv/bin/ruff format . && .venv/bin/ruff check --fix .
npx --yes prettier --write --single-quote --print-width=100 --trailing-comma=es5 --end-of-line=lf "**/*.{md,yml,yaml,html,css,js,ts}"
```

## Social banner

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install Pillow
python banner.py
```

## Credits

Forked from [monperrus/crawler-user-agents](https://github.com/monperrus/crawler-user-agents).
