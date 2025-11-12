# 2-Tier CAG+RAG Technical Implementation Guide

## Code Examples and Integration Patterns

---

## 1. CAG Layer Implementation

### 1.1 Context Manager

```python
# context_manager.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib

@dataclass
class UserContext:
    """User context for CAG processing"""
    user_id: str
    session_id: str
    domain_preferences: List[str]
    interaction_history: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class ContextManager:
    """Manages context for CAG layer processing"""

    def __init__(self, redis_client=None, ttl: int = 3600):
        self.redis_client = redis_client
        self.ttl = ttl
        self.context_cache = {}

    async def build_context(self,
                           user_id: str,
                           session_id: str,
                           query: str) -> UserContext:
        """Build comprehensive context for query processing"""

        # Retrieve user history
        history = await self._get_user_history(user_id)

        # Analyse domain preferences
        domain_preferences = await self._analyse_domain_preferences(
            user_id, history
        )

        # Extract metadata
        metadata = {
            'timestamp': datetime.utcnow().isoformat(),
            'query_hash': hashlib.md5(query.encode()).hexdigest(),
            'session_start': await self._get_session_start(session_id),
            'interaction_count': len(history)
        }

        return UserContext(
            user_id=user_id,
            session_id=session_id,
            domain_preferences=domain_preferences,
            interaction_history=history[-10:],  # Last 10 interactions
            metadata=metadata
        )

    async def _get_user_history(self, user_id: str) -> List[Dict]:
        """Retrieve user interaction history"""
        if self.redis_client:
            history_key = f"user:history:{user_id}"
            history_json = await self.redis_client.get(history_key)
            if history_json:
                return json.loads(history_json)
        return []

    async def _analyse_domain_preferences(self,
                                         user_id: str,
                                         history: List[Dict]) -> List[str]:
        """Analyse and rank domain preferences based on history"""
        domain_counts = {}

        for interaction in history:
            domains = interaction.get('domains', [])
            for domain in domains:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        # Sort by frequency
        sorted_domains = sorted(
            domain_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [domain for domain, _ in sorted_domains[:5]]
```

### 1.2 Query Classifier

```python
# query_classifier.py
from enum import Enum
from typing import List, Tuple, Optional
import re
from transformers import pipeline

class QueryType(Enum):
    """Query classification types"""
    ANALYTICAL = "analytical"
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    GENERATIVE = "generative"

class QueryClassifier:
    """Classifies queries for appropriate routing"""

    def __init__(self, model_name: str = "bert-base-uncased"):
        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_name
        )
        self.domain_patterns = self._initialise_patterns()

    def _initialise_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialise regex patterns for domain detection"""
        return {
            'PIPE': [
                re.compile(r'\bapi\b', re.I),
                re.compile(r'\bintegration\b', re.I),
                re.compile(r'\bpipeline\b', re.I)
            ],
            'IV': [
                re.compile(r'\bllm\b', re.I),
                re.compile(r'\brag\b', re.I),
                re.compile(r'\bai\s+model\b', re.I)
            ],
            'AXIS': [
                re.compile(r'\bmachine\s+learning\b', re.I),
                re.compile(r'\bneural\s+network\b', re.I),
                re.compile(r'\bmodel\s+training\b', re.I)
            ],
            'BNI': [
                re.compile(r'\bbusiness\s+service\b', re.I),
                re.compile(r'\bworkflow\b', re.I)
            ],
            'ECO': [
                re.compile(r'\bblockchain\b', re.I),
                re.compile(r'\bsmart\s+contract\b', re.I),
                re.compile(r'\bcrypto\b', re.I)
            ]
        }

    async def classify_query(self,
                            query: str,
                            context: UserContext) -> Tuple[QueryType, List[str]]:
        """Classify query and identify target domains"""

        # Classify query type
        query_type = await self._classify_type(query)

        # Detect target domains
        target_domains = await self._detect_domains(query, context)

        return query_type, target_domains

    async def _classify_type(self, query: str) -> QueryType:
        """Classify the query type using NLP"""
        labels = [qt.value for qt in QueryType]

        result = self.classifier(
            query,
            candidate_labels=labels,
            multi_label=False
        )

        top_label = result['labels'][0]
        return QueryType(top_label)

    async def _detect_domains(self,
                             query: str,
                             context: UserContext) -> List[str]:
        """Detect relevant domains for the query"""
        detected_domains = []

        # Pattern-based detection
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if pattern.search(query):
                    detected_domains.append(domain)
                    break

        # Use context preferences if no domains detected
        if not detected_domains and context.domain_preferences:
            detected_domains = context.domain_preferences[:2]

        # Default to PIPE if still no domains
        if not detected_domains:
            detected_domains = ['PIPE']

        return detected_domains
```

