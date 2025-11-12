# CAG+RAG Integration Guide for BSW-Arch Bots

> How to integrate the CAG+RAG system with BSW-Arch bot factory bots

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Target Audience**: Bot Developers

## Overview

This guide shows how to integrate the 2-tier CAG+RAG system with bots in the BSW-Arch factory. The system provides intelligent, context-aware query processing across all domains.

## Integration Points

### 1. Direct API Integration

Use the MCP Server API to send queries and receive contextual responses.

#### Python Client Example

```python
#!/usr/bin/env python3
"""
Example: ECO monitoring bot using CAG+RAG
"""

import httpx
import asyncio

class CAGRAGClient:
    """Client for CAG+RAG MCP Server"""

    def __init__(self, endpoint: str = "http://localhost:8000"):
        self.endpoint = endpoint
        self.client = httpx.AsyncClient()

    async def query(self,
                   query: str,
                   user_id: str,
                   session_id: str,
                   domains: list = None):
        """Send query to CAG+RAG system"""

        request = {
            "query": query,
            "user_id": user_id,
            "session_id": session_id
        }

        if domains:
            request["domains"] = domains

        response = await self.client.post(
            f"{self.endpoint}/api/v1/query",
            json=request
        )

        return response.json()

    async def close(self):
        await self.client.aclose()


async def main():
    """Example usage in ECO bot"""

    client = CAGRAGClient(endpoint="http://cag-rag-service:8000")

    # Query for resource optimization
    response = await client.query(
        query="What are the current resource optimization opportunities?",
        user_id="eco-monitoring-bot",
        session_id="monitoring-session-123",
        domains=["ECO"]
    )

    print(f"Response: {response['response']}")
    print(f"Confidence: {response['confidence']}")
    print(f"Sources: {response['sources']}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Environment Configuration

Add CAG+RAG endpoint to bot configuration:

```yaml
# bot-config.yaml
cag_rag:
  endpoint: "http://cag-rag-service:8000"
  timeout: 30
  retry_attempts: 3
```

### 3. Documentation Integration

Combine CAG+RAG with documentation scanner:

```python
import sys
sys.path.insert(0, "/opt/documentation/bot-utils")

from doc_scanner import DocScanner
from cag_rag_client import CAGRAGClient

# Initialize
scanner = DocScanner("/opt/documentation")
cag_rag = CAGRAGClient()

# Get domain docs
eco_docs = scanner.get_documents_by_domain("ECO")

# Query CAG+RAG with context
response = await cag_rag.query(
    query="How do I optimize container resources?",
    user_id="eco-bot",
    session_id="session-123",
    domains=["ECO"],
    context={
        "available_docs": [doc['id'] for doc in eco_docs],
        "bot_domain": "ECO"
    }
)
```

## Domain-Specific Integration

### AXIS Bots (Architecture)

```python
# Example: AXIS architecture bot
response = await cag_rag.query(
    query="Generate a system architecture for microservices deployment",
    user_id="axis-architect-bot",
    session_id="design-session-456",
    domains=["AXIS", "ECO"],  # Architecture + Infrastructure
    context={
        "project_type": "microservices",
        "scale": "medium",
        "requirements": ["high-availability", "auto-scaling"]
    }
)

# Response will include:
# - Architecture patterns
# - Component designs
# - Infrastructure requirements
```

### PIPE Bots (Pipeline)

```python
# Example: PIPE deployment bot
response = await cag_rag.query(
    query="What's the recommended CI/CD pipeline for containerized apps?",
    user_id="pipe-deploy-bot",
    session_id="pipeline-789",
    domains=["PIPE", "ECO"],  # Pipeline + Infrastructure
    context={
        "container_platform": "kubernetes",
        "git_platform": "codeberg",
        "build_tool": "apko"
    }
)

# Response will include:
# - Pipeline stages
# - Container build steps
# - Deployment strategies
```

### ECO Bots (Ecological)

```python
# Example: ECO monitoring bot
response = await cag_rag.query(
    query="Analyze current resource usage and suggest optimizations",
    user_id="eco-monitoring-bot",
    session_id="monitoring-123",
    domains=["ECO"],
    context={
        "current_metrics": {
            "cpu_usage": 75,
            "memory_usage": 60,
            "pod_count": 48
        },
        "cluster_capacity": {
            "total_cpu": "100",
            "total_memory": "200Gi"
        }
    }
)

# Response will include:
# - Resource optimization suggestions
# - Scaling recommendations
# - Cost reduction opportunities
```

### IV Bots (Intelligence/Validation)

```python
# Example: IV validation bot
response = await cag_rag.query(
    query="Validate this ML model architecture for production",
    user_id="iv-validation-bot",
    session_id="validation-321",
    domains=["IV", "ECO"],  # Intelligence + Infrastructure
    context={
        "model_type": "transformer",
        "inference_requirements": {
            "latency_target": "100ms",
            "throughput": "1000 req/s"
        }
    }
)

