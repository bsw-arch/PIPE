# MCP (Model Context Protocol) Integration Guide

Complete guide to integrating MCP servers into the PIPE ecosystem.

## What is MCP?

Model Context Protocol (MCP) is an open standard from Anthropic that enables AI assistants to securely connect to data sources and tools. Think of it as a universal adapter for AI agents to access external systems.

## Architecture

```
┌──────────────────────────────────────────────┐
│         PIPE Domain Bots                     │
│  (BNI, BNP, AXIS, IV, etc.)                  │
└────────────────┬─────────────────────────────┘
                 │ Events
                 ▼
┌──────────────────────────────────────────────┐
│         EventBus (Integration Hub)           │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│         MCPConnectorBot                      │
│  ┌────────────────────────────────────────┐  │
│  │  Server Manager                        │  │
│  │  - Register MCP servers                │  │
│  │  - Manage connections                  │  │
│  │  - Health monitoring                   │  │
│  └────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────┐  │
│  │  Tool Executor                         │  │
│  │  - Execute MCP tool calls              │  │
│  │  - Handle responses                    │  │
│  │  - Error handling                      │  │
│  └────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────┐  │
│  │  Context Manager                       │  │
│  │  - Manage AI context                   │  │
│  │  - Resource access                     │  │
│  │  - Prompt management                   │  │
│  └────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
    ┌────▼─────┐    ┌────▼─────┐
    │  GitHub  │    │  Slack   │
    │MCP Server│    │MCP Server│
    └──────────┘    └──────────┘
```

## Installation

### Step 1: Install MCP Dependencies

```bash
# Install MCP Python SDK
pip install mcp

# Or add to requirements.txt
echo "mcp>=1.0.0" >> requirements.txt
pip install -r requirements.txt
```

### Step 2: Install MCP Servers

MCP servers are typically Node.js applications. Install the ones you need:

```bash
# GitHub MCP Server
npx @modelcontextprotocol/server-github

# Slack MCP Server
npx @modelcontextprotocol/server-slack

# Postgres MCP Server
npx @modelcontextprotocol/server-postgres

# Filesystem MCP Server
npx @modelcontextprotocol/server-filesystem

# Web search MCP Server
npx @modelcontextprotocol/server-brave-search
```

### Step 3: Configure MCP Servers

Create `config/mcp_servers.yaml`:

```yaml
mcp_servers:
  github:
    command: "npx"
    args:
      - "@modelcontextprotocol/server-github"
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
    enabled: true
    description: "GitHub repository access"

  slack:
    command: "npx"
    args:
      - "@modelcontextprotocol/server-slack"
    env:
      SLACK_BOT_TOKEN: "${SLACK_BOT_TOKEN}"
    enabled: true
    description: "Slack workspace integration"

  postgres:
    command: "npx"
    args:
      - "@modelcontextprotocol/server-postgres"
      - "postgresql://user:pass@localhost:5432/dbname"
    enabled: true
    description: "PostgreSQL database access"

  filesystem:
    command: "npx"
    args:
      - "@modelcontextprotocol/server-filesystem"
      - "/path/to/allowed/directory"
    enabled: false  # Disabled for security
    description: "Local filesystem access"
```

## Implementation

### Step 1: Create MCP Connector Bot

Create `src/bots/mcp_connector_bot.py`:

