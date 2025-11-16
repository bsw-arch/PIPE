# PIPE Monitoring & Observability Guide

Complete guide to monitoring, observability, and production operations for the PIPE Bot System.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Metrics](#metrics)
- [Health Checks](#health-checks)
- [Structured Logging](#structured-logging)
- [Prometheus Integration](#prometheus-integration)
- [Grafana Dashboards](#grafana-dashboards)
- [Alerts](#alerts)
- [Production Setup](#production-setup)

---

## Overview

PIPE provides comprehensive monitoring and observability features:

- **Prometheus Metrics**: Industry-standard metrics export
- **Health Check Endpoints**: Kubernetes-compatible liveness/readiness probes
- **Structured JSON Logging**: Machine-parseable logs for aggregation
- **Metrics HTTP Server**: Built-in HTTP server for metrics scraping
- **Grafana Dashboards**: Pre-built visualization dashboards
- **Real-time Monitoring**: Bot status, governance metrics, performance data

---

## Quick Start

### 1. Start the Metrics Server

```python
import asyncio
from src.monitoring import MetricsServer, HealthChecker
from src.utils.metrics import MetricsCollector

async def main():
    # Initialize components
    metrics = MetricsCollector()
    health_checker = HealthChecker()

    # Create metrics server
    server = MetricsServer(
        metrics_collector=metrics,
        health_checker=health_checker,
        port=9090
    )

    # Start server
    await server.start()

    # Keep running
    await asyncio.Event().wait()

asyncio.run(main())
```

### 2. Access Endpoints

- **Metrics**: http://localhost:9090/metrics
- **Health**: http://localhost:9090/health
- **Liveness**: http://localhost:9090/health/live
- **Readiness**: http://localhost:9090/health/ready

### 3. View in Browser

Navigate to http://localhost:9090/ for an index of all endpoints.

---

## Metrics

### Available Metrics

#### Bot Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pipe_bot_status` | Gauge | Bot operational status (1=running, 0=other) |
| `pipe_bot_uptime_seconds` | Gauge | Bot uptime in seconds |
| `pipe_bot_tasks_total` | Counter | Total tasks processed by bot |
| `pipe_bot_errors_total` | Counter | Total errors encountered |

**Labels**: `bot` (bot name), `status` (bot status)

#### Governance Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pipe_governance_domains_total` | Gauge | Total domains in ecosystem |
| `pipe_governance_domains_active` | Gauge | Active domains |
| `pipe_governance_integrations_total` | Gauge | Total integrations |
| `pipe_governance_integrations_active` | Gauge | Active integrations |
| `pipe_governance_compliance_percentage` | Gauge | Ecosystem compliance percentage |
| `pipe_governance_reviews_total` | Gauge | Total reviews |
| `pipe_governance_reviews_pending` | Gauge | Pending reviews |
| `pipe_governance_reviews_approved` | Gauge | Approved reviews |

#### Performance Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pipe_data_processor_queue_size` | Gauge | Data processor queue size |
| `pipe_data_processor_processing_time_avg` | Summary | Average processing time |
| `pipe_events_published` | Counter | Events published to event bus |
| `pipe_events_processed` | Counter | Events processed |

### Prometheus Format Example

```
# TYPE pipe_bot_status gauge
pipe_bot_status{bot="pipeline_bot",status="running"} 1
pipe_bot_status{bot="data_processor_bot",status="running"} 1

# TYPE pipe_bot_uptime_seconds gauge
pipe_bot_uptime_seconds{bot="pipeline_bot"} 3600.5

# TYPE pipe_bot_tasks_total counter
pipe_bot_tasks_total{bot="pipeline_bot"} 1250
```

---

## Health Checks

### Liveness Probe

**Endpoint**: `GET /health/live`

Checks if the application is alive and responsive.

**Success Response** (HTTP 200):
```json
{
  "status": "alive",
  "timestamp": "2025-11-13T10:30:00Z",
  "uptime_seconds": 3600.5
}
```

**Use Cases**:
- Kubernetes liveness probe
- Docker health check
- Process monitoring

### Readiness Probe

**Endpoint**: `GET /health/ready`

Checks if the application is ready to serve traffic.

**Success Response** (HTTP 200):
```json
{
  "status": "ready",
  "ready": true,
  "timestamp": "2025-11-13T10:30:00Z",
  "reasons": ["All systems operational"]
}
```

**Not Ready Response** (HTTP 503):
```json
{
  "status": "not_ready",
  "ready": false,
  "timestamp": "2025-11-13T10:30:00Z",
  "reasons": ["1 bot(s) in error state: ['data_processor']"]
}
```

**Use Cases**:
- Kubernetes readiness probe
- Load balancer health check
- Service mesh integration

### Detailed Health Check

**Endpoint**: `GET /health`

Comprehensive health check with component breakdown.

**Response** (HTTP 200/503):
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T10:30:00Z",
  "uptime_seconds": 3600.5,
  "components": {
    "bots": {
      "status": "healthy",
      "total_bots": 4,
      "running_bots": 4,
      "error_bots": 0,
      "total_errors": 2,
      "issues": []
    },
    "governance": {
      "status": "healthy",
      "active_domains": 5,
      "active_integrations": 3,
      "compliance_percentage": 85.5,
      "pending_reviews": 2,
      "issues": []
    }
  },
  "metrics": {
    "events_published": 5000,
    "events_processed": 4995
  },
  "issues": []
}
```

**Health Status Levels**:
- `healthy`: All systems operational
- `degraded`: Some issues but functional
- `unhealthy`: Critical issues affecting operation

---

## Structured Logging

### JSON Log Format

All logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2025-11-13T10:30:00.123456Z",
  "level": "INFO",
  "logger": "pipe.bot.pipeline",
  "message": "Pipeline completed successfully",
  "module": "pipeline_bot",
  "function": "run_pipeline",
  "line": 145,
  "process": {"id": 12345, "name": "MainProcess"},
  "thread": {"id": 67890, "name": "MainThread"},
  "pipeline_id": "test_pipeline_1",
  "duration": 2.5
}
```

### Configure Structured Logging

```python
from src.monitoring.structured_logger import configure_structured_logging

# Enable JSON logging
configure_structured_logging(
    level="INFO",
    json_file="logs/pipe.json",
    enable_console=True
)
```

### Context Logger

Add context to all log messages:

```python
from src.monitoring.structured_logger import ContextLogger

logger = ContextLogger(logger, context={"bot": "pipeline"})
logger.add_context(pipeline_id="test_001")

logger.info("Processing started")  # Includes bot and pipeline_id
```

### Audit Logging

Log compliance and security events:

```python
from src.monitoring.structured_logger import create_audit_logger, log_audit_event

audit_logger = create_audit_logger("logs/audit.json")

log_audit_event(
    audit_logger.get_logger(),
    event_type="integration",
    actor="admin@example.com",
    action="approve",
    resource="INT-000001",
    result="success",
    compliance_id="comp_123"
)
```

---

## Prometheus Integration

### 1. Install Prometheus

```bash
# Docker
docker run -d -p 9091:9090 \\
  -v $(pwd)/config/prometheus.yml:/etc/prometheus/prometheus.yml \\
  prom/prometheus

# Or download from: https://prometheus.io/download/
```

### 2. Configure Prometheus

Create `config/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'pipe-bots'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          environment: 'production'
          service: 'pipe-bots'
```

### 3. Verify Metrics

```bash
# Check if Prometheus is scraping
curl http://localhost:9091/api/v1/targets

# Query metrics
curl 'http://localhost:9091/api/v1/query?query=pipe_bot_status'
```

---

## Grafana Dashboards

### 1. Install Grafana

```bash
# Docker
docker run -d -p 3000:3000 grafana/grafana

# Access at: http://localhost:3000
# Default credentials: admin/admin
```

### 2. Add Prometheus Data Source

1. Navigate to **Configuration → Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Set URL: `http://localhost:9091`
5. Click **Save & Test**

### 3. Import PIPE Dashboard

1. Navigate to **Dashboards → Import**
2. Click **Upload JSON file**
3. Select `config/grafana-dashboard.json`
4. Select Prometheus data source
5. Click **Import**

### Dashboard Panels

The PIPE dashboard includes:

- **System Overview**: Running bots, domains, integrations, compliance
- **Bot Status Table**: Detailed bot status information
- **Bot Uptime Graph**: Uptime trends over time
- **Task Rate**: Tasks processed per second
- **Error Rate**: Errors per second with alerting
- **Compliance Gauge**: Current compliance percentage
- **Review Backlog**: Pending vs approved reviews
- **Processing Time**: Average data processing time
- **Event Bus Activity**: Event publishing/processing rates
- **Queue Size**: Data processor queue metrics

---

## Alerts

### Configure Alerts in Grafana

Pre-configured alerts in the dashboard:

#### High Error Rate Alert

**Condition**: Error rate > 0.1 errors/sec for 5 minutes
**Action**: Send notification
**Severity**: Warning

#### High Queue Size Alert

**Condition**: Queue size > 100 items for 5 minutes
**Action**: Send notification
**Severity**: Warning

### Notification Channels

Configure notification channels in Grafana:

1. **Email**: Send alerts to email
2. **Slack**: Post alerts to Slack channel
3. **PagerDuty**: Create incidents for critical alerts
4. **Webhook**: Custom webhook integration

Example Slack configuration:

```json
{
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "channel": "#pipe-alerts",
  "username": "PIPE Monitoring",
  "icon_emoji": ":robot_face:"
}
```

---

## Production Setup

### Docker Compose

Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  pipe:
    image: pipe-bots:latest
    ports:
      - "9090:9090"
    environment:
      - METRICS_PORT=9090
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9091:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your-secure-password
    volumes:
      - grafana-data:/var/lib/grafana
      - ./config/grafana-dashboard.json:/etc/grafana/provisioning/dashboards/pipe.json

volumes:
  prometheus-data:
  grafana-data:
```

Start the stack:

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### Kubernetes Deployment

#### 1. Service Definition

```yaml
apiVersion: v1
kind: Service
metadata:
  name: pipe-metrics
  labels:
    app: pipe
spec:
  ports:
    - port: 9090
      name: metrics
  selector:
    app: pipe
  type: ClusterIP
```

#### 2. Deployment with Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pipe-bots
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pipe
  template:
    metadata:
      labels:
        app: pipe
    spec:
      containers:
        - name: pipe
          image: pipe-bots:latest
          ports:
            - containerPort: 9090
              name: metrics
          livenessProbe:
            httpGet:
              path: /health/live
              port: 9090
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 9090
            initialDelaySeconds: 5
            periodSeconds: 5
```

#### 3. ServiceMonitor for Prometheus Operator

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: pipe-metrics
  labels:
    app: pipe
spec:
  selector:
    matchLabels:
      app: pipe
  endpoints:
    - port: metrics
      interval: 15s
      path: /metrics
```

### Best Practices

1. **Metrics Retention**: Keep 15 days of metrics in Prometheus
2. **Log Rotation**: Rotate JSON logs daily, keep 30 days
3. **Alert Fatigue**: Set appropriate thresholds to avoid noise
4. **Dashboard Organization**: Group related metrics together
5. **Security**: Protect metrics endpoints with authentication
6. **Backup**: Regularly backup Prometheus data and Grafana dashboards
7. **Capacity Planning**: Monitor resource usage trends

### Troubleshooting

#### Metrics Not Showing

```bash
# Check if metrics server is running
curl http://localhost:9090/metrics

# Check Prometheus targets
curl http://localhost:9091/api/v1/targets

# View Prometheus logs
docker logs prometheus-container
```

#### Health Checks Failing

```bash
# Check detailed health
curl http://localhost:9090/health | jq

# Check individual bots
# Look for issues in the response
```

#### High Resource Usage

```bash
# Check metrics
curl http://localhost:9090/metrics | grep queue_size
curl http://localhost:9090/metrics | grep error

# Review structured logs
tail -f logs/pipe.json | jq
```

---

## Integration Examples

### Custom Metrics

Export custom application metrics:

```python
from src.monitoring import PrometheusExporter

custom_metrics = {
    "my_custom_metric": {
        "type": "gauge",
        "value": 42,
        "labels": {"component": "custom"}
    }
}

prometheus = PrometheusExporter(metrics_collector)
custom_output = prometheus.export_custom_metrics(custom_metrics)
```

### Health Check Callbacks

Provide real-time data to health checks:

```python
def get_bot_statuses():
    return [
        {
            "name": "pipeline_bot",
            "status": "running",
            "uptime_seconds": 3600,
            "task_count": 100,
            "error_count": 0
        }
    ]

server.set_bot_status_callback(get_bot_statuses)
```

---

## Summary

PIPE provides production-grade monitoring with:

- ✅ Prometheus metrics for scraping and alerting
- ✅ Kubernetes-compatible health checks
- ✅ Structured JSON logging for aggregation
- ✅ Pre-built Grafana dashboards
- ✅ Real-time observability into bots and governance
- ✅ Production-ready deployment examples

For questions or issues, consult the troubleshooting section or check application logs.

---

**Built with ❤️ for the BSW Architecture PIPE Domain**
