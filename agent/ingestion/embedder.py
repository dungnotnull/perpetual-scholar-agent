"""Ingestion pipeline: embedding and priority scoring."""
from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

from agent.config.settings import settings

logger = logging.getLogger(__name__)

# Lazy-loaded embedding model (singleton)
_embedding_model = None


def _get_embedding_model():
    """Lazy-load the sentence-transformers embedding model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _embedding_model = SentenceTransformer(settings.embedding_model)
    return _embedding_model


def embed_text(text: str) -> np.ndarray:
    """Embed a single text string using the configured embedding model.

    Args:
        text: Text to embed.

    Returns:
        numpy float32 array of shape (embedding_dimension,).
    """
    model = _get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.astype(np.float32)


def embed_batch(texts: List[str]) -> np.ndarray:
    """Embed a batch of text strings.

    Args:
        texts: List of texts to embed.

    Returns:
        numpy float32 array of shape (len(texts), embedding_dimension).
    """
    model = _get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype(np.float32)


def compute_domain_focus_embedding(domain_focus: Optional[str] = None) -> np.ndarray:
    """Compute the embedding vector for the domain focus string.

    Args:
        domain_focus: Domain description. Defaults to settings.domain_focus.

    Returns:
        Normalized embedding vector of shape (embedding_dimension,).
    """
    text = domain_focus or settings.domain_focus
    return embed_text(text)


def compute_priority_score(
    item_embedding: np.ndarray,
    domain_embedding: np.ndarray,
) -> float:
    """Compute priority score as cosine similarity to domain focus.

    Since embeddings are already L2-normalized, cosine similarity = dot product.

    Args:
        item_embedding: Embedding of the ingested item.
        domain_embedding: Embedding of the domain focus string.

    Returns:
        Float between -1 and 1 (cosine similarity).
    """
    return float(np.dot(item_embedding, domain_embedding))


def score_items(items: list, domain_embedding: Optional[np.ndarray] = None) -> list:
    """Compute and assign priority scores to a list of items.

    Items are modified in-place: item.priority_score is set.

    Args:
        items: List of item objects with .title, .abstract or .description.
        domain_embedding: Pre-computed domain focus embedding. Computed if None.

    Returns:
        Same list, sorted by priority_score descending.
    """
    if domain_embedding is None:
        domain_embedding = compute_domain_focus_embedding()

    texts = []
    for item in items:
        # Build text from available fields
        text_parts = [item.title]
        if hasattr(item, "abstract") and item.abstract:
            text_parts.append(item.abstract)
        if hasattr(item, "description") and item.description:
            text_parts.append(item.description)
        texts.append(" ".join(text_parts))

    embeddings = embed_batch(texts)

    for i, item in enumerate(items):
        item.priority_score = compute_priority_score(embeddings[i], domain_embedding)

    # Sort by priority (highest first)
    items.sort(key=lambda x: x.priority_score, reverse=True)

    logger.info(
        f"Priority scoring: {len(items)} items, "
        f"top score = {items[0].priority_score:.4f}, "
        f"avg = {sum(i.priority_score for i in items) / len(items):.4f}"
    )
    return items
