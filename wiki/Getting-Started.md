# Getting Started with Platform Security Bot

This guide will help you get started with the **pipe-security-bot** autonomous AI agent.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+**: Required for running the bot
- **Docker & Docker Compose**: For containerised deployment
- **Git**: For repository management
- **SSH Key**: For Codeberg access

### System Requirements

- CPU: 2+ cores recommended
- RAM: 4GB minimum, 8GB recommended
- Storage: 10GB available space
- Network: Stable internet connection

## Installation

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone ssh://git@codeberg.org/PIPE-Bots/pipe-security-bot.git
cd pipe-security-bot

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Option 2: Manual Installation

```bash
# Clone the repository
git clone ssh://git@codeberg.org/PIPE-Bots/pipe-security-bot.git
cd pipe-security-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python src/main.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Bot Configuration
BOT_NAME=pipe-security-bot
BOT_MODE=autonomous

# META-KERAGR Connection
META_KERAGR_HOST=localhost
META_KERAGR_PORT=3108

# Coordination API
COORDINATION_HOST=localhost
COORDINATION_PORT=3111

# CrewAI Settings
CREWAI_ENABLED=true
CREWAI_MAX_AGENTS=5

# Security
TLS_ENABLED=true
RBAC_ENABLED=true
```

### Configuration File

Edit `config/config.yaml`:

```yaml
bot:
  name: pipe-security-bot
  mode: autonomous  # autonomous, collaborative, supervised, learning
  log_level: INFO

meta_keragr:
  host: localhost
  port: 3108
  timeout: 30

coordination:
  api_host: localhost
  api_port: 3111
  retry_attempts: 3

crewai:
  enabled: true
  max_agents: 5
  coordination_timeout: 60

security:
  tls_enabled: true
  rbac_enabled: true
  audit_logging: true
```

## First Steps

### 1. Verify Installation

```bash
# Check bot status
pipe-security-bot --status

# Run health check
pipe-security-bot --health
```

### 2. Test Connectivity

```bash
# Test META-KERAGR connection
pipe-security-bot test --keragr

# Test coordination API
pipe-security-bot test --coordination
```

### 3. Run First Operation

```bash
# Start in learning mode
pipe-security-bot start --mode learning

# Check logs
tail -f logs/pipe-security-bot.log
```

## Next Steps

- **[Architecture](Architecture)**: Understand the system design
- **[API Reference](API-Reference)**: Explore API capabilities
- **[Integration Guide](Integration-Guide)**: Connect with other bots
- **[Examples](Examples)**: See real-world usage examples

## Troubleshooting

If you encounter issues:

1. Check the [Troubleshooting Guide](Troubleshooting)
2. Review logs in `logs/pipe-security-bot.log`
3. Verify network connectivity to META-KERAGR
4. Ensure all dependencies are installed

## Support

- **Issues**: [Report on Codeberg](https://codeberg.org/PIPE-Bots/pipe-security-bot/issues)
- **Discussions**: [Community Forum](https://codeberg.org/PIPE-Bots/pipe-security-bot/discussions)

---

*Part of the Disconnect Collective - SECURE · RELIABLE · INDEPENDENT*
