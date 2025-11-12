# ECO Bot Examples - Complete Reference

> Production-ready examples for all ECO domain bot categories

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Total Examples**: 7 bots across 7 categories

## Overview

This directory contains fully functional example implementations for ECO domain bots, covering all major categories of the 48-bot ECO infrastructure.

## Available Bot Examples

| # | Bot Name | Category | Lines | Purpose |
|---|----------|----------|-------|---------|
| 1 | **eco-monitoring-bot** | Monitoring | 428 | System monitoring and health checks |
| 2 | **eco-infra-bot** | Infrastructure | 300 | OpenTofu infrastructure provisioning |
| 3 | **eco-resource-bot** | Optimization | 350 | Resource usage analysis and optimization |
| 4 | **eco-container-bot** | Container | 450 | Container security and size optimization |
| 5 | **eco-backup-bot** | Storage | 420 | Automated backup and recovery |
| 6 | **eco-security-bot** | Security | 480 | Security hardening and compliance |
| 7 | **eco-cleanup-bot** | Maintenance | 250 | Resource cleanup and garbage collection |
| 8 | **eco-scaler-bot** | Optimization | 280 | Auto-scaling management (HPA/VPA) |

**Total**: 2,958 lines of production-ready bot code

## Quick Start

### Run Any Bot

```bash
# Set environment
export DOCS_PATH="/opt/documentation"
export BOT_DOMAIN="ECO"
export METRICS_PORT="8000"

# Run a bot
python3 eco-bots/examples/eco_monitoring_bot.py
python3 eco-bots/examples/eco_container_bot.py
python3 eco-bots/examples/eco_backup_bot.py
# ... etc
```

### Build Container

```bash
# Using the monitoring bot Dockerfile as template
docker build -f eco-bots/examples/Dockerfile.eco-monitoring-bot \
  -t eco-bot-name:1.0.0 .

# Verify size (<50MB target)
docker images eco-bot-name:1.0.0
```

## Bot Details

### 1. ECO Monitoring Bot
**File**: `eco_monitoring_bot.py`
**Category**: Monitoring & Observability
**Responsibilities**:
- CPU, memory, disk, network monitoring
- Health check automation
- Prometheus metrics export
- Resource trend analysis
- Alert threshold management

**Key Features**:
- Real-time resource tracking
- Automatic health checks
- Metrics server on port 8000
- Context-aware monitoring

**Usage**:
```bash
python3 eco-bots/examples/eco_monitoring_bot.py
# Access metrics: http://localhost:8000/metrics
```

---

### 2. ECO Infrastructure Bot
**File**: `eco_infra_bot.py`
**Category**: Infrastructure Management
**Responsibilities**:
- OpenTofu infrastructure provisioning (NOT Terraform)
- FAGAM compliance checking
- Kubernetes resource management
- Namespace and deployment creation

**Key Features**:
- Uses OpenTofu (HashiCorp Terraform prohibited)
- FAGAM violation detection
- Infrastructure as Code
- Automated provisioning

**FAGAM Compliance**:
```python
# ✅ CORRECT
await provision_infrastructure(provider='opentofu')

# ❌ WRONG - Will be rejected
await provision_infrastructure(provider='terraform')  # FAGAM violation!
```

---

### 3. ECO Resource Bot
**File**: `eco_resource_bot.py`
**Category**: Resource Optimization
**Responsibilities**:
- Resource usage analysis
- Efficiency calculation (CPU/memory)
- Waste identification
- Optimization recommendations
- Cost savings tracking

**Key Features**:
- Efficiency target: 70%
- Automatic waste detection
- Savings calculations
- Prometheus metrics

**Example Output**:
```
📊 CPU Efficiency: 65.5% | Memory Efficiency: 72.3%
💡 Optimization Recommendations:
   CPU: 1500m → 900m (save 600m)
   Reason: CPU efficiency is 65.5%, below target 70%
```

---

