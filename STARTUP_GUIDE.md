# BSW-ARCH Enterprise Architecture Platform Startup Guide
> **Beter Samen Werken** - Production-ready startup instructions for Dutch Ministry of Finance

## Overview

This guide provides comprehensive instructions for starting the complete Enterprise Architecture Platform with proper service dependencies, health checks, and conflict resolution.

## Quick Start

```bash
# Start HA PostgreSQL cluster first
./start-bsw-postgresql-ha.sh

# Start complete BSW-ARCH platform
./start-complete-devsecops-integrated.sh

# Alternative: Start specific BSW contexts
./start-bio-architects.sh          # Architecture + IAM
./start-devsecops.sh              # Security pipeline
./start-gitops-integrated.sh      # Git + CI/CD
./start-hybrid-architects.sh      # Full hybrid team

# Health monitoring
./docker-health-check.sh status
./docker-health-check.sh watch

# Stop services
podman-compose -f docker-compose-bsw-postgresql-ha.yml down
```

## Service Architecture

### Platform Components

The EA Platform consists of **18 core services** organised in **6 dependency tiers**:

#### Tier 1: Infrastructure Foundation (Start First)
- **Vault** (Port 8200) - Centralised secrets management
- **Zot Registry** (Port 5000) - Local container registry with Chainguard images
- **External Volumes** - Persistent storage for all services

#### Tier 2: Networking & Service Discovery
- **Consul** (Ports 8500, 8600, 8502) - Service mesh and discovery
- **Traefik** (Ports 80, 443, 8080) - Reverse proxy and load balancer

#### Tier 3: Identity & Access Management
- **BSW-ARCH PostgreSQL HA Cluster** (Ports 5432/5433) - 3-node HA database with Patroni
  - Primary: `bsw-arch-postgresql-node-1` (Port 5432) - Write operations
  - Replicas: `bsw-arch-postgresql-node-{2,3}` (Port 5433) - Read operations
  - HAProxy Load Balancer: Automatic failover and connection routing
- **Zitadel IAM** (Port 8082) - Identity provider with OIDC/OAuth2

#### Tier 4: Application Services
- **Forgejo** (Port 3000) - Git repository server with OIDC
- **ArgoCD** (Port 8081) - GitOps deployment platform
- **Woodpecker CI** (Port 8000) - Continuous integration
- **Jenkins** (Port 8080/8081) - Enterprise CI/CD
- **Hybrid Architects** - Digital and biological architecture agents

#### Tier 5: Security & Monitoring
- **DevSecOps Pipeline** - Gitleaks, Semgrep, SonarQube, Trivy, Grype, Nuclei
- **SonarQube** (Port 9000) - Code quality analysis
- **Grafana** (Port 3001) - Monitoring dashboards with Zitadel OIDC
- **Prometheus** (Port 9091) - Metrics collection
- **Loki** (Port 3101) - Log aggregation

#### Tier 6: Specialised Services
- **Neo4j** (Ports 7474, 7687) - BSW KERAG-R knowledge graph
- **Qdrant** (Ports 6333, 6334) - Vector database for AI/ML
- **Archi Collaborative** (Port 8090) - Architecture modelling

## Prerequisites

### System Requirements

```bash
# Minimum requirements:
- Docker 24.0+
- Docker Compose 2.0+
- 16GB RAM (32GB recommended)
- 50GB free disk space
- Linux/macOS (Windows with WSL2)

# Verify prerequisites:
docker --version
docker-compose --version
docker info
```

### Host Directory Setup

```bash
# Create required host directories:
sudo mkdir -p /var/lib/neo4j-bsw
sudo mkdir -p /var/lib/neo4j-bsw-logs  
sudo mkdir -p /var/lib/neo4j-bsw-import
sudo mkdir -p /var/lib/vault-bsw
sudo mkdir -p /home/user/.local/share/containers/volumes/ea-persistent/_data

# Set proper ownership:
sudo chown -R user:user /home/user/.local/share/containers/volumes/ea-persistent
sudo chown -R 7474:7474 /var/lib/neo4j-bsw* # Neo4j user
```

### External Volumes

```bash
# Create Docker volumes:
docker volume create ea-vault-data
docker volume create ea-persistent

# Verify volumes:
docker volume ls | grep ea-
```

## Startup Sequence

### Automated Startup (Recommended)

```bash
# Full platform startup with health checks:
./docker-compose-startup.sh start

# This will:
# 1. Create external volumes
# 2. Start services in correct dependency order  
# 3. Perform health checks between tiers
# 4. Display service URLs when complete
```

