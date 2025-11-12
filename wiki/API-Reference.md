# API Reference - Platform Security Bot

Complete API documentation for the **pipe-security-bot** autonomous AI agent.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

All API requests require authentication via Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/v1/status
```

## Core Endpoints

### Health Check

Check bot health and status.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "bot": "pipe-security-bot",
  "mode": "autonomous",
  "uptime": 3600,
  "version": "1.0.0"
}
```

### Bot Status

Get detailed bot status and metrics.

**Endpoint:** `GET /status`

**Response:**

```json
{
  "bot_name": "pipe-security-bot",
  "mode": "autonomous",
  "active_tasks": 5,
  "completed_tasks": 127,
  "failed_tasks": 2,
  "success_rate": 98.4,
  "meta_keragr_connected": true,
  "coordination_api_connected": true,
  "crewai_agents": 3
}
```

### Execute Operation

Execute a bot operation.

**Endpoint:** `POST /execute`

**Request:**

```json
{
  "operation": "operation_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "mode": "autonomous"
}
```

**Response:**

```json
{
  "task_id": "task-123-abc",
  "status": "initiated",
  "operation": "operation_name",
  "estimated_completion": "2025-10-05T14:30:00Z"
}
```

### Get Task Status

Check task execution status.

**Endpoint:** `GET /tasks/{task_id}`

**Response:**

```json
{
  "task_id": "task-123-abc",
  "status": "completed",
  "progress": 100,
  "result": {
    "success": true,
    "data": {}
  },
  "started_at": "2025-10-05T14:25:00Z",
  "completed_at": "2025-10-05T14:28:00Z"
}
```

## META-KERAGR Integration

### Query Knowledge Graph

**Endpoint:** `POST /keragr/query`

**Request:**

```json
{
  "query": "MATCH (n) WHERE n.type = 'pattern' RETURN n",
  "limit": 10
}
```

### Store Knowledge

**Endpoint:** `POST /keragr/store`

**Request:**

```json
{
  "knowledge_type": "pattern",
  "data": {
    "pattern_id": "pat-001",
    "description": "Common failure pattern",
    "frequency": 15
  }
}
```

## CrewAI Coordination

### Get Active Agents

**Endpoint:** `GET /crewai/agents`

**Response:**

```json
{
  "active_agents": 3,
  "agents": [
    {
      "agent_id": "agent-001",
      "role": "coordinator",
      "status": "active"
    }
  ]
}
```

### Coordinate Task

**Endpoint:** `POST /crewai/coordinate`

**Request:**

```json
{
  "task": "complex_operation",
  "agents": ["pipe-docs-bot", "pipe-analytics-bot"],
  "coordination_mode": "collaborative"
}
```

## Metrics & Analytics

### Get Metrics

**Endpoint:** `GET /metrics`

**Response:**

```json
{
  "response_time_ms": 85,
  "availability_percent": 99.9,
  "accuracy_percent": 96.5,
  "collaboration_success_percent": 92.1,
  "knowledge_graph_size": 15420
}
```

## WebSocket API

For real-time updates, connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Bot update:', data);
};
```

## Error Handling

All API errors follow this format:

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Parameter 'param1' is required",
    "details": {}
  }
}
```

### Common Error Codes

- `INVALID_PARAMETER`: Missing or invalid parameter
- `AUTHENTICATION_FAILED`: Invalid or expired token
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Internal server error

## Rate Limiting

- **Standard**: 100 requests/minute
- **Burst**: 200 requests/minute
- **WebSocket**: 1000 messages/minute

## SDKs

Official SDKs are available:

- **Python**: `pip install pipe-bot-sdk`
- **TypeScript**: `npm install @pipe-bots/sdk`
- **Go**: `go get codeberg.org/PIPE-Bots/go-sdk`

---

*Part of the Disconnect Collective - SECURE · RELIABLE · INDEPENDENT*
