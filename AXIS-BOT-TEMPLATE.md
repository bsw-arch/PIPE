# PIPE Bot Repository Template
## Universal Structure for All 46 PIPE Bots

**Version**: 1.0.0
**Status**: Production Ready
**Apply to**: All PIPE Augmentic AI Bots

---

## 📁 Universal Directory Structure

```
axis-{bot-name}/
│
├── .gitignore                      # Standard Git ignore
├── .github-workflow-guide.md       # GitFlow guide
├── LICENSE                         # MIT License
├── README.md                       # Bot-specific README
├── CONTRIBUTING.md                 # Contribution guidelines
├── CHANGELOG.md                    # Version history
│
├── agents/                         # 🤖 Bot Implementation
│   ├── {bot_name}/                # Main bot code (VARIABLE)
│   │   ├── __init__.py
│   │   ├── agent.py               # Main agent class
│   │   ├── tasks.py               # Task definitions
│   │   ├── tools.py               # Agent tools
│   │   └── config.py              # Bot configuration
│   │
│   ├── shared/                    # Shared utilities (FIXED)
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent framework
│   │   ├── augmentic_agent.py     # Augmentic AI features
│   │   ├── logger.py              # Logging utilities
│   │   ├── keragr_client.py       # META-KERAGR integration
│   │   └── coordination.py        # Multi-bot coordination
│   │
│   └── tests/                     # Agent unit tests
│       ├── test_agent.py
│       ├── test_tasks.py
│       └── test_tools.py
│
├── containers/                     # 🐳 Container Definitions
│   ├── base/                      # Shared Wolfi base (FIXED)
│   │   ├── wolfi.yaml
│   │   ├── apko.yaml
│   │   ├── melange.yaml
│   │   ├── README.md
│   │   ├── scripts/
│   │   │   └── build.sh
│   │   └── sbom/
│   │       └── generate.sh
│   │
│   ├── main/                      # Main bot container (FIXED)
│   │   ├── wolfi.yaml
│   │   ├── apko.yaml
│   │   ├── dependencies.txt
│   │   ├── Dockerfile.wolfi
│   │   ├── entrypoint.sh
│   │   ├── README.md
│   │   ├── scripts/
│   │   │   └── build.sh
│   │   └── sbom/
│   │       └── generate.sh
│   │
│   ├── {component}/               # Optional components (VARIABLE)
│   │   ├── wolfi.yaml            # e.g., scheduler, worker, api
│   │   ├── apko.yaml
│   │   ├── Dockerfile.wolfi
│   │   └── ...
│   │
│   └── shared/                    # Shared container resources (FIXED)
│       ├── scripts/
│       │   ├── health-check.sh
│       │   └── graceful-shutdown.sh
│       └── configs/
│           └── logging.yaml
│
├── iac/                           # 🏗️ Infrastructure as Code
│   ├── README.md                  # IaC documentation
│   │
│   ├── helm/                      # Kubernetes deployment
│   │   ├── charts/
│   │   │   └── axis-{bot}/
│   │   │       ├── Chart.yaml
│   │   │       ├── values.yaml
│   │   │       └── templates/
│   │   └── values/
│   │       ├── dev.yaml
│   │       ├── staging.yaml
│   │       └── production.yaml
│   │
│   ├── ansible/                   # Podman deployment
│   │   ├── playbooks/
│   │   │   ├── deploy-containers.yml
│   │   │   └── configure-openbao.yml
│   │   ├── roles/
│   │   │   └── axis-{bot}/
│   │   └── inventory/
│   │       ├── dev.ini
│   │       └── production.ini
│   │
│   ├── opentofu/                  # Infrastructure provisioning
│   │   ├── modules/
│   │   │   ├── k3s-cluster/
│   │   │   └── openbao-setup/
│   │   └── environments/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── production/
│   │
│   └── openbao/                   # Secrets management
│       ├── policies/
│       │   └── axis-{bot}-policy.hcl
│       └── secrets/
│           └── setup-secrets.sh
│
├── build/                         # 🔨 Build Automation
│   ├── README.md
│   ├── build-all.sh              # Build all containers
│   ├── generate-all-sboms.sh     # Generate SBOMs
│   ├── test-all.sh               # Run all tests
│   ├── push-all.sh               # Push to registry
│   │
│   ├── templates/                # Build templates
│   │   ├── wolfi-template.yaml
│   │   ├── apko-template.yaml
│   │   └── melange-template.yaml
│   │
│   └── utils/                    # Build utilities
│       ├── size-report.sh
│       └── dependency-tree.sh
│
├── ci/                            # 🔄 CI/CD Pipelines
│   ├── .woodpecker.yml           # Main pipeline
│   └── .woodpecker/
│       ├── build-pipeline.yml
│       ├── test-pipeline.yml
│       ├── security-pipeline.yml
│       └── deploy-pipeline.yml
│
├── sbom/                          # 📋 Software Bill of Materials
│   ├── main/                     # Main bot SBOM (FIXED)
│   │   ├── sbom.spdx.json
│   │   ├── sbom.cyclonedx.json
│   │   ├── packages.txt
│   │   └── vulnerabilities.json
│   │
│   ├── {component}/              # Component SBOMs (VARIABLE)
│   │
│   ├── combined/                 # Combined SBOM
│   │   ├── platform-sbom.spdx.json
│   │   └── dependency-graph.json
│   │
│   └── signatures/               # Cosign signatures
│       └── {container}.sig
│
├── tests/                         # 🧪 Testing
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── security/                 # Security tests
│   │   ├── test_sbom_generation.py
│   │   └── test_vulnerability_scan.py
│   └── performance/              # Performance tests
│       └── test_container_size.py
│
├── docs/                          # 📚 Documentation
│   ├── ARCHITECTURE.md           # Architecture documentation
│   ├── API.md                    # API reference
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── DEVELOPMENT.md            # Development guide
│   │
│   ├── diagrams/                 # Architecture diagrams
│   │   ├── architecture.mermaid
│   │   ├── deployment.mermaid
│   │   └── workflow.mermaid
│   │
│   └── examples/                 # Usage examples
│       ├── basic-usage.py
│       └── advanced-usage.py
│
├── examples/                      # 💡 Example Implementations
│   └── {use-case}/
│       ├── README.md
│       └── example.py
│
├── orchestration/                 # 🎭 Multi-Bot Orchestration
│   └── workflows/
│       ├── {bot}-workflow.py
│       └── collaboration.py
│
├── guardrails/                    # 🛡️ Security & Compliance
│   └── policies/
│       ├── security-policy.yaml
│       └── compliance-policy.yaml
│
├── metrics/                       # 📊 Monitoring & Observability
│   ├── prometheus.yml
│   └── dashboards/
│       └── grafana-{bot}.json
│
└── wiki/                          # 📖 Wiki Documentation
    ├── Home.md
    ├── Getting-Started.md
    ├── API-Reference.md
    └── Troubleshooting.md
```