### Manual Startup (For Debugging)

```bash
# Tier 1: Infrastructure
docker-compose -f docker-compose-zot-registry.yml up -d
# Wait for health: curl -f http://localhost:8200/v1/sys/health
# Wait for health: curl -f http://localhost:5000/v2/

# Tier 2: Networking  
docker-compose -f docker-compose-traefik-consul.yml up -d
# Wait for health: curl -f http://localhost:8500/v1/status/leader
# Wait for health: curl -f http://localhost:8080/api/rawdata

# Tier 3: Identity
docker-compose -f docker-compose-zitadel-iam.yml up -d
# Wait for health: curl -f http://localhost:8082/debug/ready

# Tier 4: Applications
docker-compose -f docker-compose-gitops-integrated.yml up -d
docker-compose -f docker-compose-hybrid-architects.yml up -d
docker-compose -f docker-compose-argocd-bio.yml up -d
docker-compose -f docker-compose-archi-collaborative.yml up -d

# Tier 5: Security & Monitoring
docker-compose -f docker-compose-devsecops.yml up -d

# Tier 6: Specialised
docker-compose -f docker-compose-bsw-kerag.yml up -d
```

## Health Monitoring

### Service Health Checks

```bash
# Quick health overview:
./docker-health-check.sh status

# Continuous monitoring:
./docker-health-check.sh watch

# Show all service URLs:  
./docker-health-check.sh urls

# Resource usage statistics:
./docker-health-check.sh resources

# Complete platform overview:
./docker-health-check.sh full
```

### Manual Health Verification

```bash
# Infrastructure checks:
curl -f http://localhost:8200/v1/sys/health     # Vault
curl -f http://localhost:5000/v2/               # Zot Registry

# Networking checks:
curl -f http://localhost:8500/v1/status/leader  # Consul  
curl -f http://localhost:8080/api/rawdata       # Traefik

# Identity checks:
curl -f http://localhost:8082/debug/ready       # Zitadel

# Application checks:
curl -f http://localhost:3000/api/healthz       # Forgejo
curl -f http://localhost:8081/healthz           # ArgoCD
curl -f http://localhost:8000/                  # Woodpecker

# Security & Monitoring checks:
curl -f http://localhost:9000/api/system/status # SonarQube
curl -f http://localhost:3001/api/health        # Grafana
curl -f http://localhost:9091/-/ready           # Prometheus

# Specialised checks:
curl -f http://localhost:7474/db/system/        # Neo4j
curl -f http://localhost:6333/health            # Qdrant
```

## Service URLs & Access

### Core Platform Services

| Service | URL | Credentials | Notes |
|---------|-----|-------------|-------|
| **Vault UI** | http://localhost:8200 | See vault-keys.txt | Secrets management |
| **Zot Registry** | http://localhost:5000 | admin/stored-in-vault | Container registry |
| **Consul UI** | http://localhost:8500 | No auth | Service discovery |
| **Traefik Dashboard** | http://localhost:8080 | admin/stored-in-vault | Reverse proxy |

### Identity & Authentication

| Service | URL | Credentials | Notes |
|---------|-----|-------------|-------|
| **Zitadel IAM** | http://localhost:8082 | bio-admin/stored-in-vault | OIDC provider |

### GitOps & CI/CD

| Service | URL | Credentials | Notes |
|---------|-----|-------------|-------|
| **Forgejo Git** | http://localhost:3000 | Setup on first login | Git repositories |
| **ArgoCD** | http://localhost:8081 | admin/stored-in-vault | GitOps deployments |
| **Woodpecker CI** | http://localhost:8000 | Via Forgejo OIDC | CI/CD pipelines |
| **Jenkins** | http://localhost:8080 | admin/admin123 | Enterprise CI/CD |

### Security & Quality

| Service | URL | Credentials | Notes |
|---------|-----|-------------|-------|
| **SonarQube** | http://localhost:9000 | admin/admin | Code quality |

### Monitoring & Observability

| Service | URL | Credentials | Notes |
|---------|-----|-------------|-------|
| **Grafana** | http://localhost:3001 | Via Zitadel OIDC | Dashboards |
| **Prometheus** | http://localhost:9091 | No auth | Metrics |

### Specialised Services

| Service | URL | Credentials | Notes |
|---------|-----|-------------|-------|
| **Neo4j Browser** | http://localhost:7474 | neo4j/BSW-KERAG-2024 | Knowledge graph |
| **Qdrant UI** | http://localhost:6333 | No auth | Vector database |
| **Archi Collaborative** | http://localhost:8090 | Setup required | Architecture |