### 4. ECO Container Bot
**File**: `eco_container_bot.py`
**Category**: Container & Registry
**Responsibilities**:
- Container image optimization
- Size monitoring (<50MB target)
- Vulnerability scanning
- Base image compliance (Wolfi only)
- Layer optimization

**Key Features**:
- Enforces 50MB size limit
- Zero vulnerability tolerance
- Chainguard Wolfi base requirement
- Multi-stage build recommendations

**Compliance Checks**:
```
✅ Size: 35MB (within limit)
✅ Base: wolfi-base (approved)
✅ Vulnerabilities: 0 (compliant)
❌ Size: 75MB (exceeds 50MB limit) - VIOLATION
```

---

### 5. ECO Backup Bot
**File**: `eco_backup_bot.py`
**Category**: Storage & Data
**Responsibilities**:
- Automated backup scheduling
- Data integrity verification
- Multi-location replication
- Retention management
- Restore point tracking

**Key Features**:
- Daily automated backups
- 30-day retention
- 3-location replication
- Checksum verification
- RTO estimation

**Backup Schedule**:
- Databases: Every 24h (full)
- Volumes: Every 24h (incremental)
- Configs: Every 12h (full)
- Secrets: Every 24h (full, encrypted)

---

### 6. ECO Security Bot
**File**: `eco_security_bot.py`
**Category**: Security & Compliance
**Responsibilities**:
- Container security scanning
- Network policy validation
- RBAC policy audit
- Secrets management (OpenBao)
- Auto-remediation
- Security scoring (0-100)

**Key Features**:
- Zero-trust security model
- Non-root container enforcement
- Network policy validation
- OpenBao integration (NOT Vault)
- Auto-remediation for low/medium issues

**Security Scoring**:
```
📊 Security Score: 85/100
   CRITICAL: 0
   HIGH: 2
   MEDIUM: 3
   LOW: 1
✅ Auto-remediated 3 findings
```

---

### 7. ECO Cleanup Bot
**File**: `eco_cleanup_bot.py`
**Category**: Maintenance & Cleanup
**Responsibilities**:
- Unused container image cleanup
- Orphaned volume removal
- Completed job cleanup
- Log rotation and archival

**Key Features**:
- 30-day image retention
- 24-hour job retention
- 7-day log retention
- Automatic garbage collection

**Example Output**:
```
✅ Removed 8 images, reclaimed 2000MB
✅ Removed 3 volumes, reclaimed 3000MB
✅ Removed 12 completed jobs
✅ Archived 18 log files, reclaimed 900MB
📊 Total space reclaimed: 5900MB
```

---

### 8. ECO Scaler Bot
**File**: `eco_scaler_bot.py`
**Category**: Resource Optimization
**Responsibilities**:
- Horizontal Pod Autoscaling (HPA)
- Vertical Pod Autoscaling (VPA)
- Predictive scaling
- Cost-aware scaling
- Load-based decisions

**Key Features**:
- CPU threshold: 70% (scale up), 30% (scale down)
- Memory threshold: 80% (scale up), 40% (scale down)
- Min replicas: 1, Max replicas: 10
- Real-time scaling decisions

**Example Output**:
```
↗️ Scaling eco-monitoring: 2 → 3 (cpu=75%)
↘️ Scaling cag-rag-mcp: 5 → 4 (low_usage cpu=25% memory=35%)
```

## Common Features

All ECO bot examples include:

### 1. Documentation Integration
```python
from doc_scanner import DocScanner

scanner = DocScanner("/opt/documentation")
eco_docs = scanner.get_documents_by_domain("ECO")
```

### 2. Prometheus Metrics
```python
from prometheus_client import start_http_server, Gauge, Counter

# Start metrics server
start_http_server(8000)

# Define metrics
my_metric = Gauge('bot_metric_name', 'Description')
my_counter = Counter('bot_counter_name', 'Description')
```

### 3. Async Architecture
```python
async def run(self):
    while True:
        await self.do_work()
        await asyncio.sleep(interval)

# Run
asyncio.run(bot.run())
```

### 4. Structured Logging
```python
self.logger.info("✅ Operation successful")
self.logger.warning("⚠️  Warning message")
self.logger.error("❌ Error message")
```

