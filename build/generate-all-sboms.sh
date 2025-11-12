#!/bin/bash
# Generate All SBOMs - Master SBOM Generation Script
# ===================================================
# Generates SBOMs for all PIPE Task Bot containers
# Uses Syft for generation and Grype for CVE scanning

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
REGISTRY="${REGISTRY:-localhost:5000}"
TAG="${TAG:-latest}"

echo "🔍 PIPE Task Bot - Generate All SBOMs"
echo "======================================"
echo "Registry: ${REGISTRY}"
echo "Tag: ${TAG}"
echo ""

# Containers to generate SBOMs for
CONTAINERS=(
    "base"
    "task-bot"
    "task-scheduler"
    "task-executor"
)

# Track SBOM results
SUCCESSFUL_SBOMS=()
FAILED_SBOMS=()
TOTAL_VULNS=0

# Generate SBOM for each container
for container in "${CONTAINERS[@]}"; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Generating SBOM: ${container}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    CONTAINER_DIR="${PROJECT_DIR}/containers/${container}"

    if [ ! -d "${CONTAINER_DIR}" ]; then
        echo "⚠️  Warning: Container directory not found: ${CONTAINER_DIR}"
        FAILED_SBOMS+=("${container}")
        continue
    fi

    # Determine image name
    if [ "${container}" = "base" ]; then
        IMAGE_NAME="${REGISTRY}/axis-task-bot-base:${TAG}"
    else
        IMAGE_NAME="${REGISTRY}/axis-${container}:${TAG}"
    fi

    # Check if image exists
    if ! podman images "${IMAGE_NAME}" --format "{{.Repository}}" | grep -q "axis"; then
        echo "⚠️  Warning: Image not found: ${IMAGE_NAME}"
        echo "Please build the image first: ./build/build-all.sh"
        FAILED_SBOMS+=("${container}")
        continue
    fi

    # Generate SBOM
    if [ -f "${CONTAINER_DIR}/sbom/generate.sh" ]; then
        cd "${CONTAINER_DIR}"

        if ./sbom/generate.sh "${IMAGE_NAME}"; then
            echo "✅ SBOM generated: ${container}"
            SUCCESSFUL_SBOMS+=("${container}")

            # Count vulnerabilities
            VULN_FILE="${PROJECT_DIR}/sbom/${container}/vulnerabilities.json"
            if [ -f "${VULN_FILE}" ]; then
                VULN_COUNT=$(jq '.matches | length' "${VULN_FILE}")
                TOTAL_VULNS=$((TOTAL_VULNS + VULN_COUNT))
            fi
        else
            echo "❌ SBOM generation failed: ${container}"
            FAILED_SBOMS+=("${container}")
        fi
    else
        echo "⚠️  Warning: SBOM generation script not found: ${CONTAINER_DIR}/sbom/generate.sh"
        FAILED_SBOMS+=("${container}")
    fi
done

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SBOM Generation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Successful SBOM generations (${#SUCCESSFUL_SBOMS[@]}):"
for sbom in "${SUCCESSFUL_SBOMS[@]}"; do
    echo "  ✅ ${sbom}"
done

if [ ${#FAILED_SBOMS[@]} -gt 0 ]; then
    echo ""
    echo "Failed SBOM generations (${#FAILED_SBOMS[@]}):"
    for sbom in "${FAILED_SBOMS[@]}"; do
        echo "  ❌ ${sbom}"
    done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 Vulnerability Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Total vulnerabilities found: ${TOTAL_VULNS}"

if [ ${TOTAL_VULNS} -eq 0 ]; then
    echo "✅ No vulnerabilities detected!"
else
    echo "⚠️  Vulnerabilities detected - review individual reports"
    echo ""
    echo "Vulnerability details by container:"
    for container in "${SUCCESSFUL_SBOMS[@]}"; do
        VULN_FILE="${PROJECT_DIR}/sbom/${container}/vulnerabilities.json"
        if [ -f "${VULN_FILE}" ]; then
            VULN_COUNT=$(jq '.matches | length' "${VULN_FILE}")
            echo "  ${container}: ${VULN_COUNT} vulnerabilities"

            # Show critical/high
            CRITICAL_HIGH=$(jq -r '.matches[] | select(.vulnerability.severity == "Critical" or .vulnerability.severity == "High") | "\(.vulnerability.severity): \(.vulnerability.id)"' "${VULN_FILE}" | wc -l)
            if [ ${CRITICAL_HIGH} -gt 0 ]; then
                echo "    ⚠️  Critical/High: ${CRITICAL_HIGH}"
            fi
        fi
    done
fi

echo ""
echo "SBOM files location: ${PROJECT_DIR}/sbom/"
echo ""
ls -lh "${PROJECT_DIR}/sbom/"

echo ""
echo "Next steps:"
echo "  1. Review vulnerability reports: cat sbom/*/vulnerabilities.json"
echo "  2. Test containers: ./build/test-all.sh"
echo "  3. Push to registry: ./build/push-all.sh"

# Exit with error if any SBOMs failed or vulnerabilities found
if [ ${#FAILED_SBOMS[@]} -gt 0 ] || [ ${TOTAL_VULNS} -gt 0 ]; then
    exit 1
fi