## Troubleshooting

### Common Issues

#### Port Conflicts

```bash
# Check port usage:
netstat -tulpn | grep -E "(8080|3000|8200|5000)"

# Kill conflicting processes:
sudo lsof -ti:8080 | xargs sudo kill -9

# Use alternative ports if needed (see compose files)
```

#### Volume Permissions

```bash
# Fix volume ownership:
sudo chown -R user:user /home/user/.local/share/containers/volumes/ea-persistent
sudo chown -R 7474:7474 /var/lib/neo4j-bsw*

# Recreate volumes if corrupted:
docker volume rm ea-persistent ea-vault-data
docker volume create ea-persistent
docker volume create ea-vault-data
```

#### Service Startup Failures

```bash
# Check service logs:
docker-compose -f docker-compose-zot-registry.yml logs vault-zot-secrets
docker-compose -f docker-compose-gitops-integrated.yml logs forgejo

# Restart specific service:
docker-compose -f docker-compose-zitadel-iam.yml restart zitadel

# Verify dependencies:
./docker-health-check.sh status
```

#### Network Connectivity

```bash
# Check Docker networks:
docker network ls
docker network inspect ea-integrated-network

# Test inter-service connectivity:
docker exec ea-forgejo-gitops curl -f http://postgres-integrated:5432
```

### Resource Issues

```bash
# Monitor resource usage:
docker stats

# Clean up unused resources:
docker system prune -a --volumes

# Increase Docker memory (Docker Desktop):
# Settings -> Resources -> Memory: 8GB minimum
```

### Log Analysis

```bash
# View startup logs:
tail -f /home/user/Code/startup.log

# Service-specific logs:
docker-compose -f docker-compose-hybrid-architects.yml logs -f jenkins
docker-compose -f docker-compose-traefik-consul.yml logs traefik

# All container logs:
docker logs ea-zitadel-iam
docker logs ea-vault-secrets-manager
```

## Security Configuration

### Secrets Management

All sensitive credentials are managed through HashiCorp Vault:

```bash
# Access Vault:
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=$(grep 'Root Token:' /home/user/.local/share/containers/volumes/ea-persistent/_data/vault-keys.txt | cut -d' ' -f3)

# List secrets:
vault kv list ea-secrets

# Read specific secret:
vault kv get ea-secrets/zitadel/admin
```

### OIDC Integration

Services integrated with Zitadel for SSO:
- ArgoCD - GitOps platform
- Grafana - Monitoring dashboards  
- Forgejo - Git repositories (optional)

### Network Security

- All services behind Traefik reverse proxy
- TLS termination at proxy level
- Service-to-service communication via Consul Connect
- Network isolation between service tiers

## Maintenance

### Regular Tasks

```bash
# Weekly health check:
./docker-health-check.sh full > health-report-$(date +%Y%m%d).txt

# Update container images:
docker-compose -f docker-compose-zot-registry.yml pull
docker-compose -f docker-compose-zot-registry.yml up -d

# Backup persistent volumes:
sudo tar -czf ea-backup-$(date +%Y%m%d).tar.gz /home/user/.local/share/containers/volumes/ea-persistent/_data

# Clean up logs:
docker system prune --force
```

### Performance Optimisation

```bash
# Monitor performance:
docker stats --no-stream > performance-$(date +%Y%m%d).txt

# Optimize resource allocation:
# Edit compose files to adjust memory limits
# Scale replicas for high-load services
```

## Support

### Documentation
- Service Dependencies: `SERVICE_DEPENDENCIES.md`
- Individual compose files contain service-specific documentation
- Health check endpoints documented in monitoring script

### Logs Location
- Startup logs: `/home/user/Code/startup.log`
- Container logs: `docker logs <container-name>`
- Service logs: Available through each compose file

### Common Commands

```bash
# Start platform:
./docker-compose-startup.sh start

# Stop platform:
./docker-compose-startup.sh stop

# Restart platform:
./docker-compose-startup.sh restart

# Check status:
./docker-health-check.sh status

# Monitor continuously:
./docker-health-check.sh watch

# Get service URLs:
./docker-health-check.sh urls

# Full platform overview:
./docker-health-check.sh full
```

This comprehensive startup system ensures reliable, secure, and well-monitored deployment of the complete Enterprise Architecture Platform with proper dependency management and health monitoring.