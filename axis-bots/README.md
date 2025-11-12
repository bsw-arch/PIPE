# AXIS Bots - Architecture and Design Patterns

> Architecture Domain: 45 specialized bots for enterprise architecture, design patterns, validation, and strategic planning

**Version**: 1.0.0
**Last Updated**: 2025-11-12
**Domain**: AXIS (Architecture)
**Bot Count**: 45

## Overview

The AXIS (Architecture) domain manages enterprise architecture, design patterns, validation, compliance checking, and strategic planning for the BSW-Arch bot factory. This domain ensures architectural excellence across all 185 bots while maintaining TOGAF compliance, ArchiMate notation standards, and FAGAM prohibition requirements.

## Quick Start

### 1. Clone Documentation

```bash
# Clone documentation repository
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation

# Verify structure
ls /opt/documentation/docs
```

### 2. Install Dependencies

```bash
# Python dependencies
pip install -r axis-bots/examples/requirements.txt

# Or individual packages
pip install pyyaml requests anthropic pydantic crewai
```

### 3. Run Example Bot

```bash
# Set environment
export DOCS_PATH="/opt/documentation/docs"
export BOT_DOMAIN="AXIS"
export ANTHROPIC_API_KEY="your-api-key-here"

# Run documentation bot
python3 axis-bots/examples/axis_docs_bot.py

# Run validation bot
python3 axis-bots/examples/axis_validation_bot.py
```

### 4. Build Container

```bash
# Using Dockerfile
cd axis-bots/examples
docker build -f Dockerfile.axis-docs-bot -t axis-docs-bot:1.0.0 .

# Verify size (should be <50MB)
docker images axis-docs-bot:1.0.0
```

### 5. Deploy to Kubernetes

```bash
# Create namespace and setup
kubectl apply -f docs/templates/deployment/axis/axis-namespace-setup.yaml

# Deploy documentation bot
kubectl apply -f docs/templates/deployment/axis/axis-docs-bot.yaml

# Check status
kubectl get pods -n axis-bots
```

## Directory Structure

```
axis-bots/
├── examples/              # Example bot implementations
│   ├── axis_docs_bot.py
│   ├── axis_validation_bot.py
│   ├── axis_blueprint_bot.py
│   ├── axis_coordination_bot.py
│   ├── axis_assessment_bot.py
│   ├── Dockerfile.axis-docs-bot
│   └── requirements.txt
├── configs/               # Configuration files
│   └── axis-bot-list.yaml
└── README.md

docs/
├── architecture/
│   └── domains/
│       └── AXIS/
│           └── AXIS-DOMAIN-ARCHITECTURE.md
├── guides/
│   ├── AXIS-BOTS-SETUP-GUIDE.md
│   └── bot-domains/
│       └── AXIS-BOTS-INSTRUCTIONS.md
├── reference/
│   └── AXIS-BOTS-API-KEYS.md
└── specifications/
    ├── bots/
    │   └── axis/
    │       ├── axis-docs-bot.yaml
    │       ├── axis-validation-bot.yaml
    │       └── axis-coordination-bot.yaml
    └── containers/
        └── axis/
            ├── axis-base.yaml
            └── axis-docs-bot.yaml
```

## AXIS Bot Categories

### Architecture Framework Bots (12 bots)
| Bot Name | Purpose |
|----------|---------|
| **axis-docs-bot** | Documentation generation and maintenance |
| **axis-patterns-bot** | Design patterns library and recommendations |
| **axis-blueprint-bot** | System blueprints and reference architectures |
| **axis-framework-bot** | Enterprise architecture frameworks (TOGAF, Zachman) |
| **axis-standards-bot** | Standards compliance and enforcement |
| **axis-notation-bot** | ArchiMate notation and diagramming |
| **axis-modelling-bot** | Architecture modelling and simulation |
| **axis-repository-bot** | Architecture repository management |
| **axis-metamodel-bot** | Metamodel management and validation |
| **axis-viewpoint-bot** | Viewpoint generation and management |
| **axis-stakeholder-bot** | Stakeholder analysis and communication |
| **axis-catalog-bot** | Architecture catalogue management |