```python
"""MCP Connector Bot - Connects PIPE to MCP servers."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

from src.core.bot_base import BotBase
from src.core.event_bus import Event, EventBus
from src.core.state_manager import StateManager
from src.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class MCPServer:
    """Represents an MCP server instance."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.command = config.get("command")
        self.args = config.get("args", [])
        self.env = config.get("env", {})
        self.enabled = config.get("enabled", True)
        self.description = config.get("description", "")
        self.process: Optional[asyncio.subprocess.Process] = None
        self.tools: List[Dict[str, Any]] = []

    async def start(self) -> bool:
        """Start the MCP server process."""
        if not self.enabled:
            logger.info(f"MCP server {self.name} is disabled")
            return False

        try:
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self.env
            )

            # Wait for server to be ready
            await asyncio.sleep(1)

            # Discover available tools
            await self._discover_tools()

            logger.info(
                f"MCP server {self.name} started with {len(self.tools)} tools"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start MCP server {self.name}: {e}")
            return False

    async def _discover_tools(self):
        """Discover tools available from this MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        response = await self._send_request(request)
        if response and "result" in response:
            self.tools = response["result"].get("tools", [])

    async def _send_request(self, request: Dict[str, Any]) -> Optional[Dict]:
        """Send JSON-RPC request to MCP server."""
        if not self.process or not self.process.stdin:
            return None

        try:
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()

            response_line = await self.process.stdout.readline()
            if response_line:
                return json.loads(response_line.decode())

        except Exception as e:
            logger.error(f"Error sending request to {self.name}: {e}")

        return None

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Optional[Dict]:
        """Call a tool on this MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        response = await self._send_request(request)
        return response.get("result") if response else None

    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None


class MCPConnectorBot(BotBase):
    """Bot that connects PIPE to MCP servers."""

    def __init__(
        self,
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: Optional[MetricsCollector] = None,
        config_file: str = "config/mcp_servers.yaml"
    ):
        super().__init__(
            "MCPConnector",
            event_bus,
            state_manager,
            metrics
        )
        self.config_file = Path(config_file)
        self.servers: Dict[str, MCPServer] = {}

    async def initialize(self) -> None:
        """Initialize MCP connector and start servers."""
        await super().initialize()

        # Load MCP server configurations
        self._load_config()

        # Start configured MCP servers
        await self._start_servers()

        # Subscribe to MCP-related events
        await self.event_bus.subscribe("mcp.tool.call", self._handle_tool_call)
        await self.event_bus.subscribe("mcp.server.list", self._handle_list_servers)
        await self.event_bus.subscribe("mcp.tools.list", self._handle_list_tools)

        self.logger.info(
            f"MCPConnector initialized with {len(self.servers)} servers"
        )

    def _load_config(self):
        """Load MCP server configurations."""
        if not self.config_file.exists():
            self.logger.warning(f"Config file not found: {self.config_file}")
            return

        with open(self.config_file, "r") as f:
            config = yaml.safe_load(f)

        for name, server_config in config.get("mcp_servers", {}).items():
            self.servers[name] = MCPServer(name, server_config)

    async def _start_servers(self):
        """Start all enabled MCP servers."""
        for server in self.servers.values():
            if server.enabled:
                success = await server.start()
                if success:
                    self.metrics.increment(f"mcp.server.{server.name}.started")

    async def _handle_tool_call(self, event: Event) -> None:
        """Handle MCP tool call request."""
        server_name = event.data.get("server")
        tool_name = event.data.get("tool")
        arguments = event.data.get("arguments", {})
        request_id = event.data.get("request_id")

        self.logger.info(
            f"Tool call: {server_name}.{tool_name} (request: {request_id})"
        )

        if server_name not in self.servers:
            await self._publish_error(
                request_id, f"Unknown MCP server: {server_name}"
            )
            return

        server = self.servers[server_name]

        try:
            result = await server.call_tool(tool_name, arguments)

            await self.event_bus.publish(
                Event(
                    event_type="mcp.tool.response",
                    source=self.name,
                    data={
                        "request_id": request_id,
                        "server": server_name,
                        "tool": tool_name,
                        "result": result
                    }
                )
            )

            self.metrics.increment(f"mcp.tool.{server_name}.{tool_name}.success")

        except Exception as e:
            self.logger.error(f"Tool call failed: {e}")
            await self._publish_error(request_id, str(e))
            self.metrics.increment(f"mcp.tool.{server_name}.{tool_name}.error")

    async def _handle_list_servers(self, event: Event) -> None:
        """List available MCP servers."""
        servers = [
            {
                "name": name,
                "description": server.description,
                "enabled": server.enabled,
                "tool_count": len(server.tools)
            }
            for name, server in self.servers.items()
        ]

        await self.event_bus.publish(
            Event(
                event_type="mcp.server.list.response",
                source=self.name,
                data={"servers": servers}
            )
        )

    async def _handle_list_tools(self, event: Event) -> None:
        """List tools available from MCP servers."""
        server_name = event.data.get("server")

        if server_name and server_name in self.servers:
            tools = self.servers[server_name].tools
        else:
            # List all tools from all servers
            tools = []
            for server in self.servers.values():
                for tool in server.tools:
                    tools.append({
                        "server": server.name,
                        **tool
                    })

        await self.event_bus.publish(
            Event(
                event_type="mcp.tools.list.response",
                source=self.name,
                data={"tools": tools}
            )
        )

    async def _publish_error(self, request_id: str, error: str):
        """Publish error event."""
        await self.event_bus.publish(
            Event(
                event_type="mcp.tool.error",
                source=self.name,
                data={
                    "request_id": request_id,
                    "error": error
                }
            )
        )

    async def cleanup(self) -> None:
        """Stop all MCP servers and cleanup."""
        for server in self.servers.values():
            await server.stop()

        await super().cleanup()
```

