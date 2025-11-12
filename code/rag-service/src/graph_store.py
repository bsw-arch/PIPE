#!/usr/bin/env python3
"""
Graph Store - Neo4j Knowledge Graph Integration
Provides relationship-based knowledge retrieval
"""

from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GraphStore:
    """
    Neo4j-based knowledge graph store
    Handles entity relationships and semantic connections
    """

    def __init__(
        self,
        uri: str = "bolt://neo4j:7687",
        user: str = "neo4j",
        password: str = "changeme"
    ):
        """
        Initialise graph store connection

        Args:
            uri: Neo4j connection URI
            user: Database username
            password: Database password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[AsyncDriver] = None

    async def initialise(self):
        """Initialise Neo4j connection"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )

            # Verify connectivity
            async with self.driver.session() as session:
                result = await session.run("RETURN 1")
                await result.single()

            logger.info("Graph store initialised successfully")

            # Create indexes for performance
            await self._create_indexes()

        except Exception as e:
            logger.error(f"Failed to initialise graph store: {e}")
            raise

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Graph store connection closed")

    async def _create_indexes(self):
        """Create necessary indexes for query performance"""
        indexes = [
            "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX document_id IF NOT EXISTS FOR (d:Document) ON (d.doc_id)",
            "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)",
        ]

        async with self.driver.session() as session:
            for index_query in indexes:
                try:
                    await session.run(index_query)
                except Exception as e:
                    logger.warning(f"Index creation skipped: {e}")

    async def query_related_entities(
        self,
        entity_name: str,
        max_depth: int = 2,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query entities related to a given entity

        Args:
            entity_name: Name of the entity to query
            max_depth: Maximum relationship depth to traverse
            limit: Maximum number of results

        Returns:
            List of related entities with relationships
        """
        query = f"""
        MATCH path = (e:Entity {{name: $entity_name}})-[r*1..{max_depth}]-(related:Entity)
        RETURN DISTINCT
            related.name as name,
            related.type as type,
            related.domain as domain,
            [rel in relationships(path) | type(rel)] as relationship_path,
            length(path) as distance,
            related.description as description
        ORDER BY distance ASC
        LIMIT $limit
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    entity_name=entity_name,
                    limit=limit
                )

                records = []
                async for record in result:
                    records.append({
                        'name': record['name'],
                        'type': record['type'],
                        'domain': record['domain'],
                        'relationship_path': record['relationship_path'],
                        'distance': record['distance'],
                        'description': record['description'],
                        'source': 'graph',
                        'score': 1.0 / (record['distance'] + 1)  # Closer = higher score
                    })

                logger.info(f"Found {len(records)} related entities for '{entity_name}'")
                return records

        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            return []

    async def query_by_concept(
        self,
        concept: str,
        domain: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query entities by concept or semantic meaning

        Args:
            concept: Concept to search for
            domain: Optional domain filter (PIPE, IV, AXIS, etc.)
            limit: Maximum results

        Returns:
            List of matching entities
        """
        query = """
        MATCH (c:Concept {name: $concept})-[:RELATES_TO]->(e:Entity)
        WHERE $domain IS NULL OR e.domain = $domain
        RETURN
            e.name as name,
            e.type as type,
            e.domain as domain,
            e.description as description,
            c.confidence as confidence
        ORDER BY confidence DESC
        LIMIT $limit
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    concept=concept,
                    domain=domain,
                    limit=limit
                )

                records = []
                async for record in result:
                    records.append({
                        'name': record['name'],
                        'type': record['type'],
                        'domain': record['domain'],
                        'description': record['description'],
                        'source': 'graph_concept',
                        'score': record['confidence'] if record['confidence'] else 0.7
                    })

                return records

        except Exception as e:
            logger.error(f"Concept query failed: {e}")
            return []

    async def semantic_search(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Semantic search combining entity and relationship information

        Args:
            query: Natural language query
            domain: Optional domain filter
            limit: Maximum results

        Returns:
            List of relevant knowledge entries
        """
        # Extract entities from query (simple approach - in production use NER)
        entities = self._extract_entities_simple(query)

        all_results = []

        # Query for each detected entity
        for entity in entities[:3]:  # Limit to top 3 entities
            related = await self.query_related_entities(
                entity_name=entity,
                max_depth=2,
                limit=limit
            )
            all_results.extend(related)

        # Deduplicate and sort by score
        seen = set()
        unique_results = []
        for result in sorted(all_results, key=lambda x: x['score'], reverse=True):
            key = (result['name'], result['type'])
            if key not in seen:
                seen.add(key)
                unique_results.append(result)

        return unique_results[:limit]

    def _extract_entities_simple(self, query: str) -> List[str]:
        """
        Simple entity extraction (capitalised words)
        In production, use spaCy or similar NER tool

        Args:
            query: Query text

        Returns:
            List of potential entity names
        """
        words = query.split()
        entities = []

        for word in words:
            # Simple heuristic: capitalised words might be entities
            if word[0].isupper() and len(word) > 2:
                entities.append(word.strip('.,!?;:'))

        return entities

    async def add_document_knowledge(
        self,
        doc_id: str,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ):
        """
        Add knowledge from a document to the graph

        Args:
            doc_id: Document identifier
            entities: List of entities with properties
            relationships: List of relationships between entities
        """
        async with self.driver.session() as session:
            # Create document node
            await session.run(
                """
                MERGE (d:Document {doc_id: $doc_id})
                SET d.indexed_at = datetime()
                """,
                doc_id=doc_id
            )

            # Create entity nodes
            for entity in entities:
                await session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    SET e.type = $type,
                        e.domain = $domain,
                        e.description = $description
                    MERGE (d:Document {doc_id: $doc_id})
                    MERGE (d)-[:CONTAINS]->(e)
                    """,
                    name=entity['name'],
                    type=entity.get('type', 'Unknown'),
                    domain=entity.get('domain', 'PIPE'),
                    description=entity.get('description', ''),
                    doc_id=doc_id
                )

            # Create relationships
            for rel in relationships:
                await session.run(
                    """
                    MATCH (e1:Entity {name: $from_entity})
                    MATCH (e2:Entity {name: $to_entity})
                    MERGE (e1)-[r:%s]->(e2)
                    SET r.confidence = $confidence,
                        r.source = $source
                    """ % rel['type'],
                    from_entity=rel['from'],
                    to_entity=rel['to'],
                    confidence=rel.get('confidence', 0.8),
                    source=doc_id
                )

        logger.info(f"Added {len(entities)} entities and {len(relationships)} relationships from {doc_id}")

    async def get_domain_statistics(self, domain: str) -> Dict[str, Any]:
        """
        Get statistics about knowledge in a specific domain

        Args:
            domain: Domain name (PIPE, IV, AXIS, etc.)

        Returns:
            Statistics dictionary
        """
        query = """
        MATCH (e:Entity {domain: $domain})
        OPTIONAL MATCH (e)-[r]-()
        RETURN
            count(DISTINCT e) as entity_count,
            count(DISTINCT r) as relationship_count,
            collect(DISTINCT e.type) as entity_types
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, domain=domain)
                record = await result.single()

                return {
                    'domain': domain,
                    'entity_count': record['entity_count'],
                    'relationship_count': record['relationship_count'],
                    'entity_types': record['entity_types'],
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Failed to get domain statistics: {e}")
            return {
                'domain': domain,
                'entity_count': 0,
                'relationship_count': 0,
                'entity_types': [],
                'error': str(e)
            }


if __name__ == "__main__":
    # Test graph store
    import asyncio

    async def test():
        store = GraphStore()
        await store.initialise()

        # Test query
        results = await store.query_related_entities("PIPE", max_depth=2, limit=5)
        print(f"Found {len(results)} related entities")

        for result in results:
            print(f"- {result['name']} ({result['type']}): distance={result['distance']}")

        await store.close()

    asyncio.run(test())