### Validation & Assessment Bots (10 bots)
| Bot Name | Purpose |
|----------|---------|
| **axis-validation-bot** | Architecture validation and compliance checking |
| **axis-assessment-bot** | System assessment and gap analysis |
| **axis-review-bot** | Design review automation |
| **axis-audit-bot** | Architecture audit and standards compliance |
| **axis-compliance-bot** | Regulatory and standard compliance |
| **axis-quality-bot** | Architecture quality assessment |
| **axis-governance-bot** | Governance policy enforcement |
| **axis-principles-bot** | Architecture principles validation |
| **axis-constraints-bot** | Constraint identification and management |
| **axis-requirements-bot** | Requirements traceability |

### Strategic & Planning Bots (8 bots)
| Bot Name | Purpose |
|----------|---------|
| **axis-strategy-bot** | Strategic architecture planning |
| **axis-planning-bot** | Architecture roadmap planning |
| **axis-risk-bot** | Risk assessment and mitigation |
| **axis-innovation-bot** | Innovation tracking and adoption |
| **axis-capability-bot** | Capability-based planning |
| **axis-roadmap-bot** | Technology roadmap management |
| **axis-portfolio-bot** | Portfolio management and optimization |
| **axis-investment-bot** | Investment analysis and prioritization |

### Coordination & Integration Bots (7 bots)
| Bot Name | Purpose |
|----------|---------|
| **axis-coordination-bot** | Multi-bot coordination and orchestration |
| **axis-integration-bot** | System integration patterns and services |
| **axis-gateway-bot** | API gateway management |
| **axis-orchestration-bot** | Workflow orchestration |
| **axis-collaboration-bot** | Cross-domain collaboration |
| **axis-federation-bot** | Federated architecture management |
| **axis-interoperability-bot** | Interoperability standards |

### Operational Bots (8 bots)
| Bot Name | Purpose |
|----------|---------|
| **axis-monitoring-bot** | Architecture monitoring and alerting |
| **axis-analytics-bot** | Architecture analytics and metrics |
| **axis-report-bot** | Reporting and documentation generation |
| **axis-kb-bot** | Knowledge base management |
| **axis-search-bot** | Architecture search and discovery |
| **axis-versioning-bot** | Version control and change management |
| **axis-migration-bot** | Migration planning and execution |
| **axis-transformation-bot** | Digital transformation management |

**Total**: 45 AXIS bots across 5 categories

## Key Architectural Requirements

### 1. TOGAF Compliance
All AXIS bots must comply with TOGAF 10 principles:
- Architecture Development Method (ADM)
- Architecture Content Framework
- Enterprise Continuum
- Architecture Capability Framework

### 2. ArchiMate Notation
Use ArchiMate 3.2 for all architecture diagrams:
- Strategy layer
- Business layer
- Application layer
- Technology layer
- Physical layer
- Motivation extension
- Implementation & Migration extension

### 3. FAGAM Prohibition
**Strictly Prohibited**:
- ❌ Google products (Cloud, Terraform, etc.)
- ❌ AWS proprietary services
- ❌ Microsoft Azure services
- ❌ HashiCorp products (use OpenTofu, OpenBao)
- ❌ Apple products
- ❌ Facebook/Meta products

**Approved Alternatives**:
- ✅ OpenTofu (instead of Terraform)
- ✅ OpenBao (instead of Vault)
- ✅ Chainguard Wolfi (base images)
- ✅ Codeberg (git hosting)
- ✅ CNCF projects
- ✅ Linux Foundation projects

### 4. Container Requirements
- **Maximum Size**: 50MB per container
- **Base Image**: Chainguard Wolfi (15MB typical)
- **Build Tool**: apko (declarative builds)
- **Security**: Full SBOM + signatures
- **Scanning**: Continuous vulnerability scanning

### 5. Documentation Standards
- **Language**: UK English (favour, organise, colour)
- **Format**: Markdown with Mermaid diagrams
- **Architecture Diagrams**: ArchiMate 3.2 or C4 model
- **Code Examples**: Python with type hints
- **Line Length**: Maximum 120 characters

## Recommended Workflows

### Workflow 1: New AXIS Bot Initialisation
```bash
# 1. Clone documentation
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation

# 2. Scan initial documents
python3 /opt/documentation/bot-utils/doc_scanner.py --action list --domain AXIS

# 3. Load bot-specific context
python3 axis-bots/examples/axis_docs_bot.py --init

# 4. Begin operation
python3 axis-bots/examples/axis_docs_bot.py --run
```

