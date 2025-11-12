#!/bin/bash
# Start PIPE domain bots

set -e

echo "Starting PIPE Domain Bot System"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p state logs

# Start the bot system
echo ""
echo "Starting bots..."
python -m src.main
