# BSW-Arch Knowledge Graph System

## Overview

This directory contains the OpenCode + Knowledge Graph RAG system for the BSW-Arch bot factory.

## Architecture

```
knowledge-graph/
├── indexer/
│   └── bot_spec_indexer.py      # Indexes bots, docs, templates into Neo4j + ChromaDB
├── mcp-server/
│   └── mcp_server.py             # MCP server with domain-specific tools
├── data/
│   └── chroma_db/                # Vector embeddings (created after indexing)
└── README.md                     # This file
```

## Components

### 1. Bot Specification Indexer

**File**: `indexer/bot_spec_indexer.py`

Indexes the entire BSW-Arch repository into a knowledge graph:

- **Bot specifications** (YAML files) → Neo4j nodes with relationships
- **Documentation** (Markdown files) → Vector embeddings in ChromaDB
- **Templates** → Searchable templates
- **Container specs** → Linked to bots
- **Bot examples** → Code examples for reference

**Usage**:
```bash
python indexer/bot_spec_indexer.py /path/to/bsw-arch
```

### 2. MCP Server

**File**: `mcp-server/mcp_server.py`

Provides tools that OpenCode can use to query the knowledge graph:

#### Available Tools:

1. **`query_bot_knowledge`** - Hybrid search (graph + semantic)
   - Query: Natural language question
   - Domain filter: AXIS/PIPE/ECO/IV/ALL
   - Returns: Relevant bots, docs, and context

2. **`get_bot_dependencies`** - Dependency analysis
   - Bot name: Name of bot to analyze
   - Returns: What it depends on, what depends on it

3. **`analyze_bot_impact`** - Impact analysis
   - Bot name: Bot being changed
   - Returns: All affected bots categorized by risk

4. **`find_similar_bots`** - Similarity search
   - Description: Functionality you're looking for
   - Returns: Bots with similar capabilities

5. **`get_domain_overview`** - Domain statistics
   - Domain: AXIS/PIPE/ECO/IV
   - Returns: Comprehensive domain overview

#### Available Resources:

- **`project://stats`** - Overall bot factory statistics

**Usage**:
```bash
# Start MCP server
python mcp-server/mcp_server.py

# Or run in background
python mcp-server/mcp_server.py &
```

## Integration with OpenCode

### Configuration

OpenCode config is in `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "servers": {
      "bsw-bot-factory": {
        "command": "python3",
        "args": ["/absolute/path/to/mcp_server.py"],
        "env": {
          "NEO4J_URI": "bolt://localhost:7687",
          "NEO4J_USER": "neo4j",
          "NEO4J_PASSWORD": "bsw-secure-password-2024",
          "CHROMA_PATH": "/absolute/path/to/chroma_db"
        }
      }
    }
  }
}
```

### Custom Commands

Custom OpenCode commands are in `.opencode/commands/`:

- **`/bot-explain`** - Explain bot with full context
- **`/bot-impact`** - Analyze impact of bot changes
- **`/bot-find-similar`** - Find similar bots
- **`/domain-overview`** - Get domain statistics

## Data Storage

### Neo4j Graph Database

**Access**: http://localhost:7474
**Credentials**: neo4j / bsw-secure-password-2024

**Node Types**:
- `Bot` - Bot specifications
- `Document` - Documentation files
- `Template` - Bot templates
- `Container` - Container specifications
- `BotExample` - Example code

**Relationships**:
- `DEPENDS_ON` - Bot dependencies
- `RUNS_IN` - Bot-to-container mapping
- `DEFINED_IN` - Code location

### ChromaDB Vector Store

**Location**: `knowledge-graph/data/chroma_db/`

**Collections**:
- `bsw_bot_specs` - All indexed content with semantic embeddings

**Metadata**:
- `type` - bot_spec, documentation, template, bot_example
- `domain` - AXIS, PIPE, ECO, IV, GENERAL
- `file_path` - Source file location

## Workflow

### 1. Initial Setup

```bash
# Run setup script (from bsw-arch root)
./setup-knowledge-graph.sh
```

### 2. Index Repository

```bash
# Full index
python indexer/bot_spec_indexer.py .

# Incremental (future feature)
python indexer/bot_spec_indexer.py . --incremental
```

### 3. Start MCP Server

```bash
python mcp-server/mcp_server.py &
```

### 4. Use OpenCode

```bash
cd /home/user/bsw-arch
opencode

> /bot-explain eco-monitoring-bot
```

## Maintenance

### Re-Index After Changes

After adding/modifying bot specs or documentation:

```bash
python indexer/bot_spec_indexer.py .
```

### Verify Knowledge Graph

```bash
# Connect to Neo4j
docker exec -it neo4j-bsw-arch cypher-shell -u neo4j -p bsw-secure-password-2024

# Query bot count
MATCH (b:Bot) RETURN count(b);

# Query by domain
MATCH (b:Bot {domain: "AXIS"}) RETURN b.name;
```

### Clean and Rebuild

```bash
# Stop and remove Neo4j
docker stop neo4j-bsw-arch
docker rm neo4j-bsw-arch

# Remove ChromaDB
rm -rf knowledge-graph/data/chroma_db

# Re-run setup
./setup-knowledge-graph.sh

# Re-index
python indexer/bot_spec_indexer.py .
```

## Performance

### Expected Indexing Time

For BSW-Arch repository (~185 bots, 17 docs):
- Initial indexing: **3-5 minutes**
- Query response: **100-500ms**
- Impact analysis: **500-2000ms**

### Optimization Tips

1. **Create Neo4j indexes** (automatic, but verify):
   ```cypher
   CREATE INDEX bot_name IF NOT EXISTS FOR (b:Bot) ON (b.name);
   CREATE INDEX bot_domain IF NOT EXISTS FOR (b:Bot) ON (b.domain);
   ```

2. **Limit query depth** - Use `depth=2` instead of `depth=5`

3. **Use domain filters** - Filter by domain to reduce search space

4. **Cache frequently used queries** - MCP server caches common queries

## Development

### Adding Custom MCP Tools

Edit `mcp-server/mcp_server.py`:

```python
@mcp.tool()
async def your_custom_tool(param: str) -> str:
    """Your tool description"""
    # Implementation
    pass
```

### Extending the Indexer

Edit `indexer/bot_spec_indexer.py`:

```python
def index_new_type(self, path: Path):
    """Index a new type of content"""
    # Implementation
    pass
```

## Dependencies

### Python Packages

```
fastmcp
neo4j
chromadb
tree-sitter
tree-sitter-python
sentence-transformers
pyyaml
```

### External Services

- **Neo4j** (Docker container)
- **Ollama** (Local LLM)
- **OpenCode** (npm package)

## Troubleshooting

See [KNOWLEDGE-GRAPH-QUICKSTART.md](../KNOWLEDGE-GRAPH-QUICKSTART.md#-troubleshooting) for detailed troubleshooting guide.

---

**Last Updated**: 2025-11-11
**Version**: 1.0
