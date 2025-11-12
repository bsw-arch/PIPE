# ECO Bots - Infrastructure and Operations

> Ecological Domain: 48 specialized bots for infrastructure, monitoring, and resource optimization

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Domain**: ECO (Ecological)
**Bot Count**: 48

## Overview

The ECO (Ecological) domain manages infrastructure provisioning, resource optimization, monitoring, and operational efficiency for the BSW-Arch bot factory. This domain ensures efficient operations across all 185 bots while maintaining FAGAM compliance and container efficiency targets (<50MB per container).

## Quick Start

### 1. Clone Documentation

```bash
# Clone documentation repository
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation

# Verify structure
ls /opt/documentation/docs
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r eco-bots/examples/requirements.txt

# Or individual packages
pip install pyyaml requests prometheus-client psutil kubernetes
```

### 3. Run Example Bot

```bash
# Set environment
export DOCS_PATH="/opt/documentation/docs"
export BOT_DOMAIN="ECO"
export METRICS_PORT="8000"

# Run monitoring bot
python3 eco-bots/examples/eco_monitoring_bot.py
```

### 4. Build Container

```bash
# Using Dockerfile
cd eco-bots/examples
docker build -f Dockerfile.eco-monitoring-bot -t eco-monitoring-bot:1.0.0 .

# Verify size (should be <50MB)
docker images eco-monitoring-bot:1.0.0
```

### 5. Deploy to Kubernetes

```bash
# Create namespace and setup
kubectl apply -f docs/templates/deployment/eco/eco-namespace-setup.yaml

# Deploy monitoring bot
kubectl apply -f docs/templates/deployment/eco/eco-monitoring-bot.yaml

# Check status
kubectl get pods -n eco-bots
```

## Directory Structure

```
eco-bots/
├── infrastructure/       # Infrastructure templates
├── monitoring/          # Monitoring configurations
├── examples/            # Example bot implementations
│   ├── eco_monitoring_bot.py
│   ├── Dockerfile.eco-monitoring-bot
│   └── requirements.txt
├── configs/             # Configuration files
│   └── eco-bot-list.yaml
└── README.md

docs/
├── architecture/
│   └── domains/
│       └── ECO/
│           └── ECO-DOMAIN-ARCHITECTURE.md
├── specifications/
│   ├── containers/
│   │   └── eco/
│   │       ├── eco-base.yaml
│   │       ├── eco-monitoring-bot.yaml
│   │       └── eco-infra-bot.yaml
│   └── infrastructure/
│       └── eco/
│           ├── opentofu-base.tf
│           └── monitoring-stack.tf
└── templates/
    └── deployment/
        └── eco/
            ├── eco-monitoring-bot.yaml
            └── eco-namespace-setup.yaml
```

## ECO Bot Categories (48 Total)

### Infrastructure Management (8 bots)
- `eco-infra-bot`: Infrastructure provisioning
- `eco-provision-bot`: Resource provisioning automation
- `eco-config-bot`: Configuration management
- `eco-terraform-bot`: OpenTofu operations (NOT Terraform)
- `eco-iacode-bot`: Infrastructure as Code
- `eco-cluster-bot`: Cluster management
- `eco-node-bot`: Node management
- `eco-namespace-bot`: Namespace management

### Resource Optimization (8 bots)
- `eco-resource-bot`: Resource allocation
- `eco-scaler-bot`: Auto-scaling
- `eco-optimize-bot`: Performance optimization
- `eco-efficiency-bot`: Efficiency analysis
- `eco-cost-bot`: Cost optimization
- `eco-capacity-bot`: Capacity planning
- `eco-quota-bot`: Quota management
- `eco-limit-bot`: Limit enforcement

### Monitoring & Observability (8 bots)
- `eco-monitoring-bot`: System monitoring
- `eco-metrics-bot`: Metrics collection
- `eco-log-bot`: Log aggregation
- `eco-alert-bot`: Alerting
- `eco-healthcheck-bot`: Health checks
- `eco-status-bot`: Status dashboard
- `eco-trace-bot`: Distributed tracing
- `eco-dashboard-bot`: Dashboard management

### Container & Registry (6 bots)
- `eco-container-bot`: Container lifecycle
- `eco-registry-bot`: Registry operations
- `eco-image-bot`: Image optimization
- `eco-cache-bot`: Build cache
- `eco-build-bot`: Container builds
- `eco-scan-bot`: Security scanning

### Storage & Data (6 bots)
- `eco-storage-bot`: Storage management
- `eco-backup-bot`: Backup automation
- `eco-restore-bot`: Recovery operations
- `eco-archive-bot`: Data archiving
- `eco-snapshot-bot`: Snapshot management
- `eco-volume-bot`: Volume management

### Network & Connectivity (5 bots)
- `eco-network-bot`: Network configuration
- `eco-gateway-bot`: API gateway
- `eco-loadbalancer-bot`: Load balancing
- `eco-dns-bot`: DNS management
- `eco-ingress-bot`: Ingress management

