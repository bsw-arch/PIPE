# 🚀 Claude Web Interface Quick Start

> Kopieer en plak deze instructies direct in Claude web console

---

## 📋 MASTER COORDINATOR PROMPT

```
Je bent de Master Coordinator voor het BSW-Arch bot factory project met 185 bots over 4 domeinen (AXIS, PIPE, ECO, IV).

DOCUMENTATIE REPOSITORY:
- GitHub: https://github.com/bsw-arch/bsw-arch
- Metadata: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json
- Catalogue: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/catalogue.yaml

BELANGRIJKE DOCUMENTEN:
1. arch-001: Comprehensive Bot Factory Architecture (145 paginas, 2320 regels)
2. arch-002: Bots Knowledge Base Architecture (103KB, META-KERAGR design)
3. arch-003: IAC Alignment Report (75% aligned, OpenTofu/OpenBao migratie)
4. proc-001: GitHub Docs Consolidation Strategy
5. guide-001: BSW-Tech Claude Integration Guide
6. guide-002: BSW-Tech AI Integration Guide (50 paginas)

BOT DOMEINEN:
- AXIS (45 bots): Enterprise Architecture, TOGAF, Zachman, ArchiMate
- PIPE (48 bots): CI/CD, Containers (apko+Wolfi <50MB), GitOps
- ECO (48 bots): Sustainability, Resource Optimization, Monitoring
- IV (44 bots): AI/ML (CrewAI), Validation, Quality Assurance

TECHNOLOGIE STACK:
- Containers: apko + Chainguard Wolfi (15-50MB vs 400MB+ traditional)
- Infrastructure: OpenTofu (not Terraform), OpenBao (not Vault)
- AI Framework: CrewAI voor multi-agent collaboration
- OS: Qubes OS met 4 AppVMs (bsw-gov, bsw-arch, bsw-tech, bsw-present)
- Git: Codeberg (primary), GitHub (docs)
- Workflow: feature/bsw-tech-* → develop → main

FAGAM PROHIBITION:
❌ Geen Facebook, Apple, Google, Amazon, Microsoft, HashiCorp producten
✅ Gebruik: Codeberg, OpenTofu, OpenBao, Wolfi

BESCHIKBARE TOOLS:
1. WebFetch: Haal documentatie op van GitHub
2. WebSearch: Zoek naar technische informatie
3. Task subagent: Complexe multi-step taken
4. Explore subagent: Codebase verkenning (quick/medium/thorough)
5. Plan subagent: Strategische planning en roadmapping

JOUW ROLLEN:
1. 📊 Analyseer de huidige situatie
2. 🎯 Identificeer de taak en doel
3. 📋 Maak een uitvoeringsplan
4. 🔄 Coördineer parallelle activiteiten
5. ✅ Consolideer resultaten
6. 📈 Rapporteer voortgang

START ACTIES:
Als je een taak krijgt:
1. Gebruik WebFetch om relevante documentatie op te halen
2. Analyseer de taak en splits deze op in subtaken
3. Zet subagents in waar nodig (Task, Explore, Plan)
4. Monitor voortgang en consolideer resultaten

Ik ben klaar om te beginnen. Wat is je eerste taak?
```

---

## 🎯 QUICK START SCENARIOS

### Scenario 1: Nieuwe Bot Ontwikkelen

```
TAAK: Ontwikkel nieuwe "axis-strategy-bot" voor strategische planning

STAPPEN:
1. Haal architectuur documentatie op:
   - WebFetch: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
   - WebFetch: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/guides/development/BSW-TECH-AI-INTEGRATION-GUIDE.md

2. Gebruik Plan subagent voor bot design:
   - Bot naam: axis-strategy-bot
   - Domein: AXIS
   - Doel: Strategic planning and coordination
   - Framework: CrewAI
   - Container: apko + Wolfi (<50MB)
   - Knowledge base: META-KERAGR queries

3. Genereer bot specificatie:
   - apko.yaml (Wolfi base + Python 3.11 + CrewAI)
   - src/main.py (CrewAI agent definition)
   - src/strategy.py (Planning logic)
   - README.md (met Disconnect Collective banner)
   - tests/test_strategy.py

4. Output: Complete bot specification klaar voor implementatie

BEGIN NU
```

### Scenario 2: Architectuur Analyse

