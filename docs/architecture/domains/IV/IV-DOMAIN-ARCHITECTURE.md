# IV Domain Architecture

> Intelligence, Validation, LLM Integration, and RAG Systems

**Version**: 1.0.0
**Last Updated**: 2025-11-11
**Domain**: IV (Intelligence/Validation)
**Bot Count**: 44

## Overview

The IV (Intelligence/Validation) domain manages AI/ML model integration, LLM orchestration, RAG (Retrieval-Augmented Generation) systems, knowledge base management, and intelligent validation for the BSW-Arch bot factory. This domain ensures intelligent operations across all 185 bots while maintaining FAGAM compliance and leveraging state-of-the-art AI technologies.

## Domain Responsibilities

### 1. LLM Integration & Orchestration
- LLM model management and deployment
- Multi-model orchestration (Claude, GPT, local models)
- Prompt engineering and optimization
- Model versioning and selection
- Token usage optimization

### 2. RAG Systems
- Vector database management (FAISS)
- Knowledge graph operations (Neo4j)
- Document store management (MongoDB)
- Hybrid retrieval strategies
- Context-aware generation

### 3. Context-Augmented Generation (CAG)
- User context management
- Session tracking and history
- Query classification and routing
- Domain preference analysis
- Multi-domain query coordination

### 4. Knowledge Base Management
- Documentation indexing and retrieval
- Knowledge graph construction
- Semantic search optimization
- Content validation and quality
- Cross-domain knowledge linking

### 5. Intelligent Validation
- Code validation using AI
- Documentation completeness checking
- Architectural compliance validation
- Quality assurance automation
- Anomaly detection

### 6. Model Training & Fine-tuning
- Custom model training workflows
- Fine-tuning for domain-specific tasks
- Embedding model optimization
- Transfer learning strategies
- Model evaluation and testing

## Architecture Patterns

