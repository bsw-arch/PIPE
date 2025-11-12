# Infrastructure as Code (IaC) - AXIS Task Bot

Complete declarative infrastructure for AXIS Task Bot deployment using:
- **Helm**: Kubernetes package management
- **Ansible**: Container orchestration & configuration
- **OpenTofu**: Infrastructure provisioning
- **OpenBao**: Secrets management

---

## 📁 Structure

```
iac/
├── helm/                       # Kubernetes Helm charts
│   ├── charts/
│   │   └── axis-patterns-bot/     # Main Helm chart
│   └── values/
│       ├── dev.yaml           # Development values
│       ├── staging.yaml       # Staging values
│       └── production.yaml    # Production values
│
├── ansible/                    # Ansible automation
│   ├── playbooks/
│   │   ├── deploy-containers.yml
│   │   ├── configure-openbao.yml
│   │   └── setup-registry.yml
│   ├── roles/
│   │   ├── axis-patterns-bot/
│   │   ├── openbao/
│   │   └── zot-registry/
│   └── inventory/
│       ├── dev.ini
│       └── production.ini
│
├── opentofu/                   # Infrastructure provisioning
│   ├── modules/
│   │   ├── k3s-cluster/
│   │   ├── container-registry/
│   │   └── openbao-setup/
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── production/
│
└── openbao/                    # Secrets management
    ├── policies/
    │   ├── axis-patterns-bot-policy.hcl
    │   └── ci-cd-policy.hcl
    └── secrets/
        └── secrets-template.yaml
```

---

## 🚀 Quick Start

### 1. Deploy with Helm (Kubernetes)
```bash
# Install Helm chart
helm install axis-patterns-bot ./iac/helm/charts/axis-patterns-bot \
  --values ./iac/helm/values/production.yaml \
  --namespace axis-bots \
  --create-namespace

# Verify deployment
kubectl get pods -n axis-bots
```

### 2. Deploy with Ansible (Podman)
```bash
# Deploy containers
ansible-playbook -i iac/ansible/inventory/production.ini \
  iac/ansible/playbooks/deploy-containers.yml

# Configure OpenBao
ansible-playbook -i iac/ansible/inventory/production.ini \
  iac/ansible/playbooks/configure-openbao.yml
```

### 3. Provision Infrastructure (OpenTofu)
```bash
# Initialize OpenTofu
cd iac/opentofu/environments/production
tofu init

# Plan infrastructure
tofu plan

# Apply infrastructure
tofu apply
```

### 4. Setup OpenBao Secrets
```bash
# Enable KV secrets engine
openbao secrets enable -path=axis-bots kv-v2

# Apply policies
openbao policy write axis-patterns-bot iac/openbao/policies/axis-patterns-bot-policy.hcl

# Store secrets
openbao kv put axis-bots/task-bot \
  keragr_url="http://localhost:3108" \
  coordination_url="http://localhost:3111"
```

---

## 🎯 Deployment Strategies

### Strategy 1: Full Kubernetes (Production)
```
OpenTofu → K3s Cluster
    ↓
Helm → Deploy containers to K8s
    ↓
OpenBao → Inject secrets
    ↓
AXIS Task Bot Running
```

### Strategy 2: Podman Containers (Development)
```
Ansible → Deploy Podman containers
    ↓
OpenBao → Inject secrets
    ↓
AXIS Task Bot Running
```

### Strategy 3: Hybrid (Staging)
```
OpenTofu → Infrastructure
    ↓
Ansible → Configure & deploy
    ↓
OpenBao → Secrets management
    ↓
AXIS Task Bot Running
```

---

## 🔐 OpenBao Integration

### Secrets Structure
```
axis-bots/
├── task-bot/
│   ├── keragr_url
│   ├── coordination_url
│   ├── api_key
│   └── encryption_key
├── task-scheduler/
│   └── scheduler_token
└── task-executor/
    └── executor_token
```

### Dynamic Secrets
OpenBao dynamically generates:
- API tokens (short-lived)
- Database credentials
- SSH keys for CI/CD

### Secret Injection Methods
1. **Kubernetes**: Vault Agent Injector
2. **Podman**: Environment variables via Ansible
3. **CI/CD**: Vault CLI in Woodpecker

---

## 🔄 CI/CD Integration

### Woodpecker Pipeline with OpenBao
```yaml
pipeline:
  secrets:
    image: openbao/openbao:latest
    commands:
      - openbao login -method=jwt token=$VAULT_TOKEN
      - export KERAGR_URL=$(openbao kv get -field=keragr_url axis-bots/task-bot)

  build:
    image: docker.io/library/docker:latest
    commands:
      - ./build/build-all.sh

  deploy:
    image: bitnami/helm:latest
    commands:
      - helm upgrade --install axis-patterns-bot ./iac/helm/charts/axis-patterns-bot
```

---

## 📊 Environment Configuration

### Development
- **Platform**: Podman containers
- **Orchestration**: Ansible
- **Secrets**: OpenBao (dev mode)
- **Registry**: Local Zot (localhost:5000)

