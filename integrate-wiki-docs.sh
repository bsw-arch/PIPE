#!/bin/bash
# Bot Wiki Documentation Integration Script
# Integrates GitHub bsw-arch documentation into Codeberg bot repository wikis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO_PATH="/home/user/github/bsw-arch"
WORK_DIR="/tmp/bot-integration"
BRANCH_NAME="feature/bsw-tech-arch-001-github-wiki-docs-integration"

# Function to print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to integrate docs into wiki
integrate_wiki_docs() {
    local domain=$1
    local bot_name=$2
    local org_name="${domain}-Bots"
    local repo_url="git@codeberg.org:${org_name}/${bot_name}.git"
    local bot_dir="${WORK_DIR}/${domain}/${bot_name}"

    print_info "Processing ${org_name}/${bot_name} wiki"

    # Create work directory
    mkdir -p "${WORK_DIR}/${domain}"
    cd "${WORK_DIR}/${domain}"

    # Clone repository
    if [ -d "${bot_name}" ]; then
        print_warning "Repository already cloned, using existing"
        cd "${bot_name}"
        git fetch origin
    else
        print_info "Cloning ${repo_url}"
        if ! git clone "${repo_url}" 2>&1; then
            print_error "Failed to clone ${repo_url} - repository may not exist"
            return 1
        fi
        cd "${bot_name}"
    fi

    # Check if wiki directory exists
    if [ ! -d "wiki" ]; then
        print_warning "No wiki directory found in ${bot_name}"
        return 1
    fi

    # Check if branch already exists
    if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
        print_warning "Branch ${BRANCH_NAME} already exists, checking out"
        git checkout "${BRANCH_NAME}"
    else
        # Create feature branch from main or develop
        if git show-ref --verify --quiet refs/heads/main; then
            git checkout main
            git pull origin main
        elif git show-ref --verify --quiet refs/heads/develop; then
            git checkout develop
            git pull origin develop
        fi
        git checkout -b "${BRANCH_NAME}"
    fi

    # Create wiki subdirectories for organization
    mkdir -p wiki/Architecture
    mkdir -p wiki/Domain
    mkdir -p wiki/Reference
    mkdir -p wiki/Guides

    print_info "Creating wiki pages for architecture documentation"

    # Create Architecture wiki pages
    cat > wiki/Architecture/Enterprise-CAG-RAG.md << 'WIKEOF'
---
title: "Enterprise CAG+RAG Architecture"
description: "Multi-domain CAG+RAG solution architecture"
category: "Architecture"
---

# Enterprise CAG+RAG Solution Architecture

**Source:** [bsw-arch GitHub repository](https://github.com/bsw-arch/bsw-arch)

This page links to the comprehensive Enterprise CAG+RAG Solution Architecture documentation.

## Overview

The BSW-Tech bot factory implements a 2-tier CAG+RAG (Context-Aware Generation + Retrieval-Augmented Generation) architecture across all 185 bots in 8 domains.

## Full Documentation

For the complete architecture documentation, see:
- Repository: `/docs/shared/architecture/ENTERPRISE-CAG-RAG-SOLUTION-ARCHITECTURE.md`
- Or view the [GitHub source](https://github.com/bsw-arch/bsw-arch/blob/main/docs/architecture/ENTERPRISE-CAG-RAG-SOLUTION-ARCHITECTURE.md)

## Key Components

- **CAG Layer (Tier 1)**: Context-aware query classification and routing
- **RAG Layer (Tier 2)**: Hybrid retrieval (FAISS + Neo4j + MongoDB)
- **META-KERAGR**: Master knowledge coordination system
- **Multi-bot Coordination**: CrewAI orchestration

## Related Pages

- [[Architecture/Bot-Factory-Architecture|Bot Factory Comprehensive Analysis]]
- [[Architecture/Data-Architecture-Governance|Data Architecture & Governance]]
- [[Guides/CAG-RAG-Implementation|CAG+RAG Implementation Guide]]
WIKEOF

    cat > wiki/Architecture/Bot-Factory-Architecture.md << 'WIKEOF'
---
title: "Bot Factory Comprehensive Architecture"
description: "Complete 185-bot factory analysis (145 pages)"
category: "Architecture"
---

# Comprehensive Bot Factory Architecture Analysis

**Source:** [bsw-arch GitHub repository](https://github.com/bsw-arch/bsw-arch)

## Overview

This is the master architecture document covering all 185 bots across 8 domains:
- ECO (48 bots) - Infrastructure & Operations
- PIPE (48 bots) - CI/CD & Integration
- AXIS (45 bots) - Architecture & Design
- IV (44 bots) - AI/ML & Intelligence
- BU, BNI, BNP, DC (~136 bots) - Business & Content

## Full Documentation

**Location:** `/docs/shared/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md`

This 145-page document includes:
- System architecture overview
- Domain-by-domain analysis
- Container strategy (apko + Wolfi)
- Network segmentation
- Security compliance
- Deployment patterns

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Bots | 185 across 8 domains |
| Container Size | <50MB per bot |
| Network Zones | 12+ segmented zones |
| Architecture | 2-Tier CAG+RAG |

## Related Pages

- [[Architecture/Enterprise-CAG-RAG|Enterprise CAG+RAG]]
- [[Reference/Augmentic-AI-Integration|Augmentic AI Framework]]
WIKEOF

    cat > wiki/Architecture/Data-Architecture-Governance.md << 'WIKEOF'
---
title: "Data Architecture & Governance Framework"
description: "BSW-Tech data governance and architecture"
category: "Architecture"
---

# Data Architecture & Governance Framework

**Source:** [bsw-arch GitHub repository](https://github.com/bsw-arch/bsw-arch)

## Overview

Enterprise data governance framework for BSW-Tech bot factory covering:
- Data classification and lifecycle
- Privacy and compliance (GDPR, ISO 27001)
- Master Data Management (MDM)
- Data quality and lineage

## Full Documentation

**Location:** `/docs/shared/architecture/DATA-ARCHITECTURE-GOVERNANCE-FRAMEWORK.md`

## Related Standards

- **TOGAF 9.2**: Enterprise architecture framework
- **Zachman Framework**: Architecture documentation
- **ArchiMate 3.1**: Architecture modelling
- **ISO 27001**: Information security
WIKEOF

    # Create Guides wiki pages
    cat > wiki/Guides/BSW-Tech-AI-Integration.md << 'WIKEOF'
---
title: "BSW-Tech AI Integration Guide"
description: "Integrating AI capabilities with BSW-Tech workflows"
category: "Guides"
---

# BSW-Tech AI Integration Guide

**Source:** [bsw-arch GitHub repository](https://github.com/bsw-arch/bsw-arch)

## Overview

Guide for integrating AI capabilities (Claude, local LLMs, CrewAI) with BSW-Tech development workflows.

## Full Documentation

**Location:** `/docs/shared/guides/BSW-TECH-AI-INTEGRATION-GUIDE.md`

## Topics Covered

- Claude Code integration
- Multi-tab workflows
- Bot development patterns
- AI-assisted architecture
- CrewAI multi-agent coordination

## Related Pages

- [[Guides/Claude-Integration|Claude Integration]]
- [[Reference/Augmentic-AI-Integration|Augmentic AI Framework]]
WIKEOF

    cat > wiki/Guides/Claude-Integration.md << 'WIKEOF'
---
title: "Claude Integration Guide"
description: "Using Claude Code with BSW-Tech projects"
category: "Guides"
---

# Claude Integration Guide

**Source:** [bsw-arch GitHub repository](https://github.com/bsw-arch/bsw-arch)

## Overview

Comprehensive guide for using Claude Code with BSW-Tech bot development including:
- CLAUDE.md format specifications
- Multi-tab console workflows
- Bot-specific instructions
- Architecture documentation integration

## Full Documentation

**Location:** `/docs/shared/guides/CLAUDE.md`

## Key Concepts

- **CLAUDE.md files**: Bot-specific AI instructions
- **Multi-tab workflows**: Parallel bot development
- **Context management**: Efficient documentation access
- **BSW-Tech conventions**: UK English, TOGAF compliance

## Related Pages

- [[Guides/BSW-Tech-AI-Integration|AI Integration Guide]]
- [[Guides/Multi-Tab-Claude-Console|Multi-Tab Console Instructions]]
WIKEOF

    # Create Reference wiki pages
    cat > wiki/Reference/Augmentic-AI-Integration.md << 'WIKEOF'
---
title: "Augmentic AI Integration Plan"
description: "Framework for Augmentic AI implementation"
category: "Reference"
---

# Augmentic AI Integration Plan

**Source:** [bsw-arch GitHub repository](https://github.com/bsw-arch/bsw-arch)

## What is Augmentic AI?

**Augmentic AI** = Augment + Authentic + Automatic

A paradigm shift from traditional automation to self-improving, collaborative AI systems that:
- Learn continuously through META-KERAGR knowledge graphs
- Collaborate autonomously via CrewAI multi-agent orchestration
- Adapt intelligently with pattern recognition
- Operate independently with human oversight for critical decisions

## Full Documentation

**Location:** `/docs/shared/reference/AUGMENTIC-AI-INTEGRATION-PLAN.md`

## Implementation Across Domains

All 185 bots implement Augmentic AI principles:
- **ECO**: Infrastructure self-optimization
- **AXIS**: Architecture pattern learning
- **IV**: RAG system adaptation
- **PIPE**: CI/CD workflow improvement

## Related Pages

- [[Architecture/Bot-Factory-Architecture|Bot Factory Architecture]]
- [[Reference/Knowledge-Base-Quick-Start|Knowledge Base Setup]]
WIKEOF

    cat > wiki/Reference/Knowledge-Base-Quick-Start.md << 'WIKEOF'
---
title: "Knowledge Base Quick Start"
description: "Setting up bot knowledge bases"
category: "Reference"
---

# Knowledge Base Quick Start

**Source:** [bsw-arch GitHub repository](https://github.com/bsw-arch/bsw-arch)

## Overview

Quick start guide for setting up knowledge bases for bots including:
- META-KERAGR hybrid knowledge graphs
- Neo4j graph databases
- FAISS vector stores
- MongoDB document storage
- Redis caching

## Full Documentation

**Location:** `/docs/shared/reference/KNOWLEDGE-BASE-QUICK-START.md`

## Quick Setup

```bash
# Clone documentation
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation

# Run knowledge graph setup
cd /opt/documentation
./setup-knowledge-graph.sh
```

## Components

- **Neo4j**: Graph relationships
- **FAISS**: Vector similarity search
- **MongoDB**: Document storage
- **Redis**: Cache layer
- **META-KERAGR**: Coordination layer

## Related Pages

- [[Architecture/Enterprise-CAG-RAG|CAG+RAG Architecture]]
- [[Guides/CAG-RAG-Implementation|Implementation Guide]]
WIKEOF

    # Add domain-specific wiki pages
    print_info "Creating ${domain} domain wiki pages"

    case ${domain} in
        ECO)
            cat > wiki/Domain/ECO-Architecture.md << 'WIKEOF'
---
title: "ECO Domain Architecture"
description: "Ecological domain infrastructure and operations"
category: "Domain"
---

# ECO Domain Architecture

**Domain:** ECO (Ecological)
**Bot Count:** 48
**Network:** 10.100.8.0/24

## Overview

The ECO domain manages infrastructure provisioning, resource optimization, monitoring, and operational efficiency for all 185 bots.

## Full Documentation

**Locations:**
- `/docs/domain/ECO/ECO-DOMAIN-ARCHITECTURE.md`
- `/docs/domain/ECO/ECO-BOTS-README.md`
- `/docs/domain/ECO/ECO-BOTS-QUICK-START.md`

## ECO Bot Categories

1. **Infrastructure Management** (8 bots)
2. **Resource Optimization** (8 bots)
3. **Monitoring & Observability** (8 bots)
4. **Container & Registry** (6 bots)
5. **Storage & Data** (6 bots)
6. **Network & Security** (6 bots)
7. **Compliance & Audit** (6 bots)

## Related Pages

- [[Architecture/Bot-Factory-Architecture|Complete Bot Factory]]
- [[Getting-Started|ECO Bot Getting Started]]
WIKEOF
            ;;
        AXIS)
            cat > wiki/Domain/AXIS-Architecture.md << 'WIKEOF'
---
title: "AXIS Domain Architecture"
description: "Architecture domain design patterns and governance"
category: "Domain"
---

# AXIS Domain Architecture

**Domain:** AXIS (Architecture)
**Bot Count:** 45
**Network:** 10.100.6.0/24

## Overview

The AXIS domain provides enterprise architecture, design patterns, compliance validation, and architectural governance for the bot factory.

## Full Documentation

**Location:** `/docs/domain/AXIS/AXIS-BOTS-SETUP-GUIDE.md`

## AXIS Specializations

- Architecture documentation generation
- Design pattern validation
- TOGAF 9.2 compliance checking
- Blueprint generation
- Multi-bot coordination

## CAG+RAG Integration

AXIS bots use advanced CAG+RAG capabilities for architecture knowledge retrieval.

**See:** [[Architecture/Enterprise-CAG-RAG|Enterprise CAG+RAG Architecture]]

## Related Pages

- [[Architecture/Bot-Factory-Architecture|Complete Bot Factory]]
- [[Guides/Multi-Tab-Claude-Console|Multi-Tab Development]]
WIKEOF
            ;;
        IV)
            cat > wiki/Domain/IV-Architecture.md << 'WIKEOF'
---
title: "IV Domain Architecture"
description: "IntelliVerse AI/ML and RAG systems"
category: "Domain"
---

# IV Domain Architecture

**Domain:** IV (IntelliVerse/Intelligence)
**Bot Count:** 44
**Network:** 10.100.7.0/24

## Overview

The IV domain handles LLM orchestration, RAG systems, validation, and intelligence coordination across all bot operations.

## Full Documentation

**Locations:**
- `/docs/domain/IV/IV-DOMAIN-ARCHITECTURE.md`
- `/docs/domain/IV/IV-BOTS-CAG-RAG-IMPLEMENTATION.md`
- `/docs/domain/IV/IV-BOTS-SETUP.md`

## IV Specializations

- Multi-model LLM orchestration
- Hybrid RAG retrieval (vector + graph + document)
- Knowledge base indexing
- Context and session management
- Quality validation

## CAG+RAG System

IV domain is the master implementation of the 2-tier CAG+RAG architecture.

**See:** `/docs/shared/cag-rag/` directory

## Related Pages

- [[Architecture/Enterprise-CAG-RAG|CAG+RAG Architecture]]
- [[Reference/Knowledge-Base-Quick-Start|Knowledge Base Setup]]
WIKEOF
            ;;
        PIPE)
            cat > wiki/Domain/PIPE-Architecture.md << 'WIKEOF'
---
title: "PIPE Domain Architecture"
description: "Pipeline domain CI/CD and integration"
category: "Domain"
---

# PIPE Domain Architecture

**Domain:** PIPE (Pipeline)
**Bot Count:** 48
**Network:** 10.100.1.0/24

## Overview

The PIPE domain provides core API management, integration orchestration, CI/CD pipelines, and deployment automation.

## Full Documentation

**Location:** `/docs/domain/PIPE/PIPE-BOTS-INSTRUCTIONS.md`

## PIPE Specializations

- API management and gateway (PAPI)
- Artifact and build management (PART)
- Integration orchestration (PINT)
- Component management (PCMP)
- Deployment automation (PDEP)

## Pipeline Categories

1. **API & Gateway Bots**
2. **Build & Artifact Bots**
3. **Integration Bots**
4. **Deployment Bots**
5. **Monitoring & Validation Bots**

## Related Pages

- [[Architecture/Bot-Factory-Architecture|Complete Bot Factory]]
- [[Getting-Started|PIPE Bot Getting Started]]
WIKEOF
            ;;
    esac

    # Update sidebar to include new pages
    print_info "Updating wiki sidebar"

    # Backup existing sidebar
    cp wiki/_Sidebar.md wiki/_Sidebar.md.backup

    # Check if Architecture section exists, if not add it
    if ! grep -q "## 📐 Architecture" wiki/_Sidebar.md; then
        cat >> wiki/_Sidebar.md << 'SIDEBAREOF'

## 📐 Architecture

- [[Architecture/Enterprise-CAG-RAG|Enterprise CAG+RAG]]
- [[Architecture/Bot-Factory-Architecture|Bot Factory Architecture]]
- [[Architecture/Data-Architecture-Governance|Data Governance]]

## 📚 Guides

- [[Guides/BSW-Tech-AI-Integration|AI Integration]]
- [[Guides/Claude-Integration|Claude Integration]]

## 📖 Reference

- [[Reference/Augmentic-AI-Integration|Augmentic AI]]
- [[Reference/Knowledge-Base-Quick-Start|Knowledge Base Setup]]

## 🌐 Domain

- [[Domain/${domain}-Architecture|${domain} Architecture]]

---

**Documentation Source:** [bsw-arch GitHub](https://github.com/bsw-arch/bsw-arch)
SIDEBAREOF
    fi

    # Add all wiki changes
    git add wiki/

    # Check if there are changes (after adding)
    if git diff --cached --quiet; then
        print_warning "No changes to commit for ${bot_name}"
        return 0
    fi

    # Commit changes
    print_info "Committing wiki documentation"
    git commit -m "docs: integrate GitHub architecture documentation into wiki

Add comprehensive architecture documentation to wiki from bsw-arch GitHub repository:

Wiki Pages Added:
- Architecture/Enterprise-CAG-RAG.md
- Architecture/Bot-Factory-Architecture.md
- Architecture/Data-Architecture-Governance.md
- Guides/BSW-Tech-AI-Integration.md
- Guides/Claude-Integration.md
- Reference/Augmentic-AI-Integration.md
- Reference/Knowledge-Base-Quick-Start.md
- Domain/${domain}-Architecture.md

These wiki pages link to full documentation in the repository and provide:
- Global architecture context for all 185 bots
- ${domain} domain-specific architecture
- Augmentic AI framework integration
- Knowledge base and CAG+RAG implementation guides

Updated sidebar navigation to include new architecture sections.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

    # Push to remote
    print_info "Pushing to Codeberg"
    if git push -u origin "${BRANCH_NAME}"; then
        print_success "Successfully integrated wiki docs for ${org_name}/${bot_name}"
        return 0
    else
        print_error "Failed to push ${org_name}/${bot_name}"
        return 1
    fi
}

# Main execution
main() {
    local domain=$1
    local bot_name=$2

    if [ -z "${domain}" ] || [ -z "${bot_name}" ]; then
        echo "Usage: $0 <DOMAIN> <BOT_NAME>"
        echo "Example: $0 ECO eco-infra-bot"
        exit 1
    fi

    print_info "Starting wiki documentation integration"
    print_info "Domain: ${domain}"
    print_info "Bot: ${bot_name}"
    print_info "GitHub repo: ${GITHUB_REPO_PATH}"
    print_info "Work directory: ${WORK_DIR}"

    # Ensure GitHub repo exists
    if [ ! -d "${GITHUB_REPO_PATH}" ]; then
        print_error "GitHub repository not found at ${GITHUB_REPO_PATH}"
        exit 1
    fi

    # Run integration
    if integrate_wiki_docs "${domain}" "${bot_name}"; then
        print_success "Wiki documentation integration complete!"
        print_info "Branch created: ${BRANCH_NAME}"
        print_info "Review changes at: https://codeberg.org/${domain}-Bots/${bot_name}/src/branch/${BRANCH_NAME}"
    else
        print_error "Wiki documentation integration failed"
        exit 1
    fi
}

# Execute
main "$@"