### Security & Compliance (4 bots)
- `eco-security-bot`: Security hardening
- `eco-secrets-bot`: Secrets management (OpenBao)
- `eco-compliance-bot`: Compliance checking
- `eco-firewall-bot`: Firewall management

### Maintenance & Cleanup (3 bots)
- `eco-cleanup-bot`: Resource cleanup
- `eco-maintenance-bot`: Scheduled maintenance
- `eco-upgrade-bot`: System upgrades
- `eco-patch-bot`: Security patching

## Key Requirements

### FAGAM Prohibition

**STRICTLY PROHIBITED**:
- ❌ AWS proprietary services
- ❌ Google Cloud Platform
- ❌ Microsoft Azure
- ❌ HashiCorp Terraform → Use OpenTofu
- ❌ HashiCorp Vault → Use OpenBao

**ALLOWED**:
- ✅ Open source infrastructure tools
- ✅ CNCF projects (Kubernetes, Prometheus)
- ✅ Linux Foundation projects
- ✅ Self-hosted solutions

### Container Efficiency

**Target**: <50MB per container

**Strategy**:
- Chainguard Wolfi base images (~15MB)
- apko for declarative builds
- Multi-stage builds
- Minimal dependencies

### Resource Limits

**Small Bot**:
```yaml
requests:
  cpu: 100m
  memory: 128Mi
limits:
  cpu: 200m
  memory: 256Mi
```

**Medium Bot**:
```yaml
requests:
  cpu: 250m
  memory: 256Mi
limits:
  cpu: 500m
  memory: 512Mi
```

**Large Bot**:
```yaml
requests:
  cpu: 500m
  memory: 512Mi
limits:
  cpu: 1
  memory: 1Gi
```

## Building Containers

### Using apko (Recommended)

```bash
# Build with apko
apko build docs/specifications/containers/eco/eco-monitoring-bot.yaml \
  eco-monitoring-bot:1.0.0 \
  eco-monitoring-bot.tar

# Load into Docker
docker load < eco-monitoring-bot.tar

# Verify size
docker images | grep eco-monitoring-bot
```

### Using Dockerfile

```bash
# Build
docker build \
  -f eco-bots/examples/Dockerfile.eco-monitoring-bot \
  -t eco-monitoring-bot:1.0.0 \
  .

# Run locally
docker run -p 8000:8000 eco-monitoring-bot:1.0.0
```

### Multi-architecture Builds

```bash
# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f eco-bots/examples/Dockerfile.eco-monitoring-bot \
  -t eco-monitoring-bot:1.0.0 \
  --push \
  .
```

## Infrastructure Provisioning

### Using OpenTofu (NOT Terraform)

```bash
# Initialize
cd docs/specifications/infrastructure/eco
tofu init

# Plan
tofu plan -var="namespace=eco-bots" -var="resource_tier=medium"

# Apply
tofu apply -var="namespace=eco-bots" -var="resource_tier=medium"

# Verify
kubectl get namespace eco-bots
kubectl get resourcequota -n eco-bots
```

### Deploy Monitoring Stack

```bash
# Deploy Prometheus, Grafana, Loki
tofu apply -target=kubernetes_namespace.monitoring
tofu apply -target=kubernetes_deployment.prometheus
tofu apply -target=kubernetes_deployment.grafana

# Access Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Open http://localhost:3000
# Default credentials: admin/admin
```

## Monitoring Configuration

### Prometheus Metrics

ECO bots expose metrics on port 8000:

```python
# In your bot code
from prometheus_client import start_http_server, Gauge, Counter

# Start metrics server
start_http_server(8000)

# Define metrics
cpu_gauge = Gauge('bot_cpu_usage_percent', 'CPU usage', ['bot_name'])
memory_gauge = Gauge('bot_memory_usage_bytes', 'Memory usage', ['bot_name'])
error_counter = Counter('bot_errors_total', 'Errors', ['bot_name', 'type'])

# Update metrics
cpu_gauge.labels(bot_name='eco-monitoring-bot').set(45.2)
memory_gauge.labels(bot_name='eco-monitoring-bot').set(256 * 1024 * 1024)
```

### Grafana Dashboards

Access Grafana:
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

Import dashboard from:
- `eco-bots/monitoring/grafana-dashboard.json` (TODO)

### Alert Rules

Alerts are configured in `monitoring-stack.tf`:
- High CPU (>80% for 5 min)
- High Memory (>90% for 5 min)
- Pod restarts (>3 in 10 min)
- Container size (>50MB)
- High error rate (>5%)

## Python API Usage

### DocScanner

```python
from doc_scanner import DocScanner

# Initialize
scanner = DocScanner("/opt/documentation")

# Get ECO documents
eco_docs = scanner.get_documents_by_domain("ECO")
print(f"Found {len(eco_docs)} ECO documents")

# Get infrastructure docs
infra_docs = scanner.get_documents_by_category("infrastructure")

# Read specific document
content = scanner.read_document("eco-domain-architecture")
```

