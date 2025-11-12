# BSW-Arch CAG+RAG System

> 2-Tier Context-Aware Generation + Retrieval-Augmented Generation for Bot Factory

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Status**: Implementation Ready

## Overview

This directory contains the implementation of a 2-tier CAG+RAG system for the BSW-Arch bot factory. The system provides intelligent, context-aware query processing and response generation across all bot domains (AXIS, PIPE, ECO, IV).

## Architecture

```
CAG Layer (Context-Aware Generation)
  ├── Context Manager: User history and preferences
  ├── Query Classifier: NLP-based query understanding
  └── Domain Router: Multi-domain routing

RAG Layer (Retrieval-Augmented Generation)
  ├── Vector Search: FAISS semantic similarity
  ├── Graph Search: Neo4j relationship traversal
  ├── Document Search: MongoDB full-text
  └── Knowledge Fusion: Multi-source fusion

MCP Server (Integration Layer)
  └── FastAPI unified API
```

## Directory Structure

```
cag-rag-system/
├── cag/                    # CAG Layer implementations
│   ├── context_manager.py
│   ├── query_classifier.py
│   └── domain_router.py
├── rag/                    # RAG Layer implementations
│   ├── hybrid_retrieval_engine.py
│   └── knowledge_fusion_engine.py
├── mcp/                    # MCP Server
│   └── mcp_server.py
├── tests/                  # Test suites
│   ├── unit/
│   ├── integration/
│   └── load/
├── config/                 # Configuration files
│   └── cag-rag-config.yaml
└── README.md
```

## Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Install dependencies
pip install fastapi uvicorn pydantic redis motor neo4j faiss-cpu

# Optional: For NLP classification
pip install transformers torch
```

### Run MCP Server

```bash
# Basic run
python mcp/mcp_server.py

# With custom host/port
python mcp/mcp_server.py --host 0.0.0.0 --port 8000

# Access API docs
open http://localhost:8000/docs
```

### Test Query

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I optimize resource usage in the ECO domain?",
    "user_id": "test_user",
    "session_id": "test_session"
  }'

# Using Python
python -c "
import requests
response = requests.post('http://localhost:8000/api/v1/query', json={
    'query': 'How do I optimize resource usage in the ECO domain?',
    'user_id': 'test_user',
    'session_id': 'test_session'
})
print(response.json())
"
```

## API Endpoints

### POST /api/v1/query
Process a CAG+RAG query

**Request**:
```json
{
  "query": "How do I deploy containers in the ECO domain?",
  "user_id": "user123",
  "session_id": "session456",
  "domains": ["ECO", "PIPE"]  // Optional
}
```

**Response**:
```json
{
  "response": "To deploy containers in the ECO domain...",
  "metadata": {
    "query_type": "informational",
    "domains": ["ECO", "PIPE"],
    "processing_time": 0.5
  },
  "sources": [
    {
      "domain": "ECO",
      "type": "bot_factory",
      "confidence": 0.85
    }
  ],
  "confidence": 0.85
}
```

### GET /health
Health check endpoint

### GET /api/v1/domains
Get available bot domains

### POST /api/v1/classify
Classify a query without generating response

## Components

### CAG Layer

#### Context Manager (`cag/context_manager.py`)
- Manages user context and history
- Analyzes domain preferences
- Caches context in Redis

**Usage**:
```python
from context_manager import ContextManager

manager = ContextManager()
context = await manager.build_context(
    user_id="user123",
    session_id="session456",
    query="How do I deploy?"
)
```

#### Query Classifier (`cag/query_classifier.py`)
- Classifies query types (analytical, transactional, etc.)
- Detects target domains using NLP and patterns
- Supports both transformer-based and rule-based classification

**Usage**:
```python
from query_classifier import QueryClassifier

classifier = QueryClassifier()
query_type, domains = await classifier.classify_query(
    query="How do I optimize ECO resources?",
    context=context
)
```

### MCP Server (`mcp/mcp_server.py`)
- FastAPI-based unified API
- Integrates CAG and RAG layers
- Handles routing to bot domains

## Configuration

### Environment Variables

```bash
# Redis (Context caching)
export REDIS_URL="redis://localhost:6379"

# PostgreSQL (User data)
export POSTGRES_URL="postgresql://user:pass@localhost:5432/cag_db"

# Neo4j (Knowledge graph)
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"

# MongoDB (Document store)
export MONGODB_URI="mongodb://localhost:27017"

# MCP Server
export MCP_HOST="0.0.0.0"
export MCP_PORT="8000"
```

