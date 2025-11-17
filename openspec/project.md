# PIPE Domain Bot System - Project Context

## Project Overview

**PIPE** (Platform for Integration, Processing, and Execution) is an enterprise-grade bot automation framework with governance capabilities for the BSW Architecture project.

## Purpose

PIPE provides:
- **Bot Automation**: 4 specialized bots (Pipeline, DataProcessor, Monitor, IntegrationHub)
- **Governance System**: Enterprise-grade governance for 9-domain ecosystem
- **AI Memory**: Cognee-powered knowledge graph for learning from decisions
- **Cross-Domain Integration**: Hub-and-spoke topology with approval workflows
- **Compliance Tracking**: Automated compliance monitoring and reporting

## Technology Stack

### Core Technologies
- **Python 3.9+**: Primary language
- **AsyncIO**: Fully asynchronous architecture
- **Pydantic**: Type validation and DataPoints
- **PyYAML**: Configuration management

### Infrastructure (100% Open-Source)
- **OpenTofu**: Infrastructure as Code (NO Terraform!)
- **Ansible**: Configuration management
- **Helm**: Kubernetes package management
- **OpenBao**: Secrets management (NO Vault!)
- **Zitadel**: Identity and access management
- **Zot**: OCI container registry
- **Cosign**: Container image signing
- **Cilium**: eBPF-based networking
- **Cognee**: AI memory and knowledge graph

### Storage & Data
- **LanceDB**: Vector store for embeddings
- **NetworkX**: Graph store (lightweight)
- **JSON**: State persistence

### Testing & Quality
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage (71%+)
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

## Architecture

### Event-Driven Design
```
EventBus (Pub/Sub)
    ↓
Bots (4 types)
    ↓
StateManager (Persistence)
    ↓
MetricsCollector (Observability)
```

### Layered Architecture
1. **Core Layer**: BotBase, EventBus, StateManager
2. **Bot Layer**: PipelineBot, DataProcessorBot, MonitorBot, IntegrationHubBot
3. **Governance Layer**: GovernanceManager, DomainRegistry, ComplianceTracker, ReviewPipeline
4. **Integration Layer**: OpenBao, Zitadel, Cognee clients

### Domain Ecosystem
Nine domains in the BSW ecosystem:
- **BNI**: Blockchain Network Infrastructure
- **BNP**: Blockchain Network Protocol
- **AXIS**: Authentication and Identity Services
- **IV**: Identity Verification
- **EcoX**: Ecosystem Exchange
- **THRIVE**: Tokenized Health and Resilience
- **DC**: Data Commons
- **BU**: Business Units
- **PIPE**: Platform for Integration (central hub)

## Coding Conventions

### Python Style
- **PEP 8** compliance enforced by black and flake8
- **Type hints** required for all function signatures
- **Async/await** for all I/O operations
- **Docstrings** required for all public functions (Google style)

### Naming Conventions
- **Classes**: PascalCase (e.g., `BotBase`, `EventBus`)
- **Functions/Methods**: snake_case (e.g., `initialize`, `publish_event`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Private members**: Leading underscore (e.g., `_handle_event`)

### File Organization
```
src/
├── core/          # Core framework (base classes, event bus, state)
├── bots/          # Bot implementations
├── governance/    # Governance system
├── integrations/  # External integrations (OpenBao, Zitadel, Cognee)
├── monitoring/    # Observability
└── utils/         # Utilities
```

### Error Handling
- Use try/except blocks with specific exceptions
- Log errors with context using `self.logger.error()`
- Increment error metrics: `self.metrics.increment("errors")`
- Never silently catch exceptions

### Logging
- Use structured logging with context
- Levels: DEBUG, INFO, WARNING, ERROR
- Include bot name: `logging.getLogger(f"pipe.bot.{name}")`

### Testing
- Minimum 70% code coverage required
- Unit tests for all core components
- Integration tests for bot interactions
- Use pytest fixtures for reusable components
- Mock external dependencies

## Design Patterns

### Used Patterns
- **Abstract Factory**: BotBase for all bots
- **Pub/Sub**: EventBus for decoupled communication
- **Strategy**: Pluggable data processors
- **Template Method**: Bot lifecycle (initialize, execute, cleanup)
- **Singleton-like**: EventBus, StateManager instances
- **Decorator**: Retry decorator for resilience

### Forbidden Technologies
❌ **HashiCorp Vault** → Use OpenBao
❌ **HashiCorp Consul** → Use Kubernetes native
❌ **HashiCorp Terraform** → Use OpenTofu

## Development Workflow

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest --cov=src --cov-report=term-missing
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

### Running Bots
```bash
# Run locally
python -m src.main

# Run with Docker
docker-compose up
```

## Governance Workflow

### Integration Request Flow
1. Domain requests integration via GovernanceManager
2. Review created in ReviewPipeline
3. Compliance check via ComplianceTracker
4. Approval by reviewers
5. Integration activated
6. Logged to Cognee AI memory

### Compliance Categories
- Integration Standards
- Quality Metrics
- Security Policy
- Data Governance
- Review Process

## Performance Considerations

### Async Best Practices
- Use `asyncio.gather()` for parallel operations
- Implement backpressure in queues
- Use async locks for shared state
- Avoid blocking I/O in async functions

### Metrics to Monitor
- Event throughput (events/sec)
- Bot error rates
- Queue sizes
- Processing latency
- Memory usage

## Security

### Secrets Management
- All secrets in OpenBao (NO environment variables)
- Kubernetes service account authentication
- Dynamic secrets with TTL
- Encryption at rest and in transit

### Network Security
- Cilium network policies (zero-trust)
- Domain isolation (hub-and-spoke only)
- TLS everywhere
- Image signature verification (Cosign)

### Access Control
- Zitadel OIDC/OAuth 2.0
- Role-based access control (RBAC)
- Service account per bot
- Least privilege principle

## AI Memory (Cognee)

### DataPoint Types
- `DomainDataPoint`: Ecosystem domains
- `IntegrationDataPoint`: Cross-domain connections
- `ComplianceRecordDataPoint`: Compliance checks
- `ReviewDecisionDataPoint`: Review history
- `IntegrationPatternDataPoint`: Learned patterns

### Workflow
1. Add governance data to Cognee
2. Cognify to build knowledge graph
3. Search with semantic understanding
4. Learn from patterns over time

## Documentation Standards

### Required Documentation
- README.md: Project overview and quick start
- ARCHITECTURE.md: System architecture
- GOVERNANCE.md: Governance framework
- INFRASTRUCTURE.md: Infrastructure stack
- COGNEE_INTEGRATION.md: AI memory integration
- Inline docstrings: All public functions

### Markdown Style
- Use ATX-style headers (`# Header`)
- Code blocks with language specifiers
- Lists with consistent indentation
- Links to relevant sections

## Version Control

### Commit Messages
Use Conventional Commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test updates
- `chore:` Maintenance

### Branching
- `main`: Production-ready code
- `claude/*`: AI-generated feature branches
- Feature branches: Descriptive names

## Project Priorities

1. **Correctness**: Type safety, comprehensive testing
2. **Performance**: Async-first, efficient resource usage
3. **Security**: Zero-trust, secrets management, image signing
4. **Maintainability**: Clean code, documentation, patterns
5. **Observability**: Metrics, logging, health checks

## Future Considerations

- **Memify**: Add derived facts to knowledge graph (Cognee feature)
- **Advanced Search**: Implement all 12 Cognee search modes
- **Distributed Tracing**: OpenTelemetry integration
- **GraphQL API**: Governance query interface
- **ML Anomaly Detection**: Pattern-based issue detection