### GitHub API Client

```python
from github_api_client import GitHubDocsClient

# Initialize
client = GitHubDocsClient(token="your_github_token")

# Get metadata
metadata = client.get_metadata()
print(f"Version: {metadata['repository']['version']}")

# Get document
doc = client.get_document("docs/architecture/domains/ECO/ECO-DOMAIN-ARCHITECTURE.md")
```

## Deployment Workflows

### Workflow 1: New Bot Deployment

```bash
# 1. Create bot code
cat > my_eco_bot.py << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, "/opt/documentation/bot-utils")
from doc_scanner import DocScanner

scanner = DocScanner("/opt/documentation")
eco_docs = scanner.get_documents_by_domain("ECO")
print(f"Loaded {len(eco_docs)} ECO docs")
EOF

# 2. Create Dockerfile
cat > Dockerfile << 'EOF'
FROM cgr.dev/chainguard/wolfi-base:latest
RUN apk add git python-3.11 py3-pip
WORKDIR /opt
RUN git clone https://github.com/bsw-arch/bsw-arch.git documentation
COPY my_eco_bot.py /app/
WORKDIR /app
USER 65532
CMD ["python3", "my_eco_bot.py"]
EOF

# 3. Build
docker build -t my-eco-bot:1.0.0 .

# 4. Deploy
kubectl create deployment my-eco-bot \
  --image=my-eco-bot:1.0.0 \
  --namespace=eco-bots

# 5. Expose metrics
kubectl expose deployment my-eco-bot \
  --port=8000 \
  --namespace=eco-bots
```

### Workflow 2: Infrastructure Update

```bash
# 1. Update OpenTofu config
cd docs/specifications/infrastructure/eco

# 2. Plan changes
tofu plan -out=tfplan

# 3. Review
tofu show tfplan

# 4. Apply
tofu apply tfplan

# 5. Verify
kubectl get all -n eco-bots
```

## Troubleshooting

### Problem: Container exceeds 50MB

```bash
# Check image size
docker images my-bot

# Analyze layers
docker history my-bot:1.0.0

# Solutions:
# 1. Use Wolfi base (15MB)
# 2. Multi-stage build
# 3. Remove build dependencies
# 4. Use apko instead of Dockerfile
```

### Problem: High memory usage

```bash
# Check pod metrics
kubectl top pod -n eco-bots

# Check memory limits
kubectl describe pod my-bot -n eco-bots | grep -A 5 Limits

# Solutions:
# 1. Increase memory limits
# 2. Check for memory leaks
# 3. Optimize code
# 4. Use memory profiling
```

### Problem: Prometheus not scraping

```bash
# Check service annotations
kubectl get svc my-bot -n eco-bots -o yaml | grep prometheus

# Verify metrics endpoint
kubectl port-forward -n eco-bots pod/my-bot 8000:8000
curl http://localhost:8000/metrics

# Check Prometheus targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090/targets
```

### Problem: FAGAM violation detected

```bash
# Check for prohibited dependencies
grep -r "terraform\|vault\|aws-sdk\|google-cloud\|azure" .

# Replace with alternatives:
# terraform → opentofu
# vault → openbao
# AWS SDK → Direct API calls or open source alternatives
```

## Resource Optimization

### Right-Sizing

```bash
# Monitor actual usage
kubectl top pod -n eco-bots --containers

# Adjust resources based on usage
kubectl set resources deployment/my-bot \
  --limits=cpu=200m,memory=256Mi \
  --requests=cpu=100m,memory=128Mi \
  -n eco-bots
```

### Auto-Scaling

```bash
# Create HPA
kubectl autoscale deployment my-bot \
  --cpu-percent=80 \
  --min=1 \
  --max=5 \
  -n eco-bots

# Check HPA
kubectl get hpa -n eco-bots
```

## References

- [ECO Domain Architecture](../docs/architecture/domains/ECO/ECO-DOMAIN-ARCHITECTURE.md)
- [Container Specifications](../docs/specifications/containers/eco/)
- [Infrastructure Templates](../docs/specifications/infrastructure/eco/)
- [Deployment Templates](../docs/templates/deployment/eco/)
- [Comprehensive Bot Factory Architecture](../docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md)

## Support

### Documentation
- Architecture: `docs/architecture/domains/ECO/`
- Specifications: `docs/specifications/`
- Templates: `docs/templates/deployment/eco/`

### External Resources
- Chainguard Wolfi: https://github.com/wolfi-dev
- apko: https://github.com/chainguard-dev/apko
- OpenTofu: https://opentofu.org
- OpenBao: https://openbao.org
- Prometheus: https://prometheus.io

### Issues
- GitHub: https://github.com/bsw-arch/bsw-arch/issues
- Codeberg: https://codeberg.org/ECO-Bots

---

**Maintained by**: BSW-Tech Architecture Team
**Domain**: ECO (Ecological)
**Bot Count**: 48 specialized infrastructure and operations bots
**Last Updated**: 2025-11-10
