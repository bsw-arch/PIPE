#!/usr/bin/env python3
"""
Hybrid Retrieval Engine
Combines vector similarity (FAISS) and graph relationships (Neo4j)
for enhanced knowledge retrieval
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from vector_store import VectorStore
from graph_store import GraphStore

logger = logging.getLogger(__name__)


class HybridRetrieval:
    """
    Hybrid retrieval combining:
    1. Vector similarity search (semantic)
    2. Graph relationship traversal (structural)
    3. Score fusion and re-ranking
    """

    def __init__(
        self,
        vector_store: VectorStore,
        graph_store: GraphStore,
        vector_weight: float = 0.6,
        graph_weight: float = 0.4
    ):
        """
        Initialise hybrid retrieval

        Args:
            vector_store: Initialised vector store
            graph_store: Initialised graph store
            vector_weight: Weight for vector similarity scores (0-1)
            graph_weight: Weight for graph relationship scores (0-1)
        """
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight

        logger.info(
            f"Hybrid retrieval initialised: vector_weight={vector_weight}, "
            f"graph_weight={graph_weight}"
        )

    async def retrieve(
        self,
        query: str,
        domain: Optional[str] = None,
        top_k: int = 10,
        use_vector: bool = True,
        use_graph: bool = True,
        rerank: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval combining vector and graph search

        Args:
            query: User query
            domain: Optional domain filter
            top_k: Number of results to return
            use_vector: Enable vector similarity search
            use_graph: Enable graph relationship search
            rerank: Apply re-ranking to results

        Returns:
            List of retrieved knowledge entries with hybrid scores
        """
        start_time = datetime.utcnow()

        vector_results = []
        graph_results = []

        # Step 1: Vector similarity search
        if use_vector:
            try:
                vector_results = self.vector_store.search(
                    query=query,
                    top_k=top_k * 2  # Get more candidates for fusion
                )
                logger.info(f"Vector search returned {len(vector_results)} results")
            except Exception as e:
                logger.error(f"Vector search failed: {e}")

        # Step 2: Graph relationship search
        if use_graph:
            try:
                graph_results = await self.graph_store.semantic_search(
                    query=query,
                    domain=domain,
                    limit=top_k * 2
                )
                logger.info(f"Graph search returned {len(graph_results)} results")
            except Exception as e:
                logger.error(f"Graph search failed: {e}")

        # Step 3: Fuse results
        fused_results = self._fuse_results(
            vector_results=vector_results,
            graph_results=graph_results
        )

        # Step 4: Re-rank if enabled
        if rerank and len(fused_results) > 0:
            fused_results = self._rerank_results(
                query=query,
                results=fused_results
            )

        # Step 5: Return top_k results
        final_results = fused_results[:top_k]

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(
            f"Hybrid retrieval complete: {len(final_results)} results "
            f"in {processing_time:.2f}ms"
        )

        # Add retrieval metadata
        for result in final_results:
            result['retrieval_time_ms'] = processing_time
            result['retrieval_method'] = 'hybrid'

        return final_results

    def _fuse_results(
        self,
        vector_results: List[Dict[str, Any]],
        graph_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fuse vector and graph results using weighted scoring

        Uses Reciprocal Rank Fusion (RRF) combined with score weighting

        Args:
            vector_results: Results from vector search
            graph_results: Results from graph search

        Returns:
            Fused and deduplicated results
        """
        # Create lookup by content/name
        result_map: Dict[str, Dict[str, Any]] = {}

        # Process vector results
        for rank, result in enumerate(vector_results):
            key = self._get_result_key(result)
            rrf_score = 1.0 / (rank + 60)  # RRF with k=60

            if key not in result_map:
                result_map[key] = result.copy()
                result_map[key]['vector_score'] = result.get('score', 0.0)
                result_map[key]['vector_rank'] = rank
                result_map[key]['graph_score'] = 0.0
                result_map[key]['rrf_score'] = rrf_score * self.vector_weight
            else:
                result_map[key]['vector_score'] = max(
                    result_map[key].get('vector_score', 0.0),
                    result.get('score', 0.0)
                )
                result_map[key]['rrf_score'] += rrf_score * self.vector_weight

        # Process graph results
        for rank, result in enumerate(graph_results):
            key = self._get_result_key(result)
            rrf_score = 1.0 / (rank + 60)

            if key not in result_map:
                result_map[key] = result.copy()
                result_map[key]['vector_score'] = 0.0
                result_map[key]['graph_score'] = result.get('score', 0.0)
                result_map[key]['graph_rank'] = rank
                result_map[key]['rrf_score'] = rrf_score * self.graph_weight
            else:
                result_map[key]['graph_score'] = max(
                    result_map[key].get('graph_score', 0.0),
                    result.get('score', 0.0)
                )
                result_map[key]['rrf_score'] += rrf_score * self.graph_weight

        # Calculate final hybrid scores
        for key, result in result_map.items():
            vector_score = result.get('vector_score', 0.0)
            graph_score = result.get('graph_score', 0.0)
            rrf_score = result.get('rrf_score', 0.0)

            # Weighted combination: 70% RRF + 30% direct scores
            result['hybrid_score'] = (
                0.7 * rrf_score +
                0.3 * (vector_score * self.vector_weight + graph_score * self.graph_weight)
            )

        # Sort by hybrid score
        fused_results = sorted(
            result_map.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )

        return fused_results

    def _get_result_key(self, result: Dict[str, Any]) -> str:
        """
        Generate unique key for a result (for deduplication)

        Args:
            result: Result dictionary

        Returns:
            Unique key string
        """
        # Try multiple fields for key generation
        if 'content' in result:
            return result['content'][:100]  # First 100 chars of content
        elif 'name' in result:
            return result['name']
        elif 'text' in result:
            return result['text'][:100]
        else:
            return str(result)

    def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Re-rank results using query-specific features

        Simple re-ranking based on:
        - Query term overlap
        - Result diversity
        - Recency (if available)

        Args:
            query: Original query
            results: Results to re-rank

        Returns:
            Re-ranked results
        """
        query_terms = set(query.lower().split())

        for result in results:
            # Calculate query overlap bonus
            content = result.get('content', result.get('text', result.get('description', '')))
            content_terms = set(content.lower().split())
            overlap = len(query_terms & content_terms) / max(len(query_terms), 1)

            # Apply overlap bonus (up to +20% score)
            result['hybrid_score'] *= (1.0 + 0.2 * overlap)

            # Diversity bonus: prefer different sources
            source = result.get('source', 'unknown')
            if source == 'graph':
                result['hybrid_score'] *= 1.05  # 5% bonus for graph results
            elif source == 'vector':
                result['hybrid_score'] *= 1.02  # 2% bonus for vector results

        # Re-sort after re-ranking
        reranked_results = sorted(
            results,
            key=lambda x: x['hybrid_score'],
            reverse=True
        )

        return reranked_results

    async def retrieve_with_expansion(
        self,
        query: str,
        domain: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve with query expansion using graph relationships

        Steps:
        1. Initial retrieval
        2. Extract entities from top results
        3. Expand query with related entities
        4. Second retrieval pass
        5. Fuse and deduplicate

        Args:
            query: Original query
            domain: Optional domain filter
            top_k: Number of final results

        Returns:
            Enhanced retrieval results
        """
        # Step 1: Initial retrieval
        initial_results = await self.retrieve(
            query=query,
            domain=domain,
            top_k=5  # Fewer for expansion
        )

        if len(initial_results) == 0:
            return []

        # Step 2: Extract entities from top results
        entities = []
        for result in initial_results[:3]:  # Top 3 only
            if 'name' in result:
                entities.append(result['name'])

        # Step 3: Get related entities from graph
        expanded_entities = []
        for entity in entities[:2]:  # Limit expansion
            try:
                related = await self.graph_store.query_related_entities(
                    entity_name=entity,
                    max_depth=1,
                    limit=5
                )
                expanded_entities.extend([r['name'] for r in related])
            except Exception as e:
                logger.warning(f"Entity expansion failed for {entity}: {e}")

        # Step 4: Expanded query
        if expanded_entities:
            expanded_query = f"{query} {' '.join(expanded_entities[:3])}"
            logger.info(f"Expanded query: {expanded_query}")

            # Second retrieval pass
            expanded_results = await self.retrieve(
                query=expanded_query,
                domain=domain,
                top_k=top_k
            )

            # Merge with initial results
            all_results = initial_results + expanded_results

            # Deduplicate
            seen = set()
            final_results = []
            for result in all_results:
                key = self._get_result_key(result)
                if key not in seen:
                    seen.add(key)
                    final_results.append(result)

            return sorted(
                final_results,
                key=lambda x: x.get('hybrid_score', 0),
                reverse=True
            )[:top_k]
        else:
            return initial_results

    def update_weights(self, vector_weight: float, graph_weight: float):
        """
        Update fusion weights dynamically

        Args:
            vector_weight: New vector weight (0-1)
            graph_weight: New graph weight (0-1)
        """
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight
        logger.info(f"Updated weights: vector={vector_weight}, graph={graph_weight}")


if __name__ == "__main__":
    # Test hybrid retrieval
    import asyncio

    async def test():
        # Initialise stores
        vector_store = VectorStore()
        graph_store = GraphStore()
        await graph_store.initialise()

        # Initialise hybrid retrieval
        hybrid = HybridRetrieval(
            vector_store=vector_store,
            graph_store=graph_store
        )

        # Test query
        results = await hybrid.retrieve(
            query="How do I build a CAG+RAG system?",
            top_k=5
        )

        print(f"Retrieved {len(results)} results:")
        for i, result in enumerate(results):
            print(f"{i + 1}. Score: {result.get('hybrid_score', 0):.3f}")
            print(f"   Vector: {result.get('vector_score', 0):.3f}, "
                  f"Graph: {result.get('graph_score', 0):.3f}")

        await graph_store.close()

    asyncio.run(test())
