# Cognee Integration Guide

Complete guide to integrating Cognee AI knowledge graph and memory system into PIPE.

## What is Cognee?

Cognee is an open-source AI memory layer that transforms documents and data into a living knowledge graph. It provides persistent memory for AI agents through:
- **Extract-Cognify-Load (ECL)** pipeline
- **Knowledge graph** with temporal awareness
- **Vector search** for semantic queries
- **Graph relationships** for connected insights

## Why Cognee for PIPE?

- **Institutional Memory**: Remember all governance decisions and integration reviews
- **Contextual Decisions**: Bots make decisions based on historical patterns
- **Trend Analysis**: Analyze compliance trends over time
- **Knowledge Discovery**: Find connections between domains and integrations
- **Audit Trail**: Complete knowledge graph of system evolution

## Architecture

```
┌──────────────────────────────────────────────────┐
│         PIPE Domain Events                       │
│  • Integration approvals                         │
│  • Governance decisions                          │
│  • Compliance violations                         │
│  • Bot actions                                   │
└────────────────┬─────────────────────────────────┘
                 │
                 │ Events published to
                 ▼
┌──────────────────────────────────────────────────┐
│         EventBus                                 │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│    CogneeMemoryBot                               │
│  ┌────────────────────────────────────────────┐  │
│  │  Extract                                   │  │
│  │  - Parse events                            │  │
│  │  - Chunk data                              │  │
│  │  - Extract entities                        │  │
│  └────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────┐  │
│  │  Cognify                                   │  │
│  │  - Build knowledge graph                   │  │
│  │  - Generate embeddings                     │  │
│  │  - Add temporal context                    │  │
│  └────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────┐  │
│  │  Load                                      │  │
│  │  - Store in graph DB (Memgraph)           │  │
│  │  - Store in vector DB (LanceDB)           │  │
│  │  - Index for search                       │  │
│  └────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
    ┌────▼─────┐    ┌────▼──────┐
    │Knowledge │    │  Vector   │
    │  Graph   │    │  Store    │
    │(Memgraph)│    │(LanceDB)  │
    └──────────┘    └───────────┘
```

## Installation

### Step 1: Install Cognee

```bash
# Install cognee
pip install cognee

# Or add to requirements.txt
echo "cognee>=0.2.0" >> requirements.txt
echo "lancedb>=0.5.0" >> requirements.txt
echo "memgraph>=1.4.0" >> requirements.txt
pip install -r requirements.txt
```

### Step 2: Install Backend Databases

#### Option A: LanceDB (Simple, embedded)

```bash
# LanceDB is already included with cognee
# No additional setup needed
```

#### Option B: Memgraph (Advanced, graph-native)

```bash
# Using Docker
docker run -p 7687:7687 -p 7444:7444 \
  --name memgraph \
  -v mg_lib:/var/lib/memgraph \
  memgraph/memgraph-platform
```

### Step 3: Configure Cognee

Create `config/cognee_config.yaml`:

```yaml
cognee:
  # Backend configuration
  vector_db:
    type: lancedb  # or 'memgraph'
    path: ./data/cognee/vectors

  graph_db:
    type: memgraph  # or 'networkx' for simple graphs
    host: localhost
    port: 7687
    username: ""
    password: ""

  # LLM for cognification
  llm:
    provider: anthropic  # or 'openai'
    model: claude-3-sonnet-20240229
    api_key: ${ANTHROPIC_API_KEY}
    temperature: 0.0

  # Embedding model
  embeddings:
    provider: openai
    model: text-embedding-3-small
    api_key: ${OPENAI_API_KEY}

  # Processing settings
  processing:
    chunk_size: 512
    chunk_overlap: 50
    temporal_aware: true  # Enable time-aware graph

  # Cognification rules
  cognification:
    extract_entities: true
    extract_relationships: true
    add_metadata: true
    enable_reasoning: false  # Advanced feature
```

## Implementation

### Step 1: Create Cognee Memory Bot

Create `src/bots/cognee_memory_bot.py`:

