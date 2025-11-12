#!/bin/bash
# Start BSW AI Documentation Bots
# UK English spelling throughout

set -e

echo "🤖 Starting BSW AI Documentation Bots..."

# Check for Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY environment variable not set"
    echo "Please set your Anthropic API key:"
    echo "export ANTHROPIC_API_KEY='sk-ant-...'"
    exit 1
fi

echo "✅ Anthropic API key found"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ ERROR: Python 3.11+ required, found $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version $PYTHON_VERSION OK"

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install --quiet anthropic flask requests 2>/dev/null || {
    echo "Installing dependencies..."
    pip3 install anthropic flask requests
}

echo "✅ Dependencies installed"

# Check if port 8004 is available
if lsof -Pi :8004 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8004 already in use"
    echo "Attempting to stop existing service..."
    kill $(lsof -t -i:8004) 2>/dev/null || true
    sleep 2
fi

# Set working directory
cd "$(dirname "$0")"

# Create logs directory
mkdir -p /var/log/bsw-arch 2>/dev/null || mkdir -p ./logs

LOG_DIR="/var/log/bsw-arch"
if [ ! -w "$LOG_DIR" ]; then
    LOG_DIR="./logs"
fi

LOG_FILE="$LOG_DIR/documentation-bots.log"

echo "📝 Logging to: $LOG_FILE"

# Start documentation webhook integration
echo "🚀 Starting Documentation Bot Webhook Integration on port 8004..."

python3 documentation_webhook_integration.py > "$LOG_FILE" 2>&1 &
BOT_PID=$!

# Wait a moment for startup
sleep 2

# Check if service started successfully
if ! ps -p $BOT_PID > /dev/null; then
    echo "❌ ERROR: Documentation bots failed to start"
    echo "Check logs: tail -f $LOG_FILE"
    exit 1
fi

# Health check
echo "🔍 Running health check..."
sleep 1

HEALTH_STATUS=$(curl -s http://localhost:8004/health 2>/dev/null || echo "failed")

if [[ "$HEALTH_STATUS" == *"healthy"* ]]; then
    echo "✅ Documentation bots started successfully!"
    echo ""
    echo "📊 Service Information:"
    echo "   - Webhook endpoint: http://localhost:8004/webhook/documentation"
    echo "   - Health check: http://localhost:8004/health"
    echo "   - Bot status: http://localhost:8004/documentation/bots/status"
    echo "   - Test endpoint: http://localhost:8004/webhook/documentation/test"
    echo "   - Process ID: $BOT_PID"
    echo "   - Log file: $LOG_FILE"
    echo ""
    echo "🤖 Active Domain Bots:"
    curl -s http://localhost:8004/documentation/bots/status | python3 -m json.tool 2>/dev/null | grep -A1 '"bots"' || echo "   - AXIS, PIPE, IV, ECOX"
    echo ""
    echo "📋 Usage Examples:"
    echo ""
    echo "# Test AXIS bot:"
    echo "curl -X POST http://localhost:8004/webhook/documentation/test -H 'Content-Type: application/json' -d '{\"domain\": \"AXIS\"}'"
    echo ""
    echo "# Check status:"
    echo "curl http://localhost:8004/documentation/bots/status | jq"
    echo ""
    echo "# View logs:"
    echo "tail -f $LOG_FILE"
    echo ""
    echo "# Stop service:"
    echo "kill $BOT_PID"
    echo ""
    echo "✨ Documentation bots ready to generate UK English documentation!"
else
    echo "❌ ERROR: Health check failed"
    echo "Check logs: tail -f $LOG_FILE"
    kill $BOT_PID 2>/dev/null || true
    exit 1
fi

# Keep script running and show logs
echo "📖 Showing live logs (Ctrl+C to stop viewing, service continues):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -f "$LOG_FILE"
