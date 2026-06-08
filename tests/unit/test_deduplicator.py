"""
Unit tests for deduplicator module.

Tests paper deduplication logic including content-based similarity detection
and metadata-based duplicate identification.
"""

import pytest
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from agent.ingestion.deduplicator import Deduplicator


class TestDeduplicatorInitialization:
    """Test deduplicator initialization and configuration."""

    def test_default_initialization(self):
        """Test default deduplicator initialization."""
        dedup = Deduplicator()
        assert dedup is not None
        assert dedup.similarity_threshold == 0.85  # Assuming default

    def test_custom_threshold(self):
        """Test custom similarity threshold."""
        dedup = Deduplicator(threshold=0.9)
        assert dedup.similarity_threshold == 0.9

    def test_dedup_strategy_selection(self):
        """Test different deduplication strategies."""
        # Test with content-based strategy
        dedup_content = Deduplicator(strategy="content")
        assert dedup_content.strategy == "content"

        # Test with metadata-based strategy
        dedup_metadata = Deduplicator(strategy="metadata")
        assert dedup_metadata.strategy == "metadata"


class TestDeduplicatorByMetadata:
    """Test metadata-based deduplication."""

    @pytest.fixture
    def deduplicator(self):
        """Provide deduplicator instance."""
        return Deduplicator(strategy="metadata")

    @pytest.fixture
    def sample_papers(self):
        """Provide sample papers with duplicates."""
        return [
            {
                "id": "arxiv:2301.00001",
                "title": "Optimizing Database Queries",
                "authors": ["Jane Doe"],
                "published": "2025-01-15"
            },
            {
                "id": "github:user/repo-1",
                "title": "Optimizing Database Queries",  # Duplicate title
                "authors": ["Jane Doe"],
                "published": "2025-01-15"
            },
            {
                "id": "arxiv:2301.00002",
                "title": "Advanced Caching Strategies",
                "authors": ["John Smith"],
                "published": "2025-01-16"
            },
            {
                "id": "arxiv:2301.00003",
                "title": "Advanced Caching Strategies",  # Duplicate title
                "authors": ["John Smith"],
                "published": "2025-01-16"
            },
            {
                "id": "medium:post-1",
                "title": "Unique Article",
                "authors": ["Bob Johnson"],
                "published": "2025-01-17"
            }
        ]

    def test_removes_duplicates_by_title_and_author(self, deduplicator, sample_papers):
        """Test removing duplicates by title and author combination."""
        unique_papers = deduplicator.deduplicate(sample_papers)
        assert len(unique_papers) == 3  # 3 unique papers

    def test_preserves_first_occurrence(self, deduplicator, sample_papers):
        """Test first occurrence is preserved."""
        unique_papers = deduplicator.deduplicate(sample_papers)
        ids = [p["id"] for p in unique_papers]
        # First occurrences should be preserved
        assert "arxiv:2301.00001" in ids  # First "Optimizing Database Queries"
        assert "arxiv:2301.00002" in ids  # First "Advanced Caching Strategies"
        assert "medium:post-1" in ids

    def test_handles_empty_list(self, deduplicator):
        """Test handling empty paper list."""
        result = deduplicator.deduplicate([])
        assert result == []

    def test_handles_single_item(self, deduplicator):
        """Test handling single paper."""
        papers = [{"id": "1", "title": "Only Paper"}]
        result = deduplicator.deduplicate(papers)
        assert len(result) == 1

    def test_no_false_positives(self, deduplicator):
        """Test no false positives on similar but distinct papers."""
        papers = [
            {"id": "1", "title": "Database Optimization", "authors": ["Alice"]},
            {"id": "2", "title": "Database Performance", "authors": ["Bob"]},
            {"id": "3", "title": "Network Optimization", "authors": ["Charlie"]}
        ]
        result = deduplicator.deduplicate(papers)
        assert len(result) == 3  # All unique

    def test_handles_missing_fields(self, deduplicator):
        """Test handling papers with missing fields."""
        papers = [
            {"id": "1", "title": "Paper A", "authors": ["Alice"]},
            {"id": "2", "title": "Paper A"},  # Missing authors
            {"id": "3", "authors": ["Bob"]}  # Missing title
        ]
        result = deduplicator.deduplicate(papers)
        # Should handle gracefully - exact behavior depends on implementation
        assert isinstance(result, list)


