"""Cognee AI Memory client for PIPE governance and integration intelligence.

Cognee organizes PIPE's governance data into AI memory using a three-store architecture:
- Relational store: Tracks documents, chunks, and provenance
- Vector store: Semantic embeddings for similarity search
- Graph store: Entity and relationship knowledge graph

This enables:
- Semantic search across integration history
- Graph navigation of domain relationships
- Learning from past governance decisions
- Contextual memory for compliance tracking
"""

import logging
import os
from typing import Dict, Any, Optional, List
from enum import Enum

try:
    import cognee
    from cognee import add, cognify, search
    from cognee.modules.data.operations import add_data_points
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    logging.warning("Cognee not installed. Install with: pip install cognee")


class SearchMode(Enum):
    """Cognee search modes."""
    CHUNKS = "chunks"  # Raw chunks with similarity
    INSIGHTS = "insights"  # Generated insights from graph
    DEFAULT = "default"  # Hybrid search


class CogneeClient:
    """
    Client for Cognee AI memory integration with PIPE.

    Provides semantic search, knowledge graph navigation, and AI memory
    for governance decisions, integration patterns, and compliance tracking.
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        vector_db_provider: str = "lancedb",
        graph_db_provider: str = "networkx",
    ):
        """
        Initialize Cognee client.

        Args:
            llm_provider: LLM provider (openai, anthropic, etc.)
            llm_model: Model name (gpt-4, claude-3-opus, etc.)
            vector_db_provider: Vector store (lancedb, qdrant, weaviate)
            graph_db_provider: Graph store (networkx, neo4j, falkordb)
        """
        if not COGNEE_AVAILABLE:
            raise ImportError(
                "Cognee is not installed. Install with: pip install cognee"
            )

        self.logger = logging.getLogger("pipe.integrations.cognee")

        # Configure Cognee
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.vector_db_provider = vector_db_provider
        self.graph_db_provider = graph_db_provider

        self._configured = False

    async def configure(self) -> bool:
        """
        Configure Cognee with PIPE settings.

        Returns:
            True if configuration successful
        """
        try:
            # Set LLM configuration
            os.environ["LLM_PROVIDER"] = self.llm_provider
            os.environ["LLM_MODEL"] = self.llm_model

            # Set vector DB configuration
            os.environ["VECTOR_DB_PROVIDER"] = self.vector_db_provider

            # Set graph DB configuration
            os.environ["GRAPH_DB_PROVIDER"] = self.graph_db_provider

            self._configured = True
            self.logger.info("Cognee configured successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to configure Cognee: {str(e)}")
            return False

    async def add_governance_data(self, data: Any) -> bool:
        """
        Add governance data to Cognee memory.

        This is the first step in building AI memory. Data is prepared
        for cognification (chunking, embedding, graph extraction).

        Args:
            data: Governance data (text, dict, DataPoint, etc.)

        Returns:
            True if data added successfully
        """
        if not self._configured:
            await self.configure()

        try:
            await add(data)
            self.logger.info("Governance data added to Cognee")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add governance data: {str(e)}")
            return False

    async def cognify_governance_data(self) -> bool:
        """
        Build knowledge graph from governance data.

        This processes added data:
        1. Splits into chunks
        2. Extracts entities and relationships
        3. Creates embeddings
        4. Builds queryable knowledge graph

        Returns:
            True if cognification successful
        """
        if not self._configured:
            await self.configure()

        try:
            await cognify()
            self.logger.info("Governance data cognified successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to cognify governance data: {str(e)}")
            return False

    async def search_integrations(
        self,
        query: str,
        search_mode: SearchMode = SearchMode.DEFAULT,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for integrations using semantic search + graph.

        Args:
            query: Search query (e.g., "integrations similar to BNI-PIPE")
            search_mode: Search mode (chunks, insights, default)
            limit: Maximum results to return

        Returns:
            List of search results with context
        """
        if not self._configured:
            await self.configure()

        try:
            results = await search(
                query,
                search_type=search_mode.value,
            )

            self.logger.info(f"Found {len(results)} results for: {query}")
            return results[:limit]

        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return []

    async def find_similar_compliance_issues(
        self, issue_description: str, domain: str = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find compliance issues similar to the given description.

        Uses vector similarity to find conceptually related issues.

        Args:
            issue_description: Description of the compliance issue
            domain: Optional domain filter
            limit: Maximum results

        Returns:
            List of similar compliance issues with context
        """
        query = f"compliance issues similar to: {issue_description}"
        if domain:
            query += f" in domain {domain}"

        return await self.search_integrations(
            query, search_mode=SearchMode.INSIGHTS, limit=limit
        )

    async def find_integration_patterns(
        self, pattern_description: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find integration patterns matching description.

        Args:
            pattern_description: What kind of pattern to find
            limit: Maximum results

        Returns:
            List of matching integration patterns
        """
        query = f"integration patterns: {pattern_description}"
        return await self.search_integrations(
            query, search_mode=SearchMode.INSIGHTS, limit=limit
        )

    async def get_domain_context(self, domain_code: str) -> Dict[str, Any]:
        """
        Get comprehensive context about a domain.

        Uses graph traversal to gather all related information:
        - Domain capabilities
        - Active integrations
        - Compliance history
        - Review decisions

        Args:
            domain_code: Domain code (BNI, BNP, etc.)

        Returns:
            Dictionary with domain context
        """
        query = f"everything about domain {domain_code}"
        results = await self.search_integrations(
            query, search_mode=SearchMode.INSIGHTS, limit=20
        )

        return {
            "domain": domain_code,
            "context": results,
            "total_items": len(results),
        }

    async def add_datapoints(self, datapoints: List[Any]) -> bool:
        """
        Add structured DataPoints to Cognee.

        DataPoints are automatically:
        - Embedded based on index_fields
        - Converted to graph nodes and edges
        - Stored with provenance

        Args:
            datapoints: List of DataPoint objects

        Returns:
            True if added successfully
        """
        if not self._configured:
            await self.configure()

        try:
            await add_data_points(datapoints)
            self.logger.info(f"Added {len(datapoints)} DataPoints to Cognee")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add DataPoints: {str(e)}")
            return False

    async def learn_from_review_decision(
        self, review_id: str, decision: str, rationale: str
    ) -> bool:
        """
        Learn from a review decision.

        Adds the decision to AI memory so future similar cases
        can reference this precedent.

        Args:
            review_id: Review identifier
            decision: Decision made (approved, rejected, etc.)
            rationale: Reasoning behind decision

        Returns:
            True if learned successfully
        """
        decision_data = {
            "type": "review_decision",
            "review_id": review_id,
            "decision": decision,
            "rationale": rationale,
        }

        return await self.add_governance_data(decision_data)

    async def suggest_integration_path(
        self, source_domain: str, target_domain: str
    ) -> Dict[str, Any]:
        """
        Suggest optimal integration path based on learned patterns.

        Uses AI memory to find successful integration patterns
        between similar domains.

        Args:
            source_domain: Source domain code
            target_domain: Target domain code

        Returns:
            Suggested integration approach with reasoning
        """
        query = f"successful integration patterns from {source_domain} to {target_domain}"
        results = await self.search_integrations(
            query, search_mode=SearchMode.INSIGHTS, limit=5
        )

        return {
            "source": source_domain,
            "target": target_domain,
            "suggested_patterns": results,
            "confidence": len(results) / 5.0,  # Simple confidence score
        }

    async def reset_memory(self) -> bool:
        """
        Reset Cognee memory (for testing/development).

        WARNING: This deletes all stored data!

        Returns:
            True if reset successful
        """
        try:
            await cognee.prune.prune_data()
            await cognee.prune.prune_system()
            self.logger.warning("Cognee memory reset completed")
            return True

        except Exception as e:
            self.logger.error(f"Failed to reset memory: {str(e)}")
            return False

    async def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about AI memory.

        Returns:
            Memory statistics
        """
        # Note: This is a placeholder - actual implementation depends on
        # Cognee's internal APIs which may vary
        return {
            "status": "configured" if self._configured else "not_configured",
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "vector_db": self.vector_db_provider,
            "graph_db": self.graph_db_provider,
        }


# Singleton instance
_cognee_client: Optional[CogneeClient] = None


async def get_cognee_client(
    llm_provider: str = None,
    llm_model: str = None,
    vector_db_provider: str = None,
    graph_db_provider: str = None,
) -> CogneeClient:
    """
    Get or create Cognee client singleton.

    Args:
        llm_provider: LLM provider (default: from env or "openai")
        llm_model: Model name (default: from env or "gpt-4")
        vector_db_provider: Vector store (default: "lancedb")
        graph_db_provider: Graph store (default: "networkx")

    Returns:
        Cognee client instance
    """
    global _cognee_client

    if _cognee_client is None:
        _cognee_client = CogneeClient(
            llm_provider=llm_provider or os.getenv("LLM_PROVIDER", "openai"),
            llm_model=llm_model or os.getenv("LLM_MODEL", "gpt-4"),
            vector_db_provider=vector_db_provider or os.getenv("VECTOR_DB_PROVIDER", "lancedb"),
            graph_db_provider=graph_db_provider or os.getenv("GRAPH_DB_PROVIDER", "networkx"),
        )
        await _cognee_client.configure()

    return _cognee_client
