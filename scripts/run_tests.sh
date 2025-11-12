#!/bin/bash
# Run tests with coverage

set -e

echo "Running PIPE Bot System Tests"
echo "=============================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
echo "Running unit tests..."
pytest tests/unit/ -v --cov=src --cov-report=term-missing

echo ""
echo "Running integration tests..."
pytest tests/integration/ -v

echo ""
echo "Generating coverage report..."
pytest tests/ --cov=src --cov-report=html --cov-report=xml

echo ""
echo "✓ All tests completed!"
echo "Coverage report: htmlcov/index.html"
