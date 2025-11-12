#!/bin/bash
# Bot Documentation Integration Script
# Integrates GitHub bsw-arch documentation into individual Codeberg bot repositories

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
BRANCH_NAME="feature/bsw-tech-arch-001-github-docs-integration"

# Function to print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to integrate docs into a single bot repository
integrate_bot_docs() {
    local domain=$1
    local bot_name=$2
    local org_name="${domain}-Bots"
    local repo_url="git@codeberg.org:${org_name}/${bot_name}.git"
    local bot_dir="${WORK_DIR}/${domain}/${bot_name}"

    print_info "Processing ${org_name}/${bot_name}"

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

    # Create documentation structure
    mkdir -p docs/shared/architecture
    mkdir -p docs/shared/guides
    mkdir -p docs/shared/reference
    mkdir -p docs/domain/${domain}

    # Copy global architecture documentation
    print_info "Copying global architecture documentation"
    cp -f "${GITHUB_REPO_PATH}/docs/architecture/ENTERPRISE-CAG-RAG-SOLUTION-ARCHITECTURE.md" docs/shared/architecture/ 2>/dev/null || true
    cp -f "${GITHUB_REPO_PATH}/docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md" docs/shared/architecture/ 2>/dev/null || true
    cp -f "${GITHUB_REPO_PATH}/docs/architecture/DATA-ARCHITECTURE-GOVERNANCE-FRAMEWORK.md" docs/shared/architecture/ 2>/dev/null || true

    # Copy global guides
    print_info "Copying global guides"
    cp -f "${GITHUB_REPO_PATH}/docs/guides/development/CLAUDE.md" docs/shared/guides/ 2>/dev/null || true
    cp -f "${GITHUB_REPO_PATH}/docs/guides/development/BSW-TECH-AI-INTEGRATION-GUIDE.md" docs/shared/guides/ 2>/dev/null || true

    # Copy global reference
    cp -f "${GITHUB_REPO_PATH}/docs/reference/AUGMENTIC-AI-INTEGRATION-PLAN.md" docs/shared/reference/ 2>/dev/null || true
    cp -f "${GITHUB_REPO_PATH}/docs/reference/KNOWLEDGE-BASE-QUICK-START.md" docs/shared/reference/ 2>/dev/null || true

    # Copy domain-specific documentation
    print_info "Copying ${domain} domain documentation"
    case ${domain} in
        ECO)
            cp -rf "${GITHUB_REPO_PATH}/eco-bots/README.md" docs/domain/ECO/ECO-BOTS-README.md 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/eco-bots/README-BOT-EXAMPLES.md" docs/domain/ECO/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/architecture/domains/ECO/"*.md docs/domain/ECO/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/guides/ECO-BOTS-QUICK-START.md" docs/domain/ECO/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/eco-bots/configs/eco-bot-list.yaml" docs/domain/ECO/ 2>/dev/null || true
            ;;
        AXIS)
            cp -rf "${GITHUB_REPO_PATH}/docs/guides/AXIS-BOTS-SETUP-GUIDE.md" docs/domain/AXIS/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/reference/AXIS-BOTS-API-KEYS.md" docs/domain/AXIS/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/reference/APKO-DOMAIN-CONTAINERS-STRATEGY.md" docs/domain/AXIS/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/guides/MULTI-TAB-CLAUDE-WEB-CONSOLE-INSTRUCTIES.md" docs/domain/AXIS/ 2>/dev/null || true
            # CAG-RAG for AXIS
            mkdir -p docs/shared/cag-rag
            cp -rf "${GITHUB_REPO_PATH}/docs/architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md" docs/shared/cag-rag/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/guides/CAG-RAG-IMPLEMENTATION-GUIDE.md" docs/shared/cag-rag/ 2>/dev/null || true
            ;;
        IV)
            cp -rf "${GITHUB_REPO_PATH}/docs/architecture/domains/IV/"*.md docs/domain/IV/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/guides/bot-domains/IV-BOTS-CAG-RAG-IMPLEMENTATION.md" docs/domain/IV/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/guides/setup/IV-BOTS-SETUP.md" docs/domain/IV/ 2>/dev/null || true
            # CAG-RAG for IV
            mkdir -p docs/shared/cag-rag
            cp -rf "${GITHUB_REPO_PATH}/cag-rag-system/README.md" docs/shared/cag-rag/CAG-RAG-SYSTEM-README.md 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md" docs/shared/cag-rag/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/guides/CAG-RAG-IMPLEMENTATION-GUIDE.md" docs/shared/cag-rag/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/architecture/components/cag-rag/2-TIER-CAG-RAG-IMPLEMENTATION-GUIDE.md" docs/shared/cag-rag/ 2>/dev/null || true
            ;;
        PIPE)
            cp -rf "${GITHUB_REPO_PATH}/docs/guides/bot-domains/PIPE-BOTS-INSTRUCTIONS.md" docs/domain/PIPE/ 2>/dev/null || true
            cp -rf "${GITHUB_REPO_PATH}/docs/reference/BSW-Pipeline-Analysis-2025-09-01.md" docs/domain/PIPE/ 2>/dev/null || true
            ;;
    esac

    # Copy knowledge graph documentation for all domains
    mkdir -p docs/shared/knowledge-graph
    cp -f "${GITHUB_REPO_PATH}/KNOWLEDGE-GRAPH-QUICKSTART.md" docs/shared/knowledge-graph/ 2>/dev/null || true

    # Add all documentation
    git add docs/

    # Check if there are changes (after adding)
    if git diff --cached --quiet; then
        print_warning "No changes to commit for ${bot_name}"
        return 0
    fi

    # Commit changes
    print_info "Committing documentation"
    git commit -m "feat: add GitHub architecture documentation

Integrate comprehensive architecture documentation from bsw-arch GitHub repository:

- Global architecture documentation (ENTERPRISE-CAG-RAG, comprehensive analysis)
- ${domain} domain-specific guides and architecture
- Augmentic AI integration documentation
- BSW-Tech AI integration guide
- Knowledge graph documentation

This provides ${bot_name} with centralized knowledge access.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

    # Push to remote
    print_info "Pushing to Codeberg"
    if git push -u origin "${BRANCH_NAME}"; then
        print_success "Successfully integrated docs for ${org_name}/${bot_name}"
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

    print_info "Starting documentation integration"
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
    if integrate_bot_docs "${domain}" "${bot_name}"; then
        print_success "Documentation integration complete!"
        print_info "Branch created: ${BRANCH_NAME}"
        print_info "Review changes at: https://codeberg.org/${domain}-Bots/${bot_name}/src/branch/${BRANCH_NAME}"
    else
        print_error "Documentation integration failed"
        exit 1
    fi
}

# Execute
main "$@"
