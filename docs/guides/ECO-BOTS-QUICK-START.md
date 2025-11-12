# ECO Bots Quick Start Guide

> Get started with ECO domain bots in 5 minutes

**Domain**: ECO (Ecological)
**Purpose**: Infrastructure, monitoring, resource optimization
**Bot Count**: 48

## Prerequisites

- Python 3.11+
- Docker or Podman
- kubectl (for Kubernetes deployment)
- OpenTofu (for infrastructure provisioning)
- Git

## 5-Minute Quick Start

### Step 1: Clone Documentation (30 seconds)

```bash
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation
cd /opt/documentation
```

### Step 2: Install Dependencies (1 minute)

```bash
pip install pyyaml requests prometheus-client psutil
```

### Step 3: Run Example Bot (30 seconds)

```bash
export DOCS_PATH="/opt/documentation/docs"
export BOT_DOMAIN="ECO"
export METRICS_PORT="8000"

python3 eco-bots/examples/eco_monitoring_bot.py
```

### Step 4: View Metrics (30 seconds)

Open a new terminal:

```bash
curl http://localhost:8000/metrics
```

You should see Prometheus metrics output.

### Step 5: Build Container (2 minutes)

```bash
cd eco-bots/examples
docker build -f Dockerfile.eco-monitoring-bot -t eco-monitoring-bot:1.0.0 .

# Verify size (should be <50MB)
docker images eco-monitoring-bot:1.0.0
```

## Deploy to Kubernetes

### Local Kubernetes (minikube)

```bash
# Start minikube
minikube start

# Create namespace
kubectl apply -f docs/templates/deployment/eco/eco-namespace-setup.yaml

# Deploy monitoring bot
kubectl apply -f docs/templates/deployment/eco/eco-monitoring-bot.yaml

# Check status
kubectl get pods -n eco-bots

# View logs
kubectl logs -f deployment/eco-monitoring-bot -n eco-bots

# Access metrics
kubectl port-forward -n eco-bots svc/eco-monitoring-bot 8000:8000

# In another terminal
curl http://localhost:8000/metrics
```

## Common Tasks

### View ECO Bot List

```bash
cat eco-bots/configs/eco-bot-list.yaml
```

### Scan Documentation

```bash
python3 bot-utils/doc_scanner.py --action list --domain ECO
```

### Check Container Size

```bash
docker images | grep eco
```

### View Resource Usage

```bash
kubectl top pod -n eco-bots
```

### Deploy Monitoring Stack

```bash
cd docs/specifications/infrastructure/eco
tofu init
tofu plan
tofu apply

# Access Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Open http://localhost:3000 (admin/admin)
```

## Troubleshooting

### Documentation not found

```bash
# Ensure you cloned to the right location
ls /opt/documentation/docs

# If not, clone again
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation
```

### Python import errors

```bash
# Install missing dependencies
pip install pyyaml requests prometheus-client psutil

# Or install from requirements
pip install -r eco-bots/examples/requirements.txt
```

### Container too large

```bash
# Check size
docker images | grep eco

# If >50MB, rebuild with Wolfi base
# See: docs/specifications/containers/eco/eco-base.yaml
```

### Metrics not accessible

```bash
# Check if bot is running
ps aux | grep eco_monitoring_bot

# Check if port is in use
lsof -i :8000

# Check firewall
sudo ufw status
```

## Next Steps

1. **Explore Examples**:
   ```bash
   ls eco-bots/examples/
   ```

2. **Read Architecture**:
   ```bash
   cat docs/architecture/domains/ECO/ECO-DOMAIN-ARCHITECTURE.md
   ```

3. **Review Container Specs**:
   ```bash
   ls docs/specifications/containers/eco/
   ```

4. **Study Infrastructure Templates**:
   ```bash
   ls docs/specifications/infrastructure/eco/
   ```

5. **Customize Deployment**:
   ```bash
   ls docs/templates/deployment/eco/
   ```

## Resources

- **Full Documentation**: [eco-bots/README.md](../../eco-bots/README.md)
- **Domain Architecture**: [docs/architecture/domains/ECO/ECO-DOMAIN-ARCHITECTURE.md](../architecture/domains/ECO/ECO-DOMAIN-ARCHITECTURE.md)
- **Container Specs**: [docs/specifications/containers/eco/](../specifications/containers/eco/)
- **Infrastructure**: [docs/specifications/infrastructure/eco/](../specifications/infrastructure/eco/)

## Support

- **GitHub Issues**: https://github.com/bsw-arch/bsw-arch/issues
- **Codeberg**: https://codeberg.org/ECO-Bots
- **Documentation**: https://github.com/bsw-arch/bsw-arch

---

**Last Updated**: 2025-11-10
**Version**: 1.0.0
**Domain**: ECO (Ecological)