### Configuration File (`config/cag-rag-config.yaml`)

```yaml
cag:
  context_ttl: 3600
  max_history_items: 10

rag:
  embedding_model: "all-MiniLM-L6-v2"
  top_k: 10

domains:
  AXIS:
    endpoint: "http://axis-orchestrator:8000"
  PIPE:
    endpoint: "http://pipe-orchestrator:8000"
  ECO:
    endpoint: "http://eco-orchestrator:8000"
  IV:
    endpoint: "http://iv-orchestrator:8000"
```

## Integration with Bot Factory

### ECO Bots Integration

```python
# Example: ECO monitoring bot using CAG+RAG
from mcp.mcp_client import CAGRAGClient

client = CAGRAGClient(endpoint="http://localhost:8000")

response = await client.query(
    query="What are current resource optimization opportunities?",
    user_id="eco-monitoring-bot",
    session_id="monitoring-123",
    domains=["ECO"],
    context={
        "bot_domain": "ECO",
        "bot_name": "eco-monitoring-bot"
    }
)

print(f"Response: {response.response}")
print(f"Confidence: {response.confidence}")
```

### Documentation Access

The CAG+RAG system integrates with `doc_scanner.py`:

```python
# In bot code
import sys
sys.path.insert(0, "/opt/documentation/bot-utils")

from doc_scanner import DocScanner
scanner = DocScanner("/opt/documentation")

# Get domain-specific docs
eco_docs = scanner.get_documents_by_domain("ECO")

# Use with CAG+RAG for enhanced responses
```

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ --cov=cag_rag --cov-report=html
```

### Adding New Domain Patterns

```python
from cag.query_classifier import QueryClassifier

classifier = QueryClassifier()

# Add pattern for new domain
classifier.add_domain_pattern(
    domain="ECO",
    pattern=r"\b(resource|infrastructure|monitoring)\b"
)
```

### Extending Query Types

Edit `cag/query_classifier.py` to add new `QueryType` enum values and corresponding patterns.

## Deployment

### Docker

```bash
# Build image
docker build -t cag-rag-system:latest .

# Run container
docker run -p 8000:8000 \
  -e REDIS_URL=redis://redis:6379 \
  cag-rag-system:latest
```

### Kubernetes

```bash
# Deploy to cluster
kubectl apply -f ../docs/templates/cag-rag/deployment/

# Check status
kubectl get pods -n cag-rag
kubectl logs -f deployment/cag-rag-system -n cag-rag
```

### Docker Compose

```bash
# Start all services (MCP, Redis, Postgres, Neo4j, MongoDB)
docker-compose -f ../docs/templates/cag-rag/docker-compose.yaml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f mcp-server
```

## Monitoring

### Metrics

The system exposes Prometheus metrics:

```
cag_query_latency_seconds
cag_query_total
cag_context_cache_hit_rate
rag_retrieval_latency_seconds
mcp_request_duration_seconds
```

Access metrics: `http://localhost:8000/metrics`

### Health Check

```bash
curl http://localhost:8000/health
```

## Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Query Latency (p50) | <1s | Typical query processing |
| Query Latency (p99) | <3s | Complex multi-domain queries |
| Throughput | 100 req/s | Per server instance |
| Cache Hit Rate | >70% | Context and result caching |

## Troubleshooting

### Server won't start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep -E "(fastapi|uvicorn|pydantic)"

# Check ports
lsof -i :8000
```

### Queries timing out

```bash
# Check Redis connection
redis-cli ping

# Check domain endpoints
curl http://localhost:8000/api/v1/domains

# Review logs
tail -f /var/log/cag-rag/server.log
```

### Classification not working

```bash
# Install transformers (optional but recommended)
pip install transformers torch

# Fallback to rule-based works without transformers
```

## References

- [Implementation Guide](../docs/architecture/components/cag-rag/2-TIER-CAG-RAG-IMPLEMENTATION-GUIDE.md)
- [Bot Factory Architecture](../docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md)
- [ECO Bots Documentation](../eco-bots/README.md)

## Support

- **GitHub Issues**: https://github.com/bsw-arch/bsw-arch/issues
- **Documentation**: `/docs/architecture/components/cag-rag/`
- **Component Label**: `component:cag-rag`

---

**Maintained by**: BSW-Tech Architecture Team
**Component**: CAG+RAG System
**Version**: 1.0.0
**Last Updated**: 2025-11-10
