# BSW-Arch Knowledge Graph Quick Start Guide

## 🎯 Overview

This guide will help you set up and use the OpenCode + Knowledge Graph system for the BSW-Arch bot factory. You'll be able to:

- ✅ Query bot specifications using natural language
- ✅ Analyze bot dependencies and impact
- ✅ Find similar bots and reusable patterns
- ✅ Get domain overviews and statistics
- ✅ Use spec-driven development with OpenSpec
- ✅ Keep everything running **100% locally** (no FAGAM)

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Docker** (for Neo4j database)
- **Python 3.10+** (for indexer and MCP server)
- **Node.js 18+** (for OpenCode and OpenSpec)
- **8GB+ RAM** (16GB recommended)
- **~10GB disk space** (for models and databases)

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Run Setup Script

```bash
cd /home/user/bsw-arch
chmod +x setup-knowledge-graph.sh
./setup-knowledge-graph.sh
```

This will:
- Start Neo4j database container
- Install Python dependencies
- Install and configure Ollama
- Install OpenCode and OpenSpec
- Create project structure

**Time:** ~10 minutes (depending on download speeds)

---

### Step 2: Index Your Repository

```bash
# Activate virtual environment
source venv/bin/activate

# Index all documentation and bot specs
python knowledge-graph/indexer/bot_spec_indexer.py .
```

**Expected output:**
```
📂 Indexing repository: /home/user/bsw-arch

1. Indexing bot specifications...
   ✓ Indexed: eco-base.yaml (ECO)
   ✓ Indexed: eco-infra-bot.yaml (ECO)
   ...

2. Indexing container specifications...
   ✓ Indexed: eco-base.yaml (ECO)
   ...

3. Indexing documentation...
   ✓ Indexed: architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md (42 chunks)
   ...

4. Indexing templates...
   ✓ Indexed: deployment/eco/eco-namespace-setup.yaml (deployment)
   ...

5. Indexing bot examples...
   ✓ Indexed: eco_monitoring_bot.py (ECO)
   ...

6. Creating database indexes...
   ✓ Created index
   ...

✓ Indexing complete!

📊 Knowledge Graph Statistics
==================================================

Bots by Domain:
  AXIS: 45 bots
  ECO: 48 bots
  IV: 44 bots
  PIPE: 48 bots

Documents: 17
Templates: 12
Containers: 8
BotExamples: 4

Relationships: 256
Vector embeddings: 892
```

**Time:** ~3-5 minutes

---

### Step 3: Start MCP Server

In a separate terminal:

```bash
cd /home/user/bsw-arch
source venv/bin/activate

# Start MCP server in background
python knowledge-graph/mcp-server/mcp_server.py &

# Or run in foreground to see logs
python knowledge-graph/mcp-server/mcp_server.py
```

**Verify it's running:**
```bash
ps aux | grep mcp_server
```

---

### Step 4: Configure OpenCode

```bash
# Copy configuration to OpenCode config directory
mkdir -p ~/.config/opencode
cp opencode-config.json ~/.config/opencode/opencode.json

# Verify configuration
cat ~/.config/opencode/opencode.json
```

**Important:** The config file uses **absolute paths**. If you installed bsw-arch in a different location, update the paths in `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "servers": {
      "bsw-bot-factory": {
        "args": ["/YOUR/ACTUAL/PATH/bsw-arch/knowledge-graph/mcp-server/mcp_server.py"],
        "env": {
          "CHROMA_PATH": "/YOUR/ACTUAL/PATH/bsw-arch/knowledge-graph/data/chroma_db"
        }
      }
    }
  }
}
```

---

### Step 5: Initialize OpenSpec (Optional but Recommended)

```bash
cd /home/user/bsw-arch

# Initialize OpenSpec
openspec init

# When prompted, select: OpenCode
```

This creates:
- `openspec/AGENTS.md` - Workflow instructions
- `openspec/project.md` - Project context
- `openspec/specs/` - Specifications directory
- `openspec/changes/` - Proposals and changes directory

---

## 🎓 Usage Examples

### Example 1: Understanding a Bot

```bash
cd /home/user/bsw-arch
opencode
```

In OpenCode:
```
> /bot-explain eco-monitoring-bot

# OpenCode will:
# 1. Query the knowledge graph
# 2. Show bot purpose, dependencies, and related bots
# 3. Provide usage examples
```

**Expected Response:**
```markdown
# ECO Monitoring Bot

## Purpose
The eco-monitoring-bot monitors resource usage, sustainability metrics,
and system health across the bot factory infrastructure.

## Domain
ECO (Ecological)

## Capabilities
- Resource monitoring (CPU, memory, disk)
- Carbon footprint tracking
- Alert generation for anomalies
- Metrics aggregation and reporting

## Dependencies
This bot depends on:
- eco-base (base container)
- eco-metrics-bot (metrics collection)

## Dependents
Bots that depend on eco-monitoring-bot:
- eco-report-bot (uses monitoring data for reports)
- eco-optimization-bot (uses metrics for optimization)

## Container
Runs in: eco-monitoring-container (apko + Wolfi, 45MB)

## Related Bots
- eco-metrics-bot: Collects raw metrics
- eco-optimization-bot: Acts on monitoring data
- pipe-monitoring-bot: Similar monitoring for PIPE domain

## Example Usage
Deploy as a Kubernetes DaemonSet to monitor all nodes...
```

