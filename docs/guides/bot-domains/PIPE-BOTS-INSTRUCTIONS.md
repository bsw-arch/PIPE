================================================================================
PIPE BOTS - PIPELINE DOMAIN INSTRUCTIONS
================================================================================

PURPOSE: PIPE bots handle CI/CD pipelines, build automation, deployment,
         testing, and release management for the BSW-Arch bot factory

TOTAL PIPE BOTS: 48
DOMAIN: Pipeline, CI/CD, Build, Test, Deploy, Release
FOCUS: Automation, continuous integration, delivery, deployment

================================================================================
1. INITIAL SETUP - SCAN DOCUMENTATION
================================================================================

Step 1: Clone the documentation repository
-------------------------------------------
cd /opt
git clone https://github.com/bsw-arch/bsw-arch.git documentation

Step 2: Install Python dependencies
------------------------------------
pip install pyyaml requests

Step 3: Scan pipeline-specific documents
-----------------------------------------
cd /opt/documentation/bot-utils
python3 doc_scanner.py --action list --domain PIPE --priority critical

Expected output: List of critical pipeline documents


================================================================================
2. INITIAL DOCUMENT SCAN - WHAT TO READ FIRST
================================================================================

CRITICAL PRIORITY (Read these FIRST):
--------------------------------------
1. docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
   - Section on CI/CD pipeline architecture
   - 185-bot deployment strategy
   - Container build processes (apko + Wolfi)
   - GitOps workflow patterns

2. docs/processes/GITHUB-DOCS-CONSOLIDATION-STRATEGY.md
   - Git repository structure
   - Documentation update workflows
   - Deployment processes

3. docs/architecture/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
   - Bot coordination patterns
   - Inter-bot communication
   - Pipeline orchestration

HIGH PRIORITY (Read after critical):
-------------------------------------
4. docs/guides/BSW-TECH-CLAUDE-INTEGRATION-GUIDE.md
   - CI/CD automation with Claude AI
   - Multi-agent build patterns
   - Automated testing strategies

5. docs/guides/BSW-TECH-AI-INTEGRATION-GUIDE.md
   - CrewAI framework for pipeline bots
   - Bot collaboration in pipelines
   - Automated deployment patterns

