#!/bin/bash
# Setup script for CAG+RAG system
# Prepares environment and downloads models

set -e

echo "======================================"
echo "CAG+RAG System Setup"
echo "======================================"

# Colours for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Colour

# Function to print coloured messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_success "Python version $PYTHON_VERSION meets requirements (>= $REQUIRED_VERSION)"
else
    print_error "Python version $PYTHON_VERSION is too old. Required: >= $REQUIRED_VERSION"
    exit 1
fi

# Check available disk space (need ~20GB for models)
echo "Checking disk space..."
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
REQUIRED_SPACE=20

if [ "$AVAILABLE_SPACE" -ge "$REQUIRED_SPACE" ]; then
    print_success "Sufficient disk space: ${AVAILABLE_SPACE}GB available"
else
    print_warning "Low disk space: ${AVAILABLE_SPACE}GB available (recommended: ${REQUIRED_SPACE}GB)"
fi

# Check available RAM
echo "Checking available RAM..."
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -ge 32 ]; then
    print_success "Sufficient RAM: ${TOTAL_RAM}GB"
elif [ "$TOTAL_RAM" -ge 16 ]; then
    print_warning "RAM: ${TOTAL_RAM}GB (recommended: 32GB+)"
else
    print_error "Insufficient RAM: ${TOTAL_RAM}GB (minimum: 16GB)"
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p models data/vector_store data/documents logs
print_success "Directories created"

# Install CAG service dependencies
echo "Installing CAG service dependencies..."
cd cag-service
pip install --no-cache-dir -r requirements.txt
print_success "CAG dependencies installed"
cd ..

# Install RAG service dependencies
echo "Installing RAG service dependencies..."
cd rag-service
pip install --no-cache-dir -r requirements.txt
print_success "RAG dependencies installed"
cd ..

# Install MCP server dependencies
echo "Installing MCP server dependencies..."
cd mcp-server
pip install --no-cache-dir -r requirements.txt
print_success "MCP dependencies installed"
cd ..

# Download embedding model
echo "Downloading embedding model (sentence-transformers/all-MiniLM-L6-v2)..."
python3 << EOF
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.save('./models/embeddings')
print("Embedding model downloaded successfully")
EOF
print_success "Embedding model downloaded"

# Download Llama model (optional, requires HuggingFace token)
echo "Downloading Llama-2-7B model..."
if [ -n "$HF_TOKEN" ]; then
    python3 << EOF
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

print("Downloading Llama-2-7B with 4-bit quantization...")
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-chat-hf')
tokenizer.save_pretrained('./models/llama')

print("Llama tokenizer downloaded. Full model will be loaded on first run.")
EOF
    print_success "Llama model prepared"
else
    print_warning "HF_TOKEN not set. Llama model will be downloaded on first run."
    print_warning "To download now: export HF_TOKEN=<your_token> and re-run"
fi

# Create .env file template
echo "Creating .env template..."
cat > .env.template << 'EOF'
# Environment
ENVIRONMENT=development

# Database connections
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cag_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=changeme

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=rag_db

# Kafka
KAFKA_BROKERS=localhost:9092

# Models
MODEL_CACHE_DIR=./models
VECTOR_STORE_PATH=./data/vector_store

# HuggingFace (for Llama model access)
HF_TOKEN=your_huggingface_token_here
EOF

if [ ! -f .env ]; then
    cp .env.template .env
    print_success ".env file created from template"
else
    print_warning ".env file already exists, not overwriting"
fi

# Setup complete
echo ""
echo "======================================"
print_success "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start infrastructure: ./scripts/start_infrastructure.sh"
echo "3. Run services: ./scripts/run_local.sh"
echo "4. Or deploy to Kubernetes: ./scripts/deploy.sh"
echo ""
