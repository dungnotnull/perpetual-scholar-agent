"""Ingestion pipeline: arXiv paper fetcher."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import arxiv

from agent.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class PaperItem:
    """Structured representation of an arXiv paper."""
    source: str = "arxiv"
    source_id: str = ""           # arXiv ID e.g. "2106.09685"
    title: str = ""
    url: str = ""
    abstract: str = ""
    authors: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    published: Optional[datetime] = None
    content_hash: str = ""         # SHA-256 of (title + abstract)
    priority_score: float = 0.0


def fetch_arxiv_papers(
    categories: Optional[List[str]] = None,
    max_results: Optional[int] = None,
    since_hours: int = 24,
) -> List[PaperItem]:
    """Fetch recent papers from arXiv for specified categories.

    Args:
        categories: arXiv categories to search. Defaults to settings.
        max_results: Maximum papers to return. Defaults to settings.
        since_hours: Only return papers published in the last N hours.

    Returns:
        List of PaperItem objects.
    """
    import hashlib

    categories = categories or settings.arxiv_categories_list
    max_results = max_results or settings.arxiv_max_results

    client = arxiv.Client()
    query = " OR ".join(f"cat:{cat}" for cat in categories)

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    papers: List[PaperItem] = []

    for result in client.results(search):
        if result.published.replace(tzinfo=timezone.utc) < cutoff:
            continue

        content = f"{result.title}\n{result.summary}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        paper = PaperItem(
            source="arxiv",
            source_id=result.entry_id.split("/")[-1] if "/" in result.entry_id else result.entry_id,
            title=result.title,
            url=result.entry_id,
            abstract=result.summary.replace("\n", " ").strip(),
            authors=[a.name for a in result.authors],
            categories=result.categories,
            published=result.published,
            content_hash=content_hash,
        )
        papers.append(paper)

    logger.info(f"Fetched {len(papers)} papers from arXiv (categories: {categories})")
    return papers


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    papers = fetch_arxiv_papers(max_results=5)
    for p in papers[:3]:
        print(f"  {p.source_id}: {p.title[:80]}...")
