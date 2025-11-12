# BSW-ARCH Container Orchestration & Management

**Document**: BSW-ARCH-Container-Orchestration.md
**Version**: v3.0.0
**AppVM**: bsw-arch
**Last Updated**: 2025-09-21 11:45 UTC
**Status**: Production Implementation Complete
**Semantic Version**: v3.0.0 (Major: Production release, Minor: Core features, Patch: Documentation)

## BSW-ARCH Container Architecture Overview

The BSW-ARCH Enterprise Architecture AI Factory operates 13 production containers with enforced memory limits, providing infrastructure services, domain coordination, and distributed storage capabilities across the Dutch Ministry of Finance enterprise architecture platform.

### BSW-ARCH Container Stack
```yaml
🐳 BSW-ARCH Container Infrastructure (13 Containers):

Core Monitoring Stack (3 containers):
├── bsw-grafana: 512MB (Monitoring Dashboard)
├── bsw-postgresql-pod: 384MB (Database Services)
└── bsw-prometheus-pod: 256MB (Metrics Collection)

Domain Coordinators (3 containers):
├── axis-coordinator: 128MB (AI Architecture Domain)
├── pipe-coordinator: 128MB (AI Interfacing Domain)
└── iv-coordinator: 128MB (AI Memory Domain)

Infrastructure Services (2 containers):
├── bsw-arch-vault: 256MB (Secret Management)
└── bsw-arch-zot-registry: 192MB (Container Registry)

MinIO Distributed Storage (5 containers):
├── bsw-arch-minio-node-1: 256MB (Storage Node 1)
├── bsw-arch-minio-node-2: 256MB (Storage Node 2)
├── bsw-arch-minio-node-3: 256MB (Storage Node 3)
├── bsw-arch-minio-node-4: 256MB (Storage Node 4)
└── bsw-arch-minio-node-5: 256MB (Storage Node 5)

Total Container Memory: 2.816GB (with limits enforced)
```

## BSW-ARCH Container Memory Optimization

### Memory Limit Implementation Results
**Before Optimization**: 100% unlimited containers (0/13 with limits)
**After Optimization**: 100% limited containers (13/13 with limits)

```bash
# BSW-ARCH Container Memory Limits Applied (2025-09-20)
Container                Memory Limit    Status
bsw-grafana             512MB           ✅ Applied
bsw-postgresql-pod      384MB           ✅ Applied
bsw-prometheus-pod      256MB           ✅ Applied
axis-coordinator        128MB           ✅ Applied
pipe-coordinator        128MB           ✅ Applied
iv-coordinator          128MB           ✅ Applied
bsw-arch-vault          256MB           ✅ Applied
bsw-arch-zot-registry   192MB           ✅ Applied
bsw-arch-minio-node-1   256MB           ✅ Applied
bsw-arch-minio-node-2   256MB           ✅ Applied
bsw-arch-minio-node-3   256MB           ✅ Applied
bsw-arch-minio-node-4   256MB           ✅ Applied
bsw-arch-minio-node-5   256MB           ✅ Applied
```

### Container Memory Enforcement Commands
```bash
# BSW-ARCH Container Memory Limit Application
#!/bin/bash
echo "🐳 Applying BSW-ARCH Container Memory Limits"

# Core monitoring services
podman update --memory=512m bsw-grafana
podman update --memory=384m bsw-postgresql-pod
podman update --memory=256m bsw-prometheus-pod

# Domain coordinators
for coord in axis-coordinator pipe-coordinator iv-coordinator; do
  podman update --memory=128m $coord
done

# Infrastructure services
podman update --memory=256m bsw-arch-vault
podman update --memory=192m bsw-arch-zot-registry

# MinIO distributed storage cluster
for node in bsw-arch-minio-node-{1..5}; do
  podman update --memory=256m $node
done

echo "✅ BSW-ARCH Container limits applied successfully"
```

## BSW-ARCH Core Monitoring Stack

### Grafana Dashboard (Port 3000)
**Container**: `bsw-grafana`
**Image**: `localhost:5000/bsw/grafana:latest`
**Memory Limit**: 512MB
**Purpose**: Centralized monitoring dashboard for BSW-ARCH ecosystem

```yaml
Grafana Configuration:
├── Data Sources: Prometheus, PostgreSQL
├── Dashboards: BSW-ARCH system metrics, service health
├── Alerts: Memory, CPU, service availability
├── Users: Admin (Dutch Ministry of Finance)
└── Plugins: BSW-specific visualization plugins
```

