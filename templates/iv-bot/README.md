# IV Bot Template with Knowledge Graph Integration

This template provides a complete starting point for creating IV (Intelligence/Validation) domain bots integrated with the BSW-Arch AI Development Platform.

## Features

- ✅ Neo4j Knowledge Graph integration
- ✅ ChromaDB vector store for embeddings
- ✅ Ollama local LLM integration
- ✅ RAG (Retrieval-Augmented Generation) support
- ✅ Continuous learning from feedback
- ✅ FAGAM-compliant (no prohibited dependencies)
- ✅ Minimal container image (<50MB base)
- ✅ Non-root user execution
- ✅ Health checks included

## Quick Start

### 1. Copy Template

```bash
# Create your bot directory
mkdir -p /path/to/my-iv-bot
cd /path/to/my-iv-bot

# Copy template files
cp /home/user/bsw-arch/templates/iv-bot/* .
```

### 2. Customize Configuration

Edit `config.yaml` to customize your bot:

```yaml
bot_name: "my-custom-bot"
bot_type: "intelligence"  # or validation, rag, ai-ml, etc.
```

### 3. Implement Bot Logic

Edit `bot_main.py` to add your custom logic:

```python
class MyIVBot(IVBot):
    """Custom IV Bot implementation"""

    async def custom_function(self):
        """Your custom bot logic here"""
        result = await self.query_knowledge_graph("my query")
        # Process result...
        return result
```

### 4. Build Container

```bash
# Build the Docker image
docker build -t my-iv-bot:latest .

# Or using podman
podman build -t my-iv-bot:latest .
```

### 5. Run Bot

#### Option A: Standalone (with external services)

```bash
docker run -d \
  --name my-iv-bot \
  -e NEO4J_URI=bolt://neo4j:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=your-password \
  -e CHROMA_HOST=chromadb \
  -e CHROMA_PORT=8000 \
  -e OLLAMA_HOST=http://ollama:11434 \
  my-iv-bot:latest
```

#### Option B: Docker Compose (recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.13.0
    environment:
      NEO4J_AUTH: neo4j/bsw-arch-neo4j-2025
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j-data:/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma-data:/chroma/chroma

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

  my-iv-bot:
    build: .
    depends_on:
      - neo4j
      - chromadb
      - ollama
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: bsw-arch-neo4j-2025
      CHROMA_HOST: chromadb
      CHROMA_PORT: 8000
      OLLAMA_HOST: http://ollama:11434

volumes:
  neo4j-data:
  chroma-data:
  ollama-data:
```

Run the stack:

```bash
docker-compose up -d
```

## Bot Types

Choose the appropriate `bot_type` in your config:

### AI/ML Bots
- `ai-ml`: Machine learning model management
- `ml-pipeline`: ML pipeline orchestration
- `model-training`: Model training and evaluation

### Knowledge Management
- `knowledge`: Knowledge base management
- `doc-scanner`: Documentation scanning and indexing
- `knowledge-sync`: Cross-domain knowledge synchronization

### Data Analysis
- `data-analysis`: Data analysis and insights
- `data-quality`: Data quality validation
- `data-pipeline`: Data pipeline management

### Validation
- `validation`: General validation
- `schema-validator`: Schema validation
- `compliance-check`: Compliance checking

### NLP
- `nlp`: Natural language processing
- `sentiment-analysis`: Sentiment analysis
- `entity-extraction`: Entity extraction

### RAG
- `rag`: RAG query processing
- `retrieval`: Document retrieval
- `context-builder`: Context building

### Recommendations
- `recommendations`: Recommendation engine
- `similarity`: Similarity matching

### Conversational AI
- `conversational`: Conversational interface
- `chatbot`: Chatbot functionality

## Knowledge Graph Integration

### Query Knowledge Graph

```python
async def example_query():
    bot = IVBot()
    await bot.initialize()

    # Query with vector search
    result = await bot.query_knowledge_graph(
        query="find IV bot architecture",
        use_vector_search=True,
        max_results=5
    )

    print(f"Found {len(result['vector_results'])} vector results")
    print(f"Found {len(result['graph_results'])} graph results")
```

### RAG Query

```python
async def example_rag():
    bot = IVBot()
    await bot.initialize()

    # RAG query with LLM
    result = await bot.rag_query(
        question="How do IV bots integrate with the knowledge graph?",
        use_ollama=True
    )

    print(f"Answer: {result['answer']}")
```

### Continuous Learning

```python
async def example_learning():
    bot = IVBot()
    await bot.initialize()

    # Get response
    result = await bot.rag_query("some question")

    # Collect user feedback
    await bot.learn_from_feedback(
        query="some question",
        response=result['answer'],
        feedback={"rating": 5, "helpful": True}
    )
```

## Advanced Customization

### Custom Embedding Model

```python
class MyIVBot(IVBot):
    def __init__(self, config_path="config.yaml"):
        super().__init__(config_path)
        # Use different embedding model
        self.embedder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
