#!/bin/bash
# Stop locally running CAG+RAG services

set -e

echo "======================================"
echo "Stopping CAG+RAG Local Services"
echo "======================================"

# Colours
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Function to stop a service
stop_service() {
    local name=$1
    local port=$2
    local pid_file="logs/${name}.pid"

    echo "Stopping $name..."

    # Try to stop via PID file
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid 2>/dev/null
            sleep 2

            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null
            fi

            print_success "$name stopped (PID: $pid)"
        else
            print_warning "$name not running (stale PID file)"
        fi
        rm "$pid_file"
    fi

    # Kill any process on the port
    local port_pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$port_pid" ]; then
        kill -9 $port_pid 2>/dev/null
        print_success "Killed process on port $port"
    fi
}

# Stop all services
stop_service "mcp-server" 8000
stop_service "cag-service" 8001
stop_service "rag-service" 8002

echo ""
print_success "All services stopped"
echo ""