### Step 2: Register with Governance

Create `examples/mcp_setup.py`:

```python
"""Setup MCP integration with PIPE governance."""

import asyncio
from src.governance.governance_manager import GovernanceManager
from src.core.event_bus import EventBus
from src.core.state_manager import StateManager
from src.bots.mcp_connector_bot import MCPConnectorBot


async def setup_mcp_integration():
    """Setup MCP integration with governance approval."""
    # Initialize components
    event_bus = EventBus()
    state_manager = StateManager()
    governance = GovernanceManager()

    print("=== MCP Integration Setup ===\n")

    # Step 1: Register MCP as a domain
    print("Registering MCP domain...")
    mcp_domain = await governance.register_domain(
        "MCP",
        capabilities=[
            "github_access",
            "slack_integration",
            "postgres_queries",
            "tool_execution"
        ],
        compliance_requirements=["data_access_audit", "rate_limiting"]
    )
    print(f"✓ MCP domain registered: {mcp_domain['domain_id']}\n")

    # Step 2: Request integrations for domains that need MCP
    print("Requesting MCP integrations...")

    # BNP needs database access
    bnp_mcp = await governance.request_integration(
        source_domain="BNP",
        target_domain="MCP",
        integration_type="database_access",
        purpose="Analytics and reporting via PostgreSQL MCP server"
    )
    print(f"✓ BNP → MCP integration requested: {bnp_mcp['integration_id']}")

    # IV needs GitHub access
    iv_mcp = await governance.request_integration(
        source_domain="IV",
        target_domain="MCP",
        integration_type="github_access",
        purpose="Code repository analysis via GitHub MCP server"
    )
    print(f"✓ IV → MCP integration requested: {iv_mcp['integration_id']}")

    # AXIS needs Slack notifications
    axis_mcp = await governance.request_integration(
        source_domain="AXIS",
        target_domain="MCP",
        integration_type="slack_integration",
        purpose="Architecture alerts via Slack MCP server"
    )
    print(f"✓ AXIS → MCP integration requested: {axis_mcp['integration_id']}\n")

    # Step 3: Approve integrations
    print("Approving integrations...")
    for integration in [bnp_mcp, iv_mcp, axis_mcp]:
        # Assign reviewer
        governance.review_pipeline.assign_reviewers(
            integration["review_id"],
            ["mcp-admin@pipe.com"]
        )

        # Approve review
        governance.review_pipeline.approve_review(
            integration["review_id"],
            "mcp-admin@pipe.com"
        )

        # Approve integration
        await governance.approve_integration(
            integration["integration_id"],
            reviewer="admin@pipe.com",
            notes="MCP server integration approved"
        )
        print(f"✓ Approved: {integration['integration_id']}")

    print("\n=== MCP Integration Setup Complete ===\n")

    # Step 4: Start MCP Connector Bot
    print("Starting MCP Connector Bot...")
    mcp_bot = MCPConnectorBot(event_bus, state_manager)
    await mcp_bot.initialize()
    print("✓ MCP Connector Bot running\n")

    # Display available servers and tools
    print("Available MCP Servers:")
    for server_name, server in mcp_bot.servers.items():
        status = "enabled" if server.enabled else "disabled"
        print(f"  • {server_name} ({status}): {server.description}")
        print(f"    Tools: {len(server.tools)}")

    return mcp_bot


if __name__ == "__main__":
    asyncio.run(setup_mcp_integration())
```

