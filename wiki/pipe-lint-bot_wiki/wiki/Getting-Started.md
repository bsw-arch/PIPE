# Getting Started with axis-task-bot

This guide will help you set up and start using the axis-task-bot in your AXIS architecture environment.

## Prerequisites

- **Python**: 3.11 or higher
- **META-KERAGR**: Knowledge graph service running on port 3108
- **Coordination API**: Bot coordination service on port 3111
- **API Keys**: Anthropic API key for Claude 3.5 Sonnet

## Installation

### 1. Clone Repository

```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no" \
  git clone git@codeberg.org:AXIS-Bots/axis-task-bot.git

cd axis-task-bot
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install anthropic requests crewai pydantic
```

### 3. Configure Environment

```bash
# Set API keys
export ANTHROPIC_API_KEY="sk-ant-..."

# Configure bot URLs
export KERAGR_URL="http://localhost:3108"
export COORDINATION_URL="http://localhost:3111"
```

## Quick Start

### Basic Usage

```python
from axis_bots import AxisTaskBot

# Initialise bot
bot = AxisTaskBot(
    keragr_url="http://localhost:3108",
    coordination_url="http://localhost:3111"
)

# Execute autonomous operation
result = bot.execute_autonomous({
    "task": "architecture_operation",
    "domain": "AXIS",
    "context": {"priority": "high"}
})

print(f"Status: {result.status}")
print(f"Result: {result.data}")
```

### Configuration File

Create `config/axis-task-bot.yml`:

```yaml
# Bot Configuration
bot:
  name: "axis-task-bot"
  version: "1.0.0"
  domain: "AXIS"

# Integration
integration:
  keragr_url: "http://localhost:3108"
  coordination_url: "http://localhost:3111"

# Performance
performance:
  timeout: 30
  retry_attempts: 3
  batch_size: 10

# Logging
logging:
  level: "INFO"
  format: "json"
  output: "/var/log/axis/axis-task-bot.log"
```

## Verification

### Health Check

```bash
curl http://localhost:3111/health/axis-task-bot
```

Expected response:
```json
{
  "status": "healthy",
  "bot": "axis-task-bot",
  "version": "1.0.0",
  "uptime": 3600,
  "last_operation": "2025-10-05T12:00:00Z"
}
```

### Test Operation

```python
# Test basic functionality
result = bot.test_operation()
assert result.status == "success"
print("✅ Bot is functioning correctly")
```

## Next Steps

- **[Architecture](Architecture)**: Understand the bot's architecture
- **[API Reference](API-Reference)**: Explore all available methods
- **[Examples](Examples)**: See real-world usage examples
- **[Integration Guide](Integration-Guide)**: Integrate with other AXIS bots

## Troubleshooting

**Bot fails to start:**
- Verify META-KERAGR is running: `curl http://localhost:3108/health`
- Check API key is set: `echo $ANTHROPIC_API_KEY`
- Review logs: `tail -f /var/log/axis/axis-task-bot.log`

**Connection timeouts:**
- Increase timeout in configuration
- Check network connectivity to services
- Verify firewall rules allow connections

**Authentication errors:**
- Regenerate API keys
- Verify Anthropic API key validity
- Check RBAC permissions

## Support

- **Issues**: [Report Issues](https://codeberg.org/AXIS-Bots/axis-task-bot/issues)
- **Documentation**: [Full Wiki](https://codeberg.org/AXIS-Bots/axis-task-bot/wiki)

---

*Part of the AXIS Bot Ecosystem - 46 Collaborative AI Agents for Enterprise Architecture*
