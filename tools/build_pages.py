#!/usr/bin/env python3
"""Generate per-crawler SEO pages, robots.txt, sitemap.xml from crawlers.json."""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TEMPLATE_PATH = DOCS / "_crawler-template.html"
SITE = "https://crawlerdex.tn3w.dev"


def name_of(pattern: str) -> str:
    s = pattern
    s = re.sub(r"\\([\\/.\-+*?^$|(){}\[\]])", r"\1", s)

    def bracket(match: re.Match[str]) -> str:
        inner = match.group(1)
        upper = re.search(r"[A-Z]", inner)
        if upper:
            return upper.group(0)
        letter = re.search(r"[a-z]", inner)
        if letter:
            return letter.group(0)
        return inner[0] if inner else ""

    def paren(match: re.Match[str]) -> str:
        inner = re.sub(r"^\?[:!=<]", "", match.group(1))
        return inner.split("|")[0] or ""

    s = re.sub(r"\[([^\]]+)\]", bracket, s)
    s = re.sub(r"\(([^)]*)\)", paren, s)
    s = re.sub(r"[()|^$]", "", s)
    s = re.sub(r"[*+?]\??", "", s)
    s = re.sub(r"\{\d+(,\d*)?\}", "", s)
    s = re.sub(r"\\[bBwWsSdD]", "", s)
    s = re.sub(r"\.", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"[/\-_]+$", "", s).strip()
    return s or pattern


def slugify(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")
    return slug or "crawler"


def initials(name: str) -> str:
    parts = [p for p in re.split(r"[\s\-_]+", name) if p]
    return ("".join(p[0] for p in parts[:2]) or "?").upper()


def domain_of(url: str | None) -> str | None:
    if not url:
        return None
    match = re.match(r"^(?:https?://)?(?:www\.)?([^/]+)", url)
    return match.group(1) if match else None


def fill(template: str, values: dict[str, str]) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def build_values(crawler: dict, name: str, slug: str) -> dict[str, str]:
    pattern = crawler.get("pattern", "")
    description = crawler.get("description") or f"{name} web crawler user-agent details."
    tags = crawler.get("tags") or ["uncategorized"]
    instances = crawler.get("instances") or []
    url = crawler.get("url")
    added = crawler.get("addition_date")

    canonical = f"{SITE}/{quote(slug)}"
    title = f"{name} crawler — user-agent, pattern & block-rate · Crawlerdex"
    seo_desc = (
        f"{name}: {description} Detection regex, real User-Agent strings, "
        f"category tags, and live block-rate across the top 25 000 sites."
    )[:300]
    keywords = ", ".join(
        [
            name,
            f"{name} bot",
            f"{name} crawler",
            f"{name} user agent",
            f"{name} user-agent",
            f"is {name} a bot",
            f"block {name}",
            f"{name} robots.txt",
            *tags,
        ]
    )

    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": f"{name} web crawler",
            "description": seo_desc,
            "about": {
                "@type": "SoftwareApplication",
                "name": name,
                "applicationCategory": "WebCrawler",
                "operatingSystem": "Any",
                "url": url or canonical,
            },
            "keywords": keywords,
            "url": canonical,
            "isPartOf": {
                "@type": "WebSite",
                "name": "Crawlerdex",
                "url": SITE,
            },
        },
        indent=2,
    )

    domain = domain_of(url)
    favicon = f"https://icons.duckduckgo.com/ip3/{domain}.ico" if domain else ""
    icon_html = (
        f'<img src="{favicon}" alt="" width="64" height="64" '
        f'loading="lazy" decoding="async" '
        f"onerror=\"this.parentNode.textContent='{html.escape(initials(name))}'\">"
        if favicon
        else html.escape(initials(name))
    )

    instances_html = "".join(
        f'<div class="instance">{html.escape(i)}</div>' for i in instances[:20]
    ) or (
        '<div class="instance" style="opacity:.6;font-style:italic">'
        "no public sample user-agents recorded.</div>"
    )
    extra_instances = (
        f'<p class="more">+ {len(instances) - 20} more samples in '
        f'<a href="https://github.com/tn3w/Crawlerdex/blob/master/crawlers.json">'
        f"crawlers.json</a></p>"
        if len(instances) > 20
        else ""
    )

    tags_html = "".join(
        f'<a class="tag-mini" href="/?tag={quote(t)}">{html.escape(t)}</a>'
        for t in tags
    )

    ref_row = (
        f'<dt>Reference</dt><dd><a href="{html.escape(url)}" '
        f'rel="noopener" target="_blank">{html.escape(url)}</a></dd>'
        if url
        else ""
    )
    added_row = f"<dt>Added</dt><dd>{html.escape(added)}</dd>" if added else ""

    return {
        "TITLE": html.escape(title),
        "SEO_DESC": html.escape(seo_desc),
        "KEYWORDS": html.escape(keywords),
        "CANONICAL": canonical,
        "JSON_LD": json_ld,
        "NAME": html.escape(name),
        "PATTERN": html.escape(pattern),
        "DESCRIPTION": html.escape(description),
        "TAGS_TEXT": html.escape(", ".join(tags)),
        "TAGS_HTML": tags_html,
        "ICON": icon_html,
        "INSTANCES_HTML": instances_html,
        "EXTRA_INSTANCES": extra_instances,
        "INSTANCE_COUNT": str(len(instances)),
        "REF_ROW": ref_row,
        "ADDED_ROW": added_row,
    }