# Response will include:
# - Validation results
# - Performance predictions
# - Infrastructure recommendations
```

## Best Practices

### 1. Session Management

```python
# Use consistent session IDs for related queries
session_id = f"{bot_name}-{task_id}-{timestamp}"

# This helps CAG layer build better context
response1 = await cag_rag.query(..., session_id=session_id)
response2 = await cag_rag.query(..., session_id=session_id)  # Reuses context
```

### 2. Domain Selection

```python
# Be specific with domains
domains = ["ECO"]  # Single domain for focused queries

# Or multi-domain for cross-cutting concerns
domains = ["ECO", "PIPE"]  # Infrastructure + Deployment
```

### 3. Context Enrichment

```python
# Provide rich context for better responses
context = {
    "bot_domain": "ECO",
    "bot_category": "monitoring",
    "current_state": {...},
    "constraints": [...],
    "preferences": [...]
}

response = await cag_rag.query(..., context=context)
```

### 4. Error Handling

```python
import asyncio
from httpx import HTTPError, TimeoutException

async def query_with_retry(client, query, max_retries=3):
    """Query with exponential backoff"""

    for attempt in range(max_retries):
        try:
            return await client.query(query)

        except TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise

        except HTTPError as e:
            if e.response.status_code >= 500:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
            raise
```

## Deployment Configuration

### Kubernetes Service Discovery

```yaml
# bot-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eco-monitoring-bot
spec:
  template:
    spec:
      containers:
      - name: bot
        env:
        - name: CAG_RAG_ENDPOINT
          value: "http://cag-rag-service.cag-rag.svc.cluster.local:8000"
```

### Docker Compose Networking

```yaml
# docker-compose.yaml
services:
  eco-bot:
    environment:
      - CAG_RAG_ENDPOINT=http://mcp-server:8000
    networks:
      - cag-rag-network

networks:
  cag-rag-network:
    external: true
    name: bsw-cag-rag-network
```

## Monitoring Integration

### Track CAG+RAG Metrics

```python
from prometheus_client import Counter, Histogram

# Define metrics
cag_rag_queries = Counter(
    'bot_cag_rag_queries_total',
    'Total CAG+RAG queries',
    ['bot_name', 'domain']
)

cag_rag_latency = Histogram(
    'bot_cag_rag_latency_seconds',
    'CAG+RAG query latency',
    ['bot_name']
)

# Use in bot
async def query_with_metrics(client, query, bot_name, domains):
    with cag_rag_latency.labels(bot_name=bot_name).time():
        response = await client.query(query, domains=domains)

    for domain in domains:
        cag_rag_queries.labels(bot_name=bot_name, domain=domain).inc()

    return response
```

## Testing

### Unit Test Example

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_cag_rag_integration():
    """Test bot integration with CAG+RAG"""

    # Mock CAG+RAG client
    mock_client = AsyncMock()
    mock_client.query.return_value = {
        "response": "Mock response",
        "confidence": 0.9,
        "sources": [{"domain": "ECO"}]
    }

    # Test bot query
    with patch('cag_rag_client.CAGRAGClient', return_value=mock_client):
        result = await my_bot_function()

        assert result is not None
        mock_client.query.assert_called_once()
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_real_cag_rag_integration():
    """Test real integration with CAG+RAG service"""

    # Requires running CAG+RAG service
    client = CAGRAGClient(endpoint="http://localhost:8000")

    response = await client.query(
        query="Test query",
        user_id="test_user",
        session_id="test_session",
        domains=["ECO"]
    )

    assert "response" in response
    assert "confidence" in response
    assert response["confidence"] > 0

    await client.close()
```

## Troubleshooting

### Connection Issues

```python
# Check CAG+RAG service health
async def check_cag_rag_health(endpoint):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{endpoint}/health")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"CAG+RAG health check failed: {e}")
        return False
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add request/response logging
client = CAGRAGClient(endpoint="...")
client.client.event_hooks = {
    'request': [lambda r: print(f"REQUEST: {r.method} {r.url}")],
    'response': [lambda r: print(f"RESPONSE: {r.status_code}")]
}
```

## References

- [CAG+RAG Implementation Guide](../../architecture/components/cag-rag/2-TIER-CAG-RAG-IMPLEMENTATION-GUIDE.md)
- [CAG+RAG System README](../../../cag-rag-system/README.md)
- [MCP Server API](../../reference/apis/cag-rag-api.md)

---

**Maintained by**: BSW-Tech Architecture Team
**Component**: CAG+RAG Integration
**Version**: 1.0.0
**Last Updated**: 2025-11-10