### 1.3 Domain Router

```python
# domain_router.py
from typing import Dict, List, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

class DomainRouter:
    """Routes queries to appropriate domain services"""

    def __init__(self, domain_config: Dict[str, Any]):
        self.domain_config = domain_config
        self.domain_clients = self._initialise_clients()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def _initialise_clients(self) -> Dict[str, Any]:
        """Initialise domain-specific clients"""
        clients = {}
        for domain, config in self.domain_config.items():
            clients[domain] = DomainClient(
                endpoint=config['endpoint'],
                auth_token=config['auth_token'],
                timeout=config.get('timeout', 30)
            )
        return clients

    async def route_query(self,
                         query: str,
                         target_domains: List[str],
                         context: UserContext) -> Dict[str, Any]:
        """Route query to target domains and collect responses"""

        # Prepare routing tasks
        routing_tasks = []
        for domain in target_domains:
            if domain in self.domain_clients:
                task = self._route_to_domain(
                    domain=domain,
                    query=query,
                    context=context
                )
                routing_tasks.append(task)

        # Execute routing in parallel
        results = await asyncio.gather(*routing_tasks, return_exceptions=True)

        # Aggregate results
        aggregated_results = {}
        for domain, result in zip(target_domains, results):
            if isinstance(result, Exception):
                aggregated_results[domain] = {
                    'error': str(result),
                    'status': 'failed'
                }
            else:
                aggregated_results[domain] = result

        return aggregated_results

    async def _route_to_domain(self,
                              domain: str,
                              query: str,
                              context: UserContext) -> Dict[str, Any]:
        """Route query to specific domain"""
        client = self.domain_clients[domain]

        # Prepare domain-specific request
        request = {
            'query': query,
            'context': {
                'user_id': context.user_id,
                'session_id': context.session_id,
                'preferences': context.domain_preferences,
                'metadata': context.metadata
            },
            'domain': domain
        }

        # Send request to domain service
        response = await client.process_query(request)

        return response
```

---

## 2. RAG Layer Implementation

### 2.1 Hybrid Retrieval Engine

