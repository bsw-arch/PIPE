# PIPE Domain Bot System

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

> **Advanced bot automation framework with enterprise-grade governance for the PIPE domain within the BSW Architecture project**

## 🚀 Overview

The PIPE Domain Bot System is a comprehensive, production-ready bot automation framework designed for the BSW Architecture project. It provides a modular, extensible platform for building and managing automated bots for pipeline orchestration, data processing, system monitoring, and **cross-domain integration governance**.

### Key Features

- **🤖 Four Bot Types**: Pipeline automation, data processing, monitoring, and integration hub bots
- **🏛️ Enterprise Governance**: Full AgenticAI governance architecture with compliance tracking
- **🔌 Cross-Domain Integration**: Hub-and-spoke integration across 9 domains
- **🧠 AI Memory**: Cognee integration for governance intelligence and pattern learning
- **📡 Event-Driven Architecture**: Loosely coupled bot communication via event bus
- **💾 State Management**: Persistent state storage with automatic recovery
- **📊 Metrics & Monitoring**: Built-in metrics collection and health checking
- **✅ Compliance Tracking**: Automated governance compliance monitoring
- **🔍 Review Pipeline**: Structured review process for cross-domain integrations
- **📋 Spec-Driven Development**: OpenSpec specifications guide all implementation
- **🔄 Async/Await**: Fully asynchronous design for high performance
- **🐳 Docker Ready**: Complete containerization support
- **🧪 Well Tested**: Comprehensive unit and integration tests
- **📝 Type Hints**: Full type annotations for better IDE support

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Bot Types](#bot-types)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Contributing](#contributing)

---

## 🏗️ Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌──────────────────────────────────────────────┐
│          Bot Orchestrator                    │
├──────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────┐ │
│  │ Pipeline   │  │   Data     │  │Monitor │ │
│  │    Bot     │  │ Processor  │  │  Bot   │ │
│  └─────┬──────┘  └──────┬─────┘  └───┬────┘ │
│        │                │             │      │
│        └────────┬───────┴─────────────┘      │
│                 │                             │
│         ┌───────▼────────┐                   │
│         │   Event Bus    │                   │
│         └────────────────┘                   │
│                 │                             │
│    ┌────────────┼────────────┐               │
│    │            │            │               │
│ ┌──▼───┐  ┌────▼────┐  ┌────▼────┐          │
│ │State │  │Metrics  │  │Logging  │          │
│ │ Mgr  │  │Collector│  │ System  │          │
│ └──────┘  └─────────┘  └─────────┘          │
└──────────────────────────────────────────────┘
```

### Core Components

- **BotBase**: Abstract base class for all bots
- **EventBus**: Pub-sub messaging system for inter-bot communication
- **StateManager**: Persistent state storage and recovery
- **MetricsCollector**: Metrics aggregation and reporting

---

## 🤖 Bot Types

### 1. Pipeline Bot

Orchestrates automated pipelines and workflows.

**Features:**
- CI/CD pipeline management
- Stage-based execution
- Pipeline scheduling
- Retry mechanisms
- Pipeline state tracking

**Use Cases:**
- Build and deployment automation
- Data processing pipelines
- Workflow orchestration

### 2. Data Processor Bot

Processes and transforms data streams.

**Features:**
- Multi-worker processing
- Pluggable data processors
- Queue-based architecture
- Support for JSON, CSV, text, and custom formats
- Data transformation and validation

**Use Cases:**
- ETL operations
- Data ingestion
- Real-time data processing
- Data validation

### 3. Monitor Bot

Monitors system health and performance.

**Features:**
- Bot health monitoring
- Metrics collection
- Alert generation
- System health scoring
- Event tracking

**Use Cases:**
- System monitoring
- Performance tracking
- Alerting and notifications
- Health dashboards

### 4. Integration Hub Bot ⭐ NEW

Manages cross-domain integration and enterprise governance.

**Features:**
- Cross-domain message routing
- Integration governance and compliance
- Review pipeline orchestration
- Domain registry management
- Quality dashboard aggregation
- 9-domain ecosystem support

**Supported Domains:**
BNI, BNP, AXIS, IV, EcoX, THRIVE, DC, BU, PIPE

**Use Cases:**
- Enterprise integration management
- Cross-domain communication
- Governance compliance tracking
- Integration quality monitoring

**📖 Full Documentation:** See [GOVERNANCE.md](docs/GOVERNANCE.md)

---

## 🏗️ Cloud-Native Infrastructure Stack

PIPE uses a **27-technology** open-source stack aligned with **EuroStack** (European digital sovereignty) principles:

### 📊 Stack Overview

**27 Technologies** across 7 capability layers:
- 🔨 Development (3): OpenSpec, PR-QUEST, Cognee
- 📦 Container Tooling (4): Podman, Buildah, Skopeo, Cosign
- 🔐 Security (5): OpenBao, Zitadel, Trivy, Syft, Grype
- 📡 Networking (2): Cilium, Zot
- 📊 Observability (4): Prometheus, Grafana, Loki, Tempo
- 🚀 GitOps (3): ArgoCD, OpenTofu, Ansible
- 🛡️ Policy (3): OPA, Kyverno, Helm
- 💾 Storage (2): Longhorn, MinIO
- 🔄 Backup (1): Velero

**CNCF Projects: 8** (6 graduated, 1 incubating, 1 sandbox)

### ✅ By Capability

#### Development & AI
- **OpenSpec** - Spec-driven development methodology (Fission-AI)
- **PR-QUEST** - LLM-powered PR review with gamification (Fission-AI)
- **Cognee** - AI memory and knowledge graph

#### Container Tooling (Docker-Free!)
- **Podman** - Daemonless container runtime (replaces Docker)
- **Buildah** - OCI image building without daemon
- **Skopeo** - Container image operations (copy, inspect, sign)
- **Cosign** - Container image signing and verification

#### Security & Identity
- **OpenBao** - Secrets management (Vault fork, NO HASHICORP!)
- **Zitadel** - Identity and access management (OAuth2/OIDC)
- **Trivy** - Comprehensive vulnerability scanner
- **Syft** - SBOM (Software Bill of Materials) generation
- **Grype** - Alternative vulnerability scanner

#### Observability (LGTM Stack)
- **Prometheus** - Metrics collection and alerting (CNCF Graduated)
- **Grafana** - Visualization and dashboards
- **Loki** - Log aggregation (like Prometheus for logs)
- **Tempo** - Distributed tracing (OpenTelemetry)

#### GitOps & Automation
- **ArgoCD** - Declarative GitOps continuous delivery (CNCF Graduated)
- **OpenTofu** - Infrastructure as Code (Terraform fork, NO HASHICORP!)
- **Ansible** - Configuration management

#### Policy & Compliance
- **OPA** - General-purpose policy engine (CNCF Graduated)
- **Kyverno** - Kubernetes-native policy management (CNCF Incubating)
- **Helm** - Kubernetes package manager (CNCF Graduated)

#### Networking & Registry
- **Cilium** - eBPF-based CNI with network policies (CNCF Graduated)
- **Zot** - OCI-native container registry

#### Storage
- **Longhorn** - Distributed block storage (CNCF Sandbox)
- **MinIO** - S3-compatible object storage

#### Backup & DR
- **Velero** - Kubernetes backup and restore (CNCF Graduated)

### ❌ Forbidden Technologies

**NO US Tech Giants / Proprietary Licensing:**

- ❌ **HashiCorp Vault** → Use **OpenBao** instead
- ❌ **HashiCorp Consul** → Use **Kubernetes native** service discovery
- ❌ **HashiCorp Terraform** → Use **OpenTofu** instead
- ❌ **Docker Desktop** → Use **Podman/Buildah** instead
- ❌ **Elastic Stack** → Use **Loki** instead (lighter, open-source)

### 🇪🇺 EuroStack Alignment

PIPE achieves **100% compliance** with **EuroStack** (European digital sovereignty initiative):
- ✅ **Digital Sovereignty** - Independence from US tech giants (NO HashiCorp, Docker, AWS)
- ✅ **100% Open-Source** - All 27 technologies are open-source (15 with Apache 2.0)
- ✅ **Self-Hosted** - All components run in our infrastructure
- ✅ **Data Sovereignty** - All data stays in Europe
- ✅ **Kubernetes-Native** - Modern cloud-native approach (alternative to OpenStack)
- ✅ **CNCF Ecosystem** - 8 CNCF projects (6 graduated, 1 incubating, 1 sandbox)
- ✅ **Green Computing** - Efficient eBPF (Cilium), lightweight components
- ✅ **Community-Driven** - Contributing back to upstream projects

**EuroStack Initiative**: €300 billion European sovereign cloud infrastructure
**Sovereign Cloud Stack (SCS)**: Reference implementation with OpenStack + Kubernetes
**PIPE Approach**: Kubernetes-native (85% SCS-compatible, 100% EuroStack-aligned)

**📖 Complete Stack Documentation**: See [CLOUD_NATIVE_STACK.md](docs/CLOUD_NATIVE_STACK.md)
**📖 EuroStack Alignment Analysis**: See [EUROSTACK_ALIGNMENT.md](docs/EUROSTACK_ALIGNMENT.md)

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Kubernetes cluster (with Cilium CNI)
- OpenTofu 1.6+
- Ansible 2.9+
- Helm 3.x
- kubectl

### Local Installation

```bash
# Clone the repository
git clone <repository-url>
cd PIPE

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Docker Installation

```bash
# Build Docker image
docker build -t pipe-bots:latest .

# Run with Docker Compose
docker-compose up -d
```

---

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from src.main import BotOrchestrator
from src.config.config_loader import load_config

async def main():
    # Load configuration
    config = load_config()

    # Create orchestrator
    orchestrator = BotOrchestrator(config)

    # Initialize and start bots
    await orchestrator.initialize_bots()
    await orchestrator.start_bots()

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the System

```bash
# Using Python directly
python -m src.main

# Using Docker
docker-compose up

# Running tests
pytest tests/ -v
```

---

## ⚙️ Configuration

Configuration is managed through YAML files in the `config/` directory.

### config/config.yaml

```yaml
# State management
state_dir: "./state"

# Logging configuration
logging:
  level: "INFO"
  file: "./logs/pipe_bots.log"

# Bot configurations
bots:
  pipeline:
    enabled: true
    check_interval: 30
    default_pipelines: []

  data_processor:
    enabled: true
    num_workers: 3
    status_interval: 30

  monitor:
    enabled: true
    monitor_interval: 60
    health_check_interval: 30
```

### Environment Variables

Override configuration with environment variables:

```bash
export PIPE_LOG_LEVEL=DEBUG
export PIPE_STATE_DIR=/custom/state/dir
```

---

## 🛠️ Development

### Project Structure

```
PIPE/
├── src/
│   ├── core/              # Core framework components
│   │   ├── bot_base.py
│   │   ├── event_bus.py
│   │   └── state_manager.py
│   ├── bots/              # Bot implementations
│   │   ├── pipeline_bot.py
│   │   ├── data_processor_bot.py
│   │   ├── monitor_bot.py
│   │   └── integration_hub_bot.py
│   ├── governance/        # Governance system
│   ├── integrations/      # Infrastructure integrations (NEW)
│   │   ├── openbao_client.py    # OpenBao secrets
│   │   └── zitadel_client.py    # Zitadel IAM
│   ├── utils/             # Utility modules
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── retry.py
│   ├── config/            # Configuration management
│   └── main.py            # Application entry point
├── infrastructure/        # Infrastructure as Code (NEW)
│   ├── opentofu/         # OpenTofu modules
│   ├── ansible/          # Ansible playbooks
│   └── cilium/           # Cilium network policies
├── charts/               # Helm charts (NEW)
│   └── pipe-bots/       # PIPE deployments
├── scripts/              # Deployment scripts (NEW)
│   ├── cosign/          # Image signing
│   └── zot/             # Registry deployment
├── tests/                # Test suite
│   ├── unit/
│   └── integration/
├── config/               # Configuration files
├── openspec/             # Spec-driven development (NEW)
│   ├── project.md        # Project context for AI
│   ├── specs/            # Behavioral specifications
│   │   ├── bots/spec.md
│   │   ├── governance/spec.md
│   │   └── integrations/spec.md
│   └── changes/          # Change proposals
│       └── example-add-memify-support/
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md
│   ├── GOVERNANCE.md
│   ├── INFRASTRUCTURE.md
│   ├── COGNEE_INTEGRATION.md   # NEW
│   └── OPENSPEC_GUIDE.md       # NEW
├── examples/             # Example implementations (NEW)
│   └── cognee/          # Cognee AI examples
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
pylint src/

# Type checking
mypy src/
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_event_bus.py -v

# Run integration tests only
pytest tests/integration/ -v
```

### Test Coverage

The project maintains >80% test coverage across:
- Unit tests for core components
- Integration tests for bot interactions
- End-to-end workflow tests

---

## 🚢 Deployment

### Production Deployment

```bash
# 1. Provision infrastructure with OpenTofu (NOT Terraform!)
cd infrastructure/opentofu
tofu init
tofu plan -out=tfplan
tofu apply tfplan

# 2. Deploy with Ansible
cd ../ansible
ansible-playbook -i inventory/production deploy-pipe.yml

# 3. Or deploy directly with Helm
helm install pipe-bots charts/pipe-bots/ -n pipe-bots --create-namespace
```

### Sign Container Images

```bash
# Generate Cosign keypair
./scripts/cosign/sign-images.sh generate-keypair

# Sign all PIPE images
./scripts/cosign/sign-images.sh sign v1.0.0

# Verify signature
./scripts/cosign/sign-images.sh verify v1.0.0 zot.pipe.local/pipe/pipeline-bot:v1.0.0
```

### Docker Deployment (Local)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Considerations

- Use OpenBao for all secrets (NO Vault!)
- Deploy Cilium CNI for network policies
- Enforce Cosign signature verification
- Configure Zitadel for authentication
- Use Zot registry for container images
- Set up proper logging aggregation
- Configure persistent volumes for state
- Implement health check endpoints
- Set up Prometheus/Grafana monitoring

---

## 📋 Spec-Driven Development with OpenSpec

PIPE uses **OpenSpec** for spec-driven development, providing:

- **Living Specifications**: Gherkin-style requirements that guide implementation
- **Change Proposals**: Structured process for proposing features
- **AI Context**: Comprehensive project context for AI assistants
- **Test-Driven Development**: Specs drive both code and tests

### Quick Start

**1. Read existing specifications:**
```bash
# Bot system specifications
cat openspec/specs/bots/spec.md

# Governance workflow specifications
cat openspec/specs/governance/spec.md

# Infrastructure integration specifications
cat openspec/specs/integrations/spec.md
```

**2. Propose a change:**
```bash
# See example proposal
cat openspec/changes/example-add-memify-support/proposal.md
```

**3. Implement from spec:**
```python
# Code references spec line numbers
async def authenticate_kubernetes(self, jwt_path: str = None) -> bool:
    """
    Authenticate to OpenBao using Kubernetes service account.

    Implements: openspec/specs/integrations/spec.md:11-15
    """
    # Implementation follows spec exactly
    ...
```

### Specification Example

```gherkin
### Requirement: OpenBao Secrets Management
The system SHALL use OpenBao for all secrets management.

#### Scenario: Kubernetes authentication
- GIVEN a bot runs in Kubernetes
- WHEN it needs to access secrets
- THEN it SHALL authenticate using service account JWT
- AND receive a time-limited token
```

**📖 Full Guide:** See [OPENSPEC_GUIDE.md](docs/OPENSPEC_GUIDE.md)

---

## 🧠 AI Memory with Cognee

PIPE integrates **Cognee** for governance intelligence:

- **Semantic Search**: Find similar integrations, compliance issues, and review decisions
- **Knowledge Graph**: Navigate relationships between domains, integrations, and reviews
- **Pattern Learning**: Learn from historical decisions to suggest optimal paths
- **Derived Facts**: Generate insights from governance data (via Memify)

### Three-Store Architecture

```
┌─────────────────────────────────────────────┐
│         Cognee AI Memory                     │
├─────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────┐  ┌────────┐ │
│  │ Relational  │  │  Vector  │  │ Graph  │ │
│  │   Store     │  │  Store   │  │ Store  │ │
│  │             │  │          │  │        │ │
│  │ Provenance  │  │Embeddings│  │ Edges  │ │
│  │ Versioning  │  │ Semantic │  │Relations│ │
│  └─────────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────┘
```

### Quick Example

```python
from src.integrations.cognee_client import get_cognee_client
from src.governance.datapoints import IntegrationDataPoint

# Add governance data
client = await get_cognee_client()
integration = IntegrationDataPoint(
    integration_id="INT-001",
    source_domain="BNI",
    target_domain="PIPE",
    integration_type="hub",
    description="Hub connection for blockchain data flow",
    status="connected"
)

await client.add_datapoints([integration])
await client.cognify_governance_data()

# Semantic search
results = await client.search_integrations(
    "hub integrations for blockchain domains",
    limit=5
)

# Suggest integration path
suggestion = await client.suggest_integration_path("EcoX", "PIPE")
print(f"Confidence: {suggestion['confidence']:.2f}")
```

### DataPoint Types

PIPE provides 8 custom DataPoint types:

1. **DomainDataPoint** - Ecosystem domains (BNI, BNP, AXIS, etc.)
2. **IntegrationDataPoint** - Cross-domain integrations
3. **ComplianceRecordDataPoint** - Compliance tracking
4. **ReviewDecisionDataPoint** - Governance review decisions
5. **IntegrationPatternDataPoint** - Learned integration patterns
6. **DomainCapabilityDataPoint** - Domain-specific capabilities
7. **GovernancePolicyDataPoint** - Governance policies
8. **PRReviewDataPoint** - PR-QUEST code reviews (NEW)

**📖 Full Documentation:** See [COGNEE_INTEGRATION.md](docs/COGNEE_INTEGRATION.md)

**🔬 Examples:** See [examples/cognee/governance_memory.py](examples/cognee/governance_memory.py)

---

## 🔍 Automated PR Review with PR-QUEST

PIPE integrates **PR-QUEST** for LLM-powered code review of integration PRs:

- **Smart Clustering**: LLM groups related code changes into logical clusters
- **Risk Detection**: Automatic identification of security issues, breaking changes, and anti-patterns
- **Quality Gates**: Block problematic PRs before merge
- **Gamification**: XP system encourages thorough reviews
- **Pattern Learning**: Store reviews in Cognee to learn from history

### PR Review Workflow

```
┌──────────────────────────────────────────────────┐
│       Integration PR Review Workflow              │
├──────────────────────────────────────────────────┤
│                                                   │
│  1. Developer creates PR                          │
│  2. PR Review Bot detects new PR                  │
│  3. PR-QUEST analyzes code changes                │
│     • LLM clusters related changes                │
│     • Detects risks (security, breaking changes)  │
│     • Generates fix suggestions                   │
│  4. Bot determines decision                       │
│     • APPROVE → Auto-merge (clean PRs)            │
│     • REJECT → Block merge (critical risks)       │
│     • NEEDS_REVIEW → Assign to human             │
│  5. Store review in Cognee                        │
│     • Learn from patterns                         │
│     • Improve future reviews                      │
│                                                   │
└──────────────────────────────────────────────────┘
```

### Quick Example

```python
from src.integrations.pr_quest_client import get_pr_quest_client
from src.integrations.pr_quest_models import determine_decision_from_analysis

# Initialize PR-QUEST client
client = await get_pr_quest_client("http://localhost:3000")

# Analyze a GitHub PR
result = await client.analyze_pr(
    "https://github.com/bsw-arch/PIPE/pull/123",
    include_llm_analysis=True  # Use LLM for smart clustering
)

# Check results
print(f"Clusters: {len(result.clusters)}")
print(f"Risks: {len(result.risks)} ({result.overall_risk_level})")
print(f"XP Awarded: {result.xp_awarded}")

# Determine decision
decision = determine_decision_from_analysis(result)
if decision.value == "APPROVE":
    print("✅ Auto-approved - No risks detected")
elif decision.value == "REJECT":
    print("❌ Auto-rejected - Critical risks found")
else:
    print("⏸️  Flagged for human review")

# Export as markdown for documentation
markdown = await client.export_markdown(result.analysis_id)
```

### Risk Detection Categories

PR-QUEST detects:

1. **SECURITY** - SQL injection, XSS, insecure dependencies
2. **BREAKING_CHANGE** - API changes that break compatibility
3. **ANTI_PATTERN** - Code smells and architectural issues
4. **PERFORMANCE** - Inefficient algorithms, memory leaks
5. **COMPLIANCE** - Policy violations, missing documentation
6. **MAINTAINABILITY** - High complexity, poor readability
7. **TESTING** - Insufficient test coverage

### Integration with Cognee

All PR reviews are stored in Cognee (8th DataPoint type: `PRReviewDataPoint`):

```python
# PR reviews are automatically stored after analysis
# Search for similar past issues
similar = await cognee_client.search_integrations(
    "PR reviews with SQL injection risks",
    limit=5
)

# Learn from historical patterns
suggestion = await cognee_client.suggest_integration_path(
    "BNI", "PIPE"
)  # Includes insights from past PR reviews
```

**📖 Full Documentation:** See [PR_QUEST_INTEGRATION.md](docs/PR_QUEST_INTEGRATION.md) *(coming soon)*

**🔬 Examples:** See [examples/pr_quest/review_integration_pr.py](examples/pr_quest/review_integration_pr.py)

**🎮 GitHub**: [Fission-AI/PR-QUEST](https://github.com/Fission-AI/PR-QUEST)

---

## 📚 API Reference

### BotBase

Base class for all bots.

```python
class BotBase(ABC):
    async def initialize(self) -> bool
    async def execute(self) -> None
    async def cleanup(self) -> None
    async def start(self) -> None
    async def stop(self) -> None
    def get_status(self) -> Dict[str, Any]
```

### EventBus

Event-driven communication system.

```python
class EventBus:
    def subscribe(self, event_type: str, callback: Callable)
    async def publish(self, event: Event)
    def get_history(self, event_type: str = None) -> List[Event]
```

### StateManager

Persistent state management.

```python
class StateManager:
    async def load_state(self, bot_name: str) -> Dict[str, Any]
    async def save_state(self, bot_name: str, state_data: Dict)
    async def get_value(self, bot_name: str, key: str)
    async def set_value(self, bot_name: str, key: str, value: Any)
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/`)
6. Format code (`black src/ tests/`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

---

## 📄 License

This project is part of the BSW Architecture project.

---

## 📧 Contact

For questions or support, please contact the BSW Architecture team.

---

## 🙏 Acknowledgments

- BSW Architecture team
- Contributors and maintainers
- Open source community

---

**Built with ❤️ for the BSW Architecture PIPE Domain**

**Made with 100% open-source technologies - NO HASHICORP PRODUCTS!**

---

## 🔐 Infrastructure Integrations

### OpenBao (Secrets Management)

```python
from integrations.openbao_client import get_openbao_client

# Authenticate with Kubernetes
client = await get_openbao_client(
    address="http://openbao-system.svc.cluster.local:8200",
    kubernetes_role="pipe-bot"
)

# Read secrets
secret = await client.read_secret("secret/data/pipe/config")

# Encrypt data
ciphertext = await client.encrypt("sensitive data")

# Generate TLS certificate
cert = await client.generate_certificate("pipe.local", ttl="24h")
```

### Zitadel (Identity & Access Management)

```python
from integrations.zitadel_client import get_zitadel_client

# Get access token
client = await get_zitadel_client(
    issuer="https://zitadel-system.svc.cluster.local",
    client_id="pipe-bot"
)

token = await client.get_access_token()

# Verify token
claims = await client.verify_token(user_token)

# Check permissions
has_perm = await client.check_permission(user_id, "integration-reviewer")
```