## Testing

### Run Individual Bot
```bash
python3 eco-bots/examples/eco_monitoring_bot.py
```

### Run with Custom Config
```bash
export LOG_LEVEL=DEBUG
export METRICS_PORT=9000
python3 eco-bots/examples/eco_security_bot.py
```

### Check Metrics
```bash
# While bot is running
curl http://localhost:8000/metrics
```

## Deployment

### Docker
```bash
# Build
docker build -f eco-bots/examples/Dockerfile.eco-monitoring-bot \
  -t my-eco-bot:1.0.0 .

# Run
docker run -p 8000:8000 \
  -e DOCS_PATH=/opt/documentation \
  -e LOG_LEVEL=INFO \
  my-eco-bot:1.0.0
```

### Kubernetes
```bash
# Use template as base
kubectl apply -f docs/templates/deployment/eco/eco-monitoring-bot.yaml

# Verify
kubectl get pods -n eco-bots
kubectl logs -f deployment/eco-monitoring-bot -n eco-bots
```

## Creating New Bots

Use any example as a template:

```bash
# Copy template
cp eco-bots/examples/eco_monitoring_bot.py eco-bots/examples/eco_your_bot.py

# Customize
# 1. Change class name: EcoMonitoringBot → EcoYourBot
# 2. Update responsibilities
# 3. Implement your logic
# 4. Update metrics
# 5. Test locally
```

## Bot Categories Coverage

| Category | Example Bots | Coverage |
|----------|--------------|----------|
| Infrastructure (8) | eco-infra-bot | ✅ 1/8 |
| Optimization (8) | eco-resource-bot, eco-scaler-bot | ✅ 2/8 |
| Monitoring (8) | eco-monitoring-bot | ✅ 1/8 |
| Container (6) | eco-container-bot | ✅ 1/6 |
| Storage (6) | eco-backup-bot | ✅ 1/6 |
| Network (5) | - | ⚠️ 0/5 |
| Security (4) | eco-security-bot | ✅ 1/4 |
| Maintenance (3) | eco-cleanup-bot | ✅ 1/3 |

**Total Coverage**: 8 of 48 bots (16.7%)

## Metrics Reference

All bots expose Prometheus metrics on port 8000:

### Common Metrics
- `bot_requests_total`: Total requests processed
- `bot_errors_total`: Total errors encountered
- `bot_processing_duration_seconds`: Processing time

### Bot-Specific Metrics

**Monitoring Bot**:
- `bot_cpu_usage_percent`
- `bot_memory_usage_bytes`
- `bot_health_status`

**Container Bot**:
- `bot_container_size_mb`
- `bot_container_vulnerabilities`
- `bot_optimization_savings_mb`

**Backup Bot**:
- `bot_backup_total`
- `bot_backup_size_mb`
- `bot_backup_duration_seconds`

**Security Bot**:
- `bot_security_findings`
- `bot_security_score`
- `bot_remediation_actions_total`

## Troubleshooting

### Bot won't start
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check dependencies
pip list | grep -E "(prometheus|doc-scanner)"

# Check documentation
ls /opt/documentation/docs/
```

### Metrics not working
```bash
# Check port availability
lsof -i :8000

# Test metrics endpoint
curl http://localhost:8000/metrics
```

### Import errors
```bash
# Ensure documentation is cloned
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation

# Check PYTHONPATH
export PYTHONPATH="/opt/documentation/bot-utils:$PYTHONPATH"
```

## References

- [ECO Domain Architecture](../docs/architecture/domains/ECO/ECO-DOMAIN-ARCHITECTURE.md)
- [ECO Bot List](../eco-bots/configs/eco-bot-list.yaml)
- [Container Specifications](../docs/specifications/containers/eco/)
- [Deployment Templates](../docs/templates/deployment/eco/)

---

**Maintained by**: BSW-Tech Architecture Team
**Component**: ECO Bot Examples
**Coverage**: 8 of 48 bots implemented
**Status**: Production Ready
