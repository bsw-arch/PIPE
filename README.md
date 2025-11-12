# BSW-Arch: Bot Factory Architecture Documentation

> Comprehensive documentation for the BSW-Tech autonomous bot factory deployed on Codeberg

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Codeberg](https://img.shields.io/badge/Codeberg-Primary-blue)](https://codeberg.org)
[![UK English](https://img.shields.io/badge/Language-UK%20English-red)](https://en.wikipedia.org/wiki/British_English)
[![FAGAM Free](https://img.shields.io/badge/FAGAM-Free-green)](docs/guides/security/)

## 📚 Overview

This repository contains comprehensive architectural documentation for the **BSW-Tech Bot Factory**, a multi-domain autonomous agent system deployed on Codeberg using Qubes OS infrastructure. The system comprises 185 specialized bots across **8 domains** (PIPE, BNI, BNP, AXIS, IV, ECO, DC, BU) with 2-tier CAG+RAG architecture, running in ultra-lightweight containers (<50MB each).

## 🎯 Quick Start

### For Architects
Start with the [enterprise CAG+RAG solution architecture](docs/architecture/ENTERPRISE-CAG-RAG-SOLUTION-ARCHITECTURE.md) for multi-domain integration overview, then dive into the [comprehensive architecture analysis](docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md) (145 pages) for complete system design.

### For Developers
Review the [BSW-Tech Claude integration guide](docs/guides/development/CLAUDE.md) and [AI integration guide](docs/guides/development/BSW-TECH-AI-INTEGRATION-GUIDE.md).

### For Bot Developers
Browse bot specifications in [`docs/specifications/bots/`](docs/specifications/bots/) and use templates from [`docs/templates/bot/`](docs/templates/bot/).

### For Operations
Check deployment procedures in [`docs/processes/deployment/`](docs/processes/deployment/) and the [IAC alignment report](docs/architecture/infrastructure/IAC-ALIGNMENT-REPORT.md).

## 🏗️ Architecture Overview

### System Structure

```
BSW-GOV (Qubes OS)
├── bsw-gov    (Governance & Architecture)
├── bsw-arch   (GitHub Documentation Hub) ← THIS REPO
├── bsw-tech   (Development & CI/CD)
└── bsw-present (Presentation & Reporting)

Codeberg Deployment (8 Domains, 185 Bots)
├── Core Infrastructure
│   └── PIPE-Bots       (48 bots - API, Integration, Pipelines)
├── Business Domains
│   ├── BNI-Bots        (~37 bots - Business Infrastructure)
│   ├── BNP-Bots        (~37 bots - Platform Services)
│   └── BU-Bots         (~42 bots - Analytics, Compliance)
├── AI Domains
│   ├── AXIS-Bots       (45 bots - Architecture, Design)
│   └── IV-Bots         (44 bots - LLM, RAG, Intelligence)
└── Specialized Domains
    ├── ECO-Bots        (48 bots - Infrastructure, Resources)
    └── DC-Bots         (~30 bots - Digital Content, Media)
```

### Key Metrics

| Metric | Value |
|--------|-------|
| **Total Bots** | 185 across 8 domains |
| **Core Domains** | PIPE (48), BNI (~37), BNP (~37), BU (~42) |
| **AI Domains** | AXIS (45), IV (44) |
| **Specialized** | ECO (48), DC (~30) |
| **Container Size** | <50MB per bot (apko + Chainguard Wolfi) |
| **Network Zones** | 12+ segmented zones (10.100.x.0/24) |
| **Architecture** | 2-Tier CAG+RAG with cascaded processing |
| **Git Repositories** | 185+ on Codeberg |
| **Documentation** | Enterprise architecture + domain guides |

### Technology Stack

- **Containers**: apko + Chainguard Wolfi (15-50MB vs traditional 400MB+)
- **Infrastructure**: OpenTofu (not Terraform), OpenBao (not Vault)
- **AI Framework**: CrewAI for multi-agent collaboration
- **RAG Systems**: FAISS (vectors), Neo4j (graphs), MongoDB (documents), Redis (cache)
- **LLM Integration**: Multi-model support (Claude, GPT, local models)
- **OS**: Qubes OS with 4 AppVM compartmentalization
- **Git Hosting**: Codeberg (FAGAM-free alternative)
- **CI/CD**: GitOps workflow (feature → develop → main)

## 📖 Documentation Structure

```
docs/
├── architecture/              # System architecture documentation
│   ├── COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
│   ├── domains/              # Domain-specific docs (AXIS, PIPE, ECO, IV)
│   ├── components/           # Component documentation
│   │   └── BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
│   └── infrastructure/       # Infrastructure docs
│       └── IAC-ALIGNMENT-REPORT.md
│
├── processes/                # Workflow and deployment procedures
│   ├── github_docs_consolidation_strategy.md
│   ├── workflows/           # Workflow definitions
│   ├── deployment/          # Deployment procedures
│   └── operations/          # Operational procedures
│
├── guides/                  # Development and security guides
│   ├── development/         # Development guides
│   │   ├── CLAUDE.md       # BSW-Tech Claude guide
│   │   └── BSW-TECH-AI-INTEGRATION-GUIDE.md
│   ├── security/           # Security guides
│   └── best-practices/     # Best practices
│
├── specifications/          # Bot and container specifications
│   ├── bots/              # Bot specifications
│   ├── containers/        # Container specs (apko/Wolfi)
│   └── integration/       # Integration patterns
│
├── diagrams/               # Architecture diagrams
│   ├── architecture/      # System diagrams (Mermaid)
│   ├── workflows/         # Workflow diagrams
│   └── infrastructure/    # Infrastructure diagrams
│
├── templates/              # Reusable templates
│   ├── bot/              # Bot creation templates
│   ├── container/        # Container configuration templates
│   └── deployment/       # Deployment templates
│
└── reference/             # Reference documentation
    ├── apis/             # API documentation
    ├── standards/        # TOGAF, Zachman, ArchiMate
    └── glossary/         # Terminology
```

Full documentation index: [docs/INDEX.md](docs/INDEX.md)

## 🤖 Bot Domains (8 Domains, 185 Bots)

### Core Infrastructure

#### PIPE (Pipeline Domain) - 48 Bots
**Purpose**: Core API, integration, CI/CD pipelines
**Network**: 10.100.1.0/24

Specialized bots:
- `PAPI`: API management and gateway
- `PART`: Artifact and build management
- `PINT`: Integration orchestration
- `PCMP`: Component management
- `PDEP`: Deployment automation

**Documentation**: [PIPE Bots Instructions](docs/guides/bot-domains/PIPE-BOTS-INSTRUCTIONS.md)

---

### Business Domains

#### BNI (Business Network Infrastructure) - ~37 Bots
**Purpose**: Business service orchestration, workflow automation
**Network**: 10.100.3.0/24

#### BNP (Business Network Platform) - ~37 Bots
**Purpose**: Platform services, multi-tenant APIs
**Network**: 10.100.4.0/24

#### BU (Business Unit) - ~42 Bots
**Purpose**: Analytics, compliance, operational excellence
**Network**: 10.100.5.0/24

---

### AI Domains

#### AXIS (Architecture Domain) - 45 Bots
**Purpose**: Enterprise architecture, design patterns, compliance
**Network**: 10.100.6.0/24

Specialized bots:
- `axis-docs-bot`: Documentation generation
- `axis-coordination-bot`: Multi-bot orchestration
- `axis-validation-bot`: Architecture validation
- `axis-blueprint-bot`: Blueprint generation

**Documentation**: [AXIS Bots Setup Guide](docs/guides/AXIS-BOTS-SETUP-GUIDE.md)

#### IV (IntelliVerse/Intelligence) - 44 Bots
**Purpose**: LLM orchestration, RAG systems, validation
**Network**: 10.100.7.0/24

Specialized bots:
- `iv-llm-orchestrator`: Multi-model LLM orchestration
- `iv-rag-hybrid-retrieval`: Hybrid search (vector + graph + document)
- `iv-kb-indexer`: Knowledge base management
- `iv-ctx-session-manager`: Context and session management
- `iv-validation-bot`: Quality validation

**Documentation**:
- [IV Domain Architecture](docs/architecture/domains/IV/IV-DOMAIN-ARCHITECTURE.md)
- [CAG+RAG Implementation Guide](docs/guides/bot-domains/IV-BOTS-CAG-RAG-IMPLEMENTATION.md)

---

### Specialized Domains

#### ECO (Ecosystem/Infrastructure) - 48 Bots
**Purpose**: Infrastructure provisioning, resource optimization, monitoring
**Network**: 10.100.8.0/24

Specialized bots:
- `eco-monitoring-bot`: Resource monitoring
- `eco-optimization-bot`: Performance optimization
- `eco-metrics-bot`: Sustainability metrics
- `eco-infra-bot`: Infrastructure provisioning

**Documentation**:
- [ECO Domain Architecture](docs/architecture/domains/ECO/ECO-DOMAIN-ARCHITECTURE.md)
- [ECO Bots Quick Start](docs/guides/ECO-BOTS-QUICK-START.md)

#### DC (Digital Content) - ~30 Bots
**Purpose**: Media asset management, content delivery
**Network**: 10.100.9.0/24

Specialized bots:
- `dc-asset-bot`: Digital asset management
- `dc-process-bot`: Media processing
- `dc-cdn-bot`: Content delivery
- `dc-cache-bot`: Cache management

## 🚀 Bot Access Patterns

Bots can access this documentation through multiple methods:

### 1. Git Clone (Recommended)
```bash
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation
```

### 2. GitHub API
```python
import requests

response = requests.get(
    "https://api.github.com/repos/bsw-arch/bsw-arch/contents/docs/architecture"
)
```

### 3. META-KERAGR Integration
Future integration with Hybrid META-KERAGR knowledge base system (10-week implementation timeline).

## 🔒 Security & Compliance

### FAGAM Prohibition
**No use of**: Facebook, Apple, Google, Amazon, Microsoft, HashiCorp products

**Alternatives used**:
- Codeberg (vs GitHub for primary hosting)
- OpenTofu (vs Terraform)
- OpenBao (vs Vault)
- Chainguard Wolfi (vs Alpine/Ubuntu)

### Standards Compliance
- **TOGAF 9.2**: Enterprise Architecture Framework
- **Zachman Framework**: Architecture documentation
- **ArchiMate 3.1**: Architecture modelling
- **ISO 27001**: Information security
- **UK English**: All documentation

## 🛠️ Development Workflow

### BSW-Tech Workflow
```
feature/bsw-tech-<id>-<description>
    ↓
  develop
    ↓
   main
```

### Commit Message Format
```
<type>: <description>

<body>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## 📊 Container Strategy

### Why apko + Wolfi?

| Aspect | Traditional (Alpine/Ubuntu) | apko + Wolfi |
|--------|----------------------------|--------------|
| **Size** | 400-1200MB | 15-50MB |
| **Build Time** | 5-15 minutes | 30-90 seconds |
| **Attack Surface** | High (200+ packages) | Minimal (10-20 packages) |
| **Vulnerability Scanning** | Daily | Continuous |
| **Supply Chain** | Moderate transparency | Full SBOM + signatures |

### Example Bot Container
```yaml
# apko.yaml
contents:
  packages:
    - wolfi-base
    - python-3.11
    - py3-crewai
entrypoint:
  command: /usr/bin/python3 /app/main.py
```

Result: **18MB** container vs traditional 450MB

## 🔗 Related Resources

### Codeberg Organizations

**Core Infrastructure:**
- [PIPE-Bots](https://codeberg.org/PIPE-Bots) - Pipeline and integration (48 bots)

**Business Domains:**
- [BNI-Bots](https://codeberg.org/BNI-Bots) - Business infrastructure (~37 bots)
- [BNP-Bots](https://codeberg.org/BNP-Bots) - Platform services (~37 bots)
- [BU-Bots](https://codeberg.org/BU-Bots) - Analytics and compliance (~42 bots)

**AI Domains:**
- [AXIS-Bots](https://codeberg.org/AXIS-Bots) - Architecture (45 bots)
- [IV-Bots](https://codeberg.org/IV-Bots) - Intelligence/LLM/RAG (44 bots)

**Specialized:**
- [ECO-Bots](https://codeberg.org/ECO-Bots) - Infrastructure (48 bots)
- [DC-Bots](https://codeberg.org/DC-Bots) - Digital content (~30 bots)

### Documentation

**Architecture**:
- [Enterprise CAG+RAG Solution Architecture](docs/architecture/ENTERPRISE-CAG-RAG-SOLUTION-ARCHITECTURE.md) - Multi-domain integration
- [Comprehensive Architecture Analysis](docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md) (145 pages)
- [Knowledge Base Architecture](docs/architecture/components/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md) (103KB)
- [IAC Alignment Report](docs/architecture/infrastructure/IAC-ALIGNMENT-REPORT.md) (75% aligned)

**Domain Guides**:
- [IV Domain Architecture](docs/architecture/domains/IV/IV-DOMAIN-ARCHITECTURE.md) - Intelligence & validation
- [IV CAG+RAG Implementation](docs/guides/bot-domains/IV-BOTS-CAG-RAG-IMPLEMENTATION.md) - Technical guide
- [ECO Domain Architecture](docs/architecture/domains/ECO/ECO-DOMAIN-ARCHITECTURE.md) - Infrastructure & resources
- [PIPE Bots Instructions](docs/guides/bot-domains/PIPE-BOTS-INSTRUCTIONS.md) - Pipeline domain

**Processes**:
- [Consolidation Strategy](docs/processes/github_docs_consolidation_strategy.md)

### External References
- [Chainguard Wolfi](https://github.com/wolfi-dev) - Secure base images
- [apko](https://github.com/chainguard-dev/apko) - Declarative container builds
- [CrewAI](https://github.com/joaomdmoura/crewai) - Multi-agent framework
- [OpenTofu](https://opentofu.org) - Open source Terraform alternative
- [Codeberg](https://codeberg.org) - FAGAM-free git hosting

## 📝 Contributing

### Adding Documentation
1. Create feature branch: `feature/bsw-tech-arch-<id>-<description>`
2. Add documentation to appropriate `docs/` subdirectory
3. Update `docs/INDEX.md` if adding new sections
4. Commit following BSW-Tech workflow
5. Merge: feature → develop → main

### Documentation Standards
- **Language**: UK English (favour, organise, colour)
- **Format**: Markdown with Mermaid diagrams
- **Line Length**: Max 120 characters
- **Headings**: Title case for H1, Sentence case for H2+
- **Code Blocks**: Always specify language

## 🎯 Use Cases

### For AI Bots
Clone this repository into bot containers to access comprehensive architectural knowledge:
```dockerfile
FROM cgr.dev/chainguard/wolfi-base:latest
RUN apk add git python-3.11
WORKDIR /opt
RUN git clone https://github.com/bsw-arch/bsw-arch.git documentation
ENV DOCS_PATH=/opt/documentation/docs
```

### For Multi-Tab Claude Workflows
Use documentation to instruct Claude across multiple tabs:
1. **Tab 1**: Architecture planning (reads `docs/architecture/`)
2. **Tab 2**: Bot implementation (reads `docs/specifications/bots/`)
3. **Tab 3**: Deployment (reads `docs/processes/deployment/`)
4. **Tab 4**: Validation (reads `docs/guides/security/`)

### For Knowledge Base Systems
Integrate with 2-Tier CAG+RAG system (IV domain):
- **Git Layer**: Version-controlled documentation (this repo)
- **CAG Layer**: Context-augmented generation (query classification, domain routing)
- **RAG Layer**: Hybrid retrieval (FAISS vectors, Neo4j graphs, MongoDB docs)
- **API Layer**: FastAPI MCP server for bot access
- **Bot Layer**: CrewAI agents consuming knowledge

See [IV CAG+RAG Implementation Guide](docs/guides/bot-domains/IV-BOTS-CAG-RAG-IMPLEMENTATION.md) for technical details.

## 📈 Roadmap

### Phase 1: Documentation Consolidation (Complete)
- ✅ Copied 17 core documents (~1MB)
- ✅ Created structured directory layout
- ✅ Generated INDEX.md and TREE.txt
- ✅ Pushed to GitHub

### Phase 2: Bot Integration (4 weeks)
- [ ] Update all 185 bots to clone documentation
- [ ] Add documentation reading capabilities
- [ ] Implement caching mechanisms
- [ ] Test bot access patterns

### Phase 3: CAG+RAG System Implementation (10 weeks)
- [x] Design 2-tier CAG+RAG architecture
- [x] Document implementation patterns
- [ ] Deploy hybrid retrieval engine (FAISS + Neo4j + MongoDB)
- [ ] Create FastAPI MCP service layer
- [ ] Implement context management (CAG layer)
- [ ] Integrate with all bot domains

### Phase 4: Continuous Improvement (Ongoing)
- [ ] Weekly documentation sync automation
- [ ] Bot feedback integration
- [ ] Performance optimization
- [ ] Knowledge base expansion

## 🆘 Support

### Questions?
- Review [docs/INDEX.md](docs/INDEX.md) for navigation
- Check [docs/reference/glossary/](docs/reference/glossary/) for terminology
- Read [docs/guides/](docs/guides/) for how-to guides

### Issues?
- IAC misalignment: See [docs/architecture/infrastructure/IAC-ALIGNMENT-REPORT.md](docs/architecture/infrastructure/IAC-ALIGNMENT-REPORT.md)
- Container builds: Check [docs/specifications/containers/](docs/specifications/containers/)
- Bot deployment: Review [docs/processes/deployment/](docs/processes/deployment/)

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Acknowledgements

- **Chainguard** for Wolfi and apko
- **Codeberg** for FAGAM-free git hosting
- **CrewAI** for multi-agent framework
- **Anthropic** for Claude Code assistance
- **OpenTofu/OpenBao** communities

---

**Last Updated**: 2025-11-10
**Documentation Version**: 1.0.0
**Maintained by**: BSW-Tech Architecture Team

**Repository Statistics**:
- 📚 Total Documents: 20+ core + domain-specific
- 💾 Total Size: ~1.5MB
- 🏗️ Directories: 30+
- 🤖 Bots Supported: 185 across 8 domains
- 🌐 Network Zones: 12+ segmented zones
- 🏛️ Architecture: 2-Tier CAG+RAG with cascaded processing