```python
# hybrid_retrieval_engine.py
import numpy as np
from typing import List, Dict, Any, Tuple
import faiss
from neo4j import AsyncGraphDatabase
import motor.motor_asyncio
from sentence_transformers import SentenceTransformer

class HybridRetrievalEngine:
    """Hybrid retrieval combining vector, graph, and document search"""

    def __init__(self, config: Dict[str, Any]):
        # Vector store configuration
        self.embedding_model = SentenceTransformer(
            config.get('embedding_model', 'all-MiniLM-L6-v2')
        )
        self.vector_index = self._initialise_vector_index(config)

        # Graph database configuration
        self.graph_driver = AsyncGraphDatabase.driver(
            config['neo4j_uri'],
            auth=(config['neo4j_user'], config['neo4j_password'])
        )

        # Document database configuration
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
            config['mongodb_uri']
        )
        self.document_db = self.mongo_client[config['mongodb_database']]

    def _initialise_vector_index(self, config: Dict) -> faiss.IndexFlatL2:
        """Initialise FAISS vector index"""
        dimension = config.get('embedding_dimension', 384)
        index = faiss.IndexFlatL2(dimension)

        # Load pre-built index if exists
        index_path = config.get('index_path')
        if index_path:
            loaded_index = faiss.read_index(index_path)
            return loaded_index

        return index

    async def hybrid_search(self,
                           query: str,
                           domain: str,
                           top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform hybrid search across all retrieval methods"""

        # Parallel retrieval from all sources
        vector_task = self._vector_search(query, domain, top_k)
        graph_task = self._graph_search(query, domain, top_k)
        document_task = self._document_search(query, domain, top_k)

        vector_results, graph_results, document_results = await asyncio.gather(
            vector_task, graph_task, document_task
        )

        # Fuse results
        fused_results = await self._fuse_results(
            vector_results,
            graph_results,
            document_results,
            weights={'vector': 0.4, 'graph': 0.35, 'document': 0.25}
        )

        return fused_results[:top_k]

    async def _vector_search(self,
                           query: str,
                           domain: str,
                           top_k: int) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])

        # Search in FAISS index
        distances, indices = self.vector_index.search(
            query_embedding.astype('float32'),
            top_k * 2  # Get more for fusion
        )

        # Retrieve metadata for results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # Valid index
                result = {
                    'id': f"vector_{idx}",
                    'score': float(1 / (1 + dist)),  # Convert distance to similarity
                    'type': 'vector',
                    'domain': domain,
                    'content': await self._get_vector_content(idx)
                }
                results.append(result)

        return results

    async def _graph_search(self,
                          query: str,
                          domain: str,
                          top_k: int) -> List[Dict[str, Any]]:
        """Perform graph traversal search"""
        async with self.graph_driver.session() as session:
            # Cypher query for knowledge graph traversal
            cypher_query = """
            MATCH (n:Entity {domain: $domain})
            WHERE n.name CONTAINS $query OR n.description CONTAINS $query
            OPTIONAL MATCH (n)-[r]-(related:Entity)
            WITH n, collect({
                node: related,
                relationship: type(r)
            }) as connections
            RETURN n, connections
            ORDER BY n.relevance_score DESC
            LIMIT $limit
            """

            result = await session.run(
                cypher_query,
                domain=domain,
                query=query,
                limit=top_k * 2
            )

            results = []
            async for record in result:
                node = record['n']
                connections = record['connections']

                results.append({
                    'id': f"graph_{node['id']}",
                    'score': node.get('relevance_score', 0.5),
                    'type': 'graph',
                    'domain': domain,
                    'content': {
                        'entity': dict(node),
                        'relations': connections
                    }
                })

            return results

    async def _document_search(self,
                              query: str,
                              domain: str,
                              top_k: int) -> List[Dict[str, Any]]:
        """Perform document full-text search"""
        collection = self.document_db[f"{domain}_documents"]

        # MongoDB full-text search
        pipeline = [
            {
                '$search': {
                    'text': {
                        'query': query,
                        'path': ['title', 'content', 'tags']
                    }
                }
            },
            {
                '$addFields': {
                    'search_score': {'$meta': 'searchScore'}
                }
            },
            {
                '$sort': {'search_score': -1}
            },
            {
                '$limit': top_k * 2
            }
        ]

        results = []
        async for doc in collection.aggregate(pipeline):
            results.append({
                'id': f"doc_{doc['_id']}",
                'score': doc['search_score'],
                'type': 'document',
                'domain': domain,
                'content': {
                    'title': doc.get('title', ''),
                    'text': doc.get('content', ''),
                    'metadata': doc.get('metadata', {})
                }
            })

        return results

    async def _fuse_results(self,
                          vector_results: List[Dict],
                          graph_results: List[Dict],
                          document_results: List[Dict],
                          weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Fuse results from multiple retrieval methods"""

        # Combine all results
        all_results = {}

        # Process vector results
        for result in vector_results:
            key = result['id']
            all_results[key] = result.copy()
            all_results[key]['final_score'] = result['score'] * weights['vector']

        # Process graph results
        for result in graph_results:
            key = result['id']
            if key in all_results:
                all_results[key]['final_score'] += result['score'] * weights['graph']
            else:
                all_results[key] = result.copy()
                all_results[key]['final_score'] = result['score'] * weights['graph']

        # Process document results
        for result in document_results:
            key = result['id']
            if key in all_results:
                all_results[key]['final_score'] += result['score'] * weights['document']
            else:
                all_results[key] = result.copy()
                all_results[key]['final_score'] = result['score'] * weights['document']

        # Sort by final score
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )

        return sorted_results
```

### 2.2 Knowledge Fusion Engine

