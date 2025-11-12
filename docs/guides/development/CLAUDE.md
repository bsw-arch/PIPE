# CLAUDE.md - BSW Infrastructure Repository

This file provides guidance for working with the BSW Infrastructure repository following the BSW-Tech feature branching strategy.

## Forbidden Technologies (FAGAM + HashiCorp)

**MANDATORY: The following technologies are FORBIDDEN and must NEVER be used or referenced:**

### FAGAM Companies (Forbidden)
- **Facebook/Meta** - All products and services
- **Apple** - All products and services
- **Google/Alphabet** - All products and services
- **Amazon/AWS** - All products and services
- **Microsoft/Azure** - All products and services

### HashiCorp (Forbidden)
- **Terraform** - Use OpenTofu instead
- **Vault** - Use OpenBao instead
- **Consul** - Use alternative service mesh
- **Nomad** - Use Kubernetes/K3s instead
- **Packer** - Use apko/melange instead
- **Vagrant** - Use Podman/Docker Compose instead
- **Waypoint** - Use Woodpecker CI/Argo CD instead

### Compliance Standard
- **EuroStack.eu** - The authoritative standard for European cloud infrastructure
- **Comply or Explain** - Any deviation from EuroStack requires documented justification

### Approved Alternatives
- **Infrastructure as Code**: OpenTofu (Terraform fork)
- **Secrets Management**: OpenBao (Vault fork)
- **Container Orchestration**: Kubernetes, K3s
- **CI/CD**: Woodpecker CI, Argo CD, Flux
- **Service Mesh**: Linkerd, Istio (non-Google fork)
- **Container Images**: apko, melange, Wolfi OS

---

## BSW-Tech Feature Branching Strategy

**MANDATORY: Every new feature requires a new branch starting with `bsw-tech-`**

### Branch Naming Convention
```bash
# BSW-Tech Feature branches (MANDATORY PREFIX)
feature/bsw-tech-infrastructure-001-zitadel-iac
feature/bsw-tech-devops-002-woodpecker-ci
feature/bsw-tech-security-003-openbao-integration
feature/bsw-tech-containers-004-chainguard-migration
feature/bsw-tech-monitoring-005-grafana-setup

# BSW-Tech Story branches (from Features)
feature/bsw-tech-auth-001-oidc-config
feature/bsw-tech-pipeline-002-security-scanning
feature/bsw-tech-storage-003-zot-registry

# Bug fix branches  
bugfix/bsw-tech-321-fix-memory-leak

# Hotfix branches
hotfix/bsw-tech-911-critical-patch
```

### Repository Structure
**All bsw-tech code is organised in logical subfolders:**

```bash
/bsw-tech/
├── dual-gitops-pipeline/     # CI/CD and GitOps components
│   ├── infrastructure/       # OpenTofu/Terraform configs
│   ├── Dockerfile.*         # Container definitions
│   ├── deploy-*.sh          # Deployment scripts
│   └── README.md            # Pipeline documentation
├── k3s/                     # Kubernetes cluster management
│   ├── ansible-playbook.yml # Cluster configuration
│   ├── main.tf              # K3s infrastructure
│   └── templates/           # Configuration templates
├── security/                # Security tooling and configs
│   ├── devsecops-scanner/   # Security scanning tools
│   ├── openbao/             # OpenBao secrets management
│   └── policies/            # Security policies
├── monitoring/              # Observability stack
│   ├── grafana/             # Dashboard configurations
│   ├── prometheus/          # Metrics collection
│   └── loki/               # Log aggregation
└── containers/              # Container orchestration
    ├── chainguard/         # Chainguard container configs
    ├── zot/                # Registry configurations
    └── compose/            # Docker Compose files
```

### Feature Branch Workflow
1. **Create Feature Branch**: `git checkout -b feature/bsw-tech-{category}-{number}-{description}`
2. **Work in Subfolder**: All changes go in appropriate `/bsw-tech/{category}/` subfolder
3. **Follow Structure**: Maintain logical organisation within bsw-tech directory
4. **Test Locally**: Validate all changes in bsw-tech AppVM environment
5. **PR to Develop**: Feature branch → develop → main (never direct to main)
6. **Clean History**: Squash commits and ensure no AI tool references

### Development Standards

#### Container Requirements

**MANDATORY: All bot containers MUST use apko for minimal, secure images**