### 2-Tier CAG+RAG Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CAG Layer (Tier 1)                │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Context     │  │    Query     │  │  Domain  │ │
│  │   Manager     │→ │  Classifier  │→ │  Router  │ │
│  └───────────────┘  └──────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│                   RAG Layer (Tier 2)                │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │    Hybrid     │  │  Knowledge   │  │ Response │ │
│  │   Retrieval   │→ │    Fusion    │→ │Generator │ │
│  └───────────────┘  └──────────────┘  └──────────┘ │
│   ↓       ↓      ↓                                  │
│  Vector  Graph  Docs                                │
└─────────────────────────────────────────────────────┘
```

### Data Stores

#### Vector Store (FAISS)
- **Purpose**: Semantic similarity search
- **Technology**: FAISS IndexFlatL2
- **Embeddings**: sentence-transformers (384d)
- **Scale**: Millions of vectors
- **Use Cases**: Code search, documentation retrieval

#### Graph Store (Neo4j)
- **Purpose**: Knowledge graph and relationships
- **Technology**: Neo4j 5 Community
- **Query Language**: Cypher
- **Use Cases**: Entity relationships, architectural dependencies

#### Document Store (MongoDB)
- **Purpose**: Full-text search and document storage
- **Technology**: MongoDB 6 with Atlas Search
- **Scale**: All BSW-Arch documentation
- **Use Cases**: Document retrieval, metadata management

#### Cache Layer (Redis)
- **Purpose**: Session state, query caching
- **Technology**: Redis 7
- **TTL**: Configurable (default 1 hour)
- **Use Cases**: Context caching, rate limiting

## Technology Stack

### AI/ML Frameworks
- **LLM Orchestration**: CrewAI
- **Embeddings**: sentence-transformers
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **NLP**: Transformers (Hugging Face)

### Databases
- **Graph**: Neo4j 5 Community Edition
- **Document**: MongoDB 6
- **Vector**: FAISS indexes
- **Cache**: Redis 7

### API & Integration
- **Framework**: FastAPI
- **Protocol**: HTTP/REST, WebSocket
- **Authentication**: JWT tokens
- **Spec**: OpenAPI 3.0

### Containerization
- **Base**: apko + Chainguard Wolfi
- **Target Size**: <50MB per container
- **Orchestration**: Kubernetes (production)
- **Local Dev**: Docker Compose

## IV Bot Categories

### 1. LLM Integration Bots (12 bots)
- `iv-llm-orchestrator-001` - Multi-model LLM orchestration
- `iv-llm-claude-001` - Claude API integration
- `iv-llm-gpt-001` - OpenAI GPT integration
- `iv-llm-local-001` - Local model management
- `iv-llm-prompt-engineer-001` - Prompt optimization
- `iv-llm-token-optimizer-001` - Token usage optimization
- `iv-llm-response-validator-001` - Response quality validation
- `iv-llm-context-builder-001` - Context window management
- `iv-llm-streaming-001` - Streaming response handler
- `iv-llm-embeddings-001` - Embedding generation
- `iv-llm-fine-tuner-001` - Model fine-tuning
- `iv-llm-evaluator-001` - Model performance evaluation

### 2. RAG System Bots (10 bots)
- `iv-rag-hybrid-retrieval-001` - Hybrid search coordinator
- `iv-rag-vector-search-001` - Vector similarity search
- `iv-rag-graph-traversal-001` - Knowledge graph queries
- `iv-rag-document-search-001` - Full-text document search
- `iv-rag-fusion-engine-001` - Multi-source result fusion
- `iv-rag-reranker-001` - Result reranking
- `iv-rag-chunk-optimizer-001` - Document chunking optimization
- `iv-rag-index-builder-001` - Index construction and updates
- `iv-rag-query-expander-001` - Query expansion
- `iv-rag-relevance-scorer-001` - Relevance scoring

### 3. Knowledge Base Bots (8 bots)
- `iv-kb-indexer-001` - Documentation indexing
- `iv-kb-graph-builder-001` - Knowledge graph construction
- `iv-kb-validator-001` - Content validation
- `iv-kb-linker-001` - Cross-reference linking
- `iv-kb-summarizer-001` - Content summarization
- `iv-kb-tagger-001` - Automatic tagging
- `iv-kb-version-tracker-001` - Version control integration
- `iv-kb-quality-checker-001` - Quality assurance

### 4. Context Management Bots (6 bots)
- `iv-ctx-session-manager-001` - Session state management
- `iv-ctx-history-tracker-001` - Interaction history
- `iv-ctx-preference-analyzer-001` - User preference analysis
- `iv-ctx-domain-router-001` - Multi-domain routing
- `iv-ctx-query-classifier-001` - Query intent classification
- `iv-ctx-cache-manager-001` - Context caching

### 5. Validation Bots (8 bots)
- `iv-val-code-checker-001` - AI-powered code validation
- `iv-val-docs-checker-001` - Documentation completeness
- `iv-val-arch-compliance-001` - Architecture validation
- `iv-val-security-scanner-001` - Security vulnerability detection
- `iv-val-quality-analyzer-001` - Quality metrics analysis
- `iv-val-anomaly-detector-001` - Anomaly detection
- `iv-val-consistency-checker-001` - Cross-domain consistency
- `iv-val-performance-analyzer-001` - Performance analysis

## Integration Points

### With PIPE Domain
- Code analysis for CI/CD pipelines
- Automated code review
- Documentation generation
- Build failure analysis

### With AXIS Domain
- ML model validation
- Architecture compliance checking
- Design pattern recommendations
- Technical debt analysis

### With ECO Domain
- Resource optimization recommendations
- Infrastructure health analysis
- Cost optimization insights
- Monitoring alert intelligence

### With BNI Domain
- Business logic validation
- Workflow optimization
- Process intelligence
- Decision support

## Key Workflows

### 1. CAG+RAG Query Processing

```
User Query
    ↓
Context Building (CAG)
    ↓
Query Classification
    ↓
Domain Routing
    ↓
Hybrid Retrieval (RAG)
    ├→ Vector Search
    ├→ Graph Traversal
    └→ Document Search
    ↓
Knowledge Fusion
    ↓
Response Generation
    ↓
User Response
```

### 2. Knowledge Base Update

```
New Documentation
    ↓
Content Validation
    ↓
Chunking & Processing
    ↓
Parallel Indexing
    ├→ Vector Index (FAISS)
    ├→ Graph Index (Neo4j)
    └→ Document Index (MongoDB)
    ↓
Cross-Reference Linking
    ↓
Quality Verification
    ↓
Production Deployment
```

### 3. Multi-Domain Intelligence

```
Complex Query
    ↓
Query Classification (IV)
    ↓
Domain Detection
    ├→ PIPE Context
    ├→ AXIS Context
    ├→ ECO Context
    └→ BNI Context
    ↓
Parallel Domain Queries
    ↓
Knowledge Fusion (IV)
    ↓
Unified Response
```

## Configuration

### Environment Variables

```bash
# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LLM_MODEL_PRIMARY=claude-3-opus-20240229
LLM_MODEL_FALLBACK=gpt-4-turbo
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.7

# Vector Store
FAISS_INDEX_PATH=/data/faiss_index
FAISS_INDEX_TYPE=IndexFlatL2
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Graph Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<secure-password>
NEO4J_DATABASE=bsw_knowledge

