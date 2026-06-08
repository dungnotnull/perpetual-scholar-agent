"""Ingestion pipeline: GitHub Trending fetcher."""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class GitHubItem:
    """Structured representation of a trending GitHub repository."""
    source: str = "github"
    source_id: str = ""           # repo full_name e.g. "user/repo"
    title: str = ""
    url: str = ""
    description: str = ""
    stars: int = 0
    language: str = ""
    topics: List[str] = field(default_factory=list)
    content_hash: str = ""
    priority_score: float = 0.0


def fetch_github_trending(
    languages: Optional[List[str]] = None,
    since: str = "daily",
    max_results: int = 30,
) -> List[GitHubItem]:
    """Fetch trending repositories from GitHub.

    Uses PyGithub to search for popular repos by language as a proxy
    for the GitHub Trending page (which has no official API).

    Args:
        languages: Programming languages to search. Defaults to settings.
        since: Time period — "daily", "weekly", "monthly".
        max_results: Maximum repos per language.

    Returns:
        List of GitHubItem objects.
    """
    from github import Github

    languages = languages or settings.github_languages_list
    github_token = settings.github_token

    g = Github(github_token) if github_token else Github()
    items: List[GitHubItem] = []

    # Map 'since' to GitHub stars timeframe
    stars_threshold = {
        "daily": 10,      # Created in last day with 10+ stars
        "weekly": 50,     # Created in last week with 50+ stars
        "monthly": 100,   # Created in last month with 100+ stars
    }.get(since, 10)

    for lang in languages:
        try:
            query = f"language:{lang} stars:>{stars_threshold}"
            repos = g.search_repositories(query=query, sort="stars")

            count = 0
            for repo in repos:
                if count >= max_results:
                    break

                content = f"{repo.full_name}\n{repo.description or ''}"
                content_hash = hashlib.sha256(content.encode()).hexdigest()

                item = GitHubItem(
                    source="github",
                    source_id=repo.full_name,
                    title=repo.full_name,
                    url=repo.html_url,
                    description=repo.description or "",
                    stars=repo.stargazers_count,
                    language=repo.language or lang,
                    topics=list(repo.get_topics()),
                    content_hash=content_hash,
                )
                items.append(item)
                count += 1

        except Exception as e:
            logger.warning(f"GitHub search failed for language '{lang}': {e}")
            continue

    logger.info(f"Fetched {len(items)} trending repos from GitHub (languages: {languages})")
    return items


def fetch_repo_readme(full_name: str) -> Optional[str]:
    """Fetch the README content of a GitHub repository.

    Args:
        full_name: Repository full name (e.g. "user/repo").

    Returns:
        README content as string, or None if not found.
    """
    from github import Github

    g = Github(settings.github_token) if settings.github_token else Github()

    try:
        repo = g.get_repo(full_name)
        readme = repo.get_readme()
        return readme.decoded_content.decode("utf-8", errors="replace")
    except Exception as e:
        logger.warning(f"Could not fetch README for {full_name}: {e}")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    repos = fetch_github_trending(max_results=5)
    for r in repos[:3]:
        print(f"  {r.source_id} (★{r.stars}): {(r.description or '')[:60]}...")