REFERENCE (Available as needed):
---------------------------------
- docs/specifications/containers/*.yaml (Container build specs)
- docs/specifications/bots/*.yaml (Bot deployment configs)
- docs/reference/*.md (Technical references)


================================================================================
3. PYTHON API USAGE
================================================================================

Basic Scanner Usage for PIPE Bots:
-----------------------------------
```python
from doc_scanner import DocScanner

# Initialize
scanner = DocScanner("/opt/documentation")

# Get PIPE-specific documents
pipe_docs = scanner.get_documents_by_domain("PIPE")

# Get process/workflow documents
process_docs = scanner.get_documents_by_category("processes")

# Get deployment-related documents
deploy_docs = [d for d in scanner.scan_all_documents()
               if 'deployment' in d.get('topics', [])]

# Read a specific document
content = scanner.read_document("proc-001")

# Get CI/CD related topics
cicd_docs = [d for d in scanner.scan_all_documents()
             if 'ci-cd' in d.get('topics', [])]
```

GitHub API Client (For Pipeline Automation):
---------------------------------------------
```python
from github_api_client import GitHubDocsClient

# Initialize
client = GitHubDocsClient(token="your_github_token")

# Check for documentation updates (trigger rebuild)
metadata = client.get_metadata()
version = metadata['repository']['version']

# Fetch latest deployment specs
specs = client.list_directory("docs/specifications/containers")

# Get container build configuration
config = client.get_document("docs/specifications/containers/apko-base.yaml")
```


================================================================================
4. PIPE BOT CATEGORIES AND THEIR FOCUS
================================================================================

BUILD & COMPILATION BOTS:
--------------------------
- pipe-build-bot          : Main build orchestration and compilation
- pipe-compile-bot        : Code compilation and artifact generation
- pipe-package-bot        : Package creation and versioning
- pipe-artifact-bot       : Build artifact management and storage

TESTING BOTS:
-------------
- pipe-test-bot           : Test execution and orchestration
- pipe-unittest-bot       : Unit test execution
- pipe-integration-bot    : Integration test execution
- pipe-e2e-bot            : End-to-end test automation
- pipe-coverage-bot       : Code coverage analysis
- pipe-quality-bot        : Code quality checks

DEPLOYMENT BOTS:
----------------
- pipe-deploy-bot         : Deployment orchestration
- pipe-release-bot        : Release management and versioning
- pipe-rollback-bot       : Automated rollback procedures
- pipe-canary-bot         : Canary deployment management
- pipe-bluegreen-bot      : Blue-green deployment automation

CONTAINER & REGISTRY BOTS:
---------------------------
- pipe-container-bot      : Container image building (apko + Wolfi)
- pipe-registry-bot       : Container registry management
- pipe-image-bot          : Image optimization and scanning
- pipe-scan-bot           : Security scanning of containers

CI/CD ORCHESTRATION BOTS:
--------------------------
- pipe-ci-bot             : Continuous integration orchestration
- pipe-cd-bot             : Continuous deployment orchestration
- pipe-pipeline-bot       : Pipeline definition and execution
- pipe-workflow-bot       : Workflow automation and triggers
- pipe-scheduler-bot      : Build and deployment scheduling

CODE MANAGEMENT BOTS:
---------------------
- pipe-git-bot            : Git operations and management
- pipe-merge-bot          : Automated merge management
- pipe-branch-bot         : Branch strategy enforcement
- pipe-tag-bot            : Git tagging and version management

MONITORING & REPORTING BOTS:
-----------------------------
- pipe-monitor-bot        : Pipeline monitoring and alerts
- pipe-metrics-bot        : Build and deployment metrics
- pipe-report-bot         : Pipeline reporting and dashboards
- pipe-alert-bot          : Alert management and notifications

OPTIMIZATION & ANALYSIS BOTS:
------------------------------
- pipe-optimize-bot       : Build optimization
- pipe-cache-bot          : Build cache management
- pipe-parallel-bot       : Parallel execution optimization
- pipe-benchmark-bot      : Performance benchmarking

... (16 more PIPE bots available)


================================================================================
5. RECOMMENDED WORKFLOWS FOR PIPE BOTS
================================================================================

Workflow 1: New PIPE Bot Initialization
----------------------------------------
1. Clone documentation:
   git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation

2. Scan CI/CD documents:
   python3 /opt/documentation/bot-utils/doc_scanner.py --action list --domain PIPE

3. Read pipeline architecture:
   - COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md (CI/CD sections)
   - GITHUB-DOCS-CONSOLIDATION-STRATEGY.md

4. Load bot-specific pipeline configs:
   scanner = DocScanner("/opt/documentation")
   my_docs = scanner.get_documents_for_bot("pipe-YOUR-BOT-NAME")

5. Configure pipeline triggers and begin operation


Workflow 2: Container Build Pipeline (pipe-build-bot + pipe-container-bot)
---------------------------------------------------------------------------
1. Trigger: Git push to feature branch

2. pipe-git-bot detects change:
   - Validates branch naming (feature/bsw-tech-ai-XXX)
   - Checks commit message format
   - Notifies pipe-build-bot

3. pipe-build-bot orchestrates:
   - Calls pipe-test-bot for unit tests
   - Calls pipe-quality-bot for linting
   - Calls pipe-container-bot for image build

4. pipe-container-bot builds:
   - Use apko + Chainguard Wolfi base
   - Build declarative container (<50MB target)
   - No FAGAM dependencies
   - Push to registry

5. pipe-scan-bot validates:
   - Security scanning
   - Vulnerability checks
   - License compliance

6. pipe-artifact-bot stores:
   - Save build artifacts
   - Generate SBOM
   - Update manifest


Workflow 3: Deployment Pipeline (pipe-deploy-bot orchestration)
----------------------------------------------------------------
1. Trigger: Merge to develop or main branch

2. pipe-merge-bot validates:
   - Branch protection rules
   - Required approvals
   - CI checks passed

3. pipe-build-bot rebuilds for target:
   - Clean build for deployment
   - Generate deployment artifacts
   - Create release notes

4. pipe-test-bot runs full suite:
   - Unit tests
   - Integration tests
   - E2E tests
   - Performance tests

5. pipe-deploy-bot executes strategy:
   - Choose strategy (canary, blue-green, rolling)
   - Deploy to staging first
   - Run smoke tests
   - Deploy to production

6. pipe-monitor-bot observes:
   - Track deployment metrics
   - Monitor error rates
   - Alert on anomalies

7. pipe-rollback-bot stands ready:
   - Automatic rollback on critical errors
   - Manual rollback capability
   - Restore previous version


Workflow 4: Multi-Bot Testing Pipeline (pipe-test-bot orchestration)
---------------------------------------------------------------------
1. pipe-test-bot receives build:
   - New container image ready
   - Deployment configuration provided

2. Parallel test execution:
   - pipe-unittest-bot: Run unit tests
   - pipe-integration-bot: Run integration tests
   - pipe-e2e-bot: Run end-to-end tests
   - pipe-security-bot: Run security tests

3. pipe-coverage-bot analyzes:
   - Collect coverage from all tests
   - Generate coverage report
   - Check against thresholds (>80% required)

4. pipe-quality-bot validates:
   - Code quality metrics
   - Technical debt analysis
   - Maintainability score

5. pipe-report-bot aggregates:
   - Combine all test results
   - Generate comprehensive report
   - Notify stakeholders

6. Decision: Pass/Fail
   - Pass: Continue to deployment
   - Fail: Block deployment, notify developers


================================================================================
6. KEY PIPELINE REQUIREMENTS
================================================================================

Container Build Strategy:
--------------------------
- Tool: apko (declarative container builds)
- Base: Chainguard Wolfi (minimal, secure)
- Target Size: 15-50MB (NOT 400MB+)
- Format: OCI-compliant images
- Registry: Self-hosted or Codeberg

Build Tools Allowed:
--------------------
YES: apko, buildah, kaniko, podman
YES: Open source CI tools (GitLab CI, Gitea Actions, Woodpecker CI)
YES: CNCF projects (Tekton, Argo CD, Flux)

NO: Docker Hub (use Chainguard, cgr.dev)
NO: GitHub Actions (use Gitea Actions or Woodpecker)
NO: CircleCI, Travis CI (proprietary)
NO: HashiCorp products

GitOps Workflow (CRITICAL):
----------------------------
Feature Branch:
  feature/bsw-tech-ai-XXX-description
    ↓
  Develop Branch:
    - Integration testing
    - Staging deployment
    ↓
  Main Branch:
    - Production ready
    - Auto-deploy to prod

Branch Protection:
- No direct commits to main
- Require PR reviews (2 approvals)
- All CI checks must pass
- Signed commits required

Testing Requirements:
---------------------
- Unit tests: >80% coverage
- Integration tests: All APIs tested
- E2E tests: Critical paths validated
- Security tests: OWASP Top 10 checked
- Performance tests: Benchmarks met

Deployment Strategies:
----------------------
1. Canary: 5% → 25% → 50% → 100%
2. Blue-Green: Full environment switch
3. Rolling: Progressive pod replacement
4. Recreate: Stop old, start new (dev only)


================================================================================
7. CONTAINER BUILD EXAMPLE (APKO + WOLFI)
================================================================================

apko.yaml Configuration:
------------------------
```yaml
contents:
  repositories:
    - https://packages.wolfi.dev/os
  keyring:
    - https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
  packages:
    - wolfi-base
    - python-3.11
    - py3-pip
    - git

accounts:
  groups:
    - groupname: nonroot
      gid: 65532
  users:
    - username: nonroot
      uid: 65532
      gid: 65532
  run-as: 65532

entrypoint:
  type: service-bundle
  services:
    bot: /usr/bin/python3 /app/main.py

archs:
  - x86_64
  - aarch64

environment:
  DOCS_PATH: /opt/documentation
  PYTHONPATH: /opt/documentation/bot-utils
```

Build Command:
--------------
```bash
apko build apko.yaml pipe-bot:latest output.tar
```

Expected Result:
- Image size: 15-25MB
- No vulnerabilities
- Non-root user
- Multi-arch support


================================================================================
8. DOCKERFILE INTEGRATION (PIPE BOT)
================================================================================

```dockerfile
FROM cgr.dev/chainguard/wolfi-base:latest

# Install pipeline tools
RUN apk add --no-cache \
    git \
    python-3.11 \
    py3-pip \
    bash

# Clone documentation
WORKDIR /opt
RUN git clone https://github.com/bsw-arch/bsw-arch.git documentation

# Install Python dependencies
RUN pip install --no-cache-dir pyyaml requests

# Add bot-utils to Python path
ENV PYTHONPATH="/opt/documentation/bot-utils:$PYTHONPATH"
ENV DOCS_PATH="/opt/documentation/docs"

# Copy PIPE bot code
COPY . /app
WORKDIR /app

# Install bot dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Non-root user
RUN addgroup -g 65532 nonroot && \
    adduser -u 65532 -G nonroot -s /bin/sh -D nonroot && \
    chown -R nonroot:nonroot /app

USER nonroot

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import sys; sys.exit(0)"

# Run bot
CMD ["python3", "main.py"]
```


================================================================================
9. EXAMPLE PIPE BOT IMPLEMENTATION
================================================================================

```python
#!/usr/bin/env python3
"""
PIPE Bot Example - Build Orchestration Bot
Orchestrates CI/CD pipeline for bot factory
"""

import sys
import os
sys.path.insert(0, "/opt/documentation/bot-utils")

from doc_scanner import DocScanner
import subprocess
import json

class PipeBuildBot:
    def __init__(self):
        self.scanner = DocScanner("/opt/documentation")
        self.docs = self.scanner.get_documents_by_domain("PIPE")

    def validate_branch(self, branch_name):
        """Validate branch naming convention"""
        if branch_name.startswith("feature/bsw-tech-ai-"):
            return True
        elif branch_name in ["develop", "main"]:
            return True
        else:
            raise ValueError(f"Invalid branch name: {branch_name}")

    def run_unit_tests(self):
        """Execute unit tests"""
        print("🧪 Running unit tests...")
        result = subprocess.run(
            ["pytest", "tests/unit", "-v", "--cov=src"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def run_integration_tests(self):
        """Execute integration tests"""
        print("🔗 Running integration tests...")
        result = subprocess.run(
            ["pytest", "tests/integration", "-v"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def build_container(self, bot_name):
        """Build container using apko"""
        print(f"🐳 Building container for {bot_name}...")

        # Check apko.yaml exists
        if not os.path.exists("apko.yaml"):
            raise FileNotFoundError("apko.yaml not found")

        # Build with apko
        result = subprocess.run(
            ["apko", "build", "apko.yaml", f"{bot_name}:latest", "output.tar"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ Container built successfully")
            return True
        else:
            print(f"❌ Container build failed: {result.stderr}")
            return False

    def check_container_size(self, image_name):
        """Verify container is <50MB"""
        result = subprocess.run(
            ["podman", "images", image_name, "--format", "{{.Size}}"],
            capture_output=True,
            text=True
        )

        size_str = result.stdout.strip()
        print(f"📦 Container size: {size_str}")

        # Parse size (simplified)
        if "MB" in size_str:
            size_mb = float(size_str.replace("MB", ""))
            if size_mb > 50:
                raise ValueError(f"Container too large: {size_mb}MB (max 50MB)")

        return True

    def run_pipeline(self, bot_name, branch):
        """Execute full CI/CD pipeline"""
        print(f"🚀 Starting pipeline for {bot_name} on {branch}")

        # Step 1: Validate branch
        try:
            self.validate_branch(branch)
            print("✅ Branch name validated")
        except ValueError as e:
            print(f"❌ {e}")
            return False

        # Step 2: Run unit tests
        if not self.run_unit_tests():
            print("❌ Unit tests failed")
            return False
        print("✅ Unit tests passed")

        # Step 3: Run integration tests
        if not self.run_integration_tests():
            print("❌ Integration tests failed")
            return False
        print("✅ Integration tests passed")

        # Step 4: Build container
        if not self.build_container(bot_name):
            print("❌ Container build failed")
            return False
        print("✅ Container built")

        # Step 5: Check container size
        try:
            self.check_container_size(f"{bot_name}:latest")
            print("✅ Container size validated")
        except ValueError as e:
            print(f"❌ {e}")
            return False

        # Step 6: Security scan
        print("🔒 Running security scan...")
        # (Implement security scanning)

        print(f"✅ Pipeline complete for {bot_name}")
        return True


def main():
    print("🏗️  PIPE Build Bot Starting...")

    bot = PipeBuildBot()

    # Example: Run pipeline for a bot
    bot_name = os.getenv("BOT_NAME", "pipe-test-bot")
    branch = os.getenv("GIT_BRANCH", "feature/bsw-tech-ai-001-test")

    success = bot.run_pipeline(bot_name, branch)

    if success:
        print("✅ Pipeline succeeded")
        sys.exit(0)
    else:
        print("❌ Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
```


================================================================================
10. PIPE BOT COLLABORATION PATTERNS
================================================================================

Pattern 1: Sequential Pipeline
-------------------------------
```
pipe-git-bot (detects change)
  ↓
pipe-build-bot (compiles code)
  ↓
pipe-test-bot (runs tests)
  ↓
pipe-container-bot (builds image)
  ↓
pipe-scan-bot (security scan)
  ↓
pipe-deploy-bot (deploys)
  ↓
pipe-monitor-bot (monitors)
```


Pattern 2: Parallel Testing
----------------------------
```
pipe-build-bot (builds artifact)
  ↓
  ├→ pipe-unittest-bot (parallel)
  ├→ pipe-integration-bot (parallel)
  ├→ pipe-e2e-bot (parallel)
  └→ pipe-security-bot (parallel)
  ↓
pipe-report-bot (aggregates results)
```


Pattern 3: Multi-Environment Deployment
----------------------------------------
```
pipe-deploy-bot (orchestrates)
  ↓
  ├→ pipe-staging-bot (deploy to staging)
  │    ↓
  │   pipe-smoke-bot (smoke tests)
  │    ↓
  │   [Manual approval]
  │    ↓
  ├→ pipe-canary-bot (5% to prod)
  │    ↓
  │   pipe-monitor-bot (watch metrics)
  │    ↓
  ├→ pipe-bluegreen-bot (full deployment)
  │    ↓
  └→ pipe-rollback-bot (ready if needed)
```


Pattern 4: Cross-Domain Pipeline (PIPE → AXIS → ECO)
-----------------------------------------------------
```
pipe-build-bot builds new bot
  ↓
axis-validation-bot validates architecture
  ↓
axis-compliance-bot checks standards
  ↓
pipe-test-bot runs full test suite
  ↓
eco-infra-bot provisions infrastructure
  ↓
pipe-deploy-bot deploys to infrastructure
  ↓
eco-monitoring-bot monitors resources
  ↓
pipe-monitor-bot monitors application
```


================================================================================
11. TROUBLESHOOTING
================================================================================

Problem: Container build fails
Solution:
  Check apko.yaml syntax:
    apko build apko.yaml test:latest output.tar --debug

  Verify Wolfi package availability:
    Check https://packages.wolfi.dev/os

Problem: Container too large (>50MB)
Solution:
  Remove unnecessary packages:
    - Only include runtime dependencies
    - Use multi-stage builds
    - Minimize Python packages

  Check what's consuming space:
    podman history image:latest

Problem: Tests failing in pipeline but pass locally
Solution:
  Check environment differences:
    - Environment variables
    - File permissions
    - Network access
    - Dependencies versions

  Run pipeline locally:
    docker run --rm -v $(pwd):/app test-image pytest

Problem: Deployment rollback needed
Solution:
  Immediate rollback:
    pipe-rollback-bot --immediate --version=previous

  Find last good version:
    git log --oneline main | head -5

  Deploy specific version:
    pipe-deploy-bot --version=v1.2.3

Problem: Pipeline stuck or hanging
Solution:
  Check pipeline status:
    pipe-monitor-bot --status

  View running jobs:
    kubectl get pods -n pipelines

  Kill stuck pipeline:
    pipe-pipeline-bot --cancel --job-id=12345


================================================================================
12. CI/CD BEST PRACTICES FOR PIPE BOTS
================================================================================

1. Fast Feedback:
   - Unit tests: <2 minutes
   - Integration tests: <10 minutes
   - Full pipeline: <20 minutes

2. Fail Fast:
   - Run fastest tests first
   - Stop pipeline on critical failures
   - Don't waste resources on doomed builds

3. Reproducible Builds:
   - Pin all dependency versions
   - Use declarative builds (apko)
   - No "latest" tags in production

4. Security First:
   - Scan every container
   - Check for vulnerabilities
   - Validate dependencies

5. Observability:
   - Log everything
   - Track metrics (build time, success rate)
   - Alert on failures

6. Self-Service:
   - Developers can trigger pipelines
   - Clear error messages
   - Easy rollback procedures

7. Progressive Deployment:
   - Start with canary (5%)
   - Monitor before scaling
   - Automatic rollback on errors


================================================================================
13. QUICK REFERENCE URLS
================================================================================

Documentation Repository:
https://github.com/bsw-arch/bsw-arch

Wolfi Packages:
https://packages.wolfi.dev/os

Chainguard Images:
https://images.chainguard.dev

Codeberg Organizations:
- PIPE Bots: https://codeberg.org/PIPE-Bots
- AXIS Bots: https://codeberg.org/AXIS-Bots
- ECO Bots: https://codeberg.org/ECO-Bots
- IV Bots: https://codeberg.org/IV-Bots

Apko Documentation:
https://github.com/chainguard-dev/apko


================================================================================
14. FINAL CHECKLIST FOR PIPE BOT DEPLOYMENT
================================================================================

Pre-Deployment:
[ ] Documentation repository cloned to /opt/documentation
[ ] Python dependencies installed (pyyaml, requests)
[ ] Bot-utils in PYTHONPATH
[ ] CI/CD documents scanned
[ ] Pipeline architecture understood

Configuration:
[ ] apko.yaml created and validated
[ ] Container size target set (<50MB)
[ ] FAGAM prohibition compliance verified
[ ] GitOps workflow configured (feature→develop→main)
[ ] Test coverage thresholds defined (>80%)

Pipeline Setup:
[ ] Git triggers configured
[ ] Build stages defined
[ ] Test execution automated
[ ] Security scanning enabled
[ ] Deployment strategy chosen

Integration:
[ ] Multi-bot coordination tested
[ ] Cross-domain pipelines working
[ ] Parallel execution validated
[ ] Failure handling implemented
[ ] Rollback procedures tested

Monitoring:
[ ] Build metrics tracked
[ ] Deployment monitoring active
[ ] Alert rules configured
[ ] Logging aggregated
[ ] Dashboards created

Production:
[ ] Staging environment tested
[ ] Canary deployment successful
[ ] Full deployment completed
[ ] Rollback tested
[ ] Documentation updated


================================================================================
END OF PIPE BOT INSTRUCTIONS
================================================================================

Last Updated: 2025-11-10
Version: 1.0.0
Domain: PIPE (Pipeline)
Bots: 48 CI/CD, build, test, deployment, and release management bots

For support: https://github.com/bsw-arch/bsw-arch/issues