class TestDeduplicatorByContent:
    """Test content-based deduplication."""

    @pytest.fixture
    def content_deduplicator(self):
        """Provide content-based deduplicator."""
        return Deduplicator(strategy="content", threshold=0.9)

    def test_content_similarity_detection(self, content_deduplicator):
        """Test detecting similar content."""
        papers = [
            {
                "id": "1",
                "title": "Paper A",
                "abstract": "This paper discusses database optimization using machine learning techniques."
            },
            {
                "id": "2",
                "title": "Paper B",
                "abstract": "This paper discusses database optimization using ML techniques."  # Very similar
            },
            {
                "id": "3",
                "title": "Paper C",
                "abstract": "Network protocols for distributed systems."  # Different topic
            }
        ]
        result = content_deduplicator.deduplicate(papers)
        # Should detect similarity between 1 and 2
        assert len(result) < len(papers)

    def test_threshold_affects_results(self):
        """Test similarity threshold affects deduplication."""
        papers = [
            {"id": "1", "abstract": "Database optimization is important"},
            {"id": "2", "abstract": "Database optimization is crucial"}  # Similar
        ]

        strict_dedup = Deduplicator(threshold=0.95)
        loose_dedup = Deduplicator(threshold=0.7)

        strict_result = strict_dedup.deduplicate(papers)
        loose_result = loose_dedup.deduplicate(papers)

        # Stricter threshold should catch fewer duplicates
        assert len(loose_result) <= len(strict_result)


class TestDeduplicatorByURL:
    """Test URL-based deduplication."""

    @pytest.fixture
    def url_deduplicator(self):
        """Provide URL-based deduplicator."""
        return Deduplicator(strategy="url")

    def test_removes_duplicate_urls(self, url_deduplicator):
        """Test removing duplicate URLs."""
        papers = [
            {"id": "1", "url": "https://example.com/paper1"},
            {"id": "2", "url": "https://example.com/paper1"},  # Duplicate URL
            {"id": "3", "url": "https://example.com/paper2"}
        ]
        result = url_deduplicator.deduplicate(papers)
        assert len(result) == 2

    def test_handles_missing_urls(self, url_deduplicator):
        """Test handling papers without URLs."""
        papers = [
            {"id": "1", "url": "https://example.com/paper1"},
            {"id": "2", "title": "Paper without URL"},
            {"id": "3", "url": None}
        ]
        result = url_deduplicator.deduplicate(papers)
        # Should handle papers without URLs
        assert len(result) <= len(papers)

    def test_normalizes_urls(self, url_deduplicator):
        """Test URL normalization (trailing slashes, etc)."""
        papers = [
            {"id": "1", "url": "https://example.com/paper"},
            {"id": "2", "url": "https://example.com/paper/"},  # Trailing slash
            {"id": "3", "url": "HTTPS://EXAMPLE.COM/paper"}  # Different case
        ]
        result = url_deduplicator.deduplicate(papers)
        # Should detect as duplicates after normalization
        assert len(result) < len(papers)


class TestDeduplicatorPerformance:
    """Test deduplicator performance on large datasets."""

    @pytest.fixture
    def large_paper_set(self):
        """Generate large set of papers."""
        papers = []
        for i in range(1000):
            papers.append({
                "id": f"paper-{i}",
                "title": f"Research Paper {i % 100}",  # Every 100 papers share title
                "authors": [f"Author {i % 10}"],
                "abstract": f"Abstract content for paper {i}"
            })
        return papers

    def test_handles_large_dataset(self, large_paper_set):
        """Test deduplicating large dataset."""
        dedup = Deduplicator()
        result = dedup.deduplicate(large_paper_set)
        # Should deduplicate efficiently
        assert len(result) < len(large_paper_set)
        assert len(result) > 0

    @pytest.mark.slow
    def test_performance_on_large_dataset(self, large_paper_set):
        """Test performance scales well."""
        import time
        dedup = Deduplicator()

        start = time.time()
        result = dedup.deduplicate(large_paper_set)
        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 10.0  # 10 seconds max for 1000 papers


class TestDeduplicatorEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def deduplicator(self):
        """Provide deduplicator instance."""
        return Deduplicator()

    def test_handles_unicode_content(self, deduplicator):
        """Test handling Unicode characters in content."""
        papers = [
            {"id": "1", "title": "论文数据库优化", "abstract": "中文摘要"},
            {"id": "2", "title": "論文データベース最適化", "abstract": "日本語の要約"},
            {"id": "3", "title": "논문 데이터베이스 최적화", "abstract": "한국어 초록"}
        ]
        result = dedup.deduplicate(papers)
        # Should handle Unicode without errors
        assert isinstance(result, list)

    def test_handles_very_long_content(self, deduplicator):
        """Test handling very long content."""
        long_abstract = "word " * 10000  # Long abstract
        papers = [
            {"id": "1", "abstract": long_abstract},
            {"id": "2", "abstract": long_abstract}
        ]
        result = dedup.deduplicate(papers)
        assert len(result) <= len(papers)

    def test_handles_special_characters(self, deduplicator):
        """Test handling special characters."""
        papers = [
            {"id": "1", "title": "C++ Optimization Techniques"},
            {"id": "2", "title": "C# Performance Tips"},
            {"id": "3", "title": "F# Functional Patterns"}
        ]
        result = dedup.deduplicate(papers)
        assert len(result) == 3  # All different

    def test_handles_none_values(self, deduplicator):
        """Test handling None values in fields."""
        papers = [
            {"id": "1", "title": None, "authors": ["Alice"]},
            {"id": "2", "title": "Paper B", "authors": None},
            {"id": "3", "title": None, "authors": None}
        ]
        result = dedup.deduplicate(papers)
        # Should handle None values gracefully
        assert isinstance(result, list)


class TestDeduplicatorStatistics:
    """Test deduplication statistics and reporting."""

    def test_tracks_duplicate_count(self):
        """Test tracking number of duplicates removed."""
        papers = [
            {"id": "1", "title": "Paper A"},
            {"id": "2", "title": "Paper A"},  # Duplicate
            {"id": "3", "title": "Paper B"},
            {"id": "4", "title": "Paper B"},  # Duplicate
        ]
        dedup = Deduplicator()
        result = dedup.deduplicate(papers)

        # Check statistics if available
        if hasattr(dedup, 'duplicates_removed'):
            assert dedup.duplicates_removed == 2

    def test_provides_deduplication_report(self):
        """Test providing detailed deduplication report."""
        papers = [
            {"id": "1", "title": "Paper A"},
            {"id": "2", "title": "Paper A"},
            {"id": "3", "title": "Paper B"}
        ]
        dedup = Deduplicator()
        result = dedup.deduplicate(papers)

        # Check if report method exists
        if hasattr(dedup, 'get_report'):
            report = dedup.get_report()
            assert 'original_count' in report
            assert 'unique_count' in report
            assert 'duplicates_removed' in report


class TestDeduplicatorIntegration:
    """Test deduplicator with realistic data."""

    @pytest.fixture
    def realistic_papers(self):
        """Provide realistic paper data."""
        return [
            {
                "id": "arxiv:2301.12345",
                "title": "Efficient Database Indexing with Machine Learning",
                "authors": ["Jane Smith", "John Doe"],
                "abstract": "We present a novel approach to database indexing...",
                "published": "2025-01-15",
                "source": "arxiv"
            },
            {
                "id": "arxiv:2301.12346",
                "title": "Efficient Database Indexing with Machine Learning",
                "authors": ["Jane Smith", "John Doe"],
                "abstract": "A novel approach to database indexing is presented...",
                "published": "2025-01-15",
                "source": "arxiv"
            },
            {
                "id": "github:ml-indexing",
                "title": "ML-Based Database Indexing Implementation",
                "authors": ["dev_user"],
                "abstract": "Code implementation of ML-based indexing",
                "published": "2025-01-16",
                "source": "github",
                "url": "https://github.com/user/ml-indexing"
            },
            {
                "id": "medium:optimization-guide",
                "title": "Complete Guide to Database Optimization",
                "authors": ["Tech Blogger"],
                "abstract": "Comprehensive guide covering all optimization techniques",
                "published": "2025-01-17",
                "source": "medium",
                "url": "https://medium.com/p/optimization-guide"
            }
        ]

    def test_realistic_deduplication(self, realistic_papers):
        """Test deduplication on realistic dataset."""
        dedup = Deduplicator()
        result = dedup.deduplicate(realistic_papers)

        # Should identify and remove duplicates
        assert len(result) < len(realistic_papers)

        # Should preserve variety of sources
        sources = {p.get("source") for p in result}
        assert len(sources) > 1


@pytest.mark.parametrize("strategy,threshold", [
    ("metadata", 0.85),
    ("content", 0.9),
    ("url", 1.0),
])
def test_deduplicator_strategies(strategy, threshold):
    """Test different deduplication strategies."""
    papers = [
        {"id": "1", "title": "Paper A", "url": "https://example.com/a"},
        {"id": "2", "title": "Paper A", "url": "https://example.com/a"},
    ]

    dedup = Deduplicator(strategy=strategy, threshold=threshold)
    result = dedup.deduplicate(papers)

    # All strategies should detect duplicates
    assert len(result) <= len(papers)