- **Container Runtime**: `podman` ONLY (NEVER Docker)
- **Primary Build Tool**: `apko` for declarative, reproducible container builds
- **Base Images**: Wolfi OS packages only (no traditional distros)
- **Registry**: Zot at `localhost:5000` (30MB binary, no database)
- **Image Size Target**: 15-40MB per bot (90% smaller than traditional)
- **Actual Size**: 42MB per bot (still 90% smaller than traditional 400MB+)
- **Security Target**: Zero CVEs on build day
- **Container naming**: All containers use `{org}-{bot-name}` format
- **NEVER commit container images to git**: Use Zot registry at localhost:5000

##### Podman Requirements (MANDATORY)
- **ALWAYS use Podman**: Never use Docker, containerd, or other runtimes
- **Rootless mode**: All containers run rootless (UID 65532)
- **Daemonless**: Podman is daemonless, more secure than Docker
- **OCI compliant**: Full OCI container compatibility
- **Version**: Podman 5.6.2+ required
- **Alias**: Can create `docker` alias pointing to `podman` for compatibility
- **Socket**: Use Podman socket API if needed: `/run/user/$(id -u)/podman/podman.sock`

##### apko Build Standards
```yaml
# Example: axis-analytics-bot/containers/apko.yaml
contents:
  repositories:
    - https://packages.wolfi.dev/os
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
  packages:
    - wolfi-base
    - python-3.12
    - py3.12-crewai
    - ca-certificates-bundle

entrypoint:
  command: /usr/bin/python3 -m axis_analytics_bot

accounts:
  run-as: 65532  # Non-root user

archs:
  - x86_64
  - aarch64
```

##### Container Signing & SBOM
- **Sign all images**: Use `cosign` with BSW-Tech signing key
- **Generate SBOM**: Use `syft` to create SPDX-format SBOM
- **Vulnerability scanning**: Use `grype` for continuous CVE monitoring
- **Store artifacts**: SBOM and scan results in `sbom/` directory

#### Code Quality
- UK English spelling throughout all code and documentation
- Run appropriate linters before completing tasks
- Comprehensive security scanning with Trivy/Grype
- All secrets stored in OpenBao (Vault fork)

#### Commit Standards
```bash
# Format: <type>(<scope>): <description>
#
# Password: monoxide640

feat(infrastructure): implement Zitadel IAM integration
fix(containers): resolve Chainguard image build issue
security(openbao): update secrets management policies
ci(pipeline): enhance DevSecOps scanning
```

## Bot Ecosystems Overview

**Total Infrastructure**: 120 standardised repositories across 4 ecosystems

### AXIS Bots (11 repositories)
**Organisation**: https://codeberg.org/AXIS-Bots
**Purpose**: Architecture Assessment, Blueprint Design, Strategic Planning

**Repositories:**
1. axis-assessment-bot - Architecture assessment and validation
2. axis-blueprint-bot - Technical blueprint generation
3. axis-coordination-bot - Multi-bot orchestration coordinator
4. axis-innovation-bot - Innovation pattern detection
5. axis-integration-bot - System integration planning
6. axis-patterns-bot - Design pattern recommendations
7. axis-planning-bot - Strategic planning automation
8. axis-review-bot - Architecture review automation
9. axis-risk-bot - Risk assessment and mitigation
10. axis-strategy-bot - Strategy formulation
11. axis-validation-bot - Validation and compliance checking

**Container Size**: 25-35MB average per bot

### PIPE Bots (56 repositories)
**Organisation**: https://codeberg.org/PIPE-Bots
**Purpose**: Pipeline Operations, Data Processing, API Management

**Key Repositories:**
- pipe-ai-bot - AI/ML pipeline orchestration
- pipe-analytics-bot - Analytics processing
- pipe-api-bot - API gateway management
- pipe-docs-bot - Documentation generation
- pipe-integration-bot - External system integration
- pipe-ml - Machine learning pipeline
- pipe-models - Model registry and versioning
- pipe-training - Training pipeline orchestration
- ... (48 additional operational bots)

**Container Size**: 30-45MB average per bot

### ECO Bots (45 repositories)
**Organisation**: https://codeberg.org/ECO-Bots
**Purpose**: Ecological Optimisation, Resource Management, Sustainability

**Repository Pattern**: ECO-{function}-bot (e.g., ECO-alert-bot, ECO-monitoring-bot)

**Key Capabilities:**
- Resource usage optimisation
- Sustainability metrics tracking
- Ecological compliance monitoring
- Energy efficiency analysis
- Carbon footprint reduction

**Container Size**: 20-30MB average per bot

