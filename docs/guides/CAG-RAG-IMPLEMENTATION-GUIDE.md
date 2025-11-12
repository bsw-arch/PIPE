# How to Build the 2-Tier CAG+RAG System
## Step-by-Step Implementation Guide

### Version 1.0 | November 2024

---

## Executive Summary

This guide provides practical, step-by-step instructions for building the complete 2-tier CAG+RAG system from the ground up. Whether you're starting from scratch or integrating into existing infrastructure, this guide will walk you through every stage of implementation.

### What You'll Build:
- **Complete CAG Layer** - Context-aware generation with domain routing
- **Full RAG Layer** - Hybrid retrieval with vector, graph, and document stores
- **8-Domain Integration** - PIPE, IV, AXIS, BNI, BNP, ECO, DC, BU
- **Production-Ready System** - Monitoring, security, compliance

### Time to Complete: 12-16 weeks

---

## Table of Contents

1. [Prerequisites & Environment Setup](#1-prerequisites--environment-setup)
2. [Phase 1: Foundation Infrastructure](#2-phase-1-foundation-infrastructure)
3. [Phase 2: CAG Layer Implementation](#3-phase-2-cag-layer-implementation)
4. [Phase 3: RAG Layer Implementation](#4-phase-3-rag-layer-implementation)
5. [Phase 4: Domain Integration](#5-phase-4-domain-integration)
6. [Phase 5: Testing & Validation](#6-phase-5-testing--validation)
7. [Phase 6: Production Deployment](#7-phase-6-production-deployment)
8. [Troubleshooting Guide](#8-troubleshooting-guide)

---

## 1. Prerequisites & Environment Setup

### 1.1 Development Environment

**Required Software:**
```bash
# Development tools
sudo apt-get update
sudo apt-get install -y \
    git \
    python3.11 \
    python3-pip \
    docker.io \
    docker-compose \
    kubectl \
    helm

# Verify installations
python3 --version  # Should be 3.11+
docker --version   # Should be 20.10+
kubectl version    # Should be 1.28+
```

**Python Dependencies:**
```bash
# Create virtual environment
python3 -m venv cag-rag-env
source cag-rag-env/bin/activate

# Install core dependencies
pip install --upgrade pip
pip install \
    fastapi==0.104.0 \
    uvicorn[standard]==0.24.0 \
    langchain==0.1.0 \
    sentence-transformers==2.2.2 \
    faiss-cpu==1.7.4 \
    neo4j==5.14.0 \
    motor==3.3.2 \
    aiokafka==0.9.0 \
    redis==5.0.1 \
    prometheus-client==0.19.0 \
    pydantic==2.5.0
```

### 1.2 Infrastructure Requirements

**Minimum Hardware:**
- CPU: 8 cores
- RAM: 32GB
- Storage: 500GB SSD
- Network: 1Gbps

**Recommended Hardware:**
- CPU: 16+ cores
- RAM: 64GB+
- Storage: 1TB+ NVMe SSD
- Network: 10Gbps

**Cloud Alternative:**
- 4x c6i.2xlarge instances (AWS equivalent)
- 500GB gp3 storage per instance
- VPC with private subnets

### 1.3 Clone Repository

```bash
# Clone the documentation repository
git clone https://github.com/bsw-arch/bsw-arch.git
cd bsw-arch

# Review architecture documentation
cd docs
ls -la architecture/  # Review architecture docs
ls -la guides/        # Review implementation guides
```

---

## 2. Phase 1: Foundation Infrastructure

**Duration: Weeks 1-2**

### 2.1 Set Up Kubernetes Cluster

```bash
# Option 1: Local development with k3d
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
k3d cluster create cag-rag-cluster \
    --servers 1 \
    --agents 3 \
    --port 8080:80@loadbalancer

# Option 2: Production with kubeadm
# Follow: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/

# Verify cluster
kubectl get nodes
kubectl get pods --all-namespaces
```

### 2.2 Deploy Storage Systems

**Step 1: Deploy PostgreSQL**
```bash
# Create namespace
kubectl create namespace cag-rag

# Deploy PostgreSQL using Helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
    --namespace cag-rag \
    --set auth.postgresPassword=changeme \
    --set primary.persistence.size=50Gi

# Verify
kubectl get pods -n cag-rag -l app.kubernetes.io/name=postgresql
```

**Step 2: Deploy MongoDB**
```bash
# Deploy MongoDB
helm install mongodb bitnami/mongodb \
    --namespace cag-rag \
    --set auth.rootPassword=changeme \
    --set persistence.size=100Gi \
    --set architecture=replicaset \
    --set replicaCount=3

# Verify
kubectl get pods -n cag-rag -l app.kubernetes.io/name=mongodb
```

**Step 3: Deploy Neo4j**
```bash
# Create Neo4j deployment
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: neo4j
  namespace: cag-rag
spec:
  serviceName: neo4j
  replicas: 1
  selector:
    matchLabels:
      app: neo4j
  template:
    metadata:
      labels:
        app: neo4j
    spec:
      containers:
      - name: neo4j
        image: neo4j:5-community
        ports:
        - containerPort: 7474
          name: http
        - containerPort: 7687
          name: bolt
        env:
        - name: NEO4J_AUTH
          value: neo4j/changeme
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: neo4j
  namespace: cag-rag
spec:
  ports:
  - port: 7474
    name: http
  - port: 7687
    name: bolt
  selector:
    app: neo4j
EOF

# Verify
kubectl get pods -n cag-rag -l app=neo4j
```

**Step 4: Deploy Redis**
```bash
# Deploy Redis cluster
helm install redis bitnami/redis \
    --namespace cag-rag \
    --set auth.password=changeme \
    --set cluster.enabled=true \
    --set cluster.slaveCount=2 \
    --set master.persistence.size=10Gi

# Verify
kubectl get pods -n cag-rag -l app.kubernetes.io/name=redis
```

**Step 5: Deploy Kafka**
```bash
# Deploy Kafka using Strimzi operator
kubectl create namespace kafka
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Create Kafka cluster
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: cag-rag-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
    storage:
      type: persistent-claim
      size: 100Gi
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

# Wait for cluster to be ready
kubectl wait kafka/cag-rag-kafka --for=condition=Ready --timeout=300s -n kafka
```

### 2.3 Verify Infrastructure

```bash
# Create verification script
cat > verify-infrastructure.sh <<'EOF'
#!/bin/bash

echo "=== Infrastructure Verification ==="

# Check PostgreSQL
echo "Checking PostgreSQL..."
kubectl exec -n cag-rag postgresql-0 -- psql -U postgres -c "SELECT version();"

# Check MongoDB
echo "Checking MongoDB..."
kubectl exec -n cag-rag mongodb-0 -- mongosh --eval "db.version()"

# Check Neo4j
echo "Checking Neo4j..."
kubectl exec -n cag-rag neo4j-0 -- cypher-shell -u neo4j -p changeme "RETURN 1;"

# Check Redis
echo "Checking Redis..."
kubectl exec -n cag-rag redis-master-0 -- redis-cli -a changeme PING

# Check Kafka
echo "Checking Kafka..."
kubectl get kafka -n kafka cag-rag-kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'

echo "=== Verification Complete ==="
EOF

chmod +x verify-infrastructure.sh
./verify-infrastructure.sh
```

---

## 3. Phase 2: CAG Layer Implementation

**Duration: Weeks 3-5**

### 3.1 Create CAG Service

**Step 1: Create Project Structure**
```bash
mkdir -p cag-service/{src,tests,config}
cd cag-service

# Create requirements.txt
cat > requirements.txt <<EOF
fastapi==0.104.0
uvicorn[standard]==0.24.0
pydantic==2.5.0
asyncpg==0.29.0
aioredis==2.0.1
aiokafka==0.9.0
python-jose==3.3.0
python-multipart==0.0.6
prometheus-fastapi-instrumentator==6.1.0
EOF

pip install -r requirements.txt
```

**Step 2: Implement Context Manager**
```python
# src/context_manager.py
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import asyncpg
import json

@dataclass
class UserContext:
    """User context for CAG processing"""
    user_id: str
    session_id: str
    domain_preferences: List[str]
    interaction_history: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class ContextManager:
    """Manages context for CAG layer"""

    def __init__(self, db_url: str, redis_url: str):
        self.db_url = db_url
        self.redis_url = redis_url
        self.db_pool = None
        self.redis = None

    async def initialize(self):
        """Initialize database connections"""
        self.db_pool = await asyncpg.create_pool(self.db_url)
        # Redis connection setup here

    async def build_context(self,
                           user_id: str,
                           session_id: str,
                           query: str) -> UserContext:
        """Build comprehensive context"""

        # Get user history from database
        history = await self._get_user_history(user_id)

        # Analyse domain preferences
        preferences = await self._analyse_preferences(user_id, history)

        # Build metadata
        metadata = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'session_id': session_id
        }

        return UserContext(
            user_id=user_id,
            session_id=session_id,
            domain_preferences=preferences,
            interaction_history=history[-10:],
            metadata=metadata
        )

    async def _get_user_history(self, user_id: str) -> List[Dict]:
        """Retrieve user history from database"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM user_interactions
                WHERE user_id = $1
                ORDER BY timestamp DESC
                LIMIT 50
                """,
                user_id
            )
            return [dict(row) for row in rows]

    async def _analyse_preferences(self,
                                  user_id: str,
                                  history: List[Dict]) -> List[str]:
        """Analyse domain preferences"""
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

**Step 3: Implement Query Classifier**
```python
# src/query_classifier.py
from typing import Tuple, List
from enum import Enum
import re

class QueryType(Enum):
    ANALYTICAL = "analytical"
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    GENERATIVE = "generative"

class QueryClassifier:
    """Classifies queries for routing"""

    def __init__(self):
        self.domain_patterns = {
            'PIPE': [
                re.compile(r'\bapi\b', re.I),
                re.compile(r'\bintegration\b', re.I),
            ],
            'IV': [
                re.compile(r'\bllm\b', re.I),
                re.compile(r'\brag\b', re.I),
            ],
            'AXIS': [
                re.compile(r'\barchitecture\b', re.I),
                re.compile(r'\bdesign\b', re.I),
            ]
        }

    async def classify_query(self,
                            query: str,
                            context: 'UserContext') -> Tuple[QueryType, List[str]]:
        """Classify query and detect target domains"""

        # Classify type
        query_type = self._classify_type(query)

        # Detect domains
        domains = self._detect_domains(query, context)

        return query_type, domains

    def _classify_type(self, query: str) -> QueryType:
        """Classify query type"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['how', 'why', 'explain']):
            return QueryType.INFORMATIONAL
        elif any(word in query_lower for word in ['create', 'generate', 'build']):
            return QueryType.GENERATIVE
        elif any(word in query_lower for word in ['analyse', 'compare', 'evaluate']):
            return QueryType.ANALYTICAL
        else:
            return QueryType.TRANSACTIONAL

    def _detect_domains(self, query: str, context) -> List[str]:
        """Detect relevant domains"""
        detected = []

        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if pattern.search(query):
                    detected.append(domain)
                    break

        # Use context preferences if no domains detected
        if not detected and context.domain_preferences:
            detected = context.domain_preferences[:2]

        return detected or ['PIPE']
```

**Step 4: Create CAG API**
```python
# src/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio

from context_manager import ContextManager
from query_classifier import QueryClassifier

app = FastAPI(title="CAG Layer API")

# Initialize components
context_manager = None
query_classifier = None

class QueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: str
    domains: Optional[List[str]] = None

class QueryResponse(BaseModel):
    query_type: str
    target_domains: List[str]
    context: Dict[str, Any]
    processing_time: float

@app.on_event("startup")
async def startup():
    global context_manager, query_classifier

    # Initialize context manager
    context_manager = ContextManager(
        db_url="postgresql://postgres:changeme@postgresql:5432/cag_db",
        redis_url="redis://redis:6379"
    )
    await context_manager.initialize()

    # Initialize classifier
    query_classifier = QueryClassifier()

@app.post("/api/v1/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process CAG query"""
    import time
    start_time = time.time()

    try:
        # Build context
        context = await context_manager.build_context(
            user_id=request.user_id,
            session_id=request.session_id,
            query=request.query
        )

        # Classify query
        query_type, target_domains = await query_classifier.classify_query(
            query=request.query,
            context=context
        )

        # Override with requested domains if provided
        if request.domains:
            target_domains = request.domains

        processing_time = time.time() - start_time

        return QueryResponse(
            query_type=query_type.value,
            target_domains=target_domains,
            context={
                'user_id': context.user_id,
                'session_id': context.session_id,
                'preferences': context.domain_preferences,
                'metadata': context.metadata
            },
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "cag-layer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Step 5: Deploy CAG Service**
```bash
# Create Dockerfile
cat > Dockerfile <<EOF
FROM cgr.dev/chainguard/python:latest-dev as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM cgr.dev/chainguard/python:latest
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src/ .
CMD ["python", "main.py"]
EOF

# Build and push
docker build -t cag-service:v1.0 .
docker tag cag-service:v1.0 your-registry/cag-service:v1.0
docker push your-registry/cag-service:v1.0

# Deploy to Kubernetes
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cag-service
  namespace: cag-rag
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cag-service
  template:
    metadata:
      labels:
        app: cag-service
    spec:
      containers:
      - name: cag-service
        image: your-registry/cag-service:v1.0
        ports:
        - containerPort: 8001
        env:
        - name: DB_URL
          value: postgresql://postgres:changeme@postgresql:5432/cag_db
        - name: REDIS_URL
          value: redis://redis:6379
---
apiVersion: v1
kind: Service
metadata:
  name: cag-service
  namespace: cag-rag
spec:
  selector:
    app: cag-service
  ports:
  - port: 8001
    targetPort: 8001
EOF
```

---

## 4. Phase 3: RAG Layer Implementation

**Duration: Weeks 6-8**

### 4.1 Set Up Vector Store

**Step 1: Deploy FAISS Service**
```python
# rag-service/src/vector_store.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import pickle

class VectorStore:
    """FAISS-based vector store"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector store"""
        texts = [doc['text'] for doc in documents]

        # Generate embeddings
        embeddings = self.model.encode(texts)

        # Add to index
        self.index.add(embeddings.astype('float32'))

        # Store metadata
        self.metadata.extend(documents)

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search similar documents"""
        # Generate query embedding
        query_embedding = self.model.encode([query])

        # Search
        distances, indices = self.index.search(
            query_embedding.astype('float32'),
            top_k
        )

        # Return results with metadata
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(1 / (1 + dist))
                result['rank'] = i + 1
                results.append(result)

        return results

    def save(self, path: str):
        """Save index to disk"""
        faiss.write_index(self.index, f"{path}/index.faiss")
        with open(f"{path}/metadata.pkl", 'wb') as f:
            pickle.dump(self.metadata, f)

    def load(self, path: str):
        """Load index from disk"""
        self.index = faiss.read_index(f"{path}/index.faiss")
        with open(f"{path}/metadata.pkl", 'rb') as f:
            self.metadata = pickle.load(f)
```

**Step 2: Implement Graph Store**
```python
# rag-service/src/graph_store.py
from neo4j import AsyncGraphDatabase
from typing import List, Dict, Any

class GraphStore:
    """Neo4j-based graph store"""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def add_knowledge(self,
                           entity: str,
                           entity_type: str,
                           properties: Dict[str, Any],
                           relations: List[Dict[str, Any]] = None):
        """Add knowledge to graph"""
        async with self.driver.session() as session:
            # Create entity node
            await session.run(
                f"""
                MERGE (e:{entity_type} {{name: $name}})
                SET e += $properties
                RETURN e
                """,
                name=entity,
                properties=properties
            )

            # Create relationships
            if relations:
                for relation in relations:
                    await session.run(
                        f"""
                        MATCH (a:{entity_type} {{name: $entity}})
                        MATCH (b:{{name: $related}})
                        MERGE (a)-[r:{relation['type']}]->(b)
                        SET r += $props
                        """,
                        entity=entity,
                        related=relation['target'],
                        props=relation.get('properties', {})
                    )

    async def search_graph(self,
                          query: str,
                          domain: str,
                          max_depth: int = 2) -> List[Dict[str, Any]]:
        """Search knowledge graph"""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (n:Entity {domain: $domain})
                WHERE n.name CONTAINS $query OR n.description CONTAINS $query
                OPTIONAL MATCH path = (n)-[*1..""" + str(max_depth) + """]->(related)
                RETURN n, relationships(path) as rels, nodes(path) as nodes
                LIMIT 10
                """,
                domain=domain,
                query=query
            )

            results = []
            async for record in result:
                node = record['n']
                results.append({
                    'entity': dict(node),
                    'relationships': record['rels'],
                    'connected_nodes': record['nodes']
                })

            return results

    async def close(self):
        """Close driver connection"""
        await self.driver.close()
```

**Step 3: Create Hybrid Retrieval Engine**
```python
# rag-service/src/hybrid_retrieval.py
from typing import List, Dict, Any
import asyncio
from vector_store import VectorStore
from graph_store import GraphStore

class HybridRetrievalEngine:
    """Combines vector, graph, and document search"""

    def __init__(self, config: Dict[str, Any]):
        self.vector_store = VectorStore()
        self.graph_store = GraphStore(
            uri=config['neo4j_uri'],
            user=config['neo4j_user'],
            password=config['neo4j_password']
        )

    async def hybrid_search(self,
                           query: str,
                           domain: str,
                           top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform hybrid search"""

        # Parallel retrieval
        vector_task = asyncio.create_task(
            self._vector_search(query, top_k)
        )
        graph_task = asyncio.create_task(
            self.graph_store.search_graph(query, domain, max_depth=2)
        )

        vector_results, graph_results = await asyncio.gather(
            vector_task, graph_task
        )

        # Fuse results
        fused = self._fuse_results(
            vector_results,
            graph_results,
            weights={'vector': 0.6, 'graph': 0.4}
        )

        return fused[:top_k]

    def _vector_search(self, query: str, top_k: int) -> List[Dict]:
        """Vector similarity search"""
        return self.vector_store.search(query, top_k * 2)

    def _fuse_results(self,
                     vector_results: List[Dict],
                     graph_results: List[Dict],
                     weights: Dict[str, float]) -> List[Dict]:
        """Fuse results from multiple sources"""
        all_results = {}

        # Process vector results
        for result in vector_results:
            key = result.get('id', result.get('text', '')[:50])
            all_results[key] = result.copy()
            all_results[key]['final_score'] = result['score'] * weights['vector']
            all_results[key]['type'] = 'vector'

        # Process graph results
        for result in graph_results:
            entity = result['entity']
            key = entity.get('name', str(entity))

            if key in all_results:
                all_results[key]['final_score'] += 0.5 * weights['graph']
            else:
                all_results[key] = {
                    'entity': entity,
                    'final_score': 0.5 * weights['graph'],
                    'type': 'graph'
                }

        # Sort by final score
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )

        return sorted_results
```

**Step 4: Deploy RAG Service**
```python
# rag-service/src/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from hybrid_retrieval import HybridRetrievalEngine

app = FastAPI(title="RAG Layer API")

# Initialize retrieval engine
retrieval_engine = None

class RetrievalRequest(BaseModel):
    query: str
    domain: str
    top_k: Optional[int] = 10

class RetrievalResponse(BaseModel):
    results: List[Dict[str, Any]]
    count: int
    processing_time: float

@app.on_event("startup")
async def startup():
    global retrieval_engine
    retrieval_engine = HybridRetrievalEngine({
        'neo4j_uri': 'bolt://neo4j:7687',
        'neo4j_user': 'neo4j',
        'neo4j_password': 'changeme'
    })

@app.post("/api/v1/retrieve", response_model=RetrievalResponse)
async def retrieve(request: RetrievalRequest):
    """Perform hybrid retrieval"""
    import time
    start_time = time.time()

    try:
        results = await retrieval_engine.hybrid_search(
            query=request.query,
            domain=request.domain,
            top_k=request.top_k
        )

        processing_time = time.time() - start_time

        return RetrievalResponse(
            results=results,
            count=len(results),
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-layer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

---

## 5. Phase 4: Domain Integration

**Duration: Weeks 9-12**

### 5.1 Create MCP Server

```python
# mcp-server/src/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import asyncio

app = FastAPI(title="CAG+RAG MCP Server")

class QueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: str
    domains: Optional[List[str]] = None

class QueryResponse(BaseModel):
    response: str
    metadata: Dict[str, Any]
    sources: List[Dict[str, Any]]
    confidence: float

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process complete CAG+RAG query"""

    try:
        # Step 1: CAG Processing
        async with httpx.AsyncClient() as client:
            cag_response = await client.post(
                "http://cag-service:8001/api/v1/process",
                json=request.dict()
            )
            cag_data = cag_response.json()

        # Step 2: RAG Retrieval for each domain
        retrieval_results = []
        for domain in cag_data['target_domains']:
            async with httpx.AsyncClient() as client:
                rag_response = await client.post(
                    "http://rag-service:8002/api/v1/retrieve",
                    json={
                        'query': request.query,
                        'domain': domain,
                        'top_k': 10
                    }
                )
                results = rag_response.json()
                retrieval_results.extend(results['results'])

        # Step 3: Generate response (simplified)
        response_text = await _generate_response(
            query=request.query,
            context=cag_data['context'],
            knowledge=retrieval_results
        )

        return QueryResponse(
            response=response_text,
            metadata={
                'query_type': cag_data['query_type'],
                'domains': cag_data['target_domains'],
                'processing_time': cag_data['processing_time']
            },
            sources=retrieval_results[:5],
            confidence=0.85
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_response(query: str,
                            context: Dict,
                            knowledge: List[Dict]) -> str:
    """Generate response using retrieved knowledge"""
    # This is a simplified version
    # In production, integrate with your LLM
    knowledge_text = "\n".join([
        k.get('text', str(k)) for k in knowledge[:5]
    ])

    return f"Based on the retrieved knowledge: {knowledge_text[:500]}..."

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-server"}
```

### 5.2 Deploy Complete Stack

```bash
# Deploy MCP Server
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: cag-rag
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: your-registry/mcp-server:v1.0
        ports:
        - containerPort: 8000
        env:
        - name: CAG_SERVICE_URL
          value: http://cag-service:8001
        - name: RAG_SERVICE_URL
          value: http://rag-service:8002
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
  namespace: cag-rag
spec:
  selector:
    app: mcp-server
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
EOF
```

---

## 6. Phase 5: Testing & Validation

**Duration: Weeks 13-14**

### 6.1 Integration Tests

```python
# tests/test_integration.py
import pytest
import httpx
import asyncio

BASE_URL = "http://mcp-server"

@pytest.mark.asyncio
async def test_complete_pipeline():
    """Test complete CAG+RAG pipeline"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "query": "How do I implement a CAG+RAG system?",
                "user_id": "test_user",
                "session_id": "test_session"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "metadata" in data
        assert "sources" in data
        assert len(data["sources"]) > 0

@pytest.mark.asyncio
async def test_domain_routing():
    """Test domain routing"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "query": "Tell me about PIPE architecture",
                "user_id": "test_user",
                "session_id": "test_session",
                "domains": ["PIPE"]
            }
        )

        data = response.json()
        assert "PIPE" in data["metadata"]["domains"]
```

### 6.2 Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py <<'EOF'
from locust import HttpUser, task, between

class CAGRAGUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def query_system(self):
        self.client.post("/api/v1/query", json={
            "query": "What is CAG+RAG?",
            "user_id": "load_test_user",
            "session_id": "load_test_session"
        })

EOF

# Run load test
locust -f locustfile.py --host=http://your-mcp-server
```

---

## 7. Phase 6: Production Deployment

**Duration: Weeks 15-16**

### 7.1 Production Checklist

```yaml
production_checklist:
  infrastructure:
    - [ ] Multi-zone Kubernetes cluster
    - [ ] Automated backups configured
    - [ ] Disaster recovery tested
    - [ ] Monitoring stack deployed
    - [ ] Alerting configured

  security:
    - [ ] TLS/SSL certificates installed
    - [ ] API authentication enabled
    - [ ] Network policies applied
    - [ ] Secrets management configured
    - [ ] GDPR compliance verified

  performance:
    - [ ] Load testing completed
    - [ ] Autoscaling configured
    - [ ] Caching optimised
    - [ ] Database indexes created
    - [ ] Query response time <2s

  operations:
    - [ ] Documentation complete
    - [ ] Runbooks created
    - [ ] On-call rotation established
    - [ ] Incident response plan ready
    - [ ] Training completed
```

### 7.2 Monitoring Setup

```bash
# Deploy Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace

# Deploy Grafana dashboards
kubectl apply -f monitoring/dashboards/
```

---

## 8. Troubleshooting Guide

### Common Issues

**Issue: CAG Service Not Starting**
```bash
# Check logs
kubectl logs -n cag-rag deployment/cag-service

# Common fixes:
# 1. Database connection
kubectl exec -it postgresql-0 -n cag-rag -- psql -U postgres

# 2. Redis connection
kubectl exec -it redis-master-0 -n cag-rag -- redis-cli PING
```

**Issue: Slow Query Response**
```bash
# Check resource usage
kubectl top pods -n cag-rag

# Check database performance
kubectl exec -it postgresql-0 -n cag-rag -- \
    psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Add indexes if needed
CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
```

**Issue: High Error Rate**
```bash
# Check error logs
kubectl logs -n cag-rag -l app=mcp-server --tail=100

# Check service health
kubectl get pods -n cag-rag
kubectl describe pod <pod-name> -n cag-rag
```

---

## Next Steps

After completing this implementation:

1. **Optimise Performance** - Profile and optimise bottlenecks
2. **Add Domains** - Integrate additional domains beyond PIPE, IV, AXIS
3. **Enhance AI** - Integrate advanced LLM models
4. **Scale Out** - Deploy to multi-region setup
5. **Continuous Improvement** - Monitor metrics and iterate

---

## Support & Resources

- **Documentation**: `/docs` directory in this repository
- **Architecture**: `docs/architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md`
- **Technical Guide**: `docs/guides/development/CAG-RAG-TECHNICAL-IMPLEMENTATION-GUIDE.md`
- **Data Guide**: `docs/architecture/DATA-ARCHITECTURE-GOVERNANCE-FRAMEWORK.md`
- **Issues**: https://github.com/bsw-arch/bsw-arch/issues

---

*Implementation Guide v1.0*
*Last Updated: November 2024*
*BSW-Tech Architecture Team*
