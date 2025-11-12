"""
Query Classifier - Classifies queries and detects target domains
Uses Hugging Face sentence transformers for embedding-based classification
"""

from typing import Tuple, List, Dict
from enum import Enum
import re
import torch
from sentence_transformers import SentenceTransformer
import numpy as np
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
    """Classifies queries for appropriate routing"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model: SentenceTransformer = None
        self.domain_patterns = self._initialise_domain_patterns()
        self.query_type_patterns = self._initialise_type_patterns()

    async def initialise(self):
        """Initialise the embedding model"""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.model.eval()  # Set to evaluation mode

        # Warm up the model
        _ = self.model.encode("test query")

        logger.info("Query Classifier initialised")

    def _initialise_domain_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialise regex patterns for domain detection"""
        return {
            'PIPE': [
                re.compile(r'\bapi\b', re.I),
                re.compile(r'\bintegration\b', re.I),
                re.compile(r'\bpipeline\b', re.I),
                re.compile(r'\bendpoint\b', re.I),
                re.compile(r'\brest\b', re.I),
                re.compile(r'\bwebhook\b', re.I),
            ],
            'IV': [
                re.compile(r'\bllm\b', re.I),
                re.compile(r'\brag\b', re.I),
                re.compile(r'\bai\s+model\b', re.I),
                re.compile(r'\bchat\b', re.I),
                re.compile(r'\bconversation\b', re.I),
                re.compile(r'\bgenerat(e|ion)\b', re.I),
            ],
            'AXIS': [
                re.compile(r'\barchitecture\b', re.I),
                re.compile(r'\bdesign\s+pattern\b', re.I),
                re.compile(r'\bsystem\s+design\b', re.I),
                re.compile(r'\btogaf\b', re.I),
                re.compile(r'\barchimat(e|ure)\b', re.I),
            ],
            'BNI': [
                re.compile(r'\bbusiness\s+(service|process)\b', re.I),
                re.compile(r'\bworkflow\b', re.I),
                re.compile(r'\bprocess\s+automation\b', re.I),
            ],
            'BNP': [
                re.compile(r'\bplatform\b', re.I),
                re.compile(r'\binfrastructure\b', re.I),
                re.compile(r'\bcloud\b', re.I),
            ],
            'ECO': [
                re.compile(r'\bblockchain\b', re.I),
                re.compile(r'\bsmart\s+contract\b', re.I),
                re.compile(r'\bcrypto\b', re.I),
                re.compile(r'\bweb3\b', re.I),
                re.compile(r'\bdecentrali[sz]ed\b', re.I),
            ],
            'DC': [
                re.compile(r'\bmedia\b', re.I),
                re.compile(r'\bcontent\b', re.I),
                re.compile(r'\bdigital\s+asset\b', re.I),
                re.compile(r'\bdam\b', re.I),
            ],
            'BU': [
                re.compile(r'\banalytics\b', re.I),
                re.compile(r'\breport(ing)?\b', re.I),
                re.compile(r'\bmetrics\b', re.I),
                re.compile(r'\bdashboard\b', re.I),
            ]
        }

    def _initialise_type_patterns(self) -> Dict[QueryType, List[str]]:
        """Initialise patterns for query type classification"""
        return {
            QueryType.INFORMATIONAL: [
                'how', 'what', 'why', 'when', 'where', 'who',
                'explain', 'describe', 'tell me about', 'define'
            ],
            QueryType.GENERATIVE: [
                'create', 'generate', 'build', 'write', 'make',
                'design', 'develop', 'implement', 'code'
            ],
            QueryType.ANALYTICAL: [
                'analyse', 'analyze', 'compare', 'evaluate',
                'assess', 'review', 'examine', 'investigate'
            ],
            QueryType.TRANSACTIONAL: [
                'update', 'delete', 'insert', 'modify',
                'change', 'add', 'remove', 'set'
            ],
            QueryType.NAVIGATIONAL: [
                'show', 'list', 'find', 'search', 'get',
                'fetch', 'retrieve', 'display'
            ]
        }

    async def classify_query(self,
                            query: str,
                            context: 'UserContext') -> Tuple[QueryType, List[str]]:
        """
        Classify query and identify target domains

        Returns:
            Tuple of (QueryType, List of domain names)
        """
        # Classify query type
        query_type = self._classify_type(query)

        # Detect target domains
        domains = self._detect_domains(query, context)

        logger.info(
            f"Query classified - Type: {query_type.value}, "
            f"Domains: {domains}"
        )

        return query_type, domains

    def _classify_type(self, query: str) -> QueryType:
        """Classify the query type using pattern matching"""
        query_lower = query.lower()

        # Score each type
        type_scores = {}

        for qtype, patterns in self.query_type_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in query_lower:
                    score += 1
            type_scores[qtype] = score

        # Return type with highest score
        if max(type_scores.values()) > 0:
            return max(type_scores.items(), key=lambda x: x[1])[0]

        # Default to informational
        return QueryType.INFORMATIONAL

    def _detect_domains(self,
                       query: str,
                       context: 'UserContext') -> List[str]:
        """Detect relevant domains for the query"""
        detected_domains = set()

        # Pattern-based detection
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if pattern.search(query):
                    detected_domains.add(domain)
                    break

        # Use semantic similarity if model is loaded
        if self.model is not None and len(detected_domains) == 0:
            semantic_domains = self._semantic_domain_detection(query)
            detected_domains.update(semantic_domains)

        # Use context preferences if still no domains detected
        if not detected_domains and context.domain_preferences:
            detected_domains.update(context.domain_preferences[:2])

        # Default to PIPE if no domains detected
        if not detected_domains:
            detected_domains.add('PIPE')

        return sorted(list(detected_domains))

    def _semantic_domain_detection(self, query: str) -> List[str]:
        """
        Use semantic similarity to detect domains
        Compares query embedding with domain description embeddings
        """
        # Domain descriptions for semantic matching
        domain_descriptions = {
            'PIPE': "API integration pipeline endpoints REST services",
            'IV': "AI LLM RAG chat conversation generation",
            'AXIS': "Architecture design patterns system TOGAF",
            'BNI': "Business services workflow process automation",
            'BNP': "Platform infrastructure cloud deployment",
            'ECO': "Blockchain smart contracts crypto web3",
            'DC': "Digital media content assets management",
            'BU': "Analytics reporting metrics dashboards"
        }

        try:
            # Encode query
            query_embedding = self.model.encode(query, convert_to_tensor=True)

            # Encode domain descriptions
            domain_embeddings = self.model.encode(
                list(domain_descriptions.values()),
                convert_to_tensor=True
            )

            # Calculate cosine similarity
            similarities = torch.nn.functional.cosine_similarity(
                query_embedding.unsqueeze(0),
                domain_embeddings
            )

            # Get domains with similarity > threshold
            threshold = 0.3
            domains = []

            for idx, similarity in enumerate(similarities):
                if similarity > threshold:
                    domain_name = list(domain_descriptions.keys())[idx]
                    domains.append(domain_name)

            return domains[:3]  # Top 3 domains

        except Exception as e:
            logger.error(f"Semantic domain detection error: {e}")
            return []