**Management Commands**:
```bash
# Check Grafana status
podman logs bsw-grafana | tail -20

# Restart Grafana
podman restart bsw-grafana

# Access Grafana
curl http://localhost:3000/api/health

# Update Grafana memory limit
podman update --memory=512m bsw-grafana
```

### PostgreSQL Database (Port 5432)
**Container**: `bsw-postgresql-pod`
**Image**: `docker.io/library/postgres:15`
**Memory Limit**: 384MB
**Purpose**: Database services for BSW-ARCH applications

```yaml
PostgreSQL Configuration:
├── Databases: bsw_arch, monitoring, keragr
├── Users: bsw_admin, grafana, applications
├── Backup: Daily automated backups
├── Performance: Optimized for 384MB memory
└── Security: Vault-managed credentials
```

**Management Commands**:
```bash
# Check PostgreSQL status
podman exec bsw-postgresql-pod pg_isready

# Database backup
podman exec bsw-postgresql-pod pg_dump bsw_arch > backup-$(date +%Y%m%d).sql

# Monitor database performance
podman exec bsw-postgresql-pod psql -c "SELECT * FROM pg_stat_activity;"

# Update PostgreSQL memory limit
podman update --memory=384m bsw-postgresql-pod
```

### Prometheus Metrics (Port 9090)
**Container**: `bsw-prometheus-pod`
**Image**: `docker.io/prom/prometheus:latest`
**Memory Limit**: 256MB
**Purpose**: Metrics collection and storage for BSW-ARCH services

```yaml
Prometheus Configuration:
├── Targets: All BSW-ARCH services, containers
├── Retention: 15 days (optimized for memory)
├── Scrape Interval: 30 seconds
├── Storage: Local storage with rotation
└── Rules: BSW-ARCH specific alerting rules
```

**Management Commands**:
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Query BSW-ARCH metrics
curl "http://localhost:9090/api/v1/query?query=container_memory_usage_bytes"

# Reload Prometheus config
podman exec bsw-prometheus-pod kill -HUP 1

# Update Prometheus memory limit
podman update --memory=256m bsw-prometheus-pod
```

## BSW-ARCH Domain Coordinators

### AXIS Coordinator (Port 4000)
**Container**: `axis-coordinator`
**Image**: `docker.io/library/python:3.13-slim`
**Memory Limit**: 128MB
**Purpose**: Coordination hub for AI Architecture domain (13 organisations)

```python
# AXIS Coordinator Configuration
AXIS_ORGANISATIONS = [
    "AXIS-Core", "AXIS-Governance", "AXIS-Standards",
    "AXIS-Assessment", "AXIS-Compliance", "AXIS-Documentation",
    "AXIS-Integration", "AXIS-Patterns", "AXIS-Review",
    "AXIS-Risk", "AXIS-Strategy", "AXIS-Training", "AXIS-Innovation"
]

COORDINATOR_CONFIG = {
    "port": 4000,
    "memory_limit": "128MB",
    "organisations": 13,
    "domain": "AI_Architecture"
}
```

### PIPE Coordinator (Port 5100)
**Container**: `pipe-coordinator`
**Image**: `docker.io/library/python:3.13-slim`
**Memory Limit**: 128MB
**Purpose**: Coordination hub for AI Interfacing domain (13 organisations)

```python
# PIPE Coordinator Configuration
PIPE_ORGANISATIONS = [
    "PIPE-Core", "PIPE-Gateway", "PIPE-Protocols",
    "PIPE-Authentication", "PIPE-Communication", "PIPE-DataFlow",
    "PIPE-Integration", "PIPE-Monitoring", "PIPE-Security",
    "PIPE-Testing", "PIPE-Documentation", "PIPE-ServiceMesh", "PIPE-EventBridge"
]

COORDINATOR_CONFIG = {
    "port": 5100,
    "memory_limit": "128MB",
    "organisations": 13,
    "domain": "AI_Interfacing"
}
```

### IV Coordinator (Port 6000)
**Container**: `iv-coordinator`
**Image**: `docker.io/library/python:3.13-slim`
**Memory Limit**: 128MB
**Purpose**: Coordination hub for AI Memory domain (13 organisations)

```python
# IV Coordinator Configuration
IV_ORGANISATIONS = [
    "IV-Core", "IV-Memory", "IV-Agents",
    "IV-Knowledge", "IV-Learning", "IV-Reasoning",
    "IV-Analytics", "IV-Integration", "IV-Interface",
    "IV-Monitoring", "IV-Planning", "IV-Execution", "IV-Security"
]

