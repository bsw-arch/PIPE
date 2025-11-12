# Multi-Tab Claude Web Console Instructies

> Gedetailleerde instructies voor het gebruik van BSW-Arch documentatie met parallelle subagents en MCP tools

**Versie**: 1.0.0
**Datum**: 2025-11-10
**Taal**: Nederlands (UK English in code)
**Doelgroep**: Architecten, Ontwikkelaars, Bot Operators

---

## 📋 Inhoudsopgave

1. [Overzicht](#overzicht)
2. [Voorbereiding](#voorbereiding)
3. [Tab Configuratie](#tab-configuratie)
4. [Parallelle Workflows](#parallelle-workflows)
5. [MCP Tools Gebruik](#mcp-tools-gebruik)
6. [Subagent Orchestration](#subagent-orchestration)
7. [Praktische Voorbeelden](#praktische-voorbeelden)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overzicht

### Doel
Het maximaal benutten van Claude's capabilities door:
- **Parallelle verwerking** via multiple tabs
- **Subagents** voor gespecialiseerde taken
- **MCP tools** voor externe systeem integratie
- **Documentatie scanning** via bot-utils

### Architectuur

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Web Console                        │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│   TAB 1     │   TAB 2     │   TAB 3     │     TAB 4        │
│ Coordinator │ Architecture│  Pipeline   │   Validation     │
│             │   Analysis  │   Build     │   & Testing      │
├─────────────┴─────────────┴─────────────┴──────────────────┤
│              Subagents (Explore, Plan, Task)                 │
├──────────────────────────────────────────────────────────────┤
│         MCP Tools (Codeberg, GitHub, Filesystem)             │
├──────────────────────────────────────────────────────────────┤
│              BSW-Arch Documentation Repository               │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔧 Voorbereiding

### Stap 1: Repository Setup

Open een **Terminal Tab** en clone de documentatie:

```bash
# Clone BSW-Arch documentatie
git clone https://github.com/bsw-arch/bsw-arch.git ~/bsw-arch-docs

# Installeer Python dependencies
pip install pyyaml requests

# Test de doc scanner
cd ~/bsw-arch-docs/bot-utils
python3 doc_scanner.py --action stats
```

### Stap 2: MCP Server Configuratie

Configureer de volgende MCP servers in Claude Desktop/Web:

#### GitHub MCP Server
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### Codeberg MCP Server
```json
{
  "mcpServers": {
    "codeberg": {
      "command": "python3",
      "args": ["/home/user/Code/mcp-servers/codeberg_mcp_server.py"],
      "env": {
        "CODEBERG_TOKEN": "dc048e78437e4f07ff078eedde0e4bf9a8b1a960"
      }
    }
  }
}
```

#### Filesystem MCP Server
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
    }
  }
}
```

### Stap 3: Documentatie Metadata Laden

Download de metadata voor snelle referentie:

```bash
# Download metadata
curl -o ~/metadata.json https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json

# Download catalogue
curl -o ~/catalogue.yaml https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/catalogue.yaml

# Bekijk statistieken
cat ~/metadata.json | jq '.statistics'
```

---

## 🗂️ Tab Configuratie

### Tab 1: Coordinator (Master Control)

**Rol**: Orchestration, planning, taak verdeling

**Eerste Prompt**:
```
Je bent de Master Coordinator voor een multi-tab Claude workflow voor het BSW-Arch bot factory project.

DOCUMENTATIE LOCATIE:
- Repository: ~/bsw-arch-docs
- Metadata: ~/metadata.json
- Catalogue: ~/catalogue.yaml
- Bot Utils: ~/bsw-arch-docs/bot-utils/

JOUW TAKEN:
1. Taken verdelen over tabs 2-4
2. Voortgang monitoren
3. Resultaten consolideren
4. Beslissingen nemen

BESCHIKBARE TABS:
- Tab 2: Architecture Analysis (AXIS focus)
- Tab 3: Pipeline Build (PIPE focus)
- Tab 4: Validation & Testing (ECO/IV focus)

BESCHIKBARE SUBAGENTS:
- Explore: Codebase verkenning
- Plan: Planning en strategie
- Task: Complexe taken uitvoeren

BESCHIKBARE MCP TOOLS:
- GitHub: Repository access
- Codeberg: Bot repositories
- Filesystem: Lokale files

Wat is de eerste taak die je wilt uitvoeren?
```

### Tab 2: Architecture Analysis

**Rol**: Architectuur analyse, design decisions, AXIS domein

**Eerste Prompt**:
```
Je bent de Architecture Analyst voor het BSW-Arch project, gespecialiseerd in het AXIS domein.

DOCUMENTATIE:
Gebruik de doc_scanner.py om AXIS-specifieke documentatie te laden:

```bash
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py \
  --action list \
  --domain AXIS
```

FOCUS GEBIEDEN:
1. Enterprise Architecture (TOGAF, Zachman, ArchiMate)
2. Bot Factory Design
3. Multi-Domain Coordination
4. Knowledge Base Architecture

TOOLS:
- Explore subagent voor codebase scanning
- GitHub MCP voor repository access
- doc_scanner.py voor documentatie filtering

WORKFLOW:
1. Scan critical priority documents (arch-001, arch-002, arch-003)
2. Analyseer architectuur patronen
3. Identificeer design gaps
4. Rapporteer aan Tab 1 (Coordinator)

Klaar om te beginnen?
```

### Tab 3: Pipeline Build

**Rol**: CI/CD, deployment, automation, PIPE domein

**Eerste Prompt**:
```
Je bent de Pipeline Engineer voor het BSW-Arch project, gespecialiseerd in het PIPE domein.

DOCUMENTATIE:
Laad PIPE-specifieke documentatie:

```bash
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py \
  --action list \
  --category processes
```

FOCUS GEBIEDEN:
1. Container builds (apko + Wolfi)
2. GitOps workflows
3. Deployment automation
4. CI/CD pipelines

TOOLS:
- Task subagent voor build taken
- Codeberg MCP voor bot repositories
- Filesystem MCP voor lokale builds

BOT FOCUS:
- pipe-build-bot
- pipe-test-bot
- pipe-deployment-bot
- pipe-release-bot

WORKFLOW:
1. Scan container specifications (ref-001)
2. Review GitOps processes (ref-009, ref-010)
3. Plan deployment strategie
4. Rapporteer aan Tab 1 (Coordinator)

Klaar om te beginnen?
```

### Tab 4: Validation & Testing

**Rol**: Testing, validation, quality assurance, ECO/IV domein

**Eerste Prompt**:
```
Je bent de Validation Engineer voor het BSW-Arch project, gespecialiseerd in ECO en IV domeinen.

DOCUMENTATIE:
Laad validation-specifieke documentatie:

```bash
# ECO domein (sustainability, optimization)
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py \
  --action list \
  --domain ECO

# IV domein (intelligence, validation)
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py \
  --action list \
  --domain IV
```

FOCUS GEBIEDEN:
1. IAC Alignment Validation (arch-003)
2. Knowledge Base Testing (arch-002)
3. Resource Optimization
4. Quality Metrics

TOOLS:
- Explore subagent voor test discovery
- Plan subagent voor test strategie
- Task subagent voor test uitvoering

BOT FOCUS:
- iv-validation-bot
- iv-analysis-bot
- eco-monitoring-bot
- eco-optimization-bot

WORKFLOW:
1. Scan IAC alignment report (arch-003)
2. Valideer FAGAM compliance
3. Test knowledge base integration
4. Rapporteer aan Tab 1 (Coordinator)

Klaar om te beginnen?
```

---

## 🔄 Parallelle Workflows

### Workflow 1: Complete Architecture Analysis

**Doel**: Analyseer volledige bot factory architectuur parallel

#### Tab 1 (Coordinator)
```
TAAK: Complete Architecture Analysis

VERDEEL TAKEN:
1. Tab 2: Analyseer COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
2. Tab 3: Review deployment processen en GitOps workflows
3. Tab 4: Valideer IAC alignment en compliance

Gebruik Explore subagent in parallel voor alle tabs.

START COMMANDO:
"Begin parallel analysis - all tabs execute simultaneously"
```

#### Tab 2 (Architecture)
```
Gebruik Explore subagent:

INSTRUCTIE:
Analyseer ~/bsw-arch-docs/docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md

FOCUS:
1. Bot domains (AXIS, PIPE, ECO, IV)
2. Container strategy (apko + Wolfi)
3. Multi-AppVM architecture
4. Mermaid diagrams (10 stuks)

OUTPUT:
Samenvatting van architectuur beslissingen + design patterns

DURATION: 5-10 minuten
```

#### Tab 3 (Pipeline)
```
Gebruik Task subagent:

INSTRUCTIE:
Review deployment documentatie:
- ref-009: CLAUDE-20250901-0011-BSW-MULTI-APPVM-GITOPS.md
- ref-010: CLAUDE-20250901-0125-BSW-COMPLETE-GITOPS-STACK.md

FOCUS:
1. GitOps workflow (feature → develop → main)
2. Multi-AppVM deployment
3. Container registry setup
4. Automation scripts

OUTPUT:
Deployment strategie + automation requirements

DURATION: 5-10 minuten
```

#### Tab 4 (Validation)
```
Gebruik Explore subagent:

INSTRUCTIE:
Valideer IAC alignment:
- arch-003: IAC-ALIGNMENT-REPORT.md

FOCUS:
1. 75% alignment analyse
2. Terraform → OpenTofu migratie gaps
3. Vault → OpenBao migratie gaps
4. FAGAM compliance issues

OUTPUT:
Validation report + remediation plan

DURATION: 5-10 minuten
```

### Workflow 2: Bot Implementation Pipeline

**Doel**: Implementeer nieuwe bot parallel across domains

#### Tab 1 (Coordinator)
```
TAAK: Implementeer nieuwe "axis-strategy-bot"

STAPPEN:
1. Tab 2: Design bot architectuur
2. Tab 3: Setup CI/CD pipeline
3. Tab 4: Create test strategie

Gebruik Plan subagent in Tab 2
Gebruik Task subagent in Tab 3 & 4

COORDINATIE:
- Tab 2 moet eerst klaar zijn (design)
- Tab 3 & 4 kunnen parallel (na Tab 2)
```

#### Tab 2 (Architecture)
```
Gebruik Plan subagent:

INSTRUCTIE:
Design nieuwe axis-strategy-bot

REFERENTIES:
- arch-001: Bot factory patterns
- arch-002: Knowledge base integration
- guide-002: AI integration guide

OUTPUTS:
1. Bot specification (YAML)
2. CrewAI agent definition
3. Knowledge base queries
4. Integration patterns

SAVE TO: ~/axis-strategy-bot-spec.yaml
```

#### Tab 3 (Pipeline)
```
Gebruik Task subagent:

INSTRUCTIE:
Setup CI/CD voor axis-strategy-bot

TASKS:
1. Create Codeberg repository
2. Setup apko.yaml (wolfi-base + python + crewai)
3. Create GitHub Actions workflow
4. Configure container registry

REFERENTIES:
- ref-001: APKO domain containers strategy

OUTPUTS:
- Repository created
- CI/CD configured
- Container buildable
```

#### Tab 4 (Validation)
```
Gebruik Task subagent:

INSTRUCTIE:
Create test suite voor axis-strategy-bot

TASKS:
1. Unit tests (pytest)
2. Integration tests (CrewAI)
3. Knowledge base tests
4. Container tests

OUTPUTS:
- tests/test_axis_strategy_bot.py
- tests/test_integration.py
- Container smoke tests
```

### Workflow 3: Documentation Scanning & Knowledge Extraction

**Doel**: Scan alle documentatie en extracteer kennis voor bots

#### Tab 1 (Coordinator)
```
TAAK: Complete Documentation Scan

GEBRUIK MCP TOOLS:
- GitHub MCP: Fetch latest docs
- Filesystem MCP: Local processing

VERDEEL:
1. Tab 2: Critical & High priority docs (5 docs)
2. Tab 3: Medium priority docs (13 docs)
3. Tab 4: Create embeddings chunks

PARALLEL EXECUTION: JA
```

#### Tab 2 (Architecture)
```
Gebruik doc_scanner.py + Explore subagent:

COMMANDO:
```bash
# Laad critical priority documents
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py \
  --action list \
  --priority critical \
  --output critical_docs.json

# Laad high priority documents
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py \
  --action list \
  --priority high \
  --output high_docs.json
```

VERVOLGENS:
Gebruik Explore subagent om elk document te analyseren en key concepts te extracteren.

OUTPUT:
- critical_concepts.json
- high_priority_concepts.json
```

#### Tab 3 (Pipeline)
```
Gebruik doc_scanner.py + Explore subagent:

COMMANDO:
```bash
# Laad medium priority documents
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py \
  --action list \
  --priority medium \
  --output medium_docs.json
```

VERVOLGENS:
Scan alle 13 medium priority docs voor:
- Technical specifications
- Configuration examples
- Historical context

OUTPUT:
- medium_priority_index.json
```

#### Tab 4 (Validation)
```
Gebruik create_embeddings_chunks.py:

COMMANDO:
```bash
# Create embeddings-ready chunks
cd ~/bsw-arch-docs/bot-utils
python3 create_embeddings_chunks.py

# Output: embeddings_chunks.json
```

VERVOLGENS:
Valideer chunks:
- Check chunk sizes (< 1000 chars)
- Verify heading paths
- Validate token estimates

OUTPUT:
- embeddings_chunks.json (RAG-ready)
- validation_report.json
```

---

## 🛠️ MCP Tools Gebruik

### GitHub MCP Tool

**Gebruik in elk tab voor GitHub repository access**

#### Voorbeeld 1: Fetch Latest Documentation
```
Gebruik GitHub MCP tool:

REPOSITORY: bsw-arch/bsw-arch
ACTION: Get file contents

FILES:
- docs/metadata.json
- docs/catalogue.yaml
- docs/CHANGELOG.md

STORE LOCALLY voor offline access
```

#### Voorbeeld 2: Search Documentation
```
Gebruik GitHub MCP tool:

REPOSITORY: bsw-arch/bsw-arch
ACTION: Search code

QUERY: "knowledge base" extension:md

FILTER: docs/ directory only
```

#### Voorbeeld 3: Check for Updates
```
Gebruik GitHub MCP tool:

REPOSITORY: bsw-arch/bsw-arch
ACTION: Get latest commit

COMPARE WITH: Local metadata.json version

IF DIFFERENT: Trigger documentation rescan
```

### Codeberg MCP Tool

**Gebruik voor bot repository management**

#### Voorbeeld 1: Create New Bot Repository
```
Gebruik Codeberg MCP tool:

ORGANIZATION: AXIS-Bots
ACTION: Create repository

NAME: axis-strategy-bot
DESCRIPTION: Strategic planning and coordination bot
PRIVATE: false
AUTO_INIT: true (with README)
```

#### Voorbeeld 2: List All AXIS Bots
```
Gebruik Codeberg MCP tool:

ORGANIZATION: AXIS-Bots
ACTION: List repositories

FILTER:
- Name pattern: axis-*-bot
- Has topics: ["bot", "axis", "architecture"]
```

#### Voorbeeld 3: Update Bot README
```
Gebruik Codeberg MCP tool:

REPOSITORY: AXIS-Bots/axis-docs-bot
ACTION: Update file

FILE: README.md
CONTENT: [New README with Disconnect Collective banner]
BRANCH: feature/bsw-tech-axis-001-update-readme
```

### Filesystem MCP Tool

**Gebruik voor lokale file operations**

#### Voorbeeld 1: Read Documentation
```
Gebruik Filesystem MCP tool:

OPERATION: Read file
PATH: /home/user/bsw-arch-docs/docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md

PROCESS: Extract key sections
```

#### Voorbeeld 2: Write Analysis Results
```
Gebruik Filesystem MCP tool:

OPERATION: Write file
PATH: /home/user/analysis-results/architecture-summary.md

CONTENT: [Samenvatting van analyse uit Tab 2]
```

#### Voorbeeld 3: List Bot Repositories
```
Gebruik Filesystem MCP tool:

OPERATION: List directory
PATH: /home/user/Code/

FILTER: axis-*-bot directories
```

---

## 🤖 Subagent Orchestration

### Explore Subagent

**Specialisatie**: Codebase verkenning, file discovery, search

#### Gebruik Cases

**Tab 2: Architectuur Verkenning**
```
Gebruik Explore subagent (thoroughness: medium):

TAAK: Verken AXIS bot architectuur

ZOEK NAAR:
1. Bot type definities
2. CrewAI agent configuraties
3. Knowledge base integraties
4. API endpoints

LOCATIES:
- ~/bsw-arch-docs/docs/architecture/
- ~/bsw-arch-docs/docs/specifications/bots/
```

**Tab 3: Pipeline Discovery**
```
Gebruik Explore subagent (thoroughness: quick):

TAAK: Find all deployment scripts

ZOEK NAAR:
- deploy*.sh
- build*.yaml
- apko.yaml files
- Dockerfile variants

LOCATIES:
- ~/bsw-arch-docs/docs/processes/
- ~/bsw-arch-docs/docs/templates/
```

**Tab 4: Test Discovery**
```
Gebruik Explore subagent (thoroughness: very thorough):

TAAK: Discover all validation patterns

ZOEK NAAR:
- Test specifications
- Validation schemas
- Compliance checks
- Quality metrics

LOCATIES:
- ~/bsw-arch-docs/docs/guides/security/
- ~/bsw-arch-docs/docs/reference/
```

### Plan Subagent

**Specialisatie**: Planning, strategie, roadmapping

#### Gebruik Cases

**Tab 1: Master Planning**
```
Gebruik Plan subagent:

TAAK: Create 4-week bot integration roadmap

INPUT:
- 185 bots across 4 domains
- Documentation repository ready
- Container strategy (apko + Wolfi)

OUTPUT:
- Week-by-week plan
- Domain-specific milestones
- Resource allocation
- Risk assessment
```

**Tab 2: Architecture Planning**
```
Gebruik Plan subagent:

TAAK: Design META-KERAGR knowledge base

REFERENTIES:
- arch-002: BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
- ref-006: KNOWLEDGE-BASE-OPTIONS-COMPARISON.md

OUTPUT:
- System architecture
- Technology stack decisions
- Integration patterns
- 10-week implementation timeline
```

**Tab 3: Pipeline Planning**
```
Gebruik Plan subagent:

TAAK: Plan GitOps migration strategie

CURRENT STATE:
- Manual deployments
- Mixed container strategies
- No unified CI/CD

TARGET STATE:
- Full GitOps (feature → develop → main)
- Standardized apko/Wolfi containers
- Automated testing & deployment

OUTPUT: Migration roadmap
```

### Task Subagent

**Specialisatie**: Complexe taken uitvoeren, multi-step workflows

#### Gebruik Cases

**Tab 2: Implementation Tasks**
```
Gebruik Task subagent:

TAAK: Implementeer nieuwe AXIS bot

STAPPEN:
1. Create repository on Codeberg
2. Generate bot template (CrewAI)
3. Configure apko.yaml
4. Setup knowledge base queries
5. Create README met Disconnect Collective banner
6. Push initial commit

AUTONOMOUS: JA
```

**Tab 3: Build & Deploy Tasks**
```
Gebruik Task subagent:

TAAK: Build and deploy all PIPE bots

STAPPEN:
1. For each of 48 PIPE bots:
   - Pull latest code
   - Build container (apko)
   - Run tests
   - Push to registry
   - Deploy to K8s

PARALLEL: 4 bots at a time
DURATION: ~2 hours
```

**Tab 4: Validation Tasks**
```
Gebruik Task subagent:

TAAK: Validate all bot configurations

STAPPEN:
1. Scan all 185 bot repositories
2. Check for:
   - README compliance
   - apko.yaml validity
   - FAGAM prohibition adherence
   - License (MIT)
   - Branch structure (feature/develop/main)
3. Generate compliance report

OUTPUT: compliance-report.json
```

---

## 💡 Praktische Voorbeelden

### Voorbeeld 1: New Bot Development (Complete Workflow)

#### Tab 1: Coordinator Start
```
NIEUW BOT PROJECT: axis-analytics-bot

TAAK VERDELING:
- Tab 2: Design & Architectuur (30 min)
- Tab 3: Implementation & Build (45 min)
- Tab 4: Testing & Validation (30 min)

TOTALE DUUR: ~2 uur (met overlap)

START: Nu alle tabs parallel starten
```

#### Tab 2: Design (Start meteen)
```
Gebruik Plan subagent:

CONTEXT:
Laad AXIS domain documentatie:
```bash
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py \
  --action list \
  --domain AXIS \
  --bot axis-analytics-bot
```

DESIGN:
1. Bot doel: Analytics en reporting voor AXIS domain
2. CrewAI agent rol: Data Analyst
3. Tools: pandas, matplotlib, crewai
4. Knowledge base queries: Architecture metrics
5. Output: Analytics dashboards

SAVE: ~/designs/axis-analytics-bot-spec.yaml
```

#### Tab 3: Implementation (Start na 10 min Tab 2)
```
Gebruik Task subagent:

WACHT OP: ~/designs/axis-analytics-bot-spec.yaml

IMPLEMENTATIE:
1. Create Codeberg repo:
   ```bash
   # Via Codeberg MCP
   Create AXIS-Bots/axis-analytics-bot
   ```

2. Generate bot structure:
   ```
   axis-analytics-bot/
   ├── src/
   │   ├── main.py           (CrewAI agent)
   │   ├── analytics.py      (Analytics logic)
   │   └── queries.py        (KB queries)
   ├── tests/
   │   └── test_analytics.py
   ├── apko.yaml             (Container)
   ├── README.md             (With banner)
   └── .gitignore
   ```

3. Write code using spec
4. Commit to feature/bsw-tech-axis-015-analytics-bot
5. Merge to develop
```

#### Tab 4: Testing (Start na Tab 3 commit)
```
Gebruik Task subagent:

CLONE REPO:
```bash
git clone https://codeberg.org/AXIS-Bots/axis-analytics-bot.git
cd axis-analytics-bot
```

RUN TESTS:
1. Unit tests:
   ```bash
   pytest tests/
   ```

2. Container build test:
   ```bash
   apko build apko.yaml axis-analytics-bot:latest output.tar
   ```

3. Integration test:
   - Load documentation
   - Run analytics
   - Generate report

4. Validation:
   - FAGAM compliance check
   - Code quality (black, pylint)
   - Documentation complete

REPORT: test-results.json naar Tab 1
```

#### Tab 1: Consolidation
```
ONTVANG VAN ALLE TABS:
- Tab 2: axis-analytics-bot-spec.yaml ✓
- Tab 3: Repository created & code pushed ✓
- Tab 4: All tests passed ✓

VOLGENDE STAPPEN:
1. Merge develop → main
2. Tag release v1.0.0
3. Deploy to production
4. Update documentation
5. Notify team

STATUS: axis-analytics-bot COMPLETE 🎉
```

### Voorbeeld 2: Documentation Update Workflow

#### Tab 1: Coordinator
```
TAAK: Update alle bot documentatie met nieuwe knowledge base patterns

SCAN SCOPE: 185 bots
DOMEINEN: AXIS (45), PIPE (48), ECO (48), IV (44)

PARALLEL VERDELING:
- Tab 2: AXIS bots (45 bots)
- Tab 3: PIPE bots (48 bots)
- Tab 4: ECO + IV bots (92 bots)

ACTIE PER BOT:
1. Clone repository
2. Update README (add META-KERAGR section)
3. Add knowledge base examples
4. Commit & push

TOTALE TIJD: ~3-4 uur parallel
```

#### Tab 2: AXIS Bots (45 bots)
```
Gebruik Task subagent:

FOR EACH AXIS BOT:
```bash
for bot in axis-*-bot; do
  echo "Processing $bot..."

  git clone https://codeberg.org/AXIS-Bots/$bot.git
  cd $bot

  # Update README
  cat >> README.md << 'EOF'

## 📚 Knowledge Base Integration

This bot uses the META-KERAGR hybrid knowledge base system:

### Documentation Access
```python
from doc_scanner import DocScanner
scanner = DocScanner("/opt/documentation")
docs = scanner.get_documents_for_bot("${bot}")
```

### Recommended Documents
- arch-001: Comprehensive Bot Factory Architecture
- arch-002: Knowledge Base Architecture
- proc-001: Documentation Consolidation Strategy

See: https://github.com/bsw-arch/bsw-arch
EOF

  # Commit
  git add README.md
  git commit -m "docs: add META-KERAGR knowledge base integration"
  git push origin main

  cd ..
done
```

PROGRESS TRACKING:
- Log elk voltooid bot
- Rapporteer errors
- Update percentage (45 bots)
```

#### Tab 3 & 4: Parallel hetzelfde voor PIPE en ECO/IV

### Voorbeeld 3: Complete Architecture Audit

#### Tab 1: Coordinator
```
AUDIT SCOPE: Complete BSW-Arch bot factory

PARALLEL AUDIT TRACKS:
1. Tab 2: Architecture Compliance (TOGAF/Zachman/ArchiMate)
2. Tab 3: Infrastructure Alignment (IAC, containers, deployment)
3. Tab 4: Security & Compliance (FAGAM, licenses, standards)

GEBRUIK:
- Explore subagents (very thorough)
- All MCP tools
- Complete documentation scan

DUUR: 1-2 uur
OUTPUT: Complete audit report
```

#### Tab 2: Architecture Compliance
```
Gebruik Explore subagent (very thorough):

AUDIT CRITERIA:
1. TOGAF 9.2 compliance
2. Zachman framework alignment
3. ArchiMate 3.1 modelling

SCAN:
- All architecture documents
- Bot specifications
- Design decisions

VALIDATE:
- Architecture principles adherence
- Pattern consistency
- Documentation completeness

OUTPUT: architecture-compliance-report.md
```

#### Tab 3: Infrastructure Alignment
```
Gebruik Explore subagent (very thorough):

AUDIT CRITERIA:
1. Container strategy (apko + Wolfi)
2. IAC tools (OpenTofu, not Terraform)
3. Secrets (OpenBao, not Vault)
4. Deployment (GitOps, K8s)

SCAN:
- apko.yaml files (all 185 bots)
- IAC scripts
- Deployment manifests

VALIDATE:
- Container sizes < 50MB
- No FAGAM dependencies
- Proper secrets management

OUTPUT: infrastructure-alignment-report.md
```

#### Tab 4: Security & Compliance
```
Gebruik Explore subagent (very thorough):

AUDIT CRITERIA:
1. FAGAM prohibition
2. License compliance (MIT)
3. Security best practices
4. UK English documentation

SCAN:
- All dependencies
- All licenses
- All documentation

VALIDATE:
- No Google/Amazon/Microsoft/Apple/Facebook
- No HashiCorp products
- All repos have MIT license
- Documentation uses UK spelling

OUTPUT: security-compliance-report.md
```

---

## 🐛 Troubleshooting

### Probleem 1: Subagent Timeout

**Symptoom**: Subagent stopt na 2-3 minuten

**Oplossing**:
```
SPLIT TAAK IN KLEINERE CHUNKS:

In plaats van:
"Scan all 185 bots"

Gebruik:
"Scan first 20 bots, then continue"

OF gebruik Task subagent met explicit batching:
```bash
for batch in {1..10}; do
  start=$((($batch-1)*20))
  end=$(($batch*20))
  echo "Processing bots $start to $end"
  # Process 20 bots
done
```
```

### Probleem 2: MCP Tool Niet Beschikbaar

**Symptoom**: "MCP tool 'github' not available"

**Oplossing**:
```
CHECK MCP SERVER STATUS:

1. Verify in Claude settings:
   - MCP servers section
   - Check if servers are running
   - Restart if needed

2. Test met simpele commando:
   "List available MCP tools"

3. Als niet beschikbaar, gebruik alternatief:
   - GitHub MCP → github_api_client.py
   - Codeberg MCP → REST API direct
   - Filesystem MCP → Bash commands
```

### Probleem 3: Cross-Tab Communicatie

**Symptoom**: Tabs kunnen elkaars output niet zien

**Oplossing**:
```
GEBRUIK FILESYSTEM ALS SHARED STATE:

Tab 2 (producer):
```bash
# Write output
echo "Design complete" > /tmp/tab2-status.txt
cat design.yaml > /tmp/tab2-output.yaml
```

Tab 3 (consumer):
```bash
# Wait for Tab 2
while [ ! -f /tmp/tab2-status.txt ]; do
  sleep 5
done

# Read output
cat /tmp/tab2-output.yaml
```

Tab 1 (coordinator):
```bash
# Monitor all tabs
watch -n 5 'ls -lh /tmp/tab*-status.txt'
```
```

### Probleem 4: Doc Scanner Errors

**Symptoom**: doc_scanner.py fails met "metadata not found"

**Oplossing**:
```
VERIFY PATHS:

```bash
# Check repository location
ls -la ~/bsw-arch-docs/docs/

# Check metadata
ls -la ~/bsw-arch-docs/docs/metadata.json

# Check catalogue
ls -la ~/bsw-arch-docs/docs/catalogue.yaml

# If missing, re-clone:
cd ~
rm -rf bsw-arch-docs
git clone https://github.com/bsw-arch/bsw-arch.git bsw-arch-docs
```

# Verify doc_scanner
python3 ~/bsw-arch-docs/bot-utils/doc_scanner.py --action stats
```
```

### Probleem 5: Te Veel Parallelle Tasks

**Symptoom**: System overload, tabs worden traag

**Oplossing**:
```
REDUCE PARALLELISM:

VOOR:
- Tab 2: Process 45 bots
- Tab 3: Process 48 bots
- Tab 4: Process 92 bots

NA:
- Tab 2: Process 15 bots (batch 1)
- Tab 3: Process 15 bots (batch 1)
- Tab 4: Process 15 bots (batch 1)

Then continue with batch 2, 3, etc.

OF:
Execute tabs sequentially:
1. Tab 2 → complete
2. Tab 3 → complete
3. Tab 4 → complete
```

---

## 📚 Referenties

### Documentatie Links

- **GitHub Repository**: https://github.com/bsw-arch/bsw-arch
- **Metadata JSON**: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json
- **Catalogue YAML**: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/catalogue.yaml
- **Bot Utils**: https://github.com/bsw-arch/bsw-arch/tree/main/bot-utils

### Codeberg Organizations

- **AXIS-Bots**: https://codeberg.org/AXIS-Bots
- **PIPE-Bots**: https://codeberg.org/PIPE-Bots
- **ECO-Bots**: https://codeberg.org/ECO-Bots
- **IV-Bots**: https://codeberg.org/IV-Bots

### Tools & Scripts

- **doc_scanner.py**: `~/bsw-arch-docs/bot-utils/doc_scanner.py`
- **github_api_client.py**: `~/bsw-arch-docs/bot-utils/github_api_client.py`
- **create_embeddings_chunks.py**: `~/bsw-arch-docs/bot-utils/create_embeddings_chunks.py`

---

## ✅ Checklist: Multi-Tab Setup

Gebruik deze checklist om een multi-tab sessie op te starten:

- [ ] Repository gecloned (`~/bsw-arch-docs`)
- [ ] Python dependencies geïnstalleerd (`pyyaml`, `requests`)
- [ ] MCP servers geconfigureerd (GitHub, Codeberg, Filesystem)
- [ ] Metadata downloaded (`~/metadata.json`, `~/catalogue.yaml`)
- [ ] doc_scanner.py getest (werkt)
- [ ] 4 Claude tabs geopend
- [ ] Tab 1: Coordinator prompt ingesteld
- [ ] Tab 2: Architecture prompt ingesteld
- [ ] Tab 3: Pipeline prompt ingesteld
- [ ] Tab 4: Validation prompt ingesteld
- [ ] Shared filesystem paths gecreëerd (`/tmp/tab*-*.txt`)
- [ ] Eerste taak geïdentificeerd
- [ ] Parallel execution plan klaar

**Klaar om te beginnen!** 🚀

---

**Versie**: 1.0.0
**Laatst Bijgewerkt**: 2025-11-10
**Auteur**: BSW-Tech Architecture Team
**Licentie**: MIT
