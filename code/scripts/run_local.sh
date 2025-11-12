#!/bin/bash
# Run CAG+RAG services locally for development and testing

set -e

echo "======================================"
echo "CAG+RAG Local Development Server"
echo "======================================"

# Colours
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    print_success "Environment variables loaded from .env"
else
    print_warning ".env file not found. Using defaults."
fi

# Check if infrastructure is running
check_service() {
    local service=$1
    local host=$2
    local port=$3

    if nc -z $host $port 2>/dev/null; then
        print_success "$service is running at $host:$port"
        return 0
    else
        print_warning "$service is not running at $host:$port"
        return 1
    fi
}

echo ""
echo "Checking infrastructure services..."
check_service "PostgreSQL" "${POSTGRES_HOST:-localhost}" "${POSTGRES_PORT:-5432}" || \
    print_info "Start with: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=changeme postgres:15"

check_service "Redis" "${REDIS_HOST:-localhost}" "${REDIS_PORT:-6379}" || \
    print_info "Start with: docker run -d -p 6379:6379 redis:7-alpine"

check_service "Neo4j" "localhost" "7687" || \
    print_info "Start with: docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/changeme neo4j:5"

check_service "MongoDB" "localhost" "27017" || \
    print_info "Start with: docker run -d -p 27017:27017 mongo:7"

check_service "Kafka" "localhost" "9092" || \
    print_info "Start Kafka with: docker-compose -f docker-compose.infra.yml up -d"

echo ""
print_info "If infrastructure services are not running, start them first."
print_info "Or use: ./scripts/start_infrastructure.sh"
echo ""

# Function to start a service in background
start_service() {
    local name=$1
    local dir=$2
    local port=$3
    local log_file="logs/${name}.log"

    mkdir -p logs

    echo "Starting $name on port $port..."
    cd $dir

    # Kill existing process on port if any
    lsof -ti:$port | xargs kill -9 2>/dev/null || true

    # Start service
    PORT=$port python3 -m uvicorn src.main:app --host 0.0.0.0 --port $port --reload > "../$log_file" 2>&1 &

    local pid=$!
    echo $pid > "../logs/${name}.pid"

    cd ..

    # Wait for service to start
    for i in {1..30}; do
        if nc -z localhost $port 2>/dev/null; then
            print_success "$name started (PID: $pid, Port: $port)"
            return 0
        fi
        sleep 1
    done

    print_error "$name failed to start. Check logs: $log_file"
    return 1
}

# Start services
echo "Starting CAG+RAG services..."
echo ""

start_service "cag-service" "cag-service" 8001
sleep 2

start_service "rag-service" "rag-service" 8002
sleep 2

start_service "mcp-server" "mcp-server" 8000

echo ""
echo "======================================"
print_success "All services started!"
echo "======================================"
echo ""
echo "Service URLs:"
echo "  - MCP Server:  http://localhost:8000"
echo "  - CAG Service: http://localhost:8001"
echo "  - RAG Service: http://localhost:8002"
echo ""
echo "API Documentation:"
echo "  - MCP Docs:  http://localhost:8000/docs"
echo "  - CAG Docs:  http://localhost:8001/docs"
echo "  - RAG Docs:  http://localhost:8002/docs"
echo ""
echo "Health Checks:"
echo "  - MCP:  curl http://localhost:8000/health"
echo "  - CAG:  curl http://localhost:8001/health"
echo "  - RAG:  curl http://localhost:8002/health"
echo ""
echo "Logs:"
echo "  - MCP:  tail -f logs/mcp-server.log"
echo "  - CAG:  tail -f logs/cag-service.log"
echo "  - RAG:  tail -f logs/rag-service.log"
echo ""
echo "To stop all services:"
echo "  ./scripts/stop_local.sh"
echo ""
echo "Test query:"
cat << 'EOF'
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I implement CAG+RAG architecture?",
    "user_id": "user_123",
    "session_id": "sess_456",
    "domains": ["PIPE", "AXIS"]
  }'
EOF
echo ""