```python
"""Cognee Memory Bot - Builds knowledge graph from PIPE events."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import cognee
from pathlib import Path

from src.core.bot_base import BotBase
from src.core.event_bus import Event, EventBus
from src.core.state_manager import StateManager
from src.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class CogneeMemoryBot(BotBase):
    """Bot that cognifies PIPE events into knowledge graph."""

    def __init__(
        self,
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: Optional[MetricsCollector] = None,
        config_file: str = "config/cognee_config.yaml"
    ):
        super().__init__(
            "CogneeMemory",
            event_bus,
            state_manager,
            metrics
        )
        self.config_file = Path(config_file)
        self.cognified_events = set()

    async def initialize(self) -> None:
        """Initialize Cognee and subscribe to events."""
        await super().initialize()

        # Initialize Cognee
        await self._init_cognee()

        # Subscribe to all events for cognification
        await self.event_bus.subscribe("*", self._handle_event)

        # Subscribe to knowledge queries
        await self.event_bus.subscribe(
            "cognee.query",
            self._handle_query
        )

        self.logger.info("CogneeMemory initialized with knowledge graph")

    async def _init_cognee(self):
        """Initialize Cognee with configuration."""
        # Set Cognee configuration
        cognee.config.set({
            "graph_db_type": "networkx",  # Simple graph for start
            "vector_db_type": "lancedb",
            "llm_provider": "anthropic"
        })

        # Create cognee data directory
        data_dir = Path("./data/cognee")
        data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Cognee initialized")

    async def _handle_event(self, event: Event) -> None:
        """Cognify all domain events into knowledge graph."""
        # Skip cognee's own events to avoid loops
        if event.event_type.startswith("cognee."):
            return

        # Skip if already cognified
        event_id = f"{event.event_type}:{event.source}:{event.timestamp}"
        if event_id in self.cognified_events:
            return

        try:
            # Extract relevant information from event
            document = self._event_to_document(event)

            # Cognify the document
            await cognee.add([document])

            # Mark as cognified
            self.cognified_events.add(event_id)

            self.metrics.increment("cognee.events.cognified")
            self.logger.debug(f"Cognified event: {event.event_type}")

        except Exception as e:
            self.logger.error(f"Failed to cognify event: {e}")
            self.metrics.increment("cognee.events.error")

    def _event_to_document(self, event: Event) -> str:
        """Convert event to document for cognification."""
        # Create structured document from event
        doc = f"""
Event Type: {event.event_type}
Source: {event.source}
Timestamp: {event.timestamp}

Data:
"""
        for key, value in event.data.items():
            doc += f"- {key}: {value}\n"

        # Add metadata
        doc += f"\nMetadata:\n"
        for key, value in event.metadata.items():
            doc += f"- {key}: {value}\n"

        return doc

    async def _handle_query(self, event: Event) -> None:
        """Handle knowledge graph query."""
        query = event.data.get("query")
        request_id = event.data.get("request_id")

        self.logger.info(f"Knowledge query: {query} (request: {request_id})")

        try:
            # Search the knowledge graph
            results = await cognee.search(
                cognee.SearchType.INSIGHTS,
                query
            )

            # Publish results
            await self.event_bus.publish(
                Event(
                    event_type="cognee.query.response",
                    source=self.name,
                    data={
                        "request_id": request_id,
                        "query": query,
                        "results": results,
                        "count": len(results)
                    }
                )
            )

            self.metrics.increment("cognee.queries.success")

        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            await self._publish_error(request_id, str(e))
            self.metrics.increment("cognee.queries.error")

    async def get_governance_insights(
        self, time_period: str = "30d"
    ) -> Dict[str, Any]:
        """Get governance insights from knowledge graph."""
        query = f"What integrations were approved in the last {time_period}?"

        results = await cognee.search(
            cognee.SearchType.INSIGHTS,
            query
        )

        return {
            "query": query,
            "insights": results,
            "period": time_period
        }

    async def get_compliance_trends(
        self, domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get compliance trends over time."""
        if domain:
            query = f"What are the compliance trends for {domain} domain?"
        else:
            query = "What are the overall compliance trends?"

        results = await cognee.search(
            cognee.SearchType.INSIGHTS,
            query
        )

        return {
            "query": query,
            "domain": domain,
            "trends": results
        }

    async def find_similar_integrations(
        self, integration_description: str
    ) -> List[Dict[str, Any]]:
        """Find similar integrations from history."""
        query = f"Find integrations similar to: {integration_description}"

        results = await cognee.search(
            cognee.SearchType.INSIGHTS,
            query
        )

        return results

    async def _publish_error(self, request_id: str, error: str):
        """Publish error event."""
        await self.event_bus.publish(
            Event(
                event_type="cognee.query.error",
                source=self.name,
                data={
                    "request_id": request_id,
                    "error": error
                }
            )
        )

    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        return {
            "total_cognified": len(self.cognified_events),
            "graph_ready": True,
            "backend": "lancedb + networkx"
        }
```

### Step 2: Setup Cognee with Governance

Create `examples/cognee_setup.py`:

```python
"""Setup Cognee integration with PIPE."""

import asyncio
from src.governance.governance_manager import GovernanceManager
from src.core.event_bus import Event, EventBus
from src.core.state_manager import StateManager
from src.bots.cognee_memory_bot import CogneeMemoryBot
from src.utils.metrics import MetricsCollector


async def setup_cognee_integration():
    """Setup Cognee knowledge graph integration."""
    # Initialize components
    event_bus = EventBus()
    state_manager = StateManager()
    metrics = MetricsCollector()
    governance = GovernanceManager()

    print("=== Cognee Knowledge Graph Setup ===\n")

    # Step 1: Register Cognee as a domain
    print("Registering Cognee domain...")
    cognee_domain = await governance.register_domain(
        "COGNEE",
        capabilities=[
            "knowledge_graph",
            "memory_storage",
            "semantic_search",
            "temporal_analysis"
        ],
        compliance_requirements=["data_privacy", "audit_logging"]
    )
    print(f"✓ Cognee domain registered: {cognee_domain['domain_id']}\n")

    # Step 2: Request integrations
    print("Requesting Cognee integrations...")

    # All domains can query Cognee
    domains = ["BNI", "BNP", "AXIS", "IV"]
    integrations = []

    for domain in domains:
        integration = await governance.request_integration(
            source_domain=domain,
            target_domain="COGNEE",
            integration_type="knowledge_query",
            purpose=f"{domain} needs access to historical knowledge"
        )
        integrations.append(integration)
        print(f"✓ {domain} → COGNEE requested: {integration['integration_id']}")

    print()

    # Step 3: Approve integrations
    print("Approving integrations...")
    for integration in integrations:
        governance.review_pipeline.assign_reviewers(
            integration["review_id"],
            ["data-admin@pipe.com"]
        )
        governance.review_pipeline.approve_review(
            integration["review_id"],
            "data-admin@pipe.com"
        )
        await governance.approve_integration(
            integration["integration_id"],
            reviewer="admin@pipe.com",
            notes="Cognee knowledge access approved"
        )
        print(f"✓ Approved: {integration['integration_id']}")

    print("\n=== Starting Cognee Memory Bot ===\n")

    # Step 4: Start Cognee Memory Bot
    cognee_bot = CogneeMemoryBot(event_bus, state_manager, metrics)
    await cognee_bot.initialize()
    print("✓ Cognee Memory Bot running\n")

    # Step 5: Cognify some sample events
    print("Cognifying sample governance events...")

    sample_events = [
        Event(
            event_type="integration.approved",
            source="GOVERNANCE",
            data={
                "integration_id": "INT-001",
                "source_domain": "BNP",
                "target_domain": "BNI",
                "purpose": "Authentication services",
                "approved_by": "admin@pipe.com",
                "approved_at": "2024-01-15T10:00:00Z"
            }
        ),
        Event(
            event_type="compliance.violation",
            source="GOVERNANCE",
            data={
                "domain": "IV",
                "violation_type": "missing_review",
                "severity": "medium",
                "detected_at": "2024-01-20T14:30:00Z"
            }
        ),
        Event(
            event_type="integration.approved",
            source="GOVERNANCE",
            data={
                "integration_id": "INT-002",
                "source_domain": "AXIS",
                "target_domain": "BNP",
                "purpose": "Architecture compliance checks",
                "approved_by": "admin@pipe.com",
                "approved_at": "2024-02-01T09:00:00Z"
            }
        )
    ]

    for event in sample_events:
        await event_bus.publish(event)
        await asyncio.sleep(0.5)  # Allow time for cognification

    print(f"✓ Cognified {len(sample_events)} sample events\n")

    # Step 6: Query the knowledge graph
    print("=== Testing Knowledge Queries ===\n")

    # Query 1: Governance insights
    insights = await cognee_bot.get_governance_insights("30d")
    print("Governance Insights (last 30 days):")
    print(f"  Query: {insights['query']}")
    print(f"  Results: {len(insights['insights'])} insights found\n")

    # Query 2: Find similar integrations
    similar = await cognee_bot.find_similar_integrations(
        "authentication between domains"
    )
    print("Similar Integrations:")
    print(f"  Found: {len(similar)} similar integration(s)\n")

    # Query 3: Knowledge stats
    stats = await cognee_bot.get_knowledge_stats()
    print("Knowledge Graph Stats:")
    print(f"  Total events cognified: {stats['total_cognified']}")
    print(f"  Backend: {stats['backend']}")

    print("\n=== Cognee Setup Complete ===\n")

    return cognee_bot


if __name__ == "__main__":
    asyncio.run(setup_cognee_integration())
```

## Usage Examples

### Example 1: Query Historical Decisions

```python
async def query_past_decisions():
    """Query knowledge graph for past governance decisions."""
    event_bus = EventBus()

    # Ask about past approvals
    await event_bus.publish(
        Event(
            event_type="cognee.query",
            source="BNP",
            data={
                "request_id": "REQ-001",
                "query": "What integrations between BNP and BNI were approved last month?"
            }
        )
    )

    # Subscribe to response
    async def handle_response(event: Event):
        if event.data.get("request_id") == "REQ-001":
            print(f"Results: {event.data['results']}")

    await event_bus.subscribe("cognee.query.response", handle_response)
```

