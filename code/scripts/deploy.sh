#!/bin/bash
# Kubernetes deployment script for CAG+RAG system

set -e

echo "======================================"
echo "CAG+RAG Kubernetes Deployment"
echo "======================================"

# Colours
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

# Configuration
NAMESPACE=${NAMESPACE:-cag-rag}
IMAGE_REGISTRY=${IMAGE_REGISTRY:-localhost:5000}
IMAGE_TAG=${IMAGE_TAG:-latest}

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl."
    exit 1
fi

print_success "kubectl found"

# Check cluster connection
echo "Checking Kubernetes cluster connection..."
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

print_success "Connected to Kubernetes cluster"

# Create namespace
echo "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
print_success "Namespace ready"

# Build Docker images
echo "Building Docker images..."

echo "Building CAG service..."
docker build -t ${IMAGE_REGISTRY}/cag-service:${IMAGE_TAG} ./cag-service
print_success "CAG service image built"

echo "Building RAG service..."
docker build -t ${IMAGE_REGISTRY}/rag-service:${IMAGE_TAG} ./rag-service
print_success "RAG service image built"

echo "Building MCP server..."
docker build -t ${IMAGE_REGISTRY}/mcp-server:${IMAGE_TAG} ./mcp-server
print_success "MCP server image built"

# Push images (if not local registry)
if [ "$IMAGE_REGISTRY" != "localhost:5000" ]; then
    echo "Pushing images to registry..."
    docker push ${IMAGE_REGISTRY}/cag-service:${IMAGE_TAG}
    docker push ${IMAGE_REGISTRY}/rag-service:${IMAGE_TAG}
    docker push ${IMAGE_REGISTRY}/mcp-server:${IMAGE_TAG}
    print_success "Images pushed to registry"
fi

# Deploy infrastructure components
echo "Deploying infrastructure components..."

# PostgreSQL
echo "Deploying PostgreSQL..."
kubectl apply -f ../deployment/postgresql.yaml -n $NAMESPACE
print_success "PostgreSQL deployed"

# Redis
echo "Deploying Redis..."
kubectl apply -f ../deployment/redis.yaml -n $NAMESPACE
print_success "Redis deployed"

# Neo4j
echo "Deploying Neo4j..."
kubectl apply -f ../deployment/neo4j.yaml -n $NAMESPACE
print_success "Neo4j deployed"

# MongoDB
echo "Deploying MongoDB..."
kubectl apply -f ../deployment/mongodb.yaml -n $NAMESPACE
print_success "MongoDB deployed"

# Kafka (using Strimzi operator)
echo "Deploying Kafka..."
kubectl apply -f ../deployment/kafka.yaml -n $NAMESPACE
print_success "Kafka deployed"

# Wait for infrastructure to be ready
echo "Waiting for infrastructure to be ready (this may take a few minutes)..."
kubectl wait --for=condition=ready pod -l app=postgresql -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=neo4j -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=mongodb -n $NAMESPACE --timeout=300s
print_success "Infrastructure ready"

# Deploy application services
echo "Deploying application services..."

# CAG Service
echo "Deploying CAG service..."
kubectl apply -f ../deployment/cag-service.yaml -n $NAMESPACE
print_success "CAG service deployed"

# RAG Service
echo "Deploying RAG service..."
kubectl apply -f ../deployment/rag-service.yaml -n $NAMESPACE
print_success "RAG service deployed"

# MCP Server
echo "Deploying MCP server..."
kubectl apply -f ../deployment/mcp-server.yaml -n $NAMESPACE
print_success "MCP server deployed"

# Wait for application services
echo "Waiting for services to be ready..."
kubectl wait --for=condition=ready pod -l app=cag-service -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=rag-service -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=mcp-server -n $NAMESPACE --timeout=300s
print_success "All services ready"

# Get service endpoints
echo ""
echo "======================================"
print_success "Deployment Complete!"
echo "======================================"
echo ""
echo "Service endpoints:"
echo "- MCP Server: http://$(kubectl get svc mcp-server -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):8000"
echo "- CAG Service: http://$(kubectl get svc cag-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):8001"
echo "- RAG Service: http://$(kubectl get svc rag-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):8002"
echo ""
echo "To check status:"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/mcp-server -n $NAMESPACE"
echo "  kubectl logs -f deployment/cag-service -n $NAMESPACE"
echo "  kubectl logs -f deployment/rag-service -n $NAMESPACE"
echo ""
echo "To access services locally:"
echo "  kubectl port-forward svc/mcp-server 8000:8000 -n $NAMESPACE"
echo ""
