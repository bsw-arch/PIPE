# Knowledge Base Quick Start Guide
## Get Your Bot Connected in 15 Minutes

**For**: Bot Developers
**Version**: 1.0
**Date**: 2025-11-10

---

## Overview

This guide gets your bot connected to the BSW Knowledge Base in **15 minutes or less**.

**What You'll Get**:
- ✅ Access to all BSW documentation (governance, architecture, wikis)
- ✅ Intelligent semantic search across all domains
- ✅ Knowledge graph queries (find related bots, patterns, ADRs)
- ✅ Real-time updates when documentation changes
- ✅ Multi-domain knowledge discovery

---

## Prerequisites

```bash
# Check you have:
python3 --version  # 3.11+
pip3 --version
```

---

## Step 1: Install SDK (2 minutes)

```bash
# Install the knowledge SDK
pip3 install bsw-knowledge-sdk

# Or for development
git clone https://codeberg.org/BSW-Docs/bsw-knowledge-sdk.git
cd bsw-knowledge-sdk
pip3 install -e .
```

---

## Step 2: Get Your API Token (1 minute)

```bash
# Request token from BSW admin, or generate locally:
export KNOWLEDGE_API_TOKEN="your_token_here"

# Add to your bot's .env file
echo "KNOWLEDGE_API_TOKEN=$KNOWLEDGE_API_TOKEN" >> .env
```

---

## Step 3: Basic Integration (5 minutes)

### Simple Search Example

```python
# Add to your bot's main file
from bsw_knowledge_sdk import KnowledgeClient
import os
import asyncio

# Initialize knowledge client
knowledge = KnowledgeClient(
    api_url=os.getenv('KNOWLEDGE_API_URL', 'http://localhost:3108'),
    bot_id='your-bot-name',  # e.g., 'axis-framework-bot'
    domain='YOUR_DOMAIN',     # e.g., 'AXIS', 'PIPE', 'IV', 'ECO'
    auth_token=os.getenv('KNOWLEDGE_API_TOKEN')
)

# Search for documentation
async def search_docs(question: str):
    results = await knowledge.search(question)

    for result in results['results']:
        print(f"📄 {result['title']}")
        print(f"   Relevance: {result['relevance_score']:.2f}")
        print(f"   {result['excerpt']}")
        print()

# Example usage
asyncio.run(search_docs("How to deploy with apko?"))
```

---

## Step 4: Advanced Features (7 minutes)

### Knowledge Graph Queries

```python
# Find related bots
async def find_related_bots(bot_name: str):
    query = f"""
    MATCH (me:Bot {{name: '{bot_name}'}})-[r]-(related:Bot)
    RETURN related.name, related.domain, type(r) as relationship
    LIMIT 10
    """
    results = await knowledge.graph_query(query)
    return results['results']

# Find all bots integrating with ARTEMIS
async def find_artemis_bots():
    query = """
    MATCH (bot:Bot)-[:INTEGRATES_WITH]->(platform:Platform {name: 'ARTEMIS'})
    RETURN bot.name, bot.domain, bot.api_endpoint
    ORDER BY bot.domain
    """
    return await knowledge.graph_query(query)
```

### Real-Time Updates

```python
# Subscribe to documentation updates
async def on_knowledge_update(update):
    print(f"📢 Knowledge updated: {update['type']}")
    print(f"   Affected domains: {update['domains']}")
    # Refresh your local cache here

# Start subscription
await knowledge.subscribe_to_updates(
    domains=['AXIS', 'PIPE'],  # Your relevant domains
    on_update=on_knowledge_update
)
```

### Complete Bot Integration

```python
from bsw_knowledge_sdk import KnowledgeClient
import asyncio
import os

class MyBot:
    def __init__(self):
        # Initialize knowledge client
        self.knowledge = KnowledgeClient(
            api_url=os.getenv('KNOWLEDGE_API_URL', 'http://localhost:3108'),
            bot_id='my-bot',
            domain='AXIS',
            auth_token=os.getenv('KNOWLEDGE_API_TOKEN')
        )

        # Start background tasks
        asyncio.create_task(self.subscribe_to_updates())

    async def subscribe_to_updates(self):
        """Subscribe to real-time knowledge updates"""
        await self.knowledge.subscribe_to_updates(
            domains=['AXIS'],
            on_update=self.on_knowledge_updated
        )

    async def on_knowledge_updated(self, update):
        """Handle knowledge update notification"""
        print(f"Knowledge updated: {update['doc_id']}")
        # Invalidate cache, refresh, etc.

    async def ask_knowledge(self, question: str):
        """Query the knowledge base"""
        # Simple search
        results = await self.knowledge.search(question)

        if results['results']:
            top_result = results['results'][0]
            return {
                'answer': top_result['excerpt'],
                'source': top_result['source']['file'],
                'confidence': top_result['relevance_score']
            }
        else:
            return {'answer': 'No documentation found', 'confidence': 0}

    async def find_integration_patterns(self, pattern_type: str):
        """Find architecture patterns from knowledge graph"""
        results = await self.knowledge.search(
            f"architecture pattern {pattern_type}",
            filters={'domain': 'AXIS', 'type': 'pattern'}
        )
        return results['results']

# Usage
async def main():
    bot = MyBot()

    # Ask questions
    answer = await bot.ask_knowledge("How to integrate with ARTEMIS?")
    print(f"Answer: {answer['answer']}")
    print(f"Source: {answer['source']}")
    print(f"Confidence: {answer['confidence']:.2f}")

    # Find patterns
    patterns = await bot.find_integration_patterns("bot-orchestration")
    for pattern in patterns:
        print(f"📋 {pattern['title']}: {pattern['excerpt']}")

if __name__ == '__main__':
    asyncio.run(main())
```