### Example 2: Analyze Compliance Trends

```python
async def analyze_compliance():
    """Analyze compliance trends using Cognee."""
    cognee_bot = CogneeMemoryBot(event_bus, state_manager)

    # Get compliance trends for AXIS domain
    trends = await cognee_bot.get_compliance_trends(domain="AXIS")

    print(f"Compliance Trends for AXIS:")
    for trend in trends["trends"]:
        print(f"  - {trend}")
```

### Example 3: Find Similar Past Integrations

```python
async def find_similar():
    """Find similar integrations before creating new one."""
    cognee_bot = CogneeMemoryBot(event_bus, state_manager)

    # Before requesting new integration, check for similar ones
    similar = await cognee_bot.find_similar_integrations(
        "Real-time data synchronization between analytics and reporting"
    )

    print("Found similar integrations:")
    for integration in similar:
        print(f"  - {integration}")

    # Use insights to inform new integration design
```

## Advanced Features

### Temporal Analysis

Enable temporal awareness in `config/cognee_config.yaml`:

```yaml
processing:
  temporal_aware: true
```

Then query time-based patterns:

```python
# Query: "Show me integration approval trends over the last 6 months"
results = await cognee.search(
    cognee.SearchType.INSIGHTS,
    "integration approval trends last 6 months"
)
```

### Custom Cognification Rules

Create `src/cognee/custom_rules.py`:

```python
from cognee import DataPoint, Graph

async def custom_governance_cognification(event: Event) -> Graph:
    """Custom cognification for governance events."""
    graph = Graph()

    if event.event_type == "integration.approved":
        # Extract entities
        source_domain = DataPoint(
            type="Domain",
            id=event.data["source_domain"],
            properties={"name": event.data["source_domain"]}
        )

        target_domain = DataPoint(
            type="Domain",
            id=event.data["target_domain"],
            properties={"name": event.data["target_domain"]}
        )

        integration = DataPoint(
            type="Integration",
            id=event.data["integration_id"],
            properties={
                "purpose": event.data["purpose"],
                "approved_at": event.data["approved_at"],
                "approved_by": event.data["approved_by"]
            }
        )

        # Create relationships
        graph.add_relationship(
            source_domain,
            "INTEGRATES_WITH",
            target_domain,
            via=integration
        )

    return graph
```

## Monitoring & Metrics

Track Cognee performance:

```python
# Metrics to monitor
metrics.gauge("cognee.graph.nodes", node_count)
metrics.gauge("cognee.graph.relationships", relationship_count)
metrics.timing("cognee.cognification.duration", duration_ms)
metrics.increment("cognee.queries.total")
metrics.histogram("cognee.query.results", result_count)
```

## Best Practices

### 1. Selective Cognification
Don't cognify everything - focus on high-value events:
```python
COGNIFY_EVENT_TYPES = [
    "integration.approved",
    "integration.rejected",
    "compliance.violation",
    "domain.registered",
    "governance.decision"
]

if event.event_type in COGNIFY_EVENT_TYPES:
    await cognee.add([document])
```

### 2. Batch Processing
Cognify events in batches for efficiency:
```python
batch = []
for event in events:
    batch.append(event_to_document(event))
    if len(batch) >= 10:
        await cognee.add(batch)
        batch = []
```

### 3. Privacy Filtering
Filter sensitive data before cognification:
```python
def sanitize_event(event: Event) -> Event:
    """Remove sensitive data from event."""
    sanitized = event.copy()
    # Remove passwords, tokens, PII
    sanitized.data.pop("password", None)
    sanitized.data.pop("token", None)
    return sanitized
```

## Troubleshooting

### "Connection to Memgraph failed"
```bash
# Check Memgraph is running
docker ps | grep memgraph

# Start Memgraph
docker start memgraph
```

### "Cognification is slow"
```python
# Use faster embedding model
cognee.config.set({
    "embeddings_model": "text-embedding-3-small"  # Faster
})

# Reduce chunk size
cognee.config.set({
    "chunk_size": 256  # Smaller chunks
})
```

### "Out of memory"
```python
# Process in smaller batches
batch_size = 5  # Reduce from 10

# Clear cache periodically
await cognee.prune(keep_last_n=1000)
```

## Next Steps

- [MCP Integration](./MCP_INTEGRATION.md)
- [OpenSpec Integration](./OPENSPEC_INTEGRATION.md)
- [Return to Architecture Overview](./AI_INTEGRATION_ARCHITECTURE.md)

## Resources

- [Cognee GitHub](https://github.com/topoteretes/cognee)
- [Cognee Documentation](https://docs.cognee.ai/)
- [Memgraph Documentation](https://memgraph.com/docs)
- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
