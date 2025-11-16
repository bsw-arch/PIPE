# CI/CD Pipeline Setup Guide

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the PIPE project.

## Overview

The PIPE project uses GitHub Actions for automated testing, code quality checks, and deployment. The pipeline ensures code quality, runs comprehensive tests, and provides coverage reports.

## Table of Contents

- [Quick Start](#quick-start)
- [Pipeline Components](#pipeline-components)
- [Pre-commit Hooks](#pre-commit-hooks)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Coverage Reporting](#coverage-reporting)
- [Security Scanning](#security-scanning)
- [Branch Protection](#branch-protection)
- [Local Development](#local-development)

## Quick Start

### For Developers

```bash
# 1. Clone the repository
git clone <repository-url>
cd PIPE

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Run setup script
./scripts/setup-dev.sh

# 4. Make changes and commit
git add .
git commit -m "Your changes"  # Pre-commit hooks run automatically
```

## Pipeline Components

### 1. Code Quality Checks (Linting)

Runs on every push and pull request to main, develop, and claude/** branches.

**Tools:**
- **Black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **Flake8**: Linting and style guide enforcement
- **Pylint**: Additional code analysis
- **MyPy**: Static type checking

**Configuration:** See `pyproject.toml` for tool-specific settings.

### 2. Testing

Tests run on multiple Python versions (3.10, 3.11, 3.12) to ensure compatibility.

**Test Types:**
- **Unit Tests**: Fast, isolated tests (`tests/unit/`)
- **Integration Tests**: Cross-module tests (`tests/integration/`)

**Commands:**
```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### 3. Coverage Reporting

Coverage target: **71%+** (currently at 71%)

**Coverage Locations:**
- Terminal output during test runs
- HTML report in `htmlcov/` directory
- Uploaded to Codecov (on PR/push to main)
- GitHub Actions summary

**View Coverage:**
```bash
# Generate and open HTML report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### 4. Security Scanning

**Tools:**
- **Safety**: Checks for known security vulnerabilities in dependencies
- **Bandit**: Scans Python code for security issues
- **detect-secrets**: Prevents committing secrets

**Manual Security Scan:**
```bash
# Check dependencies
safety check

# Scan code
bandit -r src/ -f json -o security-report.json

# Check for secrets
detect-secrets scan
```

### 5. Build Verification

Verifies that:
- Docker image builds successfully
- All Python modules can be imported
- No circular dependencies exist

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit to catch issues early.

### Installation

```bash
pip install pre-commit
pre-commit install
```

### Hooks Configured

1. **Trailing whitespace** - Remove trailing spaces
2. **End of file fixer** - Ensure files end with newline
3. **YAML/JSON/TOML checks** - Validate syntax
4. **Large file check** - Prevent committing large files (>1MB)
5. **Merge conflict check** - Detect merge conflict markers
6. **Private key detection** - Prevent committing SSH keys
7. **Black** - Auto-format Python code
8. **isort** - Sort imports
9. **Flake8** - Lint code
10. **Bandit** - Security checks
11. **MyPy** - Type checking
12. **Pytest** - Run unit tests

### Manual Execution

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for a commit (not recommended)
git commit --no-verify -m "Emergency fix"
```

### Configuration

Pre-commit configuration: `.pre-commit-config.yaml`
Tool settings: `pyproject.toml`

## GitHub Actions Workflows

### Main CI Workflow (`.github/workflows/ci.yml`)

Triggered on:
- Push to `main`, `develop`, `claude/**`
- Pull requests to `main`, `develop`

**Jobs:**

1. **lint** - Code quality checks
   - Runtime: ~2-3 minutes
   - Tools: Black, isort, Flake8, Pylint, MyPy

2. **test** - Run test suite
   - Runtime: ~3-5 minutes per Python version
   - Matrix: Python 3.10, 3.11, 3.12
   - Outputs: Test results, coverage reports

3. **coverage** - Generate coverage reports
   - Runtime: ~2-3 minutes
   - Uploads to Codecov
   - Creates HTML artifacts

4. **security** - Security scanning
   - Runtime: ~2-3 minutes
   - Runs Safety and Bandit
   - Generates security reports

5. **build** - Verify build
   - Runtime: ~3-5 minutes
   - Builds Docker image
   - Verifies imports

**Total Pipeline Time:** ~10-15 minutes

### Deploy Workflow (`.github/workflows/deploy.yml`)

Triggered on:
- Tag pushes (`v*`)
- Manual workflow dispatch

**Not yet configured** - placeholder for future deployment automation.

## Coverage Reporting

### Current Coverage: 71%

**High Coverage Modules (>80%):**
- `monitoring/metrics_server.py` - 100%
- `config/config_loader.py` - 98%
- `utils/metrics.py` - 97%
- `core/event_bus.py` - 93%
- `utils/retry.py` - 92%
- `domain_registry.py` - 90%
- `review_pipeline.py` - 90%

**Modules Needing Coverage:**
- `main.py` - 0%
- `monitoring/health_checker.py` - 79%
- `monitoring/prometheus_exporter.py` - 79%
- `core/state_manager.py` - 78%

**Coverage Goals:**
- Overall: Maintain >70%, target 80%
- New code: >80% coverage required
- Critical paths: >90% coverage

### Viewing Coverage

**Locally:**
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

**In GitHub:**
1. Go to Actions tab
2. Click on latest workflow run
3. Check "Summary" for coverage percentage
4. Download "coverage-report-html" artifact

**Codecov Dashboard:**
- Available at: `https://codecov.io/gh/<org>/PIPE`
- Provides historical trends and PR comparisons

## Security Scanning

### Dependency Scanning (Safety)

Checks all dependencies against known vulnerability databases.

**Manual Run:**
```bash
safety check --json
```

**In CI:** Runs automatically on every push

### Code Security (Bandit)

Scans Python code for common security issues:
- SQL injection
- Shell injection
- Hardcoded passwords
- Insecure random functions
- etc.

**Manual Run:**
```bash
bandit -r src/ -f json -o bandit-report.json
```

**In CI:** Runs automatically on every push

### Secrets Detection

Prevents committing sensitive data (API keys, passwords, tokens).

**Setup:**
```bash
# Initialize baseline
detect-secrets scan > .secrets.baseline

# Audit findings
detect-secrets audit .secrets.baseline
```

**In Pre-commit:** Scans every commit

## Branch Protection

### Recommended Rules for `main` branch:

```yaml
Required status checks:
  - lint
  - test (Python 3.11)
  - coverage
  - security

Required reviews: 1

Additional settings:
  - Require branches to be up to date
  - Include administrators
  - Restrict push access
  - Require signed commits (optional)
```

### Setup Instructions:

1. Go to Repository Settings → Branches
2. Add rule for `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass
   - ✅ Require conversation resolution
   - ✅ Do not allow bypassing

## Local Development

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
vim src/my_module.py

# 3. Run tests locally
pytest tests/ -v

# 4. Check coverage
pytest tests/ --cov=src --cov-report=term-missing

# 5. Run linters manually (optional - pre-commit will run them)
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# 6. Commit (pre-commit runs automatically)
git add .
git commit -m "feat: add new feature"

# 7. Push
git push origin feature/my-feature

# 8. Create pull request
gh pr create --fill  # or use GitHub web UI
```

### Useful Git Aliases

After running `./scripts/setup-dev.sh`, these aliases are available:

```bash
git test    # Run all tests
git cov     # Run tests with coverage
git lint    # Run all linters
```

### Troubleshooting

**Pre-commit hooks failing:**
```bash
# See what failed
git commit -m "test"

# Run hooks manually to debug
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

**Tests failing in CI but passing locally:**
- Check Python version match
- Verify all dependencies in requirements.txt
- Check for environment-specific code
- Review GitHub Actions logs

**Coverage too low:**
```bash
# See what's not covered
pytest tests/ --cov=src --cov-report=term-missing

# Focus on missing lines
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Maintenance

### Updating Dependencies

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update Python dependencies
pip list --outdated
pip install --upgrade <package>

# Update requirements.txt
pip freeze > requirements.txt
```

### Monitoring CI Performance

- Check GitHub Actions dashboard for slow jobs
- Review artifact sizes
- Monitor cache hit rates
- Optimize test execution order

## Best Practices

1. **Always run tests locally** before pushing
2. **Keep coverage above 70%** for all new code
3. **Fix linting issues** before committing
4. **Review security reports** regularly
5. **Keep dependencies updated** monthly
6. **Write meaningful commit messages** following conventional commits
7. **Use feature branches** for all changes
8. **Request reviews** for significant changes

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Framework](https://pre-commit.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Black Code Style](https://black.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## Support

For issues with CI/CD:
1. Check GitHub Actions logs
2. Review this documentation
3. Run locally to reproduce
4. Create issue with details

---

Last Updated: 2025-01-16
Coverage: 71%
Status: ✅ Operational
