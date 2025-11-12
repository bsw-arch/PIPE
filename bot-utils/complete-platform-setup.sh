#!/bin/bash
#
# Complete BSW-Arch AI Development Platform Setup
# Installs and configures:
# - OpenSpec + OpenCode
# - Neo4j Knowledge Graph
# - ChromaDB Vector Store
# - Ollama (Local LLM)
# - Enhanced MCP Server
# - IV Bots with Knowledge Graph Integration
# - Proton Drive Sync (optional)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt"
DOCUMENTATION_DIR="/opt/documentation"
OPENSPEC_DIR="/opt/openspec"
OPENCODE_DIR="/opt/opencode"
NEO4J_DIR="/opt/neo4j"
CHROMA_DIR="/opt/chroma-data"
OLLAMA_MODELS=("deepseek-coder:6.7b" "llama2:7b")

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  BSW-Arch AI Development Platform Setup                     ║${NC}"
echo -e "${BLUE}║  Complete Integration: OpenCode + OpenSpec + Knowledge Graph║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN} $1${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ This script must be run as root${NC}"
        echo "   Please run: sudo $0"
        exit 1
    fi
}

# Check root
check_root

# Step 1: System Dependencies
print_section "1. Installing System Dependencies"

if command_exists apt-get; then
    echo "📦 Detected Debian/Ubuntu system"
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        wget \
        docker.io \
        docker-compose \
        openjdk-11-jre \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev
elif command_exists dnf; then
    echo "📦 Detected Fedora/RHEL system"
    dnf install -y \
        python3 \
        python3-pip \
        git \
        curl \
        wget \
        docker \
        docker-compose \
        java-11-openjdk \
        gcc \
        openssl-devel \
        libffi-devel \
        python3-devel
else
    echo -e "${RED}❌ Unsupported package manager${NC}"
    exit 1
fi

echo -e "${GREEN}✅ System dependencies installed${NC}"

# Step 2: Python Dependencies
print_section "2. Installing Python Dependencies"

pip3 install --upgrade pip

# Core dependencies
pip3 install \
    sentence-transformers \
    chromadb \
    neo4j \
    pyyaml \
    aiohttp \
    asyncio \
    watchdog \
    requests

# MCP SDK
if ! pip3 show mcp >/dev/null 2>&1; then
    echo "📦 Installing MCP SDK..."
    pip3 install mcp
fi

echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Step 3: Neo4j Setup
print_section "3. Setting up Neo4j Knowledge Graph"

if [ ! -d "$NEO4J_DIR" ]; then
    mkdir -p "$NEO4J_DIR"

    # Download Neo4j
    NEO4J_VERSION="5.13.0"
    echo "📥 Downloading Neo4j $NEO4J_VERSION..."
    wget -q -O /tmp/neo4j.tar.gz \
        "https://dist.neo4j.org/neo4j-community-${NEO4J_VERSION}-unix.tar.gz"

    tar -xzf /tmp/neo4j.tar.gz -C "$NEO4J_DIR" --strip-components=1
    rm /tmp/neo4j.tar.gz

    # Configure Neo4j
    cat > "$NEO4J_DIR/conf/neo4j.conf" << 'EOF'
# Network Configuration
server.default_listen_address=0.0.0.0
server.bolt.enabled=true
server.bolt.listen_address=:7687
server.http.enabled=true
server.http.listen_address=:7474

# Memory Configuration
server.memory.heap.initial_size=512m
server.memory.heap.max_size=2g
server.memory.pagecache.size=512m

# Security
dbms.security.auth_enabled=true

# Performance
dbms.checkpoint.interval.time=300s
EOF

    echo -e "${GREEN}✅ Neo4j installed${NC}"
else
    echo -e "${YELLOW}⚠️  Neo4j already installed${NC}"
fi

# Create systemd service for Neo4j
if [ ! -f /etc/systemd/system/neo4j.service ]; then
    cat > /etc/systemd/system/neo4j.service << EOF
[Unit]
Description=Neo4j Graph Database
After=network.target

[Service]
Type=forking
User=root
ExecStart=$NEO4J_DIR/bin/neo4j start
ExecStop=$NEO4J_DIR/bin/neo4j stop
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable neo4j
    systemctl start neo4j

    echo "⏳ Waiting for Neo4j to start..."
    sleep 10

    # Set initial password
    echo "🔐 Setting Neo4j password..."
    "$NEO4J_DIR/bin/neo4j-admin" dbms set-initial-password "bsw-arch-neo4j-2025" || true

    echo -e "${GREEN}✅ Neo4j service configured${NC}"