---

### Example 2: Analyzing Bot Impact

```
> /bot-impact pipe-build-bot

# What would break if we modified pipe-build-bot?
```

**Expected Response:**
```markdown
# Impact Analysis: pipe-build-bot

**Change Type:** modification
**Domain:** PIPE

**Total Affected Bots:** 12

## 🔴 HIGH RISK (distance ≤ 1) - 5 bots
Direct dependents that will be immediately affected:

- **pipe-test-bot** (PIPE) - Depends on build artifacts
- **pipe-release-bot** (PIPE) - Requires build completion
- **pipe-deployment-bot** (PIPE) - Deploys built containers
- **axis-validation-bot** (AXIS) - Validates build outputs
- **eco-optimization-bot** (ECO) - Analyzes build metrics

## 🟡 MEDIUM RISK (distance 2-3) - 4 bots
- **pipe-monitoring-bot** (PIPE)
- **iv-analysis-bot** (IV)
...

## Recommendations
1. ⚠️ Update pipe-test-bot integration tests first
2. ⚠️ Ensure backward compatibility for build artifact format
3. ⚠️ Coordinate with AXIS and ECO domain teams
4. ✅ Deploy to staging environment before production
```

---

### Example 3: Finding Similar Bots

```
> /bot-find-similar I need a bot that handles documentation generation and keeps it up to date
```

**Expected Response:**
```markdown
# Similar Bots: documentation generation

Found 5 similar bots

## 1. axis-docs-bot (AXIS)
**Similarity:** 94%
**Approach:** Generates architecture documentation from templates and metadata
**Pros:** Well-tested, integrates with TOGAF/ArchiMate
**Cons:** AXIS-specific, may need adaptation

## 2. pipe-docs-bot (PIPE)
**Similarity:** 87%
**Approach:** Auto-generates pipeline documentation from YAML configs
**Pros:** Real-time updates, CI/CD integrated
**Cons:** Limited to pipeline documentation

## 3. eco-report-bot (ECO)
**Similarity:** 76%
**Approach:** Generates sustainability reports
**Pros:** Excellent formatting, multi-format output
**Cons:** Different focus (metrics vs docs)

## Recommendation
Use **axis-docs-bot** as your starting point because:
1. Most similar functionality (94% match)
2. Mature codebase with extensive tests
3. Template system is reusable
4. Can be extended to other domains

Reusable patterns:
- Template rendering engine
- Markdown generation utilities
- Automated update scheduling
```

---

### Example 4: Domain Overview

```
> /domain-overview AXIS
```

**Expected Response:**
```markdown
# AXIS Domain Overview

**Total Bots:** 45

## Domain Purpose
Enterprise architecture, design patterns, compliance, and blueprint generation.

## Most Complex Bots (by dependencies)
- **axis-coordination-bot**: 12 dependencies
- **axis-validation-bot**: 8 dependencies
- **axis-integration-bot**: 7 dependencies

## Most Critical Bots (by dependents)
- **axis-docs-bot**: 15 dependents
- **axis-blueprint-bot**: 11 dependents
- **axis-base**: 45 dependents (base container)

## Key Architecture Patterns
- Template-based generation
- TOGAF/Zachman framework compliance
- Multi-layer validation (syntax, semantics, architecture)

## Inter-Domain Dependencies
- Works closely with IV domain for validation
- Provides blueprints to PIPE domain for deployment
- Receives metrics from ECO domain for analysis

## Development Guidelines
1. Follow UK English for all documentation
2. Use TOGAF 9.2 terminology
3. All bots must extend axis-base container
4. Include ArchiMate diagrams in specifications

## Related Documentation
- docs/architecture/domains/AXIS-DOMAIN-ANALYSIS.md
- docs/guides/development/AXIS-BOT-DEVELOPMENT.md
```

---

### Example 5: Spec-Driven Bot Development with OpenSpec

#### Create a Proposal
```
> /openspec-proposal Add rate limiting to ECO monitoring API
```

OpenCode will:
1. Query knowledge graph for existing ECO bots
2. Analyze eco-monitoring-bot dependencies
3. Find similar implementations
4. Create proposal in `openspec/changes/add-rate-limiting/`

#### Validate the Proposal
```bash
$ openspec validate add-rate-limiting --strict
✓ All requirements have scenarios
✓ Spec format correct
✓ Tasks are actionable
```

#### Implement the Change
```
> /openspec-apply add-rate-limiting
```

OpenCode will:
1. Read proposal and tasks
2. Query graph for dependencies
3. Implement with full context
4. Mark tasks as complete

#### Archive When Done
```
> /openspec-archive add-rate-limiting
```

Then re-index:
```bash
python knowledge-graph/indexer/bot_spec_indexer.py . --incremental
```