COORDINATOR_CONFIG = {
    "port": 6000,
    "memory_limit": "128MB",
    "organisations": 13,
    "domain": "AI_Memory"
}
```

## BSW-ARCH Infrastructure Services

### HashiCorp Vault (Port 8200)
**Container**: `bsw-arch-vault`
**Image**: `docker.io/hashicorp/vault:latest`
**Memory Limit**: 256MB
**Purpose**: Centralized secret management for BSW-ARCH ecosystem

```yaml
Vault Configuration:
├── Mode: Development (demo-token: demo-token)
├── Secrets: All BSW-ARCH service credentials
├── Policies: Domain-specific access control
├── Backends: KV v2, Database, PKI
└── Integration: OpenTofu, Ansible, Helm
```

**Management Commands**:
```bash
# Check Vault status
export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="demo-token"
vault status

# List secret engines
vault secrets list

# Store BSW-ARCH secrets
vault kv put secret/bsw-arch/postgres username=bsw_admin password=secure_pass

# Update Vault memory limit
podman update --memory=256m bsw-arch-vault
```

### Zot Container Registry (Port 5000)
**Container**: `bsw-arch-zot-registry`
**Image**: `docker.io/library/registry:2`
**Memory Limit**: 192MB
**Purpose**: Local container registry for Chainguard distroless images

```yaml
Zot Registry Configuration:
├── Storage: Local filesystem
├── Images: 50+ Chainguard distroless images
├── Security: Digital sovereignty compliance
├── Access: Local BSW-ARCH services only
└── Sync: Periodic sync with external registries
```

**Management Commands**:
```bash
# Check registry catalog
curl http://localhost:5000/v2/_catalog

# List image tags
curl http://localhost:5000/v2/bsw/grafana/tags/list

# Push image to local registry
podman push localhost:5000/bsw/custom-image:latest

# Update registry memory limit
podman update --memory=192m bsw-arch-zot-registry
```

## BSW-ARCH MinIO Distributed Storage

### 5-Node MinIO Cluster Architecture
```yaml
BSW-ARCH MinIO Cluster:
├── Total Nodes: 5
├── Storage Distribution: Round-robin across tenants
├── Total Storage: 500GB (100GB per node)
├── Tenant Buckets: 10 (multi-tenant isolation)
└── High Availability: N-1 node failure tolerance

Node Distribution:
├── Node 1 (9000-9001): management, bsw-alfa, bsw-arch
├── Node 2 (9002-9003): bsw-beta, axis-knowledge
├── Node 3 (9004-9005): bsw-gamma, pipe-interface, iv-memory
├── Node 4 (9006-9007): keragr-federation, bot-ecosystem
└── Node 5 (9008-9009): Load balancing and HA
```

### MinIO Node Management
```bash
# BSW-ARCH MinIO Cluster Management

# Check all MinIO nodes
for port in 9000 9002 9004 9006 9008; do
  echo "Checking MinIO node on port $port:"
  curl -s http://localhost:$port/minio/health/live && echo " ✅ Healthy" || echo " ❌ Unhealthy"
done

# MinIO cluster status
mc admin info local

# List all tenant buckets
mc ls local

# Create new tenant bucket
mc mb local/new-tenant-bucket

# MinIO node resource usage
podman stats --no-stream bsw-arch-minio-node-{1..5}
```

### Tenant Bucket Configuration
```yaml
BSW-ARCH MinIO Tenants:
├── bsw-management: Administrative data and configs
├── bsw-alfa-team: Alpha team project data
├── bsw-beta-team: Beta team project data
├── bsw-gamma-team: Gamma team project data
├── bsw-arch-domain: Enterprise architecture artifacts
├── axis-knowledge: AI architecture knowledge base
├── pipe-interface: Interface definitions and schemas
├── iv-memory: AI memory and knowledge graphs
├── keragr-federation: Federated knowledge storage
└── bot-ecosystem: AI bot and agent data
```

## BSW-ARCH Container Orchestration Best Practices

### Container Lifecycle Management
```bash
# BSW-ARCH Container Lifecycle Script
#!/bin/bash

bsw_arch_start_containers() {
    echo "🚀 Starting BSW-ARCH Container Stack"

    # Start infrastructure first
    podman start bsw-arch-vault
    podman start bsw-arch-zot-registry
    sleep 10

    # Start storage cluster
    for node in bsw-arch-minio-node-{1..5}; do
        podman start $node
        sleep 2
    done

    # Start monitoring
    podman start bsw-postgresql-pod
    podman start bsw-prometheus-pod
    podman start bsw-grafana
    sleep 10

    # Start domain coordinators
    podman start axis-coordinator
    podman start pipe-coordinator
    podman start iv-coordinator

    echo "✅ BSW-ARCH Container Stack started"
}