### IV Bots (8 repositories)
**Organisation**: https://codeberg.org/IV-Bots
**Purpose**: Intelligence & Validation, Security Operations, Knowledge Management

**Repositories:**
1. iv-analytics-bot - Intelligence analytics
2. iv-docs-ai - Documentation intelligence
3. iv-integration-bot - Intelligence integration
4. iv-moe - Mixture of Experts orchestration
5. iv-monitor-bot - Security monitoring
6. iv-report-bot - Intelligence reporting
7. iv-security-operations-bot - Security operations automation
8. iv-wiki-ai - Knowledge management

**Container Size**: 40-60MB average per bot (ML models included)

---

## Current BSW-Tech Components

### Infrastructure (OpenTofu)
- **Location**: `/bsw-tech/dual-gitops-pipeline/infrastructure/opentofu/`
- **Purpose**: Infrastructure as Code for BSW-Tech stack (OpenTofu - Terraform fork)
- **Key Files**: `containers.tf` - Container orchestration
- **Bot IaC**: Each bot includes complete OpenTofu configurations
- **IMPORTANT**: OpenTofu only - Terraform is forbidden (HashiCorp)

### Kubernetes Management
- **Location**: `/bsw-tech/k3s/`
- **Purpose**: K3s cluster deployment and management
- **Key Files**: `main.tf`, `ansible-playbook.yml`
- **Bot Deployment**: Helm charts in each bot's `iac/helm/` directory

### Security & DevSecOps
- **Location**: `/bsw-tech/dual-gitops-pipeline/`
- **Components**:
  - Dockerfile.devsecops-scanner*
  - Security scanning scripts (Trivy, Grype, Semgrep)
  - OpenBao integration (Vault fork - HashiCorp forbidden)
- **Bot Security**: Each bot includes security policies in `guardrails/`
- **IMPORTANT**: OpenBao only - HashiCorp Vault is forbidden

### Container Registry
- **Registry**: Zot at `localhost:5000` (30MB binary, zero database)
- **Images**: All 120 bot containers stored here
- **Signing**: All images signed with cosign
- **SBOM**: SPDX-format SBOM for each container
- **Never commit**: Container images belong in registry, not git

### CI/CD Pipeline
- **Primary**: Woodpecker CI (container-native, lightweight)
- **Workflows**: Argo Workflows for complex DAG-based pipelines
- **GitOps**: Flux/ArgoCD patterns for declarative deployment
- **Bot Pipelines**: Each bot includes `.woodpecker/` CI configuration

## Bot Repository Structure

**MANDATORY: All 120 bot repositories follow this standardised structure**

```bash
{bot-name}/
├── agents/                    # Bot agent implementations
├── build/                     # Build scripts and automation
├── ci/                        # CI/CD pipeline configs
├── containers/                # Container definitions
│   ├── apko.yaml             # apko build definition (MANDATORY)
│   └── Dockerfile.legacy     # Legacy fallback only
├── docs/                      # Documentation
├── examples/                  # Usage examples
├── guardrails/                # Policy enforcement
├── iac/                       # Infrastructure as Code
│   ├── ansible/              # Automation playbooks
│   ├── helm/                 # Kubernetes charts
│   ├── openbao/              # Secrets management
│   └── opentofu/             # Infrastructure provisioning
├── metrics/                   # Monitoring dashboards
├── orchestration/             # Workflow definitions
├── sbom/                      # Software Bill of Materials
│   ├── {bot-name}.spdx.json  # SBOM in SPDX format
│   └── {bot-name}.vulnerabilities.json
├── tests/                     # Test suites
├── wiki/                      # Comprehensive documentation
│   ├── Home.md               # Overview and architecture
│   ├── Getting-Started.md    # Quick start guide
│   └── API-Reference.md      # Complete API documentation
├── .gitignore                # 69-line comprehensive
├── .woodpecker.yml           # CI pipeline configuration
├── FOLDER-STRUCTURE.md       # Structure documentation
├── LICENSE                   # MIT License
└── README.md                 # Bot-specific content
```

**File Counts per Bot:**
- Total files: 56-63 per repository
- .gitkeep files: 33+ for directory structure
- IaC configurations: OpenTofu, Ansible, Helm, OpenBao
- Wiki pages: 3+ markdown documents

---

## Augmentic AI Architecture

**All 120 bots are branded as "Augmentic AI" autonomous agents**