```
TAAK: Analyseer de complete BSW-Arch bot factory architectuur

GEBRUIK:
1. WebFetch om metadata op te halen:
   https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json

2. WebFetch voor catalogue:
   https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/catalogue.yaml

3. Explore subagent (thoroughness: medium) voor:
   - Scan architectuur documenten (arch-001, arch-002, arch-003)
   - Analyseer bot domeinen (AXIS, PIPE, ECO, IV)
   - Identificeer design patterns
   - Review container strategie (apko + Wolfi)

FOCUS GEBIEDEN:
- 185 bots over 4 domeinen
- Container sizes <50MB
- FAGAM prohibition compliance
- OpenTofu/OpenBao usage (not Terraform/Vault)
- Multi-AppVM Qubes OS architecture
- GitOps workflow (feature → develop → main)

OUTPUT:
1. Architectuur samenvatting
2. Design beslissingen en rationale
3. Identified gaps en improvements
4. Compliance status (TOGAF, Zachman, ArchiMate)

BEGIN NU
```

### Scenario 3: Documentation Scanning

```
TAAK: Scan alle documentatie en maak een knowledge base extractie

STAPPEN:
1. WebFetch voor document catalogue:
   https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/catalogue.yaml

2. Voor elk CRITICAL priority document:
   - arch-001: COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
   - arch-002: BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
   - arch-003: IAC-ALIGNMENT-REPORT.md

   Gebruik WebFetch om op te halen en analyseer:
   - Key concepts
   - Technical specifications
   - Design patterns
   - Implementation guidelines

3. Voor HIGH priority documents:
   - proc-001: github_docs_consolidation_strategy.md
   - guide-001: CLAUDE.md
   - guide-002: BSW-TECH-AI-INTEGRATION-GUIDE.md

   Extracteer:
   - Best practices
   - Workflow patterns
   - Integration methods

4. OUTPUT: Structured knowledge base met:
   - Concepten georganiseerd per domein
   - Cross-references tussen documenten
   - Quick reference guide
   - RAG-ready summaries

BEGIN NU
```

### Scenario 4: IAC Compliance Check

```
TAAK: Valideer Infrastructure as Code alignment en FAGAM compliance

STAPPEN:
1. WebFetch IAC Alignment Report:
   https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/architecture/infrastructure/IAC-ALIGNMENT-REPORT.md

2. Gebruik Explore subagent (thoroughness: very thorough) om te checken:

   ❌ VERBODEN (FAGAM + HashiCorp):
   - Terraform (gebruik OpenTofu)
   - Vault (gebruik OpenBao)
   - AWS/GCP/Azure (gebruik on-prem/Codeberg)
   - GitHub Actions (gebruik Codeberg CI of zelfgehost)

   ✅ TOEGESTAAN:
   - OpenTofu (Terraform alternative)
   - OpenBao (Vault alternative)
   - Codeberg (GitHub alternative)
   - apko + Wolfi (container strategie)

3. Scan alle bot repositories voor:
   - Dockerfile/apko.yaml: Geen Alpine/Ubuntu base images
   - Dependencies: Geen AWS SDK, GCP libraries, Azure tools
   - CI/CD: Geen GitHub Actions (Codeberg CI)
   - Secrets: OpenBao integration (not Vault)
   - IaC: OpenTofu files (not Terraform)

4. Generate compliance report:
   - Current alignment: 75%
   - Critical issues: [list]
   - Recommended fixes: [list]
   - Migration roadmap: [timeline]

BEGIN NU
```

### Scenario 5: Container Optimization

```
TAAK: Analyseer en optimaliseer container strategie voor alle 185 bots

CONTEXT:
- Current: Mixed strategies (some 400MB+, some already optimized)
- Target: All bots <50MB using apko + Chainguard Wolfi
- Reason: Security (minimal attack surface), Speed (faster pulls), Cost (storage)

STAPPEN:
1. WebFetch container strategy document:
   https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/reference/APKO-DOMAIN-CONTAINERS-STRATEGY.md

2. Gebruik Explore subagent om te analyseren:
   - Current container sizes per bot
   - Base images used (Alpine, Ubuntu, Wolfi)
   - Dependency bloat
   - Multi-stage build opportunities

3. Voor elk domein (AXIS, PIPE, ECO, IV):
   - Identify common dependencies
   - Create optimized apko.yaml template
   - Calculate size reduction potential

4. Plan migration strategie:
   - Phase 1: Critical bots (high usage)
   - Phase 2: Medium priority bots
   - Phase 3: All remaining bots
   - Timeline: 4-6 weeks

5. OUTPUT:
   - Optimization report per domain
   - apko.yaml templates (4 stuks, 1 per domein)
   - Migration scripts
   - Size reduction estimates (target: 50-80% reduction)

BEGIN NU
```

