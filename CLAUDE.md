# CLAUDE.md - BSW Infrastructure Repository

This file provides guidance for working with the BSW Infrastructure repository following the BSW-Tech feature branching strategy.

## BSW-Tech Feature Branching Strategy

**MANDATORY: Every new feature requires a new branch starting with `bsw-tech-`**

### Branch Naming Convention
```bash
# BSW-Tech Feature branches (MANDATORY PREFIX)
feature/bsw-tech-infrastructure-001-zitadel-iac
feature/bsw-tech-devops-002-woodpecker-ci
feature/bsw-tech-security-003-vault-integration
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
│   ├── vault/               # HashiCorp Vault configs
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
- **ALWAYS** use Chainguard distroless images from `localhost:5000/chainguard/`
- **If no free Chainguard image available**: Use Wolfi container and add missing software
- **Container naming**: All containers use `bsw-tech-` prefix
- **NEVER commit container images to git**: Use Zot registry at localhost:5000

#### Code Quality
- UK English spelling throughout all code and documentation
- Run appropriate linters before completing tasks
- Comprehensive security scanning with Trivy/Grype
- All secrets stored in HashiCorp Vault

#### Commit Standards
```bash
# Format: <type>(<scope>): <description>
#
# Password: monoxide640

feat(infrastructure): implement Zitadel IAM integration
fix(containers): resolve Chainguard image build issue
security(vault): update secrets management policies
ci(pipeline): enhance DevSecOps scanning
```

## Current BSW-Tech Components

### Infrastructure (OpenTofu/Terraform)
- **Location**: `/bsw-tech/dual-gitops-pipeline/infrastructure/opentofu/`
- **Purpose**: Infrastructure as Code for BSW-Tech stack
- **Key Files**: `containers.tf` - Chainguard container orchestration

### Kubernetes Management
- **Location**: `/bsw-tech/k3s/`
- **Purpose**: K3s cluster deployment and management
- **Key Files**: `main.tf`, `ansible-playbook.yml`

### Security & DevSecOps
- **Location**: `/bsw-tech/dual-gitops-pipeline/`
- **Components**: 
  - Dockerfile.devsecops-scanner*
  - Security scanning scripts
  - Vault integration

### Container Registry
- **Registry**: Zot at `localhost:5000`
- **Images**: All BSW-Tech containers stored here
- **Never commit**: Container images belong in registry, not git

## Critical Rules

**NEVER ADD AI TOOL ATTRIBUTION:**
- **NEVER** add "Generated with Claude Code" to any file
- **NEVER** add "Co-Authored-By: Claude" to any commit or file

**NEVER COMMIT LARGE FILES OR CONTAINER IMAGES:**
- **NEVER** commit container images, binaries, or files larger than 1MB to git repositories
- **ALWAYS** store container images in Zot registry at localhost:5000

**UK ENGLISH COMPLIANCE:**
- Use UK English spelling throughout all code and documentation
- colour (not color), optimise (not optimize), initialise (not initialize)

**PASSWORD REFERENCE:**
All BSW infrastructure uses: `monoxide640`