# Document Store
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DATABASE=bsw_docs
MONGODB_COLLECTION_PREFIX=iv_

# Cache
REDIS_URL=redis://redis:6379
REDIS_DB=0
REDIS_TTL=3600

# MCP Server
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
MCP_WORKERS=4
MCP_TIMEOUT=30
```

### Resource Requirements

#### Development
- **Memory**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum
- **Storage**: 20GB for indexes and models
- **GPU**: Optional (improves embedding generation)

#### Production
- **Memory**: 32GB per node
- **CPU**: 16 cores per node
- **Storage**: 100GB SSD for indexes
- **GPU**: Recommended (NVIDIA T4 or better)
- **Replicas**: 3 minimum for high availability

## Performance Metrics

### Query Performance
- **p50 Latency**: <500ms
- **p95 Latency**: <1500ms
- **p99 Latency**: <3000ms
- **Throughput**: 100 queries/second

### Retrieval Accuracy
- **Vector Search Recall@10**: >0.85
- **Graph Traversal Precision**: >0.90
- **Document Search F1**: >0.80
- **Hybrid Fusion Improvement**: +15-20%

### Resource Utilization
- **Container Size**: 45-50MB (target <50MB)
- **Memory per Pod**: 2-4GB
- **CPU per Pod**: 0.5-2 cores
- **Cache Hit Rate**: >70%

## Security Considerations

### API Security
- JWT-based authentication
- Rate limiting (100 req/min per user)
- Request validation
- Response sanitization

### Data Privacy
- PII detection and masking
- Secure credential storage (OpenBao)
- Audit logging
- GDPR compliance

### Model Security
- Prompt injection detection
- Output filtering
- Model access controls
- Version pinning

## Monitoring & Observability

### Key Metrics
- Query latency (p50, p95, p99)
- Cache hit rate
- Model API usage and costs
- Retrieval accuracy scores
- Error rates by component

### Logging
- Structured JSON logs
- Request/response tracing
- Error stack traces
- Performance profiling

### Alerting
- High latency (>3s)
- Low accuracy (<0.7)
- API errors (>5%)
- Resource exhaustion

## Development Guide

### Local Setup

```bash
# Clone repository
git clone https://codeberg.org/bsw-tech/iv-bots.git
cd iv-bots

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start dependencies
docker-compose up -d redis neo4j mongodb

# Build FAISS index
python scripts/build_index.py

# Run development server
uvicorn main:app --reload --port 8000
```

### Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# Load testing
locust -f tests/load/locustfile.py
```

### Deployment

```bash
# Build containers
apko build config.yaml iv-bot:latest iv-bot.tar

# Tag and push
docker tag iv-bot:latest codeberg.org/bsw-tech/iv-bot:latest
docker push codeberg.org/bsw-tech/iv-bot:latest

# Deploy to Kubernetes
kubectl apply -f k8s/
```

## Related Documentation

### Implementation Guides
- [CAG+RAG Technical Implementation](../../../guides/bot-domains/IV-BOTS-CAG-RAG-IMPLEMENTATION.md) - Detailed code examples and integration patterns
- [BSW-Tech AI Integration Guide](../../../guides/development/BSW-TECH-AI-INTEGRATION-GUIDE.md)
- [Claude Integration Guide](../../../guides/development/CLAUDE.md)

### Architecture Documents
- [Comprehensive Bot Factory Architecture](../../COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md)
- [Bots Knowledge Base Architecture](../../components/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md)

### Other Domains
- [PIPE Domain](./PIPE-DOMAIN-ARCHITECTURE.md) - Pipeline and CI/CD
- [AXIS Domain](./AXIS-DOMAIN-ARCHITECTURE.md) - Architecture and design
- [ECO Domain](./ECO-DOMAIN-ARCHITECTURE.md) - Infrastructure and resources
- [BNI Domain](./BNI-DOMAIN-ARCHITECTURE.md) - Business services

## Support

### Resources
- **Documentation**: https://docs.bsw-tech.org/iv/
- **GitHub**: https://github.com/bsw-arch/bsw-arch
- **Codeberg**: https://codeberg.org/bsw-tech/iv-bots (primary)

### Contributing
- Follow the [contribution guidelines](../../../CONTRIBUTING.md)
- Use the [bot template](../../../templates/bot/IV-BOT-TEMPLATE.md)
- Submit PRs to the `develop` branch
- Include tests and documentation

---

*IV Domain Architecture v1.0.0*
*BSW-Arch Bot Factory*
*Last Updated: 2025-11-11*