---

## 🔧 Advanced Usage

### Custom MCP Tools

You can add domain-specific tools to `knowledge-graph/mcp-server/mcp_server.py`:

```python
@mcp.tool()
async def analyze_bot_security(bot_name: str) -> str:
    """Custom security analysis for bots"""
    # Your implementation
    pass
```

### Query Neo4j Directly

```bash
docker exec -it neo4j-bsw-arch cypher-shell -u neo4j -p bsw-secure-password-2024
```

Example queries:
```cypher
// Find all AXIS bots
MATCH (b:Bot {domain: "AXIS"})
RETURN b.name, b.description
ORDER BY b.name;

// Find circular dependencies
MATCH (b:Bot)-[:DEPENDS_ON*]->(b)
RETURN b.name;

// Find orphaned bots (no dependents)
MATCH (b:Bot)
WHERE NOT (b)<-[:DEPENDS_ON]-()
RETURN b.name, b.domain;
```

### View Knowledge Graph

Open Neo4j Browser: http://localhost:7474

Visualize bot dependencies:
```cypher
MATCH (b:Bot {domain: "ECO"})-[r:DEPENDS_ON]->(dep)
RETURN b, r, dep
```

---

## 📊 Monitoring and Maintenance

### Check System Status

```bash
# Neo4j
docker ps | grep neo4j-bsw-arch

# MCP Server
ps aux | grep mcp_server

# Ollama
curl http://localhost:11434/api/tags
```

### Re-Index After Changes

```bash
# Full re-index
python knowledge-graph/indexer/bot_spec_indexer.py .

# Incremental (only changed files)
python knowledge-graph/indexer/bot_spec_indexer.py . --incremental
```

### View Statistics

In OpenCode:
```
> Use the get_project_stats resource to show me current statistics
```

---

## 🐛 Troubleshooting

### Issue: Neo4j won't start

```bash
# Check logs
docker logs neo4j-bsw-arch

# Restart
docker restart neo4j-bsw-arch

# If corrupted, remove and recreate
docker rm -f neo4j-bsw-arch
./setup-knowledge-graph.sh
```

### Issue: MCP tools not available in OpenCode

```bash
# Verify absolute paths in config
cat ~/.config/opencode/opencode.json

# Test MCP server directly
cd /home/user/bsw-arch
source venv/bin/activate
python knowledge-graph/mcp-server/mcp_server.py

# Check OpenCode can see the server
opencode auth status
```

### Issue: Ollama model not found

```bash
# Pull the model
ollama pull deepseek-coder:6.7b

# List available models
ollama list

# Test model
ollama run deepseek-coder:6.7b "print hello world in python"
```

### Issue: Slow queries

```bash
# Create Neo4j indexes (should be automatic, but verify)
docker exec -it neo4j-bsw-arch cypher-shell -u neo4j -p bsw-secure-password-2024

# In cypher-shell:
CREATE INDEX bot_name IF NOT EXISTS FOR (b:Bot) ON (b.name);
CREATE INDEX bot_domain IF NOT EXISTS FOR (b:Bot) ON (b.domain);
```

---

## 🎯 Next Steps

1. **Explore your documentation**: Try queries like "How do PIPE bots handle deployments?"

2. **Analyze bot dependencies**: Use `/bot-impact` before making changes

3. **Find reusable patterns**: Use `/bot-find-similar` to avoid duplication

4. **Create proposals with OpenSpec**: Use `/openspec-proposal` for new features

5. **Add custom MCP tools**: Extend the MCP server with domain-specific tools

6. **Integrate with CI/CD**: Add knowledge graph updates to your deployment pipeline

---

## 📚 Additional Resources

- **OpenCode Docs**: https://opencode.ai/docs
- **Neo4j Cypher Manual**: https://neo4j.com/docs/cypher-manual
- **MCP Protocol**: https://modelcontextprotocol.io
- **OpenSpec Guide**: https://github.com/fission-ai/openspec
- **BSW-Arch Documentation**: `/home/user/bsw-arch/docs/`

---

## 🙋 Getting Help

### Check Logs

```bash
# MCP server logs
tail -f /tmp/mcp_server.log

# Neo4j logs
docker logs -f neo4j-bsw-arch

# Ollama logs
journalctl -u ollama -f
```

### Test Individual Components

```bash
# Test Neo4j connection
python3 -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'bsw-secure-password-2024')); print('✓ Connected')"

# Test ChromaDB
python3 -c "import chromadb; client = chromadb.PersistentClient(path='./knowledge-graph/data/chroma_db'); print('✓ ChromaDB OK')"

# Test Ollama
ollama list
```

---

**Last Updated**: 2025-11-11
**Version**: 1.0
**Maintained by**: BSW-Tech Architecture Team

---

## 🎉 You're All Set!

You now have a powerful, privacy-first AI assistant that understands your bot factory architecture. Start exploring with:

```bash
cd /home/user/bsw-arch
opencode

> Tell me about the ECO domain bots
```

Happy bot building! 🤖🚀