## Usage Examples

### Example 1: GitHub Repository Query

```python
import asyncio
from src.core.event_bus import Event, EventBus

async def query_github_repo():
    """Query GitHub repository information via MCP."""
    event_bus = EventBus()

    # Request repository information
    await event_bus.publish(
        Event(
            event_type="mcp.tool.call",
            source="IV",
            data={
                "request_id": "REQ-001",
                "server": "github",
                "tool": "get_repository",
                "arguments": {
                    "owner": "anthropics",
                    "repo": "anthropic-sdk-python"
                }
            }
        )
    )

    # Wait for response
    # (In practice, subscribe to mcp.tool.response event)
    await asyncio.sleep(1)
```

### Example 2: Slack Notification

```python
async def send_slack_alert():
    """Send alert to Slack via MCP."""
    event_bus = EventBus()

    await event_bus.publish(
        Event(
            event_type="mcp.tool.call",
            source="AXIS",
            data={
                "request_id": "REQ-002",
                "server": "slack",
                "tool": "post_message",
                "arguments": {
                    "channel": "#architecture-alerts",
                    "text": "⚠️ Compliance threshold exceeded"
                }
            }
        )
    )
```

### Example 3: PostgreSQL Query

```python
async def query_analytics():
    """Query analytics data from PostgreSQL via MCP."""
    event_bus = EventBus()

    await event_bus.publish(
        Event(
            event_type="mcp.tool.call",
            source="BNP",
            data={
                "request_id": "REQ-003",
                "server": "postgres",
                "tool": "execute_query",
                "arguments": {
                    "query": "SELECT COUNT(*) FROM transactions WHERE date > NOW() - INTERVAL '30 days'"
                }
            }
        )
    )
```

## Security Considerations

1. **API Keys**: Store in environment variables, never commit to git
2. **Rate Limiting**: Implement rate limits on MCP tool calls
3. **Access Control**: Only approved integrations can call MCP tools
4. **Audit Logging**: Log all MCP tool calls for compliance
5. **Error Handling**: Graceful degradation if MCP server unavailable

## Testing

```bash
# Run MCP integration tests
python -m pytest tests/integration/test_mcp_integration.py -v

# Test specific MCP server
python examples/mcp_setup.py
```

## Troubleshooting

### MCP Server Won't Start
- Check Node.js version ≥ 18
- Verify environment variables are set
- Check server logs in stderr

### Tool Calls Timeout
- Increase timeout in configuration
- Check network connectivity
- Verify MCP server is responsive

### No Tools Discovered
- Wait for server to fully start
- Check MCP server supports tools/list method
- Verify JSON-RPC communication

## Next Steps

- [OpenSpec Integration](./OPENSPEC_INTEGRATION.md)
- [Cognee Integration](./COGNEE_INTEGRATION.md)
- [Return to Architecture Overview](./AI_INTEGRATION_ARCHITECTURE.md)
