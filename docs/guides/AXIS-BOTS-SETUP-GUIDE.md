================================================================================
AXIS BOTS - ARCHITECTURE DOMAIN INSTRUCTIONS
================================================================================

PURPOSE: AXIS bots handle architecture, design patterns, validation,
         assessment, and strategic planning for the BSW-Arch bot factory

TOTAL AXIS BOTS: 45
DOMAIN: Architecture, Enterprise Architecture, TOGAF, Zachman, ArchiMate
FOCUS: System design, patterns, compliance, frameworks, blueprints

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

Step 3: Scan architecture-specific documents
---------------------------------------------
cd /opt/documentation/bot-utils
python3 doc_scanner.py --action list --domain AXIS --priority critical

Expected output: List of critical architecture documents


================================================================================
2. INITIAL DOCUMENT SCAN - WHAT TO READ FIRST
================================================================================

CRITICAL PRIORITY (Read these FIRST):
--------------------------------------
1. docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
   - 145 pages, complete bot factory design
   - 185 bots across 4 domains
   - 10 Mermaid diagrams
   - Container strategy (apko + Wolfi)

2. docs/architecture/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
   - Hybrid META-KERAGR knowledge base design
   - Bot documentation access patterns
   - 4-layer architecture: Git → KERAGR → API → Bots

3. docs/processes/GITHUB-DOCS-CONSOLIDATION-STRATEGY.md
   - Documentation organisation
   - Bot scanning patterns
   - Update detection

HIGH PRIORITY (Read after critical):
-------------------------------------
4. docs/guides/BSW-TECH-CLAUDE-INTEGRATION-GUIDE.md
   - Claude AI integration
   - Multi-agent patterns
   - MCP tools usage

5. docs/guides/BSW-TECH-AI-INTEGRATION-GUIDE.md
   - 50-page comprehensive AI guide
   - CrewAI framework usage
   - Bot collaboration patterns

