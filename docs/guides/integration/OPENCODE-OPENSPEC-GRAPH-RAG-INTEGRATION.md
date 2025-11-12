# OpenCode + OpenSpec + Knowledge Graph RAG Integration for BSW-Arch

## Executive Summary

This comprehensive guide integrates OpenCode, OpenSpec, and Knowledge-Enhanced Graph RAG into the BSW-Arch bot factory infrastructure, creating a complete spec-driven AI development platform that works seamlessly with IV bots, CAG+RAG architecture, and Proton Drive documentation storage.

**What You'll Build:**
- 🎯 Spec-driven development with OpenSpec
- 🧠 Knowledge graph-powered code intelligence
- 🤖 AI-assisted development with OpenCode
- 📊 Complete traceability from specs to code
- 🔒 100% open source, privacy-first, FAGAM-compliant

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Integration with BSW-Arch](#2-integration-with-bsw-arch)
3. [Prerequisites and Setup](#3-prerequisites-and-setup)
4. [OpenSpec Integration](#4-openspec-integration)
5. [Knowledge Graph Setup](#5-knowledge-graph-setup)
6. [Enhanced MCP Server](#6-enhanced-mcp-server)
7. [OpenCode Configuration](#7-opencode-configuration)
8. [Neovim Integration](#8-neovim-integration)
9. [Complete Workflow Examples](#9-complete-workflow-examples)
10. [Integration with IV Bots](#10-integration-with-iv-bots)
11. [Integration with Proton Drive](#11-integration-with-proton-drive)
12. [Advanced Features](#12-advanced-features)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Architecture Overview

### 1.1 Complete Integrated Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BSW-ARCH INTEGRATED AI DEVELOPMENT PLATFORM           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    SPEC-DRIVEN DEVELOPMENT LAYER                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │ │
│  │  │  OpenSpec    │→ │  OpenCode    │→ │  Validation  │             │ │
│  │  │  (Specs)     │  │  (AI Code)   │  │  (Tests)     │             │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                ↕                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    DOCUMENTATION & STORAGE LAYER                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │ │
│  │  │ Proton Drive │→ │  Local Sync  │→ │   Git Repo   │             │ │
│  │  │  (Cloud)     │  │  (/opt/docs) │  │   (GitHub)   │             │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                ↕                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    KNOWLEDGE & INTELLIGENCE LAYER                   │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │ │
│  │  │   Neo4j      │  │   ChromaDB   │  │  MCP Server  │             │ │
│  │  │ (Graph KB)   │  │  (Vectors)   │  │   (Tools)    │             │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                ↕                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    CAG+RAG PROCESSING LAYER                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │ │
│  │  │  CAG (Tier1) │→ │  RAG (Tier2) │→ │  Response    │             │ │
│  │  │  (Context)   │  │  (Retrieval) │  │  (Generate)  │             │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                ↕                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    IV BOTS EXECUTION LAYER                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │
│  │  │ iv-rag   │  │ iv-docs  │  │iv-validate│ │iv-learning│          │ │
│  │  │   bot    │  │   bot    │  │   bot     │ │    bot    │          │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │ │
│  │               ... 40 more IV bots ...                              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                ↕                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    LOCAL LLM LAYER                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │ │
│  │  │   Ollama     │  │    Claude    │  │   Hybrid     │             │ │
│  │  │ (Self-host)  │  │  (External)  │  │  (Strategy)  │             │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
1. SPECIFICATION PHASE
   ├─ OpenSpec creates proposals in Proton Drive
   ├─ Synced to local /opt/documentation/openspec
   └─ Indexed into Neo4j knowledge graph

2. CONTEXT BUILDING (CAG Tier 1)
   ├─ Query classified by domain (PIPE, IV, AXIS, etc.)
   ├─ OpenSpec specs provide requirements context
   ├─ Knowledge graph provides code structure context
   └─ Proton Drive ensures latest documentation

3. KNOWLEDGE RETRIEVAL (RAG Tier 2)
   ├─ Neo4j: Structural code relationships + specs
   ├─ ChromaDB: Semantic embeddings
   ├─ MCP Server: Unified tool interface
   └─ Hybrid search: Graph + Vector + Spec-aware

4. IMPLEMENTATION PHASE
   ├─ OpenCode generates code using full context
   ├─ IV bots validate against specifications
   ├─ Code indexed back into knowledge graph
   └─ Proton Drive sync archives completed changes

5. CONTINUOUS LEARNING
   ├─ iv-learning-bot detects documentation changes
   ├─ Knowledge graph auto-updates
   ├─ iv-validation-bot ensures spec compliance
   └─ Feedback loop improves future generations
```

---

## 2. Integration with BSW-Arch

### 2.1 How This Enhances Existing Infrastructure

**Integration Point 1: IV Bots**
- OpenSpec specifications become **requirements sources** for IV bots
- Knowledge graph provides **structural understanding** for RAG queries
- MCP server gives IV bots **spec-aware tools**
- iv-validation-bot ensures **spec compliance**

**Integration Point 2: CAG+RAG Architecture**
- OpenSpec specs feed into **CAG context building**
- Knowledge graph enhances **RAG retrieval quality**
- Spec-to-code traceability enables **impact analysis**
- Multi-domain routing uses **spec-aware classification**

**Integration Point 3: Proton Drive**
- OpenSpec specifications stored **encrypted in Proton Drive**
- Continuous sync keeps **local knowledge graph updated**
- Version control via Proton Drive provides **spec history**
- Team collaboration on specs with **end-to-end encryption**

**Integration Point 4: Bot Factory**
- **185 bots** can now query knowledge graph via MCP
- **Spec-driven bot development** with full traceability
- **Cross-domain bot coordination** using shared knowledge graph
- **Automated bot testing** against specifications

### 2.2 Benefits for BSW-Arch

✅ **Deterministic AI Development**: Specs lock intent before coding
✅ **Complete Traceability**: From requirements to implementation
✅ **Privacy-First**: 100% local processing, FAGAM-compliant
✅ **Team Collaboration**: Encrypted specs in Proton Drive
✅ **Quality Assurance**: Automated spec validation
✅ **Knowledge Preservation**: Institutional knowledge in graph

---

## 3. Prerequisites and Setup

### 3.1 System Requirements

```yaml
Required Components:
  - Python: 3.10+
  - Node.js: 20.19+
  - Docker: Latest
  - Neovim: 0.9+
  - Ollama: Latest

Storage Requirements:
  - Disk: 20GB free (10GB for models, 5GB for graphs, 5GB for docs)
  - RAM: 16GB recommended

Network Access:
  - Proton Drive: For documentation sync
  - GitHub: For code repositories
  - Ollama: Local LLM inference
  - Neo4j: Local graph database (port 7687)
  - ChromaDB: Local vector store
```

### 3.2 Installation Steps

```bash
#!/bin/bash
# complete-bsw-arch-ai-platform-setup.sh
# Complete setup for BSW-Arch integrated AI development platform

set -e

echo "🚀 BSW-Arch AI Development Platform Setup"
echo "=========================================="

# Step 1: Install OpenSpec (CRITICAL - Install First)
echo ""
echo "📋 Step 1: Installing OpenSpec..."
npm install -g @fission-ai/openspec@latest
openspec --version

# Step 2: Install OpenCode
echo ""
echo "🤖 Step 2: Installing OpenCode..."
curl -fsSL https://opencode.ai/install | bash
opencode --version

# Step 3: Install Ollama
echo ""
echo "🦙 Step 3: Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull deepseek-coder:latest

# Step 4: Install Python dependencies
echo ""
echo "🐍 Step 4: Installing Python dependencies..."
pip install --break-system-packages \
    fastmcp \
    neo4j \
    chromadb \
    tree-sitter \
    tree-sitter-python \
    tree-sitter-javascript \
    tree-sitter-typescript \
    sentence-transformers \
    pyyaml \
    watchdog \
    python-dotenv \
    proton-drive-cli

# Step 5: Start Neo4j
echo ""
echo "🗄️  Step 5: Starting Neo4j..."
docker run -d \
    --name neo4j-bsw-arch \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/bsw-arch-secure-password \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    neo4j:latest

# Wait for Neo4j to start
echo "Waiting for Neo4j to start..."
sleep 15

# Step 6: Clone BSW-Arch documentation
echo ""
echo "📚 Step 6: Setting up BSW-Arch documentation..."
sudo mkdir -p /opt/documentation
sudo chown $USER:$USER /opt/documentation

# Option A: From Proton Drive (if configured)
if command -v proton-drive-cli &> /dev/null; then
    echo "Syncing from Proton Drive..."
    proton-drive-cli sync \
        --remote /bsw-arch \
        --local /opt/documentation \
        --recursive
else
    # Option B: From GitHub
    echo "Cloning from GitHub..."
    git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation
fi

# Step 7: Initialize OpenSpec in BSW-Arch
echo ""
echo "📋 Step 7: Initializing OpenSpec..."
cd /opt/documentation
openspec init

# Step 8: Index the codebase
echo ""
echo "📊 Step 8: Building knowledge graph..."
# Download the enhanced indexer from this guide
python3 /opt/documentation/bot-utils/graph_indexer_with_specs.py /opt/documentation

# Step 9: Configure OpenCode
echo ""
echo "⚙️  Step 9: Configuring OpenCode..."
mkdir -p ~/.config/opencode

cat > ~/.config/opencode/opencode.json << 'EOF'
{
  "provider": "ollama",
  "model": "deepseek-coder:latest",
  "api_base": "http://localhost:11434",
  "temperature": 0.2,
  "mcp": {
    "servers": {
      "bsw-arch-knowledge-graph": {
        "command": "python3",
        "args": ["/opt/documentation/bot-utils/enhanced_mcp_server.py"],
        "env": {
          "NEO4J_URI": "bolt://localhost:7687",
          "NEO4J_USER": "neo4j",
          "NEO4J_PASSWORD": "bsw-arch-secure-password",
          "CHROMA_PATH": "/opt/documentation/chroma_db",
          "OPENSPEC_PATH": "/opt/documentation/openspec"
        }
      }
    }
  },
  "theme": "default",
  "autoApprove": false,
  "shell": "/bin/bash",
  "autoCompact": true
}
EOF

# Step 10: Verify setup
echo ""
echo "✅ Step 10: Verifying setup..."

echo "  Checking OpenSpec..."
openspec --version && echo "  ✓ OpenSpec installed" || echo "  ✗ OpenSpec not found"

echo "  Checking OpenCode..."
opencode --version && echo "  ✓ OpenCode installed" || echo "  ✗ OpenCode not found"

echo "  Checking Neo4j..."
curl -s http://localhost:7474 > /dev/null && echo "  ✓ Neo4j running" || echo "  ✗ Neo4j not running"

echo "  Checking Ollama..."
curl -s http://localhost:11434/api/tags > /dev/null && echo "  ✓ Ollama running" || echo "  ✗ Ollama not running"

echo "  Checking documentation..."
[ -d "/opt/documentation/docs" ] && echo "  ✓ Documentation synced" || echo "  ✗ Documentation not found"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Access Neo4j Browser: http://localhost:7474"
echo "2. Login: neo4j / bsw-arch-secure-password"
echo "3. Start OpenCode: cd /opt/documentation && opencode"
echo "4. Try: /openspec:proposal Add my first feature"
echo ""
echo "Documentation:"
echo "- IV Bots Setup: /opt/documentation/docs/guides/setup/IV-BOTS-SETUP.md"
echo "- CAG+RAG Architecture: /opt/documentation/docs/architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md"
echo "- This Guide: /opt/documentation/docs/guides/integration/OPENCODE-OPENSPEC-GRAPH-RAG-INTEGRATION.md"
```

---

## 4. OpenSpec Integration

### 4.1 Initialize OpenSpec for BSW-Arch

```bash
cd /opt/documentation

# Initialize OpenSpec
openspec init

# This creates:
# /opt/documentation/openspec/
#   ├── AGENTS.md       # AI workflow instructions
#   ├── project.md      # BSW-Arch project context
#   ├── specs/          # Current specifications
#   └── changes/        # Active changes
```

### 4.2 Configure BSW-Arch Project Context

Edit `/opt/documentation/openspec/project.md`:

```markdown
# BSW-Arch Project Context

## Purpose
BSW-Arch is a comprehensive bot factory architecture with 185 specialized bots
across 4 domains (AXIS, PIPE, ECO, IV) designed for secure, FAGAM-compliant,
AI-driven development and operations.

## Tech Stack
- **Backend**: Python (FastAPI), Go
- **Frontend**: React, TypeScript
- **AI/ML**: Ollama (DeepSeek Coder, LLaMA), Claude (external)
- **Knowledge**: Neo4j (graph), ChromaDB (vectors), PostgreSQL
- **Infrastructure**: Kubernetes, Docker, GitOps (ArgoCD)
- **Storage**: Proton Drive (encrypted), GitHub
- **Containers**: apko + Wolfi base (<50MB per bot)

## Architecture Patterns
- **Bot Factory**: 185 specialized bots across 4 domains
- **CAG+RAG**: 2-tier context-aware + retrieval-augmented generation
- **Knowledge Graph**: Neo4j-based code and spec intelligence
- **Spec-Driven**: OpenSpec for requirements management
- **Privacy-First**: All AI processing local (Ollama)
- **FAGAM-Compliant**: No Facebook, Apple, Google, Amazon, Microsoft

## Bot Domains
- **AXIS (45 bots)**: AI model management and deployment
- **PIPE (48 bots)**: Core API and integration
- **ECO (48 bots)**: Ecosystem and blockchain
- **IV (44 bots)**: Intelligence, validation, RAG

## Coding Conventions
- **Python**: PEP 8, type hints required, docstrings mandatory
- **Go**: gofmt, golangci-lint
- **TypeScript**: ESLint + Prettier, strict mode
- **Containers**: <50MB using apko + Wolfi
- **Testing**: 80% coverage minimum
- **Documentation**: UK English, comprehensive

## Security Requirements
- **FAGAM Prohibition**: Strictly enforced
- **Encryption**: End-to-end for all data at rest
- **Authentication**: Certificate + 2FA
- **Network Segmentation**: Isolated zones per domain
- **Audit Logging**: All operations logged

## Performance Targets
- **API Response**: <200ms p95
- **Bot Startup**: <5 seconds
- **Container Size**: <50MB (exceptions require approval)
- **Knowledge Graph Query**: <500ms
- **RAG Query**: <2 seconds end-to-end

## Knowledge Graph Structure
**Nodes:**
- Function, Class, Module, File (code)
- Specification, Requirement, Scenario (specs)
- Change, Task (OpenSpec)
- Bot, Domain, Service (architecture)

**Relationships:**
- CALLS, IMPORTS, INHERITS (code)
- IMPLEMENTS, FULFILLS (spec-to-code)
- CONTAINS, MODIFIES (OpenSpec)
- DEPENDS_ON, DEPLOYED_IN (architecture)

## Testing Strategy
- **Unit Tests**: Every function, pytest
- **Integration Tests**: API endpoints, cross-bot communication
- **Spec Validation**: 100% requirement coverage
- **Performance Tests**: Load testing for critical paths
- **Security Tests**: OWASP Top 10 compliance

## Documentation Standards
- **Architecture**: TOGAF, ArchiMate
- **API**: OpenAPI 3.0
- **Specs**: OpenSpec format
- **Knowledge Base**: Markdown in Proton Drive
- **Code**: Inline docstrings + external guides
```

### 4.3 Create Your First Specification

```bash
# Create a specification for IV bot authentication
openspec scaffold iv-bot-authentication

# This creates:
# openspec/changes/iv-bot-authentication/
#   ├── proposal.md
#   ├── tasks.md
#   └── specs/
#       └── iv-bot-authentication.md
```

Edit `openspec/changes/iv-bot-authentication/specs/iv-bot-authentication.md`:

```markdown
# Specification: IV Bot Authentication

## Overview
All IV bots SHALL authenticate with the knowledge graph using certificate-based
authentication with 2FA backup.

### Requirement: Certificate-Based Authentication
Each IV bot SHALL use X.509 certificates for authentication to Neo4j.

#### Scenario: Normal Authentication
- **Given**: IV bot has valid certificate
- **When**: Bot attempts to connect to Neo4j
- **Then**: Connection is established successfully

#### Scenario: Certificate Expired
- **Given**: IV bot has expired certificate
- **When**: Bot attempts to connect
- **Then**: Connection is refused and error logged

#### Acceptance Criteria:
- [ ] Certificate validity checked before connection
- [ ] Expired certificates rejected
- [ ] Certificate rotation supported
- [ ] Audit log entry created for each attempt

### Requirement: 2FA Backup Authentication
IV bots SHALL support TOTP-based 2FA as fallback authentication.

#### Scenario: 2FA Fallback
- **Given**: Certificate authentication unavailable
- **When**: Bot uses 2FA token
- **Then**: Connection established with reduced privileges

#### Acceptance Criteria:
- [ ] TOTP tokens validated
- [ ] Time-window synchronization handled
- [ ] Fallback privileges documented
- [ ] Security team notified of fallback usage

## Testing Requirements
- Unit tests for certificate validation
- Integration tests for Neo4j connection
- Security tests for invalid certificate handling
- Performance tests for connection pooling
```

---

## 5. Knowledge Graph Setup

### 5.1 Enhanced Indexer with OpenSpec Support

The enhanced indexer (from the guide) now indexes:
- **Code**: Functions, classes, imports, calls
- **Specifications**: Requirements, scenarios, acceptance criteria
- **Changes**: Proposals, tasks, design docs
- **Relationships**: Spec-to-code implementation links

```bash
# Index BSW-Arch with specs
python3 /opt/documentation/bot-utils/graph_indexer_with_specs.py /opt/documentation

# Expected output:
# 📂 Indexing repository: /opt/documentation
# 📋 Indexing OpenSpec specifications...
#   Processing: openspec/specs/iv-bot-authentication.md
#   Processing: openspec/changes/iv-bot-authentication/...
# 💻 Indexing code files...
#   Processing: bot-utils/doc_scanner.py
#   Processing: bot-utils/github_api_client.py
#   ...
# 🔗 Linking specifications to code...
#   Created 42 spec-to-code links
# ✅ Indexing complete! 156 files indexed
```

### 5.2 Verify Knowledge Graph

```bash
# Access Neo4j Browser
open http://localhost:7474

# Login: neo4j / bsw-arch-secure-password

# Run queries to explore:

# 1. View all specifications
MATCH (s:Specification)
RETURN s.id, s.status
LIMIT 10;

# 2. Find spec-to-code links
MATCH (s:Specification)-[:CONTAINS]->(r:Requirement)
MATCH (r)<-[:IMPLEMENTS]-(f:Function)
RETURN s.id, r.description, f.name, f.file
LIMIT 10;

# 3. Check OpenSpec changes
MATCH (c:Change)-[:HAS_TASK]->(t:Task)
RETURN c.id, c.status, count(t) as tasks
LIMIT 10;

# 4. Find unspecified code
MATCH (f:Function)
WHERE NOT (f)-[:IMPLEMENTS]->(:Requirement)
RETURN f.name, f.file
LIMIT 20;
```

---

## 6. Enhanced MCP Server

### 6.1 Start the MCP Server

The enhanced MCP server provides spec-aware tools to OpenCode:

```bash
# Start MCP server
cd /opt/documentation/bot-utils
python3 enhanced_mcp_server.py

# Server provides these tools:
# - query_spec_aware_graph
# - validate_spec_implementation
# - analyze_change_impact_with_specs
# - suggest_spec_for_code
# - find_unspecified_code
# - generate_traceability_matrix
```

### 6.2 Test MCP Tools

```bash
# Test from OpenCode
opencode

# Query with spec awareness
> Use query_spec_aware_graph to explain IV bot authentication

# Validate a specification
> Use validate_spec_implementation for "iv-bot-authentication"

# Find code without specs
> Use find_unspecified_code
```

---

## 7. OpenCode Configuration

### 7.1 BSW-Arch OpenCode Configuration

File: `~/.config/opencode/opencode.json`

```json
{
  "provider": "ollama",
  "model": "deepseek-coder:latest",
  "api_base": "http://localhost:11434",
  "temperature": 0.2,
  "mcp": {
    "servers": {
      "bsw-arch-knowledge-graph": {
        "command": "python3",
        "args": ["/opt/documentation/bot-utils/enhanced_mcp_server.py"],
        "env": {
          "NEO4J_URI": "bolt://localhost:7687",
          "NEO4J_USER": "neo4j",
          "NEO4J_PASSWORD": "bsw-arch-secure-password",
          "CHROMA_PATH": "/opt/documentation/chroma_db",
          "OPENSPEC_PATH": "/opt/documentation/openspec"
        }
      }
    }
  },
  "openspec": {
    "enabled": true,
    "autoValidate": true,
    "strictMode": true
  },
  "theme": "default",
  "autoApprove": false,
  "shell": "/bin/bash",
  "autoCompact": true
}
```

### 7.2 BSW-Arch Custom Commands

Create `.opencode/commands/` in your project:

**File: `.opencode/commands/bsw-validate-bot.md`**

```markdown
---
description: "Validate bot implementation against BSW-Arch standards"
---

Validate the current bot implementation using BSW-Arch standards:

1. Use `query_spec_aware_graph` to find the bot's specification
2. Use `validate_spec_implementation` to check requirement coverage
3. Verify container size is <50MB
4. Check FAGAM compliance (no prohibited dependencies)
5. Ensure UK English in all documentation
6. Validate test coverage >80%
7. Check security: certificate auth, encryption, audit logging

Generate a comprehensive validation report.
```

**File: `.opencode/commands/bsw-create-iv-bot.md`**

```markdown
---
description: "Create a new IV bot following BSW-Arch patterns"
agent: "build"
---

Create a new IV bot for the BSW-Arch bot factory:

1. Ask user for bot purpose and category (AI/ML, RAG, Validation, etc.)
2. Use `/openspec:proposal` to create specification
3. Use `query_spec_aware_graph` to find similar IV bots
4. Generate bot code following patterns:
   - Dockerfile with Wolfi base
   - Python main.py with IV bot template
   - Proton Drive sync on startup
   - Neo4j knowledge graph integration
   - Test suite with >80% coverage
5. Use `validate_spec_implementation` to verify
6. Create Kubernetes deployment manifest
7. Update bot factory documentation

Ensure FAGAM compliance throughout.
```

---

## 8. Neovim Integration

### 8.1 Complete Neovim Configuration

File: `~/.config/nvim/lua/plugins/bsw-arch-ai.lua`

```lua
return {
  -- OpenCode + OpenSpec + BSW-Arch keybindings
  {
    "folke/which-key.nvim",
    optional = true,
    opts = function(_, opts)
      opts.spec = opts.spec or {}
      table.insert(opts.spec, {
        -- OpenCode base
        { "<leader>o", group = "opencode", icon = "🤖" },
        { "<leader>oo", "<cmd>!opencode<cr>", desc = "Open OpenCode", icon = "🚀" },

        -- OpenSpec workflow
        { "<leader>s", group = "openspec", icon = "📋" },
        { "<leader>sp", "<cmd>!opencode /openspec:proposal<cr>", desc = "Create proposal", icon = "📝" },
        { "<leader>sa", "<cmd>!opencode /openspec:apply<cr>", desc = "Apply change", icon = "⚙️" },
        { "<leader>sr", "<cmd>!opencode /openspec:archive<cr>", desc = "Archive change", icon = "📦" },
        { "<leader>sv", "<cmd>!openspec validate --strict<cr>", desc = "Validate specs", icon = "✓" },
        { "<leader>sl", "<cmd>!openspec list<cr>", desc = "List changes", icon = "📋" },

        -- Knowledge Graph queries
        { "<leader>g", group = "knowledge-graph", icon = "🌐" },
        { "<leader>gq", desc = "Query graph", icon = "🔍",
          "<cmd>!opencode 'Use query_spec_aware_graph to'<cr>"
        },
        { "<leader>gv", desc = "Validate spec", icon = "✓",
          "<cmd>!opencode 'Use validate_spec_implementation'<cr>"
        },
        { "<leader>gi", desc = "Impact analysis", icon = "⚡",
          "<cmd>!opencode 'Use analyze_change_impact_with_specs'<cr>"
        },
        { "<leader>gu", desc = "Unspecified code", icon = "❓",
          "<cmd>!opencode 'Use find_unspecified_code'<cr>"
        },
        { "<leader>gt", desc = "Traceability matrix", icon = "📊",
          "<cmd>!opencode 'Use generate_traceability_matrix'<cr>"
        },

        -- BSW-Arch specific
        { "<leader>b", group = "bsw-arch", icon = "🏭" },
        { "<leader>bb", "<cmd>!opencode /bsw-create-iv-bot<cr>", desc = "Create IV bot", icon = "🤖" },
        { "<leader>bv", "<cmd>!opencode /bsw-validate-bot<cr>", desc = "Validate bot", icon = "✓" },
        { "<leader>bd", "<cmd>!proton-drive-cli sync<cr>", desc = "Sync Proton Drive", icon = "☁️" },
        { "<leader>br", desc = "Re-index knowledge graph", icon = "📊",
          "<cmd>!python3 /opt/documentation/bot-utils/graph_indexer_with_specs.py /opt/documentation<cr>"
        },
      })
    end,
  },

  -- Telescope for browsing BSW-Arch docs and specs
  {
    "nvim-telescope/telescope.nvim",
    keys = {
      {
        "<leader>fs",
        function()
          require("telescope.builtin").find_files({
            cwd = "/opt/documentation/openspec",
            prompt_title = "OpenSpec Files",
          })
        end,
        desc = "Find specs",
      },
      {
        "<leader>fd",
        function()
          require("telescope.builtin").find_files({
            cwd = "/opt/documentation/docs",
            prompt_title = "BSW-Arch Docs",
          })
        end,
        desc = "Find BSW docs",
      },
      {
        "<leader>fb",
        function()
          require("telescope.builtin").grep_string({
            cwd = "/opt/documentation",
            search = "iv-.*-bot",
            prompt_title = "Find IV Bots",
          })
        end,
        desc = "Find IV bots",
      },
    },
  },
}
```

---

## 9. Complete Workflow Examples

### 9.1 Example: Create a New IV Bot

**Scenario**: Create `iv-summarize-bot` for documentation summarization

```bash
# Step 1: Create proposal
opencode

> /openspec:proposal Create iv-summarize-bot for documentation summarization

# OpenCode creates:
# openspec/changes/create-iv-summarize-bot/
#   ├── proposal.md
#   ├── tasks.md
#   └── specs/
#       └── iv-summarize-bot.md

# Step 2: Query existing bots for patterns
> Use query_spec_aware_graph to find similar IV bots like iv-docs-bot

# OpenCode shows:
# Found iv-docs-bot in docs/guides/setup/IV-BOTS-SETUP.md
# Pattern: NLP bot category
# Dependencies: sentence-transformers, spaCy
# Container: ~150MB (needs approval for >50MB)

# Step 3: Refine specification with graph insights
> Update the proposal to follow iv-docs-bot patterns
> Ensure container <200MB with model included

# Step 4: Validate proposal
openspec validate create-iv-summarize-bot --strict

# Step 5: Implement
> /openspec:apply create-iv-summarize-bot

# OpenCode generates:
# - Dockerfile with Wolfi base
# - Python main.py with summarization logic
# - Kubernetes deployment manifest
# - Test suite
# - Documentation

# Step 6: Validate implementation
> Use validate_spec_implementation for "iv-summarize-bot"

# OpenCode reports:
# Overall Coverage: 100% (5/5 requirements)
# All acceptance criteria met
# Test coverage: 87%

# Step 7: Test and deploy
pytest tests/test_iv_summarize_bot.py
kubectl apply -f k8s/iv-summarize-bot-deployment.yaml

# Step 8: Archive
openspec archive create-iv-summarize-bot

# Step 9: Re-index knowledge graph
python3 /opt/documentation/bot-utils/graph_indexer_with_specs.py /opt/documentation

# Done! New bot is part of the knowledge graph
```

### 9.2 Example: Validate All IV Bots Against Specs

```bash
opencode

> Check all 44 IV bots for specification compliance

> For each IV bot:
  1. Use find_unspecified_code to list bots without specs
  2. For bots with specs, use validate_spec_implementation
  3. Generate a compliance report showing:
     - Bots with 100% spec coverage
     - Bots with partial coverage
     - Bots without any specs
  4. Prioritize bots that need specs

# OpenCode analyzes and reports:
#
# IV Bot Specification Compliance Report
# ======================================
#
# ✅ Full Compliance (35 bots):
#   - iv-rag-bot: 100% (12/12 requirements)
#   - iv-docs-bot: 100% (8/8 requirements)
#   ...
#
# ⚠️ Partial Compliance (7 bots):
#   - iv-analysis-bot: 75% (9/12 requirements)
#   - iv-trends-bot: 60% (6/10 requirements)
#   ...
#
# ❌ No Specification (2 bots):
#   - iv-legacy-bot
#   - iv-experimental-bot
#
# Recommendations:
# 1. Create specs for 2 unspecified bots
# 2. Complete 19 missing requirements across 7 bots
# 3. Add tests for 14 implementations with <80% coverage

> Create proposals for the 2 bots without specs using suggest_spec_for_code
```

---

## 10. Integration with IV Bots

### 10.1 Enhanced IV Bot Template

**File: `templates/iv-bot-with-knowledge-graph.py`**

```python
#!/usr/bin/env python3
"""
Enhanced IV Bot Template with Knowledge Graph Integration
Integrates with OpenSpec, Neo4j, and Proton Drive
"""

import os
import sys
import logging
from pathlib import Path

# Add bot-utils to path
sys.path.insert(0, "/opt/documentation/bot-utils")

from doc_scanner import DocScanner
from neo4j import GraphDatabase
import chromadb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeGraphIVBot:
    """Base class for IV bots with knowledge graph integration"""

    def __init__(self, bot_name: str):
        self.bot_name = bot_name
        self.docs_path = Path("/opt/documentation")

        # Initialize documentation scanner
        self.doc_scanner = DocScanner(str(self.docs_path))

        # Initialize Neo4j connection
        self.neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "password")
            )
        )

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.docs_path / "chroma_db")
        )

        logger.info(f"✅ {bot_name} initialized with knowledge graph")

    def query_knowledge_graph(self, cypher: str, **params):
        """Query Neo4j knowledge graph"""
        with self.neo4j_driver.session() as session:
            result = session.run(cypher, **params)
            return list(result)

    def get_my_specification(self):
        """Get OpenSpec specification for this bot"""
        spec_query = """
        MATCH (s:Specification)
        WHERE s.id CONTAINS $bot_name
        RETURN s.id, s.content
        """
        return self.query_knowledge_graph(spec_query, bot_name=self.bot_name)

    def validate_against_spec(self):
        """Validate bot implementation against its specification"""
        spec = self.get_my_specification()
        if not spec:
            logger.warning(f"⚠️  No specification found for {self.bot_name}")
            return False

        logger.info(f"✓ Specification found: {spec[0]['s.id']}")

        # Check if all requirements are implemented
        impl_query = """
        MATCH (s:Specification {id: $spec_id})-[:CONTAINS]->(r:Requirement)
        OPTIONAL MATCH (r)<-[:IMPLEMENTS]-(f:Function)
        WITH r, count(f) as impl_count
        RETURN
            count(r) as total_reqs,
            sum(CASE WHEN impl_count > 0 THEN 1 ELSE 0 END) as implemented_reqs
        """

        result = self.query_knowledge_graph(
            impl_query,
            spec_id=spec[0]['s.id']
        )

        if result:
            total = result[0]['total_reqs']
            implemented = result[0]['implemented_reqs']
            coverage = implemented / total if total > 0 else 0

            logger.info(f"📊 Spec coverage: {coverage:.1%} ({implemented}/{total})")
            return coverage == 1.0

        return False

    def run(self):
        """Main bot execution"""
        logger.info(f"🚀 Starting {self.bot_name}...")

        # Validate against spec
        if self.validate_against_spec():
            logger.info("✅ Spec validation passed")
        else:
            logger.warning("⚠️  Spec validation failed - review implementation")

        # Bot-specific logic here
        self.execute()

        logger.info(f"✓ {self.bot_name} completed")

    def execute(self):
        """Override this method in subclasses"""
        raise NotImplementedError("Subclass must implement execute()")

    def __del__(self):
        """Cleanup connections"""
        if hasattr(self, 'neo4j_driver'):
            self.neo4j_driver.close()


# Example: IV Summarize Bot
class IVSummarizeBot(KnowledgeGraphIVBot):
    """Summarizes documentation using knowledge graph context"""

    def __init__(self):
        super().__init__("iv-summarize-bot")

        # Load summarization model
        from transformers import pipeline
        self.summarizer = pipeline("summarization", model="t5-base")

    def execute(self):
        """Summarize documentation"""
        # Get documents from knowledge graph
        docs_query = """
        MATCH (f:File)
        WHERE f.path ENDS WITH '.md'
        RETURN f.path, f.content
        LIMIT 10
        """

        docs = self.query_knowledge_graph(docs_query)

        for doc in docs:
            content = doc['f.content']
            if content and len(content) > 100:
                summary = self.summarizer(
                    content[:1000],  # Limit input
                    max_length=100,
                    min_length=30
                )

                logger.info(f"📄 {doc['f.path']}")
                logger.info(f"📝 Summary: {summary[0]['summary_text']}")


if __name__ == "__main__":
    bot = IVSummarizeBot()
    bot.run()
```

### 10.2 Deploy IV Bot with Knowledge Graph

**File: `k8s/iv-summarize-bot-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iv-summarize-bot
  namespace: iv-bots
  labels:
    app: iv-summarize-bot
    domain: iv
    category: nlp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: iv-summarize-bot
  template:
    metadata:
      labels:
        app: iv-summarize-bot
    spec:
      containers:
      - name: iv-summarize-bot
        image: bsw-arch/iv-summarize-bot:latest
        env:
        - name: NEO4J_URI
          value: "bolt://neo4j-bsw-arch.iv-bots.svc:7687"
        - name: NEO4J_USER
          valueFrom:
            secretKeyRef:
              name: neo4j-credentials
              key: username
        - name: NEO4J_PASSWORD
          valueFrom:
            secretKeyRef:
              name: neo4j-credentials
              key: password
        - name: OPENSPEC_PATH
          value: "/opt/documentation/openspec"
        volumeMounts:
        - name: documentation
          mountPath: /opt/documentation
          readOnly: true
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
      volumes:
      - name: documentation
        persistentVolumeClaim:
          claimName: bsw-arch-docs-pvc
```

---

## 11. Integration with Proton Drive

### 11.1 Sync OpenSpec to Proton Drive

```bash
# Configure Proton Drive to sync OpenSpec
cat >> ~/.config/proton-drive/sync-config.yaml << 'EOF'
sync_paths:
  - local: /opt/documentation/openspec
    remote: /bsw-arch/openspec
    bidirectional: true
    watch: true

  - local: /opt/documentation/docs
    remote: /bsw-arch/docs
    bidirectional: false  # One-way: Proton → local
    watch: true

sync_interval: 300  # 5 minutes
EOF
```

### 11.2 Automated Workflow

```python
#!/usr/bin/env python3
"""
Complete BSW-Arch workflow with Proton Drive integration
"""

import subprocess
import time
from pathlib import Path

def complete_workflow_with_proton():
    """
    1. Proton Drive syncs latest specs
    2. Knowledge graph re-indexes
    3. IV bots validate against specs
    4. Changes archived back to Proton Drive
    """

    print("🔄 Starting complete BSW-Arch workflow...")

    # Step 1: Sync from Proton Drive
    print("\n📥 Step 1: Syncing from Proton Drive...")
    subprocess.run([
        "proton-drive-cli", "sync",
        "--remote", "/bsw-arch",
        "--local", "/opt/documentation",
        "--recursive"
    ])

    # Step 2: Re-index knowledge graph
    print("\n📊 Step 2: Re-indexing knowledge graph...")
    subprocess.run([
        "python3",
        "/opt/documentation/bot-utils/graph_indexer_with_specs.py",
        "/opt/documentation"
    ])

    # Step 3: Validate all IV bots
    print("\n✅ Step 3: Validating IV bots...")
    # This would call OpenCode with validation command
    subprocess.run([
        "opencode",
        "-p", "Use find_unspecified_code and validate all IV bots"
    ])

    # Step 4: Archive completed changes
    print("\n📦 Step 4: Archiving completed changes...")
    changes_dir = Path("/opt/documentation/openspec/changes")
    for change_dir in changes_dir.iterdir():
        if change_dir.is_dir():
            # Check if all tasks completed
            tasks_file = change_dir / "tasks.md"
            if tasks_file.exists():
                content = tasks_file.read_text()
                if "- [ ]" not in content:  # All tasks checked
                    change_id = change_dir.name
                    print(f"  Archiving {change_id}...")
                    subprocess.run(["openspec", "archive", change_id])

    # Step 5: Sync back to Proton Drive
    print("\n📤 Step 5: Syncing back to Proton Drive...")
    subprocess.run([
        "proton-drive-cli", "sync",
        "--local", "/opt/documentation",
        "--remote", "/bsw-arch",
        "--recursive"
    ])

    print("\n✅ Complete workflow finished!")

if __name__ == "__main__":
    # Run every hour
    while True:
        complete_workflow_with_proton()
        time.sleep(3600)
```

---

## 12. Advanced Features

### 12.1 CI/CD Integration

**File: `.github/workflows/bsw-arch-spec-compliance.yml`**

```yaml
name: BSW-Arch Spec Compliance

on:
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  spec-compliance:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          npm install -g @fission-ai/openspec@latest
          pip install -r requirements.txt

      - name: Start Neo4j
        run: |
          docker run -d \
            --name neo4j-ci \
            -p 7474:7474 -p 7687:7687 \
            -e NEO4J_AUTH=neo4j/ci-password \
            neo4j:latest
          sleep 15

      - name: Index codebase
        run: |
          python3 bot-utils/graph_indexer_with_specs.py .

      - name: Validate all specs
        run: |
          openspec list --specs | while read spec_id; do
            echo "Validating $spec_id..."
            openspec validate "$spec_id" --strict
          done

      - name: Generate compliance report
        run: |
          python3 << 'EOF'
import asyncio
from enhanced_mcp_server import (
    validate_spec_implementation,
    find_unspecified_code,
    generate_traceability_matrix
)

async def main():
    # Check all specs
    specs = [...]  # Load from openspec/

    for spec_id in specs:
        result = await validate_spec_implementation(spec_id)
        print(result)
        print("\n" + "="*70 + "\n")

    # Find unspecified code
    unspecified = await find_unspecified_code()
    print(unspecified)
    print("\n" + "="*70 + "\n")

    # Generate traceability matrix
    matrix = await generate_traceability_matrix()
    print(matrix)

asyncio.run(main())
EOF

      - name: Check compliance threshold
        run: |
          # Fail if coverage < 90%
          python3 -c "
from enhanced_mcp_server import validate_spec_implementation
import asyncio

async def check():
    specs = [...]  # Load from openspec/
    total_coverage = 0
    for spec_id in specs:
        result = await validate_spec_implementation(spec_id)
        # Parse coverage from result
        # total_coverage += coverage

    avg_coverage = total_coverage / len(specs)
    if avg_coverage < 0.90:
        print(f'Spec coverage {avg_coverage:.1%} below 90% threshold')
        exit(1)

asyncio.run(check())
          "
```

### 12.2 Automated Spec Generation

```bash
opencode

> For all IV bots without specifications:
  1. Use find_unspecified_code to list them
  2. For each unspecified bot:
     a. Use suggest_spec_for_code to generate draft spec
     b. Analyze code patterns and dependencies
     c. Create comprehensive OpenSpec specification
     d. Include requirements, scenarios, acceptance criteria
  3. Save to openspec/changes/add-specs-for-iv-bots/
  4. Create a proposal for bulk spec addition

# OpenCode will generate specs for all 44 IV bots
```

---

## 13. Troubleshooting

### 13.1 Common Issues

#### Issue: OpenSpec commands not working

```bash
# Solution 1: Verify OpenSpec installation
npm list -g @fission-ai/openspec
# Should show version

# Solution 2: Reinstall
npm install -g @fission-ai/openspec@latest

# Solution 3: Check OpenCode recognizes it
opencode
> /openspec:proposal test
# Should create proposal, not error
```

#### Issue: Knowledge graph doesn't link specs to code

```bash
# Solution: Re-index with enhanced indexer
python3 /opt/documentation/bot-utils/graph_indexer_with_specs.py /opt/documentation

# Verify links
opencode
> Use query_spec_aware_graph to show spec-code links for IV bots
```

#### Issue: MCP server tools not available

```bash
# Check MCP server is running
ps aux | grep enhanced_mcp_server

# Check OpenCode config
cat ~/.config/opencode/opencode.json | grep -A5 '"mcp"'

# Ensure absolute paths
# WRONG: "args": ["./enhanced_mcp_server.py"]
# RIGHT: "args": ["/opt/documentation/bot-utils/enhanced_mcp_server.py"]
```

#### Issue: Proton Drive sync fails

```bash
# Check authentication
proton-drive-cli login

# Test sync
proton-drive-cli sync \
    --remote /bsw-arch \
    --local /opt/documentation \
    --dry-run

# Check logs
journalctl -u proton-drive-sync -f
```

---

## Summary

This integration creates a **world-class, privacy-first AI development platform** for BSW-Arch:

✅ **Spec-Driven Development**: OpenSpec ensures requirements are clear
✅ **Knowledge Graph Intelligence**: Neo4j understands code structure
✅ **AI-Assisted Coding**: OpenCode with full context awareness
✅ **Complete Traceability**: From specs to code to deployment
✅ **Secure Collaboration**: Proton Drive for encrypted spec storage
✅ **Privacy-First**: All AI processing local (Ollama)
✅ **FAGAM-Compliant**: Zero dependencies on prohibited services
✅ **Bot Factory Ready**: All 185 bots can leverage the platform

### Next Steps

1. **Run complete setup script** (Section 3.2)
2. **Create your first spec** (Section 4.3)
3. **Index the knowledge graph** (Section 5.1)
4. **Configure OpenCode** (Section 7.1)
5. **Create your first IV bot** (Section 9.1)

### Documentation Links

- [IV Bots Setup Guide](../setup/IV-BOTS-SETUP.md)
- [CAG+RAG Architecture](../../architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md)
- [Proton Drive Integration](./PROTON-DRIVE-INTEGRATION.md)
- [Comprehensive Bot Factory Architecture](../../architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md)

---

*Document Version: 1.0*
*Last Updated: 2025-11-11*
*Integration: OpenCode + OpenSpec + Graph RAG + BSW-Arch*
*For support: https://github.com/bsw-arch/bsw-arch/issues*
