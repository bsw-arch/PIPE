# PIPE Cloud-Native Stack

**Complete infrastructure stack aligned with EuroStack digital sovereignty principles**

## Overview

PIPE uses a comprehensive **27-technology** open-source stack across 7 capability layers. Every component is carefully selected for:

- ✅ **100% Open-Source** - No proprietary licenses
- ✅ **EuroStack Aligned** - European digital sovereignty
- ✅ **CNCF Ecosystem** - 8 CNCF projects (6 graduated)
- ✅ **Production-Ready** - Battle-tested at scale
- ✅ **No HashiCorp** - Independent from US tech giants

---

## Complete Stack (27 Technologies)

### 🔨 Development & Collaboration (3)

| Technology | Purpose | License | Status |
|------------|---------|---------|--------|
| **OpenSpec** | Spec-driven development methodology | MIT | ✅ Integrated |
| **PR-QUEST** | Interactive PR review with LLM analysis | MIT | ✅ Integrated |
| **Cognee** | AI memory and knowledge graph | MIT | ✅ Integrated |

### 📦 Container Tooling (4)

| Technology | Purpose | License | CNCF |
|------------|---------|---------|------|
| **Podman** | Daemonless container runtime (replaces Docker) | Apache 2.0 | - |
| **Buildah** | OCI image building without daemon | Apache 2.0 | - |
| **Skopeo** | Container image operations | Apache 2.0 | - |
| **Cosign** | Container image signing | Apache 2.0 | - |

**Why not Docker?**
- Docker Desktop requires paid licenses for companies >250 employees
- Podman is daemonless and more secure (rootless by default)
- Buildah provides more control over image building
- Full OCI compatibility

### 🔐 Security & Identity (5)

| Technology | Purpose | License | CNCF |
|------------|---------|---------|------|
| **OpenBao** | Secrets management (Vault fork) | MPL 2.0 | - |
| **Zitadel** | Identity and access management | Apache 2.0 | - |
| **Trivy** | Comprehensive vulnerability scanner | Apache 2.0 | - |
| **Syft** | SBOM (Software Bill of Materials) generation | Apache 2.0 | - |
| **Grype** | Alternative vulnerability scanner | Apache 2.0 | - |

**Security Scanning Coverage:**
- Container images (OS packages + dependencies)
- Infrastructure as Code (OpenTofu, Kubernetes)
- Git repositories (secrets detection)
- SBOMs (CycloneDX, SPDX)

### 📡 Networking & Service Mesh (2)

| Technology | Purpose | License | CNCF |
|------------|---------|---------|------|
| **Cilium** | eBPF-based CNI with network policies | Apache 2.0 | ✅ Graduated |
| **Zot** | OCI-native container registry | Apache 2.0 | - |

**Cilium Features:**
- eBPF-based networking (fastest CNI)
- Network policies (micro-segmentation)
- Service mesh capabilities
- Hubble observability

### 📊 Observability - LGTM Stack (4)

| Technology | Purpose | License | CNCF |
|------------|---------|---------|------|
| **Prometheus** | Metrics collection and alerting | Apache 2.0 | ✅ Graduated |
| **Grafana** | Visualization and dashboards | AGPL 3.0 | - |
| **Loki** | Log aggregation (like Prometheus for logs) | AGPL 3.0 | - |
| **Tempo** | Distributed tracing | AGPL 3.0 | - |

**LGTM Stack Benefits:**
- **L**oki - Lightweight log aggregation
- **G**rafana - Unified visualization
- **T**empo - Distributed tracing
- **M**etrics (Prometheus) - Industry standard

**PIPE Dashboards:**
1. Bot Health - All 5 bots status, uptime, errors
2. Governance - Integration approvals, review times
3. PR Review - PR-QUEST analysis, risk distribution
4. Cognee AI - Memory usage, query performance
5. Infrastructure - Kubernetes cluster health

### 🚀 GitOps & Automation (3)

