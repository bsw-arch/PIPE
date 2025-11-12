#!/bin/bash
# BSW-Arch Knowledge Graph Setup Script
# Sets up OpenCode + Neo4j + MCP for bot factory architecture

set -e

echo "🚀 BSW-Arch Knowledge Graph Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in correct directory
if [ ! -f "README.md" ] || [ ! -d "docs" ]; then
    echo "❌ Error: Please run this script from the bsw-arch root directory"
    exit 1
fi

echo "${YELLOW}Step 1: Installing system dependencies${NC}"
echo "---------------------------------------"

# Check for required tools
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Please install Docker first."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }

echo "✓ All required tools found"
echo ""

echo "${YELLOW}Step 2: Starting Neo4j database${NC}"
echo "--------------------------------"

# Start Neo4j container for knowledge graph
if ! docker ps | grep -q neo4j-bsw-arch; then
    echo "Starting Neo4j container..."
    docker run -d \
      --name neo4j-bsw-arch \
      -p 7474:7474 \
      -p 7687:7687 \
      -e NEO4J_AUTH=neo4j/bsw-secure-password-2024 \
      -v $HOME/neo4j-bsw/data:/data \
      -v $HOME/neo4j-bsw/logs:/logs \
      neo4j:latest

    echo "⏳ Waiting for Neo4j to start (30 seconds)..."
    sleep 30
    echo "✓ Neo4j started"
else
    echo "✓ Neo4j container already running"
fi

echo ""
echo "${YELLOW}Step 3: Installing Python dependencies${NC}"
echo "---------------------------------------"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate and install
source venv/bin/activate

pip install -q --upgrade pip
pip install -q \
    fastmcp \
    neo4j \
    chromadb \
    tree-sitter \
    tree-sitter-python \
    tree-sitter-javascript \
    tree-sitter-typescript \
    sentence-transformers \
    pyyaml

echo "✓ Python dependencies installed"
echo ""

echo "${YELLOW}Step 4: Installing Ollama (if not installed)${NC}"
echo "---------------------------------------------"

if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✓ Ollama installed"
else
    echo "✓ Ollama already installed"
fi

# Pull DeepSeek Coder model
echo "Pulling DeepSeek Coder model (this may take a while)..."
ollama pull deepseek-coder:6.7b 2>/dev/null || echo "Model already exists"
echo "✓ DeepSeek Coder model ready"
echo ""

echo "${YELLOW}Step 5: Installing OpenCode${NC}"
echo "----------------------------"

if ! command -v opencode &> /dev/null; then
    echo "Installing OpenCode..."
    npm install -g opencode-ai@latest
    echo "✓ OpenCode installed"
else
    echo "✓ OpenCode already installed"
fi

echo ""
echo "${YELLOW}Step 6: Installing OpenSpec${NC}"
echo "----------------------------"

if ! command -v openspec &> /dev/null; then
    echo "Installing OpenSpec..."
    npm install -g @fission-ai/openspec@latest
    echo "✓ OpenSpec installed"
else
    echo "✓ OpenSpec already installed"
fi

echo ""
echo "${YELLOW}Step 7: Creating project structure${NC}"
echo "-----------------------------------"

# Create directories
mkdir -p knowledge-graph/{indexer,mcp-server,data}
mkdir -p .opencode/commands
mkdir -p openspec

echo "✓ Project structure created"
echo ""

echo "${GREEN}=================================="
echo "✓ Setup Complete!"
echo "==================================${NC}"
echo ""
echo "Next Steps:"
echo "1. Index your documentation:"
echo "   source venv/bin/activate"
echo "   python knowledge-graph/indexer/graph_indexer.py ."
echo ""
echo "2. Start the MCP server:"
echo "   python knowledge-graph/mcp-server/mcp_server.py &"
echo ""
echo "3. Initialize OpenSpec:"
echo "   openspec init"
echo ""
echo "4. Configure OpenCode:"
echo "   Edit ~/.config/opencode/opencode.json with the provided template"
echo ""
echo "5. Start using OpenCode:"
echo "   opencode"
echo ""
echo "Neo4j Browser: http://localhost:7474"
echo "Username: neo4j"
echo "Password: bsw-secure-password-2024"
echo ""