---

## 🎯 Variable vs Fixed Components

### **FIXED Components** (Same for all bots)
✅ Always present, same structure

```
containers/base/          # Shared Wolfi base
containers/main/          # Main bot container
containers/shared/        # Shared scripts
agents/shared/            # Shared utilities
iac/{helm,ansible,...}    # IaC stack
build/                    # Build automation
ci/                       # CI/CD
sbom/                     # SBOM generation
tests/                    # Testing structure
docs/                     # Documentation
```

### **VARIABLE Components** (Bot-specific)
🔄 Name and structure varies per bot

```
agents/{bot_name}/        # e.g., axis_docs, axis_patterns, axis_compliance
containers/{component}/   # Optional: scheduler, worker, api, etc.
sbom/{component}/         # Component-specific SBOMs
examples/{use-case}/      # Bot-specific examples
```

---

## 📝 Template Variables

Replace these in all files when creating new bot:

| Variable | Example | Description |
|----------|---------|-------------|
| `{bot-name}` | `docs-bot`, `patterns-bot` | Bot name (kebab-case) |
| `{bot_name}` | `docs_bot`, `patterns_bot` | Bot name (snake_case) |
| `{BotName}` | `DocsBot`, `PatternsBot` | Bot name (PascalCase) |
| `{component}` | `scheduler`, `worker`, `api` | Optional component name |
| `{use-case}` | `review-doc`, `validate-pattern` | Example use case |

---

## 🔧 Naming Conventions

### Repository Names
```
axis-{function}-bot
```

Examples:
- `axis-docs-bot` - Documentation bot
- `pipe-lint-bot` - Pattern recognition bot
- `axis-compliance-bot` - Compliance checking bot
- `axis-task-bot` - Task management bot ✓ (current)

### Container Images
```
localhost:5000/axis-{bot-name}:latest
localhost:5000/axis-{bot-name}-{component}:latest
```

Examples:
- `localhost:5000/axis-docs-bot:latest`
- `localhost:5000/pipe-lint-bot-analyzer:latest`

### Python Modules
```python
from agents.{bot_name} import {BotName}Agent
from agents.shared import BaseAgent
```

Examples:
```python
from agents.docs_bot import DocsBotAgent
from agents.patterns_bot import PatternsBotAgent
from agents.shared import BaseAgent
```

### OpenBao Secrets Paths
```
axis-bots/{bot-name}/
```

Examples:
- `axis-bots/docs-bot/api_key`
- `axis-bots/patterns-bot/keragr_url`

---

## 🎨 Customization Per Bot

### Minimal Bot (Simple)
Only needs:
```
agents/{bot_name}/        # Main bot code
containers/main/          # Single container
iac/                      # Standard IaC
```

Example: `axis-metrics-bot` (just collects metrics)

### Medium Bot (Standard)
Needs:
```
agents/{bot_name}/        # Main bot code
containers/main/          # Main container
containers/worker/        # Background worker
iac/                      # Standard IaC
```

Example: `axis-docs-bot` (bot + worker for processing)