---

## Common Queries

### 1. Find Bot Documentation

```python
results = await knowledge.search(
    f"documentation for {bot_name}",
    filters={'type': 'bot_doc'}
)
```

### 2. Get Domain Overview

```python
results = await knowledge.search(
    f"{domain} domain architecture overview",
    filters={'domain': domain, 'type': 'architecture'}
)
```

### 3. Find Integration Examples

```python
results = await knowledge.search(
    f"{service_name} integration example code",
    filters={'type': 'example'}
)
```

### 4. Check Technology Compatibility

```python
results = await knowledge.search(
    f"{technology} {version} compatibility issues",
    filters={'type': 'issue'}
)
```

### 5. Discover Related Services

```python
query = f"""
MATCH (service:Service {{name: '{service_name}'}})-[r]-(related)
RETURN related, type(r) as relationship_type
"""
results = await knowledge.graph_query(query)
```

---

## Environment Variables

Add to your bot's `.env` file:

```bash
# Required
KNOWLEDGE_API_URL=http://localhost:3108
KNOWLEDGE_API_TOKEN=your_token_here

# Optional
KNOWLEDGE_CACHE_TTL=3600              # Cache TTL in seconds (default: 1 hour)
KNOWLEDGE_RETRY_ATTEMPTS=3            # Number of retries on failure
KNOWLEDGE_TIMEOUT=30                  # Request timeout in seconds
```

---

## Testing Your Integration

```python
# Test script
import asyncio
from bsw_knowledge_sdk import KnowledgeClient
import os

async def test_connection():
    client = KnowledgeClient(
        api_url=os.getenv('KNOWLEDGE_API_URL'),
        bot_id='test-bot',
        domain='AXIS',
        auth_token=os.getenv('KNOWLEDGE_API_TOKEN')
    )

    # Test 1: Simple search
    print("Test 1: Simple search")
    results = await client.search("ARTEMIS")
    print(f"✓ Found {len(results['results'])} results")

    # Test 2: Graph query
    print("\nTest 2: Graph query")
    bots = await client.graph_query("""
        MATCH (b:Bot) RETURN b.name LIMIT 5
    """)
    print(f"✓ Found {len(bots['results'])} bots")

    # Test 3: WebSocket (disconnect after 5 seconds)
    print("\nTest 3: WebSocket updates")
    async def on_update(update):
        print(f"✓ Received update: {update['type']}")

    task = asyncio.create_task(
        client.subscribe_to_updates(['AXIS'], on_update)
    )
    await asyncio.sleep(5)
    task.cancel()

    print("\n✅ All tests passed!")

if __name__ == '__main__':
    asyncio.run(test_connection())
```

Run the test:

```bash
python3 test_knowledge.py
```

Expected output:

```
Test 1: Simple search
✓ Found 12 results

Test 2: Graph query
✓ Found 5 bots

Test 3: WebSocket updates
✓ Received update: knowledge_update

✅ All tests passed!
```

---

## Troubleshooting

### Issue: Connection refused

**Solution**:
```bash
# Check if META-KERAGR API is running
curl http://localhost:3108/health

# If not, start it
cd ~/services/meta-keragr
podman-compose up -d
```

### Issue: Authentication failed

**Solution**:
```bash
# Check your token is set
echo $KNOWLEDGE_API_TOKEN

# Request new token from admin
```

### Issue: No results found

**Solution**:
```python
# Check if knowledge base is populated
results = await knowledge.graph_query("MATCH (n) RETURN count(n)")
# Should return > 0

# If empty, run sync
/home/user/scripts/sync-knowledge-base.sh
```

### Issue: Slow queries

**Solution**:
```python
# Enable caching in your bot
from bsw_knowledge_sdk import KnowledgeCache

cache = KnowledgeCache(ttl=3600)  # 1 hour cache

async def search_with_cache(query):
    cached = await cache.get(query)
    if cached:
        return cached

    results = await knowledge.search(query)
    await cache.set(query, results)
    return results
```

---

## Next Steps

1. **Read Full Architecture**: See `BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md`
2. **Explore Knowledge Graph**: Open Neo4j browser at http://localhost:7474
3. **Browse Documentation**: See Git repo at `codeberg.org/BSW-Docs/bsw-documentation`
4. **Join Bot Network**: Connect to ARTEMIS platform for bot coordination

---

## Support

- **Documentation**: `/home/user/QubesIncoming/bsw-gov/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md`
- **Issues**: Create issue on Codeberg with label `knowledge-base`
- **SDK Issues**: `codeberg.org/BSW-Docs/bsw-knowledge-sdk/issues`

---

**You're now connected to the BSW Knowledge Base!** 🎉

Your bot can now:
- ✅ Search all documentation intelligently
- ✅ Query the knowledge graph
- ✅ Receive real-time updates
- ✅ Discover cross-domain knowledge

Happy coding! 🤖
