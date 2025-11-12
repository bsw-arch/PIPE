"""
Vector Store - FAISS-based vector similarity search
Uses Hugging Face embeddings
"""

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import pickle
import os
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for similarity search"""

    def __init__(self,
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 dimension: int = 384,
                 index_type: str = "L2"):
        """
        Initialise vector store

        Args:
            model_name: HuggingFace embedding model
            dimension: Embedding dimension
            index_type: FAISS index type ('L2' or 'IP' for inner product)
        """
        self.model_name = model_name
        self.dimension = dimension
        self.index_type = index_type

        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        self.id_counter = 0

    async def initialise(self):
        """Initialise embedding model and FAISS index"""
        logger.info(f"Initialising Vector Store with {self.model_name}")

        # Load embedding model
        self.model = SentenceTransformer(self.model_name)
        self.model.eval()

        # Create FAISS index
        if self.index_type == "L2":
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "IP":
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

        logger.info(f"✓ Vector Store initialised (dimension={self.dimension})")

    def add_documents(self,
                     documents: List[Dict[str, Any]],
                     batch_size: int = 32):
        """
        Add documents to vector store

        Args:
            documents: List of documents with 'text' field
            batch_size: Batch size for embedding generation
        """
        if not documents:
            return

        texts = [doc.get('text', str(doc)) for doc in documents]

        logger.info(f"Adding {len(texts)} documents to vector store")

        # Generate embeddings in batches
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            embeddings = self.model.encode(
                batch_texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            all_embeddings.append(embeddings)

        # Concatenate batches
        embeddings_array = np.vstack(all_embeddings).astype('float32')

        # Normalise for cosine similarity (if using IP index)
        if self.index_type == "IP":
            faiss.normalize_L2(embeddings_array)

        # Add to FAISS index
        self.index.add(embeddings_array)

        # Store metadata
        for doc in documents:
            doc_with_id = doc.copy()
            doc_with_id['_id'] = self.id_counter
            self.metadata.append(doc_with_id)
            self.id_counter += 1

        logger.info(f"✓ Added {len(documents)} documents (total: {self.index.ntotal})")

    def search(self,
              query: str,
              top_k: int = 10,
              min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar documents

        Args:
            query: Search query
            top_k: Number of results to return
            min_score: Minimum similarity score

        Returns:
            List of documents with scores
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []

        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        query_embedding = query_embedding.astype('float32')

        # Normalise for cosine similarity
        if self.index_type == "IP":
            faiss.normalize_L2(query_embedding)

        # Search
        distances, indices = self.index.search(query_embedding, top_k)

        # Build results
        results = []

        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0 or idx >= len(self.metadata):
                continue

            # Convert distance to similarity score
            if self.index_type == "L2":
                score = float(1.0 / (1.0 + dist))
            else:  # IP (cosine similarity)
                score = float(dist)

            if score < min_score:
                continue

            result = self.metadata[idx].copy()
            result['score'] = score
            result['rank'] = i + 1
            result['type'] = 'vector'

            results.append(result)

        logger.debug(f"Found {len(results)} results for query")

        return results

    def batch_search(self,
                    queries: List[str],
                    top_k: int = 10) -> List[List[Dict[str, Any]]]:
        """Search multiple queries in batch"""
        if self.index.ntotal == 0:
            return [[] for _ in queries]

        # Generate query embeddings
        query_embeddings = self.model.encode(queries, convert_to_numpy=True)
        query_embeddings = query_embeddings.astype('float32')

        if self.index_type == "IP":
            faiss.normalize_L2(query_embeddings)

        # Batch search
        distances, indices = self.index.search(query_embeddings, top_k)

        # Build results for each query
        all_results = []

        for query_idx in range(len(queries)):
            query_results = []

            for i, (dist, idx) in enumerate(
                zip(distances[query_idx], indices[query_idx])
            ):
                if idx < 0 or idx >= len(self.metadata):
                    continue

                if self.index_type == "L2":
                    score = float(1.0 / (1.0 + dist))
                else:
                    score = float(dist)

                result = self.metadata[idx].copy()
                result['score'] = score
                result['rank'] = i + 1
                result['type'] = 'vector'

                query_results.append(result)

            all_results.append(query_results)

        return all_results

    def save(self, path: str):
        """Save index and metadata to disk"""
        os.makedirs(path, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))

        # Save metadata
        with open(os.path.join(path, "metadata.pkl"), 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'id_counter': self.id_counter,
                'dimension': self.dimension,
                'index_type': self.index_type,
                'model_name': self.model_name
            }, f)

        logger.info(f"✓ Vector store saved to {path}")

    def load(self, path: str):
        """Load index and metadata from disk"""
        # Load FAISS index
        self.index = faiss.read_index(os.path.join(path, "index.faiss"))

        # Load metadata
        with open(os.path.join(path, "metadata.pkl"), 'rb') as f:
            data = pickle.load(f)
            self.metadata = data['metadata']
            self.id_counter = data['id_counter']
            self.dimension = data['dimension']
            self.index_type = data['index_type']
            self.model_name = data['model_name']

        # Load model
        self.model = SentenceTransformer(self.model_name)
        self.model.eval()

        logger.info(
            f"✓ Vector store loaded from {path} "
            f"({self.index.ntotal} documents)"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_documents': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'model': self.model_name,
            'memory_usage_mb': self.index.sa_code_size() / 1024 / 1024
            if self.index else 0
        }
