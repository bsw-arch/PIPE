#!/usr/bin/env python3
"""
BSW-Arch RAG Layer - Knowledge Fusion Engine
Fuses knowledge from multiple sources for response generation
"""

from typing import List, Dict, Any, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)


class KnowledgeFusionEngine:
    """
    Fuses knowledge from multiple sources for augmented generation

    Responsibilities:
    - Extract and deduplicate content
    - Rank by relevance
    - Validate knowledge
    - Build knowledge graphs
    - Calculate confidence scores
    """

    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize Knowledge Fusion Engine

        Args:
            confidence_threshold: Minimum confidence for knowledge inclusion
        """
        self.confidence_threshold = confidence_threshold
        logger.info("Knowledge Fusion Engine initialized")

    async def fuse_knowledge(self,
                           retrieval_results: List[Dict[str, Any]],
                           query: str,
                           context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Fuse retrieved knowledge for response generation

        Args:
            retrieval_results: Results from hybrid retrieval
            query: Original user query
            context: Optional user context

        Returns:
            Dictionary with:
            - primary_knowledge: Top knowledge pieces
            - supporting_knowledge: Additional context
            - knowledge_graph: Relationship map
            - confidence_scores: Confidence per piece
            - source_attribution: Source metadata
        """
        logger.info(f"Fusing knowledge from {len(retrieval_results)} results")

        # Extract and deduplicate content
        knowledge_pieces = await self._extract_knowledge(retrieval_results)

        # Rank by relevance
        ranked_knowledge = await self._rank_knowledge(knowledge_pieces, query)

        # Validate and filter
        validated_knowledge = await self._validate_knowledge(
            ranked_knowledge,
            context
        )

        # Build knowledge graph
        knowledge_graph = await self._build_knowledge_graph(validated_knowledge)

        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(validated_knowledge)

        # Source attribution
        source_attribution = self._attribute_sources(retrieval_results)

        result = {
            'primary_knowledge': validated_knowledge[:5],
            'supporting_knowledge': validated_knowledge[5:10],
            'knowledge_graph': knowledge_graph,
            'confidence_scores': confidence_scores,
            'source_attribution': source_attribution,
            'total_pieces': len(validated_knowledge)
        }

        logger.info(
            f"Fused knowledge: {len(result['primary_knowledge'])} primary, "
            f"{len(result['supporting_knowledge'])} supporting"
        )

        return result

    async def _extract_knowledge(self,
                                results: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract unique knowledge pieces from results

        Args:
            results: Retrieval results

        Returns:
            List of unique knowledge pieces
        """
        knowledge_map = {}

        for result in results:
            content = result.get('content', {})
            result_type = result.get('type', 'unknown')

            # Extract based on result type
            if result_type == 'vector':
                text = content.get('text', '')
                if not text:
                    continue

                key = hashlib.md5(text.encode()).hexdigest()[:12]
                knowledge_map[key] = {
                    'text': text,
                    'type': 'vector',
                    'source': result.get('id'),
                    'score': result.get('final_score', result.get('score', 0)),
                    'domain': result.get('domain'),
                    'sources': result.get('sources', ['vector'])
                }

            elif result_type == 'graph':
                entity = content.get('entity', {})
                relations = content.get('relations', [])

                key = f"graph_{entity.get('id', '')}"
                knowledge_map[key] = {
                    'entity': entity,
                    'relations': relations,
                    'type': 'graph',
                    'source': result.get('id'),
                    'score': result.get('final_score', result.get('score', 0)),
                    'domain': result.get('domain'),
                    'sources': result.get('sources', ['graph'])
                }

            elif result_type == 'document':
                text = content.get('text', '')
                title = content.get('title', '')

                if not text:
                    continue

                key = hashlib.md5(text.encode()).hexdigest()[:12]
                knowledge_map[key] = {
                    'text': text,
                    'title': title,
                    'type': 'document',
                    'source': result.get('id'),
                    'score': result.get('final_score', result.get('score', 0)),
                    'domain': result.get('domain'),
                    'metadata': content.get('metadata', {}),
                    'sources': result.get('sources', ['document'])
                }

        logger.debug(f"Extracted {len(knowledge_map)} unique knowledge pieces")

        return list(knowledge_map.values())

    async def _rank_knowledge(self,
                            knowledge_pieces: List[Dict],
                            query: str) -> List[Dict]:
        """
        Rank knowledge pieces by relevance to query

        Args:
            knowledge_pieces: Extracted knowledge
            query: User query

        Returns:
            Ranked knowledge pieces
        """
        # Simple ranking by existing score
        # In production, would use TF-IDF or more sophisticated methods

        for piece in knowledge_pieces:
            # Add query relevance boost
            text_to_check = ""

            if piece['type'] in ['vector', 'document']:
                text_to_check = piece.get('text', '').lower()
            elif piece['type'] == 'graph':
                entity = piece.get('entity', {})
                text_to_check = entity.get('description', '').lower()

            # Simple keyword matching for relevance boost
            query_words = set(query.lower().split())
            content_words = set(text_to_check.split())
            overlap = len(query_words & content_words)

            if overlap > 0:
                boost = min(0.2, overlap * 0.05)
                piece['score'] = piece.get('score', 0) + boost

            # Add combined score
            piece['relevance_score'] = piece['score']

        # Sort by relevance
        ranked = sorted(
            knowledge_pieces,
            key=lambda x: x.get('relevance_score', 0),
            reverse=True
        )

        logger.debug(f"Ranked {len(ranked)} knowledge pieces")

        return ranked

    async def _validate_knowledge(self,
                                 knowledge_pieces: List[Dict],
                                 context: Optional[Any]) -> List[Dict]:
        """
        Validate and filter knowledge pieces

        Args:
            knowledge_pieces: Ranked knowledge
            context: User context for validation

        Returns:
            Validated knowledge pieces
        """
        validated = []

        for piece in knowledge_pieces:
            # Check confidence threshold
            if piece.get('relevance_score', 0) < self.confidence_threshold:
                logger.debug(
                    f"Filtered piece with score {piece.get('relevance_score', 0)}"
                )
                continue

            # Check for minimum content
            if piece['type'] in ['vector', 'document']:
                if len(piece.get('text', '')) < 10:
                    continue

            # Validate domain relevance
            if context and hasattr(context, 'domain_preferences'):
                piece_domain = piece.get('domain')
                if piece_domain not in context.domain_preferences[:5]:
                    # Reduce score for non-preferred domains
                    piece['relevance_score'] *= 0.8

            validated.append(piece)

        logger.info(
            f"Validated {len(validated)} of {len(knowledge_pieces)} pieces "
            f"(threshold: {self.confidence_threshold})"
        )

        return validated

    async def _build_knowledge_graph(self,
                                    knowledge_pieces: List[Dict]) -> Dict[str, Any]:
        """
        Build knowledge graph from pieces

        Args:
            knowledge_pieces: Validated knowledge

        Returns:
            Knowledge graph structure
        """
        graph = {
            'nodes': [],
            'edges': [],
            'domains': {}
        }

        # Extract nodes
        for i, piece in enumerate(knowledge_pieces):
            node = {
                'id': f"node_{i}",
                'type': piece['type'],
                'domain': piece.get('domain'),
                'score': piece.get('relevance_score', 0),
                'sources': piece.get('sources', [])
            }

            # Add content summary
            if piece['type'] in ['vector', 'document']:
                text = piece.get('text', '')
                node['summary'] = text[:100] + '...' if len(text) > 100 else text
            elif piece['type'] == 'graph':
                entity = piece.get('entity', {})
                node['summary'] = entity.get('name', '')

            graph['nodes'].append(node)

            # Track domains
            domain = piece.get('domain')
            if domain:
                if domain not in graph['domains']:
                    graph['domains'][domain] = 0
                graph['domains'][domain] += 1

        # Extract edges from graph pieces
        for i, piece in enumerate(knowledge_pieces):
            if piece['type'] == 'graph':
                relations = piece.get('relations', [])
                for relation in relations:
                    graph['edges'].append({
                        'from': f"node_{i}",
                        'to': relation.get('node', ''),
                        'type': relation.get('type', 'RELATED')
                    })

        logger.debug(
            f"Built knowledge graph: {len(graph['nodes'])} nodes, "
            f"{len(graph['edges'])} edges"
        )

        return graph

    def _calculate_confidence_scores(self,
                                    knowledge_pieces: List[Dict]) -> Dict[str, float]:
        """
        Calculate confidence scores for each piece

        Args:
            knowledge_pieces: Validated knowledge

        Returns:
            Dictionary of piece ID to confidence score
        """
        scores = {}

        for piece in knowledge_pieces:
            piece_id = piece.get('source', f"piece_{id(piece)}")
            score = piece.get('relevance_score', 0)

            # Adjust based on source diversity
            sources = piece.get('sources', [])
            if len(sources) > 1:
                score *= 1.1  # Boost for multi-source agreement

            # Normalize to 0-1
            scores[piece_id] = min(1.0, max(0.0, score))

        return scores

    def _attribute_sources(self,
                         retrieval_results: List[Dict]) -> List[Dict[str, Any]]:
        """
        Create source attribution list

        Args:
            retrieval_results: Original retrieval results

        Returns:
            List of source attributions
        """
        sources = []
        seen_sources = set()

        for result in retrieval_results:
            source_id = result.get('id')
            if source_id in seen_sources:
                continue

            seen_sources.add(source_id)
            sources.append({
                'id': source_id,
                'type': result.get('type'),
                'domain': result.get('domain'),
                'score': result.get('final_score', result.get('score', 0)),
                'sources': result.get('sources', [result.get('type')])
            })

        # Sort by score
        sources.sort(key=lambda x: x['score'], reverse=True)

        return sources[:10]  # Top 10 sources

    def set_confidence_threshold(self, threshold: float):
        """
        Update confidence threshold

        Args:
            threshold: New threshold (0-1)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")

        self.confidence_threshold = threshold
        logger.info(f"Updated confidence threshold to {threshold}")
