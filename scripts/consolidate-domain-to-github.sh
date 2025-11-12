#!/bin/bash
# Consolidate Codeberg bots into domain-based GitHub repos
# Each bot becomes a feature branch in the domain repository

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
WORK_DIR="/tmp/domain-consolidation"
CODEBERG_DIR="${WORK_DIR}/codeberg"
GITHUB_DIR="${WORK_DIR}/github"
GITHUB_ORG="bsw-arch"
BOT_LIST="/tmp/all-bots.json"

# Functions
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Setup workspace
setup_workspace() {
    print_info "Setting up workspace"
    mkdir -p "$CODEBERG_DIR"
    mkdir -p "$GITHUB_DIR"
}

# Create domain repository (SHA-1)
create_domain_repo() {
    local domain=$1
    local github_path="${GITHUB_DIR}/${domain}-Bots"

    print_info "Creating GitHub domain repository: ${domain}-Bots"

    # Initialize SHA-1 repository
    git init --object-format=sha1 --initial-branch=main "$github_path"

    cd "$github_path"

    # Configure git
    git config user.email "claude@anthropic.com"
    git config user.name "Claude Code Domain Consolidator"

    # Create initial README
    cat > README.md << EOF
# ${domain}-Bots Domain Repository

**Domain:** ${domain}
**Purpose:** Consolidated repository for all ${domain} domain bots from Codeberg
**Structure:** Each bot is a separate feature branch

## Repository Structure

This repository consolidates all ${domain} bots from Codeberg into a single GitHub repository.

- **main branch**: Domain overview and shared documentation
- **Feature branches**: Each bot has its own branch (e.g., \`bot/${domain,,}-infra-bot\`)

## Branches

Each bot from Codeberg (SHA-256) has been converted to SHA-1 and stored as a feature branch:

\`\`\`
bot/${domain,,}-bot-name-1
bot/${domain,,}-bot-name-2
...
\`\`\`

## Conversion Details

- **Source:** Codeberg ${domain}-Bots organization (SHA-256 format)
- **Target:** GitHub bsw-arch/${domain}-Bots repository (SHA-1 format)
- **Conversion Date:** $(date -u +"%Y-%m-%d")

## Bot List

See branches for individual bots. Use:

\`\`\`bash
git branch -r          # List all remote branches
git checkout bot/NAME  # Switch to a specific bot branch
\`\`\`

## Sync Information

- **Codeberg Org:** https://codeberg.org/${domain}-Bots
- **GitHub Repo:** https://github.com/${GITHUB_ORG}/${domain}-Bots
- **Format:** SHA-256 (Codeberg) → SHA-1 (GitHub)

---

🤖 Generated with Claude Code
Bidirectional Sync System
EOF

    # Create .gitignore
    cat > .gitignore << 'EOF'
# Git
.git/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
*.log
node_modules/
dist/
build/
EOF

    # Create initial commit
    git add .
    git commit -m "feat: initialize ${domain}-Bots domain repository

Created consolidated repository for ${domain} domain bots.

Structure:
- main: Domain overview and documentation
- bot/* branches: Individual bot repositories

Each bot from Codeberg (SHA-256) converted to GitHub (SHA-1).

🤖 Generated with Claude Code
"

    # Verify SHA-1
    local commit=$(git rev-parse HEAD)
    local hash_length=${#commit}

    if [ "$hash_length" -eq 40 ]; then
        print_success "Domain repo created with SHA-1 format"
        print_info "Initial commit: $commit"
    else
        print_error "Unexpected hash format: $hash_length chars"
        return 1
    fi

    # Add GitHub remote
    local github_url="git@github.com:${GITHUB_ORG}/${domain}-Bots.git"
    git remote add origin "$github_url"

    print_success "Domain repository initialized: ${domain}-Bots"
}

# Clone bot from Codeberg
clone_bot_from_codeberg() {
    local domain=$1
    local bot_name=$2
    local org="${domain}-Bots"
    local codeberg_url="git@codeberg.org:${org}/${bot_name}.git"
    local clone_path="${CODEBERG_DIR}/${domain}/${bot_name}"

    if [ -d "$clone_path" ]; then
        print_info "Bot already cloned: ${bot_name}"
        return 0
    fi

    print_info "Cloning ${org}/${bot_name} from Codeberg (SHA-256)"

    mkdir -p "${CODEBERG_DIR}/${domain}"

    if git clone --depth 1 "$codeberg_url" "$clone_path" 2>&1; then
        cd "$clone_path"
        local hash=$(git rev-parse HEAD)
        print_success "Cloned ${bot_name} (SHA-256: ${hash:0:16}...)"
        return 0
    else
        print_error "Failed to clone ${org}/${bot_name}"
        return 1
    fi
}

# Add bot as feature branch to domain repo
add_bot_as_branch() {
    local domain=$1
    local bot_name=$2
    local codeberg_path="${CODEBERG_DIR}/${domain}/${bot_name}"
    local github_path="${GITHUB_DIR}/${domain}-Bots"
    local branch_name="bot/${bot_name}"

    if [ ! -d "$codeberg_path" ]; then
        print_error "Codeberg repo not found: $codeberg_path"
        return 1
    fi

    if [ ! -d "$github_path" ]; then
        print_error "GitHub domain repo not found: $github_path"
        return 1
    fi

    print_info "Adding ${bot_name} as branch: ${branch_name}"

    cd "$github_path"

    # Create new branch from main
    git checkout main
    git checkout -b "$branch_name"

    # Remove all files except .git
    git rm -rf . 2>/dev/null || true

    # Copy bot files
    print_info "Copying bot files"
    rsync -av --exclude='.git' "${codeberg_path}/" "${github_path}/"

    # Get original commit info
    cd "$codeberg_path"
    local original_commit=$(git rev-parse HEAD)
    local original_message=$(git log -1 --pretty=%B | head -1)
    local original_author_name=$(git log -1 --pretty="%an")
    local original_author_email=$(git log -1 --pretty="%ae")
    local original_date=$(git log -1 --pretty=%ai)

    cd "$github_path"

    # Stage all changes
    git add -A

    # Check if there are changes to commit
    if git diff --cached --quiet; then
        print_warning "No changes to commit for ${bot_name}"
        git checkout main
        git branch -D "$branch_name"
        return 0
    fi

    # Create commit with original metadata
    GIT_AUTHOR_NAME="$original_author_name" \
    GIT_AUTHOR_EMAIL="$original_author_email" \
    GIT_AUTHOR_DATE="$original_date" \
    git commit -m "feat: add ${bot_name} from Codeberg

${original_message}

Converted from Codeberg ${domain}-Bots/${bot_name}
Original SHA-256 commit: ${original_commit}

🤖 Generated with Claude Code
Bidirectional Sync: Codeberg (SHA-256) → GitHub (SHA-1)
"

    # Verify conversion
    local new_commit=$(git rev-parse HEAD)
    local new_hash_length=${#new_commit}

    if [ "$new_hash_length" -eq 40 ]; then
        print_success "✓ ${bot_name} → SHA-1 branch"
        print_info "  SHA-256: ${original_commit:0:16}..."
        print_info "  SHA-1:   ${new_commit:0:16}..."
    else
        print_error "Hash conversion failed for ${bot_name}"
        return 1
    fi

    # Return to main
    git checkout main

    return 0
}

# Process entire domain
process_domain() {
    local domain=$1

    print_info "========================================="
    print_info "Processing ${domain} Domain"
    print_info "========================================="

    # Step 1: Create domain repository
    create_domain_repo "$domain"

    # Step 2: Get bot list
    if [ ! -f "$BOT_LIST" ]; then
        print_error "Bot list not found: $BOT_LIST"
        return 1
    fi

    local bots=$(jq -r ".domains.${domain}.bots[]" "$BOT_LIST" 2>/dev/null)

    if [ -z "$bots" ]; then
        print_error "No bots found for domain: $domain"
        return 1
    fi

    local total=$(echo "$bots" | wc -l)
    print_info "Total bots to process: $total"

    # Step 3: Clone and convert each bot
    local current=0
    local success=0
    local failed=0

    for bot_name in $bots; do
        ((current++))
        print_info "Processing ${current}/${total}: ${bot_name}"

        # Clone from Codeberg
        if ! clone_bot_from_codeberg "$domain" "$bot_name"; then
            print_error "Failed to clone ${bot_name}"
            ((failed++))
            continue
        fi

        # Add as branch
        if add_bot_as_branch "$domain" "$bot_name"; then
            ((success++))
        else
            print_error "Failed to add ${bot_name} as branch"
            ((failed++))
        fi

        echo ""
    done

    # Step 4: Summary
    cd "${GITHUB_DIR}/${domain}-Bots"
    local branch_count=$(git branch | wc -l)

    print_info "========================================="
    print_success "${domain} Domain Consolidation Complete"
    print_info "========================================="
    print_info "Total bots:      $total"
    print_success "Successful:      $success"
    print_error "Failed:          $failed"
    print_info "Total branches:  $branch_count (including main)"
    print_info ""
    print_info "Repository location: ${GITHUB_DIR}/${domain}-Bots"
    print_info ""
    print_info "Branches created:"
    git branch | grep "bot/" | head -10
    if [ "$branch_count" -gt 11 ]; then
        print_info "... and $((branch_count - 11)) more"
    fi
}

# Push domain repository to GitHub
push_domain_to_github() {
    local domain=$1
    local github_path="${GITHUB_DIR}/${domain}-Bots"

    if [ ! -d "$github_path" ]; then
        print_error "Domain repository not found: $github_path"
        return 1
    fi

    cd "$github_path"

    print_info "========================================="
    print_info "Pushing ${domain}-Bots to GitHub"
    print_info "========================================="

    # Push all branches
    print_info "Pushing all branches to GitHub..."

    if git push -u origin --all 2>&1; then
        print_success "Successfully pushed all branches to GitHub"
        print_info "Repository: https://github.com/${GITHUB_ORG}/${domain}-Bots"
        return 0
    else
        print_error "Failed to push to GitHub"
        print_warning "Repository may not exist on GitHub yet"
        print_info "Create at: https://github.com/new"
        print_info "Repo name: ${domain}-Bots"
        print_info "Then run: cd ${github_path} && git push -u origin --all"
        return 1
    fi
}

# Main execution
main() {
    local mode=${1:-help}

    setup_workspace

    case $mode in
        domain)
            local domain=$2

            if [ -z "$domain" ]; then
                print_error "Domain required"
                print_info "Usage: $0 domain <DOMAIN>"
                exit 1
            fi

            print_info "Starting domain consolidation: $domain"
            process_domain "$domain"
            ;;

        push)
            local domain=$2

            if [ -z "$domain" ]; then
                print_error "Domain required"
                print_info "Usage: $0 push <DOMAIN>"
                exit 1
            fi

            push_domain_to_github "$domain"
            ;;

        *)
            echo "Usage: $0 <mode> <domain>"
            echo ""
            echo "Modes:"
            echo "  domain <DOMAIN>   Consolidate all bots in domain to GitHub repo"
            echo "  push <DOMAIN>     Push consolidated domain repo to GitHub"
            echo ""
            echo "Examples:"
            echo "  $0 domain ECO     # Consolidate all 48 ECO bots"
            echo "  $0 push ECO       # Push ECO-Bots repo to GitHub"
            echo ""
            echo "Repository Structure:"
            echo "  GitHub: ${GITHUB_ORG}/<DOMAIN>-Bots"
            echo "  - main branch: Domain overview"
            echo "  - bot/* branches: Individual bots"
            echo ""
            echo "Working Directory: ${WORK_DIR}"
            exit 1
            ;;
    esac
}

# Execute
main "$@"