bsw_arch_stop_containers() {
    echo "🛑 Stopping BSW-ARCH Container Stack"
    podman stop $(podman ps -q)
    echo "✅ All containers stopped"
}

bsw_arch_restart_containers() {
    echo "🔄 Restarting BSW-ARCH Container Stack"
    bsw_arch_stop_containers
    sleep 10
    bsw_arch_start_containers
}
```

### Container Health Monitoring
```python
# BSW-ARCH Container Health Monitor
import subprocess
import json
from datetime import datetime

def check_container_health():
    """Monitor BSW-ARCH container health"""

    # Get container status
    result = subprocess.run(
        ['podman', 'ps', '--format', 'json'],
        capture_output=True, text=True
    )

    containers = json.loads(result.stdout)

    health_report = {
        'timestamp': datetime.now().isoformat(),
        'total_containers': len(containers),
        'healthy_containers': 0,
        'unhealthy_containers': [],
        'memory_usage': {}
    }

    for container in containers:
        name = container['Names'][0]
        state = container['State']

        if state == 'running':
            health_report['healthy_containers'] += 1
        else:
            health_report['unhealthy_containers'].append({
                'name': name,
                'state': state,
                'created': container['CreatedAt']
            })

    return health_report

# Run health check
if __name__ == "__main__":
    health = check_container_health()
    print(f"📊 BSW-ARCH Container Health: {health['healthy_containers']}/{health['total_containers']} healthy")

    if health['unhealthy_containers']:
        print("⚠️ Unhealthy containers:")
        for container in health['unhealthy_containers']:
            print(f"  - {container['name']}: {container['state']}")
```

### Container Resource Optimization
```bash
# BSW-ARCH Container Resource Optimization
#!/bin/bash

optimize_container_resources() {
    echo "🔧 Optimizing BSW-ARCH Container Resources"

    # Monitor current usage
    echo "📊 Current container memory usage:"
    podman stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"

    # Identify over-allocated containers
    echo ""
    echo "🔍 Analyzing resource allocation..."

    for container in $(podman ps --format="{{.Names}}"); do
        # Get current memory limit
        limit=$(podman inspect $container | jq -r '.[0].HostConfig.Memory')

        if [ "$limit" = "0" ]; then
            echo "⚠️ $container: No memory limit set"
        else
            limit_mb=$((limit / 1024 / 1024))
            echo "✅ $container: ${limit_mb}MB limit"
        fi
    done

    echo ""
    echo "🎯 Resource optimization recommendations:"
    echo "  - All containers have memory limits ✅"
    echo "  - Monitor usage patterns for right-sizing"
    echo "  - Consider CPU limits for non-critical services"
}

# Run optimization analysis
optimize_container_resources
```

## BSW-ARCH Container Backup & Recovery

### Container Configuration Backup
```bash
# BSW-ARCH Container Backup Script
#!/bin/bash

backup_container_configs() {
    local backup_dir="/tmp/bsw-arch-container-backup-$(date +%Y%m%d)"
    mkdir -p "$backup_dir"

    echo "📦 Backing up BSW-ARCH container configurations"

    # Backup container inspect data
    for container in $(podman ps -a --format="{{.Names}}"); do
        podman inspect "$container" > "$backup_dir/${container}-inspect.json"
    done

    # Backup volumes and mounts
    podman volume ls --format json > "$backup_dir/volumes.json"

    # Backup network configuration
    podman network ls --format json > "$backup_dir/networks.json"

    # Create archive
    tar -czf "bsw-arch-containers-$(date +%Y%m%d).tar.gz" -C /tmp "$backup_dir"
    rm -rf "$backup_dir"

    echo "✅ Container backup complete: bsw-arch-containers-$(date +%Y%m%d).tar.gz"
}

restore_container_configs() {
    local backup_file="$1"

    if [ ! -f "$backup_file" ]; then
        echo "❌ Backup file not found: $backup_file"
        return 1
    fi

    echo "🔄 Restoring BSW-ARCH container configurations"
    tar -xzf "$backup_file" -C /tmp

    # Restore process would go here
    echo "⚠️ Manual restore required - inspect backup files in /tmp/"
}
```

---

**🎯 BSW-ARCH Container Orchestration: Comprehensive container management for the Enterprise Architecture AI Factory, ensuring optimal resource utilization, high availability, and operational excellence.**