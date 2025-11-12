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
- **📡 Event-Driven Architecture**: Loosely coupled bot communication via event bus
- **💾 State Management**: Persistent state storage with automatic recovery
- **📊 Metrics & Monitoring**: Built-in metrics collection and health checking
- **✅ Compliance Tracking**: Automated governance compliance monitoring
- **🔍 Review Pipeline**: Structured review process for cross-domain integrations
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

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Docker (optional, for containerized deployment)

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
│   │   └── monitor_bot.py
│   ├── utils/             # Utility modules
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── retry.py
│   ├── config/            # Configuration management
│   └── main.py            # Application entry point
├── tests/                 # Test suite
│   ├── unit/
│   └── integration/
├── config/                # Configuration files
├── scripts/               # Utility scripts
├── docs/                  # Documentation
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

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Considerations

- Use environment-specific configuration files
- Set up proper logging aggregation
- Configure persistent volumes for state
- Implement health check endpoints
- Set up monitoring and alerting

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
