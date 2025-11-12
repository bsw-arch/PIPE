#!/usr/bin/env python3
"""
BSW-Arch CAG Layer - Query Classifier
Classifies queries for appropriate routing to bot domains
"""

from enum import Enum
from typing import List, Tuple, Optional, Dict
import re
import logging

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query classification types"""
    ANALYTICAL = "analytical"
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    GENERATIVE = "generative"


class QueryClassifier:
    """
    Classifies queries for appropriate routing

    Responsibilities:
    - Query type classification
    - Domain detection
    - Intent extraction
    """

    def __init__(self, model_name: str = "bert-base-uncased", use_transformers: bool = False):
        """
        Initialize Query Classifier

        Args:
            model_name: Name of NLP model to use
            use_transformers: Whether to use transformers library (requires installation)
        """
        self.use_transformers = use_transformers
        self.model_name = model_name
        self.classifier = None

        # Initialize transformer if available
        if use_transformers:
            try:
                from transformers import pipeline
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model=model_name
                )
                logger.info(f"Query classifier initialized with {model_name}")
            except ImportError:
                logger.warning(
                    "Transformers not available, falling back to rule-based classification"
                )
                self.use_transformers = False

        # Initialize domain patterns
        self.domain_patterns = self._initialize_patterns()

        # Initialize query type patterns
        self.query_type_patterns = self._initialize_query_type_patterns()

    def _initialize_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialize regex patterns for domain detection"""
        return {
            'AXIS': [
                re.compile(r'\b(architecture|design\s+pattern|blueprint|diagram)\b', re.I),
                re.compile(r'\b(enterprise|system\s+design|component)\b', re.I),
                re.compile(r'\b(togaf|archimate|zachman)\b', re.I),
            ],
            'PIPE': [
                re.compile(r'\b(api|integration|pipeline|ci/cd)\b', re.I),
                re.compile(r'\b(deployment|build|release|automation)\b', re.I),
                re.compile(r'\b(webhook|rest|graphql|grpc)\b', re.I),
            ],
            'ECO': [
                re.compile(r'\b(infrastructure|resource|monitoring|optimization)\b', re.I),
                re.compile(r'\b(kubernetes|container|docker|helm)\b', re.I),
                re.compile(r'\b(prometheus|grafana|metrics|alerting)\b', re.I),
                re.compile(r'\b(opentofu|openbao|iac)\b', re.I),
            ],
            'IV': [
                re.compile(r'\b(ai|ml|llm|rag|cag)\b', re.I),
                re.compile(r'\b(machine\s+learning|neural\s+network|model)\b', re.I),
                re.compile(r'\b(training|inference|embedding|vector)\b', re.I),
                re.compile(r'\b(validation|testing|quality)\b', re.I),
            ]
        }

    def _initialize_query_type_patterns(self) -> Dict[QueryType, List[re.Pattern]]:
        """Initialize patterns for query type classification"""
        return {
            QueryType.ANALYTICAL: [
                re.compile(r'\b(analyze|compare|evaluate|assess)\b', re.I),
                re.compile(r'\b(why|how\s+(does|do|can|should))\b', re.I),
                re.compile(r'\b(trend|pattern|insight|correlation)\b', re.I),
            ],
            QueryType.TRANSACTIONAL: [
                re.compile(r'\b(create|delete|update|modify|change)\b', re.I),
                re.compile(r'\b(deploy|start|stop|restart|scale)\b', re.I),
                re.compile(r'\b(send|execute|run|process)\b', re.I),
            ],
            QueryType.INFORMATIONAL: [
                re.compile(r'\b(what\s+is|what\s+are|tell\s+me)\b', re.I),
                re.compile(r'\b(show|list|display|get|fetch)\b', re.I),
                re.compile(r'\b(information|details|status|state)\b', re.I),
            ],
            QueryType.NAVIGATIONAL: [
                re.compile(r'\b(find|locate|where|search)\b', re.I),
                re.compile(r'\b(go\s+to|navigate|link)\b', re.I),
                re.compile(r'\b(document|specification|guide)\b', re.I),
            ],
            QueryType.GENERATIVE: [
                re.compile(r'\b(generate|create|build|design)\b', re.I),
                re.compile(r'\b(write|implement|develop|code)\b', re.I),
                re.compile(r'\b(template|scaffold|boilerplate)\b', re.I),
            ],
        }

    async def classify_query(self,
                            query: str,
                            context=None) -> Tuple[QueryType, List[str]]:
        """
        Classify query and identify target domains

        Args:
            query: User query string
            context: Optional UserContext for preference-based routing

        Returns:
            Tuple of (QueryType, List of target domains)
        """
        logger.info(f"Classifying query: {query[:50]}...")

        # Classify query type
        query_type = await self._classify_type(query)

        # Detect target domains
        target_domains = await self._detect_domains(query, context)

        logger.info(
            f"Query classified as {query_type.value} "
            f"targeting domains: {target_domains}"
        )

        return query_type, target_domains

    async def _classify_type(self, query: str) -> QueryType:
        """
        Classify the query type using NLP or rules

        Args:
            query: User query string

        Returns:
            QueryType enum value
        """
        # Use transformer if available
        if self.use_transformers and self.classifier:
            return await self._classify_type_transformer(query)

        # Fallback to rule-based classification
        return await self._classify_type_rules(query)

    async def _classify_type_transformer(self, query: str) -> QueryType:
        """Classify query type using transformer model"""
        try:
            labels = [qt.value for qt in QueryType]

            result = self.classifier(
                query,
                candidate_labels=labels,
                multi_label=False
            )

            top_label = result['labels'][0]
            return QueryType(top_label)

        except Exception as e:
            logger.error(f"Transformer classification failed: {e}, falling back to rules")
            return await self._classify_type_rules(query)

    async def _classify_type_rules(self, query: str) -> QueryType:
        """Classify query type using rule-based patterns"""
        scores = {qt: 0 for qt in QueryType}

        for query_type, patterns in self.query_type_patterns.items():
            for pattern in patterns:
                if pattern.search(query):
                    scores[query_type] += 1

        # Return type with highest score, default to INFORMATIONAL
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return QueryType.INFORMATIONAL

    async def _detect_domains(self,
                             query: str,
                             context=None) -> List[str]:
        """
        Detect relevant domains for the query

        Args:
            query: User query string
            context: Optional UserContext

        Returns:
            List of domain names (AXIS, PIPE, ECO, IV)
        """
        detected_domains = []
        domain_scores = {}

        # Pattern-based detection
        for domain, patterns in self.domain_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(query):
                    score += 1

            if score > 0:
                domain_scores[domain] = score

        # Get domains with matches
        if domain_scores:
            # Sort by score
            sorted_domains = sorted(
                domain_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            detected_domains = [domain for domain, _ in sorted_domains]

        # Use context preferences if no domains detected
        if not detected_domains and context and hasattr(context, 'domain_preferences'):
            detected_domains = context.domain_preferences[:2]
            logger.debug(f"Using context preferences: {detected_domains}")

        # Default to PIPE if still no domains (general purpose)
        if not detected_domains:
            detected_domains = ['PIPE']
            logger.debug("No domains detected, defaulting to PIPE")

        return detected_domains

    def add_domain_pattern(self, domain: str, pattern: str):
        """
        Add a new pattern for domain detection

        Args:
            domain: Domain name (AXIS, PIPE, ECO, IV)
            pattern: Regex pattern string
        """
        if domain not in self.domain_patterns:
            self.domain_patterns[domain] = []

        self.domain_patterns[domain].append(re.compile(pattern, re.I))
        logger.info(f"Added pattern '{pattern}' for domain {domain}")

    def get_domain_keywords(self, domain: str) -> List[str]:
        """
        Get keywords associated with a domain

        Args:
            domain: Domain name

        Returns:
            List of keywords
        """
        if domain not in self.domain_patterns:
            return []

        keywords = []
        for pattern in self.domain_patterns[domain]:
            # Extract keywords from pattern (simplified)
            pattern_str = pattern.pattern
            # Remove regex syntax
            cleaned = re.sub(r'[\\()\[\]{}|^$.*+?]', ' ', pattern_str)
            keywords.extend(cleaned.split())

        return list(set(keywords))
