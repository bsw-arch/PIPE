#!/bin/bash
# Convert Codeberg SHA-256 repos to GitHub SHA-1 repos
# Clones from Codeberg, converts hash format, pushes to GitHub

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
WORK_DIR="/tmp/sha256-to-sha1"
CODEBERG_DIR="${WORK_DIR}/codeberg"
GITHUB_DIR="${WORK_DIR}/github"
GITHUB_ORG="bsw-arch"

# Functions
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Setup working directories
setup_workspace() {
    print_info "Setting up workspace"
    mkdir -p "$CODEBERG_DIR"
    mkdir -p "$GITHUB_DIR"
}

# Clone Codeberg repo (SHA-256)
clone_codeberg_repo() {
    local domain=$1
    local bot_name=$2
    local org="${domain}-Bots"
    local codeberg_url="git@codeberg.org:${org}/${bot_name}.git"
    local clone_path="${CODEBERG_DIR}/${domain}/${bot_name}"

    print_info "Cloning ${org}/${bot_name} from Codeberg (SHA-256)"

    if [ -d "$clone_path" ]; then
        print_warning "Repository already cloned at $clone_path"
        return 0
    fi

    mkdir -p "${CODEBERG_DIR}/${domain}"

    if git clone "$codeberg_url" "$clone_path" 2>&1; then
        print_success "Cloned ${org}/${bot_name}"

        # Verify it's SHA-256
        cd "$clone_path"
        local hash_format=$(git config extensions.objectFormat 2>/dev/null || echo "sha1")
        print_info "Codeberg repo format: $hash_format"

        # Get commit hash length to verify
        local latest_commit=$(git rev-parse HEAD)
        local hash_length=${#latest_commit}
        print_info "Latest commit hash length: $hash_length chars"

        if [ "$hash_length" -eq 64 ]; then
            print_success "Verified: SHA-256 format (64-char hash)"
        else
            print_warning "Unexpected hash length: $hash_length"
        fi

        return 0
    else
        print_error "Failed to clone ${org}/${bot_name}"
        return 1
    fi
}

# Convert SHA-256 repo to SHA-1 and push to GitHub
convert_and_push_to_github() {
    local domain=$1
    local bot_name=$2
    local codeberg_path="${CODEBERG_DIR}/${domain}/${bot_name}"
    local github_path="${GITHUB_DIR}/${domain}/${bot_name}"
    local github_repo_name="${domain}-${bot_name}"
    local github_url="git@github.com:${GITHUB_ORG}/${github_repo_name}.git"

    print_info "Converting ${bot_name} from SHA-256 to SHA-1"

    if [ ! -d "$codeberg_path" ]; then
        print_error "Codeberg repo not found: $codeberg_path"
        return 1
    fi

    # Create GitHub working directory
    mkdir -p "${GITHUB_DIR}/${domain}"

    # Initialize new SHA-1 repo
    print_info "Creating new SHA-1 repository"
    git init --object-format=sha1 "$github_path"

    cd "$github_path"

    # Configure git for this repo
    git config user.email "claude@anthropic.com"
    git config user.name "Claude Code Bot Converter"

    # Copy all files from Codeberg repo (excluding .git)
    print_info "Copying repository content"
    rsync -av --exclude='.git' "${codeberg_path}/" "${github_path}/"

    # Add all files
    git add .

    # Get original commit info from Codeberg
    cd "$codeberg_path"
    local original_commit=$(git rev-parse HEAD)
    local original_message=$(git log -1 --pretty=%B)
    local original_author=$(git log -1 --pretty="%an <%ae>")
    local original_date=$(git log -1 --pretty=%ai)

    cd "$github_path"

    # Create commit with original metadata
    print_info "Creating SHA-1 commit"
    GIT_AUTHOR_NAME="$(echo "$original_author" | cut -d'<' -f1 | xargs)" \
    GIT_AUTHOR_EMAIL="$(echo "$original_author" | grep -oP '(?<=<)[^>]+')" \
    GIT_AUTHOR_DATE="$original_date" \
    git commit -m "${original_message}

Converted from Codeberg SHA-256 repository
Original Codeberg commit: ${original_commit}
Source: ${domain}-Bots/${bot_name}

🤖 Converted with Claude Code
"

    # Verify SHA-1 format
    local new_commit=$(git rev-parse HEAD)
    local new_hash_length=${#new_commit}

    if [ "$new_hash_length" -eq 40 ]; then
        print_success "Verified: SHA-1 format (40-char hash)"
        print_info "SHA-256 commit: $original_commit"
        print_info "SHA-1 commit:   $new_commit"
    else
        print_error "Unexpected hash length: $new_hash_length"
        return 1
    fi

    # Add GitHub remote
    print_info "Adding GitHub remote: $github_url"
    git remote add origin "$github_url"

    # Try to push (will fail if repo doesn't exist on GitHub)
    print_info "Pushing to GitHub (main branch)"
    if git push -u origin main 2>&1; then
        print_success "Pushed to GitHub: https://github.com/${GITHUB_ORG}/${github_repo_name}"
        return 0
    else
        print_warning "Push failed - repository may not exist on GitHub yet"
        print_info "Create repo at: https://github.com/new"
        print_info "Repo name: ${github_repo_name}"
        print_info "Then run: cd ${github_path} && git push -u origin main"
        return 2
    fi
}

# Process single bot
process_bot() {
    local domain=$1
    local bot_name=$2

    print_info "========================================="
    print_info "Processing: ${domain}/${bot_name}"
    print_info "========================================="

    # Step 1: Clone from Codeberg (SHA-256)
    if ! clone_codeberg_repo "$domain" "$bot_name"; then
        print_error "Failed to clone ${domain}/${bot_name}"
        return 1
    fi

    # Step 2: Convert and push to GitHub (SHA-1)
    convert_and_push_to_github "$domain" "$bot_name"
    local result=$?

    if [ $result -eq 0 ]; then
        print_success "✓ ${domain}/${bot_name} - Fully migrated"
    elif [ $result -eq 2 ]; then
        print_warning "⚠ ${domain}/${bot_name} - Converted but needs GitHub repo creation"
    else
        print_error "✗ ${domain}/${bot_name} - Failed"
    fi

    return $result
}

# Process pilot bots
process_pilot() {
    print_info "Processing pilot bots (test run)"

    local bots=(
        "ECO:eco-infra-bot"
        "AXIS:axis-docs-bot"
        "PIPE:pipe-build-bot"
    )

    local total=${#bots[@]}
    local success=0
    local partial=0
    local failed=0

    for bot_spec in "${bots[@]}"; do
        IFS=':' read -r domain bot_name <<< "$bot_spec"

        if process_bot "$domain" "$bot_name"; then
            ((success++))
        elif [ $? -eq 2 ]; then
            ((partial++))
        else
            ((failed++))
        fi

        echo ""
    done

    print_info "========================================="
    print_info "Pilot Results"
    print_info "========================================="
    print_info "Total:    $total"
    print_success "Success:  $success"
    print_warning "Partial:  $partial (needs GitHub repo)"
    print_error "Failed:   $failed"
}

# Process domain
process_domain() {
    local domain=$1
    local bot_list_file="/tmp/all-bots.json"

    if [ ! -f "$bot_list_file" ]; then
        print_error "Bot list not found: $bot_list_file"
        return 1
    fi

    print_info "Processing all bots in ${domain} domain"

    local bots=$(jq -r ".domains.${domain}.bots[]" "$bot_list_file")
    local total=$(echo "$bots" | wc -l)
    local current=0
    local success=0
    local partial=0
    local failed=0

    print_info "Total bots in ${domain}: ${total}"

    for bot_name in $bots; do
        ((current++))
        print_info "Processing ${current}/${total}: ${bot_name}"

        if process_bot "$domain" "$bot_name"; then
            ((success++))
        elif [ $? -eq 2 ]; then
            ((partial++))
        else
            ((failed++))
        fi

        echo ""
    done

    print_info "========================================="
    print_info "${domain} Domain Results"
    print_info "========================================="
    print_info "Total:    $total"
    print_success "Success:  $success"
    print_warning "Partial:  $partial"
    print_error "Failed:   $failed"
}

# Main execution
main() {
    local mode=${1:-help}

    setup_workspace

    case $mode in
        pilot)
            print_info "Starting pilot conversion (3 bots)"
            process_pilot
            ;;

        bot)
            # Single bot mode
            local domain=$2
            local bot_name=$3

            if [ -z "$domain" ] || [ -z "$bot_name" ]; then
                print_error "Domain and bot name required"
                print_info "Usage: $0 bot <DOMAIN> <BOT_NAME>"
                exit 1
            fi

            process_bot "$domain" "$bot_name"
            ;;

        domain)
            # Full domain mode
            local domain=$2

            if [ -z "$domain" ]; then
                print_error "Domain required"
                print_info "Usage: $0 domain <DOMAIN>"
                exit 1
            fi

            process_domain "$domain"
            ;;

        *)
            echo "Usage: $0 <mode> [options]"
            echo ""
            echo "Modes:"
            echo "  pilot                    Convert 3 pilot bots (test run)"
            echo "  bot <DOMAIN> <BOT_NAME>  Convert single bot"
            echo "  domain <DOMAIN>          Convert all bots in domain"
            echo ""
            echo "Examples:"
            echo "  $0 pilot"
            echo "  $0 bot ECO eco-infra-bot"
            echo "  $0 domain ECO"
            echo ""
            echo "Working directories:"
            echo "  Codeberg (SHA-256): $CODEBERG_DIR"
            echo "  GitHub (SHA-1):     $GITHUB_DIR"
            exit 1
            ;;
    esac
}

# Execute
main "$@"
