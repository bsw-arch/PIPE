# PIPE Infrastructure Architecture

## Overview

The PIPE Domain Bot System uses a modern, open-source infrastructure stack with enterprise-grade security and governance. This architecture explicitly uses open-source alternatives to proprietary HashiCorp products.

## Technology Stack

### Infrastructure as Code
- **OpenTofu** - Open-source Terraform alternative for infrastructure provisioning
- **Ansible** - Configuration management and automation

### Security & Identity
- **OpenBao** - Open-source Vault alternative for secrets management
- **Zitadel** - Open-source identity and access management (IAM)
- **Cosign** - Container image signing and verification

### Container & Registry
- **Zot** - OCI-native container registry
- **Helm** - Kubernetes package manager
- **Cilium** - eBPF-based networking and security

### Forbidden Technologies
❌ **HashiCorp Vault** - Use OpenBao instead
❌ **HashiCorp Consul** - Use native Kubernetes service discovery
❌ **HashiCorp Terraform** - Use OpenTofu instead

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Developer Workflow                        │
│  OpenTofu → Ansible → Helm → Kubernetes (Cilium CNI)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Security Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ OpenBao  │  │ Zitadel  │  │   Zot    │  │ Cosign   │       │
│  │ Secrets  │  │   IAM    │  │ Registry │  │  Sign    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                            │
│  ┌───────────────────────────────────────────────────┐          │
│  │              Cilium CNI (eBPF)                     │          │
│  │  - Network Policy Enforcement                      │          │
│  │  - Service Mesh                                    │          │
│  │  - Security Observability                          │          │
│  └───────────────────────────────────────────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ PIPE Bots    │  │  Governance  │  │  Monitoring  │         │
│  │  Namespace   │  │   Namespace  │  │   Namespace  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. OpenTofu (Infrastructure as Code)

**Purpose**: Provision and manage infrastructure resources

**Key Features**:
- Open-source Terraform fork (BUSL → MPL 2.0)
- Compatible with existing Terraform modules
- State management with backend support
- Declarative infrastructure definition

**Usage in PIPE**:
- Kubernetes cluster provisioning
- Network configuration
- Storage provisioning
- Service dependencies

### 2. OpenBao (Secrets Management)

**Purpose**: Centralized secrets management and encryption

**Key Features**:
- Open-source Vault fork (BUSL → MPL 2.0)
- Dynamic secrets generation
- Encryption as a service
- PKI/Certificate management
- Kubernetes integration via injector

**Secrets Managed**:
- Database credentials
- API keys and tokens
- TLS certificates
- Signing keys
- OAuth client secrets

**Integration Points**:
- PIPE bots fetch secrets at runtime
- Kubernetes secret injection via init containers
- Dynamic database credentials with TTL
- Certificate rotation automation

### 3. Zitadel (Identity & Access Management)

**Purpose**: Authentication and authorization

**Key Features**:
- Multi-tenancy support
- OAuth 2.0 / OIDC provider
- SAML 2.0 support
- User management
- API authentication
- Fine-grained RBAC

**PIPE Integration**:
- Domain-based multi-tenancy (9 domains)
- Service account authentication
- API gateway authentication
- Governance approval workflows
- User identity for audit trails

**Roles**:
- `domain-admin` - Domain-level administration
- `integration-reviewer` - Review integration requests
- `compliance-auditor` - Read-only compliance access
- `bot-operator` - Bot management permissions
- `governance-admin` - Full governance access

### 4. Zot (Container Registry)

**Purpose**: OCI-native container registry

**Key Features**:
- OCI Distribution Spec compliant
- Minimal resource footprint
- Built-in vulnerability scanning
- Storage deduplication
- Signature verification

**PIPE Usage**:
- Store PIPE bot images
- Integration with Cosign for signing
- Vulnerability scanning before deployment
- Image promotion pipeline