| Technology | Purpose | License | CNCF |
|------------|---------|---------|------|
| **ArgoCD** | Declarative GitOps continuous delivery | Apache 2.0 | ✅ Graduated |
| **OpenTofu** | Infrastructure as Code (Terraform fork) | MPL 2.0 | - |
| **Ansible** | Configuration management | GPL 3.0 | - |

**GitOps Workflow:**
```
Developer commits → Git (source of truth)
                    ↓
                ArgoCD detects change
                    ↓
                Auto-sync to Kubernetes
                    ↓
                PIPE deployed
```

### 🛡️ Policy & Compliance (3)

| Technology | Purpose | License | CNCF |
|------------|---------|---------|------|
| **OPA** | General-purpose policy engine | Apache 2.0 | ✅ Graduated |
| **Kyverno** | Kubernetes-native policy management | Apache 2.0 | ✅ Incubating |
| **Helm** | Kubernetes package manager | Apache 2.0 | ✅ Graduated |

**Policy Examples:**
- ✅ Only signed images allowed (Cosign verification)
- ✅ No HashiCorp images permitted
- ✅ Integration PRs must pass PR-QUEST review
- ✅ Resource limits required on all pods
- ✅ Labels required for cost tracking

### 💾 Storage & Data (2)

| Technology | Purpose | License | CNCF |
|------------|---------|---------|------|
| **Longhorn** | Distributed block storage for Kubernetes | Apache 2.0 | ✅ Sandbox |
| **MinIO** | S3-compatible object storage | AGPL 3.0 | - |

**Storage Strategy:**
- **Longhorn** - Persistent volumes for bot state, databases
- **MinIO** - Object storage for PR cache, governance docs, backups

### 🔄 Backup & Disaster Recovery (1)

| Technology | Purpose | License | CNCF |
|------------|---------|---------|------|
| **Velero** | Kubernetes backup and restore | Apache 2.0 | ✅ Graduated |

**Backup Schedule:**
- Daily backups at 2 AM
- 7-day retention
- Backs up: All bots, secrets, Cognee data, governance records
- Storage: MinIO
- RTO (Recovery Time Objective): 30 minutes
- RPO (Recovery Point Objective): 24 hours

---

## CNCF Projects in PIPE

### Graduated (6)
1. ✅ Prometheus - Metrics
2. ✅ ArgoCD - GitOps
3. ✅ OPA - Policy
4. ✅ Helm - Package management
5. ✅ Cilium - Networking
6. ✅ Velero - Backup

### Incubating (1)
7. ✅ Kyverno - Kubernetes policy

### Sandbox (1)
8. ✅ Longhorn - Storage

**Total CNCF Projects: 8/27 (30%)**

---

## Architecture Layers

```
┌──────────────────────────────────────────────────────────┐
│                   Layer 7: Development                    │
│   OpenSpec │ PR-QUEST │ Cognee                           │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   Layer 6: GitOps                         │
│   ArgoCD (Continuous Delivery)                           │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   Layer 5: Policy                         │
│   OPA │ Kyverno │ Cosign                                 │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   Layer 4: Application                    │
│   5 PIPE Bots │ Zitadel │ OpenBao                        │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   Layer 3: Platform                       │
│   Kubernetes │ Cilium │ Podman │ Longhorn │ MinIO        │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   Layer 2: Observability                  │
│   Prometheus │ Grafana │ Loki │ Tempo                    │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   Layer 1: Infrastructure                 │
│   OpenTofu │ Ansible │ Helm │ Trivy │ Velero             │
└──────────────────────────────────────────────────────────┘
```

---

## Technology Selection Criteria

Every technology in the PIPE stack was evaluated against these criteria:

### 1. Open-Source ✅
- **Must Have**: OSI-approved license
- **Preferred**: Apache 2.0, MIT, MPL 2.0
- **Acceptable**: AGPL 3.0 (for standalone services)
- **Forbidden**: Proprietary, SSPL, Business Source License

### 2. Production-Ready ✅
- **Must Have**: Used in production by >100 companies
- **Preferred**: CNCF Graduated or Incubating
- **Bonus**: Fortune 500 adoption