### Core Technologies
- **LLM**: Claude 3.5 Sonnet (via Anthropic API or local Ollama)
- **Agent Framework**: CrewAI for multi-agent collaboration
- **Knowledge Base**: META-KERAGR graph database (http://localhost:3108)
- **Vector Store**: Qdrant for semantic search
- **Orchestration**: Temporal for durable workflows

### Multi-Bot Collaboration
- **Coordination**: axis-coordination-bot orchestrates cross-bot workflows
- **Integration**: pipe-integration-bot handles external system connections
- **Knowledge Sharing**: Shared META-KERAGR instance for collective learning
- **Communication**: RESTful APIs + event-driven messaging

### Compliance Frameworks
All bots comply with:
- **TOGAF 9.2** - Enterprise Architecture Framework
- **Zachman Framework** - Enterprise Architecture Blueprint
- **ArchiMate 3.1** - Architecture Modelling Language
- **UK Cyber Essentials** - Security baseline
- **GDPR & NIS2** - European data protection and security

### Agent Capabilities
- Autonomous task execution
- Multi-step reasoning and planning
- Context-aware decision making
- Continuous learning through knowledge graphs
- Collaborative problem-solving across bots

---

## Repository Security Standards

**MANDATORY: All repositories are PRIVATE with SHA-256 encryption**

- **ALL repositories**: Must be private on Codeberg
- **Encryption**: SHA-256 encryption mandatory for all repositories
- **Access**: Requires proper authentication token for all operations
- **Public repos**: NEVER allowed - all repositories must remain private
- **API authentication**: All API calls require valid Codeberg token with appropriate permissions
- **Git operations**: Always use SSH with configured keys (`~/.ssh/id_ed25519`)
- **Submodules**: All bot repositories are git submodules of bsw-infra
- **Branch protection**: develop and main branches require PR reviews

## Critical Rules

**NEVER ADD AI TOOL ATTRIBUTION:**
- **NEVER** add "Generated with Claude Code" to any file
- **NEVER** add "Co-Authored-By: Claude" to any commit or file

**NEVER COMMIT LARGE FILES OR CONTAINER IMAGES:**
- **NEVER** commit container images, binaries, or files larger than 1MB to git repositories
- **ALWAYS** store container images in Zot registry at localhost:5000
- **Check .gitignore**: Verify all binaries, images, and large files are excluded

**UK ENGLISH COMPLIANCE:**
- Use UK English spelling throughout all code and documentation
- colour (not color), optimise (not optimize), initialise (not initialize)

**PASSWORD REFERENCE:**
All BSW infrastructure uses: `monoxide640`

---

## Deployment Procedures

### apko Container Build Process

**MANDATORY: All bot containers MUST be built with apko**

```bash
#!/bin/bash
# Build single bot container with apko

BOT_NAME="axis-analytics-bot"
ORG="axis-bots"
REGISTRY="localhost:5000"

# 1. Build with apko
apko build \
  "${BOT_NAME}/containers/apko.yaml" \
  "${REGISTRY}/${ORG}/${BOT_NAME}:latest" \
  "${BOT_NAME}.tar"

# 2. Load to Podman (MANDATORY: Use Podman, not Docker)
podman load < "${BOT_NAME}.tar"

# 3. Push to Zot registry (MANDATORY: Use Podman, not Docker)
podman push "${REGISTRY}/${ORG}/${BOT_NAME}:latest"

# 4. Sign with cosign
cosign sign --key /home/user/.ssh/cosign.key \
  "${REGISTRY}/${ORG}/${BOT_NAME}:latest"

# 5. Generate SBOM
syft "${REGISTRY}/${ORG}/${BOT_NAME}:latest" \
  -o spdx-json > "${BOT_NAME}/sbom/${BOT_NAME}.spdx.json"

# 6. Scan for vulnerabilities
grype "${REGISTRY}/${ORG}/${BOT_NAME}:latest" \
  -o json > "${BOT_NAME}/sbom/${BOT_NAME}.vulnerabilities.json"

# 7. Cleanup
rm "${BOT_NAME}.tar"
```

### Bulk Bot Deployment

**Deploy all 120 bots to K3s cluster:**

```bash
#!/bin/bash
# Deploy all bot ecosystems

ECOSYSTEMS=("AXIS-Bots" "PIPE-Bots" "ECO-Bots" "IV-Bots")

for ecosystem in "${ECOSYSTEMS[@]}"; do
  echo "Deploying ${ecosystem}..."

  # Apply Helm charts for all bots in ecosystem
  for bot_dir in ${ecosystem,,}-*-bot/; do
    bot_name=$(basename "$bot_dir")

    helm upgrade --install "${bot_name}" \
      "${bot_dir}/iac/helm/" \
      --namespace "${ecosystem,,}" \
      --create-namespace \
      --set image.registry="localhost:5000" \
      --set image.repository="${ecosystem,,}/${bot_name}" \
      --set image.tag="latest"
  done
done
```

### Infrastructure Deployment Checklist

**Before deploying bots to production:**

- [ ] K3s cluster deployed and healthy
- [ ] OpenBao installed and initialised
- [ ] Zot registry running at localhost:5000
- [ ] All 120 bot containers built with apko
- [ ] All containers signed with cosign
- [ ] SBOM generated for all containers
- [ ] Vulnerability scans show zero critical CVEs
- [ ] Woodpecker CI configured and operational
- [ ] Prometheus + Grafana monitoring deployed
- [ ] META-KERAGR knowledge graph running (localhost:3108)
- [ ] Network policies configured (zero-trust)

---

## Monitoring & Observability

### Metrics Collection
- **Prometheus**: Scrapes metrics from all 120 bots
- **Grafana**: Dashboards per ecosystem (AXIS, PIPE, ECO, IV)
- **AlertManager**: Alert routing and deduplication

### Log Aggregation
- **Loki**: Centralised log storage
- **Promtail**: Log collection from all pods
- **Grafana**: Log exploration and analysis

### Distributed Tracing
- **Tempo**: Trace storage and querying
- **OpenTelemetry**: Instrumentation for all bots

### Agent Monitoring
- **Langfuse**: LLM call tracking and analysis
- **Phoenix**: Agent behaviour monitoring
- **Custom metrics**: Bot-specific performance indicators

### Monitoring Endpoints
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Loki: http://localhost:3100
- META-KERAGR: http://localhost:3108
- Coordination API: http://localhost:3111

---

## Operational Standards

### Bot Lifecycle Management

**Development → Staging → Production**

1. **Development**: Local testing with Ollama + local K3s
2. **Staging**: Full deployment to staging cluster
3. **Production**: Gradual rollout with canary deployments

### Version Control
- **Git Strategy**: GitFlow (main, develop, feature branches)
- **Semantic Versioning**: v{major}.{minor}.{patch}
- **Release Tags**: Tag all production releases
- **Changelog**: Maintain CHANGELOG.md per bot

### Backup & Recovery
- **etcd snapshots**: Daily K3s cluster backups
- **OpenBao backups**: Encrypted secret backups
- **Container images**: Retain last 10 tagged versions
- **Disaster recovery**: RTO 4 hours, RPO 24 hours

### Resource Quotas
**Per bot namespace:**
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Total cluster allocation for 120 bots:**
- Memory: ~60GB (512MB × 120)
- CPU: ~60 cores (500m × 120)
- Storage: ~100GB (container images + data)

---

## Troubleshooting Guide

### Common Issues

**Bot container fails to start:**
```bash
# Check logs
kubectl logs -n axis-bots axis-analytics-bot-xxx

# Verify image exists
curl http://localhost:5000/v2/axis-bots/axis-analytics-bot/tags/list

# Check SBOM for missing dependencies
cat axis-analytics-bot/sbom/axis-analytics-bot.spdx.json | jq '.packages'
```

**High memory usage:**
```bash
# Check resource usage
kubectl top pods -n axis-bots

# Review apko.yaml for unnecessary packages
cat axis-analytics-bot/containers/apko.yaml

# Rebuild with minimal dependencies
apko build axis-analytics-bot/containers/apko.yaml
```

**CVE detected in container:**
```bash
# Rescan with grype
grype localhost:5000/axis-bots/axis-analytics-bot:latest

# Update Wolfi packages in apko.yaml
# Rebuild container
# Redeploy with Helm
```

---

## Performance Targets

### Container Metrics
- **Build time**: < 2 minutes per bot
- **Image size**: 15-40MB (90% reduction vs traditional)
- **Startup time**: < 5 seconds
- **Memory footprint**: < 512MB per bot

### Bot Performance
- **Response time**: < 500ms for API calls
- **LLM latency**: < 2 seconds for Claude API
- **Knowledge retrieval**: < 100ms from META-KERAGR
- **Multi-bot collaboration**: < 1 second coordination overhead

### Infrastructure Targets
- **Cluster uptime**: 99.9% (8.76 hours downtime/year)
- **Deployment time**: < 5 minutes per bot
- **Rollback time**: < 2 minutes
- **MTTR**: < 1 hour (Mean Time To Recovery)