# BSW-ARCH Service Dependencies Analysis
> **High Availability Architecture** for Dutch Ministry of Finance

## Service Dependency Map

### Tier 1: Infrastructure Foundation (HA Services)
```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   Vault HA Cluster  │    │  PostgreSQL HA       │    │ Zot Registry    │
│ bsw-arch-vault-{1,2,3}│    │ bsw-arch-postgresql- │    │     :5000       │
│    Ports: 3200-3202 │    │ {node-1,2,3}         │    │ (Containers)    │
│   (Secrets + Config)│    │ Ports: 5432,5433     │    │                 │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                        ┌────────────▼────────────┐
                        │   BSW Application       │
                        │   Services Layer        │
                        │ (Dependencies Met)      │
                        └─────────────────────────┘
```

### Tier 2: Networking & Service Discovery
```
┌─────────────────┐    ┌──────────────────┐
│ Consul Service  │    │ Traefik Reverse  │
│   Discovery     │    │     Proxy        │
│ 8500,8600,8502  │◄──►│  80,443,8080     │
│                 │    │                  │
└─────────────────┘    └──────────────────┘
         │                       │
         └───────────────────────┼───────────────────────┐
                                 │                       │
                    ┌────────────▼─────┐    ┌───────────▼────┐
                    │   All Web Apps   │    │  Load Balancing │
                    │ (Service Mesh)   │    │   & Routing     │
                    └──────────────────┘    └────────────────┘
```

### Tier 3: Identity & Access Management
```
┌─────────────────┐    depends on    ┌──────────────────┐
│   PostgreSQL    │◄─────────────────│   Zitadel IAM    │
│     5432        │                  │   8082, 8444     │
│   (Database)    │                  │     (OIDC)       │
└─────────────────┘                  └──────────────────┘
         │                                    │
         └────────────────┐                   │
                          │                   │
                    ┌─────▼───────────────────▼─────┐
                    │    All Authenticated Apps     │
                    │ (ArgoCD, Grafana, Forgejo)    │
                    └───────────────────────────────┘
```

### Tier 4: Application Services

#### GitOps Stack
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Forgejo      │    │   Woodpecker     │    │     ArgoCD      │
│   Git Server    │◄──►│      CI          │───►│   GitOps        │
│   3000, 3001    │    │     8000         │    │   8081, 8443    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     Jenkins CI/CD       │
                    │    8080 (alternate)     │
                    └─────────────────────────┘
```

#### Hybrid Architects Platform
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Digital       │    │   Biological     │    │     Hybrid      │
│ Architects      │◄──►│   Architects     │◄──►│ Orchestrator    │
│   8083          │    │     8084         │    │    8085         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Archi Collaborative   │
                    │        8090             │
                    └─────────────────────────┘
```

### Tier 5: Security & Monitoring

#### DevSecOps Pipeline
```
Code Security          Build Security         Deploy Security        Monitor Security
┌─────────────┐       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Gitleaks   │──────►│   Trivy     │──────►│   Nuclei    │──────►│  Grafana    │
│  Semgrep    │       │   Syft      │       │ OWASP ZAP   │       │ 3000, 3001  │
│ SonarQube   │       │   Grype     │       │             │       │             │
│   9000      │       │             │       │             │       └─────────────┘
└─────────────┘       └─────────────┘       └─────────────┘               │
                                                                           │
                              ┌─────────────┐       ┌─────────────┐       │
                              │ Prometheus  │◄──────│    Loki     │◄──────┘
                              │ 9090, 9091  │       │ 3100, 3101  │
                              │  (Metrics)  │       │   (Logs)    │
                              └─────────────┘       └─────────────┘
```

### Tier 6: Specialised Services

#### Knowledge Management (BSW KERAG-R)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     Neo4j       │    │     Qdrant       │    │   KERAG-R       │
│ Knowledge Graph │◄──►│ Vector Database  │◄──►│   Frontend      │
│ 7474, 7687      │    │  6333, 6334      │    │    3003         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Hybrid Search API       │
                    │       8001              │
                    └─────────────────────────┘
