#!/bin/bash
# Development environment setup script for PIPE
# This script sets up pre-commit hooks and development dependencies

set -e

echo "🚀 Setting up PIPE development environment..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Recommended: python3 -m venv venv && source venv/bin/activate"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install production dependencies
echo ""
echo "📦 Installing production dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Production dependencies installed"
else
    echo "⚠️  requirements.txt not found"
fi

# Install development dependencies
echo ""
echo "🛠️  Installing development dependencies..."
pip install \
    pytest \
    pytest-cov \
    pytest-asyncio \
    pytest-mock \
    black \
    isort \
    flake8 \
    flake8-docstrings \
    flake8-bugbear \
    pylint \
    mypy \
    bandit \
    pre-commit \
    safety \
    pydocstyle \
    detect-secrets

echo "✓ Development dependencies installed"

# Initialize detect-secrets baseline
echo ""
echo "🔐 Initializing secrets detection..."
if [ ! -f ".secrets.baseline" ]; then
    detect-secrets scan > .secrets.baseline
    echo "✓ Secrets baseline created"
else
    echo "✓ Secrets baseline already exists"
fi

# Install pre-commit hooks
echo ""
echo "🪝 Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg
echo "✓ Pre-commit hooks installed"

# Run pre-commit on all files (optional)
echo ""
read -p "Run pre-commit checks on all files now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running pre-commit on all files..."
    pre-commit run --all-files || true
fi

# Create useful git aliases
echo ""
echo "⚙️  Setting up useful git aliases..."
git config --local alias.test "!pytest tests/ -v"
git config --local alias.cov "!pytest tests/ --cov=src --cov-report=term-missing"
git config --local alias.lint "!pre-commit run --all-files"
echo "✓ Git aliases configured:"
echo "   - git test  : Run all tests"
echo "   - git cov   : Run tests with coverage"
echo "   - git lint  : Run all linters"

# Summary
echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Quick start:"
echo "  1. Make changes to code"
echo "  2. Run tests:    pytest tests/ -v"
echo "  3. Check coverage: pytest tests/ --cov=src"
echo "  4. Pre-commit will run automatically on git commit"
echo "  5. Manual check:   pre-commit run --all-files"
echo ""
echo "Happy coding! 🎉"