```

### Custom Graph Queries

```python
async def custom_graph_query(self):
    """Custom Cypher query"""
    async with self.neo4j_driver.session() as session:
        result = await session.run("""
            MATCH (bot:Bot)-[:IMPLEMENTS]->(spec:Specification)
            WHERE bot.domain = 'IV'
            RETURN bot, spec
        """)

        async for record in result:
            print(record["bot"], record["spec"])
```

### Multi-Bot Collaboration

```python
class CollaborativeBot(IVBot):
    async def collaborate_with_bot(self, other_bot_id: str, query: str):
        """Collaborate with another bot via knowledge graph"""
        # Query shared knowledge
        result = await self.query_knowledge_graph(query)

        # Store collaboration in graph
        async with self.neo4j_driver.session() as session:
            await session.run("""
                MATCH (b1:Bot {id: $bot1}), (b2:Bot {id: $bot2})
                CREATE (b1)-[:COLLABORATED_WITH {
                    query: $query,
                    timestamp: timestamp()
                }]->(b2)
            """, bot1=self.bot_name, bot2=other_bot_id, query=query)
```

## Deployment

### Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-iv-bot
  namespace: iv-bots
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-iv-bot
  template:
    metadata:
      labels:
        app: my-iv-bot
        domain: IV
    spec:
      containers:
      - name: my-iv-bot
        image: my-iv-bot:latest
        env:
        - name: NEO4J_URI
          value: "bolt://neo4j.default.svc.cluster.local:7687"
        - name: NEO4J_USER
          valueFrom:
            secretKeyRef:
              name: neo4j-auth
              key: username
        - name: NEO4J_PASSWORD
          valueFrom:
            secretKeyRef:
              name: neo4j-auth
              key: password
        - name: CHROMA_HOST
          value: "chromadb.default.svc.cluster.local"
        - name: OLLAMA_HOST
          value: "http://ollama.default.svc.cluster.local:11434"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python3
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 10
          periodSeconds: 30
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

## Testing

### Unit Tests

Create `test_bot.py`:

```python
import pytest
from bot_main import IVBot

@pytest.mark.asyncio
async def test_initialization():
    bot = IVBot()
    await bot.initialize()
    assert bot.neo4j_driver is not None
    await bot.cleanup()

@pytest.mark.asyncio
async def test_query():
    bot = IVBot()
    await bot.initialize()
    result = await bot.query_knowledge_graph("test query")
    assert "combined_context" in result
    await bot.cleanup()
```

Run tests:

```bash
pytest test_bot.py
```

## Monitoring

### Health Check Endpoint

Add to `bot_main.py`:

```python
from aiohttp import web

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({"status": "healthy"})

# Add to bot initialization
app = web.Application()
app.router.add_get('/health', health_check)
runner = web.AppRunner(app)
await runner.setup()
site = web.TCPSite(runner, '0.0.0.0', 8080)
await site.start()
```

### Metrics

Track bot metrics in Neo4j:

```python
async def record_metric(self, metric_name: str, value: float):
    """Record bot metric"""
    async with self.neo4j_driver.session() as session:
        await session.run("""
            CREATE (m:Metric {
                bot: $bot,
                name: $name,
                value: $value,
                timestamp: timestamp()
            })
        """, bot=self.bot_name, name=metric_name, value=value)
```

## Troubleshooting

### Connection Issues

```bash
# Check Neo4j connectivity
docker exec my-iv-bot python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://neo4j:7687', auth=('neo4j', 'password'))
driver.verify_connectivity()
print('Neo4j OK')
"

# Check ChromaDB connectivity
docker exec my-iv-bot python3 -c "
import chromadb
client = chromadb.HttpClient(host='chromadb', port=8000)
print(f'ChromaDB OK: {client.heartbeat()}')
"
```

### View Logs

```bash
docker logs my-iv-bot -f
```

### Debugging

Enable debug logging in `config.yaml`:

```yaml
logging:
  level: "DEBUG"
```

## Best Practices

1. **Security**
   - Always use environment variables for sensitive data
   - Run as non-root user
   - Keep base image updated

2. **Performance**
   - Cache frequent queries
   - Use connection pooling
   - Limit concurrent queries

3. **Reliability**
   - Implement proper error handling
   - Add retry logic for transient failures
   - Monitor resource usage

4. **Maintainability**
   - Document custom logic
   - Write unit tests
   - Use semantic versioning

## Support

For issues or questions:
- Documentation: `/home/user/bsw-arch/docs/guides/setup/IV-BOTS-SETUP.md`
- Knowledge Graph Guide: `/home/user/bsw-arch/docs/guides/integration/OPENCODE-OPENSPEC-GRAPH-RAG-INTEGRATION.md`
- BSW-Arch Repository: https://codeberg.org/bsw-arch

## License

Part of BSW-Arch AI Development Platform
