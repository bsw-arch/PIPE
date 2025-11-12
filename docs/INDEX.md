# BSW-Arch Documentation Index

This repository contains comprehensive documentation for the BSW-Tech bot factory architecture deployed on Codeberg.

## 📚 Documentation Structure

### Architecture Documentation (`architecture/`)
- **Main Analysis**: COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md (145 pages)
- **CAG+RAG Solution**: CAG-RAG-SOLUTION-ARCHITECTURE.md (2-tier cascaded domain integration)
- **Data Architecture**: DATA-ARCHITECTURE-GOVERNANCE-FRAMEWORK.md (Data governance, quality, compliance)
- **Infrastructure**: IAC-ALIGNMENT-REPORT.md
- **Knowledge Base**: BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
- **Domains**: AXIS, PIPE, ECO, IV domain-specific documentation

### Process Documentation (`processes/`)
- Workflow definitions
- Deployment procedures
- GitOps automation
- CI/CD pipelines

### Development Guides (`guides/`)
- **Setup Guides**: IV Bots Setup (Intelligence/Validation domain)
- **Integration Guides**:
  - **Complete AI Platform**: OpenCode + OpenSpec + Knowledge Graph RAG (Spec-driven development)
  - **Cloud Storage**: Proton Drive + IV Bots + CAG+RAG + OpenCode
- Multi-tab Claude workflows
- BSW-Tech integration guide
- AXIS bots setup and operations guide
- CAG+RAG technical implementation guide
- **CAG+RAG step-by-step implementation guide (How to Build)**
- Security best practices
- Development standards
- Bot domain instructions (PIPE, AXIS, ECO, IV)

### Bot Specifications (`specifications/`)
- Bot type definitions (49 bots across 4 domains)
- Container specifications (apko/Wolfi)
- Integration patterns

### Architecture Diagrams (`diagrams/`)
- System architecture diagrams
- Workflow visualizations
- Infrastructure layouts

### Templates (`templates/`)
- Bot creation templates
- Container configuration templates
- Deployment templates

### Reference Documentation (`reference/`)
- API documentation
- TOGAF/Zachman/ArchiMate standards
- Glossary and terminology

## 🚀 Quick Start

1. **Understanding the Architecture**:
   - Start with: `architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md`
   - CAG+RAG Solution: `architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md`

2. **Setting up Development Environment**:
   - Read: `guides/development/CLAUDE.md`
   - Follow: `guides/development/BSW-TECH-AI-INTEGRATION-GUIDE.md`

3. **Setting up IV Bots** (Intelligence/Validation domain):
   - Complete setup guide: `guides/setup/IV-BOTS-SETUP.md`
   - RAG implementation, Ollama integration, AI/ML workflows

4. **Complete AI Development Platform** (OpenCode + OpenSpec + Knowledge Graph RAG):
   - Full integration guide: `guides/integration/OPENCODE-OPENSPEC-GRAPH-RAG-INTEGRATION.md`
   - Spec-driven development with OpenSpec, Knowledge Graph (Neo4j), AI coding (OpenCode)
   - Complete traceability from requirements to code, Neovim integration

5. **Proton Drive Integration** (Secure cloud storage for documentation):
   - Integration guide: `guides/integration/PROTON-DRIVE-INTEGRATION.md`
   - Automated sync workflows, OpenCode integration, FAGAM-compliant storage

6. **AXIS Bots Setup** (Architecture Domain):
   - Read: `guides/AXIS-BOTS-SETUP-GUIDE.md`
   - Follow the 15-section comprehensive setup guide

7. **CAG+RAG System Implementation**:
   - Architecture: `architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md`
   - Technical Guide: `guides/development/CAG-RAG-TECHNICAL-IMPLEMENTATION-GUIDE.md`
   - Data Framework: `architecture/DATA-ARCHITECTURE-GOVERNANCE-FRAMEWORK.md`
   - **Build Guide**: `guides/CAG-RAG-IMPLEMENTATION-GUIDE.md` ⭐ (Start here to build the system)
   - **Working Code**: `code/` ⭐ (Complete implementation with HuggingFace + Llama)

8. **Creating a New Bot**:
   - Use templates in: `templates/bot/`
   - Follow specifications in: `specifications/bots/`

9. **Deployment**:
   - Review: `processes/workflows/`
   - Execute: `processes/deployment/`

## 🤖 Bot Access Patterns

Bots can access this documentation through:

1. **Git Clone**: Clone this repository into bot containers
2. **GitHub API**: Programmatic access via REST API
3. **Proton Drive**: Secure, encrypted cloud sync (FAGAM-compliant)
4. **Knowledge Graph**: Neo4j-based graph database with spec-code traceability
5. **MCP Server**: Model Context Protocol for AI tool integration
6. **META-KERAGR**: Future integration with knowledge base system

## 📊 Key Metrics

- **Total Bots**: 185 (AXIS: 45, PIPE: 48, ECO: 48, IV: 44)
- **Bot Domains**: 4 (AXIS, PIPE, ECO, IV)
- **Container Size**: <50MB per bot (apko/Wolfi)
- **AppVMs**: 4 (bsw-gov, bsw-arch, bsw-tech, bsw-present)
- **AI Platform**: OpenCode + OpenSpec + Neo4j + ChromaDB + Ollama

## 🔒 Security & Compliance

- **FAGAM Prohibition**: No Facebook, Apple, Google, Amazon, Microsoft, HashiCorp
- **Open Source Alternatives**: OpenTofu (not Terraform), OpenBao (not Vault)
- **UK English**: All documentation uses British English

## 📝 Contributing

All updates follow BSW-Tech workflow:
```
feature/bsw-tech-* → develop → main
```

## 🔗 Related Repositories

- **Codeberg Bots**:
  - AXIS-Bots: https://codeberg.org/AXIS-Bots
  - PIPE-Bots: https://codeberg.org/PIPE-Bots
  - ECO-Bots: https://codeberg.org/ECO-Bots
  - IV-Bots: https://codeberg.org/IV-Bots

---

**Last Updated**: 2025-11-11
**Maintained by**: BSW-Tech Architecture Team