REFERENCE (Available as needed):
---------------------------------
- docs/reference/*.md (13 documents from bsw-gov)
- docs/specifications/bots/*.yaml
- docs/specifications/containers/*.yaml


================================================================================
3. PYTHON API USAGE
================================================================================

Basic Scanner Usage:
--------------------
```python
from doc_scanner import DocScanner

# Initialise
scanner = DocScanner("/opt/documentation")

# Get AXIS-specific documents
axis_docs = scanner.get_documents_by_domain("AXIS")

# Get architecture category documents
arch_docs = scanner.get_documents_by_category("architecture")

# Get critical priority documents
critical = scanner.get_documents_by_priority("critical")

# Read a specific document
content = scanner.read_document("arch-001")

# Get initial scan list (recommended startup)
initial = scanner.get_initial_scan_documents()
```

GitHub API Client (No Clone Required):
---------------------------------------
```python
from github_api_client import GitHubDocsClient

# Initialise (optional GitHub token)
client = GitHubDocsClient(token="your_github_token")

# Fetch metadata
metadata = client.get_metadata()
print(f"Bots supported: {metadata['statistics']['bots_supported']}")

# Get a document
content = client.get_document("docs/INDEX.md")

# Search for topics
results = client.search_documents("TOGAF architecture")
```


================================================================================
4. AXIS BOT CATEGORIES AND THEIR FOCUS
================================================================================

ARCHITECTURE FRAMEWORK BOTS:
-----------------------------
- axis-docs-bot          : Documentation generation and maintenance
- axis-patterns-bot      : Design patterns library and recommendations
- axis-blueprint-bot     : System blueprints and reference architectures
- axis-framework-bot     : Enterprise architecture frameworks (TOGAF, Zachman)

VALIDATION & ASSESSMENT BOTS:
------------------------------
- axis-validation-bot    : Architecture validation and compliance checking
- axis-assessment-bot    : System assessment and gap analysis
- axis-review-bot        : Design review automation
- axis-audit-bot         : Architecture audit and standards compliance
- axis-compliance-bot    : Regulatory and standard compliance

STRATEGIC & PLANNING BOTS:
--------------------------
- axis-strategy-bot      : Strategic architecture planning
- axis-planning-bot      : Architecture roadmap planning
- axis-risk-bot          : Risk assessment and mitigation
- axis-innovation-bot    : Innovation tracking and adoption

COORDINATION & INTEGRATION BOTS:
---------------------------------
- axis-coordination-bot  : Multi-bot coordination and orchestration
- axis-integration-bot   : System integration patterns and services
- axis-gateway-bot       : API gateway management

OPERATIONAL BOTS:
-----------------
- axis-monitoring-bot    : Architecture monitoring and alerting
- axis-analytics-bot     : Architecture analytics and metrics
- axis-report-bot        : Reporting and documentation generation
- axis-kb-bot           : Knowledge base management

... (31 more AXIS bots available)


================================================================================
5. RECOMMENDED WORKFLOWS FOR AXIS BOTS
================================================================================

Workflow 1: New AXIS Bot Initialisation
----------------------------------------
1. Clone documentation:
   git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation

2. Scan initial documents:
   python3 /opt/documentation/bot-utils/doc_scanner.py --action list

3. Read critical architecture docs:
   - COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
   - BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md

4. Load bot-specific documents:
   scanner = DocScanner("/opt/documentation")
   my_docs = scanner.get_documents_for_bot("axis-YOUR-BOT-NAME")

5. Begin operation with loaded context


Workflow 2: Architecture Validation (axis-validation-bot)
----------------------------------------------------------
1. Scan architecture documents:
   arch_docs = scanner.get_documents_by_category("architecture")

2. Load validation rules and standards:
   - TOGAF compliance rules
   - ArchiMate notation standards
   - FAGAM prohibition requirements

3. Validate system design:
   - Check container sizes (<50MB requirement)
   - Verify FAGAM prohibition compliance
   - Validate architecture patterns

4. Generate validation report:
   - Non-compliances identified
   - Remediation recommendations
   - Priority ranking


Workflow 3: Design Review (axis-review-bot)
--------------------------------------------
1. Load design patterns:
   patterns = scanner.get_documents_by_category("patterns")

2. Review submitted design:
   - Check against established patterns
   - Identify anti-patterns
   - Validate integration points

3. Provide feedback:
   - Pattern recommendations
   - Best practice guidance
   - Reference architecture links


Workflow 4: Multi-Bot Coordination (axis-coordination-bot)
-----------------------------------------------------------
1. Load coordination patterns:
   coord_docs = scanner.get_documents_for_bot("axis-coordination-bot")

2. Identify participating bots:
   - AXIS domain bots
   - Cross-domain collaborations (PIPE, ECO, IV)

3. Orchestrate workflow:
   - Define task dependencies
   - Assign tasks to appropriate bots
   - Monitor execution

4. Aggregate results:
   - Collect bot outputs
   - Synthesise findings
   - Generate combined report


================================================================================
6. KEY ARCHITECTURE REQUIREMENTS
================================================================================

Container Strategy:
-------------------
- Use apko + Chainguard Wolfi base images
- Target size: 15-50MB (vs 400MB+ traditional)
- No FAGAM dependencies
- Declarative builds only

FAGAM + HashiCorp Prohibition:
-------------------------------
NO Facebook products
NO Apple products
NO Google products (including Terraform)
NO Amazon products (AWS services OK if needed)
NO Microsoft products
NO HashiCorp products (use OpenTofu, OpenBao)

YES: Open source alternatives
YES: CNCF projects
YES: Linux Foundation projects

Architecture Frameworks:
------------------------
- TOGAF 10 compliance
- Zachman Framework alignment
- ArchiMate 3.2 notation
- C4 model for diagrams

GitOps Workflow:
----------------
feature/bsw-tech-ai-XXX-description → develop → main
- All changes via feature branches
- Develop branch for integration
- Main branch for production


================================================================================
7. DOCUMENT UPDATE DETECTION
================================================================================

Check for Updates:
------------------
```python
import requests

response = requests.get(
    "https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json"
)
metadata = response.json()

print(f"Version: {metadata['repository']['version']}")
print(f"Last updated: {metadata['repository']['updated']}")

# Compare with local version
local_metadata = scanner.load_metadata()
if metadata['repository']['version'] != local_metadata['repository']['version']:
    print("⚠️  Documentation has been updated!")
    # Re-clone or pull latest
```


================================================================================
8. DOCKERFILE INTEGRATION EXAMPLE
================================================================================

```dockerfile
FROM cgr.dev/chainguard/wolfi-base:latest

# Install dependencies
RUN apk add --no-cache git python-3.11 py3-pip

# Clone documentation
WORKDIR /opt
RUN git clone https://github.com/bsw-arch/bsw-arch.git documentation

# Install Python dependencies
RUN pip install --no-cache-dir pyyaml requests

# Add bot-utils to Python path
ENV PYTHONPATH="/opt/documentation/bot-utils:$PYTHONPATH"
ENV DOCS_PATH="/opt/documentation/docs"

# Copy AXIS bot code
COPY . /app
WORKDIR /app

# Run bot
CMD ["python3", "main.py"]
```


================================================================================
9. EXAMPLE AXIS BOT IMPLEMENTATION
================================================================================

```python
#!/usr/bin/env python3
"""
AXIS Bot Example - Architecture Documentation Bot
Reads and analyses architecture documentation
"""

import sys
sys.path.insert(0, "/opt/documentation/bot-utils")

from doc_scanner import DocScanner

def main():
    print("🏗️  AXIS Bot Starting...")

    # Initialise documentation scanner
    scanner = DocScanner("/opt/documentation")

    # Get AXIS-specific documents
    print("📚 Loading AXIS architecture documents...")
    axis_docs = scanner.get_documents_by_domain("AXIS")

    print(f"✅ Found {len(axis_docs)} AXIS documents")

    # Read critical architecture document
    print("\n📖 Reading comprehensive architecture analysis...")
    content = scanner.read_document("arch-001")

    if content:
        print(f"✅ Loaded {len(content)} characters")

        # Example: Count architecture patterns mentioned
        patterns = ["microservices", "event-driven", "layered", "hexagonal"]
        pattern_counts = {}

        for pattern in patterns:
            count = content.lower().count(pattern)
            if count > 0:
                pattern_counts[pattern] = count

        print("\n🔍 Architecture Patterns Found:")
        for pattern, count in pattern_counts.items():
            print(f"   - {pattern}: {count} mentions")

    # Get statistics
    stats = scanner.get_statistics()
    print(f"\n📊 Repository Statistics:")
    print(f"   Total Docs: {stats['total_documents']}")
    print(f"   Bots Supported: {stats['bots_supported']}")
    print(f"   Domains: {', '.join(stats['domains'])}")

    print("\n✅ AXIS Bot Analysis Complete")

if __name__ == "__main__":
    main()
```


================================================================================
10. TROUBLESHOOTING
================================================================================

Problem: Cannot find documentation
Solution:
  Check if repository is cloned:
    ls -la /opt/documentation

  If missing:
    cd /opt
    git clone https://github.com/bsw-arch/bsw-arch.git documentation

Problem: Python import errors
Solution:
  Add to Python path:
    export PYTHONPATH="/opt/documentation/bot-utils:$PYTHONPATH"

  Or in code:
    import sys
    sys.path.insert(0, "/opt/documentation/bot-utils")

Problem: Missing dependencies
Solution:
  Install required packages:
    pip install pyyaml requests

Problem: Rate limit on GitHub API
Solution:
  Use GitHub token:
    client = GitHubDocsClient(token="your_github_token")

  Or clone repository instead of using API

Problem: Outdated documentation
Solution:
  Pull latest changes:
    cd /opt/documentation
    git pull origin main


================================================================================
11. RECOMMENDED READING ORDER FOR AXIS BOTS
================================================================================

Day 1: Foundation
-----------------
1. COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md (2 hours)
   - Understand overall architecture
   - Learn 185-bot structure
   - Review container strategy

2. BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md (1 hour)
   - Understand knowledge base system
   - Learn META-KERAGR design
   - Bot access patterns

Day 2: Integration
-------------------
3. BSW-TECH-CLAUDE-INTEGRATION-GUIDE.md (1 hour)
   - Claude AI integration
   - Multi-agent coordination
   - MCP tools

4. GITHUB-DOCS-CONSOLIDATION-STRATEGY.md (30 min)
   - Documentation structure
   - Update patterns
   - Scanning strategies

Day 3: Implementation
---------------------
5. Reference documents as needed
6. Specific bot implementation patterns
7. Architecture frameworks (TOGAF, Zachman, ArchiMate)

Ongoing:
--------
- Monitor metadata.json for updates
- Review new patterns as added
- Contribute findings back to knowledge base


================================================================================
12. AXIS BOT COLLABORATION PATTERNS
================================================================================

Pattern 1: AXIS → AXIS Collaboration
-------------------------------------
axis-assessment-bot identifies gaps
  ↓
axis-validation-bot validates current state
  ↓
axis-blueprint-bot creates remediation design
  ↓
axis-review-bot reviews proposed design
  ↓
axis-docs-bot documents approved architecture


Pattern 2: AXIS → PIPE Collaboration
-------------------------------------
axis-blueprint-bot designs CI/CD pipeline
  ↓
pipe-build-bot implements build pipeline
  ↓
pipe-test-bot adds testing stages
  ↓
pipe-deployment-bot adds deployment automation
  ↓
axis-validation-bot validates complete pipeline


Pattern 3: AXIS → ECO Collaboration
------------------------------------
axis-framework-bot defines infrastructure requirements
  ↓
eco-infra-bot provisions infrastructure
  ↓
eco-monitoring-bot adds observability
  ↓
eco-resource-bot optimises resource usage
  ↓
axis-audit-bot validates compliance


Pattern 4: AXIS → IV Collaboration
-----------------------------------
axis-kb-bot maintains knowledge base
  ↓
iv-analysis-bot analyses architecture decisions
  ↓
iv-validation-bot validates AI/ML integration
  ↓
axis-report-bot generates insights report


================================================================================
13. CRITICAL CONSTRAINTS FOR AXIS BOTS
================================================================================

1. FAGAM Prohibition:
   - No Google Cloud products
   - No AWS proprietary services (use open standards)
   - No Azure services
   - No HashiCorp Terraform (use OpenTofu)
   - No HashiCorp Vault (use OpenBao)

2. Container Size:
   - Maximum 50MB per container
   - Use apko + Wolfi base (15MB typical)
   - Multi-stage builds required
   - No unnecessary dependencies

3. Architecture Standards:
   - TOGAF 10 compliance required
   - ArchiMate 3.2 notation for diagrams
   - Zachman Framework alignment
   - C4 model for architecture views

4. Documentation Requirements:
   - UK English spelling
   - Markdown format
   - Mermaid diagrams for architecture
   - Code examples in Python

5. GitOps Workflow:
   - Feature branches: feature/bsw-tech-ai-XXX-description
   - Develop branch for integration
   - Main branch for production
   - No direct commits to main


================================================================================
14. QUICK REFERENCE URLS
================================================================================

Documentation Repository:
https://github.com/bsw-arch/bsw-arch

Metadata (Check for updates):
https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json

Catalogue (Document list):
https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/catalogue.yaml

Documentation Index:
https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/INDEX.md

Codeberg Organisations:
- AXIS Bots: https://codeberg.org/AXIS-Bots
- PIPE Bots: https://codeberg.org/PIPE-Bots
- ECO Bots: https://codeberg.org/ECO-Bots
- IV Bots: https://codeberg.org/IV-Bots


================================================================================
15. FINAL CHECKLIST FOR AXIS BOT DEPLOYMENT
================================================================================

Pre-Deployment:
[ ] Documentation repository cloned to /opt/documentation
[ ] Python dependencies installed (pyyaml, requests)
[ ] Bot-utils in PYTHONPATH
[ ] Initial document scan completed
[ ] Critical docs read (COMPREHENSIVE, KNOWLEDGE-BASE)

Configuration:
[ ] Container size verified (<50MB)
[ ] FAGAM prohibition compliance checked
[ ] GitOps workflow configured
[ ] Architecture standards defined (TOGAF, ArchiMate)
[ ] UK English spelling enforced

Integration:
[ ] DocScanner API tested
[ ] Document access verified
[ ] Update detection working
[ ] Cross-bot communication configured
[ ] Knowledge base integration active

Validation:
[ ] Architecture compliance verified
[ ] Pattern library accessible
[ ] Design review process tested
[ ] Multi-bot coordination working
[ ] Documentation generation functional

Production:
[ ] Monitoring enabled
[ ] Logging configured
[ ] Error handling tested
[ ] Performance benchmarked
[ ] Rollback procedure documented


================================================================================
END OF AXIS BOT INSTRUCTIONS
================================================================================

Last Updated: 2025-11-10
Version: 1.0.0
Domain: AXIS (Architecture)
Bots: 45 architecture, design, validation, and strategic planning bots

For support: https://github.com/bsw-arch/bsw-arch/issues