### Complex Bot (Multi-Component)
Needs:
```
agents/{bot_name}/        # Main bot code
containers/main/          # Main bot
containers/scheduler/     # Scheduling component
containers/executor/      # Execution worker
containers/api/           # API gateway
iac/                      # Extended IaC
```

Example: `axis-task-bot` ✓ (current - full orchestration)

---

## 📦 Container Size Targets

All bots must meet these targets:

| Component | Target Size | Max Size |
|-----------|-------------|----------|
| Base Wolfi | 3-5 MB | 6 MB |
| Main Bot | 6-10 MB | 12 MB |
| Extra Component | 5-8 MB | 10 MB |
| **Total per Bot** | **<30 MB** | **40 MB** |

---

## 🔐 Security Standards

All bots MUST implement:

✅ **Non-root execution** (uid 65532)
✅ **OpenBao secrets** (no hardcoded credentials)
✅ **SBOM generation** (SPDX + CycloneDX)
✅ **CVE scanning** (Grype)
✅ **Signed artifacts** (Cosign)
✅ **TOGAF 9.2 compliance**
✅ **Audit logging**
✅ **Network policies** (K8s)

---

## 📊 Quality Standards

All bots MUST have:

✅ **Unit tests** (>80% coverage)
✅ **Integration tests**
✅ **Security tests**
✅ **Performance tests**
✅ **CI/CD pipeline**
✅ **Documentation**
✅ **Examples**
✅ **Health checks**

---

## 🚀 Quick Start: Create New Bot

```bash
# 1. Clone template
git clone git@codeberg.org:PIPE-Bots/axis-bot-template.git axis-{new-bot}-bot
cd axis-{new-bot}-bot

# 2. Run template script
./scripts/init-new-bot.sh \
  --name "{new-bot}" \
  --description "Bot description" \
  --components "main,worker"

# 3. Implement agent
vim agents/{new_bot}/agent.py

# 4. Build containers
./build/build-all.sh

# 5. Test
./build/test-all.sh

# 6. Deploy
cd iac/opentofu/environments/dev
tofu init && tofu apply
```

---

## 🔄 Migration Guide

### Migrate Existing Bot to Template

1. **Create new structure**
```bash
git clone git@codeberg.org:PIPE-Bots/axis-bot-template.git
```

2. **Copy existing code**
```bash
cp -r old-bot/agents/core/* new-bot/agents/{bot_name}/
cp -r old-bot/containers/* new-bot/containers/main/
```

3. **Update imports**
```python
# Old
from agents.core import Agent

# New
from agents.{bot_name} import Agent
from agents.shared import BaseAgent
```

4. **Update configs**
```bash
# Update container names, secrets paths, etc.
find . -type f -name "*.yaml" -o -name "*.yml" | \
  xargs sed -i 's/old-bot-name/{new-bot-name}/g'
```

5. **Test & validate**
```bash
./build/test-all.sh
./build/build-all.sh
```

---

## 📋 Checklist: New Bot Compliance

- [ ] Follows directory structure template
- [ ] Uses shared base container
- [ ] Implements BaseAgent framework
- [ ] Has OpenBao secrets integration
- [ ] Generates SBOM automatically
- [ ] Runs as non-root (uid 65532)
- [ ] Meets size targets (<30 MB total)
- [ ] Has unit tests (>80% coverage)
- [ ] Has integration tests
- [ ] Has CI/CD pipeline
- [ ] Has complete documentation
- [ ] Has usage examples
- [ ] Follows naming conventions
- [ ] TOGAF 9.2 compliant
- [ ] Integrates with META-KERAGR
- [ ] Supports multi-bot coordination

---

## 🎓 Benefits of This Template

### For Developers
✅ **Consistent structure** - Same layout for all 46 bots
✅ **Faster development** - Reuse shared components
✅ **Less boilerplate** - Template handles infrastructure
✅ **Quality enforced** - Built-in testing & security

### For Operations
✅ **Uniform deployment** - Same IaC for all bots
✅ **Predictable sizing** - All bots <30 MB
✅ **Centralized secrets** - OpenBao everywhere
✅ **Easy monitoring** - Standard metrics structure

### For Security
✅ **Supply chain transparency** - SBOM for all
✅ **CVE scanning** - Automated vulnerability checks
✅ **No hardcoded secrets** - OpenBao integration
✅ **Signed artifacts** - Cosign signatures

---

## 📞 Support

- **Template Issues**: https://codeberg.org/PIPE-Bots/axis-bot-template/issues
- **Documentation**: https://codeberg.org/PIPE-Bots/axis-bot-template/wiki
- **Examples**: See existing bots (axis-task-bot, axis-docs-bot)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-11
**Status**: ✅ Production Ready
**Apply to**: All 46 PIPE Augmentic AI Bots

---

**This template ensures:**
- 🎯 Consistency across all PIPE bots
- 🔐 Security by default
- 📦 Ultra-minimal containers (<30 MB)
- 🚀 Fast development cycles
- 🤖 Augmentic AI best practices
