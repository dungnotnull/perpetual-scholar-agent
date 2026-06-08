"""Ingestion pipeline: RSS feed fetcher (Medium, HN, etc.)."""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import List, Optional

import httpx

from agent.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class RSSItem:
    """Structured representation of an RSS feed entry."""
    source: str = "rss"
    source_id: str = ""          # URL hash
    title: str = ""
    url: str = ""
    description: str = ""
    content_hash: str = ""
    priority_score: float = 0.0


def fetch_rss_feeds(
    feed_urls: Optional[List[str]] = None,
) -> List[RSSItem]:
    """Fetch and parse RSS/Atom feeds.

    Uses httpx to download feed XML and basic XML parsing.
    Falls back to crawl4ai for complex feeds.

    Args:
        feed_urls: List of RSS/Atom feed URLs. Defaults to settings.

    Returns:
        List of RSSItem objects.
    """
    import xml.etree.ElementTree as ET

    if feed_urls is None:
        feed_urls = [f.strip() for f in settings.rss_feeds.split(",")]

    items: List[RSSItem] = []

    for url in feed_urls:
        try:
            resp = httpx.get(url, follow_redirects=True, timeout=15.0)
            resp.raise_for_status()

            # Parse Atom or RSS XML
            root = ET.fromstring(resp.content)

            # Atom format: <feed><entry>...
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns) or root.findall("entry")

            # RSS format: <rss><channel><item>...
            if not entries:
                entries = root.findall(".//item")

            for entry in entries[:20]:  # limit per feed
                title = _get_text(entry, "title") or _get_text(entry, "atom:title", ns) or ""
                link = _get_text(entry, "link") or _get_text(entry, "atom:link", ns) or ""
                desc = _get_text(entry, "description") or _get_text(entry, "summary") or ""

                # Atom <link href="..." />
                if not link:
                    link_el = entry.find("atom:link", ns) or entry.find("link")
                    if link_el is not None:
                        link = link_el.get("href", link_el.text or "")

                content = f"{title}\n{desc}"
                content_hash = hashlib.sha256(content.encode()).hexdigest()

                items.append(RSSItem(
                    source="rss",
                    source_id=hashlib.sha256(link.encode()).hexdigest()[:16],
                    title=title,
                    url=link,
                    description=desc[:500],
                    content_hash=content_hash,
                ))

        except Exception as e:
            logger.warning(f"Failed to fetch RSS feed {url}: {e}")
            continue

    logger.info(f"Fetched {len(items)} items from {len(feed_urls)} RSS feeds")
    return items


def _get_text(element, tag: str, ns: dict = None) -> Optional[str]:
    """Extract text from an XML element, trying with and without namespace."""
    if ns:
        child = element.find(tag, ns)
        if child is not None and child.text:
            return child.text.strip()
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return None


async def fetch_with_crawl4ai(url: str) -> Optional[str]:
    """Fallback: use crawl4ai to extract content from a URL.

    Args:
        url: URL to crawl.

    Returns:
        Extracted markdown content, or None.
    """
    try:
        from crawl4ai import AsyncWebCrawler

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            if result.success and result.markdown:
                return result.markdown
    except Exception as e:
        logger.warning(f"crawl4ai failed for {url}: {e}")
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    items = fetch_rss_feeds()
    for item in items[:5]:
        print(f"  {item.title[:80]}...")
