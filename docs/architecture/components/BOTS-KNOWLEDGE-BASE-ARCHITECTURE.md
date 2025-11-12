# BOTS Knowledge Base Architecture
## Comprehensive Multi-Domain Knowledge Management System

**Document Version**: 1.0
**Date**: 2025-11-10
**Author**: Claude Code (Sonnet 4.5)
**Classification**: Technical Architecture
**Status**: Design Complete - Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Recommended Architecture](#2-recommended-architecture)
3. [Implementation Plan](#3-implementation-plan)
4. [Directory Structure](#4-directory-structure)
5. [Bot Integration Pattern](#5-bot-integration-pattern)
6. [Auto-Sync Strategy](#6-auto-sync-strategy)
7. [Query Examples](#7-query-examples)
8. [Deployment Instructions](#8-deployment-instructions)
9. [Architecture Diagrams](#9-architecture-diagrams)
10. [Migration and Rollout](#10-migration-and-rollout)

---

## 1. Executive Summary

### 1.1 Challenge

The BSW enterprise architecture spans **4 AppVMs**, **4 primary domains** (AXIS, PIPE, IV, ECO), **253+ repositories**, and **30+ AI bots**. Current documentation is fragmented across:

- `/home/user/QubesIncoming/bsw-gov` (governance docs)
- `/home/user/Code/*/wiki/` (50+ bot wikis)
- Excel spreadsheets (6 data files)
- Codeberg wikis (distributed)
- CAG-KERAG-COGNEE documentation

**Bots need unified access** to all documentation for intelligent decision-making, but currently lack:
- ✗ Centralised knowledge repository
- ✗ Cross-domain knowledge discovery
- ✗ Real-time documentation updates
- ✗ Semantic search capabilities
- ✗ Version-controlled knowledge graph

### 1.2 Solution: Hybrid META-KERAGR Architecture

**Recommendation**: **Option D - Hybrid Approach** combining the best of all options:

```
┌─────────────────────────────────────────────────────────────────┐
│                  HYBRID META-KERAGR ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Git Repository Layer (Source of Truth)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  codeberg.org/BSW-Docs/bsw-documentation (Primary Repo)    │ │
│  │  • All markdown documentation                              │ │
│  │  • YAML knowledge base files                               │ │
│  │  • Excel → YAML conversions                                │ │
│  │  • Wiki consolidation from all 50+ bot repos               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  KERAGR Intelligence Layer (Smart Retrieval)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  2-Tier CAG+RAG System                                     │ │
│  │  ┌──────────────────┐  ┌──────────────────┐               │ │
│  │  │ TIER 1: CAG      │→ │ TIER 2: RAG      │               │ │
│  │  │ Context Manager  │  │ Hybrid Retrieval │               │ │
│  │  │ Query Classifier │  │ - Vector (FAISS) │               │ │
│  │  │ Domain Router    │  │ - Graph (Neo4j)  │               │ │
│  │  └──────────────────┘  │ - Docs (MongoDB) │               │ │
│  │                        └──────────────────┘               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  API Service Layer (Bot Access)                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  META-KERAGR REST API (localhost:3108)                     │ │
│  │  • RESTful endpoints for all bots                          │ │
│  │  • GraphQL interface for complex queries                   │ │
│  │  • WebSocket for real-time updates                         │ │
│  │  • Multi-domain access control                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↓                                     │
│  Bot Consumer Layer (Multi-Domain Access)                       │
│  ┌─────────┬─────────┬─────────┬─────────┬──────────────────┐ │
│  │  AXIS   │  PIPE   │   IV    │  ECO    │  All Other Bots  │ │
│  │  Bots   │  Bots   │  Bots   │  Bots   │  (30+ agents)    │ │
│  │  (30)   │  (46+)  │  (TBD)  │  (TBD)  │                  │ │
│  └─────────┴─────────┴─────────┴─────────┴──────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Benefits

| Benefit | Implementation |
|---------|----------------|
| **Single Source of Truth** | Git repository with version control |
| **Intelligent Retrieval** | KERAGR 2-tier CAG+RAG system |
| **Real-Time Sync** | Git webhooks + auto-update mechanisms |
| **Cross-Domain Access** | All bots access same knowledge via API |
| **Version Tracking** | Git history for all documentation changes |
| **Semantic Search** | Vector embeddings + knowledge graph |
| **Multi-Modal Support** | Markdown, YAML, converted Excel data |
| **Scalability** | Microservices architecture |

### 1.4 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Storage** | Git (Codeberg) + MongoDB | Source control + document storage |
| **Knowledge Graph** | Neo4j | Semantic relationships |
| **Vector Store** | FAISS | Similarity search |
| **API Layer** | FastAPI (Python 3.13) | REST + GraphQL + WebSocket |
| **CAG Engine** | LangChain + Custom | Context-aware generation |
| **RAG Engine** | Hybrid retrieval | Multi-source knowledge fusion |
| **Container** | Chainguard Wolfi | Minimal attack surface |
| **Orchestration** | Podman pods | Qubes OS compatible |

---

## 2. Recommended Architecture

### 2.1 Architecture Decision

**Selected: Option D - Hybrid Approach**

**Rationale**:

1. **Git as Source of Truth** (from Option B)
   - Version control for all documentation
   - Codeberg integration (European FOSS)
   - Branch strategy for different domains
   - Markdown + YAML for human readability
   - Excel data converted to structured YAML

2. **KERAGR for Intelligence** (from Option A)
   - 2-tier CAG+RAG system
   - Semantic search and knowledge graphs
   - Context-aware query processing
   - Multi-domain knowledge fusion
   - Confidence scoring

3. **API Service Layer** (from Option C)
   - REST API for simple queries
   - GraphQL for complex relationships
   - WebSocket for real-time updates
   - Multi-bot concurrent access
   - Access control per domain

4. **Wiki Integration** (from Option D)
   - Consolidate all 50+ bot wikis
   - Bidirectional sync with Codeberg wikis
   - Auto-generated documentation from code
   - Centralised search across all wikis

### 2.2 Component Architecture

#### 2.2.1 Layer 1: Git Repository (Source of Truth)

**Primary Repository**: `codeberg.org/BSW-Docs/bsw-documentation`

**Structure**:
```
bsw-documentation/
├── docs/                          # All markdown documentation
│   ├── architecture/              # Architecture docs from bsw-gov
│   ├── governance/                # SAFe governance documents
│   ├── domains/                   # Domain-specific docs
│   │   ├── AXIS/                  # AXIS domain documentation
│   │   ├── PIPE/                  # PIPE domain documentation
│   │   ├── IV/                    # IV domain documentation
│   │   └── ECO/                   # ECO domain documentation
│   ├── bots/                      # Bot-specific documentation
│   │   ├── axis/                  # 30 AXIS bot docs
│   │   ├── pipe/                  # 46+ PIPE bot docs
│   │   └── ...                    # Other bot docs
│   └── cag-kerag/                 # CAG-KERAG documentation
│
├── knowledge/                     # Structured knowledge base
│   ├── entities/                  # Knowledge graph entities (YAML)
│   ├── relationships/             # Entity relationships (YAML)
│   ├── taxonomies/                # Domain taxonomies
│   ├── patterns/                  # Architecture patterns
│   └── decisions/                 # Architecture Decision Records
│
├── data/                          # Converted Excel data
│   ├── pipelines.yaml             # From 2025 02 12 Pipelines.xlsx
│   ├── repos.yaml                 # From 2025 02 12 Repos.xlsx
│   ├── network-zones.yaml         # From IV_PIPE_Network_Zones.xlsx
│   └── pipe-matrix.yaml           # From pipe_matrix_structure.xlsx
│
├── wikis/                         # Consolidated bot wikis
│   ├── pipe-build-bot/            # From /home/user/Code/pipe-build-bot/wiki
│   ├── pipe-vault-bot/            # From /home/user/Code/pipe-vault-bot/wiki
│   ├── ECO-backup-bot/            # From /home/user/Code/ECO-backup-bot/wiki
│   └── ...                        # All 50+ bot wikis
│
├── schemas/                       # YAML schemas
│   ├── entity.schema.yaml
│   ├── relationship.schema.yaml
│   └── knowledge.schema.yaml
│
└── .github/workflows/             # Automation
    ├── sync-wikis.yaml            # Auto-sync from bot repos
    ├── validate-yaml.yaml         # Schema validation
    └── update-knowledge-graph.yaml # Neo4j update triggers
```

#### 2.2.2 Layer 2: KERAGR Intelligence System

**Service**: `meta-keragr-service` (Port 3108)

**Components**:

**A. CAG Layer (Tier 1)**

```python
# Context-Aware Generation Layer
class CAGLayer:
    components = {
        'context_manager': 'Tracks bot context, domain, and history',
        'query_classifier': 'Classifies queries by intent and domain',
        'domain_router': 'Routes to appropriate knowledge domains',
        'prompt_engineer': 'Generates optimal retrieval prompts'
    }

    def process_query(self, bot_id, query, context):
        """
        1. Build context from bot identity and history
        2. Classify query type (technical, governance, pattern, etc.)
        3. Identify target domains (AXIS, PIPE, IV, ECO)
        4. Engineer optimal retrieval prompts
        """
        pass
```

**B. RAG Layer (Tier 2)**

```python
# Retrieval-Augmented Generation Layer
class RAGLayer:
    stores = {
        'vector_store': 'FAISS (embeddings for semantic search)',
        'graph_store': 'Neo4j (knowledge graph relationships)',
        'document_store': 'MongoDB (full-text search)'
    }

    def hybrid_retrieval(self, engineered_prompts):
        """
        1. Vector search: Semantic similarity (FAISS)
        2. Graph traversal: Related concepts (Neo4j)
        3. Document search: Full-text queries (MongoDB)
        4. Knowledge fusion: Merge and rank results
        5. Confidence scoring: Assess result quality
        """
        pass
```

#### 2.2.3 Layer 3: API Service (META-KERAGR API)

**Service**: FastAPI application on port 3108

**Endpoints**:

**REST API**:
```python
# REST endpoints for simple queries
@app.get("/api/v1/knowledge/search")
async def search(
    query: str,
    domain: Optional[str] = None,
    bot_id: Optional[str] = None,
    limit: int = 10
):
    """Simple keyword search across all knowledge"""
    pass

@app.get("/api/v1/knowledge/entity/{entity_id}")
async def get_entity(entity_id: str):
    """Get specific entity with all relationships"""
    pass

@app.get("/api/v1/knowledge/domain/{domain}")
async def get_domain_knowledge(domain: str):
    """Get all knowledge for specific domain"""
    pass
```

**GraphQL API**:
```graphql
type Query {
  # Complex knowledge graph queries
  findRelatedConcepts(
    entityId: ID!
    depth: Int = 2
    relationTypes: [String]
  ): [Entity]

  # Cross-domain knowledge discovery
  discoverPatterns(
    domains: [String]
    pattern_type: String
  ): [Pattern]

  # Architecture decision lookup
  findADRs(
    status: String
    domains: [String]
  ): [ADR]
}
```

**WebSocket API**:
```python
@app.websocket("/ws/knowledge/updates")
async def knowledge_updates(websocket: WebSocket):
    """
    Real-time knowledge base updates
    Bots subscribe to get notified of new/changed docs
    """
    pass
```

#### 2.2.4 Layer 4: Bot Consumer Integration

**Bot SDK**: `bsw-knowledge-sdk` (Python library)

```python
# Example: axis-framework-bot using knowledge base
from bsw_knowledge_sdk import KnowledgeClient

client = KnowledgeClient(
    api_url="http://localhost:3108",
    bot_id="axis-framework-bot",
    domain="AXIS",
    auth_token=os.getenv("KNOWLEDGE_API_TOKEN")
)

# Simple query
results = await client.search(
    "How do I integrate with ARTEMIS platform?"
)

# Complex graph query
related_bots = await client.graph_query("""
    MATCH (bot:Bot)-[:INTEGRATES_WITH]->(platform:Platform {name: 'ARTEMIS'})
    RETURN bot.name, bot.api_endpoint
""")

# Subscribe to updates
await client.subscribe_to_updates(
    domains=["AXIS", "PIPE"],
    on_update=lambda doc: print(f"Updated: {doc.title}")
)
```

### 2.3 Data Flow Architecture

```mermaid
sequenceDiagram
    participant Bot as AXIS Bot
    participant SDK as Knowledge SDK
    participant API as META-KERAGR API
    participant CAG as CAG Layer
    participant RAG as RAG Layer
    participant Git as Git Repository
    participant Neo4j as Neo4j Graph
    participant FAISS as FAISS Vector
    participant Mongo as MongoDB

    Bot->>SDK: Query "How to deploy to K3s?"
    SDK->>API: POST /api/v1/knowledge/query
    API->>CAG: Build context + classify
    CAG->>RAG: Engineered prompts

    par Parallel Retrieval
        RAG->>FAISS: Vector search
        RAG->>Neo4j: Graph traversal
        RAG->>Mongo: Document search
    end

    RAG->>RAG: Fuse knowledge
    RAG->>API: Ranked results + confidence
    API->>SDK: JSON response
    SDK->>Bot: Structured knowledge

    Note over Git,Mongo: Auto-sync runs every 15 minutes
    Git->>Mongo: New docs detected
    Git->>Neo4j: Update knowledge graph
    Git->>FAISS: Regenerate embeddings
```

---

## 3. Implementation Plan

### 3.1 Phase 1: Foundation (Weeks 1-2)

#### Week 1: Repository and Data Migration

**Tasks**:
1. Create `codeberg.org/BSW-Docs/bsw-documentation` repository
2. Migrate all docs from `/home/user/QubesIncoming/bsw-gov`
3. Convert Excel files to YAML:
   - `pipelines.yaml` from `2025 02 12 Pipelines.xlsx`
   - `repos.yaml` from `2025 02 12 Repos.xlsx`
   - `network-zones.yaml` from `IV_PIPE_Network_Zones.xlsx`
   - `pipe-matrix.yaml` from `pipe_matrix_structure_full_updated.xlsx`
4. Create directory structure as specified in 2.2.1

**Deliverables**:
- ✅ Git repository created and structured
- ✅ All markdown docs committed
- ✅ Excel data converted to YAML
- ✅ Initial knowledge schema defined

**Scripts**:
```bash
# Create repository structure
/home/user/scripts/create-knowledge-repo.sh

# Convert Excel to YAML
/home/user/scripts/convert-excel-to-yaml.py

# Migrate documentation
/home/user/scripts/migrate-docs.sh
```

#### Week 2: Wiki Consolidation

**Tasks**:
1. Clone all 50+ bot wikis from `/home/user/Code/*/wiki`
2. Consolidate into `bsw-documentation/wikis/`
3. Create wiki sync automation
4. Set up bidirectional sync with Codeberg wikis

**Script**:
```bash
#!/bin/bash
# /home/user/scripts/consolidate-wikis.sh

WIKI_DIRS=(
    "/home/user/Code/pipe-build-bot/wiki"
    "/home/user/Code/pipe-vault-bot/wiki"
    "/home/user/Code/ECO-backup-bot/wiki"
    "/home/user/Code/axis-augment-models/wiki"
    # ... all 50+ wiki directories
)

for wiki in "${WIKI_DIRS[@]}"; do
    bot_name=$(basename $(dirname $wiki))
    echo "Consolidating $bot_name wiki..."

    mkdir -p ~/bsw-documentation/wikis/$bot_name
    rsync -av --exclude='.git' $wiki/ ~/bsw-documentation/wikis/$bot_name/

    # Create metadata file
    cat > ~/bsw-documentation/wikis/$bot_name/meta.yaml <<EOF
bot_name: $bot_name
source: $wiki
last_sync: $(date -Iseconds)
domain: $(detect_domain $bot_name)
EOF
done
```

### 3.2 Phase 2: Knowledge Graph Creation (Weeks 3-4)

#### Week 3: Neo4j Knowledge Graph Setup

**Tasks**:
1. Deploy Neo4j container (Chainguard Wolfi base)
2. Design knowledge graph schema:
   - Entities: Bot, Domain, Pattern, ADR, Service, API
   - Relationships: INTEGRATES_WITH, DEPENDS_ON, PART_OF, IMPLEMENTS
3. Create YAML → Neo4j import pipeline
4. Populate initial knowledge graph

**Neo4j Schema**:
```cypher
// Entity types
CREATE CONSTRAINT bot_name IF NOT EXISTS FOR (b:Bot) REQUIRE b.name IS UNIQUE;
CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT adr_id IF NOT EXISTS FOR (a:ADR) REQUIRE a.id IS UNIQUE;

// Example entities
CREATE (pipe:Domain {name: 'PIPE', services: 21, network: '10.100.1.0/24'})
CREATE (axis:Domain {name: 'AXIS', organizations: 14, repositories: 253})
CREATE (framework_bot:Bot {
    name: 'axis-framework-bot',
    domain: 'AXIS',
    api: 'http://localhost:8085/api/v1/framework',
    status: 'production'
})

// Relationships
CREATE (framework_bot)-[:PART_OF]->(axis)
CREATE (framework_bot)-[:INTEGRATES_WITH]->(:Platform {name: 'ARTEMIS'})
```

**YAML Entity Example**:
```yaml
# knowledge/entities/bots/axis-framework-bot.yaml
entity_type: Bot
name: axis-framework-bot
domain: AXIS
status: production
description: Framework detection and update management bot
capabilities:
  - framework_detection
  - python_compatibility_checking
  - configuration_validation
api:
  base_url: http://localhost:8085/api/v1/framework
  endpoints:
    - /detect
    - /check
    - /suggest
    - /health
integrations:
  - ARTEMIS
  - Codeberg
  - Git
dependencies:
  - Python 3.13
  - Git
  - Chainguard Wolfi
related_docs:
  - /docs/bots/axis/axis-framework-bot.md
  - /wikis/axis-framework-bot/
```

#### Week 4: Vector Store and Embeddings

**Tasks**:
1. Deploy FAISS vector store
2. Generate embeddings for all documentation
3. Create embedding pipeline for new docs
4. Test semantic search

**Embedding Pipeline**:
```python
# /home/user/scripts/generate-embeddings.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Use lightweight model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Process all markdown files
docs = load_all_markdown_docs('/home/user/bsw-documentation/docs')

# Generate embeddings
embeddings = []
for doc in docs:
    # Chunk documents (max 512 tokens)
    chunks = chunk_document(doc.content, max_tokens=512)
    for chunk in chunks:
        embedding = model.encode(chunk)
        embeddings.append({
            'doc_id': doc.id,
            'chunk_id': chunk.id,
            'embedding': embedding,
            'text': chunk.text,
            'metadata': {
                'domain': doc.domain,
                'bot': doc.bot,
                'file_path': doc.path
            }
        })

# Create FAISS index
dimension = 384  # all-MiniLM-L6-v2 dimension
index = faiss.IndexFlatL2(dimension)

# Add embeddings to index
vectors = np.array([e['embedding'] for e in embeddings]).astype('float32')
index.add(vectors)

# Save index
faiss.write_index(index, '/data/faiss/knowledge_base.index')

# Save metadata
save_json(embeddings, '/data/faiss/metadata.json')
```

### 3.3 Phase 3: CAG+RAG Implementation (Weeks 5-6)

#### Week 5: CAG Layer

**Tasks**:
1. Implement Context Manager
2. Implement Query Classifier
3. Implement Domain Router
4. Test context-aware query processing

**Implementation**: See existing code in `/home/user/QubesIncoming/bsw-gov/CAG - KERAG - COGNEE/cag-rag-technical-implementation-guide.md`

Use provided code examples with adaptations for multi-bot environment.

#### Week 6: RAG Layer

**Tasks**:
1. Implement Hybrid Retrieval Engine
2. Implement Knowledge Fusion Engine
3. Test multi-source retrieval
4. Benchmark performance

**Hybrid Retrieval**:
```python
# Adapted from technical guide
class MetaKERAGRRetrieval:
    async def hybrid_search(self, query, bot_context, domains):
        """
        Enhanced hybrid search for multi-bot environment
        """
        # 1. Vector search (FAISS)
        vector_results = await self.vector_search(
            query,
            filters={'domains': domains}
        )

        # 2. Graph search (Neo4j)
        graph_results = await self.graph_search(
            query,
            start_nodes={'bot': bot_context.bot_id},
            max_depth=2
        )

        # 3. Document search (MongoDB)
        doc_results = await self.document_search(
            query,
            collections=[f"{d}_docs" for d in domains]
        )

        # 4. Fuse and rank
        fused = await self.fuse_results(
            vector_results,
            graph_results,
            doc_results,
            weights={
                'vector': 0.4,
                'graph': 0.35,
                'document': 0.25
            }
        )

        return fused
```

### 3.4 Phase 4: API Service Development (Weeks 7-8)

#### Week 7: REST and GraphQL APIs

**Tasks**:
1. Implement FastAPI service
2. Create REST endpoints
3. Create GraphQL schema and resolvers
4. Add authentication and authorisation

**FastAPI Service**:
```python
# /home/user/services/meta-keragr-api/app.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter

app = FastAPI(title="META-KERAGR Knowledge API")

# REST endpoints
@app.get("/api/v1/knowledge/search")
async def search(
    query: str,
    domain: Optional[str] = None,
    bot_id: Optional[str] = None,
    limit: int = 10,
    token: str = Depends(verify_token)
):
    """Search knowledge base"""
    bot_context = get_bot_context(bot_id, token)

    results = await meta_keragr.hybrid_search(
        query=query,
        bot_context=bot_context,
        domains=[domain] if domain else bot_context.allowed_domains,
        limit=limit
    )

    return {
        'query': query,
        'results': results,
        'total': len(results),
        'confidence': calculate_avg_confidence(results)
    }

# GraphQL schema
@strawberry.type
class Bot:
    name: str
    domain: str
    api_endpoint: str
    status: str

@strawberry.type
class Query:
    @strawberry.field
    async def find_related_bots(self, bot_name: str, depth: int = 2) -> List[Bot]:
        """Find bots related via knowledge graph"""
        return await graph_db.find_related(bot_name, depth)

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

#### Week 8: WebSocket and SDK

**Tasks**:
1. Implement WebSocket for real-time updates
2. Create Python SDK for bots
3. Create TypeScript SDK (future Node.js bots)
4. Write SDK documentation

**Bot SDK**:
```python
# /home/user/packages/bsw-knowledge-sdk/client.py
import httpx
import websockets
import asyncio

class KnowledgeClient:
    def __init__(self, api_url, bot_id, domain, auth_token):
        self.api_url = api_url
        self.bot_id = bot_id
        self.domain = domain
        self.headers = {'Authorization': f'Bearer {auth_token}'}

    async def search(self, query: str, limit: int = 10):
        """Simple search"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/api/v1/knowledge/search",
                params={
                    'query': query,
                    'bot_id': self.bot_id,
                    'limit': limit
                },
                headers=self.headers
            )
            return response.json()

    async def graph_query(self, cypher: str):
        """Execute Cypher query"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/v1/knowledge/graph/query",
                json={'query': cypher},
                headers=self.headers
            )
            return response.json()

    async def subscribe_to_updates(self, domains, on_update):
        """Subscribe to real-time updates"""
        async with websockets.connect(
            f"{self.api_url.replace('http', 'ws')}/ws/knowledge/updates",
            extra_headers=self.headers
        ) as ws:
            await ws.send(json.dumps({
                'bot_id': self.bot_id,
                'domains': domains
            }))

            async for message in ws:
                data = json.loads(message)
                await on_update(data)
```

### 3.5 Phase 5: Integration and Testing (Weeks 9-10)

#### Week 9: Bot Integration

**Tasks**:
1. Integrate SDK with `axis-framework-bot`
2. Integrate SDK with `pipe-api-bot`
3. Test multi-bot concurrent access
4. Monitor performance

**Integration Example**:
```python
# In axis-framework-bot
from bsw_knowledge_sdk import KnowledgeClient

class FrameworkBot:
    def __init__(self):
        self.knowledge = KnowledgeClient(
            api_url=os.getenv('KNOWLEDGE_API_URL', 'http://localhost:3108'),
            bot_id='axis-framework-bot',
            domain='AXIS',
            auth_token=os.getenv('KNOWLEDGE_API_TOKEN')
        )

    async def check_framework_compatibility(self, framework, version):
        """Use knowledge base to check compatibility"""
        # Search for known compatibility issues
        issues = await self.knowledge.search(
            f"{framework} {version} compatibility issues"
        )

        # Query knowledge graph for dependencies
        deps = await self.knowledge.graph_query(f"""
            MATCH (f:Framework {{name: '{framework}', version: '{version}'}})-[:REQUIRES]->(d:Dependency)
            RETURN d.name, d.min_version, d.max_version
        """)

        return {
            'compatible': len(issues['results']) == 0,
            'issues': issues['results'],
            'dependencies': deps['results']
        }
```

#### Week 10: End-to-End Testing

**Test Scenarios**:

1. **Cross-Domain Query**:
   - AXIS bot queries PIPE documentation
   - Verify correct results returned
   - Check response time < 2 seconds

2. **Knowledge Graph Traversal**:
   - Query for all bots integrating with ARTEMIS
   - Verify complete relationship graph
   - Check accuracy of relationships

3. **Real-Time Updates**:
   - Update documentation in Git
   - Verify WebSocket notification
   - Confirm bots receive updates

4. **Concurrent Access**:
   - 10 bots query simultaneously
   - Verify no race conditions
   - Check consistent results

5. **Vector Search Quality**:
   - Query "How to deploy containers with apko?"
   - Verify relevant results from multiple domains
   - Check semantic relevance scores

---

## 4. Directory Structure

### 4.1 Git Repository Structure

```
codeberg.org/BSW-Docs/bsw-documentation/
│
├── README.md                           # Repository overview
├── CONTRIBUTING.md                     # Contribution guidelines
├── LICENSE                             # AGPL-3.0 license
│
├── docs/                               # Documentation root
│   │
│   ├── architecture/                   # Architecture documentation
│   │   ├── 2-tier-cag-rag-solution-architecture.md
│   │   ├── cag-rag-technical-implementation-guide.md
│   │   ├── BSW-GOV-NAMESPACE-ARCHITECTURE-DEPLOYMENT.md
│   │   ├── COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
│   │   └── ... (all architecture docs from bsw-gov)
│   │
│   ├── governance/                     # SAFe and governance
│   │   ├── safe-agile-planning.md
│   │   ├── portfolio-management.md
│   │   ├── compliance/
│   │   └── policies/
│   │
│   ├── domains/                        # Domain-specific docs
│   │   ├── AXIS/
│   │   │   ├── overview.md
│   │   │   ├── organizations.md       # 14 AXIS orgs
│   │   │   ├── architecture.md
│   │   │   └── integration-patterns.md
│   │   ├── PIPE/
│   │   │   ├── overview.md
│   │   │   ├── devops-patterns.md
│   │   │   ├── ci-cd.md
│   │   │   └── infrastructure.md
│   │   ├── IV/
│   │   │   ├── overview.md
│   │   │   ├── llm-orchestration.md
│   │   │   ├── rag-patterns.md
│   │   │   └── ml-pipelines.md
│   │   └── ECO/
│   │       ├── overview.md
│   │       ├── blockchain.md
│   │       ├── sustainability.md
│   │       └── smart-contracts.md
│   │
│   ├── bots/                           # Bot documentation
│   │   ├── axis/
│   │   │   ├── axis-framework-bot.md
│   │   │   ├── axis-docs-bot.md
│   │   │   ├── axis-compliance-bot.md
│   │   │   └── ... (30 AXIS bots)
│   │   ├── pipe/
│   │   │   ├── pipe-api-bot.md
│   │   │   ├── pipe-integration-bot.md
│   │   │   ├── pipe-artifact-bot.md
│   │   │   └── ... (46+ PIPE bots)
│   │   └── crewai/
│   │       ├── AXISBotArchitect.md
│   │       ├── BotCoordinationSpecialist.md
│   │       └── ... (CrewAI agents)
│   │
│   ├── cag-kerag/                      # KERAGR system docs
│   │   ├── overview.md
│   │   ├── cag-layer.md
│   │   ├── rag-layer.md
│   │   ├── knowledge-graph.md
│   │   └── api-reference.md
│   │
│   ├── gitops/                         # GitOps workflows
│   │   ├── issue-router.md
│   │   ├── multi-appvm-coordination.md
│   │   ├── webhook-automation.md
│   │   └── email-driven-workflows.md
│   │
│   └── infrastructure/                 # Infrastructure docs
│       ├── containers.md
│       ├── networking.md
│       ├── security.md
│       └── deployment.md
│
├── knowledge/                          # Structured knowledge base (YAML)
│   │
│   ├── entities/                       # Knowledge graph entities
│   │   ├── bots/
│   │   │   ├── axis-framework-bot.yaml
│   │   │   ├── pipe-api-bot.yaml
│   │   │   └── ... (all bots as YAML entities)
│   │   ├── domains/
│   │   │   ├── AXIS.yaml
│   │   │   ├── PIPE.yaml
│   │   │   ├── IV.yaml
│   │   │   └── ECO.yaml
│   │   ├── services/
│   │   │   ├── forgejo.yaml
│   │   │   ├── woodpecker.yaml
│   │   │   ├── artemis.yaml
│   │   │   └── ... (all services)
│   │   ├── patterns/
│   │   │   ├── bot-orchestration.yaml
│   │   │   ├── multi-domain-integration.yaml
│   │   │   └── ... (architecture patterns)
│   │   └── apis/
│   │       ├── axis-framework-api.yaml
│   │       ├── pipe-api.yaml
│   │       └── ... (API definitions)
│   │
│   ├── relationships/                  # Entity relationships
│   │   ├── bot-dependencies.yaml      # Bot → Service dependencies
│   │   ├── domain-integration.yaml    # Domain interconnections
│   │   ├── api-integrations.yaml      # API integrations
│   │   └── pattern-applications.yaml  # Where patterns are applied
│   │
│   ├── taxonomies/                     # Classification systems
│   │   ├── bot-types.yaml             # Bot taxonomy
│   │   ├── domain-capabilities.yaml   # Domain capability model
│   │   ├── architecture-layers.yaml   # Architecture layer taxonomy
│   │   └── technology-stack.yaml      # Tech stack taxonomy
│   │
│   └── decisions/                      # Architecture Decision Records
│       ├── ADR-001-git-based-knowledge.md
│       ├── ADR-002-hybrid-keragr.md
│       ├── ADR-003-neo4j-graph.md
│       └── ... (all ADRs)
│
├── data/                               # Converted Excel data
│   ├── pipelines.yaml                  # From Pipelines.xlsx
│   │   # Contains:
│   │   #   - Pipeline definitions
│   │   #   - Domain assignments
│   │   #   - Bot assignments
│   │   #   - Dependencies
│   ├── repos.yaml                      # From Repos.xlsx
│   │   # Contains:
│   │   #   - Repository list (253+ AXIS + others)
│   │   #   - Organization mappings
│   │   #   - Repository metadata
│   ├── network-zones.yaml              # From IV_PIPE_Network_Zones.xlsx
│   │   # Contains:
│   │   #   - Network topology
│   │   #   - IP allocations
│   │   #   - Security zones
│   ├── pipe-matrix.yaml                # From pipe_matrix_structure.xlsx
│   │   # Contains:
│   │   #   - PIPE organization structure
│   │   #   - Team assignments
│   │   #   - Responsibility matrix
│   └── schemas/
│       ├── pipeline.schema.yaml
│       ├── repository.schema.yaml
│       ├── network.schema.yaml
│       └── matrix.schema.yaml
│
├── wikis/                              # Consolidated bot wikis
│   ├── pipe-build-bot/
│   │   ├── meta.yaml                  # Wiki metadata
│   │   ├── Home.md
│   │   ├── Architecture.md
│   │   ├── API-Reference.md
│   │   ├── Getting-Started.md
│   │   ├── Integration-Guide.md
│   │   └── Troubleshooting.md
│   ├── pipe-vault-bot/
│   │   ├── meta.yaml
│   │   └── ... (wiki pages)
│   ├── ECO-backup-bot/
│   │   ├── meta.yaml
│   │   └── ... (wiki pages)
│   └── ... (all 50+ bot wikis)
│
├── schemas/                            # YAML schema definitions
│   ├── entity.schema.yaml             # JSON Schema for entities
│   ├── relationship.schema.yaml       # JSON Schema for relationships
│   ├── knowledge.schema.yaml          # General knowledge schema
│   └── validation-rules.yaml          # Custom validation rules
│
├── scripts/                            # Automation scripts
│   ├── sync-wikis.sh                  # Wiki synchronisation
│   ├── convert-excel-to-yaml.py       # Excel conversion
│   ├── generate-embeddings.py         # FAISS embedding generation
│   ├── update-knowledge-graph.py      # Neo4j update from YAML
│   ├── validate-yaml.py               # Schema validation
│   └── index-documents.py             # MongoDB indexing
│
├── .github/                            # GitHub Actions (or .forgejo)
│   └── workflows/
│       ├── sync-wikis.yaml            # Auto-sync bot wikis
│       ├── validate-yaml.yaml         # Validate on PR
│       ├── update-knowledge-graph.yaml # Update Neo4j on merge
│       ├── generate-embeddings.yaml   # Update FAISS on merge
│       └── deploy-docs.yaml           # Deploy to docs site
│
└── .codeberg/                          # Codeberg-specific
    └── workflows/
        └── ... (same workflows)
```

### 4.2 Service Deployment Structure

```
/home/user/services/meta-keragr/
│
├── docker-compose.yaml                 # Full stack deployment
├── .env                                # Environment configuration
│
├── api/                                # FastAPI service
│   ├── app.py                         # Main application
│   ├── routers/
│   │   ├── knowledge.py               # Knowledge endpoints
│   │   ├── graph.py                   # Graph queries
│   │   └── websocket.py               # WebSocket handlers
│   ├── models/
│   │   ├── entities.py
│   │   ├── queries.py
│   │   └── responses.py
│   ├── services/
│   │   ├── cag_layer.py               # CAG implementation
│   │   ├── rag_layer.py               # RAG implementation
│   │   ├── hybrid_retrieval.py
│   │   └── knowledge_fusion.py
│   └── Dockerfile                     # Chainguard Wolfi base
│
├── neo4j/                              # Knowledge graph
│   ├── data/                          # Persistent data
│   ├── import/                        # YAML import scripts
│   └── Dockerfile                     # Neo4j container
│
├── faiss/                              # Vector store
│   ├── indices/                       # FAISS index files
│   ├── metadata/                      # Document metadata
│   └── embeddings/                    # Embedding pipeline
│
├── mongodb/                            # Document store
│   ├── data/                          # Persistent data
│   └── init/                          # Initial collections
│
└── nginx/                              # Reverse proxy
    ├── nginx.conf
    └── ssl/                           # TLS certificates
```

### 4.3 Bot SDK Structure

```
/home/user/packages/bsw-knowledge-sdk/
│
├── setup.py                            # Python package setup
├── README.md
├── LICENSE
│
├── bsw_knowledge_sdk/
│   ├── __init__.py
│   ├── client.py                      # Main client class
│   ├── models/
│   │   ├── query.py
│   │   ├── result.py
│   │   └── entity.py
│   ├── websocket/
│   │   ├── subscriber.py
│   │   └── handlers.py
│   └── utils/
│       ├── auth.py
│       └── retry.py
│
├── tests/
│   ├── test_client.py
│   ├── test_search.py
│   └── test_websocket.py
│
└── examples/
    ├── simple_search.py
    ├── graph_query.py
    └── realtime_updates.py
```

---

## 5. Bot Integration Pattern

### 5.1 Standard Integration Pattern

**All bots follow this standard pattern for knowledge access:**

```python
# Standard bot knowledge integration pattern

from bsw_knowledge_sdk import KnowledgeClient
import os

class StandardBot:
    """Base class for all BSW bots"""

    def __init__(self, bot_id: str, domain: str):
        # Initialise knowledge client
        self.knowledge = KnowledgeClient(
            api_url=os.getenv('KNOWLEDGE_API_URL', 'http://localhost:3108'),
            bot_id=bot_id,
            domain=domain,
            auth_token=os.getenv('KNOWLEDGE_API_TOKEN')
        )

        # Subscribe to knowledge updates
        asyncio.create_task(self.subscribe_to_updates())

    async def subscribe_to_updates(self):
        """Subscribe to real-time knowledge updates"""
        await self.knowledge.subscribe_to_updates(
            domains=[self.domain],
            on_update=self.on_knowledge_updated
        )

    async def on_knowledge_updated(self, update):
        """Handle knowledge update"""
        logger.info(f"Knowledge updated: {update['doc_id']}")
        # Invalidate local cache, refresh, etc.
        await self.refresh_knowledge_cache()

    async def query_knowledge(self, question: str):
        """Query knowledge base"""
        results = await self.knowledge.search(question)
        return results

    async def get_related_entities(self, entity_type: str, entity_id: str):
        """Get related entities from knowledge graph"""
        query = f"""
        MATCH (e:{entity_type} {{id: '{entity_id}'}})-[r]-(related)
        RETURN related, type(r) as relationship
        """
        return await self.knowledge.graph_query(query)
```

### 5.2 Domain-Specific Patterns

#### 5.2.1 AXIS Bots Pattern

```python
class AXISBot(StandardBot):
    """Base class for AXIS domain bots"""

    def __init__(self, bot_id: str):
        super().__init__(bot_id, domain='AXIS')
        self.artemis_endpoint = os.getenv('ARTEMIS_ENDPOINT')

    async def find_coordinating_bots(self):
        """Find other AXIS bots to coordinate with"""
        return await self.knowledge.graph_query("""
            MATCH (me:Bot {name: '%s'})-[:COORDINATES_WITH]->(other:Bot)
            WHERE other.domain = 'AXIS' AND other.status = 'active'
            RETURN other.name, other.api_endpoint
        """ % self.bot_id)

    async def get_architecture_patterns(self, pattern_type: str):
        """Get architecture patterns from knowledge base"""
        return await self.knowledge.search(
            f"architecture pattern {pattern_type}",
            filters={'domain': 'AXIS', 'type': 'pattern'}
        )
```

**Example: axis-framework-bot Integration**:

```python
from bsw_bots.base import AXISBot

class FrameworkBot(AXISBot):
    def __init__(self):
        super().__init__(bot_id='axis-framework-bot')

    async def check_framework(self, framework: str, version: str):
        """Check framework using knowledge base"""

        # 1. Query for known issues
        issues = await self.query_knowledge(
            f"{framework} {version} known issues compatibility problems"
        )

        # 2. Get framework entity from graph
        framework_data = await self.knowledge.graph_query(f"""
            MATCH (f:Framework {{name: '{framework}', version: '{version}'}})
            OPTIONAL MATCH (f)-[:REQUIRES]->(dep:Dependency)
            OPTIONAL MATCH (f)-[:INCOMPATIBLE_WITH]->(incomp:Technology)
            RETURN f, collect(dep) as dependencies, collect(incomp) as incompatibilities
        """)

        # 3. Check against current environment
        environment = await self.get_current_environment()
        conflicts = self.find_conflicts(framework_data, environment)

        return {
            'framework': framework,
            'version': version,
            'compatible': len(conflicts) == 0 and len(issues['results']) == 0,
            'issues': issues['results'],
            'conflicts': conflicts,
            'dependencies': framework_data['dependencies']
        }
```

#### 5.2.2 PIPE Bots Pattern

```python
class PIPEBot(StandardBot):
    """Base class for PIPE domain bots"""

    def __init__(self, bot_id: str):
        super().__init__(bot_id, domain='PIPE')
        self.pipeline_registry = os.getenv('PIPELINE_REGISTRY')

    async def get_pipeline_config(self, pipeline_name: str):
        """Get pipeline configuration from knowledge"""
        results = await self.knowledge.search(
            f"pipeline {pipeline_name} configuration",
            filters={'domain': 'PIPE', 'type': 'pipeline'}
        )
        return results['results'][0] if results['results'] else None

    async def find_dependent_pipelines(self, pipeline_name: str):
        """Find pipelines that depend on this one"""
        return await self.knowledge.graph_query(f"""
            MATCH (p:Pipeline {{name: '{pipeline_name}'}})<-[:DEPENDS_ON]-(dep:Pipeline)
            RETURN dep.name, dep.domain, dep.status
        """)
```

**Example: pipe-api-bot Integration**:

```python
from bsw_bots.base import PIPEBot

class APIBot(PIPEBot):
    def __init__(self):
        super().__init__(bot_id='pipe-api-bot')

    async def validate_api_integration(self, service: str, endpoint: str):
        """Validate API integration using knowledge base"""

        # 1. Get API specification from knowledge
        api_spec = await self.knowledge.search(
            f"{service} API specification {endpoint}",
            filters={'type': 'api_spec'}
        )

        # 2. Get integration examples
        examples = await self.knowledge.search(
            f"{service} integration examples",
            filters={'domain': 'PIPE', 'type': 'example'}
        )

        # 3. Check for known issues
        issues = await self.knowledge.graph_query(f"""
            MATCH (api:API {{service: '{service}', endpoint: '{endpoint}'}})
                  -[:HAS_ISSUE]->(issue:Issue)
            WHERE issue.status = 'open'
            RETURN issue.title, issue.severity, issue.workaround
        """)

        return {
            'valid': len(api_spec['results']) > 0,
            'specification': api_spec['results'][0] if api_spec['results'] else None,
            'examples': examples['results'],
            'known_issues': issues['results']
        }
```

#### 5.2.3 IV (IntelliVerse) Bots Pattern

```python
class IVBot(StandardBot):
    """Base class for IV (IntelliVerse) domain bots"""

    def __init__(self, bot_id: str):
        super().__init__(bot_id, domain='IV')
        self.llm_endpoint = os.getenv('LLM_ENDPOINT')

    async def get_ml_model_info(self, model_name: str):
        """Get ML model information from knowledge"""
        return await self.knowledge.graph_query(f"""
            MATCH (m:MLModel {{name: '{model_name}'}})
            OPTIONAL MATCH (m)-[:TRAINED_ON]->(dataset:Dataset)
            OPTIONAL MATCH (m)-[:DEPLOYED_ON]->(platform:Platform)
            OPTIONAL MATCH (m)-[:HAS_METRIC]->(metric:Metric)
            RETURN m, dataset, platform, collect(metric) as metrics
        """)

    async def find_similar_models(self, model_name: str, limit: int = 5):
        """Find similar ML models using vector search"""
        # Get model description
        model_info = await self.get_ml_model_info(model_name)
        description = model_info['m']['description']

        # Vector search for similar models
        return await self.knowledge.search(
            description,
            filters={'domain': 'IV', 'type': 'ml_model'},
            limit=limit
        )
```

#### 5.2.4 ECO (ECOX) Bots Pattern

```python
class ECOBot(StandardBot):
    """Base class for ECO domain bots"""

    def __init__(self, bot_id: str):
        super().__init__(bot_id, domain='ECO')
        self.blockchain_endpoint = os.getenv('BLOCKCHAIN_ENDPOINT')

    async def get_smart_contract_template(self, contract_type: str):
        """Get smart contract template from knowledge"""
        results = await self.knowledge.search(
            f"smart contract template {contract_type}",
            filters={'domain': 'ECO', 'type': 'template'}
        )
        return results['results'][0] if results['results'] else None

    async def check_sustainability_metrics(self, service: str):
        """Check sustainability metrics from knowledge graph"""
        return await self.knowledge.graph_query(f"""
            MATCH (s:Service {{name: '{service}'}})-[:HAS_METRIC]->(m:SustainabilityMetric)
            RETURN m.type, m.value, m.unit, m.last_updated
            ORDER BY m.last_updated DESC
        """)
```

### 5.3 Integration Workflow

```mermaid
sequenceDiagram
    participant Bot as Any Bot
    participant SDK as Knowledge SDK
    participant API as META-KERAGR API
    participant Cache as Local Cache
    participant KG as Knowledge Graph

    Note over Bot,KG: Bot Startup
    Bot->>SDK: Initialize(bot_id, domain, token)
    SDK->>API: Authenticate
    API->>SDK: Return session
    SDK->>API: Subscribe to updates (WebSocket)

    Note over Bot,KG: Knowledge Query
    Bot->>Cache: Check local cache
    Cache-->>Bot: Cache miss
    Bot->>SDK: query("How to deploy with apko?")
    SDK->>API: POST /api/v1/knowledge/search
    API->>KG: Hybrid search (CAG+RAG)
    KG-->>API: Ranked results
    API-->>SDK: JSON response
    SDK->>Cache: Update cache
    SDK-->>Bot: Structured results

    Note over Bot,KG: Real-Time Update
    KG->>API: New doc detected
    API->>SDK: WebSocket update notification
    SDK->>Cache: Invalidate cache
    SDK->>Bot: on_knowledge_updated()
    Bot->>SDK: Refresh specific knowledge
```

### 5.4 Caching Strategy

**Each bot implements intelligent caching:**

```python
class KnowledgeCache:
    """Local knowledge cache for bots"""

    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl

    async def get(self, key: str):
        """Get from cache if not expired"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['value']
            else:
                del self.cache[key]
        return None

    async def set(self, key: str, value):
        """Set cache entry"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

    async def invalidate(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern:
            # Invalidate matching keys
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            # Clear all
            self.cache.clear()
```

---

## 6. Auto-Sync Strategy

### 6.1 Multi-Source Synchronisation

**Challenge**: Keep knowledge base synchronised across:
1. Local documentation (`/home/user/QubesIncoming/bsw-gov`)
2. Bot wikis (`/home/user/Code/*/wiki`)
3. Codeberg wikis (distributed across repos)
4. Excel data files
5. Git repository (`codeberg.org/BSW-Docs/bsw-documentation`)

**Solution**: Automated bidirectional sync with conflict resolution

### 6.2 Sync Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    AUTO-SYNC ORCHESTRATION                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────┐         ┌────────────────────┐          │
│  │ Local Files        │────────▶│  Sync Scheduler    │          │
│  │ /home/user/...     │         │  (cron every 15m)  │          │
│  └────────────────────┘         └──────────┬─────────┘          │
│                                             │                     │
│  ┌────────────────────┐                    │                     │
│  │ Bot Wikis          │────────────────────┤                     │
│  │ /home/user/Code/   │                    │                     │
│  └────────────────────┘                    ▼                     │
│                                  ┌─────────────────────┐         │
│  ┌────────────────────┐          │  Sync Engine        │         │
│  │ Codeberg Wikis     │◀────────▶│  • Change detection │         │
│  │ (50+ repos)        │          │  • Conflict resolve │         │
│  └────────────────────┘          │  • Git operations   │         │
│                                  └──────────┬──────────┘         │
│  ┌────────────────────┐                    │                     │
│  │ Excel Files        │────────────────────┤                     │
│  │ *.xlsx → YAML      │                    │                     │
│  └────────────────────┘                    ▼                     │
│                                  ┌─────────────────────┐         │
│                                  │  Git Repository     │         │
│                                  │  (Central)          │         │
│                                  └──────────┬──────────┘         │
│                                             │                     │
│                    ┌────────────────────────┼───────────────┐    │
│                    ▼                        ▼               ▼    │
│           ┌─────────────┐         ┌─────────────┐  ┌──────────┐ │
│           │   Neo4j     │         │   MongoDB   │  │  FAISS   │ │
│           │ (Knowledge  │         │ (Document   │  │ (Vector  │ │
│           │  Graph)     │         │  Store)     │  │  Store)  │ │
│           └─────────────┘         └─────────────┘  └──────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 6.3 Sync Workflow Implementation

#### 6.3.1 Sync Scheduler

```bash
#!/bin/bash
# /home/user/scripts/sync-scheduler.sh
# Runs every 15 minutes via cron

# Cron entry:
# */15 * * * * /home/user/scripts/sync-scheduler.sh >> /var/log/knowledge-sync.log 2>&1

set -e

SYNC_SCRIPT="/home/user/scripts/sync-knowledge-base.sh"
LOCK_FILE="/tmp/knowledge-sync.lock"

# Prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
    echo "Sync already running, skipping..."
    exit 0
fi

# Create lock
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# Run sync
echo "=== Knowledge Base Sync Started: $(date) ==="
$SYNC_SCRIPT
echo "=== Sync Completed: $(date) ==="
```

#### 6.3.2 Main Sync Script

```bash
#!/bin/bash
# /home/user/scripts/sync-knowledge-base.sh

set -e

REPO_DIR="/home/user/bsw-documentation"
SOURCE_DIRS=(
    "/home/user/QubesIncoming/bsw-gov"
    "/home/user/Code"
)

cd "$REPO_DIR"

# 1. Pull latest from Codeberg
echo "Pulling latest from Codeberg..."
git pull origin main

# 2. Sync local documentation
echo "Syncing local documentation..."
rsync -av --delete \
    --exclude='.git' \
    --exclude='*.swp' \
    /home/user/QubesIncoming/bsw-gov/ \
    "$REPO_DIR/docs/architecture/"

# 3. Sync bot wikis
echo "Syncing bot wikis..."
/home/user/scripts/sync-wikis.sh

# 4. Convert Excel files if modified
echo "Checking Excel files..."
/home/user/scripts/convert-excel-if-modified.py

# 5. Detect changes
if git status --porcelain | grep -q .; then
    echo "Changes detected, committing..."

    # Stage all changes
    git add .

    # Generate commit message
    CHANGED_FILES=$(git status --porcelain | wc -l)
    COMMIT_MSG="Auto-sync: $CHANGED_FILES files updated - $(date -Iseconds)"

    # Commit
    git commit -m "$COMMIT_MSG"

    # Push to Codeberg
    git push origin main

    echo "Changes pushed to Codeberg"

    # 6. Trigger knowledge graph update
    echo "Triggering knowledge graph update..."
    /home/user/scripts/update-knowledge-graph.py

    # 7. Regenerate embeddings
    echo "Regenerating embeddings..."
    /home/user/scripts/generate-embeddings.py --incremental

    # 8. Notify bots via WebSocket
    echo "Notifying bots of updates..."
    curl -X POST http://localhost:3108/api/v1/admin/notify-update \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"commit\": \"$(git rev-parse HEAD)\"}"
else
    echo "No changes detected"
fi
```

#### 6.3.3 Wiki Sync Script

```bash
#!/bin/bash
# /home/user/scripts/sync-wikis.sh

set -e

REPO_DIR="/home/user/bsw-documentation"
WIKIS_DIR="$REPO_DIR/wikis"

# Find all wiki directories
find /home/user/Code -type d -name "wiki" | while read wiki_path; do
    # Extract bot name
    bot_name=$(basename $(dirname "$wiki_path"))

    echo "Syncing wiki for $bot_name..."

    # Create target directory
    target_dir="$WIKIS_DIR/$bot_name"
    mkdir -p "$target_dir"

    # Sync wiki content
    rsync -av --delete \
        --exclude='.git' \
        --exclude='*.swp' \
        "$wiki_path/" \
        "$target_dir/"

    # Update metadata
    cat > "$target_dir/meta.yaml" <<EOF
bot_name: $bot_name
source_path: $wiki_path
last_sync: $(date -Iseconds)
domain: $(detect_domain "$bot_name")
sync_method: rsync
EOF

    echo "  ✓ Synced $bot_name wiki"
done

echo "All wikis synchronised"
```

#### 6.3.4 Excel Conversion Script

```python
#!/usr/bin/env python3
# /home/user/scripts/convert-excel-if-modified.py

import os
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime

EXCEL_DIR = Path("/home/user/QubesIncoming/bsw-gov/CAG - KERAG - COGNEE")
DATA_DIR = Path("/home/user/bsw-documentation/data")
STATE_FILE = DATA_DIR / ".conversion_state.yaml"

def get_file_mtime(filepath):
    """Get file modification time"""
    return os.path.getmtime(filepath)

def load_state():
    """Load last conversion state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}

def save_state(state):
    """Save conversion state"""
    with open(STATE_FILE, 'w') as f:
        yaml.safe_dump(state, f)

def convert_excel_to_yaml(excel_file, yaml_file):
    """Convert Excel file to YAML"""
    print(f"Converting {excel_file.name}...")

    # Read all sheets
    excel_data = pd.read_excel(excel_file, sheet_name=None)

    # Convert to dictionary
    data = {}
    for sheet_name, df in excel_data.items():
        # Convert DataFrame to list of dicts
        data[sheet_name] = df.to_dict('records')

    # Add metadata
    output = {
        'source_file': str(excel_file),
        'converted_at': datetime.now().isoformat(),
        'sheets': data
    }

    # Write YAML
    with open(yaml_file, 'w') as f:
        yaml.safe_dump(output, f, default_flow_style=False, allow_unicode=True)

    print(f"  ✓ Created {yaml_file.name}")

def main():
    # Excel to YAML mappings
    conversions = [
        ("2025 02 12 Pipelines(1).xlsx", "pipelines.yaml"),
        ("2025 02 12 Repos(1).xlsx", "repos.yaml"),
        ("IV_PIPE_Network_Zones.xlsx", "network-zones.yaml"),
        ("pipe_matrix_structure_full_updated.xlsx", "pipe-matrix.yaml"),
    ]

    state = load_state()
    changed = False

    for excel_name, yaml_name in conversions:
        excel_file = EXCEL_DIR / excel_name
        yaml_file = DATA_DIR / yaml_name

        if not excel_file.exists():
            print(f"Warning: {excel_name} not found, skipping...")
            continue

        # Check if conversion needed
        current_mtime = get_file_mtime(excel_file)
        last_mtime = state.get(excel_name, 0)

        if current_mtime > last_mtime or not yaml_file.exists():
            convert_excel_to_yaml(excel_file, yaml_file)
            state[excel_name] = current_mtime
            changed = True
        else:
            print(f"✓ {excel_name} unchanged, skipping...")

    if changed:
        save_state(state)
        print("Excel files converted successfully")
    else:
        print("No Excel files needed conversion")

if __name__ == '__main__':
    main()
```

### 6.4 Knowledge Graph Update Pipeline

```python
#!/usr/bin/env python3
# /home/user/scripts/update-knowledge-graph.py

import yaml
import asyncio
from neo4j import AsyncGraphDatabase
from pathlib import Path

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class KnowledgeGraphUpdater:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    async def update_from_yaml(self, yaml_file: Path):
        """Update knowledge graph from YAML file"""
        with open(yaml_file) as f:
            data = yaml.safe_load(f)

        entity_type = data.get('entity_type')

        async with self.driver.session() as session:
            if entity_type == 'Bot':
                await self.create_bot_entity(session, data)
            elif entity_type == 'Domain':
                await self.create_domain_entity(session, data)
            elif entity_type == 'Pattern':
                await self.create_pattern_entity(session, data)
            # ... other entity types

    async def create_bot_entity(self, session, data):
        """Create or update Bot entity"""
        query = """
        MERGE (b:Bot {name: $name})
        SET b.domain = $domain,
            b.status = $status,
            b.description = $description,
            b.api_base_url = $api_base_url,
            b.updated_at = datetime()
        """
        await session.run(query, **data)

        # Create relationships
        if 'integrations' in data:
            for integration in data['integrations']:
                await session.run("""
                    MATCH (b:Bot {name: $bot_name})
                    MERGE (p:Platform {name: $platform_name})
                    MERGE (b)-[:INTEGRATES_WITH]->(p)
                """, bot_name=data['name'], platform_name=integration)

    async def scan_and_update(self, knowledge_dir: Path):
        """Scan knowledge directory and update all entities"""
        yaml_files = knowledge_dir.rglob("*.yaml")

        for yaml_file in yaml_files:
            if yaml_file.name == 'meta.yaml':
                continue

            try:
                await self.update_from_yaml(yaml_file)
                print(f"✓ Updated {yaml_file.relative_to(knowledge_dir)}")
            except Exception as e:
                print(f"✗ Error updating {yaml_file}: {e}")

    async def close(self):
        await self.driver.close()

async def main():
    updater = KnowledgeGraphUpdater()

    try:
        knowledge_dir = Path("/home/user/bsw-documentation/knowledge")
        await updater.scan_and_update(knowledge_dir)
        print("Knowledge graph update completed")
    finally:
        await updater.close()

if __name__ == '__main__':
    asyncio.run(main())
```

### 6.5 Embedding Generation Pipeline

```python
#!/usr/bin/env python3
# /home/user/scripts/generate-embeddings.py

import argparse
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

DOCS_DIR = Path("/home/user/bsw-documentation/docs")
FAISS_DIR = Path("/home/user/services/meta-keragr/faiss")
STATE_FILE = FAISS_DIR / ".embedding_state.json"

def load_state():
    """Load last embedding state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'files': {}, 'total_chunks': 0}

def save_state(state):
    """Save embedding state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def chunk_text(text, max_tokens=512):
    """Chunk text into smaller pieces"""
    # Simple sentence-based chunking
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_tokens:
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length

    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')

    return chunks

def generate_embeddings(incremental=False):
    """Generate embeddings for all documentation"""
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    state = load_state()

    # Find all markdown files
    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")

    embeddings = []
    metadata = []

    for md_file in md_files:
        file_mtime = md_file.stat().st_mtime
        file_key = str(md_file.relative_to(DOCS_DIR))

        # Skip if incremental and file unchanged
        if incremental and file_key in state['files']:
            if state['files'][file_key] == file_mtime:
                print(f"✓ {file_key} unchanged, skipping...")
                continue

        print(f"Processing {file_key}...")

        # Read file
        with open(md_file) as f:
            content = f.read()

        # Chunk content
        chunks = chunk_text(content)

        # Generate embeddings for each chunk
        for i, chunk in enumerate(chunks):
            embedding = model.encode(chunk)
            embeddings.append(embedding)
            metadata.append({
                'file': file_key,
                'chunk_id': i,
                'text': chunk,
                'domain': detect_domain_from_path(md_file),
                'type': detect_doc_type(md_file)
            })

        # Update state
        state['files'][file_key] = file_mtime
        print(f"  ✓ Generated {len(chunks)} embeddings")

    if not embeddings:
        print("No new embeddings to generate")
        return

    # Create or update FAISS index
    print("Creating FAISS index...")
    dimension = 384

    if incremental and (FAISS_DIR / "knowledge_base.index").exists():
        # Load existing index
        index = faiss.read_index(str(FAISS_DIR / "knowledge_base.index"))

        # Load existing metadata
        with open(FAISS_DIR / "metadata.json") as f:
            existing_metadata = json.load(f)

        # Add new embeddings
        vectors = np.array(embeddings).astype('float32')
        index.add(vectors)

        # Merge metadata
        metadata = existing_metadata + metadata
    else:
        # Create new index
        index = faiss.IndexFlatL2(dimension)
        vectors = np.array(embeddings).astype('float32')
        index.add(vectors)

    # Save index
    faiss.write_index(index, str(FAISS_DIR / "knowledge_base.index"))

    # Save metadata
    with open(FAISS_DIR / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    # Update state
    state['total_chunks'] = len(metadata)
    save_state(state)

    print(f"✓ FAISS index created with {len(metadata)} total embeddings")

def detect_domain_from_path(path):
    """Detect domain from file path"""
    path_str = str(path)
    if '/AXIS/' in path_str or '/axis/' in path_str:
        return 'AXIS'
    elif '/PIPE/' in path_str or '/pipe/' in path_str:
        return 'PIPE'
    elif '/IV/' in path_str or '/iv/' in path_str:
        return 'IV'
    elif '/ECO/' in path_str or '/eco/' in path_str:
        return 'ECO'
    return 'general'

def detect_doc_type(path):
    """Detect document type from file path"""
    path_str = str(path)
    if '/bots/' in path_str:
        return 'bot_doc'
    elif '/architecture/' in path_str:
        return 'architecture'
    elif '/wikis/' in path_str:
        return 'wiki'
    elif '/governance/' in path_str:
        return 'governance'
    return 'general'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--incremental', action='store_true',
                       help='Only process changed files')
    args = parser.parse_args()

    generate_embeddings(incremental=args.incremental)
```

### 6.6 WebSocket Update Notification

```python
# Part of META-KERAGR API service
# /home/user/services/meta-keragr/api/routers/websocket.py

from fastapi import WebSocket, WebSocketDisconnect
import asyncio

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, bot_id: str, domains: List[str]):
        """Register bot WebSocket connection"""
        await websocket.accept()

        for domain in domains:
            if domain not in self.active_connections:
                self.active_connections[domain] = []
            self.active_connections[domain].append({
                'websocket': websocket,
                'bot_id': bot_id
            })

        print(f"Bot {bot_id} connected for domains: {domains}")

    async def disconnect(self, websocket: WebSocket):
        """Unregister WebSocket connection"""
        for domain, connections in self.active_connections.items():
            self.active_connections[domain] = [
                c for c in connections if c['websocket'] != websocket
            ]

    async def broadcast_update(self, domains: List[str], update_data: dict):
        """Broadcast update to all connected bots in specified domains"""
        for domain in domains:
            if domain in self.active_connections:
                connections = self.active_connections[domain]

                # Send to all connections concurrently
                await asyncio.gather(*[
                    self.send_update(conn['websocket'], update_data)
                    for conn in connections
                ], return_exceptions=True)

    async def send_update(self, websocket: WebSocket, data: dict):
        """Send update to specific WebSocket"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            print(f"Error sending update: {e}")

manager = ConnectionManager()

@app.websocket("/ws/knowledge/updates")
async def knowledge_updates(websocket: WebSocket):
    """WebSocket endpoint for knowledge updates"""
    # Get bot info from query params
    bot_id = websocket.query_params.get('bot_id')
    domains = websocket.query_params.get('domains', '').split(',')

    await manager.connect(websocket, bot_id, domains)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

@app.post("/api/v1/admin/notify-update")
async def notify_update(
    commit_hash: str,
    domains: Optional[List[str]] = None,
    token: str = Depends(verify_admin_token)
):
    """Admin endpoint to trigger update notifications"""

    # Determine affected domains from commit
    if not domains:
        domains = await detect_affected_domains(commit_hash)

    # Broadcast to all connected bots
    await manager.broadcast_update(domains, {
        'type': 'knowledge_update',
        'commit': commit_hash,
        'domains': domains,
        'timestamp': datetime.now().isoformat()
    })

    return {'status': 'notified', 'domains': domains}
```

### 6.7 Sync Monitoring and Health Checks

```python
#!/usr/bin/env python3
# /home/user/scripts/sync-healthcheck.py

import requests
import yaml
from pathlib import Path
from datetime import datetime, timedelta

def check_sync_health():
    """Check if sync is healthy"""
    issues = []

    # 1. Check last sync time
    state_file = Path("/home/user/bsw-documentation/data/.conversion_state.yaml")
    if state_file.exists():
        with open(state_file) as f:
            state = yaml.safe_load(f)

        # Check each Excel file
        for file, mtime in state.items():
            last_sync = datetime.fromtimestamp(mtime)
            if datetime.now() - last_sync > timedelta(days=1):
                issues.append(f"Excel file {file} not synced in >24h")
    else:
        issues.append("Conversion state file missing")

    # 2. Check Git sync
    try:
        result = subprocess.run(
            ['git', '-C', '/home/user/bsw-documentation', 'log', '-1', '--format=%ci'],
            capture_output=True,
            text=True
        )
        last_commit = datetime.strptime(result.stdout.strip(), '%Y-%m-%d %H:%M:%S %z')
        if datetime.now(last_commit.tzinfo) - last_commit > timedelta(hours=1):
            issues.append("Git not synced in >1 hour")
    except Exception as e:
        issues.append(f"Git check failed: {e}")

    # 3. Check knowledge graph freshness
    try:
        response = requests.get('http://localhost:7474/db/data/')
        # Check Neo4j is responding
        if response.status_code != 200:
            issues.append("Neo4j not responding")
    except Exception as e:
        issues.append(f"Neo4j check failed: {e}")

    # 4. Check FAISS index
    faiss_index = Path("/home/user/services/meta-keragr/faiss/knowledge_base.index")
    if not faiss_index.exists():
        issues.append("FAISS index missing")
    else:
        # Check age
        mtime = datetime.fromtimestamp(faiss_index.stat().st_mtime)
        if datetime.now() - mtime > timedelta(hours=1):
            issues.append("FAISS index not updated in >1 hour")

    # Report
    if issues:
        print("❌ Sync health check FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Sync health check PASSED")
        return True

if __name__ == '__main__':
    import sys
    sys.exit(0 if check_sync_health() else 1)
```

---

## 7. Query Examples

### 7.1 Simple REST Queries

#### Example 1: Search for Documentation

**Request**:
```bash
curl -X GET "http://localhost:3108/api/v1/knowledge/search" \
  -H "Authorization: Bearer $KNOWLEDGE_TOKEN" \
  -G \
  --data-urlencode "query=How to deploy containers with apko" \
  --data-urlencode "bot_id=axis-framework-bot" \
  --data-urlencode "limit=5"
```

**Response**:
```json
{
  "query": "How to deploy containers with apko",
  "results": [
    {
      "id": "doc_apko_guide_1",
      "title": "APKO Domain Containers Strategy",
      "excerpt": "apko is used to build minimal containers from Chainguard Wolfi base...",
      "relevance_score": 0.92,
      "source": {
        "file": "docs/architecture/APKO-DOMAIN-CONTAINERS-STRATEGY.md",
        "domain": "AXIS",
        "type": "architecture"
      },
      "related_entities": [
        {"type": "Bot", "name": "axis-framework-bot"},
        {"type": "Technology", "name": "Chainguard Wolfi"}
      ]
    },
    {
      "id": "wiki_pipe_build_1",
      "title": "Building Containers - pipe-build-bot wiki",
      "excerpt": "The pipe-build-bot automates container builds using apko configurations...",
      "relevance_score": 0.87,
      "source": {
        "file": "wikis/pipe-build-bot/Architecture.md",
        "domain": "PIPE",
        "type": "wiki"
      }
    }
  ],
  "total": 5,
  "confidence": 0.89,
  "processing_time_ms": 145
}
```

#### Example 2: Get Bot Information

**Request**:
```bash
curl -X GET "http://localhost:3108/api/v1/knowledge/entity/axis-framework-bot" \
  -H "Authorization: Bearer $KNOWLEDGE_TOKEN"
```

**Response**:
```json
{
  "entity_type": "Bot",
  "name": "axis-framework-bot",
  "domain": "AXIS",
  "status": "production",
  "description": "Framework detection and update management bot",
  "api": {
    "base_url": "http://localhost:8085/api/v1/framework",
    "endpoints": [
      {"path": "/detect", "method": "POST"},
      {"path": "/check", "method": "POST"},
      {"path": "/suggest", "method": "POST"},
      {"path": "/health", "method": "GET"}
    ]
  },
  "integrations": ["ARTEMIS", "Codeberg", "Git"],
  "dependencies": ["Python 3.13", "Git", "Chainguard Wolfi"],
  "related_bots": [
    {"name": "axis-docs-bot", "relationship": "COORDINATES_WITH"},
    {"name": "axis-compliance-bot", "relationship": "DEPENDS_ON"}
  ],
  "documentation": [
    "/docs/bots/axis/axis-framework-bot.md",
    "/wikis/axis-framework-bot/"
  ]
}
```

#### Example 3: Domain Knowledge Overview

**Request**:
```bash
curl -X GET "http://localhost:3108/api/v1/knowledge/domain/PIPE" \
  -H "Authorization: Bearer $KNOWLEDGE_TOKEN"
```

**Response**:
```json
{
  "domain": "PIPE",
  "description": "Pipeline Infrastructure Processing Engine - Core API and integration management",
  "network_zone": "10.100.1.0/24",
  "services_count": 21,
  "bots_count": 46,
  "sub_organizations": [
    "PIPE-Core", "PIPE-Bots", "PIPE-Docs", "PIPE-KMS",
    "PIPE-Data", "PIPE-Security", "PIPE-Observability",
    "PIPE-Decentralized", "PIPE-CI-CD", "PIPE-Infra",
    "PIPE-IoT", "PIPE-Labs", "PIPE-Media"
  ],
  "integration_level": {
    "AXIS": "high",
    "IV": "high",
    "ECO": "low",
    "BNI": "high",
    "BNP": "high"
  },
  "documentation_count": 127,
  "recent_updates": [
    {
      "file": "docs/domains/PIPE/ci-cd.md",
      "updated": "2025-11-10T14:32:00Z",
      "commit": "abc123"
    }
  ]
}
```

### 7.2 GraphQL Queries

#### Example 1: Find Related Bots

**Query**:
```graphql
query FindRelatedBots {
  bot(name: "axis-framework-bot") {
    name
    domain
    status
    integrations {
      name
      type
      api_endpoint
    }
    coordinates_with {
      name
      domain
      api_endpoint
    }
    depends_on {
      name
      type
    }
  }
}
```

**Response**:
```json
{
  "data": {
    "bot": {
      "name": "axis-framework-bot",
      "domain": "AXIS",
      "status": "production",
      "integrations": [
        {
          "name": "ARTEMIS",
          "type": "Platform",
          "api_endpoint": "http://localhost:8086/api/v1/artemis"
        },
        {
          "name": "Codeberg",
          "type": "GitService",
          "api_endpoint": "https://codeberg.org/api/v1"
        }
      ],
      "coordinates_with": [
        {
          "name": "axis-docs-bot",
          "domain": "AXIS",
          "api_endpoint": "http://localhost:8085/api/v1/docs"
        },
        {
          "name": "axis-compliance-bot",
          "domain": "AXIS",
          "api_endpoint": "http://localhost:8085/api/v1/compliance"
        }
      ],
      "depends_on": [
        {"name": "Python 3.13", "type": "Runtime"},
        {"name": "Git", "type": "Tool"},
        {"name": "Chainguard Wolfi", "type": "ContainerBase"}
      ]
    }
  }
}
```

#### Example 2: Discover Architecture Patterns

**Query**:
```graphql
query DiscoverPatterns {
  patterns(
    domains: ["AXIS", "PIPE"]
    pattern_type: "bot-orchestration"
  ) {
    id
    name
    description
    domains
    applicable_to {
      bot_type
      use_cases
    }
    related_adrs {
      id
      title
      status
    }
    examples {
      bot_name
      implementation_file
    }
  }
}
```

**Response**:
```json
{
  "data": {
    "patterns": [
      {
        "id": "pattern_bot_orchestration_1",
        "name": "Multi-Bot Coordination via ARTEMIS",
        "description": "Pattern for coordinating multiple bots through ARTEMIS platform",
        "domains": ["AXIS", "PIPE"],
        "applicable_to": {
          "bot_type": ["orchestration", "coordinator"],
          "use_cases": ["cross-domain integration", "workflow automation"]
        },
        "related_adrs": [
          {
            "id": "ADR-005",
            "title": "ARTEMIS as Central Bot Orchestration Platform",
            "status": "accepted"
          }
        ],
        "examples": [
          {
            "bot_name": "axis-orchestration-bot",
            "implementation_file": "repos/axis-orchestration-bot/orchestrator.py"
          }
        ]
      }
    ]
  }
}
```

#### Example 3: Find Architecture Decision Records

**Query**:
```graphql
query FindADRs {
  adrs(
    status: "accepted"
    domains: ["AXIS"]
    tags: ["knowledge-management", "rag"]
  ) {
    id
    title
    status
    created_date
    decision
    consequences
    related_patterns {
      name
    }
    supersedes {
      id
      title
    }
  }
}
```

**Response**:
```json
{
  "data": {
    "adrs": [
      {
        "id": "ADR-002",
        "title": "Hybrid META-KERAGR Architecture for Knowledge Management",
        "status": "accepted",
        "created_date": "2025-11-10",
        "decision": "Implement hybrid approach combining Git repository, KERAGR intelligence, and API service layer",
        "consequences": [
          "Single source of truth in Git",
          "Intelligent retrieval via CAG+RAG",
          "Real-time updates via WebSocket",
          "Cross-domain knowledge access"
        ],
        "related_patterns": [
          {"name": "Knowledge Graph Integration"},
          {"name": "Vector Search"},
          {"name": "Hybrid Retrieval"}
        ],
        "supersedes": null
      }
    ]
  }
}
```

### 7.3 Bot SDK Query Examples

#### Example 1: Simple Search from Bot

```python
from bsw_knowledge_sdk import KnowledgeClient

# Initialize client
client = KnowledgeClient(
    api_url="http://localhost:3108",
    bot_id="axis-framework-bot",
    domain="AXIS",
    auth_token=os.getenv("KNOWLEDGE_API_TOKEN")
)

# Search for documentation
results = await client.search(
    "How to integrate with ARTEMIS platform?"
)

# Process results
for result in results['results']:
    print(f"Title: {result['title']}")
    print(f"Relevance: {result['relevance_score']}")
    print(f"Excerpt: {result['excerpt']}")
    print("---")
```

#### Example 2: Graph Query from Bot

```python
# Find all bots that integrate with ARTEMIS
bots = await client.graph_query("""
    MATCH (bot:Bot)-[:INTEGRATES_WITH]->(platform:Platform {name: 'ARTEMIS'})
    RETURN bot.name, bot.domain, bot.api_endpoint, bot.status
    ORDER BY bot.domain, bot.name
""")

# Results
for bot in bots['results']:
    print(f"{bot['bot.domain']}/{bot['bot.name']}: {bot['bot.api_endpoint']}")
```

#### Example 3: Real-Time Updates Subscription

```python
# Subscribe to knowledge updates
async def on_update(update):
    print(f"Knowledge updated: {update['type']}")
    print(f"Affected domains: {update['domains']}")

    # Refresh local cache
    await refresh_knowledge_cache()

await client.subscribe_to_updates(
    domains=["AXIS", "PIPE"],
    on_update=on_update
)

# Bot continues running, receiving updates in real-time
```

### 7.4 Complex Multi-Domain Queries

#### Example 4: Cross-Domain Integration Discovery

**GraphQL Query**:
```graphql
query CrossDomainIntegration {
  findIntegrationPath(
    from_bot: "axis-framework-bot"
    to_service: "ARTEMIS"
    max_hops: 3
  ) {
    path {
      node {
        name
        type
      }
      relationship
    }
    total_hops
    confidence_score
  }
}
```

**Use Case**: Discover how `axis-framework-bot` connects to ARTEMIS through intermediate services.

#### Example 5: Technology Stack Discovery

**GraphQL Query**:
```graphql
query TechnologyStack {
  domain(name: "PIPE") {
    technology_stack {
      category
      technologies {
        name
        version
        purpose
        used_by_bots {
          name
        }
      }
    }
  }
}
```

**Use Case**: Understand complete technology stack for PIPE domain.

---

## 8. Deployment Instructions

### 8.1 Prerequisites

**System Requirements**:
- Qubes OS AppVM (bsw-gov, bsw-arch, or bsw-tech)
- 8GB RAM minimum (16GB recommended)
- 50GB free disk space (for Neo4j, FAISS, MongoDB)
- Podman installed
- Python 3.13
- Git

**Installed Tools**:
```bash
# Check prerequisites
python3 --version  # 3.13+
podman --version   # 4.0+
git --version      # 2.40+

# Install additional tools
sudo dnf install -y python3-pip rsync
pip3 install sentence-transformers faiss-cpu neo4j motor pyyaml pandas openpyxl
```

### 8.2 Step-by-Step Deployment

#### Step 1: Create Git Repository

```bash
# Clone from template or create new
cd ~/Projects
git clone https://codeberg.org/BSW-Docs/bsw-documentation.git

# Or create from scratch
mkdir -p ~/bsw-documentation
cd ~/bsw-documentation
git init
git remote add origin https://codeberg.org/BSW-Docs/bsw-documentation.git
```

#### Step 2: Set Up Directory Structure

```bash
# Run structure creation script
/home/user/scripts/create-knowledge-repo.sh

# Or manually:
cd ~/bsw-documentation
mkdir -p docs/{architecture,governance,domains,bots,cag-kerag,gitops,infrastructure}
mkdir -p knowledge/{entities,relationships,taxonomies,decisions}
mkdir -p data/{schemas}
mkdir -p wikis
mkdir -p scripts
mkdir -p .forgejo/workflows
```

#### Step 3: Migrate Documentation

```bash
# Migrate from bsw-gov
rsync -av /home/user/QubesIncoming/bsw-gov/*.md ~/bsw-documentation/docs/architecture/

# Migrate CAG-KERAG docs
rsync -av "/home/user/QubesIncoming/bsw-gov/CAG - KERAG - COGNEE/" \
    ~/bsw-documentation/docs/cag-kerag/
```

#### Step 4: Convert Excel Files

```bash
# Run conversion script
/home/user/scripts/convert-excel-to-yaml.py

# Verify output
ls -lh ~/bsw-documentation/data/*.yaml
```

#### Step 5: Consolidate Wikis

```bash
# Run wiki consolidation
/home/user/scripts/consolidate-wikis.sh

# Check results
find ~/bsw-documentation/wikis -name "meta.yaml" | wc -l
# Should show 50+ files
```

#### Step 6: Commit Initial Repository

```bash
cd ~/bsw-documentation

git add .
git commit -m "Initial knowledge base migration

- Migrated all documentation from bsw-gov
- Converted Excel files to YAML
- Consolidated 50+ bot wikis
- Created structured knowledge base

🤖 Generated with Claude Code"

git push origin main
```

#### Step 7: Deploy Neo4j

```bash
# Create Neo4j deployment
mkdir -p ~/services/meta-keragr/neo4j/{data,import}

# Create docker-compose.yaml for Neo4j
cat > ~/services/meta-keragr/docker-compose.neo4j.yaml <<'EOF'
version: '3.8'

services:
  neo4j:
    image: neo4j:5-community
    container_name: meta-keragr-neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_apoc_export_file_enabled=true
      - NEO4J_apoc_import_file_enabled=true
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - ./neo4j/data:/data
      - ./neo4j/import:/import
    restart: unless-stopped
EOF

# Start Neo4j
export NEO4J_PASSWORD="your_secure_password_here"
cd ~/services/meta-keragr
podman-compose -f docker-compose.neo4j.yaml up -d

# Verify
curl http://localhost:7474
```

#### Step 8: Deploy MongoDB

```bash
# Create MongoDB deployment
cat > ~/services/meta-keragr/docker-compose.mongodb.yaml <<'EOF'
version: '3.8'

services:
  mongodb:
    image: mongo:6
    container_name: meta-keragr-mongodb
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
    volumes:
      - ./mongodb/data:/data/db
    restart: unless-stopped
EOF

# Start MongoDB
export MONGO_PASSWORD="your_secure_password_here"
podman-compose -f docker-compose.mongodb.yaml up -d

# Verify
podman exec -it meta-keragr-mongodb mongosh --eval "db.version()"
```

#### Step 9: Generate Initial Embeddings

```bash
# Generate FAISS index
mkdir -p ~/services/meta-keragr/faiss/{indices,metadata}

/home/user/scripts/generate-embeddings.py

# This will take 10-20 minutes depending on doc count
# Progress will be shown
```

#### Step 10: Populate Knowledge Graph

```bash
# Create initial knowledge graph entities
/home/user/scripts/update-knowledge-graph.py

# Verify in Neo4j browser
# Open http://localhost:7474
# Run: MATCH (n) RETURN count(n)
```

#### Step 11: Deploy META-KERAGR API

```bash
# Create API service
mkdir -p ~/services/meta-keragr/api/{routers,models,services}

# Copy implementation files (from Phase 3 work)
# ... API implementation ...

# Create docker-compose for API
cat > ~/services/meta-keragr/docker-compose.api.yaml <<'EOF'
version: '3.8'

services:
  api:
    build: ./api
    container_name: meta-keragr-api
    ports:
      - "3108:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - MONGODB_URI=mongodb://admin:${MONGO_PASSWORD}@mongodb:27017
      - FAISS_INDEX_PATH=/faiss/knowledge_base.index
    volumes:
      - ./faiss:/faiss:ro
    depends_on:
      - neo4j
      - mongodb
    restart: unless-stopped
    networks:
      - meta-keragr

networks:
  meta-keragr:
    driver: bridge
EOF

# Start API
podman-compose -f docker-compose.api.yaml up -d

# Verify
curl http://localhost:3108/health
```

#### Step 12: Deploy Bot SDK

```bash
# Install SDK system-wide or in venv
pip3 install ~/packages/bsw-knowledge-sdk

# Or for development
pip3 install -e ~/packages/bsw-knowledge-sdk
```

#### Step 13: Set Up Auto-Sync

```bash
# Install sync scripts
sudo cp /home/user/scripts/sync-scheduler.sh /usr/local/bin/
sudo cp /home/user/scripts/sync-knowledge-base.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/sync-*.sh

# Add cron job
crontab -e

# Add this line:
*/15 * * * * /usr/local/bin/sync-scheduler.sh >> /var/log/knowledge-sync.log 2>&1

# Test sync manually
/usr/local/bin/sync-knowledge-base.sh
```

#### Step 14: Integrate First Bot

```bash
# Example: axis-framework-bot integration

# 1. Add SDK to bot requirements
cd ~/Code/axis-framework-bot
echo "bsw-knowledge-sdk" >> requirements.txt
pip3 install -r requirements.txt

# 2. Add knowledge client to bot
# Edit bot code to add KnowledgeClient

# 3. Set environment variables
cat >> .env <<EOF
KNOWLEDGE_API_URL=http://localhost:3108
KNOWLEDGE_API_TOKEN=your_bot_token_here
EOF

# 4. Test integration
python3 -c "
from bsw_knowledge_sdk import KnowledgeClient
import asyncio

async def test():
    client = KnowledgeClient(
        api_url='http://localhost:3108',
        bot_id='axis-framework-bot',
        domain='AXIS',
        auth_token='your_bot_token_here'
    )
    results = await client.search('ARTEMIS integration')
    print(f'Found {len(results[\"results\"])} results')

asyncio.run(test())
"
```

#### Step 15: Monitor and Verify

```bash
# Check all services are running
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Expected output:
# meta-keragr-api       Up 5 minutes    0.0.0.0:3108->8000/tcp
# meta-keragr-neo4j     Up 10 minutes   0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
# meta-keragr-mongodb   Up 10 minutes   0.0.0.0:27017->27017/tcp

# Check logs
podman logs meta-keragr-api
podman logs meta-keragr-neo4j
podman logs meta-keragr-mongodb

# Run health check
/home/user/scripts/sync-healthcheck.py
```

### 8.3 Production Checklist

- [ ] Git repository created and initialised
- [ ] All documentation migrated
- [ ] Excel files converted to YAML
- [ ] Bot wikis consolidated
- [ ] Neo4j deployed and populated
- [ ] MongoDB deployed and indexed
- [ ] FAISS embeddings generated
- [ ] META-KERAGR API deployed and healthy
- [ ] Bot SDK installed
- [ ] Auto-sync cron job configured
- [ ] First bot integrated and tested
- [ ] WebSocket updates working
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backups configured

### 8.4 Backup and Recovery

**Backup Strategy**:

```bash
#!/bin/bash
# /home/user/scripts/backup-knowledge-base.sh

BACKUP_DIR="/rw/backup/knowledge-base"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# 1. Backup Git repository
cd ~/bsw-documentation
git bundle create "$BACKUP_DIR/$DATE/bsw-docs.bundle" --all

# 2. Backup Neo4j data
podman exec meta-keragr-neo4j neo4j-admin database dump neo4j \
    --to=/backup/neo4j-$DATE.dump
podman cp meta-keragr-neo4j:/backup/neo4j-$DATE.dump \
    "$BACKUP_DIR/$DATE/"

# 3. Backup MongoDB
podman exec meta-keragr-mongodb mongodump \
    --archive=/backup/mongodb-$DATE.archive \
    --gzip
podman cp meta-keragr-mongodb:/backup/mongodb-$DATE.archive \
    "$BACKUP_DIR/$DATE/"

# 4. Backup FAISS index
tar czf "$BACKUP_DIR/$DATE/faiss-index.tar.gz" \
    ~/services/meta-keragr/faiss/

# 5. Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR/$DATE"
```

**Recovery**:

```bash
#!/bin/bash
# /home/user/scripts/restore-knowledge-base.sh

BACKUP_DATE="$1"  # Pass backup date as argument
BACKUP_DIR="/rw/backup/knowledge-base/$BACKUP_DATE"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup not found: $BACKUP_DIR"
    exit 1
fi

# 1. Restore Git repository
cd ~
git clone "$BACKUP_DIR/bsw-docs.bundle" bsw-documentation

# 2. Restore Neo4j
podman cp "$BACKUP_DIR/neo4j-*.dump" \
    meta-keragr-neo4j:/backup/
podman exec meta-keragr-neo4j neo4j-admin database load neo4j \
    --from=/backup/neo4j-*.dump

# 3. Restore MongoDB
podman cp "$BACKUP_DIR/mongodb-*.archive" \
    meta-keragr-mongodb:/backup/
podman exec meta-keragr-mongodb mongorestore \
    --archive=/backup/mongodb-*.archive \
    --gzip

# 4. Restore FAISS index
tar xzf "$BACKUP_DIR/faiss-index.tar.gz" -C ~/services/meta-keragr/

echo "Restore completed from: $BACKUP_DIR"
```

---

## 9. Architecture Diagrams

### 9.1 Overall System Architecture

```mermaid
graph TB
    subgraph "Layer 1: Source of Truth"
        Git[Git Repository<br/>codeberg.org/BSW-Docs/bsw-documentation]
        LocalDocs[Local Docs<br/>/home/user/QubesIncoming/bsw-gov]
        BotWikis[Bot Wikis<br/>/home/user/Code/*/wiki]
        ExcelData[Excel Files<br/>*.xlsx]
    end

    subgraph "Layer 2: Knowledge Storage"
        Neo4j[(Neo4j<br/>Knowledge Graph<br/>Port 7687)]
        MongoDB[(MongoDB<br/>Document Store<br/>Port 27017)]
        FAISS[(FAISS<br/>Vector Index<br/>File-based)]
    end

    subgraph "Layer 3: Intelligence (KERAGR)"
        CAG[CAG Layer<br/>Context-Aware Generation]
        RAG[RAG Layer<br/>Hybrid Retrieval]
    end

    subgraph "Layer 4: API Service"
        REST[REST API<br/>/api/v1/knowledge/*]
        GraphQL[GraphQL API<br/>/graphql]
        WebSocket[WebSocket<br/>/ws/knowledge/updates]
    end

    subgraph "Layer 5: Bot Consumers"
        AXIS_Bots[AXIS Bots<br/>30 agents]
        PIPE_Bots[PIPE Bots<br/>46+ agents]
        IV_Bots[IV Bots<br/>TBD]
        ECO_Bots[ECO Bots<br/>TBD]
    end

    LocalDocs -->|Auto-sync| Git
    BotWikis -->|Auto-sync| Git
    ExcelData -->|Convert| Git

    Git -->|Populate| Neo4j
    Git -->|Index| MongoDB
    Git -->|Embed| FAISS

    Neo4j --> RAG
    MongoDB --> RAG
    FAISS --> RAG

    CAG --> RAG
    RAG --> REST
    RAG --> GraphQL
    RAG --> WebSocket

    REST --> AXIS_Bots
    REST --> PIPE_Bots
    GraphQL --> AXIS_Bots
    GraphQL --> IV_Bots
    WebSocket --> AXIS_Bots
    WebSocket --> PIPE_Bots
    WebSocket --> ECO_Bots
```

### 9.2 Synchronisation Flow

```mermaid
sequenceDiagram
    participant Cron as Cron Scheduler<br/>(Every 15 min)
    participant Sync as Sync Script
    participant Git as Git Repo
    participant Neo4j as Neo4j
    participant Mongo as MongoDB
    participant FAISS as FAISS
    participant API as META-KERAGR API
    participant Bots as Connected Bots

    Cron->>Sync: Trigger sync
    Sync->>Sync: Check local files

    alt Files changed
        Sync->>Git: rsync docs
        Sync->>Git: rsync wikis
        Sync->>Git: Convert Excel
        Sync->>Git: git commit + push

        Git->>Neo4j: Trigger update
        Git->>Mongo: Index new docs
        Git->>FAISS: Generate embeddings

        Note over Neo4j,FAISS: Parallel updates

        Neo4j->>API: Update complete
        Mongo->>API: Index complete
        FAISS->>API: Embeddings complete

        API->>Bots: WebSocket notification
        Bots->>Bots: Invalidate cache
        Bots->>API: Refresh knowledge
    else No changes
        Sync->>Sync: Skip update
    end
```

### 9.3 Bot Query Flow

```mermaid
graph TB
    Bot[Bot: axis-framework-bot]
    SDK[Knowledge SDK]
    Cache[Local Cache]
    API[META-KERAGR API]

    subgraph "CAG Layer"
        ContextMgr[Context Manager]
        QueryClassifier[Query Classifier]
        DomainRouter[Domain Router]
    end

    subgraph "RAG Layer"
        VectorSearch[Vector Search<br/>FAISS]
        GraphSearch[Graph Search<br/>Neo4j]
        DocSearch[Document Search<br/>MongoDB]
        Fusion[Knowledge Fusion]
    end

    Bot -->|1. Query| SDK
    SDK -->|2. Check cache| Cache

    Cache -->|3a. Cache hit| SDK
    Cache -->|3b. Cache miss| API

    API --> ContextMgr
    ContextMgr --> QueryClassifier
    QueryClassifier --> DomainRouter

    DomainRouter --> VectorSearch
    DomainRouter --> GraphSearch
    DomainRouter --> DocSearch

    VectorSearch --> Fusion
    GraphSearch --> Fusion
    DocSearch --> Fusion

    Fusion --> API
    API -->|4. Results| SDK
    SDK -->|5. Cache + Return| Cache
    SDK -->|6. Results| Bot
```

### 9.4 Knowledge Graph Schema

```mermaid
graph LR
    Bot[Bot]
    Domain[Domain]
    Service[Service]
    API[API]
    Pattern[Pattern]
    ADR[ADR]
    Technology[Technology]

    Bot -->|PART_OF| Domain
    Bot -->|INTEGRATES_WITH| Service
    Bot -->|EXPOSES| API
    Bot -->|IMPLEMENTS| Pattern
    Bot -->|USES| Technology

    Pattern -->|DOCUMENTED_IN| ADR
    Pattern -->|APPLIES_TO| Domain

    Service -->|DEPLOYED_ON| Domain
    Service -->|DEPENDS_ON| Technology

    API -->|CONSUMED_BY| Bot

    Domain -->|HIGH_INTEGRATION| Domain
    Domain -->|LOW_INTEGRATION| Domain
```

---

## 10. Migration and Rollout

### 10.1 Phased Rollout Plan

**Phase 1: Foundation (Weeks 1-2)**
- Create Git repository
- Migrate documentation
- Set up infrastructure (Neo4j, MongoDB, FAISS)
- Deploy initial sync

**Phase 2: AXIS Domain (Week 3)**
- Integrate 5 priority AXIS bots:
  1. axis-framework-bot ✅ (already production)
  2. axis-docs-bot
  3. axis-compliance-bot
  4. axis-monitoring-bot
  5. axis-security-bot
- Test cross-bot knowledge sharing
- Validate real-time updates

**Phase 3: PIPE Domain (Week 4)**
- Integrate 5 priority PIPE bots:
  1. pipe-api-bot (PAPI)
  2. pipe-integration-bot (PINT)
  3. pipe-artifact-bot (PART)
  4. pipe-deployment-bot
  5. pipe-monitoring-bot
- Test cross-domain queries (AXIS ↔ PIPE)

**Phase 4: Full Rollout (Weeks 5-8)**
- Integrate remaining AXIS bots (25 bots)
- Integrate remaining PIPE bots (41+ bots)
- Integrate IV bots (as developed)
- Integrate ECO bots (as developed)

**Phase 5: Optimisation (Weeks 9-10)**
- Performance tuning
- Cache optimisation
- Query response time improvement
- Knowledge graph enrichment

### 10.2 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Query Response Time** | < 2 seconds | API latency monitoring |
| **Knowledge Freshness** | < 15 minutes | Last sync timestamp |
| **Bot Adoption** | 80% of bots | SDK integration count |
| **Cache Hit Rate** | > 70% | Cache statistics |
| **Search Relevance** | > 0.85 | User feedback + scoring |
| **System Uptime** | 99.5% | Health check monitoring |
| **Sync Success Rate** | > 99% | Sync error logs |

### 10.3 Rollback Plan

**If critical issues occur:**

1. **Stop auto-sync**:
   ```bash
   crontab -e
   # Comment out sync-scheduler line
   ```

2. **Revert to previous Git commit**:
   ```bash
   cd ~/bsw-documentation
   git log  # Find last good commit
   git revert <commit-hash>
   git push origin main
   ```

3. **Restore from backup**:
   ```bash
   /home/user/scripts/restore-knowledge-base.sh <backup_date>
   ```

4. **Disable bot integrations**:
   ```bash
   # In each bot's .env file
   KNOWLEDGE_API_URL=""  # Empty = disabled
   ```

5. **Continue with manual documentation** until issue resolved

---

## Appendices

### Appendix A: Technology Decisions

| Decision | Rationale |
|----------|-----------|
| **Git as Source of Truth** | Version control, auditable, distributed, familiar workflow |
| **Codeberg** | European FOSS, GDPR-compliant, digital sovereignty |
| **Neo4j for Knowledge Graph** | Industry standard, powerful querying, good Python support |
| **FAISS for Vector Search** | Fast, lightweight, no separate server needed |
| **MongoDB for Documents** | Flexible schema, full-text search, JSON-native |
| **FastAPI for API** | Modern, fast, auto-documentation, async support |
| **Chainguard Wolfi for Containers** | Minimal attack surface, FOSS, secure by default |
| **WebSocket for Updates** | Real-time, efficient, bidirectional communication |

### Appendix B: Security Considerations

**Authentication**:
- JWT tokens for bot authentication
- Token per bot (not shared)
- Token rotation supported
- Admin tokens for management endpoints

**Authorisation**:
- Domain-based access control
- Bots can only query their allowed domains
- Admin endpoints require elevated privileges

**Data Security**:
- TLS for all HTTP/WebSocket connections
- No secrets in Git repository
- Secrets managed via Vault/OpenBao
- Encrypted backups

**Network Security**:
- API only accessible within AppVM
- Optional: Reverse proxy with authentication
- Rate limiting on API endpoints

### Appendix C: Performance Optimisation

**Caching**:
- Bot-level caching (60-minute TTL)
- API-level Redis cache (15-minute TTL)
- FAISS index in memory
- MongoDB connection pooling

**Indexing**:
- Neo4j: Index on entity names and IDs
- MongoDB: Text indexes on content
- FAISS: Pre-computed embeddings

**Query Optimisation**:
- GraphQL query depth limiting
- Result set size limits
- Pagination for large results
- Lazy loading of relationships

### Appendix D: Glossary

- **CAG**: Context-Aware Generation
- **RAG**: Retrieval-Augmented Generation
- **KERAGR**: Knowledge Enhanced RAG (with R for Retrieval)
- **Meta-KERAGR**: Meta-level KERAGR system for multi-domain knowledge
- **ADR**: Architecture Decision Record
- **FAISS**: Facebook AI Similarity Search
- **Neo4j**: Graph database
- **YAML**: YAML Ain't Markup Language
- **SDK**: Software Development Kit

---

## Document Metadata

**Title**: BOTS Knowledge Base Architecture
**Version**: 1.0
**Date**: 2025-11-10
**Author**: Claude Code (Sonnet 4.5)
**Classification**: Technical Architecture
**Status**: Design Complete - Ready for Implementation
**Distribution**: BSW Team, AXIS Teams, PIPE Teams, IV Teams, ECO Teams

**Dependencies**:
- Existing CAG-KERAG documentation
- Bot factory architecture
- GitOps infrastructure
- Multi-AppVM coordination

**Next Steps**:
1. Review and approve architecture
2. Create Git repository on Codeberg
3. Begin Phase 1 implementation
4. Integrate first 5 AXIS bots
5. Measure and optimise

---

## End of Document

This comprehensive architecture provides a complete blueprint for implementing a unified knowledge base system that all BSW bots can continuously read, analyse, and access. The hybrid META-KERAGR approach combines the reliability of Git-based source control with the intelligence of CAG+RAG systems and the accessibility of modern API patterns.

For questions or implementation support, refer to the specific sections above or consult the BSW architecture team.
