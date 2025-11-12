#!/bin/bash
# Codeberg Issue Creator for Bidirectional Sync
# Creates tracking issues on all bot repositories

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CODEBERG_TOKEN="${CODEBERG_TOKEN:-ff9fc7f843584aa741ba4379521c9dec13e4c12c}"
API_BASE="https://codeberg.org/api/v1"
BOT_LIST_FILE="${BOT_LIST_FILE:-/tmp/all-bots.json}"
STATE_FILE="${STATE_FILE:-/tmp/sync-state.json}"
LOG_DIR="/tmp/logs"

# Create log directory
mkdir -p "$LOG_DIR"

# Functions
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Initialize state file if it doesn't exist
init_state_file() {
    if [ ! -f "$STATE_FILE" ]; then
        print_info "Initializing state file: $STATE_FILE"
        cat > "$STATE_FILE" << 'EOF'
{
  "metadata": {
    "created": "",
    "github_repo": "https://github.com/bsw-arch/bsw-arch",
    "total_bots": 185,
    "issues_created": 0
  },
  "bots": {}
}
EOF
        # Set created timestamp
        NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        jq --arg now "$NOW" '.metadata.created = $now' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    fi
}

# Create issue for a single bot
create_bot_issue() {
    local domain=$1
    local bot_name=$2
    local org="${domain}-Bots"
    local repo_url="${API_BASE}/repos/${org}/${bot_name}/issues"

    print_info "Creating issue for ${org}/${bot_name}"

    # Generate issue body
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local issue_body=$(cat <<ISSUEBODY
# Bidirectional Documentation Sync

**Bot:** ${bot_name}
**Domain:** ${domain}
**Status:** 🔄 Active

## Sync Configuration

- **GitHub Source:** https://github.com/bsw-arch/bsw-arch
- **Codeberg Target:** https://codeberg.org/${org}/${bot_name}
- **Sync Frequency:** On-demand / Automated
- **Git Format:** GitHub (SHA-1) ↔ Codeberg (SHA-256)

## Sync Directions

### ✅ GitHub → Codeberg (Documentation Integration)

**Status:** Pending
**Last Sync:** Never
**Files Synced:** 0

Documentation to sync:
- [ ] Global architecture docs (Enterprise CAG+RAG, Bot Factory)
- [ ] ${domain} domain-specific guides
- [ ] Augmentic AI framework
- [ ] CAG+RAG implementation guides
- [ ] Knowledge base setup documentation

### ⏸️ Codeberg → GitHub (Updates/Improvements)

**Status:** Not started
**Last Sync:** Never
**Files Synced:** 0

Bot improvements to sync back:
- [ ] Bot-specific documentation updates
- [ ] Wiki improvements
- [ ] Architecture refinements

## Sync History

| Date | Direction | Commit | Files | Status |
|------|-----------|--------|-------|--------|
| - | - | - | - | - |

## Automation

This issue is managed by the bidirectional sync automation system.

**Scripts:**
- \`sync-github-to-codeberg.sh\` - Push docs from GitHub
- \`sync-codeberg-to-github.sh\` - Pull updates to GitHub

**Last Updated:** ${timestamp}

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
ISSUEBODY
)

    # Create JSON payload
    local payload_file="/tmp/issue-${domain}-${bot_name}.json"
    jq -n \
        --arg title "[SYNC] Bidirectional documentation sync with GitHub" \
        --arg body "$issue_body" \
        '{title: $title, body: $body}' > "$payload_file"

    # Make API request
    local response=$(curl -s -X POST \
        -H "Authorization: token ${CODEBERG_TOKEN}" \
        -H "Content-Type: application/json" \
        -d @"$payload_file" \
        "$repo_url")

    # Check response
    local issue_number=$(echo "$response" | jq -r '.number // empty')
    local issue_url=$(echo "$response" | jq -r '.html_url // empty')
    local error_msg=$(echo "$response" | jq -r '.message // empty')

    if [ -n "$issue_number" ] && [ "$issue_number" != "null" ]; then
        print_success "Created issue #${issue_number} for ${org}/${bot_name}"
        print_info "URL: ${issue_url}"

        # Update state file
        update_state "$domain" "$bot_name" "$issue_number" "$issue_url"

        # Cleanup
        rm -f "$payload_file"
        return 0
    else
        print_error "Failed to create issue for ${org}/${bot_name}"
        print_error "Error: ${error_msg}"
        echo "$response" > "${LOG_DIR}/error-${domain}-${bot_name}.json"

        # Cleanup
        rm -f "$payload_file"
        return 1
    fi
}

# Update state file
update_state() {
    local domain=$1
    local bot_name=$2
    local issue_number=$3
    local issue_url=$4
    local org="${domain}-Bots"
    local repo_key="${org}/${bot_name}"

    # Update state file using jq
    jq --arg key "$repo_key" \
       --arg domain "$domain" \
       --arg org "$org" \
       --arg bot "$bot_name" \
       --arg issue_num "$issue_number" \
       --arg issue_url "$issue_url" \
       --arg repo_url "git@codeberg.org:${org}/${bot_name}.git" \
       '.bots[$key] = {
           domain: $domain,
           org: $org,
           bot_name: $bot,
           codeberg_repo: $repo_url,
           issue_number: ($issue_num | tonumber),
           issue_url: $issue_url,
           status: "issue_created",
           last_sync_github_to_codeberg: null,
           last_sync_codeberg_to_github: null,
           github_last_commit: null,
           codeberg_last_commit: null
       } | .metadata.issues_created = (.bots | length)' \
       "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Create issues for a domain
create_domain_issues() {
    local domain=$1
    local batch_size=${2:-10}
    local delay=${3:-2}

    print_info "Creating issues for ${domain} domain"

    # Get bot list for domain
    local bots=$(jq -r ".domains.${domain}.bots[]" "$BOT_LIST_FILE")
    local total=$(echo "$bots" | wc -l)
    local current=0
    local success=0
    local failed=0

    print_info "Total bots in ${domain}: ${total}"

    for bot in $bots; do
        ((current++))
        print_info "Processing ${current}/${total}: ${bot}"

        if create_bot_issue "$domain" "$bot"; then
            ((success++))
        else
            ((failed++))
        fi

        # Rate limiting - delay every batch_size requests
        if [ $((current % batch_size)) -eq 0 ] && [ $current -lt $total ]; then
            print_info "Batch complete. Waiting ${delay}s before next batch..."
            sleep $delay
        fi
    done

    print_success "${domain} domain complete: ${success} created, ${failed} failed"
}

# Create issues for specific bots (pilot mode)
create_pilot_issues() {
    local bots_spec=$1

    print_info "Creating pilot issues"

    IFS=',' read -ra BOTS <<< "$bots_spec"
    local total=${#BOTS[@]}
    local current=0
    local success=0
    local failed=0

    for bot_spec in "${BOTS[@]}"; do
        IFS=':' read -ra PARTS <<< "$bot_spec"
        local domain="${PARTS[0]}"
        local bot_name="${PARTS[1]}"

        ((current++))
        print_info "Processing ${current}/${total}: ${domain}:${bot_name}"

        if create_bot_issue "$domain" "$bot_name"; then
            ((success++))
        else
            ((failed++))
        fi

        # Small delay between pilot bots
        if [ $current -lt $total ]; then
            sleep 1
        fi
    done

    print_success "Pilot complete: ${success} created, ${failed} failed"
}

# Generate report
generate_report() {
    print_info "Generating sync status report"

    local total=$(jq '.metadata.total_bots' "$STATE_FILE")
    local created=$(jq '.metadata.issues_created' "$STATE_FILE")
    local pending=$((total - created))

    echo ""
    echo "========================================="
    echo "  CODEBERG ISSUE CREATION STATUS"
    echo "========================================="
    echo ""
    echo "Total Bots:      $total"
    echo "Issues Created:  $created"
    echo "Pending:         $pending"
    echo ""

    # Domain breakdown
    echo "Domain Breakdown:"
    echo "-----------------"
    for domain in ECO AXIS IV PIPE BU BNI BNP DC; do
        local domain_count=$(jq -r "[.bots[] | select(.domain == \"$domain\")] | length" "$STATE_FILE")
        if [ "$domain_count" -gt 0 ]; then
            printf "%-8s %3d issues created\n" "$domain:" "$domain_count"
        fi
    done
    echo ""
    echo "State File: $STATE_FILE"
    echo "========================================="
}

# Main execution
main() {
    local mode=${1:-help}

    case $mode in
        pilot)
            # Pilot mode - create issues for specific bots
            local bots=${2:-"AXIS:axis-docs-bot,IV:iv-ai-bot,PIPE:pipe-build-bot,AXIS:axis-patterns-bot"}
            print_info "Starting pilot issue creation"
            print_info "Bots: $bots"
            init_state_file
            create_pilot_issues "$bots"
            generate_report
            ;;

        domain)
            # Domain mode - create issues for entire domain
            local domain=$2
            local batch_size=${3:-10}
            local delay=${4:-2}

            if [ -z "$domain" ]; then
                print_error "Domain required. Usage: $0 domain <DOMAIN> [batch_size] [delay]"
                exit 1
            fi

            print_info "Starting domain issue creation: $domain"
            init_state_file
            create_domain_issues "$domain" "$batch_size" "$delay"
            generate_report
            ;;

        all)
            # All domains mode - create issues for all domains
            print_info "Starting mass issue creation for all domains"
            init_state_file

            for domain in ECO AXIS IV PIPE; do
                print_info "Processing domain: $domain"
                create_domain_issues "$domain" 10 2
            done

            generate_report
            ;;

        report)
            # Just generate report
            if [ ! -f "$STATE_FILE" ]; then
                print_error "State file not found: $STATE_FILE"
                exit 1
            fi
            generate_report
            ;;

        *)
            echo "Usage: $0 <mode> [options]"
            echo ""
            echo "Modes:"
            echo "  pilot <bots>              Create issues for specific bots (format: DOMAIN:bot-name,DOMAIN:bot-name)"
            echo "  domain <DOMAIN> [batch] [delay]  Create issues for entire domain"
            echo "  all                       Create issues for all domains"
            echo "  report                    Generate status report"
            echo ""
            echo "Examples:"
            echo "  $0 pilot 'AXIS:axis-docs-bot,IV:iv-ai-bot'"
            echo "  $0 domain ECO 10 2"
            echo "  $0 all"
            echo "  $0 report"
            exit 1
            ;;
    esac
}

# Execute
main "$@"