**Registry Structure**:
```
zot.pipe.local/
├── pipe/
│   ├── pipeline-bot:latest
│   ├── data-processor-bot:latest
│   ├── monitor-bot:latest
│   └── integration-hub-bot:latest
├── governance/
│   └── governance-manager:latest
└── monitoring/
    └── metrics-exporter:latest
```

### 5. Cosign (Image Signing)

**Purpose**: Container image signing and verification

**Key Features**:
- Keyless signing with OIDC
- Kubernetes admission control
- Supply chain security (SLSA)
- Transparency log integration

**PIPE Implementation**:
- Sign all production images
- Verify signatures at deployment
- Admission webhook enforcement
- Audit trail for image provenance

**Signing Workflow**:
```bash
# Build image
docker build -t zot.pipe.local/pipe/pipeline-bot:v1.0.0 .

# Sign with Cosign
cosign sign --key cosign.key zot.pipe.local/pipe/pipeline-bot:v1.0.0

# Verify before deployment
cosign verify --key cosign.pub zot.pipe.local/pipe/pipeline-bot:v1.0.0
```

### 6. Cilium (Networking & Security)

**Purpose**: eBPF-based Kubernetes networking

**Key Features**:
- CNI plugin
- Network policy enforcement
- Service mesh capabilities
- Security observability
- Cluster mesh for multi-cluster
- Hubble for network visibility

**PIPE Configuration**:
- Network policies per namespace
- Domain-based segmentation
- East-west traffic encryption
- API-aware network filtering
- Integration monitoring

**Network Policies**:
```yaml
# Allow PIPE hub to communicate with all domains
# Restrict domain-to-domain direct communication
# Enforce governance approval flow
```

### 7. Helm (Package Management)

**Purpose**: Kubernetes application deployment

**PIPE Helm Charts**:
- `pipe-core` - Core infrastructure (OpenBao, Zitadel)
- `pipe-bots` - Bot deployments
- `pipe-governance` - Governance components
- `pipe-monitoring` - Observability stack

**Chart Structure**:
```
charts/
├── pipe-core/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── pipe-bots/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
└── pipe-governance/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
```

### 8. Ansible (Configuration Management)

**Purpose**: Automation and orchestration

**Playbooks**:
- `setup-cluster.yml` - Kubernetes cluster setup
- `deploy-infrastructure.yml` - Deploy core services
- `deploy-pipe.yml` - Deploy PIPE system
- `backup-state.yml` - Backup OpenBao and state
- `rotate-secrets.yml` - Secret rotation automation

**Inventory Structure**:
```ini
[kubernetes_master]
k8s-master-01
k8s-master-02
k8s-master-03

[kubernetes_workers]
k8s-worker-01
k8s-worker-02
k8s-worker-03

[infrastructure]
openbao-01
zitadel-01
zot-registry-01
```

## Deployment Workflow

### 1. Infrastructure Provisioning (OpenTofu)

```bash
cd infrastructure/opentofu
tofu init
tofu plan -out=tfplan
tofu apply tfplan
```

### 2. Cluster Configuration (Ansible)

```bash
cd infrastructure/ansible
ansible-playbook -i inventory/production setup-cluster.yml
ansible-playbook -i inventory/production deploy-infrastructure.yml
```

### 3. Application Deployment (Helm)

```bash
# Install core infrastructure
helm install pipe-core charts/pipe-core/ -n pipe-system --create-namespace

# Install PIPE bots
helm install pipe-bots charts/pipe-bots/ -n pipe --create-namespace

# Install governance
helm install pipe-governance charts/pipe-governance/ -n pipe
```

## Security Architecture

### Secret Management Flow

```
Developer → OpenBao CLI → OpenBao Server → Kubernetes Secret
                                              ↓
                                         Pod Init Container
                                              ↓
                                         Application Pod
```

### Authentication Flow

```
User/Service → Zitadel (OAuth/OIDC) → Token → API Gateway → PIPE Service
                                                                  ↓
                                                           Verify with Zitadel
```

### Image Deployment Flow

```
Build → Sign (Cosign) → Push to Zot → Admission Webhook Verify → Deploy
                                             ↓
                                        Reject if not signed
```