### Workflow 2: Architecture Validation
```bash
# 1. Set environment
export DOCS_PATH="/opt/documentation/docs"
export VALIDATION_MODE="strict"

# 2. Run validation bot
python3 axis-bots/examples/axis_validation_bot.py \
  --validate-architecture \
  --check-togaf-compliance \
  --check-fagam-prohibition \
  --check-container-sizes

# 3. Generate validation report
python3 axis-bots/examples/axis_validation_bot.py --report
```

### Workflow 3: Design Review
```bash
# 1. Load design patterns
python3 axis-bots/examples/axis_patterns_bot.py --load

# 2. Submit design for review
python3 axis-bots/examples/axis_review_bot.py \
  --design-file design.yaml \
  --check-patterns \
  --check-antipatterns

# 3. Generate review report
python3 axis-bots/examples/axis_review_bot.py --report
```

### Workflow 4: Multi-Bot Coordination
```bash
# 1. Define coordination plan
python3 axis-bots/examples/axis_coordination_bot.py \
  --plan coordination-plan.yaml

# 2. Execute coordinated workflow
python3 axis-bots/examples/axis_coordination_bot.py \
  --execute \
  --bots axis-validation-bot,axis-assessment-bot,axis-blueprint-bot

# 3. Aggregate results
python3 axis-bots/examples/axis_coordination_bot.py \
  --aggregate-results \
  --output results/
```

## Integration Points

### 1. META-KERAGR (Knowledge Graph)
```python
# Neo4j connection for architecture knowledge
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "password")
)

# Query architecture patterns
with driver.session() as session:
    result = session.run("""
        MATCH (pattern:DesignPattern)-[:APPLIES_TO]->(domain:Domain)
        WHERE domain.name = 'AXIS'
        RETURN pattern.name, pattern.description
    """)
```

### 2. Documentation Repository
```python
# Access architectural documentation
import requests

response = requests.get(
    "https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/INDEX.md"
)
docs_index = response.text
```

### 3. CrewAI Multi-Agent Coordination
```python
from crewai import Agent, Task, Crew

# Define AXIS agents
architect = Agent(
    role="Enterprise Architect",
    goal="Design compliant architectures",
    backstory="TOGAF-certified architect with 15+ years experience"
)

validator = Agent(
    role="Architecture Validator",
    goal="Ensure TOGAF and FAGAM compliance",
    backstory="Compliance specialist for architecture standards"
)

# Create coordinated crew
crew = Crew(
    agents=[architect, validator],
    tasks=[design_task, validation_task],
    verbose=True
)
```

### 4. Anthropic Claude Integration
```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

# Architecture analysis
response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": "Analyze this architecture for TOGAF compliance"
    }]
)
```

## API Endpoints

**Base URL**: `http://localhost:8086/api/v1/axis`

### Documentation Bot
```bash
POST   /docs/generate          # Generate documentation
PUT    /docs/update            # Update documentation
GET    /docs/status            # Documentation status
DELETE /docs/archive           # Archive old versions
```

### Validation Bot
```bash
POST   /validate/architecture  # Validate architecture
POST   /validate/togaf         # Check TOGAF compliance
POST   /validate/fagam         # Check FAGAM prohibition
GET    /validate/report        # Get validation report
```

### Coordination Bot
```bash
POST   /coordinate/plan        # Create coordination plan
POST   /coordinate/execute     # Execute coordinated workflow
GET    /coordinate/status      # Get coordination status
POST   /coordinate/aggregate   # Aggregate bot results
```

### Assessment Bot
```bash
POST   /assess/system          # Assess system architecture
POST   /assess/gaps            # Identify gaps
GET    /assess/report          # Get assessment report
POST   /assess/recommendations # Generate recommendations
```

## Environment Variables

```bash
# Documentation
export DOCS_PATH="/opt/documentation/docs"
export BOT_DOMAIN="AXIS"

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Knowledge Graph
export NEO4J_URI="neo4j://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="<from-vault>"

# Architecture Standards
export TOGAF_VERSION="10"
export ARCHIMATE_VERSION="3.2"
export FAGAM_CHECK="strict"
export CONTAINER_MAX_SIZE_MB="50"

# API Endpoints
export AXIS_API_URL="http://localhost:8086/api/v1/axis"
export META_KERAGR_URL="neo4j://localhost:7687"

# GitOps
export GIT_BRANCH_PREFIX="feature/bsw-tech-axis"
export GIT_WORKFLOW="feature->develop->main"
```

## Testing