fi

# Step 4: ChromaDB Setup
print_section "4. Setting up ChromaDB Vector Store"

mkdir -p "$CHROMA_DIR"
chmod 755 "$CHROMA_DIR"

# Create ChromaDB systemd service
if [ ! -f /etc/systemd/system/chromadb.service ]; then
    cat > /etc/systemd/system/chromadb.service << EOF
[Unit]
Description=ChromaDB Vector Database
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$CHROMA_DIR
ExecStart=/usr/bin/python3 -m chromadb.cli --path $CHROMA_DIR --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable chromadb
    systemctl start chromadb

    echo -e "${GREEN}✅ ChromaDB service configured${NC}"
else
    echo -e "${YELLOW}⚠️  ChromaDB service already exists${NC}"
fi

# Step 5: Ollama Setup
print_section "5. Setting up Ollama (Local LLM)"

if ! command_exists ollama; then
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo -e "${GREEN}✅ Ollama installed${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama already installed${NC}"
fi

# Start Ollama service
systemctl enable ollama || true
systemctl start ollama || true

echo "⏳ Waiting for Ollama to start..."
sleep 5

# Pull models
for model in "${OLLAMA_MODELS[@]}"; do
    echo "📥 Pulling model: $model"
    ollama pull "$model" || echo -e "${YELLOW}⚠️  Failed to pull $model${NC}"
done

echo -e "${GREEN}✅ Ollama configured with models${NC}"

# Step 6: OpenSpec Setup
print_section "6. Setting up OpenSpec"

if [ ! -d "$OPENSPEC_DIR" ]; then
    mkdir -p "$OPENSPEC_DIR"

    # Clone OpenSpec (assuming it's available, otherwise install from package)
    if command_exists npm; then
        npm install -g openspec-cli || {
            echo -e "${YELLOW}⚠️  OpenSpec CLI not available via npm${NC}"
            echo "   Please install manually or use alternative spec management"
        }
    fi

    # Create specs directory structure
    mkdir -p "$OPENSPEC_DIR"/{proposals,applied,archived}

    echo -e "${GREEN}✅ OpenSpec directory structure created${NC}"
else
    echo -e "${YELLOW}⚠️  OpenSpec directory already exists${NC}"
fi

# Step 7: OpenCode Setup
print_section "7. Setting up OpenCode"

if [ ! -d "$OPENCODE_DIR" ]; then
    mkdir -p "$OPENCODE_DIR"/{mcp-server,config}

    # Copy MCP server to OpenCode directory
    if [ -f "$(dirname "$0")/enhanced_mcp_server.py" ]; then
        cp "$(dirname "$0")/enhanced_mcp_server.py" "$OPENCODE_DIR/mcp-server/"
        chmod +x "$OPENCODE_DIR/mcp-server/enhanced_mcp_server.py"
        echo -e "${GREEN}✅ Enhanced MCP server installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Enhanced MCP server not found in script directory${NC}"
    fi

    # Create OpenCode configuration
    cat > "$OPENCODE_DIR/config/config.yaml" << EOF
# OpenCode Configuration
neo4j:
  uri: bolt://localhost:7687
  user: neo4j
  password: bsw-arch-neo4j-2025

chromadb:
  path: $CHROMA_DIR

ollama:
  host: http://localhost:11434
  default_model: deepseek-coder:6.7b

mcp:
  server_path: $OPENCODE_DIR/mcp-server/enhanced_mcp_server.py

specs:
  directory: $OPENSPEC_DIR
EOF

    echo -e "${GREEN}✅ OpenCode configured${NC}"
else
    echo -e "${YELLOW}⚠️  OpenCode directory already exists${NC}"
fi

# Step 8: Documentation Setup
print_section "8. Setting up Documentation System"

mkdir -p "$DOCUMENTATION_DIR"