## Network Security (Cilium)

### Network Segmentation

```yaml
# Domain Isolation
BNI Domain ←→ PIPE Hub ←→ BNP Domain
    ↕                        ↕
    ✗ Direct communication blocked
    ✓ Via PIPE Hub only
```

### Network Policies

1. **Default Deny**: All namespaces start with deny-all
2. **PIPE Hub**: Can communicate with all domain namespaces
3. **Domain Namespaces**: Can only communicate with PIPE Hub
4. **Governance**: Separate network zone with audit logging
5. **Monitoring**: Read-only access via Cilium Hubble

## High Availability

### OpenBao HA

- 3-node Raft cluster
- Auto-unseal with Kubernetes secrets
- Automated backup to S3-compatible storage
- Disaster recovery procedures

### Zitadel HA

- PostgreSQL backend with replication
- Multiple replicas (min 2)
- Session persistence
- Backup and restore automation

### Zot HA

- S3-compatible backend storage
- Multiple registry replicas
- Load balancing
- Image replication

## Monitoring & Observability

### Metrics (Prometheus + Grafana)

- OpenBao metrics
- Zitadel authentication metrics
- Cilium network metrics
- PIPE bot metrics
- Governance approval metrics

### Logging (Loki + Promtail)

- Centralized log aggregation
- Structured logging from all components
- Audit trail for governance actions
- Security event logging

### Tracing (Jaeger)

- Distributed tracing across services
- Integration request flow tracking
- Performance bottleneck identification

### Network Visibility (Hubble)

- Layer 7 visibility
- Service dependency maps
- Network policy testing
- Security event detection

## Compliance & Governance

### Audit Logging

All actions logged:
- OpenBao secret access
- Zitadel authentication events
- Governance approval/rejection
- Integration requests
- Network policy changes

### Encryption

- Secrets encrypted at rest (OpenBao)
- Network traffic encrypted (Cilium)
- Image content trust (Cosign)
- TLS everywhere

### Access Control

- RBAC in Kubernetes
- Zitadel role-based access
- Cilium network policies
- OpenBao policy enforcement

## Disaster Recovery

### Backup Strategy

1. **OpenBao**: Daily snapshots to S3
2. **Zitadel DB**: Continuous replication + daily dumps
3. **Zot**: S3 backend (already replicated)
4. **OpenTofu State**: Remote backend with versioning
5. **Kubernetes State**: Velero backups

### Recovery Time Objectives (RTO)

- OpenBao: < 15 minutes
- Zitadel: < 30 minutes
- PIPE Bots: < 10 minutes
- Full System: < 1 hour

## Cost Optimization

All components are **open-source and free**:
- No vendor lock-in
- No licensing costs
- Community support
- Self-hosted control

## Migration from HashiCorp

### Vault → OpenBao

- 100% API compatible
- Direct migration path
- Same HCL configuration
- Plugin compatibility

### Terraform → OpenTofu

- Drop-in replacement
- Same state format
- Module compatibility
- Provider compatibility

### Consul → Kubernetes Native

- Service discovery via Kubernetes DNS
- Configuration via ConfigMaps/Secrets
- Health checks via readiness/liveness probes
- Service mesh via Cilium

## References

- [OpenTofu Documentation](https://opentofu.org/docs/)
- [OpenBao Documentation](https://openbao.org/docs/)
- [Zitadel Documentation](https://zitadel.com/docs)
- [Zot Documentation](https://zotregistry.io/)
- [Cosign Documentation](https://docs.sigstore.dev/cosign/)
- [Cilium Documentation](https://docs.cilium.io/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Helm Documentation](https://helm.sh/docs/)

## Next Steps

1. Provision infrastructure with OpenTofu
2. Configure OpenBao for secrets
3. Deploy Zitadel for IAM
4. Set up Zot registry with Cosign
5. Install Cilium CNI
6. Deploy PIPE with Helm
7. Configure monitoring and observability