```

## Port Allocation Matrix

| Service | Primary Port | Alternative Port | Protocol | Health Check Endpoint |
|---------|-------------|------------------|----------|----------------------|
| **Infrastructure** |
| Vault | 8200 | - | HTTP | `/v1/sys/health` |
| Zot Registry | 5000 | - | HTTP | `/v2/` |
| PostgreSQL | 5432 | - | TCP | pg_isready |
| **Networking** |
| Consul | 8500 | 8600 (DNS), 8502 (gRPC) | HTTP/UDP | `/v1/status/leader` |
| Traefik | 80, 443, 8080 | - | HTTP/HTTPS | `/api/rawdata` |
| **Identity** |
| Zitadel | 8082 | 8444 (gRPC) | HTTP | `/debug/ready` |
| **GitOps** |
| Forgejo | 3000 | 3001 | HTTP | `/api/healthz` |
| ArgoCD | 8081 | 8443, 8445 | HTTP/gRPC | `/healthz` |
| Woodpecker CI | 8000 | - | HTTP | `/` |
| Jenkins | 8080 | 8081 | HTTP | `/` |
| **Security** |
| SonarQube | 9000 | - | HTTP | `/api/system/status` |
| OWASP ZAP | 8080 | - | HTTP | N/A |
| **Monitoring** |
| Grafana | 3000 | 3001 | HTTP | `/api/health` |
| Prometheus | 9090 | 9091 | HTTP | `/-/ready` |
| Loki | 3100 | 3101 | HTTP | `/ready` |
| **Specialised** |
| Neo4j | 7474, 7687 | - | HTTP/Bolt | `/db/system/` |
| Qdrant | 6333, 6334 | - | HTTP/gRPC | `/health` |
| Archi Collab | 8090 | - | HTTP | N/A |

## Network Isolation Strategy

### Network Segments
```
ea-integrated-network (172.22.0.0/16)
├── Gateway: Traefik Reverse Proxy
├── Core Services: Vault, PostgreSQL, Zitadel
├── GitOps: Forgejo, ArgoCD, Woodpecker
└── Applications: All business services

ea-service-mesh (Bridge)
├── Consul Service Discovery
├── Service-to-service communication
└── Load balancing and routing

ea-bsw-network (Bridge)  
├── Neo4j Knowledge Graph
├── Qdrant Vector Database
└── KERAG-R Services

devsecops-network (172.20.0.0/16)
├── Security scanning tools
├── Monitoring services
└── DevSecOps pipeline
```

## Volume Dependencies

### External Volumes Required
```bash
# Create these before starting services:
docker volume create ea-vault-data
docker volume create ea-persistent

# Host directories:
/home/user/.local/share/containers/volumes/ea-persistent/_data
/var/lib/neo4j-bsw
/var/lib/neo4j-bsw-logs
/var/lib/neo4j-bsw-import
/var/lib/vault-bsw
```

### Volume Mapping
- `ea-persistent`: Shared persistent storage for all services
- `ea-vault-data`: Vault backend storage
- Service-specific volumes: Database data, logs, configurations

## Startup Sequence Optimisation

### Recommended Boot Order

1. **Prerequisites** (0-30 seconds)
   - Create external volumes
   - Ensure Docker is running
   - Verify compose files exist

2. **Tier 1: Infrastructure** (30-60 seconds)
   - Vault secrets management
   - Zot container registry
   - Wait for health checks

3. **Tier 2: Networking** (60-90 seconds)
   - Consul service discovery
   - Traefik reverse proxy
   - Service mesh initialisation

4. **Tier 3: Identity** (90-150 seconds)
   - PostgreSQL databases
   - Zitadel IAM system
   - OIDC configuration

5. **Tier 4: Applications** (150-300 seconds)
   - Forgejo git server
   - Woodpecker CI/CD
   - ArgoCD GitOps
   - Jenkins CI/CD
   - Hybrid architects platform

6. **Tier 5: Security & Monitoring** (300-450 seconds)
   - DevSecOps security tools
   - Prometheus metrics
   - Grafana dashboards
   - Log aggregation

7. **Tier 6: Specialised** (450+ seconds)
   - Neo4j knowledge graph
   - Qdrant vector database
   - KERAG-R knowledge management

### Health Check Timeouts
- **Critical services**: 60 seconds (Zitadel, SonarQube)
- **Standard services**: 30 seconds (ArgoCD, Forgejo)
- **Fast services**: 15-20 seconds (Vault, Traefik, registries)

## Conflict Resolution

### Port Conflicts
- Use alternate ports where specified
- Implement proper service discovery via Consul
- Configure Traefik routing for web services

### Service Naming
- Unique container names across all compose files
- Consistent network naming
- Clear service labelling

### Resource Management
- Health checks prevent cascade failures
- Graceful degradation for non-critical services
- Resource limits where appropriate

## Security Considerations

### Network Security
- All services behind Traefik reverse proxy
- OIDC authentication via Zitadel
- TLS termination at proxy level

### Secrets Management
- All secrets stored in HashiCorp Vault
- No hardcoded passwords in compose files
- Secure secret injection via vault sidecars

### Container Security
- Chainguard security-hardened base images
- Distroless containers where possible
- Regular security scanning via DevSecOps pipeline

This comprehensive analysis provides the foundation for a robust, secure, and properly orchestrated enterprise architecture platform deployment.