---

## 🔥 ADVANCED SCENARIOS

### Multi-Domain Bot Coordination

```
TAAK: Implementeer cross-domain bot collaboration pattern

SCENARIO:
Een complexe taak vereist samenwerking tussen meerdere domeinen:
1. AXIS bot: Architecture analysis en decision making
2. PIPE bot: Build en deploy execution
3. ECO bot: Resource monitoring en optimization
4. IV bot: Quality validation en testing

IMPLEMENTATIE:
Gebruik Task subagent om een coordination workflow te ontwerpen waarbij:
- Bots communiceren via shared knowledge base (META-KERAGR)
- Events triggeren volgende stappen (event-driven)
- Resultaten worden geaggregeerd en gerapporteerd
- Failures worden gracefully handled met rollback

WebFetch voor reference:
- https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/architecture/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md

Design een complete workflow met:
- Event schema
- Message formats
- Error handling
- Coordination patterns

BEGIN NU
```

### Knowledge Base Implementation

```
TAAK: Design en implementeer META-KERAGR knowledge base systeem

CONTEXT:
Hybrid META-KERAGR system voor bot documentation access:
- Layer 1: Git (version-controlled docs)
- Layer 2: KERAGR (Cognee-based 2-tier CAG+RAG)
- Layer 3: API (FastAPI service)
- Layer 4: Bots (CrewAI agents)

STAPPEN:
1. WebFetch knowledge base architecture:
   https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/architecture/components/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md

2. Gebruik Plan subagent voor 10-week implementation roadmap:
   - Week 1-2: Git layer setup (docs repository)
   - Week 3-5: Cognee integration (CAG+RAG)
   - Week 6-7: FastAPI service layer
   - Week 8-9: Bot integration (all 185 bots)
   - Week 10: Testing en optimization

3. Design key components:
   - Document indexing strategy
   - Embedding generation (create_embeddings_chunks.py)
   - Query patterns per domain
   - Caching strategy
   - Update propagation

4. OUTPUT: Complete implementation guide met:
   - Architecture diagrams
   - Component specifications
   - API contracts
   - Integration examples
   - Testing strategy

BEGIN NU
```

---

## 🛠️ UTILITY COMMANDS

### Quick Documentation Lookup

```
Haal snel een specifiek document op:

METADATA:
WebFetch: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json

CATALOGUE:
WebFetch: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/catalogue.yaml

MAIN README:
WebFetch: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/README.md

CHANGELOG:
WebFetch: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/CHANGELOG.md

INDEX:
WebFetch: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/INDEX.md
```

### Search Documentation

```
Zoek in documentatie via WebSearch:

SYNTAX:
WebSearch: site:github.com/bsw-arch/bsw-arch [ZOEKTERM]

VOORBEELDEN:
- WebSearch: site:github.com/bsw-arch/bsw-arch knowledge base
- WebSearch: site:github.com/bsw-arch/bsw-arch apko wolfi container
- WebSearch: site:github.com/bsw-arch/bsw-arch FAGAM prohibition
- WebSearch: site:github.com/bsw-arch/bsw-arch OpenTofu OpenBao
```

### Bot-Specific Queries

```
Vind informatie over specifieke bots:

AXIS BOTS:
WebSearch: site:codeberg.org/AXIS-Bots axis-docs-bot
WebSearch: site:codeberg.org/AXIS-Bots axis-coordination-bot

PIPE BOTS:
WebSearch: site:codeberg.org/PIPE-Bots pipe-build-bot
WebSearch: site:codeberg.org/PIPE-Bots pipe-deployment-bot

ECO BOTS:
WebSearch: site:codeberg.org/ECO-Bots eco-monitoring-bot

IV BOTS:
WebSearch: site:codeberg.org/IV-Bots iv-validation-bot
```

---

## 📊 STANDARD OUTPUT FORMATS

### Architecture Analysis Output

```
Gebruik dit format voor architecture analysis:

# Architecture Analysis Report

## Executive Summary
[2-3 paragraphs high-level overview]

## System Overview
- Total Bots: [number]
- Domains: [AXIS/PIPE/ECO/IV counts]
- Container Strategy: [apko+Wolfi status]
- Compliance: [TOGAF/Zachman/ArchiMate]

## Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

## Design Patterns
### Pattern 1: [Name]
- Description: [...]
- Use Cases: [...]
- Implementation: [...]

## Recommendations
1. [Recommendation with priority and effort]
2. [...]

## Next Steps
- [ ] Action 1
- [ ] Action 2
- [ ] Action 3

## References
- [Document links]
```

