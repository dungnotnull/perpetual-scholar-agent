"""Ingestion pipeline: __init__.py — public API."""
from agent.ingestion.arxiv_fetcher import PaperItem, fetch_arxiv_papers
from agent.ingestion.github_fetcher import GitHubItem, fetch_github_trending, fetch_repo_readme
from agent.ingestion.rss_fetcher import RSSItem, fetch_rss_feeds
from agent.ingestion.deduplicator import compute_content_hash, deduplicate_items
from agent.ingestion.embedder import embed_text, embed_batch, compute_priority_score, score_items

__all__ = [
    "PaperItem",
    "fetch_arxiv_papers",
    "GitHubItem",
    "fetch_github_trending",
    "fetch_repo_readme",
    "RSSItem",
    "fetch_rss_feeds",
    "compute_content_hash",
    "deduplicate_items",
    "embed_text",
    "embed_batch",
    "compute_priority_score",
    "score_items",
]
