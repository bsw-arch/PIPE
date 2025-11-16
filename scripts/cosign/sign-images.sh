#!/bin/bash
# Sign container images with Cosign
# Part of PIPE secure supply chain

set -euo pipefail

# Configuration
ZOT_REGISTRY="${ZOT_REGISTRY:-zot.pipe.local}"
COSIGN_KEY="${COSIGN_KEY:-cosign.key}"
COSIGN_PASSWORD="${COSIGN_PASSWORD:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v cosign &> /dev/null; then
        log_error "cosign not found. Please install from https://docs.sigstore.dev/cosign/installation/"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        log_error "docker not found"
        exit 1
    fi

    log_info "✓ All dependencies found"
}

# Generate Cosign keypair if not exists
generate_keypair() {
    if [ ! -f "$COSIGN_KEY" ]; then
        log_info "Generating Cosign keypair..."
        cosign generate-key-pair
        log_info "✓ Keypair generated: cosign.key, cosign.pub"
        log_warn "Store cosign.key securely (e.g., in OpenBao)"
    else
        log_info "Using existing keypair: $COSIGN_KEY"
    fi
}

# Sign a single image
sign_image() {
    local image=$1
    log_info "Signing image: $image"

    if [ -z "$COSIGN_PASSWORD" ]; then
        cosign sign --key "$COSIGN_KEY" "$image"
    else
        echo "$COSIGN_PASSWORD" | cosign sign --key "$COSIGN_KEY" "$image"
    fi

    log_info "✓ Signed: $image"
}

# Verify a signed image
verify_image() {
    local image=$1
    log_info "Verifying image: $image"

    if cosign verify --key cosign.pub "$image" > /dev/null 2>&1; then
        log_info "✓ Verification successful: $image"
        return 0
    else
        log_error "✗ Verification failed: $image"
        return 1
    fi
}

# Sign all PIPE images
sign_all_images() {
    local version="${1:-latest}"

    log_info "Signing all PIPE images (version: $version)"

    declare -a images=(
        "$ZOT_REGISTRY/pipe/pipeline-bot:$version"
        "$ZOT_REGISTRY/pipe/data-processor-bot:$version"
        "$ZOT_REGISTRY/pipe/monitor-bot:$version"
        "$ZOT_REGISTRY/pipe/integration-hub-bot:$version"
        "$ZOT_REGISTRY/governance/governance-manager:$version"
        "$ZOT_REGISTRY/monitoring/metrics-exporter:$version"
    )

    for image in "${images[@]}"; do
        if docker manifest inspect "$image" > /dev/null 2>&1; then
            sign_image "$image"
        else
            log_warn "Image not found, skipping: $image"
        fi
    done

    log_info "✓ All available images signed"
}

# Main function
main() {
    local command="${1:-sign}"
    local version="${2:-latest}"

    check_dependencies

    case "$command" in
        generate-keypair)
            generate_keypair
            ;;
        sign)
            generate_keypair
            sign_all_images "$version"
            ;;
        sign-single)
            if [ -z "${3:-}" ]; then
                log_error "Usage: $0 sign-single <version> <image>"
                exit 1
            fi
            generate_keypair
            sign_image "$3"
            ;;
        verify)
            if [ -z "${3:-}" ]; then
                log_error "Usage: $0 verify <version> <image>"
                exit 1
            fi
            verify_image "$3"
            ;;
        *)
            echo "Usage: $0 {generate-keypair|sign|sign-single|verify} [version] [image]"
            echo ""
            echo "Commands:"
            echo "  generate-keypair    Generate Cosign key pair"
            echo "  sign [version]      Sign all PIPE images (default: latest)"
            echo "  sign-single <ver> <image>  Sign a single image"
            echo "  verify <ver> <image>       Verify image signature"
            echo ""
            echo "Environment variables:"
            echo "  ZOT_REGISTRY       Zot registry URL (default: zot.pipe.local)"
            echo "  COSIGN_KEY         Path to Cosign private key (default: cosign.key)"
            echo "  COSIGN_PASSWORD    Password for Cosign key (optional)"
            exit 1
            ;;
    esac
}

main "$@"