### 3. Active Maintenance ✅
- **Must Have**: Commits in last 30 days
- **Must Have**: Active security patches
- **Preferred**: Releases every 3 months
- **Preferred**: Vibrant community

### 4. European Alignment ✅
- **Preferred**: European-founded or European-focused
- **Must Have**: No US government dependencies
- **Must Have**: No cloud provider lock-in
- **Bonus**: EuroStack member

### 5. Integration Quality ✅
- **Must Have**: Kubernetes-native or excellent K8s support
- **Preferred**: Helm charts available
- **Preferred**: Prometheus metrics
- **Bonus**: ArgoCD-compatible

---

## EuroStack Principles Alignment

### Digital Sovereignty ✅
- **No HashiCorp** - US company, license changes
- **No Docker Inc** - Proprietary licensing
- **Self-Hosted** - All components run in our infrastructure
- **Data Residency** - All data stays in Europe

### Open-Source First ✅
- **27/27 technologies** are open-source
- **15/27 technologies** have Apache 2.0 license
- **8/27 technologies** are CNCF projects
- **0 proprietary** components

### Green Computing ✅
- **eBPF** (Cilium) - Efficient networking
- **Podman** - Lower resource usage than Docker
- **Loki** - Lightweight log aggregation
- **Prometheus** - Efficient time-series storage

### Community-Driven ✅
- All technologies have active communities
- Contributing back to upstream projects
- Sponsoring CNCF projects
- Supporting European open-source initiatives

---

## Deployment Architecture

### Production Deployment

```yaml
# Kubernetes Cluster (3 nodes minimum)
Master Nodes (3):
  - Control plane (HA)
  - etcd cluster
  - ArgoCD

Worker Nodes (5+):
  - PIPE bots (5 deployments)
  - Observability stack (Prometheus, Grafana, Loki, Tempo)
  - Security stack (Trivy, OPA, Kyverno)
  - Storage (Longhorn, MinIO)
  - Identity (Zitadel, OpenBao)
  - Registry (Zot)

# Resource Allocation
Total CPU: 20 cores
Total Memory: 64 GB
Total Storage: 500 GB SSD

# High Availability
- 3 replicas for critical components
- Longhorn replication factor: 3
- MinIO distributed mode: 4 servers
- Prometheus retention: 30 days
- Velero backups: Daily
```

### Development Environment

```bash
# Minikube or kind for local development
minikube start --cpus 4 --memory 8192 --driver podman

# Deploy PIPE stack
kubectl create namespace pipe-dev
helm install pipe-stack charts/pipe-bots/ -n pipe-dev

# Access services
kubectl port-forward -n pipe-dev svc/grafana 3000:3000
kubectl port-forward -n pipe-dev svc/argocd-server 8080:443
```

---

## Cost Comparison

### Before Enhanced Stack
- **Infrastructure**: $500/month (Kubernetes)
- **Monitoring**: $200/month (Cloud provider)
- **Storage**: $100/month (Cloud volumes)
- **Backup**: $50/month (Cloud snapshots)
- **Total**: $850/month

### After Enhanced Stack
- **Infrastructure**: $500/month (Kubernetes - unchanged)
- **Monitoring**: $0/month (Self-hosted LGTM stack)
- **Storage**: $0/month (Longhorn + MinIO included)
- **Backup**: $0/month (Velero + MinIO)
- **Total**: $500/month

**Annual Savings**: $4,200
**ROI**: 100% after setup costs recovered

---

## Migration Path

### Phase 1: Container Tooling (Week 1)
```bash
# Replace Docker with Podman
sudo apt remove docker-ce
sudo apt install podman buildah skopeo

# Update CI/CD
sed -i 's/docker/podman/g' .github/workflows/*.yml

# Test builds
podman build -t test-image .
podman run test-image
```

### Phase 2: Observability (Weeks 2-3)
```bash
# Deploy Prometheus stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# Deploy Loki
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack -n monitoring

# Deploy Tempo
helm install tempo grafana/tempo -n monitoring
```

