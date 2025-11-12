# axis-task-bot API Reference

Complete API documentation for the axis-task-bot.

## Core Methods

### execute_autonomous()

Execute an autonomous architecture operation.

```python
result = bot.execute_autonomous({
    "task": "architecture_operation",
    "domain": "AXIS",
    "context": {"priority": "high"},
    "options": {"validate": True}
})
```

**Parameters:**
- `task` (str): Operation to perform
- `domain` (str): Architecture domain (AXIS, PIPE, IV, ECO)
- `context` (dict): Operation context and metadata
- `options` (dict): Optional configuration parameters

**Returns:**
- `OperationResult`: Result object with status, data, and metadata

---

### query_keragr()

Query META-KERAGR knowledge graph for context.

```python
context = bot.query_keragr({
    "query": "What are the TOGAF compliance requirements?",
    "domain": "AXIS",
    "limit": 10
})
```

**Parameters:**
- `query` (str): Natural language query
- `domain` (str): Knowledge domain
- `limit` (int): Maximum results to return

**Returns:**
- `list[KnowledgeResult]`: Relevant knowledge entries

---

### collaborate()

Initiate multi-bot collaboration.

```python
result = bot.collaborate({
    "collaborators": ["axis-docs-bot", "axis-compliance-bot"],
    "task": "generate_architecture_documentation",
    "coordination": "sequential"
})
```

**Parameters:**
- `collaborators` (list): Bot names to collaborate with
- `task` (str): Collaborative task description
- `coordination` (str): Coordination mode (sequential, parallel, hierarchical)

**Returns:**
- `CollaborationResult`: Aggregated results from all bots

---

### store_knowledge()

Store operation outcome in META-KERAGR.

```python
bot.store_knowledge({
    "task": "architecture_validation",
    "outcome": "success",
    "patterns": ["microservices", "event-driven"],
    "metadata": {"domain": "AXIS"}
})
```

**Parameters:**
- `task` (str): Task identifier
- `outcome` (str): Operation outcome
- `patterns` (list): Identified patterns
- `metadata` (dict): Additional metadata

**Returns:**
- `bool`: Success status

---

## Configuration Methods

### load_config()

Load configuration from YAML file.

```python
bot.load_config("config/axis-task-bot.yml")
```

### get_status()

Get current bot status.

```python
status = bot.get_status()
print(f"Health: {status.health}")
print(f"Uptime: {status.uptime}")
```

## Data Models

### OperationResult

```python
class OperationResult:
    status: str  # "success" | "failure" | "pending"
    data: dict
    metadata: dict
    timestamp: datetime
    execution_time: float
```

### KnowledgeResult

```python
class KnowledgeResult:
    id: str
    content: str
    relevance_score: float
    source: str
    metadata: dict
```

## Error Handling

```python
from axis_bots.exceptions import (
    BotException,
    ConfigurationError,
    CollaborationError,
    KnowledgeGraphError
)

try:
    result = bot.execute_autonomous(task_params)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except CollaborationError as e:
    print(f"Collaboration failed: {e}")
except BotException as e:
    print(f"Bot error: {e}")
```

## Rate Limiting

API calls are rate-limited to protect system resources:

- **Autonomous Operations**: 100 requests/minute
- **Knowledge Queries**: 500 requests/minute
- **Collaboration Requests**: 50 requests/minute

## Authentication

All API calls require valid authentication:

```python
bot = BotClass(
    keragr_url="http://localhost:3108",
    coordination_url="http://localhost:3111",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

## Webhooks

Configure webhooks for event notifications:

```python
bot.register_webhook({
    "url": "https://your-service.com/webhook",
    "events": ["operation_complete", "error_occurred"],
    "authentication": {"type": "bearer", "token": "..."}
})
```

---

*For more examples, see [Examples](Examples.md)*