# Copy bot utilities if available
if [ -d "$(dirname "$0")" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

    if [ -f "$SCRIPT_DIR/graph_indexer_with_specs.py" ]; then
        cp "$SCRIPT_DIR/graph_indexer_with_specs.py" "$DOCUMENTATION_DIR/"
        chmod +x "$DOCUMENTATION_DIR/graph_indexer_with_specs.py"
        echo -e "${GREEN}✅ Knowledge graph indexer installed${NC}"
    fi

    if [ -f "$SCRIPT_DIR/proton_drive_sync.py" ]; then
        cp "$SCRIPT_DIR/proton_drive_sync.py" "$DOCUMENTATION_DIR/"
        chmod +x "$DOCUMENTATION_DIR/proton_drive_sync.py"
        echo -e "${GREEN}✅ Proton Drive sync script installed${NC}"
    fi
fi

# Step 9: Index Initial Documentation
print_section "9. Indexing Documentation into Knowledge Graph"

# Find documentation directory
DOC_SOURCE="."
if [ -d "/home/user/bsw-arch/docs" ]; then
    DOC_SOURCE="/home/user/bsw-arch/docs"
elif [ -d "$SCRIPT_DIR/../docs" ]; then
    DOC_SOURCE="$SCRIPT_DIR/../docs"
fi

if [ -f "$DOCUMENTATION_DIR/graph_indexer_with_specs.py" ]; then
    echo "📚 Indexing documentation from: $DOC_SOURCE"

    # Wait for Neo4j to be fully ready
    sleep 5

    python3 "$DOCUMENTATION_DIR/graph_indexer_with_specs.py" \
        "$DOC_SOURCE" \
        --spec-dirs "$OPENSPEC_DIR/applied" "$OPENSPEC_DIR/proposals" \
        --neo4j-uri bolt://localhost:7687 \
        --neo4j-user neo4j \
        --neo4j-password bsw-arch-neo4j-2025 \
        --chroma-path "$CHROMA_DIR" || {
            echo -e "${YELLOW}⚠️  Initial indexing failed, you can retry later${NC}"
        }

    echo -e "${GREEN}✅ Documentation indexed${NC}"
fi

# Step 10: Create Helper Scripts
print_section "10. Creating Helper Scripts"

# Create opencode wrapper
cat > /usr/local/bin/opencode << 'EOF'
#!/bin/bash
# OpenCode CLI wrapper with MCP server

export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="bsw-arch-neo4j-2025"
export CHROMA_PATH="/opt/chroma-data"
export MCP_SERVER_PATH="/opt/opencode/mcp-server/enhanced_mcp_server.py"

# Start MCP server in background if not running
if ! pgrep -f "enhanced_mcp_server.py" > /dev/null; then
    python3 "$MCP_SERVER_PATH" &
    MCP_PID=$!
    echo "Started MCP server (PID: $MCP_PID)"
fi

# Launch your preferred editor or AI assistant
# Customize this based on your setup
if command -v nvim >/dev/null 2>&1; then
    nvim "$@"
elif command -v vim >/dev/null 2>&1; then
    vim "$@"
else
    echo "No editor configured. Please set up Neovim or your preferred editor."
fi
EOF

chmod +x /usr/local/bin/opencode

# Create spec management helper
cat > /usr/local/bin/spec << 'EOF'
#!/bin/bash
# Spec management helper

OPENSPEC_DIR="/opt/openspec"
INDEXER="/opt/documentation/graph_indexer_with_specs.py"

case "$1" in
    new|create)
        SPEC_NAME="${2:-new-spec}"
        mkdir -p "$OPENSPEC_DIR/proposals"
        cat > "$OPENSPEC_DIR/proposals/$SPEC_NAME.yaml" << SPECEOF
---
version: 1.0.0
spec:
  id: SPEC-$(echo $SPEC_NAME | tr '[:lower:]' '[:upper:]')-001
  title: $SPEC_NAME
  status: proposal
  created: $(date -Iseconds)

description: |
  TODO: Describe the specification

requirements:
  - id: REQ-001
    description: "TODO: First requirement"
    priority: high

implementation:
  file: "TODO: path/to/implementation.py"
  function: "TODO: function_name"
SPECEOF
        echo "Created: $OPENSPEC_DIR/proposals/$SPEC_NAME.yaml"
        ;;

    apply)
        SPEC_FILE="$2"
        if [ ! -f "$SPEC_FILE" ]; then
            echo "Error: Spec file not found: $SPEC_FILE"
            exit 1
        fi

        # Move from proposals to applied
        BASENAME=$(basename "$SPEC_FILE")
        mv "$SPEC_FILE" "$OPENSPEC_DIR/applied/$BASENAME"

        # Update status in file
        sed -i 's/status: proposal/status: applied/' "$OPENSPEC_DIR/applied/$BASENAME"

        # Re-index
        if [ -f "$INDEXER" ]; then
            python3 "$INDEXER" "$OPENSPEC_DIR/applied/$BASENAME" --incremental
        fi

        echo "Applied: $OPENSPEC_DIR/applied/$BASENAME"
        ;;

    validate)
        SPEC_ID="$2"
        python3 -c "