### Unit Tests
```bash
# Run all tests
pytest axis-bots/tests/

# Run specific bot tests
pytest axis-bots/tests/test_docs_bot.py
pytest axis-bots/tests/test_validation_bot.py
```

### Integration Tests
```bash
# Test multi-bot coordination
pytest axis-bots/tests/integration/test_coordination.py

# Test META-KERAGR integration
pytest axis-bots/tests/integration/test_knowledge_graph.py
```

### Container Tests
```bash
# Build and test container
docker build -t axis-docs-bot:test .
docker run --rm axis-docs-bot:test pytest

# Check container size
docker images axis-docs-bot:test --format "{{.Size}}"
```

## Troubleshooting

### Problem: Cannot find documentation
```bash
# Check if repository is cloned
ls -la /opt/documentation

# If missing, clone it
cd /opt
git clone https://github.com/bsw-arch/bsw-arch.git documentation
```

### Problem: FAGAM violation detected
```bash
# Run FAGAM checker
python3 axis-bots/examples/axis_validation_bot.py --check-fagam

# Fix by replacing prohibited dependencies:
# ❌ terraform -> ✅ opentofu
# ❌ vault -> ✅ openbao
# ❌ alpine -> ✅ wolfi
```

### Problem: Container too large (>50MB)
```bash
# Check container size
docker images your-bot:latest

# Optimize:
# 1. Use Chainguard Wolfi base (15MB)
# 2. Multi-stage builds
# 3. Remove unnecessary dependencies
# 4. Use apko for declarative builds
```

### Problem: TOGAF validation fails
```bash
# Review TOGAF requirements
python3 axis-bots/examples/axis_framework_bot.py --togaf-check

# Generate compliance report
python3 axis-bots/examples/axis_validation_bot.py \
  --togaf-report \
  --output togaf-compliance-report.md
```

## Related Documentation

### Architecture Guides
- [AXIS Bots Setup Guide](../docs/guides/AXIS-BOTS-SETUP-GUIDE.md) - Complete setup instructions
- [AXIS Domain Architecture](../docs/architecture/domains/AXIS/) - Domain architecture
- [Comprehensive Bot Factory Architecture](../docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md) - 145-page analysis

### Reference Documentation
- [AXIS Bots API Keys](../docs/reference/AXIS-BOTS-API-KEYS.md) - API keys and configuration
- [TOGAF Compliance](../docs/reference/standards/TOGAF.md) - TOGAF requirements
- [ArchiMate Standards](../docs/reference/standards/ArchiMate.md) - Notation standards

### Templates
- [Bot Creation Template](../docs/templates/bot/axis/) - Bot template
- [Container Template](../docs/templates/container/axis/) - Container configuration
- [Deployment Template](../docs/templates/deployment/axis/) - Kubernetes deployment

## Contributing

### Adding New AXIS Bot
1. Create bot specification in `docs/specifications/bots/axis/`
2. Implement bot in `axis-bots/examples/`
3. Add configuration to `axis-bots/configs/axis-bot-list.yaml`
4. Create Dockerfile following container size requirements
5. Write tests in `axis-bots/tests/`
6. Update this README

### Code Standards
- Python 3.11+ with type hints
- Follow PEP 8 style guide
- Maximum line length: 120 characters
- Docstrings for all functions and classes
- UK English in comments and documentation

## Next Steps

1. ✅ Create AXIS bots directory structure
2. ✅ Create comprehensive documentation
3. ⏳ Implement 5 example AXIS bots
4. ⏳ Create axis-bot-list.yaml configuration
5. ⏳ Build and test containers (<50MB)
6. Deploy to Kubernetes cluster
7. Integrate with META-KERAGR knowledge graph
8. Set up continuous validation pipeline
9. Create remaining 40 AXIS bots
10. Full TOGAF compliance validation

## License

MIT License - See [LICENSE](../LICENSE) for details

---

**Status**: ✅ Infrastructure Complete - Ready for Bot Implementation
**Last Updated**: 2025-11-12
**Maintained By**: BSW-Tech Architecture Team

**Quick Links**:
- [Setup Guide](../docs/guides/AXIS-BOTS-SETUP-GUIDE.md)
- [Bot Examples](./README-BOT-EXAMPLES.md)
- [API Reference](../docs/reference/AXIS-BOTS-API-KEYS.md)
- [Codeberg Organization](https://codeberg.org/AXIS-Bots)
