#!/bin/bash
# Test script for CAG+RAG system
# Runs integration tests to verify system functionality

set -e

echo "======================================"
echo "CAG+RAG System Tests"
echo "======================================"

# Colours
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

# Configuration
MCP_URL=${MCP_URL:-http://localhost:8000}
CAG_URL=${CAG_URL:-http://localhost:8001}
RAG_URL=${RAG_URL:-http://localhost:8002}

TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name=$1
    local url=$2
    local method=${3:-GET}
    local data=$4

    echo ""
    print_info "Running: $test_name"

    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null || echo "000")
    else
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null || echo "000")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        print_success "$test_name: PASSED (HTTP $http_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        print_error "$test_name: FAILED (HTTP $http_code)"
        echo "Response: $body"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo ""
echo "======================================"
echo "Health Check Tests"
echo "======================================"

run_test "MCP Server Health" "$MCP_URL/health"
run_test "CAG Service Health" "$CAG_URL/health"
run_test "RAG Service Health" "$RAG_URL/health"

echo ""
echo "======================================"
echo "Readiness Check Tests"
echo "======================================"

run_test "MCP Server Readiness" "$MCP_URL/ready" || true
run_test "CAG Service Readiness" "$CAG_URL/ready" || true
run_test "RAG Service Readiness" "$RAG_URL/ready" || true

echo ""
echo "======================================"
echo "Integration Tests"
echo "======================================"

# Test 1: Simple query through MCP
test_query_1='{
  "query": "What is CAG+RAG architecture?",
  "user_id": "test_user_1",
  "session_id": "test_session_1",
  "max_tokens": 256,
  "temperature": 0.7
}'

run_test "MCP Query Test (Basic)" "$MCP_URL/api/v1/query" "POST" "$test_query_1" || true

# Test 2: Domain-specific query
test_query_2='{
  "query": "How do I implement pipeline integration?",
  "user_id": "test_user_2",
  "session_id": "test_session_2",
  "domains": ["PIPE"],
  "max_tokens": 256
}'

run_test "MCP Query Test (Domain-Specific)" "$MCP_URL/api/v1/query" "POST" "$test_query_2" || true

# Test 3: CAG processing directly
test_cag='{
  "query": "Tell me about AXIS bots",
  "user_id": "test_user_3",
  "session_id": "test_session_3",
  "domains": ["AXIS"]
}'

run_test "CAG Processing Test" "$CAG_URL/api/v1/process" "POST" "$test_cag" || true

# Test 4: RAG retrieval (if vector store is populated)
test_rag='{
  "query": "CAG+RAG architecture",
  "top_k": 5
}'

run_test "RAG Retrieval Test" "$RAG_URL/api/v1/retrieve" "POST" "$test_rag" || true

echo ""
echo "======================================"
echo "Performance Tests"
echo "======================================"

# Measure response time
echo "Measuring MCP query latency..."
start_time=$(date +%s%3N)
curl -s -X POST "$MCP_URL/api/v1/query" \
    -H "Content-Type: application/json" \
    -d "$test_query_1" > /dev/null 2>&1 || true
end_time=$(date +%s%3N)
latency=$((end_time - start_time))

if [ $latency -lt 5000 ]; then
    print_success "Query latency: ${latency}ms (excellent)"
elif [ $latency -lt 10000 ]; then
    print_success "Query latency: ${latency}ms (good)"
else
    print_info "Query latency: ${latency}ms (acceptable)"
fi

echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
echo ""
print_success "Passed: $TESTS_PASSED"
if [ $TESTS_FAILED -gt 0 ]; then
    print_error "Failed: $TESTS_FAILED"
else
    print_success "Failed: $TESTS_FAILED"
fi
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
    echo "Success Rate: $SUCCESS_RATE%"
fi

echo ""
if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All tests passed! ✨"
    exit 0
else
    print_error "Some tests failed. Check logs for details."
    exit 1
fi