def write_robots(entries: list[tuple[str, str]]) -> None:
    lines = [
        "# Crawlerdex — bot bestiary",
        "# All crawlers welcome. We catalogue you, we don't fight you.",
        "",
        "User-agent: *",
        "Allow: /",
        "",
    ]
    for _, slug in entries:
        lines.append("User-agent: *")
        lines.append(f"Allow: /{slug}")
        lines.append("")
    lines.append(f"Sitemap: {SITE}/sitemap.xml")
    lines.append("")
    (DOCS / "robots.txt").write_text("\n".join(lines))


def write_sitemap(entries: list[tuple[str, str]]) -> None:
    today = datetime.now(timezone.utc).date().isoformat()
    urls = [
        f"<url><loc>{SITE}/</loc><lastmod>{today}</lastmod>"
        f"<changefreq>daily</changefreq><priority>1.0</priority></url>"
    ]
    for _, slug in entries:
        urls.append(
            f"<url><loc>{SITE}/{quote(slug)}</loc>"
            f"<lastmod>{today}</lastmod>"
            f"<changefreq>weekly</changefreq><priority>0.7</priority></url>"
        )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (DOCS / "sitemap.xml").write_text(body)


def main() -> int:
    crawlers = json.loads((ROOT / "crawlers.json").read_text())
    template = TEMPLATE_PATH.read_text()
    DOCS.mkdir(exist_ok=True)

    seen: set[str] = set()
    entries: list[tuple[str, str]] = []
    for crawler in crawlers:
        name = name_of(crawler["pattern"])
        slug = slugify(name)
        original = slug
        counter = 2
        while slug in seen:
            slug = f"{original}-{counter}"
            counter += 1
        seen.add(slug)
        page = fill(template, build_values(crawler, name, slug))
        (DOCS / f"{slug}.html").write_text(page)
        entries.append((name, slug))

    write_robots(entries)
    write_sitemap(entries)
    inject_index_links(entries)
    print(f"generated {len(entries)} crawler pages")
    return 0


def inject_index_links(entries: list[tuple[str, str]]) -> None:
    index_path = DOCS / "index.html"
    text = index_path.read_text()
    placeholder = "<!--CRAWLER_LINKS-->"
    if placeholder not in text:
        return
    links = "\n                ".join(
        f'<li><a href="/{quote(slug)}">{html.escape(name)}</a></li>'
        for name, slug in entries
    )
    index_path.write_text(text.replace(placeholder, links))


if __name__ == "__main__":
    sys.exit(main())