### Staging
- **Platform**: K3s single-node
- **Orchestration**: Helm
- **Secrets**: OpenBao (HA mode)
- **Registry**: Private Zot

### Production
- **Platform**: K3s cluster (3+ nodes)
- **Orchestration**: Helm + GitOps
- **Secrets**: OpenBao (HA with raft storage)
- **Registry**: Replicated Zot

---

## 🛠️ Tools Required

### Core Tools
- `helm` (v3.12+)
- `ansible` (v2.15+)
- `opentofu` (v1.6+)
- `openbao` (v2.0+)

### Container Runtime
- `podman` or `kubectl` + `k3s`

### Optional
- `k9s` - Kubernetes TUI
- `lens` - Kubernetes IDE
- `vault-cli` - OpenBao CLI

---

## 📝 Configuration Management

### Helm Values Hierarchy
```
1. charts/axis-patterns-bot/values.yaml  (defaults)
2. values/dev.yaml                    (environment)
3. --set flags                        (runtime overrides)
```

### Ansible Variables Hierarchy
```
1. roles/axis-patterns-bot/defaults/main.yml  (defaults)
2. inventory/production.ini               (inventory vars)
3. playbooks/deploy-containers.yml        (playbook vars)
4. --extra-vars                           (runtime overrides)
```

### OpenTofu Variables
```
1. modules/*/variables.tf         (module inputs)
2. environments/*/terraform.tfvars (environment config)
3. -var flags                      (runtime overrides)
```

---

## 🔒 Security Best Practices

### Secrets Management
- ✅ Never commit secrets to Git
- ✅ Use OpenBao for all sensitive data
- ✅ Rotate secrets regularly (automated)
- ✅ Use short-lived tokens where possible

### Access Control
- ✅ OpenBao policies per service
- ✅ RBAC in Kubernetes
- ✅ Least privilege principle
- ✅ Audit logging enabled

### Encryption
- ✅ TLS for all communications
- ✅ Encrypted storage (OpenBao backend)
- ✅ Encrypted container images (Cosign)

---

## 📈 Monitoring & Observability

### Metrics (Prometheus)
```yaml
# Helm values
monitoring:
  enabled: true
  prometheus:
    scrape_interval: 15s
```

### Logging (Loki)
```yaml
# Helm values
logging:
  enabled: true
  loki:
    retention: 30d
```

### Tracing (Tempo)
```yaml
# Helm values
tracing:
  enabled: true
  tempo:
    sampling_rate: 0.1
```

---

## 🧪 Testing

### Test Helm Chart
```bash
# Lint chart
helm lint ./iac/helm/charts/axis-patterns-bot

# Dry run
helm install axis-patterns-bot ./iac/helm/charts/axis-patterns-bot \
  --dry-run --debug

# Template rendering
helm template axis-patterns-bot ./iac/helm/charts/axis-patterns-bot
```

### Test Ansible Playbooks
```bash
# Check syntax
ansible-playbook --syntax-check iac/ansible/playbooks/deploy-containers.yml

# Dry run
ansible-playbook -i iac/ansible/inventory/dev.ini \
  iac/ansible/playbooks/deploy-containers.yml \
  --check

# Run with verbose
ansible-playbook -i iac/ansible/inventory/dev.ini \
  iac/ansible/playbooks/deploy-containers.yml \
  -vvv
```

### Test OpenTofu
```bash
# Validate configuration
tofu validate

# Format check
tofu fmt -check

# Plan (no apply)
tofu plan
```

---

## 🎓 Best Practices

### Infrastructure as Code
1. **Version Everything**: Git for all IaC code
2. **Modular Design**: Reusable Helm/Ansible/Tofu modules
3. **Environment Parity**: Dev = Staging = Production
4. **Automated Testing**: Validate before apply
5. **GitOps**: Pull-based deployments with ArgoCD

### Secrets Management
1. **Never Hardcode**: Use OpenBao for all secrets
2. **Dynamic Secrets**: Generate on-demand where possible
3. **Rotation**: Automate secret rotation
4. **Audit**: Log all secret access
5. **Encryption**: At-rest and in-transit

---

## 📞 Troubleshooting

### Helm Issues
```bash
# Check release status
helm status axis-patterns-bot -n axis-bots

# View rendered manifests
helm get manifest axis-patterns-bot -n axis-bots

# Rollback
helm rollback axis-patterns-bot -n axis-bots
```

### Ansible Issues
```bash
# Verbose output
ansible-playbook -vvv ...

# Check connectivity
ansible all -i inventory/dev.ini -m ping

# Run specific tags
ansible-playbook ... --tags "deploy"
```

### OpenBao Issues
```bash
# Check status
openbao status

# View policies
openbao policy list

# Test secret access
openbao kv get axis-bots/task-bot
```

---

**Status**: Ready for implementation
**Stack**: Helm + Ansible + OpenTofu + OpenBao
**Target**: Fully automated, secure, reproducible deployments
**Security**: OpenBao-backed secrets, zero hardcoded credentials
