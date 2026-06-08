"""perpetual-scholar-agent — FAISS vector index for lesson embedding storage and retrieval."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from agent.config.settings import settings


class FAISSLessonIndex:
    """Manages a FAISS flat L2 index for lesson embeddings.

    Each lesson stored in SQLite has an `embedding_id` that corresponds to
    its position in this FAISS index. This enables fast similarity search
    over verified techniques.
    """

    def __init__(self, dimension: int = None, index_dir: Optional[Path] = None):
        self.dimension = dimension or settings.embedding_dimension
        self.index_dir = index_dir or settings.data_dir
        self.index_path = self.index_dir / "lesson_index.faiss"
        self.id_map_path = self.index_dir / "lesson_id_map.json"
        self._index = None
        self._id_map: List[int] = []  # FAISS position → lesson DB id

    def _ensure_index(self):
        """Lazy-load or create the FAISS index."""
        if self._index is not None:
            return

        import faiss

        if self.index_path.exists():
            self._index = faiss.read_index(str(self.index_path))
            self._dimension = self._index.d
            # Reload id map
            if self.id_map_path.exists():
                import json
                with open(self.id_map_path) as f:
                    self._id_map = json.load(f)
        else:
            self._index = faiss.IndexFlatL2(self.dimension)
            self._id_map = []

    def add(
        self,
        embedding: np.ndarray,
        lesson_db_id: int,
    ) -> int:
        """Add a single lesson embedding to the index.

        Args:
            embedding: 1-D float32 array of shape (dimension,).
            lesson_db_id: The `id` from the `lessons` SQLite table.

        Returns:
            The FAISS internal position (also stored as `embedding_id` in SQLite).
        """
        self._ensure_index()

        if embedding.ndim != 1:
            raise ValueError(f"Expected 1-D embedding, got shape {embedding.shape}")
        if embedding.shape[0] != self.dimension:
            raise ValueError(
                f"Expected dimension {self.dimension}, got {embedding.shape[0]}"
            )

        vector = embedding.astype(np.float32).reshape(1, -1)
        position = self._index.ntotal
        self._index.add(vector)
        self._id_map.append(lesson_db_id)
        return position

    def add_batch(
        self,
        embeddings: np.ndarray,
        lesson_db_ids: List[int],
    ) -> List[int]:
        """Add a batch of lesson embeddings to the index.

        Args:
            embeddings: 2-D float32 array of shape (n, dimension).
            lesson_db_ids: List of lesson database IDs.

        Returns:
            List of FAISS positions.
        """
        self._ensure_index()

        if embeddings.ndim != 2:
            raise ValueError(f"Expected 2-D array, got shape {embeddings.shape}")
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Expected dimension {self.dimension}, got {embeddings.shape[1]}"
            )
        if embeddings.shape[0] != len(lesson_db_ids):
            raise ValueError(
                f"Mismatch: {embeddings.shape[0]} embeddings vs {len(lesson_db_ids)} IDs"
            )

        start_pos = self._index.ntotal
        vectors = embeddings.astype(np.float32)
        self._index.add(vectors)
        self._id_map.extend(lesson_db_ids)
        return list(range(start_pos, start_pos + len(lesson_db_ids)))

    def search(
        self,
        query: np.ndarray,
        top_k: int = 5,
    ) -> List[Tuple[int, float]]:
        """Search for the most similar lessons.

        Args:
            query: 1-D float32 embedding array of shape (dimension,).
            top_k: Number of nearest neighbors to return.

        Returns:
            List of (lesson_db_id, distance) tuples sorted by similarity.
        """
        self._ensure_index()

        if self._index.ntotal == 0:
            return []

        if query.ndim != 1:
            raise ValueError(f"Expected 1-D query, got shape {query.shape}")

        vector = query.astype(np.float32).reshape(1, -1)
        distances, indices = self._index.search(vector, min(top_k, self._index.ntotal))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self._id_map):
                continue
            lesson_db_id = self._id_map[idx]
            results.append((lesson_db_id, float(dist)))
        return results

    def save(self) -> None:
        """Persist the FAISS index and id map to disk."""
        self._ensure_index()
        self.index_dir.mkdir(parents=True, exist_ok=True)

        import faiss
        faiss.write_index(self._index, str(self.index_path))

        import json
        with open(self.id_map_path, "w") as f:
            json.dump(self._id_map, f)

    def __len__(self) -> int:
        self._ensure_index()
        return self._index.ntotal

    @property
    def total_vectors(self) -> int:
        self._ensure_index()
        return self._index.ntotal


def init_faiss_index(dimension: Optional[int] = None, index_dir: Optional[Path] = None) -> FAISSLessonIndex:
    """Create and initialize a new FAISS index (or load existing).

    Args:
        dimension: Embedding dimension. Defaults to settings.embedding_dimension.
        index_dir: Directory for persisting the index. Defaults to settings.data_dir.

    Returns:
        Initialized FAISSLessonIndex instance.
    """
    index = FAISSLessonIndex(dimension=dimension, index_dir=index_dir)
    index._ensure_index()
    return index


if __name__ == "__main__":
    # Quick smoke test: initialize, add a dummy vector, search, save, reload
    print("Initializing FAISS index...")
    idx = init_faiss_index(dimension=384)

    print(f"Index size before add: {idx.total_vectors}")

    dummy_embedding = np.random.randn(384).astype(np.float32)
    pos = idx.add(dummy_embedding, lesson_db_id=1)
    print(f"Added embedding at position {pos}")

    results = idx.search(dummy_embedding, top_k=1)
    print(f"Search results: {results}")

    idx.save()
    print(f"Index saved. Total vectors: {idx.total_vectors}")

    # Reload
    idx2 = init_faiss_index(dimension=384)
    print(f"Reloaded index size: {idx2.total_vectors}")
    results2 = idx2.search(dummy_embedding, top_k=1)
    print(f"Search after reload: {results2}")