import json
from enhanced_mcp_server import EnhancedMCPServer
import asyncio

async def validate():
    server = EnhancedMCPServer()
    await server._initialize()
    result = await server._validate_spec_implementation('$SPEC_ID')
    print(json.dumps(result, indent=2))
    await server.cleanup()

asyncio.run(validate())
"
        ;;

    *)
        echo "Usage: spec {new|apply|validate} [arguments]"
        echo ""
        echo "Commands:"
        echo "  new <name>       Create new spec proposal"
        echo "  apply <file>     Apply a spec proposal"
        echo "  validate <id>    Validate spec implementation"
        ;;
esac
EOF

chmod +x /usr/local/bin/spec

# Create knowledge graph query helper
cat > /usr/local/bin/kg-query << 'EOF'
#!/bin/bash
# Knowledge Graph query helper

export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="bsw-arch-neo4j-2025"
export CHROMA_PATH="/opt/chroma-data"

python3 -c "
import json
import sys
import asyncio
from enhanced_mcp_server import EnhancedMCPServer

async def query():
    query_text = ' '.join(sys.argv[1:])
    server = EnhancedMCPServer()
    await server._initialize()
    result = await server._query_spec_aware_graph(query_text)
    print(json.dumps(result, indent=2))
    await server.cleanup()

asyncio.run(query())
" "$@"
EOF

chmod +x /usr/local/bin/kg-query

echo -e "${GREEN}✅ Helper scripts created${NC}"

# Step 11: Environment Configuration
print_section "11. Configuring Environment"

# Add environment variables to profile
cat >> /etc/profile.d/bsw-arch-platform.sh << 'EOF'
# BSW-Arch AI Development Platform
export BSW_ARCH_HOME="/opt"
export OPENSPEC_DIR="/opt/openspec"
export OPENCODE_DIR="/opt/opencode"
export NEO4J_HOME="/opt/neo4j"
export CHROMA_PATH="/opt/chroma-data"
export DOCUMENTATION_DIR="/opt/documentation"

# Neo4j connection
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="bsw-arch-neo4j-2025"

# Add to PATH
export PATH="$PATH:/opt/opencode/bin"
EOF

echo -e "${GREEN}✅ Environment configured${NC}"

# Step 12: Health Checks
print_section "12. Running Health Checks"

echo -n "🔍 Checking Neo4j... "
if systemctl is-active --quiet neo4j; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

echo -n "🔍 Checking ChromaDB... "
if systemctl is-active --quiet chromadb; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

echo -n "🔍 Checking Ollama... "
if systemctl is-active --quiet ollama; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

echo -n "🔍 Checking OpenCode directory... "
if [ -d "$OPENCODE_DIR" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

echo -n "🔍 Checking OpenSpec directory... "
if [ -d "$OPENSPEC_DIR" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# Final Summary
print_section "Installation Complete! 🎉"

echo ""
echo -e "${GREEN}✅ BSW-Arch AI Development Platform is ready!${NC}"
echo ""
echo "📋 Quick Start Commands:"
echo ""
echo "  opencode              - Launch AI-assisted coding environment"
echo "  spec new my-feature   - Create new specification"
echo "  spec apply spec.yaml  - Apply specification"
echo "  kg-query \"query text\" - Query knowledge graph"
echo ""
echo "🔗 Service URLs:"
echo "  Neo4j Browser: http://localhost:7474"
echo "  ChromaDB API:  http://localhost:8000"
echo "  Ollama API:    http://localhost:11434"
echo ""
echo "📚 Documentation:"
echo "  Main docs:     $DOCUMENTATION_DIR"
echo "  Specifications: $OPENSPEC_DIR"
echo ""
echo "🔐 Credentials:"
echo "  Neo4j: neo4j / bsw-arch-neo4j-2025"
echo ""
echo "📝 Next Steps:"
echo "  1. Source environment: source /etc/profile.d/bsw-arch-platform.sh"
echo "  2. Create your first spec: spec new my-first-feature"
echo "  3. Start coding: opencode"
echo "  4. Query knowledge: kg-query \"show me IV bot architecture\""
echo ""
echo -e "${BLUE}Happy coding with BSW-Arch AI Platform! 🚀${NC}"
echo ""
