#!/usr/bin/env python3
"""
BSW-Arch RAG Layer - Hybrid Retrieval Engine
Performs hybrid search across vector, graph, and document stores
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import asyncio
import logging
import hashlib

logger = logging.getLogger(__name__)


class HybridRetrievalEngine:
    """
    Hybrid retrieval combining vector, graph, and document search

    Components:
    - Vector search: Semantic similarity using FAISS
    - Graph search: Relationship traversal using Neo4j
    - Document search: Full-text search using MongoDB
    - Fusion: Weighted combination of results
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Hybrid Retrieval Engine

        Args:
            config: Configuration dictionary with:
                - embedding_model: Name of embedding model
                - embedding_dimension: Dimension of embeddings
                - vector_top_k: Number of vector results
                - graph_top_k: Number of graph results
                - document_top_k: Number of document results
                - fusion_weights: Weights for each retrieval method
        """
        self.config = config or self._default_config()

        # Initialize components
        self.embedding_model = None
        self.vector_index = None
        self.graph_client = None
        self.document_client = None

        # Fusion weights
        self.fusion_weights = self.config.get('fusion_weights', {
            'vector': 0.4,
            'graph': 0.35,
            'document': 0.25
        })

        logger.info("Hybrid Retrieval Engine initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'embedding_model': 'all-MiniLM-L6-v2',
            'embedding_dimension': 384,
            'vector_top_k': 10,
            'graph_top_k': 10,
            'document_top_k': 10,
            'fusion_weights': {
                'vector': 0.4,
                'graph': 0.35,
                'document': 0.25
            }
        }

    def initialize_embedding_model(self):
        """Initialize sentence embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(
                self.config['embedding_model']
            )
            logger.info(f"Embedding model loaded: {self.config['embedding_model']}")
        except ImportError:
            logger.warning("sentence-transformers not available, using mock embeddings")
            self.embedding_model = None

    def initialize_vector_index(self, index_path: Optional[str] = None):
        """Initialize FAISS vector index"""
        try:
            import faiss
            dimension = self.config['embedding_dimension']

            if index_path:
                # Load existing index
                self.vector_index = faiss.read_index(index_path)
                logger.info(f"Loaded FAISS index from {index_path}")
            else:
                # Create new index
                self.vector_index = faiss.IndexFlatL2(dimension)
                logger.info(f"Created new FAISS index with dimension {dimension}")

        except ImportError:
            logger.warning("FAISS not available, vector search disabled")
            self.vector_index = None

    async def hybrid_search(self,
                           query: str,
                           domain: str,
                           top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform hybrid search across all retrieval methods

        Args:
            query: Search query
            domain: Target domain (AXIS, PIPE, ECO, IV)
            top_k: Number of results to return

        Returns:
            List of fused and ranked results
        """
        logger.info(f"Hybrid search for query: {query[:50]}... in domain {domain}")

        # Parallel retrieval from all sources
        tasks = []

        # Vector search
        if self.vector_index is not None:
            tasks.append(self._vector_search(query, domain, top_k * 2))
        else:
            tasks.append(self._mock_vector_search(query, domain, top_k * 2))

        # Graph search
        if self.graph_client is not None:
            tasks.append(self._graph_search(query, domain, top_k * 2))
        else:
            tasks.append(self._mock_graph_search(query, domain, top_k * 2))

        # Document search
        if self.document_client is not None:
            tasks.append(self._document_search(query, domain, top_k * 2))
        else:
            tasks.append(self._mock_document_search(query, domain, top_k * 2))

        # Execute all searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        vector_results = results[0] if not isinstance(results[0], Exception) else []
        graph_results = results[1] if not isinstance(results[1], Exception) else []
        document_results = results[2] if not isinstance(results[2], Exception) else []

        logger.info(
            f"Retrieved: {len(vector_results)} vector, "
            f"{len(graph_results)} graph, {len(document_results)} document results"
        )

        # Fuse results
        fused_results = await self._fuse_results(
            vector_results,
            graph_results,
            document_results
        )

        return fused_results[:top_k]

    async def _vector_search(self,
                           query: str,
                           domain: str,
                           top_k: int) -> List[Dict[str, Any]]:
        """Perform vector similarity search using FAISS"""
        if self.embedding_model is None or self.vector_index is None:
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])

        # Search in FAISS index
        distances, indices = self.vector_index.search(
            query_embedding.astype('float32'),
            top_k
        )

        # Convert to results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # Valid index
                score = float(1 / (1 + dist))  # Convert distance to similarity
                results.append({
                    'id': f"vector_{domain}_{idx}",
                    'score': score,
                    'type': 'vector',
                    'domain': domain,
                    'content': {
                        'text': f"Vector result {idx} for {domain}",
                        'index': int(idx)
                    },
                    'rank': i + 1
                })

        return results

    async def _mock_vector_search(self,
                                 query: str,
                                 domain: str,
                                 top_k: int) -> List[Dict[str, Any]]:
        """Mock vector search for testing without FAISS"""
        results = []
        for i in range(min(top_k, 5)):
            score = 0.9 - (i * 0.1)
            results.append({
                'id': f"vector_{domain}_{i}",
                'score': score,
                'type': 'vector',
                'domain': domain,
                'content': {
                    'text': f"Vector mock result {i} for query '{query}' in {domain}",
                    'index': i
                },
                'rank': i + 1
            })
        return results

    async def _graph_search(self,
                          query: str,
                          domain: str,
                          top_k: int) -> List[Dict[str, Any]]:
        """Perform graph traversal search using Neo4j"""
        # This would connect to Neo4j in production
        # For now, return mock results
        return await self._mock_graph_search(query, domain, top_k)

    async def _mock_graph_search(self,
                                query: str,
                                domain: str,
                                top_k: int) -> List[Dict[str, Any]]:
        """Mock graph search for testing without Neo4j"""
        results = []
        for i in range(min(top_k, 5)):
            score = 0.85 - (i * 0.1)
            results.append({
                'id': f"graph_{domain}_{i}",
                'score': score,
                'type': 'graph',
                'domain': domain,
                'content': {
                    'entity': {
                        'id': f"entity_{i}",
                        'name': f"Entity {i}",
                        'description': f"Graph entity for {query}"
                    },
                    'relations': [
                        {'type': 'RELATED_TO', 'node': f"entity_{i+1}"}
                    ]
                },
                'rank': i + 1
            })
        return results

    async def _document_search(self,
                              query: str,
                              domain: str,
                              top_k: int) -> List[Dict[str, Any]]:
        """Perform document full-text search using MongoDB"""
        # This would connect to MongoDB in production
        # For now, return mock results
        return await self._mock_document_search(query, domain, top_k)

    async def _mock_document_search(self,
                                   query: str,
                                   domain: str,
                                   top_k: int) -> List[Dict[str, Any]]:
        """Mock document search for testing without MongoDB"""
        results = []
        for i in range(min(top_k, 5)):
            score = 0.8 - (i * 0.1)
            results.append({
                'id': f"doc_{domain}_{i}",
                'score': score,
                'type': 'document',
                'domain': domain,
                'content': {
                    'title': f"Document {i} for {domain}",
                    'text': f"Full text content about {query} in {domain} domain",
                    'metadata': {
                        'source': f"doc_{i}.md",
                        'category': domain
                    }
                },
                'rank': i + 1
            })
        return results

    async def _fuse_results(self,
                          vector_results: List[Dict],
                          graph_results: List[Dict],
                          document_results: List[Dict]) -> List[Dict[str, Any]]:
        """
        Fuse results from multiple retrieval methods

        Uses weighted scoring to combine results from different sources.

        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search
            document_results: Results from document search

        Returns:
            Fused and ranked results
        """
        all_results = {}

        # Process vector results
        for result in vector_results:
            key = result['id']
            all_results[key] = result.copy()
            all_results[key]['final_score'] = (
                result['score'] * self.fusion_weights['vector']
            )
            all_results[key]['sources'] = ['vector']

        # Process graph results
        for result in graph_results:
            key = result['id']
            if key in all_results:
                # Combine scores
                all_results[key]['final_score'] += (
                    result['score'] * self.fusion_weights['graph']
                )
                all_results[key]['sources'].append('graph')
            else:
                all_results[key] = result.copy()
                all_results[key]['final_score'] = (
                    result['score'] * self.fusion_weights['graph']
                )
                all_results[key]['sources'] = ['graph']

        # Process document results
        for result in document_results:
            key = result['id']
            if key in all_results:
                # Combine scores
                all_results[key]['final_score'] += (
                    result['score'] * self.fusion_weights['document']
                )
                all_results[key]['sources'].append('document')
            else:
                all_results[key] = result.copy()
                all_results[key]['final_score'] = (
                    result['score'] * self.fusion_weights['document']
                )
                all_results[key]['sources'] = ['document']

        # Sort by final score
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )

        logger.info(f"Fused {len(sorted_results)} unique results")

        return sorted_results

    def update_fusion_weights(self, weights: Dict[str, float]):
        """
        Update fusion weights

        Args:
            weights: Dictionary with 'vector', 'graph', 'document' keys
        """
        # Validate weights sum to ~1.0
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Fusion weights sum to {total}, normalizing")
            weights = {k: v / total for k, v in weights.items()}

        self.fusion_weights = weights
        logger.info(f"Updated fusion weights: {weights}")
