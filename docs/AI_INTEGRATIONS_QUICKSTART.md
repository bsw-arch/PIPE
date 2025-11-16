# AI Integrations Quick Start Guide

Get started with MCP, OpenSpec, and Cognee integrations in under 30 minutes.

## Prerequisites

- Python 3.11+
- Node.js ≥ 20.19.0
- Git repository initialized
- PIPE repository cloned and set up

## Installation (5 minutes)

### 1. Install Python Dependencies

```bash
# Add to requirements.txt
cat >> requirements.txt << 'EOF'
# AI Integrations
mcp>=1.0.0
cognee>=0.2.0
lancedb>=0.5.0
EOF

# Install
pip install -r requirements.txt
```

### 2. Install OpenSpec

```bash
# Install globally
npm install -g @fission-ai/openspec@latest

# Initialize in PIPE repository
cd /path/to/PIPE
openspec init
```

### 3. Install MCP Servers

```bash
# Install commonly used MCP servers
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-slack
npm install -g @modelcontextprotocol/server-postgres
```

## Configuration (10 minutes)

### 1. Set Environment Variables

Create `.env` file:

```bash
# MCP GitHub Server
GITHUB_TOKEN=your_github_token_here

# MCP Slack Server
SLACK_BOT_TOKEN=your_slack_bot_token_here

# Cognee LLM
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 2. Create MCP Configuration

Copy the sample config:

```bash
cp config/mcp_servers.yaml.example config/mcp_servers.yaml
```

Edit `config/mcp_servers.yaml` with your settings.

### 3. Create Cognee Configuration

Copy the sample config:

```bash
cp config/cognee_config.yaml.example config/cognee_config.yaml
```

Defaults are fine for getting started.

## Quick Test (5 minutes)

### Test 1: MCP Integration

```bash
# Run MCP setup
python examples/mcp_setup.py
```

Expected output:
```
=== MCP Integration Setup ===
✓ MCP domain registered: domain_MCP_...
✓ BNP → MCP integration requested
✓ MCP Connector Bot running

Available MCP Servers:
  • github (enabled): GitHub repository access
  • slack (enabled): Slack workspace integration
  • postgres (enabled): PostgreSQL database access
```

### Test 2: OpenSpec Integration

```bash
# Create a sample spec change proposal
/openspec:proposal "Add health check endpoint"

# Check it was created
ls openspec/changes/
```

Expected: New folder with proposal files.

### Test 3: Cognee Integration

```bash
# Run Cognee setup
python examples/cognee_setup.py
```

Expected output:
```
=== Cognee Knowledge Graph Setup ===
✓ Cognee domain registered
✓ Cognee Memory Bot running
✓ Cognified 3 sample events

Knowledge Graph Stats:
  Total events cognified: 3
  Backend: lancedb + networkx
```

### Test 4: Complete Integration

```bash
# Run the full demo
python examples/ai_integrations_demo.py
```

Expected: Complete workflow demonstrating all three integrations.

## First Real Use Cases (10 minutes)

### Use Case 1: Query GitHub via MCP

```python
# examples/query_github.py
import asyncio
from src.core.event_bus import Event, EventBus

async def query_github():
    event_bus = EventBus()

    await event_bus.publish(
        Event(
            event_type="mcp.tool.call",
            source="DEMO",
            data={
                "request_id": "REQ-001",
                "server": "github",
                "tool": "get_repository",
                "arguments": {
                    "owner": "your-org",
                    "repo": "your-repo"
                }
            }
        )
    )

asyncio.run(query_github())
```

### Use Case 2: Document Your First API with OpenSpec

```bash
# Create specs directory
mkdir -p openspec/specs/apis

# Create your first API spec
cat > openspec/specs/apis/my-first-api.yaml << 'EOF'
openapi: 3.0.0
info:
  title: My First API
  version: 1.0.0

paths:
  /health:
    get:
      summary: Health check
      responses:
        '200':
          description: Service is healthy
EOF

# Validate
openspec validate
```

### Use Case 3: Ask Cognee About Your System

```python
# examples/query_cognee.py
import asyncio
from src.core.event_bus import Event, EventBus

async def ask_cognee():
    event_bus = EventBus()

    await event_bus.publish(
        Event(
            event_type="cognee.query",
            source="DEMO",
            data={
                "request_id": "REQ-002",
                "query": "What are the most common integration patterns?"
            }
        )
    )

asyncio.run(ask_cognee())
```

## Common Commands

### MCP Commands

```bash
# List available MCP servers
python -c "from examples.mcp_setup import *; asyncio.run(list_mcp_servers())"

# Call MCP tool
# (Use Python API shown above)
```

### OpenSpec Commands

```bash
# Create proposal
/openspec:proposal "description"

# Validate proposal
openspec validate proposal-name

# Apply changes
/openspec:apply proposal-name

# Archive completed
/openspec:archive proposal-name
```

### Cognee Commands

```python
# In Python
import cognee

# Add documents
await cognee.add(["document text"])

# Search
results = await cognee.search(
    cognee.SearchType.INSIGHTS,
    "your query"
)

# Get stats
await cognee.status()
```

## Troubleshooting

### MCP server won't start

```bash
# Check Node.js version
node --version  # Should be ≥ 20.19.0

# Check environment variables
env | grep -E "(GITHUB|SLACK)_"

# Check server manually
npx @modelcontextprotocol/server-github
```

### OpenSpec not found

```bash
# Check installation
which openspec

# Reinstall if needed
npm install -g @fission-ai/openspec@latest
```

### Cognee errors

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall
pip install --upgrade cognee

# Check data directory permissions
ls -la ./data/cognee/
```

## Next Steps

Now that you have the basics working:

1. **Read the Integration Architecture**: [AI_INTEGRATION_ARCHITECTURE.md](./AI_INTEGRATION_ARCHITECTURE.md)

2. **Dive Deep into Each Integration**:
   - [MCP Integration Guide](./MCP_INTEGRATION.md)
   - [OpenSpec Integration Guide](./OPENSPEC_INTEGRATION.md)
   - [Cognee Integration Guide](./COGNEE_INTEGRATION.md)

3. **Explore Examples**:
   - `examples/mcp_setup.py` - MCP configuration and usage
   - `examples/cognee_setup.py` - Cognee knowledge graph setup
   - `examples/ai_integrations_demo.py` - Complete workflow

4. **Configure for Production**:
   - Set up proper authentication
   - Configure monitoring and alerts
   - Implement rate limiting
   - Add error handling

5. **Integrate with Your Domains**:
   - Connect your domains to MCP tools
   - Document your APIs in OpenSpec
   - Start cognifying domain events

## Getting Help

- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Issues**: File issues in the PIPE repository

## Quick Reference

| Integration | Purpose | Key Command | Documentation |
|------------|---------|-------------|---------------|
| MCP | External tools | `await mcp_call(...)` | [MCP_INTEGRATION.md](./MCP_INTEGRATION.md) |
| OpenSpec | API specs | `/openspec:proposal` | [OPENSPEC_INTEGRATION.md](./OPENSPEC_INTEGRATION.md) |
| Cognee | Knowledge graph | `await cognee.search(...)` | [COGNEE_INTEGRATION.md](./COGNEE_INTEGRATION.md) |

Happy integrating! 🚀