```python
# knowledge_fusion_engine.py
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KnowledgeFusionEngine:
    """Fuses knowledge from multiple sources for augmented generation"""

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2)
        )
        self.confidence_threshold = 0.7

    async def fuse_knowledge(self,
                           retrieval_results: List[Dict[str, Any]],
                           query: str,
                           context: UserContext) -> Dict[str, Any]:
        """Fuse retrieved knowledge for response generation"""

        # Extract and deduplicate content
        knowledge_pieces = await self._extract_knowledge(retrieval_results)

        # Rank by relevance
        ranked_knowledge = await self._rank_knowledge(
            knowledge_pieces,
            query
        )

        # Validate and filter
        validated_knowledge = await self._validate_knowledge(
            ranked_knowledge,
            context
        )

        # Build knowledge graph
        knowledge_graph = await self._build_knowledge_graph(
            validated_knowledge
        )

        return {
            'primary_knowledge': validated_knowledge[:5],
            'supporting_knowledge': validated_knowledge[5:10],
            'knowledge_graph': knowledge_graph,
            'confidence_scores': self._calculate_confidence_scores(
                validated_knowledge
            ),
            'source_attribution': self._attribute_sources(retrieval_results)
        }

    async def _extract_knowledge(self,
                                results: List[Dict]) -> List[Dict[str, Any]]:
        """Extract unique knowledge pieces from results"""
        knowledge_map = {}

        for result in results:
            content = result.get('content', {})

            # Extract based on result type
            if result['type'] == 'vector':
                text = content.get('text', '')
                key = hashlib.md5(text.encode()).hexdigest()[:8]
                knowledge_map[key] = {
                    'text': text,
                    'type': 'vector',
                    'source': result['id'],
                    'score': result['final_score']
                }

            elif result['type'] == 'graph':
                entity = content.get('entity', {})
                relations = content.get('relations', [])
                key = f"graph_{entity.get('id', '')}"
                knowledge_map[key] = {
                    'entity': entity,
                    'relations': relations,
                    'type': 'graph',
                    'source': result['id'],
                    'score': result['final_score']
                }

            elif result['type'] == 'document':
                text = content.get('text', '')
                key = hashlib.md5(text.encode()).hexdigest()[:8]
                knowledge_map[key] = {
                    'text': text,
                    'title': content.get('title', ''),
                    'type': 'document',
                    'source': result['id'],
                    'score': result['final_score']
                }

        return list(knowledge_map.values())

    async def _rank_knowledge(self,
                            knowledge_pieces: List[Dict],
                            query: str) -> List[Dict]:
        """Rank knowledge pieces by relevance to query"""

        # Extract texts for TF-IDF
        texts = []
        for piece in knowledge_pieces:
            if piece['type'] in ['vector', 'document']:
                texts.append(piece.get('text', ''))
            elif piece['type'] == 'graph':
                entity = piece.get('entity', {})
                texts.append(entity.get('description', ''))

        if not texts:
            return knowledge_pieces

        # Add query to texts
        texts.append(query)

        # Calculate TF-IDF
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

        # Calculate similarity with query
        query_vector = tfidf_matrix[-1]
        similarities = cosine_similarity(
            query_vector,
            tfidf_matrix[:-1]
        ).flatten()

        # Update scores
        for i, piece in enumerate(knowledge_pieces):
            if i < len(similarities):
                piece['relevance_score'] = float(similarities[i])
                piece['combined_score'] = (
                    piece['score'] * 0.6 +
                    piece['relevance_score'] * 0.4
                )

        # Sort by combined score
        ranked = sorted(
            knowledge_pieces,
            key=lambda x: x.get('combined_score', 0),
            reverse=True
        )

        return ranked
```

---

## 3. Integration with OpenCode/OpenSpec

### 3.1 OpenSpec Integration