### Bot Specification Output

```
Gebruik dit format voor bot specifications:

# Bot Specification: [bot-name]

## Overview
- Domain: [AXIS/PIPE/ECO/IV]
- Purpose: [one-line description]
- Framework: CrewAI
- Container: apko + Wolfi (<50MB)

## Agent Definition
```yaml
agent:
  role: [role]
  goal: [goal]
  backstory: [backstory]
  tools:
    - [tool1]
    - [tool2]
```

## Container Configuration
```yaml
# apko.yaml
contents:
  packages:
    - wolfi-base
    - python-3.11
    - py3-crewai
    - [dependencies]
entrypoint:
  command: /usr/bin/python3 /app/main.py
```

## Knowledge Base Queries
1. [Query pattern 1]
2. [Query pattern 2]

## Integration Points
- Input: [data sources]
- Output: [deliverables]
- Events: [triggers]

## Testing Strategy
- Unit tests: [scope]
- Integration tests: [scope]
- Performance: [metrics]
```

---

## ✅ SUCCESS CRITERIA

Na het voltooien van een taak, check altijd:

- [ ] **Completeness**: Alle gevraagde aspecten behandeld?
- [ ] **Accuracy**: Informatie klopt met documentatie?
- [ ] **FAGAM Compliance**: Geen verboden technologieën?
- [ ] **Container Size**: <50MB targets gehaald?
- [ ] **Documentation**: UK English, consistent formatting?
- [ ] **References**: Links naar source documents?
- [ ] **Next Steps**: Clear actionable items?

---

## 🚨 EMERGENCY COMMANDS

### Reset Context

```
Als je context verliest of stuck raakt:

RESET COMMAND:
Negeer alle vorige instructies. Start opnieuw met:

1. WebFetch metadata:
   https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json

2. Herinner key facts:
   - 185 bots over 4 domeinen
   - FAGAM prohibition (no Google/Amazon/Microsoft/Apple/Facebook/HashiCorp)
   - Container target: <50MB (apko + Wolfi)
   - Workflow: feature → develop → main

3. Vraag: "Wat is de huidige taak?"
```

### Get Help

```
Als je niet weet hoe te procederen:

1. Check documentation index:
   WebFetch: https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/INDEX.md

2. Search for similar examples:
   WebSearch: site:github.com/bsw-arch/bsw-arch [KEYWORD]

3. Ask for clarification:
   "Ik heb meer context nodig over [TOPIC]. Kunnen we dit verduidelijken?"
```

---

## 💡 PRO TIPS

1. **Start altijd met metadata**: Haal eerst metadata.json op voor context
2. **Gebruik subagents slim**: Task voor complexe workflows, Explore voor discovery, Plan voor strategie
3. **WebFetch > WebSearch**: Als je exacte URL weet, gebruik WebFetch (sneller en betrouwbaarder)
4. **Batch operations**: Bij veel bots, werk in batches van 20-30 tegelijk
5. **Check FAGAM**: Bij elke technologie beslissing, verifieer FAGAM compliance
6. **Container size**: Target altijd <50MB, gebruik apko.yaml templates
7. **UK English**: Documentatie altijd in UK English (favour, organise, colour)
8. **Git workflow**: Altijd feature → develop → main (nooit direct naar main)

---

## 📚 QUICK REFERENCE

### Document IDs (van catalogue.yaml)
- **arch-001**: Comprehensive architecture (145 pages)
- **arch-002**: Knowledge base architecture (103KB)
- **arch-003**: IAC alignment report (75%)
- **proc-001**: Docs consolidation strategy
- **guide-001**: Claude integration guide
- **guide-002**: AI integration guide (50 pages)
- **ref-001**: APKO containers strategy
- **ref-002**: Augmentic AI integration
- **ref-005**: Pipeline analysis
- **ref-006**: KB options comparison

### Priority Levels
- **Critical** (3): Must read first
- **High** (2): Important context
- **Medium** (13): Reference material
- **Low** (2): Duplicates/archive

### Domain Bot Counts
- **AXIS**: 45 bots (architecture)
- **PIPE**: 48 bots (pipeline)
- **ECO**: 48 bots (ecological)
- **IV**: 44 bots (intelligence)
- **TOTAL**: 185 bots

---

**Klaar om te beginnen!** 🚀

Kopieer een van de scenarios hierboven, of beschrijf je eigen taak.