### Phase 3: Security (Week 4)
```bash
# Deploy Trivy operator
helm repo add aqua https://aquasecurity.github.io/helm-charts/
helm install trivy-operator aqua/trivy-operator -n trivy-system

# Scan all images
trivy image --severity HIGH,CRITICAL zot.pipe.local/pipe/pipeline-bot:latest
```

### Phase 4: Storage (Week 5)
```bash
# Deploy Longhorn
helm repo add longhorn https://charts.longhorn.io
helm install longhorn longhorn/longhorn -n longhorn-system

# Deploy MinIO
helm repo add minio https://charts.min.io/
helm install minio minio/minio -n minio-system
```

### Phase 5: GitOps (Week 6)
```bash
# Deploy ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### Phase 6: Policy (Week 7)
```bash
# Deploy OPA
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm install gatekeeper gatekeeper/gatekeeper -n gatekeeper-system

# Deploy Kyverno
helm repo add kyverno https://kyverno.github.io/kyverno/
helm install kyverno kyverno/kyverno -n kyverno
```

### Phase 7: Backup (Week 8)
```bash
# Deploy Velero
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm install velero vmware-tanzu/velero -n velero \
  --set configuration.provider=aws \
  --set configuration.backupStorageLocation.bucket=pipe-backups \
  --set configuration.backupStorageLocation.config.region=minio \
  --set configuration.backupStorageLocation.config.s3ForcePathStyle=true \
  --set configuration.backupStorageLocation.config.s3Url=http://minio.minio-system.svc:9000
```

---

## Troubleshooting

### Common Issues

**Podman not starting containers**
```bash
# Check rootless mode
podman info | grep rootless

# Fix permissions
sudo sysctl -w kernel.unprivileged_userns_clone=1
```

**Prometheus not scraping metrics**
```bash
# Check ServiceMonitor
kubectl get servicemonitor -A

# Verify labels
kubectl get svc <service> -o yaml | grep prometheus
```

**Trivy scan failing**
```bash
# Update vulnerability database
trivy image --download-db-only

# Check connectivity
trivy image --debug zot.pipe.local/image:latest
```

**ArgoCD not syncing**
```bash
# Check Application status
kubectl get application -n argocd

# Force refresh
argocd app sync <app-name> --force
```

---

## Monitoring & Alerts

### Critical Alerts

```yaml
groups:
  - name: pipe-critical
    rules:
      - alert: BotDown
        expr: up{job="pipe-bot"} == 0
        for: 5m
        annotations:
          summary: "PIPE bot {{ $labels.bot_name }} is down"

      - alert: HighErrorRate
        expr: rate(pipe_bot_errors_total[5m]) > 0.1
        for: 10m
        annotations:
          summary: "High error rate in {{ $labels.bot_name }}"

      - alert: LonghorStorageLow
        expr: longhorn_volume_actual_size_bytes / longhorn_volume_capacity_bytes > 0.85
        for: 15m
        annotations:
          summary: "Longhorn volume {{ $labels.volume }} is 85% full"

      - alert: VeleroBackupFailed
        expr: velero_backup_failure_total > 0
        annotations:
          summary: "Velero backup failed"
```

---

## Resources

### Documentation
- [OpenSpec Guide](./OPENSPEC_GUIDE.md)
- [Infrastructure Setup](./INFRASTRUCTURE.md)
- [Cognee Integration](./COGNEE_INTEGRATION.md)
- [PR-QUEST Integration](./PR_QUEST_INTEGRATION.md)

### External Links
- **EuroStack**: https://euro-stack.info/
- **CNCF Landscape**: https://landscape.cncf.io/
- **Podman**: https://podman.io/
- **Prometheus**: https://prometheus.io/
- **ArgoCD**: https://argo-cd.readthedocs.io/
- **Trivy**: https://aquasecurity.github.io/trivy/
- **OPA**: https://www.openpolicyagent.org/
- **Velero**: https://velero.io/

---

**Last Updated**: 2025-01-17
**Stack Version**: 2.0 (27 technologies)
**Compliance**: EuroStack-aligned, 100% open-source
**CNCF Projects**: 8 (6 graduated, 1 incubating, 1 sandbox)