```python
# openspec_integration.py
from typing import Dict, Any, List, Optional
import yaml
import jsonschema
from pathlib import Path

class OpenSpecIntegration:
    """Integration with OpenSpec for specification-driven development"""

    def __init__(self, spec_dir: Path):
        self.spec_dir = spec_dir
        self.specs = self._load_specs()
        self.validators = self._initialise_validators()

    def _load_specs(self) -> Dict[str, Any]:
        """Load OpenSpec specifications"""
        specs = {}

        for spec_file in self.spec_dir.glob("*.yaml"):
            with open(spec_file, 'r') as f:
                spec_data = yaml.safe_load(f)
                spec_name = spec_file.stem
                specs[spec_name] = spec_data

        return specs

    async def validate_against_spec(self,
                                   domain: str,
                                   operation: str,
                                   data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate data against OpenSpec specification"""

        spec_key = f"{domain}_{operation}"
        if spec_key not in self.specs:
            return False, [f"No specification found for {spec_key}"]

        spec = self.specs[spec_key]
        schema = spec.get('schema', {})

        try:
            jsonschema.validate(instance=data, schema=schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]

    async def generate_from_spec(self,
                                domain: str,
                                operation: str,
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code/configuration from OpenSpec"""

        spec_key = f"{domain}_{operation}"
        spec = self.specs.get(spec_key, {})

        # Get template
        template = spec.get('template', {})

        # Apply parameters to template
        generated = self._apply_template(template, parameters)

        # Validate generated output
        valid, errors = await self.validate_against_spec(
            domain,
            operation,
            generated
        )

        if not valid:
            raise ValueError(f"Generated output validation failed: {errors}")

        return generated

    def _apply_template(self,
                       template: Dict[str, Any],
                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply parameters to template"""
        import jinja2

        # Convert template to string for Jinja2 processing
        template_str = yaml.dump(template)

        # Create Jinja2 template
        j2_template = jinja2.Template(template_str)

        # Render with parameters
        rendered = j2_template.render(**parameters)

        # Convert back to dict
        return yaml.safe_load(rendered)
```

### 3.2 MCP Server Integration

```python
# mcp_server_integration.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

class QueryRequest(BaseModel):
    """Request model for CAG+RAG queries"""
    query: str
    user_id: str
    session_id: str
    domains: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    """Response model for CAG+RAG queries"""
    response: str
    metadata: Dict[str, Any]
    sources: List[Dict[str, Any]]
    confidence: float

class MCPServer:
    """MCP Server for CAG+RAG system"""

    def __init__(self, config: Dict[str, Any]):
        self.app = FastAPI(title="CAG+RAG MCP Server")
        self.config = config

        # Initialise components
        self.context_manager = ContextManager()
        self.query_classifier = QueryClassifier()
        self.domain_router = DomainRouter(config['domains'])
        self.retrieval_engine = HybridRetrievalEngine(config['retrieval'])
        self.fusion_engine = KnowledgeFusionEngine()
        self.openspec = OpenSpecIntegration(Path(config['spec_dir']))

        # Setup routes
        self._setup_routes()

        # Setup middleware
        self._setup_middleware()

    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.post("/api/v1/query", response_model=QueryResponse)
        async def process_query(request: QueryRequest):
            """Process CAG+RAG query"""
            try:
                # Build context (CAG Layer)
                context = await self.context_manager.build_context(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    query=request.query
                )

                # Classify query
                query_type, target_domains = await self.query_classifier.classify_query(
                    query=request.query,
                    context=context
                )

                # Override with requested domains if provided
                if request.domains:
                    target_domains = request.domains

                # Route to domains
                domain_results = await self.domain_router.route_query(
                    query=request.query,
                    target_domains=target_domains,
                    context=context
                )

                # Perform hybrid retrieval (RAG Layer)
                all_retrieval_results = []
                for domain in target_domains:
                    results = await self.retrieval_engine.hybrid_search(
                        query=request.query,
                        domain=domain,
                        top_k=10
                    )
                    all_retrieval_results.extend(results)

                # Fuse knowledge
                fused_knowledge = await self.fusion_engine.fuse_knowledge(
                    retrieval_results=all_retrieval_results,
                    query=request.query,
                    context=context
                )

                # Generate response
                response = await self._generate_response(
                    query=request.query,
                    knowledge=fused_knowledge,
                    context=context
                )

                return QueryResponse(
                    response=response['text'],
                    metadata={
                        'query_type': query_type.value,
                        'domains': target_domains,
                        'processing_time': response['processing_time']
                    },
                    sources=fused_knowledge['source_attribution'],
                    confidence=response['confidence']
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "version": "1.0.0"}

        @self.app.get("/api/v1/domains")
        async def get_domains():
            """Get available domains"""
            return {"domains": list(self.config['domains'].keys())}

    async def _generate_response(self,
                                query: str,
                                knowledge: Dict[str, Any],
                                context: UserContext) -> Dict[str, Any]:
        """Generate final response using fused knowledge"""

        # Implementation depends on your LLM choice
        # This is a placeholder

        response_text = f"Based on the analysis across domains, here's the response to '{query}'..."

        return {
            'text': response_text,
            'confidence': 0.85,
            'processing_time': 1.234
        }

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the MCP server"""
        uvicorn.run(self.app, host=host, port=port)
```

---

## 4. Deployment Configuration

### 4.1 Docker Compose Configuration

```yaml
# docker-compose.yaml
version: '3.8'

services:
  # CAG Layer Services
  cag-api:
    build:
      context: ./cag
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - POSTGRES_URL=postgresql://user:pass@postgres:5432/cag_db
    depends_on:
      - redis
      - postgres
    networks:
      - cag-rag-network

  # RAG Layer Services
  rag-engine:
    build:
      context: ./rag
      dockerfile: Dockerfile
    ports:
      - "8002:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - MONGODB_URI=mongodb://mongodb:27017
      - FAISS_INDEX_PATH=/data/faiss_index
    volumes:
      - ./data:/data
    depends_on:
      - neo4j
      - mongodb
    networks:
      - cag-rag-network

  # MCP Server
  mcp-server:
    build:
      context: ./mcp
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CAG_API_URL=http://cag-api:8000
      - RAG_API_URL=http://rag-engine:8000
      - OPENSPEC_DIR=/specs
    volumes:
      - ./specs:/specs
    depends_on:
      - cag-api
      - rag-engine
    networks:
      - cag-rag-network

  # Supporting Services
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - cag-rag-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=cag_db
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - cag-rag-network

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_apoc_export_file_enabled=true
      - NEO4J_apoc_import_file_enabled=true
    volumes:
      - neo4j-data:/data
    networks:
      - cag-rag-network

  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongodb-data:/data/db
    networks:
      - cag-rag-network

networks:
  cag-rag-network:
    driver: bridge

volumes:
  redis-data:
  postgres-data:
  neo4j-data:
  mongodb-data:
```

### 4.2 Kubernetes Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cag-rag-system
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cag-rag
  template:
    metadata:
      labels:
        app: cag-rag
    spec:
      containers:
      - name: mcp-server
        image: cag-rag/mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: CONFIG_PATH
          value: /config/config.yaml
        volumeMounts:
        - name: config
          mountPath: /config
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"

      - name: cag-engine
        image: cag-rag/cag-engine:latest
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"

      - name: rag-engine
        image: cag-rag/rag-engine:latest
        ports:
        - containerPort: 8002
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"

      volumes:
      - name: config
        configMap:
          name: cag-rag-config

---
apiVersion: v1
kind: Service
metadata:
  name: cag-rag-service
  namespace: production
spec:
  selector:
    app: cag-rag
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## 5. Testing and Monitoring

### 5.1 Integration Tests

```python
# tests/test_integration.py
import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_cag_rag_pipeline():
    """Test complete CAG+RAG pipeline"""

    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Test query
        request = {
            "query": "How do I integrate smart contracts with the PIPE network?",
            "user_id": "test_user",
            "session_id": "test_session",
            "domains": ["PIPE", "ECO"]
        }

        # Send request
        response = await client.post("/api/v1/query", json=request)

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "metadata" in data
        assert "sources" in data
        assert "confidence" in data

        assert len(data["sources"]) > 0
        assert data["confidence"] > 0.5

        # Verify domains processed
        assert "PIPE" in data["metadata"]["domains"]
        assert "ECO" in data["metadata"]["domains"]
```

---

## 6. Performance Optimisation

### 6.1 Caching Strategy

```python
# caching_strategy.py
from functools import lru_cache
import redis
import pickle
import hashlib

class CachingStrategy:
    """Multi-level caching for CAG+RAG system"""

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.local_cache = {}

    async def get_or_compute(self,
                            key: str,
                            compute_func,
                            ttl: int = 3600):
        """Get from cache or compute and store"""

        # Check local cache first
        if key in self.local_cache:
            return self.local_cache[key]

        # Check Redis cache
        cached_value = await self.redis_client.get(key)
        if cached_value:
            value = pickle.loads(cached_value)
            self.local_cache[key] = value
            return value

        # Compute value
        value = await compute_func()

        # Store in caches
        self.local_cache[key] = value
        await self.redis_client.set(
            key,
            pickle.dumps(value),
            ex=ttl
        )

        return value

    def generate_cache_key(self, *args, **kwargs):
        """Generate cache key from arguments"""
        key_data = f"{args}_{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
```

---

## 7. Architecture Compliance

### 7.1 FAGAM Prohibition Compliance

This implementation adheres to FAGAM + HashiCorp prohibition requirements:

**Prohibited Technologies (NOT used):**
- ❌ Google Cloud Platform services
- ❌ AWS proprietary services
- ❌ Microsoft Azure services
- ❌ HashiCorp Terraform (use OpenTofu instead)
- ❌ HashiCorp Vault (use OpenBao instead)

**Approved Technologies (used in this guide):**
- ✅ Open-source databases: PostgreSQL, MongoDB, Neo4j, Redis
- ✅ Open-source ML/AI: Sentence Transformers, FAISS, scikit-learn
- ✅ Open-source frameworks: FastAPI, Pydantic
- ✅ CNCF projects: Kubernetes
- ✅ Standard Python libraries

### 7.2 Container Requirements

All containers must adhere to:
- Maximum size: 50MB
- Base image: Chainguard Wolfi (apko)
- Declarative builds only
- No FAGAM dependencies

Example Dockerfile for CAG+RAG components:

```dockerfile
FROM cgr.dev/chainguard/wolfi-base:latest

# Install minimal dependencies
RUN apk add --no-cache python-3.11 py3-pip

# Copy requirements
COPY requirements.txt /app/
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Run application
CMD ["python3", "main.py"]
```

---

## 8. Integration with BSW-Arch Bot Factory

### 8.1 Domain-Specific Bot Integration

The CAG+RAG system integrates with bot domains:

**AXIS Domain (Architecture):**
- Architecture validation bots
- Design pattern bots
- Blueprint generation bots

**PIPE Domain (Pipeline/Integration):**
- API integration bots
- Data pipeline bots
- Workflow orchestration bots

**ECO Domain (Ecosystem):**
- Blockchain integration bots
- Smart contract management bots
- Distributed ledger bots

**IV Domain (Innovation & Validation):**
- LLM integration bots
- Model validation bots
- AI/ML experimentation bots

### 8.2 Knowledge Base Integration

The system integrates with the META-KERAGR knowledge base architecture:

```python
# meta_keragr_integration.py
class MetaKERAGRIntegration:
    """Integration with META-KERAGR knowledge base"""

    def __init__(self, keragr_config: Dict[str, Any]):
        self.keragr_url = keragr_config['url']
        self.keragr_api_key = keragr_config['api_key']

    async def query_knowledge_base(self,
                                  query: str,
                                  domain: str,
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Query META-KERAGR knowledge base"""

        # Prepare KERAGR query
        keragr_query = {
            'query': query,
            'domain': domain,
            'context': context,
            'retrieval_mode': 'hybrid',
            'top_k': 20
        }

        # Send request to KERAGR API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.keragr_url}/api/query",
                json=keragr_query,
                headers={'Authorization': f'Bearer {self.keragr_api_key}'}
            ) as response:
                return await response.json()
```

---

## 9. Monitoring and Observability

### 9.1 Prometheus Metrics

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
query_counter = Counter('cag_rag_queries_total', 'Total queries processed')
query_duration = Histogram('cag_rag_query_duration_seconds', 'Query processing duration')
active_queries = Gauge('cag_rag_active_queries', 'Number of active queries')
domain_routing = Counter('cag_rag_domain_routing_total', 'Domain routing events', ['domain'])

class MetricsCollector:
    """Collect metrics for CAG+RAG system"""

    @staticmethod
    async def track_query(query_func):
        """Decorator to track query metrics"""
        async def wrapper(*args, **kwargs):
            query_counter.inc()
            active_queries.inc()

            start_time = time.time()
            try:
                result = await query_func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                query_duration.observe(duration)
                active_queries.dec()

        return wrapper
```

### 9.2 Logging Configuration

```python
# logging_config.py
import logging
import structlog

def setup_logging():
    """Setup structured logging"""

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )
```

---

## 10. Security Considerations

### 10.1 Authentication and Authorisation

```python
# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

class SecurityManager:
    """Manage authentication and authorisation"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    async def verify_token(self,
                          credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
```

### 10.2 Rate Limiting

```python
# rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

class RateLimitConfig:
    """Rate limiting configuration"""

    # API rate limits
    QUERY_LIMIT = "10/minute"
    BATCH_LIMIT = "100/hour"
    HEAVY_QUERY_LIMIT = "5/minute"
```

---

*Technical Implementation Guide v1.0*
*Last Updated: November 2024*
*BSW-Arch Bot Factory - Architecture Documentation*
